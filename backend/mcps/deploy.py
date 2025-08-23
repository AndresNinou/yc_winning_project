# deployment_mcp.py

from fastmcp import FastMCP
from typing import Any, Optional, Dict
from browser_use.llm import ChatOpenAI, ChatGroq
from browser_use import Agent, BrowserSession
import os, json, subprocess, shutil, base64, ssl
from pathlib import Path
from urllib import request, error
from dotenv import load_dotenv

# Prefer a reliable CA bundle everywhere we do TLS.
# certifi is robust on macOS where the system store is often missing in Python.
try:
    import certifi
    _CERTIFI_PATH = certifi.where()
except Exception:
    certifi = None
    _CERTIFI_PATH = None

load_dotenv()

browser_session = BrowserSession(
    cdp_url="ws://localhost:9222/devtools/browser/acd036ed-d327-46ff-8bef-a148bb44cb4c",
    is_local=False
)

def _run(cmd, cwd=None, allow_fail: bool = False):
    p = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if p.returncode and not allow_fail:
        raise RuntimeError(f"{' '.join(cmd)} failed:\n{p.stderr or p.stdout}")
    return p

def _ssl_context() -> ssl.SSLContext:
    """
    Create a reusable SSLContext with a reliable CA bundle.
    Set INSECURE_SKIP_VERIFY=1 to disable verification (use only behind corp proxies).
    Optionally honor SSL_CERT_FILE / SSL_CERT_DIR if provided.
    """
    if os.getenv("INSECURE_SKIP_VERIFY") == "1":
        return ssl._create_unverified_context()

    cafile = os.getenv("SSL_CERT_FILE")
    capath = os.getenv("SSL_CERT_DIR")

    if cafile or capath:
        return ssl.create_default_context(cafile=cafile, capath=capath)

    if _CERTIFI_PATH:
        return ssl.create_default_context(cafile=_CERTIFI_PATH)

    # Fallback to system defaults (least reliable on macOS Pythons)
    return ssl.create_default_context()

_SSL_CTX = _ssl_context()

def _api(method: str, url: str, token: str, payload: Optional[Dict] = None) -> Dict:
    req = request.Request(
        url,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        },
        data=None if payload is None else json.dumps(payload).encode(),
    )
    try:
        # Use our TLS context so cert verification succeeds on macOS
        with request.urlopen(req, context=_SSL_CTX) as resp:
            return json.loads(resp.read().decode())
    except error.HTTPError as e:
        raise RuntimeError(f"{e.code} {e.reason}: {e.read().decode()}")
    except error.URLError as e:
        raise RuntimeError(f"Network error: {e.reason}")

def _configure_git_tls(repo_dir: Path):
    """
    Configure git to use the same CA bundle so HTTPS pushes don't fail.
    Respects INSECURE_SKIP_VERIFY=1 to disable verification for this repo.
    """
    if os.getenv("INSECURE_SKIP_VERIFY") == "1":
        _run(["git", "config", "http.sslVerify", "false"], cwd=repo_dir)
        return

    # If user specified custom CA, prefer that
    cafile = os.getenv("SSL_CERT_FILE")
    if cafile and Path(cafile).exists():
        _run(["git", "config", "http.sslCAInfo", str(Path(cafile).resolve())], cwd=repo_dir)
        return

    # Otherwise use certifi when available
    if _CERTIFI_PATH:
        _run(["git", "config", "http.sslCAInfo", _CERTIFI_PATH], cwd=repo_dir)

def make_repo(folder_path: str, repo_name: str) -> Dict[str, str]:
    """
    Wipes any local .git, creates/uses a PUBLIC repo on your user, pushes main.
    Requires CLASSIC PAT in GITHUB_TOKEN with 'public_repo' or 'repo'.
    """
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("Set GITHUB_TOKEN to a classic PAT with 'public_repo' or 'repo' scope.")

    if not repo_name:
        raise RuntimeError("project_name/repo_name is required.")

    p = Path(folder_path).expanduser().resolve()
    p.mkdir(parents=True, exist_ok=True)

    # Reset local VCS state
    git_dir = p / ".git"
    if git_dir.exists():
        shutil.rmtree(git_dir)

    _run(["git", "init", "-q"], cwd=p)
    _run(["git", "checkout", "-B", "main"], cwd=p)

    # Ensure there is content (ignore .git)
    if not any(e.name != ".git" for e in p.iterdir()):
        (p / "README.md").write_text(f"# {repo_name}\n")

    _run(["git", "add", "-A"], cwd=p)
    r = _run(["git", "commit", "-m", "Initial commit"], cwd=p, allow_fail=True)
    if r.returncode:
        stderr = (r.stderr or "").lower()
        if "author identity unknown" in stderr or "please tell me who you are" in stderr:
            raise RuntimeError(
                "Configure git:\n"
                "  git config --global user.name \"Your Name\"\n"
                "  git config --global user.email \"you@example.com\""
            )
        _run(["git", "commit", "--allow-empty", "-m", "Initial commit"], cwd=p)

    # Create or reuse GitHub repo on the authenticated user
    try:
        data = _api("POST", "https://api.github.com/user/repos", token,
                    {"name": repo_name, "private": True, "auto_init": False})
        remote = data["clone_url"]
    except RuntimeError as e:
        if str(e).startswith("422"):
            me = _api("GET", "https://api.github.com/user", token)
            remote = _api("GET", f"https://api.github.com/repos/{me['login']}/{repo_name}", token)["clone_url"]
        else:
            raise

    # Ensure git uses trusted CA for HTTPS
    _configure_git_tls(p)

    # Push with HTTP Basic using PAT
    _run(["git", "remote", "remove", "origin"], cwd=p, allow_fail=True)
    _run(["git", "remote", "add", "origin", remote], cwd=p)

    basic = base64.b64encode(f"x-access-token:{token}".encode()).decode()
    _run([
        "git",
        "-c", f"http.extraHeader=Authorization: Basic {basic}",
        "push", "-u", "origin", "main"
    ], cwd=p)

    return {"local_path": str(p), "remote": remote, "branch": "main"}

mcp = FastMCP("Deployment tool to Dedalus Labs")

@mcp.tool
async def deploy(project_name: Optional[str] = None, folder_path: Optional[str] = None) -> Any:
    """
    Deploy a project to Dedalus Labs
    """
    if not project_name:
        raise RuntimeError("project_name is required.")
    if not folder_path:
        folder_path = f"./{project_name}"

    make_repo(folder_path, project_name)

    llm = ChatGroq(model="meta-llama/llama-4-maverick-17b-128e-instruct")

    agent = Agent(
        task=f"""
# Role

You are an expert CI/CD Agent pushing code to Dedalus Labs

# Task

Your task is to go to Dedalus Labs and manually upload

# Output Format

Follow these steps: 

- Go to https://www.dedaluslabs.ai/dashboard/servers
- Click "Deploy Server" or "Add Server"
- Then, on the search bar with placeholder "Search repositories", tap on it, then search for the name of the project
- Tap on the project that's above "Configure Project"
- Now tap the "Configure Project"
- Click Deploy Server, and immediately finish the task

The project to deploy is: {project_name}. Reply at the end how the project went in no more than 1 sentence.
""",
        llm=llm,
        browser_session=browser_session
    )
    result = await agent.run()

    return {"final_message": result.final_result()}

if __name__ == "__main__":
    mcp.run()

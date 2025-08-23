from fastapi import APIRouter
from typing import Any, Optional
from browser_use.llm import ChatOpenAI, ChatGroq
from browser_use import Agent, BrowserSession
import os, json, subprocess, shutil, base64
from pathlib import Path
from urllib import request, error

router = APIRouter(prefix="/services", tags=["services"])

browser_session = BrowserSession(
    cdp_url=os.getenv("CHROME_WS_URL"),
    is_local=False
)

def _run(cmd, cwd=None, allow_fail=False):
    p = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if p.returncode and not allow_fail:
        raise RuntimeError(f"{' '.join(cmd)} failed:\n{p.stderr or p.stdout}")
    return p

def _api(method: str, url: str, token: str, payload: dict | None = None) -> dict:
    req = request.Request(
        url, method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        },
        data=None if payload is None else json.dumps(payload).encode(),
    )
    try:
        with request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except error.HTTPError as e:
        raise RuntimeError(f"{e.code} {e.reason}: {e.read().decode()}")

def make_repo(folder_path: str, repo_name: str) -> dict:
    """
    Wipes any local .git, creates/uses a PUBLIC repo on your user, pushes main.
    Requires CLASSIC PAT in GITHUB_TOKEN with 'public_repo' or 'repo'.
    """
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("Set GITHUB_TOKEN to a classic PAT with 'public_repo' or 'repo' scope.")

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
                    {"name": repo_name, "private": False, "auto_init": False})
        remote = data["clone_url"]
    except RuntimeError as e:
        if str(e).startswith("422"):
            me = _api("GET", "https://api.github.com/user", token)
            remote = _api("GET", f"https://api.github.com/repos/{me['login']}/{repo_name}", token)["clone_url"]
        else:
            raise

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

@router.get("/deploy")
async def deploy(project_name: Optional[str] = None, folder_path: Optional[str] = None) -> Any:
    """
    Deploy a project to Dedalus Labs
    """

    make_repo(folder_path, project_name)

    llm = ChatGroq(model="meta-llama/llama-4-maverick-17b-128e-instruct")
    # llm = ChatGroq(model="moonshotai/kimi-k2-instruct")

    agent = Agent(
        task="""
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
    # make_repo("/path/to/folder", "new-repo-name")
    make_repo("/Users/knuceles/Documents/GitHub/yc_winning_project/sandbox/uuid", "grap")
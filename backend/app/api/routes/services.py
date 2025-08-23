from fastapi import APIRouter
from typing import Any, Optional
from browser_use.llm import ChatOpenAI, ChatGroq
from browser_use import Agent, BrowserSession

router = APIRouter(prefix="/services", tags=["services"])

browser_session = BrowserSession(
    cdp_url="ws://localhost:9222/devtools/browser/acd036ed-d327-46ff-8bef-a148bb44cb4c",
    is_local=False
)


@router.get("/browser")
async def browser(project_name: Optional[str] = None) -> Any:
    # llm = ChatOpenAI(model="gpt-5-mini")
    # llm = ChatOpenAI(
    #     base_url="https://api.cerebras.ai/v1",
    #     model="qwen-3-235b-a22b-thinking-2507"
    # )
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

The project to deploy is: - HttpUtility Reply at the end how the project went in no more than 1 sentence.
""",
        llm=llm,
        browser_session=browser_session
    )
    result = await agent.run()
    
    


    return {"result": "dsa", "result": result, "final_message": result.final_result()}
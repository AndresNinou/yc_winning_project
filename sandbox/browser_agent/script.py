from fastmcp import FastMCP
from browser_agent import Agent
from browser_use.llm import ChatGroq

mcp = FastMCP("Demo 🚀")

@mcp.tool
async def browse(URL: str, task: str) -> str:
    """Browse a website to complete a task. Must be a website with minimal dynamic pages"""
    llm = ChatGroq(model="meta-llama/llama-4-maverick-17b-128e-instruct")
    agent = Agent(
        task=task,
        llm=llm,
    )
    result = await agent.run()
    return result.final_result()

if __name__ == "__main__":
    mcp.run()
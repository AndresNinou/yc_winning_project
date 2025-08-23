#!/usr/bin/env python3
"""
Test script for MCP integration with Claude Code SDK.

This script demonstrates how MCP servers are now integrated into the Claude service.
"""

import asyncio
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent))

from app.services.claude import ClaudeService, ClaudeRequest


async def test_mcp_integration():
    """Test MCP server integration with Claude Code SDK."""
    
    print("🔧 Testing MCP Integration with Claude Code SDK")
    print("-" * 50)
    
    # Initialize Claude service
    claude_service = ClaudeService()
    
    # Test request with MCP tools available
    request = ClaudeRequest(
        prompt="Can you help me scrape information from a website using firecrawl, and then potentially deploy something using the deploy tool?",
        system_prompt="You are a helpful AI assistant with access to web scraping (firecrawl) and deployment tools. Explain what tools you have available.",
        max_turns=3,
        allowed_tools=[
            "Read", "Write", "Bash", "ListDir", "Search", "StrReplace",
            "mcp__mcp-server-firecrawl",  # Firecrawl MCP tools
            "mcp__deploy"  # Deploy MCP tools
        ],
        conversation_id="test_mcp_session"
    )
    
    print("📝 Request Configuration:")
    print(f"  - MCP Servers: mcp-server-firecrawl, deploy")
    print(f"  - Allowed Tools: {len(request.allowed_tools)} tools including MCP")
    print(f"  - Conversation ID: {request.conversation_id}")
    print()
    
    try:
        print("🚀 Sending request to Claude with MCP support...")
        response = await claude_service.generate_response(request)
        
        print("✅ Response received successfully!")
        print(f"  - Conversation ID: {response.conversation_id}")
        print(f"  - Workspace Path: {response.workspace_path}")
        print()
        print("📄 Claude Response:")
        print("-" * 30)
        print(response.response)
        print("-" * 30)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("Make sure Claude Code CLI is installed and configured.")


async def test_streaming_with_mcp():
    """Test streaming responses with MCP tools."""
    
    print("\n🔄 Testing Streaming with MCP Tools")
    print("-" * 50)
    
    claude_service = ClaudeService()
    
    request = ClaudeRequest(
        prompt="Please list the available MCP tools and demonstrate using one of them.",
        system_prompt="You have access to firecrawl for web scraping and deploy tools for deployment. Show what you can do.",
        conversation_id="test_mcp_streaming"
    )
    
    try:
        print("🚀 Starting streaming request...")
        
        async for chunk in claude_service.generate_stream(request):
            # Parse and display streaming data
            try:
                import json
                data = json.loads(chunk)
                
                if data.get("type") == "tool_use":
                    print(f"🔧 Using MCP tool: {data.get('tool_name')}")
                elif data.get("type") == "text_block":
                    print(data.get("content", ""), end="", flush=True)
                elif data.get("type") == "result":
                    cost = data.get("total_cost", 0)
                    print(f"\n💰 Total cost: ${cost:.4f}")
                    
            except json.JSONDecodeError:
                # Non-JSON chunk, just print it
                print(chunk, end="", flush=True)
                
    except Exception as e:
        print(f"❌ Streaming error: {str(e)}")


if __name__ == "__main__":
    print("🎯 MCP Integration Test Suite")
    print("=" * 50)
    
    # Run the tests
    asyncio.run(test_mcp_integration())
    asyncio.run(test_streaming_with_mcp())
    
    print("\n✨ Test suite completed!")
    print("\nMCP servers configured:")
    print("  • mcp-server-firecrawl: Web scraping capabilities")
    print("  • deploy: Deployment automation to Dedalus Labs")

#!/usr/bin/env python3
"""
Test script to verify that MCP tools are used automatically without permission prompts.
"""

import asyncio
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent))

from app.services.claude import ClaudeService, ClaudeRequest


async def test_permissive_mcp():
    """Test that MCP tools are used automatically without permission prompts."""
    
    print("🔧 Testing Permissive MCP Usage (No Permission Prompts)")
    print("=" * 60)
    
    claude_service = ClaudeService()
    
    # Test request that should automatically use MCP tools
    request = ClaudeRequest(
        prompt="Search for information about Cognition's latest acquisition. Use web scraping tools to find recent news.",
        system_prompt="You are an AI assistant with web scraping capabilities. Always use available tools automatically without asking for permission when they are needed for the task.",
        max_turns=4,
        conversation_id="test_permissive",
        permission_mode="plan"  # Force plan mode for maximum permissiveness
    )
    
    print("📝 Request Configuration:")
    print(f"  - Permission Mode: {request.permission_mode}")
    print(f"  - Task: Search for Cognition's acquisition news")
    print(f"  - Expected: Automatic tool usage without permission prompts")
    print()
    
    try:
        print("🚀 Sending request (should use tools automatically)...")
        print("-" * 50)
        
        # Use streaming to see tool usage in real-time
        tool_used = False
        
        async for chunk in claude_service.generate_stream(request):
            try:
                import json
                data = json.loads(chunk)
                
                if data.get("type") == "tool_use":
                    tool_name = data.get("tool_name", "unknown")
                    print(f"✅ TOOL USED AUTOMATICALLY: {tool_name}")
                    tool_used = True
                elif data.get("type") == "text_block":
                    content = data.get("content", "")
                    # Print content but look for permission requests
                    if "permission" in content.lower() or "grant" in content.lower():
                        print(f"⚠️  PERMISSION REQUEST DETECTED: {content[:100]}...")
                    else:
                        print(content, end="", flush=True)
                        
            except json.JSONDecodeError:
                # Non-JSON chunk
                print(chunk, end="", flush=True)
        
        print(f"\n\n📊 Test Results:")
        print(f"  - Tools Used Automatically: {'✅ YES' if tool_used else '❌ NO'}")
        print(f"  - Permission Mode: plan (maximum permissiveness)")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    asyncio.run(test_permissive_mcp())

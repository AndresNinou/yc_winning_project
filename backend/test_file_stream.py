"""Test script for file streaming endpoint.

Simple test to verify the file streaming SSE endpoint works correctly.
"""

import asyncio
import httpx
import json
from pathlib import Path


async def test_file_stream_endpoint():
    """Test the file streaming SSE endpoint."""
    base_url = "http://localhost:8000"
    
    print("Testing file streaming endpoint...")
    
    try:
        # Test status endpoint first
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/api/v1/stream/status")
            print(f"Status endpoint: {response.status_code}")
            if response.status_code == 200:
                print(f"Status response: {response.json()}")
            
            # Test SSE endpoint with a short connection
            print("\nTesting SSE stream (will run for 10 seconds)...")
            async with client.stream(
                "GET",
                f"{base_url}/api/v1/stream/files",
                params={"session_id": "test_session"},
                headers={"Accept": "text/event-stream"}
            ) as response:
                print(f"SSE endpoint status: {response.status_code}")
                if response.status_code == 200:
                    print("SSE Headers:", dict(response.headers))
                    
                    # Read events for 10 seconds
                    start_time = asyncio.get_event_loop().time()
                    async for line in response.aiter_text():
                        if line.strip():
                            print(f"SSE Event: {line.strip()}")
                        
                        # Stop after 10 seconds
                        if asyncio.get_event_loop().time() - start_time > 10:
                            break
                            
            # Test stop endpoint
            response = await client.post(f"{base_url}/api/v1/stream/stop")
            print(f"\nStop endpoint: {response.status_code}")
            if response.status_code == 200:
                print(f"Stop response: {response.json()}")
                
    except Exception as e:
        print(f"Error testing endpoints: {e}")


if __name__ == "__main__":
    asyncio.run(test_file_stream_endpoint())

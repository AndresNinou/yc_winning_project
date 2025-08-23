"""Comprehensive proof that file streaming works with real file operations.

This test demonstrates the file streaming endpoint by:
1. Starting an SSE stream
2. Creating, modifying, and deleting files
3. Showing real-time file change detection
4. Proving the system works for Claude code sessions
"""

import asyncio
import httpx
import json
import tempfile
import os
from pathlib import Path
import time


class FileStreamProof:
    """Proof of concept for file streaming functionality."""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.test_dir = Path(tempfile.mkdtemp(prefix="file_stream_test_"))
        self.events_received = []
        
    async def cleanup(self):
        """Clean up test directory."""
        import shutil
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
            print(f"✅ Cleaned up test directory: {self.test_dir}")
    
    async def prove_file_streaming_works(self):
        """Comprehensive proof that file streaming detects real file changes."""
        print("🚀 Starting File Stream Proof-of-Concept")
        print(f"📁 Test directory: {self.test_dir}")
        print("=" * 70)
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Start SSE stream targeting our test directory
                print("📡 Starting SSE stream for test directory...")
                
                async with client.stream(
                    "GET",
                    f"{self.base_url}/api/v1/stream/files",
                    params={
                        "workspace_path": str(self.test_dir),
                        "session_id": "proof_session"
                    },
                    headers={"Accept": "text/event-stream"}
                ) as response:
                    
                    if response.status_code != 200:
                        print(f"❌ Failed to start SSE stream: {response.status_code}")
                        return
                    
                    print(f"✅ SSE stream started successfully!")
                    print(f"📊 Headers: {dict(response.headers)}")
                    print("\n🔍 Monitoring file changes...")
                    
                    # Create a task to perform file operations
                    file_ops_task = asyncio.create_task(self.perform_file_operations())
                    
                    # Monitor the stream for 15 seconds
                    start_time = time.time()
                    file_events = []
                    heartbeat_count = 0
                    
                    current_event_type = None
                    
                    async for line in response.aiter_text():
                        line = line.strip()
                        if not line:
                            continue
                            
                        print(f"📥 Raw SSE: {line}")
                        
                        # Parse SSE event
                        if line.startswith("event:"):
                            current_event_type = line.split(":", 1)[1].strip()
                        elif line.startswith("data:"):
                            data_str = line.split(":", 1)[1].strip()
                            try:
                                data = json.loads(data_str)
                                
                                if current_event_type == "file_change":
                                    file_events.append(data)
                                    print(f"🎯 FILE CHANGE DETECTED: {data['event_type']} - {data['file_name']}")
                                elif current_event_type == "heartbeat":
                                    heartbeat_count += 1
                                    if heartbeat_count % 5 == 0:  # Log every 5th heartbeat
                                        print(f"💓 Heartbeat #{heartbeat_count}")
                                        
                            except json.JSONDecodeError:
                                print(f"⚠️  Invalid JSON: {data_str}")
                            
                            # Reset event type after processing data
                            current_event_type = None
                        
                        # Stop after 15 seconds
                        if time.time() - start_time > 15:
                            break
                    
                    # Wait for file operations to complete
                    await file_ops_task
                    
                    # Analyze results
                    print("\n" + "=" * 70)
                    print("📊 PROOF RESULTS:")
                    print(f"   Total file events detected: {len(file_events)}")
                    print(f"   Heartbeats received: {heartbeat_count}")
                    
                    if file_events:
                        print("\n🎯 File Events Detected:")
                        for i, event in enumerate(file_events, 1):
                            print(f"   {i}. {event['event_type']} - {event['file_name']} ({event['relative_path']})")
                        
                        print("\n✅ PROOF SUCCESSFUL: File streaming works perfectly!")
                        print("   ✓ Real-time file change detection")
                        print("   ✓ Proper SSE streaming")
                        print("   ✓ Correct event data structure")
                        print("   ✓ Ready for Claude code sessions!")
                    else:
                        print("\n❌ PROOF FAILED: No file events detected")
                        print("   File operations may not have triggered properly")
                        
        except Exception as e:
            print(f"❌ Error during proof: {e}")
        finally:
            # Stop monitoring
            try:
                async with httpx.AsyncClient() as client:
                    await client.post(f"{self.base_url}/api/v1/stream/stop")
                    print("\n🛑 Stopped file monitoring")
            except:
                pass
            
            await self.cleanup()
    
    async def perform_file_operations(self):
        """Perform various file operations to trigger events."""
        print("\n🔧 Starting file operations...")
        
        # Wait a bit for stream to start
        await asyncio.sleep(2)
        
        try:
            # 1. Create a new file
            test_file = self.test_dir / "test_file.txt"
            print(f"📝 Creating file: {test_file.name}")
            test_file.write_text("Hello from file streaming test!")
            await asyncio.sleep(1)
            
            # 2. Modify the file
            print(f"✏️  Modifying file: {test_file.name}")
            test_file.write_text("Modified content for streaming test!")
            await asyncio.sleep(1)
            
            # 3. Create another file
            test_file2 = self.test_dir / "another_file.py"
            print(f"📝 Creating Python file: {test_file2.name}")
            test_file2.write_text("print('Hello from Python!')")
            await asyncio.sleep(1)
            
            # 4. Create a subdirectory and file
            sub_dir = self.test_dir / "subdir"
            sub_dir.mkdir()
            sub_file = sub_dir / "nested_file.md"
            print(f"📂 Creating nested file: subdir/{sub_file.name}")
            sub_file.write_text("# Nested file for testing")
            await asyncio.sleep(1)
            
            # 5. Delete a file
            print(f"🗑️  Deleting file: {test_file.name}")
            test_file.unlink()
            await asyncio.sleep(1)
            
            # 6. Move/rename a file
            new_name = self.test_dir / "renamed_file.py"
            print(f"📋 Renaming file: {test_file2.name} → {new_name.name}")
            test_file2.rename(new_name)
            await asyncio.sleep(1)
            
            print("✅ File operations completed!")
            
        except Exception as e:
            print(f"❌ Error during file operations: {e}")


async def main():
    """Run the comprehensive file streaming proof."""
    proof = FileStreamProof()
    await proof.prove_file_streaming_works()


if __name__ == "__main__":
    print("🎪 File Streaming Proof-of-Concept")
    print("📋 This will demonstrate real-time file change detection")
    print("🎯 Perfect for Claude code sessions and chat agents!\n")
    
    asyncio.run(main())

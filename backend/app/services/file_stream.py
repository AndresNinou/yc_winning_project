"""File streaming service for real-time file monitoring using SSE.

Provides Server-Sent Events (SSE) streaming for file system changes using watchdog.
Designed for real-time updates during Claude code sessions and chat agent interactions.
"""

import asyncio
import json
import os
from pathlib import Path
from typing import AsyncGenerator, Dict, Any, Optional
from threading import Thread
from queue import Queue, Empty

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from sse_starlette import EventSourceResponse

from app.core.config import settings
from app.core.log_config import logger

# Get the project root directory (parent of backend directory)
# This ensures it works on any machine regardless of absolute path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.resolve()


class FileChangeHandler(FileSystemEventHandler):
    """Handle file system events and queue them for SSE streaming."""
    
    def __init__(self, event_queue: Queue):
        """Initialize the handler with an event queue.
        
        Args:
            event_queue: Queue to store file system events
        """
        super().__init__()
        self.event_queue = event_queue
        self.logger = logger
        
    def on_any_event(self, event: FileSystemEvent) -> None:
        """Handle any file system event.
        
        Args:
            event: File system event from watchdog
        """
        # Convert paths to string for consistent handling
        src_path = str(event.src_path)
        
        # Skip directory events and hidden files
        if event.is_directory or self._is_hidden_file(src_path):
            return
            
        # Use time.time() instead of asyncio event loop time
        import time
        
        # Create event data
        event_data = {
            "id": f"{event.event_type}_{hash(src_path)}_{src_path.split('/')[-1]}",
            "event_type": event.event_type,
            "src_path": src_path,
            "timestamp": time.time(),
            "file_name": os.path.basename(src_path),
            "relative_path": self._get_relative_path(src_path)
        }
        
        # Add destination path for moved events
        if hasattr(event, 'dest_path'):
            dest_path = str(event.dest_path)
            event_data["dest_path"] = dest_path
            event_data["dest_file_name"] = os.path.basename(dest_path)
            event_data["dest_relative_path"] = self._get_relative_path(dest_path)
        
        try:
            self.event_queue.put_nowait(event_data)
            self.logger.info(f"📁 FILE EVENT QUEUED: {event_data['event_type']} - {event_data['file_name']}")
        except Exception as e:
            self.logger.error(f"Failed to queue file event: {e}")
    
    def _is_hidden_file(self, path: str) -> bool:
        """Check if file is hidden or should be ignored.
        
        Args:
            path: File path to check
            
        Returns:
            True if file should be ignored
        """
        ignored_patterns = {
            '.git', '.venv', '__pycache__', '.pytest_cache', 
            '.ruff_cache', 'node_modules', '.DS_Store'
        }
        
        path_parts = Path(path).parts
        # Only ignore if any part exactly matches ignored patterns
        # Don't ignore files that just start with . unless they're in ignored_patterns
        for part in path_parts:
            if part in ignored_patterns:
                return True
            # Only ignore hidden files/dirs that start with . and have common hidden names
            if part.startswith('.') and part in {'.git', '.venv', '.env', '.DS_Store'}:
                return True
        return False
    
    def _get_relative_path(self, absolute_path: str) -> str:
        """Get relative path from project root.
        
        Args:
            absolute_path: Absolute file path
            
        Returns:
            Relative path from project root
        """
        try:
            return str(Path(absolute_path).relative_to(PROJECT_ROOT))
        except ValueError:
            # If path is outside project, return basename
            return os.path.basename(absolute_path)


class FileStreamService:
    """Service for streaming file system changes via SSE."""
    
    def __init__(self):
        """Initialize the file stream service."""
        self.observer: Optional[Any] = None
        self.event_queue: Queue = Queue()
        self.handler = FileChangeHandler(self.event_queue)
        self.logger = logger
        
    def start_monitoring(self, watch_path: str) -> None:
        """Start monitoring a directory for file changes.
        
        Args:
            watch_path: Path to monitor for changes
        """
        if (self.observer is not None and 
            hasattr(self.observer, 'is_alive') and 
            callable(getattr(self.observer, 'is_alive', None)) and
            self.observer.is_alive()):
            self.logger.warning("File monitoring already active")
            return
            
        try:
            self.observer = Observer()
            self.observer.schedule(self.handler, watch_path, recursive=True)
            self.observer.start()
            self.logger.info(f"Started monitoring: {watch_path}")
        except Exception as e:
            self.logger.error(f"Failed to start file monitoring: {e}")
            raise
    
    def stop_monitoring(self) -> None:
        """Stop file system monitoring."""
        if (self.observer is not None and 
            hasattr(self.observer, 'is_alive') and 
            callable(getattr(self.observer, 'is_alive', None)) and
            self.observer.is_alive()):
            if hasattr(self.observer, 'stop') and callable(getattr(self.observer, 'stop', None)):
                self.observer.stop()
            if hasattr(self.observer, 'join') and callable(getattr(self.observer, 'join', None)):
                self.observer.join(timeout=5.0)
            self.logger.info("Stopped file monitoring")
    
    async def stream_events(self) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream file system events as SSE data.
        
        Yields:
            File system event data for SSE streaming
        """
        while True:
            try:
                # Non-blocking queue get with timeout
                event_data = self.event_queue.get_nowait()
                yield {
                    "event": "file_change",
                    "data": json.dumps(event_data)
                }
                self.event_queue.task_done()
            except Empty:
                # No events available, yield heartbeat
                yield {
                    "event": "heartbeat",
                    "data": json.dumps({"timestamp": asyncio.get_event_loop().time()})
                }
                await asyncio.sleep(1.0)  # Wait before checking again
            except Exception as e:
                self.logger.error(f"Error streaming file events: {e}")
                yield {
                    "event": "error",
                    "data": json.dumps({"error": str(e)})
                }
                await asyncio.sleep(1.0)


# Global service instance
file_stream_service = FileStreamService()


def create_file_stream_response(watch_path: str) -> EventSourceResponse:
    """Create an SSE response for file streaming.
    
    Args:
        watch_path: Directory path to monitor
        
    Returns:
        EventSourceResponse for SSE streaming
    """
    # Start monitoring the specified path
    file_stream_service.start_monitoring(watch_path)
    
    return EventSourceResponse(
        file_stream_service.stream_events(),
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )

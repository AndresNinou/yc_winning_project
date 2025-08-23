"""File streaming API endpoints for real-time file monitoring.

Provides SSE endpoints for streaming file system changes during Claude code sessions
and chat agent interactions. Uses watchdog for efficient file system monitoring.
"""

from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from sse_starlette import EventSourceResponse

from app.core.config import settings
from app.core.log_config import logger
from app.services.file_stream import create_file_stream_response, file_stream_service

# Get the project root directory (parent of backend directory)
# This ensures it works on any machine regardless of absolute path  
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.resolve()

router = APIRouter(prefix="/stream", tags=["file-streaming"])


@router.get("/files")
async def stream_file_changes(
    workspace_path: Optional[str] = Query(
        None, 
        description="Workspace path to monitor. Defaults to project root."
    ),
    session_id: Optional[str] = Query(
        None, 
        description="Session ID for tracking and logging purposes."
    )
) -> EventSourceResponse:
    """Stream file system changes via Server-Sent Events.
    
    This endpoint provides real-time file change notifications for Claude code sessions
    and chat agent interfaces. Uses efficient file system monitoring with proper
    filtering to avoid noise from build artifacts and hidden files.
    
    Args:
        workspace_path: Optional workspace path to monitor. If not provided,
                       monitors the entire project directory.
        session_id: Optional session identifier for logging and tracking.
        
    Returns:
        EventSourceResponse: SSE stream of file change events
        
    Raises:
        HTTPException: If the workspace path is invalid or inaccessible
        
    Events:
        - file_change: Actual file system changes (created, modified, deleted, moved)
        - heartbeat: Periodic keepalive messages
        - error: Error notifications
    """
    try:
        # Determine the path to monitor
        if workspace_path:
            # Validate and resolve the workspace path
            resolved_path = Path(workspace_path).resolve()
            if not resolved_path.exists():
                raise HTTPException(
                    status_code=400,
                    detail=f"Workspace path does not exist: {workspace_path}"
                )
            if not resolved_path.is_dir():
                raise HTTPException(
                    status_code=400,
                    detail=f"Workspace path is not a directory: {workspace_path}"
                )
            watch_path = str(resolved_path)
        else:
            # Default to project root (parent of backend directory)
            watch_path = str(PROJECT_ROOT)
        
        # Log the streaming session start
        logger.info(
            f"Starting file stream for path: {watch_path}"
            + (f" (session: {session_id})" if session_id else "")
        )
        
        # Create and return the SSE response
        return create_file_stream_response(watch_path)
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Failed to start file streaming: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start file streaming: {str(e)}"
        )


@router.post("/stop")
async def stop_file_streaming(
    session_id: Optional[str] = Query(
        None,
        description="Session ID to stop streaming for."
    )
) -> dict:
    """Stop file system monitoring.
    
    Gracefully stops the file system monitoring service. This is useful
    for cleanup when a Claude code session or chat agent session ends.
    
    Args:
        session_id: Optional session identifier for logging purposes.
        
    Returns:
        dict: Status message confirming the stop operation
    """
    try:
        logger.info(
            f"Stopping file stream"
            + (f" for session: {session_id}" if session_id else "")
        )
        
        file_stream_service.stop_monitoring()
        
        return {
            "status": "success",
            "message": "File streaming stopped successfully",
            "session_id": session_id
        }
        
    except Exception as e:
        logger.error(f"Failed to stop file streaming: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to stop file streaming: {str(e)}"
        )


@router.get("/status")
async def get_streaming_status() -> dict:
    """Get current file streaming status.
    
    Returns information about the current file monitoring state,
    including whether monitoring is active and basic statistics.
    
    Returns:
        dict: Current streaming status and statistics
    """
    try:
        observer_alive = (
            file_stream_service.observer is not None 
            and hasattr(file_stream_service.observer, 'is_alive')
            and callable(getattr(file_stream_service.observer, 'is_alive', None))
            and file_stream_service.observer.is_alive()
        )
        
        queue_size = file_stream_service.event_queue.qsize()
        
        return {
            "status": "active" if observer_alive else "inactive",
            "monitoring_active": observer_alive,
            "queued_events": queue_size,
            "service_info": {
                "observer_alive": observer_alive,
                "queue_empty": file_stream_service.event_queue.empty()
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get streaming status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get streaming status: {str(e)}"
        )

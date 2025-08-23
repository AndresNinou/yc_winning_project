"""Claude Code SDK routes for enhanced Claude integration.

Provides endpoints for both streaming and non-streaming Claude Code SDK interactions.
Includes Server-Sent Events (SSE) support and tool usage capabilities.
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from fastapi.params import Depends
from loguru import logger
import json

from app.services.claude import claude_service, ClaudeRequest, ClaudeResponse
from app.core.config import settings


router = APIRouter(prefix="/claude", tags=["claude"])


@router.post("/chat", response_model=ClaudeResponse)
async def chat_with_claude(request: ClaudeRequest) -> ClaudeResponse:
    """Send a prompt to Claude Code SDK and get a complete response.
    
    Args:
        request: The Claude request with prompt and parameters
        
    Returns:
        ClaudeResponse: Complete response from Claude Code SDK
        
    Raises:
        HTTPException: If the API call fails
    """
    try:
        logger.info(f"Claude Code SDK chat request: {request.prompt[:100]}...")
        response = await claude_service.generate_response(request)
        logger.info("Claude Code SDK chat response generated successfully")
        return response
        
    except Exception as e:
        logger.error(f"Claude Code SDK chat failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Claude Code SDK error: {str(e)}"
        )


@router.post("/stream")
async def stream_chat_with_claude(request: ClaudeRequest):
    """Stream a conversation with Claude Code SDK using Server-Sent Events.
    
    Args:
        request: The Claude request with prompt and parameters
        
    Returns:
        StreamingResponse: SSE stream of Claude Code SDK response
        
    Raises:
        HTTPException: If the API call fails
    """
    try:
        logger.info(f"Claude Code SDK streaming request: {request.prompt[:100]}...")
        
        async def generate_sse():
            """Generate Server-Sent Events for Claude Code SDK message-level streaming."""
            try:
                async for chunk in claude_service.generate_stream(request):
                    # Parse the chunk which is now JSON from our service
                    try:
                        chunk_data = json.loads(chunk)
                        
                        # Handle different chunk types from enhanced Claude Code SDK streaming
                        chunk_type = chunk_data.get("type")
                        
                        if chunk_type == "message_info":
                            # Message progression info
                            progress_data = {
                                'type': 'progress',
                                'message_type': chunk_data.get('message_type'),
                                'timestamp': chunk_data.get('timestamp', 0)
                            }
                            sse_data = f"data: {json.dumps(progress_data)}\n\n"
                            yield sse_data
                            
                        elif chunk_type == "text_block":
                            # Pure Claude Code SDK - complete text blocks as received
                            content_data = {
                                'type': 'content',
                                'content': chunk_data.get('content', ''),
                                'block_index': chunk_data.get('block_index', 0)
                            }
                            sse_data = f"data: {json.dumps(content_data)}\n\n"
                            yield sse_data
                            
                        elif chunk_type == "tool_execution":
                            # Tool execution info
                            tool_data = {
                                'type': 'tool_use',
                                'tool_name': chunk_data.get('tool_name'),
                                'tool_input': chunk_data.get('tool_input', ''),
                                'status': chunk_data.get('status', 'executing')
                            }
                            sse_data = f"data: {json.dumps(tool_data)}\n\n"
                            yield sse_data
                            
                        elif chunk_type == "stream_complete":
                            # Stream completion
                            complete_data = {
                                'type': 'complete',
                                'final_content': chunk_data.get('total_content', '')
                            }
                            sse_data = f"data: {json.dumps(complete_data)}\n\n"
                            yield sse_data
                            
                        elif chunk_data.get("type") in ["cli_error", "process_error", "api_error"]:
                            # Error handling
                            error_data = {
                                'type': 'error',
                                'error': chunk_data.get('error', 'Unknown error'),
                                'error_type': chunk_data.get('type')
                            }
                            sse_data = f"data: {json.dumps(error_data)}\n\n"
                            yield sse_data
                            return
                            
                    except json.JSONDecodeError:
                        # Fallback for plain text chunks (shouldn't happen with new implementation)
                        sse_data = f"data: {json.dumps({'content': chunk, 'type': 'content'})}\n\n"
                        yield sse_data
                
                # Send completion event
                completion_data = f"data: {json.dumps({'type': 'done'})}\n\n"
                yield completion_data
                
            except Exception as e:
                # Send error event
                error_data = f"data: {json.dumps({'error': str(e), 'type': 'error'})}\n\n"
                yield error_data
        
        return StreamingResponse(
            generate_sse(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Cache-Control",
            }
        )
        
    except Exception as e:
        logger.error(f"Claude Code SDK streaming setup failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Claude Code SDK streaming error: {str(e)}"
        )


@router.get("/health")
async def claude_health_check() -> Dict[str, Any]:
    """Health check for Claude Code SDK service.
    
    Returns:
        Dict containing service status and configuration info
    """
    try:
        # Simple health check - verify service is initialized and CLI available
        import os
        api_key_configured = bool(settings.ANTHOPIC_API_KEY or os.environ.get("ANTHROPIC_API_KEY"))
        
        # Check if Claude Code CLI is available
        import subprocess
        try:
            subprocess.run(["claude", "--version"], capture_output=True, check=True)
            cli_available = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            cli_available = False
        
        return {
            "service": "claude-code-sdk",
            "status": "healthy" if api_key_configured and cli_available else "degraded",
            "api_key_configured": api_key_configured,
            "cli_available": cli_available,
            "available_tools": [
                "Read", "Write", "Bash", "Search", "StrReplace",
                "CreateFile", "ListDir", "ViewFile"
            ],
            "permission_modes": [
                "default", "acceptEdits", "bypassPermissions", "plan"
            ]
        }
        
    except Exception as e:
        logger.error(f"Claude Code SDK health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Claude Code SDK service unhealthy: {str(e)}"
        )

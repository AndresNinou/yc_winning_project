"""Claude Code SDK service for enhanced Claude integration.

Provides async streaming Claude Code interactions with tool support,
proper error handling and configuration management.
"""

import asyncio
import time
from typing import AsyncGenerator, Dict, Any, Optional, List, Literal, cast
from claude_code_sdk import query, ClaudeCodeOptions
from claude_code_sdk.types import (
    AssistantMessage, TextBlock, ToolUseBlock, ToolResultBlock, 
    ThinkingBlock, Message, ResultMessage, SystemMessage, UserMessage
)
from app.services.workspace_manager import workspace_manager
from claude_code_sdk import (
    ClaudeSDKError,
    CLINotFoundError,
    CLIConnectionError,
    ProcessError,
    CLIJSONDecodeError,
)
from pydantic import BaseModel
import json
from pathlib import Path

from app.core.config import settings
from loguru import logger


class MCPServerConfig(BaseModel):
    """Configuration for an MCP server."""
    type: Literal["stdio", "sse", "http"] = "stdio"
    command: Optional[str] = None
    args: Optional[List[str]] = None
    env: Optional[Dict[str, str]] = None
    url: Optional[str] = None  # For SSE/HTTP transport
    headers: Optional[Dict[str, str]] = None  # For HTTP transport


class ClaudeRequest(BaseModel):
    """Request model for Claude Code SDK calls with MCP server support."""
    
    prompt: str
    system_prompt: Optional[str] = None
    max_turns: int = 300
    allowed_tools: Optional[List[str]] = None
    permission_mode: Literal["acceptEdits", "bypassPermissions", "default", "plan"] = "default"
    cwd: Optional[str] = None
    conversation_id: Optional[str] = None  # For maintaining conversation state
    
    # MCP Server Configuration
    mcp_servers: Optional[Dict[str, MCPServerConfig]] = None
    mcp_config_file: Optional[str] = None  # Path to .mcp.json file
    permission_prompt_tool_name: Optional[str] = None  # Custom permission prompt tool


class ClaudeResponse(BaseModel):
    """Response from Claude Code SDK."""
    response: str
    conversation_id: str
    workspace_path: Optional[str] = None
    workspace_stats: Optional[Dict[str, Any]] = None


class ClaudeService:
    """Service for interacting with Claude Code SDK with conversation state management."""
    
    def __init__(self):
        """Initialize Claude Code service."""
        # Claude Code SDK uses environment variables or CLI authentication
        # We'll set the API key as environment variable if needed
        if settings.ANTHOPIC_API_KEY:
            import os
            os.environ["ANTHROPIC_API_KEY"] = settings.ANTHOPIC_API_KEY
        
        # Store active conversation sessions
        # Each conversation_id maps to its conversation state
        self.conversation_history: Dict[str, List[str]] = {}
        self.session_locks: Dict[str, asyncio.Lock] = {}
        
        logger.info("Claude Code service initialized")

    async def prepare_mcp_servers(self, request: ClaudeRequest, workspace_path: str) -> Optional[Dict[str, Any]]:
        """
        Prepare MCP server configuration for Claude Code SDK.
        
        Args:
            request: The Claude request with MCP server configuration
            workspace_path: The conversation workspace path
            
        Returns:
            Dict containing MCP server configurations or None
        """
        mcp_servers = {}
        
        # Load from .mcp.json file if specified
        if request.mcp_config_file:
            try:
                config_path = Path(workspace_path) / request.mcp_config_file
                if config_path.exists():
                    with open(config_path, 'r') as f:
                        config_data = json.load(f)
                        if 'mcpServers' in config_data:
                            mcp_servers.update(config_data['mcpServers'])
                            logger.info(f"Loaded MCP servers from {config_path}: {list(mcp_servers.keys())}")
            except Exception as e:
                logger.warning(f"Failed to load MCP config file {request.mcp_config_file}: {e}")
        
        # Add servers from request configuration
        if request.mcp_servers:
            for server_name, server_config in request.mcp_servers.items():
                server_dict = {}
                
                # Handle different transport types
                if server_config.type == "stdio":
                    server_dict["type"] = "stdio"
                    if server_config.command:
                        server_dict["command"] = server_config.command
                    if server_config.args:
                        server_dict["args"] = server_config.args
                    if server_config.env:
                        server_dict["env"] = server_config.env
                        
                elif server_config.type == "sse":
                    server_dict["type"] = "sse"
                    if server_config.url:
                        server_dict["url"] = server_config.url
                    if server_config.headers:
                        server_dict["headers"] = server_config.headers
                        
                elif server_config.type == "http":
                    server_dict["type"] = "http"
                    if server_config.url:
                        server_dict["url"] = server_config.url
                    if server_config.headers:
                        server_dict["headers"] = server_config.headers
                
                mcp_servers[server_name] = server_dict
                logger.info(f"Added MCP server '{server_name}' with type '{server_config.type}'")
        
        # Look for default .mcp.json in workspace
        default_mcp_file = Path(workspace_path) / ".mcp.json"
        if default_mcp_file.exists():
            try:
                with open(default_mcp_file, 'r') as f:
                    config_data = json.load(f)
                    if 'mcpServers' in config_data:
                        # Merge with existing servers (request config takes precedence)
                        for server_name, server_config in config_data['mcpServers'].items():
                            if server_name not in mcp_servers:
                                mcp_servers[server_name] = server_config
                                logger.info(f"Loaded default MCP server '{server_name}' from workspace .mcp.json")
            except Exception as e:
                logger.warning(f"Failed to load default .mcp.json from workspace: {e}")
        
        return mcp_servers if mcp_servers else None

    async def generate_response(self, request: ClaudeRequest) -> ClaudeResponse:
        """Generate a non-streaming response from Claude Code SDK WITH CONVERSATION MEMORY.
        
        KEY FIX: Now uses conversation context building for memory continuity.
        
        Args:
            request: The Claude request parameters
            
        Returns:
            ClaudeResponse with the generated content and metadata
        """
        try:
            conversation_id = request.conversation_id or "default"
            
            # Build conversation context for memory continuity
            full_prompt = await self.build_conversation_context(conversation_id, request.prompt)
            
            # Prepare MCP servers configuration
            mcp_servers = await self.prepare_mcp_servers(request, workspace_path)
            
            # Prepare Claude Code options with MCP server support
            options = ClaudeCodeOptions(
                system_prompt=request.system_prompt or "You are Claude, a helpful AI assistant with MCP tool access. Maintain conversation continuity based on the context provided.",
                max_turns=300,  # Standard high limit to ensure tool execution cycles can complete
                allowed_tools=request.allowed_tools or ["Read", "Write", "Bash", "ListDir", "Search", "StrReplace"],
                permission_mode=request.permission_mode,
                cwd=Path(request.cwd) if request.cwd else Path.cwd(),
                mcp_servers=mcp_servers,  # Add MCP server configuration
                permission_prompt_tool_name=request.permission_prompt_tool_name  # Custom permission prompt
            )
            
            # Ensure conversation workspace exists and set as working directory
            workspace_path = workspace_manager.ensure_workspace_exists(conversation_id)
            logger.info(f"Conversation {conversation_id} workspace: {workspace_path}")
            
            # Update Claude Code SDK options to use conversation workspace as cwd
            options.cwd = workspace_path
            
            logger.info(f"Claude Code SDK call with context: {conversation_id} - {request.prompt[:50]}...")
            
            # Call Claude Code SDK with conversation context and workspace
            content_parts = []
            
            async for message in query(prompt=full_prompt, options=options):
                logger.info(f"Received {type(message).__name__}")
                
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            content_parts.append(block.text)
            
            # Combine all content parts
            final_content = '\n\n'.join(content_parts) if content_parts else "No content generated"
            
            # Store this conversation turn for future context
            await self.store_conversation_turn(conversation_id, request.prompt, final_content)
            
            # Get workspace stats for response
            workspace_stats = workspace_manager.get_workspace_stats(conversation_id)
            
            logger.info(f"Claude Code SDK call completed with context stored: {conversation_id}")
            
            return ClaudeResponse(
                response=final_content,
                conversation_id=conversation_id,
                workspace_path=workspace_stats.get("path") if workspace_stats else None,
                workspace_stats=workspace_stats
            )
            
        except CLINotFoundError:
            logger.error("Claude Code CLI not found. Please install: npm install -g @anthropic-ai/claude-code")
            raise Exception("Claude Code CLI not installed")
        except ProcessError as e:
            logger.error(f"Claude Code process failed: {e}")
            raise Exception(f"Claude Code process error: {str(e)}")
        except Exception as e:
            logger.error(f"Claude Code SDK call failed: {str(e)}")
            raise

    async def build_conversation_context(self, conversation_id: str, current_prompt: str) -> str:
        """Build conversation context for Claude Code SDK.
        
        PURE Claude Code SDK approach: Since we can't maintain persistent sessions
        across HTTP requests, we build conversation history and pass it as context
        in each new query() call.
        """
        if conversation_id not in self.conversation_history:
            self.conversation_history[conversation_id] = []
            
        history = self.conversation_history[conversation_id]
        
        if not history:
            # First message in conversation
            full_prompt = current_prompt
        else:
            # Build conversation context from history
            context_parts = ["Previous conversation context:"]
            context_parts.extend(history)
            context_parts.append(f"\nCurrent user message: {current_prompt}")
            full_prompt = "\n".join(context_parts)
        
        logger.info(f"Conversation {conversation_id}: Built context with {len(history)} previous messages")
        return full_prompt
    
    async def store_conversation_turn(self, conversation_id: str, user_message: str, assistant_response: str):
        """Store conversation turn for future context building."""
        if conversation_id not in self.conversation_history:
            self.conversation_history[conversation_id] = []
            
        self.conversation_history[conversation_id].extend([
            f"User: {user_message}",
            f"Assistant: {assistant_response}"
        ])
        
        # Keep only last 10 turns to avoid overwhelming context
        if len(self.conversation_history[conversation_id]) > 20:  # 10 turns = 20 messages
            self.conversation_history[conversation_id] = self.conversation_history[conversation_id][-20:]
    
    async def execute_with_context(self, conversation_id: str, request: ClaudeRequest) -> AsyncGenerator[str, None]:
        """Execute Claude Code SDK query with conversation context.
        
        PURE Claude Code SDK: Each call is a fresh query() but with conversation history
        as context to maintain memory across HTTP requests.
        """
        # Build conversation context
        full_prompt = await self.build_conversation_context(conversation_id, request.prompt)
        
        # Ensure conversation workspace exists first
        workspace_path = workspace_manager.ensure_workspace_exists(conversation_id)
        logger.info(f"Conversation {conversation_id} workspace: {workspace_path}")
        
        # Prepare MCP servers configuration
        mcp_servers = await self.prepare_mcp_servers(request, workspace_path)
        
        # Configure Claude Code options with MCP server support
        options = ClaudeCodeOptions(
            system_prompt=request.system_prompt or "You are Claude, a helpful AI assistant with MCP tool access. Maintain conversation continuity based on the context provided.",
            max_turns=300,  # Standard high limit to ensure tool execution cycles can complete
            allowed_tools=request.allowed_tools or ["Read", "Write", "Bash", "ListDir", "Search", "StrReplace"],
            permission_mode=request.permission_mode,
            cwd=Path(workspace_path),  # Use workspace path directly
            mcp_servers=mcp_servers,  # Add MCP server configuration
            permission_prompt_tool_name=request.permission_prompt_tool_name  # Custom permission prompt
        )
        
        logger.info(f"Executing Claude Code SDK query with conversation context: {conversation_id}")
        logger.info(f"MCP servers configured: {list(mcp_servers.keys()) if mcp_servers else 'None'}")
        
        assistant_response_parts: List[str] = []
        
        try:
            # Execute Claude Code SDK query with context and conversation-specific workspace
            async for message in query(prompt=full_prompt, options=options):
                message_type = type(message).__name__
                logger.info(f"Conversation {conversation_id}: Received {message_type}")
                
                # Yield message info
                yield json.dumps({
                    "type": "message_info",
                    "message_type": message_type
                })
                
                if isinstance(message, AssistantMessage):
                    for block_idx, block in enumerate(message.content):
                        if isinstance(block, TextBlock):
                            text_content = block.text
                            assistant_response_parts.append(text_content)
                            
                            # Yield complete text block
                            yield json.dumps({
                                "type": "text_block",
                                "content": text_content,
                                "block_index": block_idx
                            })
                        
                        elif isinstance(block, ToolUseBlock):
                            yield json.dumps({
                                "type": "tool_execution",
                                "tool_name": block.name,
                                "status": "executing"
                            })
                
                elif isinstance(message, UserMessage) and hasattr(message, 'content'):
                    # Only handle UserMessage with content (other message types may not have content)
                    content_str = str(message.content)
                    assistant_response_parts.append(content_str)
                    
                    yield json.dumps({
                        "type": "other_content",
                        "message_type": message_type,
                        "content": content_str[:500]
                    })
            
            # Store this conversation turn for future context
            full_assistant_response = " ".join(assistant_response_parts)
            await self.store_conversation_turn(conversation_id, request.prompt, full_assistant_response)
            
        except CLINotFoundError:
            logger.error("Claude Code CLI not found")
            yield json.dumps({"error": "Claude Code CLI not installed", "type": "cli_error"})
        except ProcessError as e:
            logger.error(f"Claude Code process failed: {e}")
            yield json.dumps({"error": str(e), "type": "process_error"})
        except Exception as e:
            logger.error(f"Claude Code SDK call failed: {str(e)}")
            yield json.dumps({"error": str(e), "type": "api_error"})
    
    async def generate_stream(self, request: ClaudeRequest) -> AsyncGenerator[str, None]:
        """Generate streaming response using PURE Claude Code SDK with conversation context.
        
        KEY FIX: Maintains conversation memory by building context from previous messages
        and passing it to each new Claude Code SDK query() call.
        """
        conversation_id = request.conversation_id or "default"
        
        # Use conversation context approach for memory continuity
        async for chunk in self.execute_with_context(conversation_id, request):
            yield chunk


    def _message_to_dict(self, message: Message) -> Dict[str, Any]:
        """Convert Claude Code SDK message to dictionary for JSON serialization."""
        return {
            "type": type(message).__name__,
            "content": getattr(message, 'content', None),
            "role": getattr(message, 'role', None)
        }


# Global service instance
claude_service = ClaudeService()

"""
Conversation Workspace Manager

Manages isolated working directories for each Claude Code conversation.
Creates, tracks, and manages conversation-specific folders where Claude Code
tools operate, ensuring complete isolation between different chat sessions.
"""

import os
import shutil
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from loguru import logger

# Get the backend directory (where this file is located)
BACKEND_DIR = Path(__file__).parent.parent.parent
DEFAULT_WORKSPACE_DIR = BACKEND_DIR / "workspaces"


class ConversationWorkspaceManager:
    """Manages isolated workspaces for Claude Code conversations."""
    
    def __init__(self, base_workspace_dir: Optional[str] = None):
        """
        Initialize the workspace manager.
        
        Args:
            base_workspace_dir: Base directory where conversation folders are created.
                              If None, uses ./workspaces relative to backend directory.
        """
        if base_workspace_dir is None:
            self.base_dir = DEFAULT_WORKSPACE_DIR
        else:
            # If provided, resolve relative to backend directory
            if not Path(base_workspace_dir).is_absolute():
                self.base_dir = BACKEND_DIR / base_workspace_dir
            else:
                self.base_dir = Path(base_workspace_dir)
        
        self.active_workspaces: Dict[str, Dict] = {}
        
        # Ensure base directory exists
        self.base_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Workspace manager initialized with base dir: {self.base_dir.resolve()}")
    
    def create_conversation_workspace(self, conversation_id: Optional[str] = None) -> str:
        """
        Create a new isolated workspace for a conversation.
        
        Args:
            conversation_id: Optional conversation ID, will generate one if not provided
            
        Returns:
            conversation_id: The conversation ID for this workspace
        """
        if not conversation_id:
            conversation_id = f"conv_{int(time.time())}_{str(uuid.uuid4())[:8]}"
        
        # Create conversation-specific directory
        workspace_path = self.base_dir / conversation_id
        workspace_path.mkdir(parents=True, exist_ok=True)
        
        # Create standard subdirectories
        (workspace_path / "files").mkdir(exist_ok=True)
        (workspace_path / "outputs").mkdir(exist_ok=True)
        (workspace_path / "logs").mkdir(exist_ok=True)
        
        # Track the workspace
        workspace_info = {
            "path": str(workspace_path),
            "created_at": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat(),
            "file_count": 0
        }
        
        self.active_workspaces[conversation_id] = workspace_info
        
        # Create a README for the workspace
        readme_content = f"""# Claude Code Conversation Workspace
        
Conversation ID: {conversation_id}
Created: {workspace_info['created_at']}

## Structure:
- `files/` - Working files for this conversation
- `outputs/` - Generated outputs and results
- `logs/` - Conversation-specific logs

This workspace is isolated from other conversations.
"""
        
        readme_path = workspace_path / "README.md"
        readme_path.write_text(readme_content.strip())
        
        logger.info(f"Created workspace for conversation {conversation_id} at {workspace_path}")
        return conversation_id
    
    def get_workspace_path(self, conversation_id: str) -> Optional[str]:
        """
        Get the workspace path for a conversation.
        
        Args:
            conversation_id: The conversation ID
            
        Returns:
            workspace_path: Path to the conversation workspace, None if not found
        """
        if conversation_id in self.active_workspaces:
            # Update last accessed time
            self.active_workspaces[conversation_id]["last_accessed"] = datetime.now().isoformat()
            return self.active_workspaces[conversation_id]["path"]
        
        # Check if workspace exists on disk but not in memory
        workspace_path = self.base_dir / conversation_id
        if workspace_path.exists():
            # Restore workspace info
            workspace_info = {
                "path": str(workspace_path),
                "created_at": datetime.fromtimestamp(workspace_path.stat().st_ctime).isoformat(),
                "last_accessed": datetime.now().isoformat(),
                "file_count": len(list(workspace_path.rglob("*")))
            }
            self.active_workspaces[conversation_id] = workspace_info
            logger.info(f"Restored workspace for conversation {conversation_id}")
            return str(workspace_path)
        
        return None
    
    def ensure_workspace_exists(self, conversation_id: str) -> str:
        """
        Ensure a workspace exists for the conversation, create if needed.
        
        Args:
            conversation_id: The conversation ID
            
        Returns:
            workspace_path: Path to the conversation workspace
        """
        workspace_path = self.get_workspace_path(conversation_id)
        if workspace_path:
            return workspace_path
        
        # Create new workspace
        self.create_conversation_workspace(conversation_id)
        workspace_path = self.get_workspace_path(conversation_id)
        if workspace_path is None:
            raise RuntimeError(f"Failed to create workspace for conversation {conversation_id}")
        return workspace_path
    
    def cleanup_old_workspaces(self, max_age_hours: int = 24) -> int:
        """
        Clean up old conversation workspaces.
        
        Args:
            max_age_hours: Maximum age in hours before workspace is cleaned up
            
        Returns:
            cleaned_count: Number of workspaces cleaned up
        """
        cleaned_count = 0
        current_time = time.time()
        cutoff_time = current_time - (max_age_hours * 3600)
        
        for conversation_id in list(self.active_workspaces.keys()):
            workspace_info = self.active_workspaces[conversation_id]
            workspace_path = Path(workspace_info["path"])
            
            # Check if workspace is old enough to clean up
            if workspace_path.exists():
                last_modified = workspace_path.stat().st_mtime
                if last_modified < cutoff_time:
                    try:
                        shutil.rmtree(workspace_path)
                        del self.active_workspaces[conversation_id]
                        cleaned_count += 1
                        logger.info(f"Cleaned up old workspace: {conversation_id}")
                    except Exception as e:
                        logger.error(f"Failed to cleanup workspace {conversation_id}: {e}")
        
        return cleaned_count
    
    def get_workspace_stats(self, conversation_id: str) -> Optional[Dict]:
        """
        Get statistics about a conversation workspace.
        
        Args:
            conversation_id: The conversation ID
            
        Returns:
            stats: Workspace statistics, None if workspace not found
        """
        workspace_path = self.get_workspace_path(conversation_id)
        if not workspace_path:
            return None
        
        path = Path(workspace_path)
        if not path.exists():
            return None
        
        stats = {
            "conversation_id": conversation_id,
            "path": workspace_path,
            "size_bytes": sum(f.stat().st_size for f in path.rglob("*") if f.is_file()),
            "file_count": len([f for f in path.rglob("*") if f.is_file()]),
            "folder_count": len([f for f in path.rglob("*") if f.is_dir()]),
            "created_at": self.active_workspaces[conversation_id]["created_at"],
            "last_accessed": self.active_workspaces[conversation_id]["last_accessed"]
        }
        
        return stats
    
    def list_active_workspaces(self) -> Dict[str, Dict]:
        """
        List all active conversation workspaces.
        
        Returns:
            workspaces: Dictionary of conversation_id -> workspace_info
        """
        return self.active_workspaces.copy()


# Global workspace manager instance
workspace_manager = ConversationWorkspaceManager()

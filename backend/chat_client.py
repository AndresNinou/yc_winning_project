#!/usr/bin/env python3
"""
Interactive Claude Code SDK Chat Client

A persistent terminal client for having conversations with Claude Code SDK.
Maintains conversation state and provides real-time SSE streaming responses.
"""

import asyncio
import json
import httpx
import sys
import time
from typing import List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.prompt import Prompt
from rich.markdown import Markdown
from rich import box


class InteractiveChatClient:
    """Interactive chat client for Claude Code SDK conversations."""
    
    def __init__(self, base_url: str = "https://integral-mozilla-ref-db.trycloudflare.com"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1/claude"
        self.console = Console()
        self.conversation_history: List[dict] = []
        self.tools_enabled = True
        self.conversation_id: Optional[str] = None
        self.workspace_path: Optional[str] = None
        self.available_tools = [
            "ListDir", "Read", "Write", "Search", 
            "StrReplace", "CreateFile", "ViewFile", "Bash"
        ]
    
    def print_welcome(self):
        """Print welcome message and instructions."""
        welcome = Panel.fit(
            "[bold cyan]💬 Claude Code SDK Interactive Chat with Workspace Isolation[/bold cyan]\n\n"
            "[dim]Commands:[/dim]\n"
            "  [bold]/help[/bold]      - Show this help\n"
            "  [bold]/tools[/bold]     - Show available tools with parameters\n"
            "  [bold]/workspace[/bold] - Show current workspace info\n"
            "  [bold]/files[/bold]     - List files in workspace\n"
            "  [bold]/clear[/bold]     - Clear conversation history\n"
            "  [bold]/history[/bold]   - Show conversation history\n"
            "  [bold]/demo[/bold]      - Run workspace isolation demo\n"
            "  [bold]/quit[/bold]      - Exit chat\n\n"
            "[dim]🗂️ Each conversation gets its own isolated workspace![/dim]\n"
            "[dim]Type your message and press Enter to chat with Claude![/dim]",
            border_style="cyan"
        )
        self.console.print(welcome)
        self.console.print()
    
    async def check_service_health(self) -> bool:
        """Check if Claude Code SDK service is healthy."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.api_base}/health")
                response.raise_for_status()
                health_data = response.json()
                
                status = health_data.get("status", "unknown")
                cli_available = health_data.get("cli_available", False)
                
                if status in ["healthy", "degraded"]:
                    tools_status = "✅ Available" if cli_available else "⚠️ Limited"
                    self.console.print(f"🩺 Service Status: [green]{status}[/green] | Tools: {tools_status}")
                    return True
                else:
                    self.console.print(f"[red]❌ Service unhealthy: {status}[/red]")
                    return False
                    
        except Exception as e:
            self.console.print(f"[red]❌ Cannot connect to Claude service: {e}[/red]")
            return False
    
    async def send_message_stream(self, message: str) -> str:
        """Send a message and receive streaming response."""
        
        payload = {
            "prompt": message,
            "conversation_id": self.conversation_id,  # Maintain conversation continuity
            "system_prompt": "You are Claude, a helpful AI assistant. Be conversational and engaging.",
            "max_turns": 300,
            "allowed_tools": self.available_tools if self.tools_enabled else [],
            "permission_mode": "default"
        }
        
        # Show thinking indicator
        self.console.print(f"[dim]🤔 Claude is thinking...[/dim]")
        
        response_content = ""
        messages_received = []
        tools_used = []
        workspace_info = None
        
        # Live display for streaming response
        live_text = Text()
        
        with Live(
            Panel(live_text, title="🤖 Claude", border_style="green"), 
            refresh_per_second=10
        ) as live:
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                try:
                    async with client.stream(
                        "POST",
                        f"{self.api_base}/stream",
                        json=payload,
                        headers={
                            "Content-Type": "application/json",
                            "Accept": "text/event-stream"
                        }
                    ) as response:
                        response.raise_for_status()
                        
                        start_time = time.time()
                        
                        async for line in response.aiter_lines():
                            if line.startswith("data: "):
                                try:
                                    event_data = json.loads(line[6:])
                                    event_type = event_data.get("type", "unknown")
                                    
                                    if event_type == "message_info":
                                        message_type = event_data.get("message_type", "Unknown")
                                        messages_received.append(message_type)
                                        # Don't show message info in the live display
                                        
                                    elif event_type == "content":
                                        content = event_data.get("content", "")
                                        response_content += content
                                        
                                        # Update live display with content
                                        live_text.plain = ""  # Clear previous
                                        live_text.append(response_content)
                                        live.update(Panel(
                                            Markdown(response_content) if len(response_content) > 50 else live_text, 
                                            title="🤖 Claude", 
                                            border_style="green"
                                        ))
                                        
                                    elif event_type == "tool_use":
                                        tool_name = event_data.get("tool_name", "Unknown")
                                        tools_used.append(tool_name)
                                        tool_info = f"\n\n🛠️ *Using tool: {tool_name}*"
                                        live_text.append(tool_info, style="dim italic")
                                        live.update(Panel(live_text, title="🤖 Claude", border_style="green"))
                                        
                                    elif event_type == "done":
                                        elapsed = time.time() - start_time
                                        # Capture workspace information if available
                                        if 'workspace_path' in event_data:
                                            workspace_info = event_data
                                            if not self.conversation_id and 'conversation_id' in event_data:
                                                self.conversation_id = event_data['conversation_id']
                                            if not self.workspace_path and 'workspace_path' in event_data:
                                                self.workspace_path = event_data['workspace_path']
                                        
                                        # Final update with complete response
                                        final_content = Markdown(response_content) if response_content else Text("No response")
                                        live.update(Panel(
                                            final_content, 
                                            title=f"🤖 Claude ({elapsed:.1f}s)", 
                                            border_style="green"
                                        ))
                                        break
                                        
                                    elif event_type == "error":
                                        error_msg = event_data.get("error", "Unknown error")
                                        live_text.append(f"\n❌ Error: {error_msg}", style="red")
                                        live.update(Panel(live_text, title="🤖 Claude - Error", border_style="red"))
                                        return f"Error: {error_msg}"
                                        
                                except json.JSONDecodeError:
                                    continue
                        
                        await asyncio.sleep(0.5)  # Brief pause to see final result
                        
                except Exception as e:
                    self.console.print(f"[red]❌ Request failed: {e}[/red]")
                    return f"Request failed: {e}"
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": message,
            "timestamp": time.time()
        })
        
        self.conversation_history.append({
            "role": "assistant", 
            "content": response_content,
            "timestamp": time.time(),
            "messages_received": messages_received,
            "tools_used": tools_used
        })
        
        return response_content
    
    def show_conversation_history(self):
        """Display conversation history."""
        if not self.conversation_history:
            self.console.print("[dim]No conversation history yet.[/dim]")
            return
        
        self.console.print(Panel.fit("[bold]📜 Conversation History[/bold]", border_style="blue"))
        
        for i, msg in enumerate(self.conversation_history, 1):
            role_icon = "👤" if msg["role"] == "user" else "🤖"
            role_color = "blue" if msg["role"] == "user" else "green"
            
            content_preview = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
            
            self.console.print(f"{i}. [{role_color}]{role_icon} {msg['role'].title()}[/{role_color}]: {content_preview}")
        
        self.console.print()
    
    def show_help(self):
        """Show help information."""
        help_text = Panel(
            "[bold]Available Commands:[/bold]\n\n"
            "  [bold cyan]/help[/bold cyan]      - Show this help message\n"
            "  [bold cyan]/tools[/bold cyan]     - Show available tools with parameters\n"
            "  [bold cyan]/workspace[/bold cyan] - Show current workspace info\n"
            "  [bold cyan]/files[/bold cyan]     - List files in workspace\n"
            "  [bold cyan]/demo[/bold cyan]      - Run workspace isolation demo\n"
            "  [bold cyan]/clear[/bold cyan]     - Clear conversation history\n"
            "  [bold cyan]/history[/bold cyan]   - Show conversation history\n"
            "  [bold cyan]/quit[/bold cyan]      - Exit the chat client\n\n"
            "[bold]🗂️ Workspace Features:[/bold]\n"
            "Each conversation gets its own isolated workspace where Claude can\n"
            "create, read, and modify files without affecting other conversations.\n\n"
            "[bold]Available Tools (when enabled):[/bold]\n" +
            ", ".join(self.available_tools) + "\n\n"
            "[dim]Just type your message to chat with Claude![/dim]",
            title="💡 Help",
            border_style="yellow"
        )
        self.console.print(help_text)
    
    async def show_available_tools(self):
        """Show detailed information about available Claude Code SDK tools."""
        tools_info = {
            "Read": {
                "description": "Read contents of files",
                "parameters": {
                    "path": "str - Path to the file to read",
                    "start_line": "int - Optional starting line number", 
                    "end_line": "int - Optional ending line number"
                },
                "example": "Read the file 'config.py' from lines 10 to 20"
            },
            "Write": {
                "description": "Create or write content to files",
                "parameters": {
                    "path": "str - Path where to write the file",
                    "content": "str - Content to write to the file"
                },
                "example": "Write 'Hello World!' to a file called 'greeting.txt'"
            },
            "Bash": {
                "description": "Execute shell commands in the workspace",
                "parameters": {
                    "command": "str - Shell command to execute",
                    "timeout": "int - Optional timeout in seconds"
                },
                "example": "Run 'ls -la' to list directory contents"
            },
            "ListDir": {
                "description": "List contents of directories", 
                "parameters": {
                    "path": "str - Directory path to list",
                    "recursive": "bool - Whether to list recursively"
                },
                "example": "List all files in the current directory"
            },
            "Search": {
                "description": "Search for text patterns in files",
                "parameters": {
                    "pattern": "str - Text pattern to search for",
                    "path": "str - Path to search in (file or directory)",
                    "case_sensitive": "bool - Whether search is case sensitive"
                },
                "example": "Search for 'function' in all Python files"
            },
            "StrReplace": {
                "description": "Replace text in files",
                "parameters": {
                    "path": "str - Path to the file",
                    "old_str": "str - Text to replace",
                    "new_str": "str - Replacement text"
                },
                "example": "Replace 'old_value' with 'new_value' in config.json"
            }
        }
        
        tools_display = "[bold]🛠️ Available Claude Code SDK Tools[/bold]\n\n"
        
        for tool_name, tool_info in tools_info.items():
            # Tool header
            tools_display += f"[bold cyan]{tool_name}[/bold cyan]\n"
            tools_display += f"  [dim]{tool_info['description']}[/dim]\n"
            
            # Parameters
            tools_display += "  [yellow]Parameters:[/yellow]\n"
            for param_name, param_desc in tool_info['parameters'].items():
                tools_display += f"    • [green]{param_name}[/green]: {param_desc}\n"
            
            # Example
            tools_display += f"  [yellow]Example:[/yellow] [dim italic]{tool_info['example']}[/dim italic]\n\n"
        
        # Status and current configuration
        tools_display += f"[bold]🔧 Current Configuration:[/bold]\n"
        tools_display += f"  Status: [green]{'Enabled' if self.tools_enabled else 'Disabled'}[/green]\n"
        tools_display += f"  Workspace: [cyan]{self.workspace_path or 'Not created yet'}[/cyan]\n"
        tools_display += f"  Conversation: [cyan]{self.conversation_id or 'New conversation'}[/cyan]\n\n"
        tools_display += "[dim]💡 Tools operate in isolated conversation workspaces for complete separation.[/dim]"
        
        tool_panel = Panel(
            tools_display,
            title="🛠️ Claude Code SDK Tools",
            border_style="cyan",
            expand=False
        )
        
        self.console.print(tool_panel)
    
    async def show_workspace_info(self):
        """Show current workspace information."""
        if not self.conversation_id or not self.workspace_path:
            self.console.print("[yellow]⚠️ No active workspace yet. Start a conversation to create one![/yellow]")
            return
        
        try:
            # Check if workspace path exists
            import os
            if os.path.exists(self.workspace_path):
                file_count = len([f for f in os.listdir(self.workspace_path) if os.path.isfile(os.path.join(self.workspace_path, f))])
                dir_count = len([d for d in os.listdir(self.workspace_path) if os.path.isdir(os.path.join(self.workspace_path, d))])
                
                workspace_info = Panel(
                    f"[bold]🗂️ Conversation Workspace[/bold]\n\n"
                    f"[cyan]Conversation ID:[/cyan] {self.conversation_id}\n"
                    f"[cyan]Workspace Path:[/cyan] {self.workspace_path}\n"
                    f"[cyan]Files:[/cyan] {file_count}\n"
                    f"[cyan]Directories:[/cyan] {dir_count}\n\n"
                    f"[dim]This workspace is isolated from other conversations.[/dim]",
                    title="🗂️ Workspace Info",
                    border_style="blue"
                )
                self.console.print(workspace_info)
            else:
                self.console.print("[red]❌ Workspace path not found![/red]")
        except Exception as e:
            self.console.print(f"[red]❌ Error checking workspace: {e}[/red]")
    
    async def list_workspace_files(self):
        """List files in the current workspace."""
        if not self.workspace_path:
            self.console.print("[yellow]⚠️ No active workspace yet. Start a conversation to create one![/yellow]")
            return
        
        try:
            import os
            if os.path.exists(self.workspace_path):
                files = []
                for root, dirs, filenames in os.walk(self.workspace_path):
                    for filename in filenames:
                        rel_path = os.path.relpath(os.path.join(root, filename), self.workspace_path)
                        size = os.path.getsize(os.path.join(root, filename))
                        files.append(f"  📄 {rel_path} ({size} bytes)")
                
                if files:
                    files_text = "\n".join(files)
                    file_panel = Panel(
                        f"[bold]📁 Workspace Files[/bold]\n\n{files_text}",
                        title="📁 Files",
                        border_style="green"
                    )
                else:
                    file_panel = Panel(
                        "[dim]No files in workspace yet.[/dim]",
                        title="📁 Files",
                        border_style="green"
                    )
                self.console.print(file_panel)
            else:
                self.console.print("[red]❌ Workspace path not found![/red]")
        except Exception as e:
            self.console.print(f"[red]❌ Error listing files: {e}[/red]")
    
    async def run_workspace_demo(self):
        """Run a demonstration of workspace isolation."""
        self.console.print("[bold cyan]🧪 Running Workspace Isolation Demo[/bold cyan]")
        
        demo_messages = [
            "Please create a file called 'test.txt' with the content 'Hello from this conversation!'",
            "List all files in the current directory", 
            "Create a subdirectory called 'demo' and put a file 'info.md' inside it with some sample content"
        ]
        
        for i, message in enumerate(demo_messages, 1):
            self.console.print(f"\n[bold]Demo Step {i}:[/bold] {message}")
            self.console.print("[dim]Press Enter to continue...[/dim]")
            input()  # Wait for user
            
            # Send the demo message
            await self.send_message_stream(message)
            self.console.print()
    
    async def run_chat(self):
        """Run the interactive chat loop."""
        
        self.print_welcome()
        
        # Check service health
        if not await self.check_service_health():
            self.console.print("[red]Cannot start chat - service unavailable.[/red]")
            return
        
        self.console.print("\n[green]✅ Ready to chat! Type your first message:[/green]\n")
        
        # Main chat loop
        while True:
            try:
                # Get user input
                user_input = Prompt.ask(
                    "[bold blue]You[/bold blue]",
                    console=self.console
                ).strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.startswith("/"):
                    command = user_input[1:].lower()
                    
                    if command == "help":
                        self.show_help()
                        continue
                        
                    elif command == "tools":
                        await self.show_available_tools()
                        continue
                        
                    elif command == "clear":
                        self.conversation_history.clear()
                        self.console.print("🗑️ Conversation history cleared")
                        continue
                        
                    elif command == "history":
                        self.show_conversation_history()
                        continue
                    
                    elif command == "workspace":
                        await self.show_workspace_info()
                        continue
                    
                    elif command == "files":
                        await self.list_workspace_files()
                        continue
                    
                    elif command == "demo":
                        await self.run_workspace_demo()
                        continue
                        
                    elif command in ["quit", "exit", "q"]:
                        self.console.print("[yellow]👋 Goodbye![/yellow]")
                        break
                        
                    else:
                        self.console.print(f"[red]Unknown command: {command}. Type /help for available commands.[/red]")
                        continue
                
                # Send message to Claude
                await self.send_message_stream(user_input)
                self.console.print()  # Add spacing
                
            except KeyboardInterrupt:
                self.console.print("\n[yellow]👋 Chat interrupted. Goodbye![/yellow]")
                break
            except EOFError:
                self.console.print("\n[yellow]👋 Chat ended. Goodbye![/yellow]")
                break
            except Exception as e:
                self.console.print(f"[red]❌ Unexpected error: {e}[/red]")


async def main():
    """Main entry point."""
    
    if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h"]:
        print("""
Interactive Claude Code SDK Chat Client

Usage:
  python chat_client.py           - Start interactive chat
  python chat_client.py --help    - Show this help

Features:
  • Real-time SSE streaming responses
  • Tool integration (file operations, bash commands)
  • Conversation history tracking  
  • Rich terminal UI with markdown support
  • Interactive commands (/help, /tools, /clear, etc.)
  
Commands during chat:
  /help     - Show available commands
  /tools    - Toggle tools on/off
  /clear    - Clear conversation history
  /history  - Show conversation history
  /quit     - Exit chat
        """)
        return
    
    try:
        client = InteractiveChatClient()
        await client.run_chat()
    except KeyboardInterrupt:
        Console().print("\n[yellow]Chat interrupted.[/yellow]")
    except Exception as e:
        Console().print(f"[red]❌ Chat client failed: {e}[/red]")


if __name__ == "__main__":
    asyncio.run(main())

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
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1/claude"
        self.console = Console()
        self.conversation_history: List[dict] = []
        self.tools_enabled = True
        self.available_tools = [
            "ListDir", "Read", "Write", "Search", 
            "StrReplace", "CreateFile", "ViewFile", "Bash"
        ]
    
    def print_welcome(self):
        """Print welcome message and instructions."""
        welcome = Panel.fit(
            "[bold cyan]💬 Claude Code SDK Interactive Chat[/bold cyan]\n\n"
            "[dim]Commands:[/dim]\n"
            "  [bold]/help[/bold]     - Show this help\n"
            "  [bold]/tools[/bold]    - Toggle tools on/off\n"
            "  [bold]/clear[/bold]    - Clear conversation history\n"
            "  [bold]/history[/bold]  - Show conversation history\n"
            "  [bold]/quit[/bold]     - Exit chat\n\n"
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
            "  [bold cyan]/help[/bold cyan]     - Show this help message\n"
            "  [bold cyan]/tools[/bold cyan]    - Toggle tools on/off (currently: " + 
            ("ON" if self.tools_enabled else "OFF") + ")\n"
            "  [bold cyan]/clear[/bold cyan]    - Clear conversation history\n"
            "  [bold cyan]/history[/bold cyan]  - Show conversation history\n"
            "  [bold cyan]/quit[/bold cyan]     - Exit the chat client\n\n"
            "[bold]Available Tools (when enabled):[/bold]\n" +
            ", ".join(self.available_tools) + "\n\n"
            "[dim]Just type your message to chat with Claude![/dim]",
            title="💡 Help",
            border_style="yellow"
        )
        self.console.print(help_text)
    
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
                        self.tools_enabled = not self.tools_enabled
                        status = "enabled" if self.tools_enabled else "disabled"
                        self.console.print(f"🛠️ Tools {status}")
                        continue
                        
                    elif command == "clear":
                        self.conversation_history.clear()
                        self.console.print("🗑️ Conversation history cleared")
                        continue
                        
                    elif command == "history":
                        self.show_conversation_history()
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

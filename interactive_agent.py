#!/usr/bin/env python3
"""Interactive Pydantic AI agent using pyResToolbox MCP server.

This script creates an interactive agent that can use all 47 tools from the
pyResToolbox MCP server for reservoir engineering calculations.

Usage:
    uv run interactive_agent.py
"""

import asyncio
import os
import sys
import warnings
from pathlib import Path
from typing import Any

# Suppress all warnings in this process
warnings.filterwarnings('ignore')
os.environ['PYTHONWARNINGS'] = 'ignore'

try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file if it exists
except ImportError:
    pass  # python-dotenv is optional

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.live import Live
from rich.table import Table
from rich.status import Status
from rich.prompt import Prompt
from rich.text import Text
from rich.syntax import Syntax
from rich.layout import Layout
from rich.align import Align
from rich import box
from rich.live_render import LiveRender

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
from pydantic_ai.usage import UsageLimits


# Initialize Rich console
console = Console()


def get_mcp_server_path() -> str:
    """Get the path to the pyResToolbox MCP server."""
    script_dir = Path(__file__).parent.absolute()
    mcp_dir = script_dir.parent / "pyrestoolbox-mcp"
    server_path = mcp_dir / "server.py"

    if not server_path.exists():
        raise FileNotFoundError(
            f"MCP server not found at {server_path}. "
            "Please ensure pyrestoolbox-mcp is installed in the parent directory."
        )

    return str(server_path)


def load_skill() -> str:
    """Load the pyResToolbox skill content (strips YAML front-matter)."""
    script_dir = Path(__file__).parent.absolute()
    skill_path = script_dir / "SKILL" / "SKILL.md"

    if not skill_path.exists():
        return ""

    text = skill_path.read_text()

    # Strip YAML front-matter (--- ... ---)
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            text = text[end + 3:].lstrip("\n")

    return text


def create_agent() -> Agent:
    """Create a Pydantic AI agent with pyResToolbox MCP tools."""
    # Get MCP server path
    mcp_server_path = get_mcp_server_path()
    
    # Create MCP server connection via STDIO
    # Suppress ALL warnings and MCP banner output
    env = {
        **os.environ,
        'PYTHONPATH': str(Path(mcp_server_path).parent),
        'PYTHONWARNINGS': 'ignore',  # Suppress ALL Python warnings
        'FASTMCP_SHOW_CLI_BANNER': 'false',  # Suppress FastMCP banner
        'FASTMCP_LOG_LEVEL': 'ERROR',  # Only show errors, suppress INFO and WARNING
    }
    
    # Remove VIRTUAL_ENV to avoid uv warning (uv will use the project's .venv)
    env.pop('VIRTUAL_ENV', None)
    
    # Use quiet server wrapper that suppresses warnings
    quiet_server_path = Path(mcp_server_path).parent / "server_quiet.py"
    server_file = 'server_quiet.py' if quiet_server_path.exists() else 'server.py'
    
    # Use fastmcp with quiet server to suppress all warnings
    mcp_server = MCPServerStdio(
        'uv',
        args=[
            'run',
            '--directory', str(Path(mcp_server_path).parent),
            'fastmcp',
            'run',
            '--no-banner',  # Suppress banner via CLI flag
            server_file
        ],
        env=env
    )
    
    # Load skill for tool-calling knowledge
    skill_content = load_skill()

    system_prompt = (
        "You are an experienced reservoir simulation engineer with deep expertise in petroleum "
        "engineering, PVT modeling, well performance, simulation workflows, and geomechanics.\n\n"
        "You maintain conversation memory — remember values from previous exchanges and reference "
        "them when the user asks follow-up questions.\n\n"
        "Always include units in responses (field units by default: psia, °F, ft, mD, cP, "
        "STB/day, MSCF/day). Explain engineering significance of results. Think in workflows.\n\n"
    )

    if skill_content:
        system_prompt += skill_content

    # Create agent with MCP tools
    agent = Agent(
        'openai:gpt-5.4',
        toolsets=[mcp_server],
        system_prompt=system_prompt,
    )
    
    return agent


def create_welcome_panel() -> Panel:
    """Create a welcome panel."""
    welcome_text = """
[bold cyan]pyResToolbox Interactive Agent[/bold cyan]

This agent has access to [bold green]108 specialized tools[/bold green] for reservoir engineering:

• Oil & Gas PVT Properties
• Well Performance & Inflow Calculations  
• Relative Permeability Tables
• Brine Properties & CO₂ Sequestration
• Reservoir Heterogeneity Analysis
• Component Library Access

[dim]Type 'help' for examples, 'quit' to exit[/dim]
    """
    return Panel(
        welcome_text,
        title="[bold]Welcome[/bold]",
        border_style="cyan",
        box=box.ROUNDED
    )


def create_tips_panel() -> Panel:
    """Create a tips panel with guidance for users."""
    tips_text = """
[bold yellow]💡 Tips for Better Results:[/bold yellow]

[cyan]1. Be Specific[/cyan]
   ✓ "Calculate bubble point for API 35 oil at 180°F, GOR 800 scf/stb"
   ✗ "Calculate bubble point"

[cyan]2. Include Units[/cyan]
   ✓ "Temperature: 180°F, Pressure: 3500 psia"
   ✓ "Permeability: 100 mD, Thickness: 50 ft"

[cyan]3. Ask Follow-up Questions[/cyan]
   The agent remembers our conversation, so you can ask:
   "What about at 200°F?" or "Calculate the viscosity too"

[cyan]4. Request Multiple Calculations[/cyan]
   ✓ "Calculate bubble point, FVF, and viscosity for API 35 oil"
   ✓ "Generate a complete PVT table"

[cyan]5. Use Natural Language[/cyan]
   ✓ "What's the Z-factor for this gas?"
   ✓ "How much oil can this well produce?"

[dim]Remember: The agent maintains conversation context, so you can reference previous values![/dim]
    """
    return Panel(
        tips_text,
        title="[bold]Getting Started Tips[/bold]",
        border_style="yellow",
        box=box.ROUNDED
    )


def create_help_panel() -> Panel:
    """Create a help panel with example queries."""
    help_text = """
[bold]Example Queries:[/bold]

[cyan]PVT Calculations:[/cyan]
  • Calculate bubble point for API 35 oil at 180°F, GOR 800 scf/stb
  • What is the Z-factor for gas SG 0.7 at 3500 psia and 180°F?
  • Calculate oil viscosity at 3000 psia for API 35 oil

[cyan]Well Performance:[/cyan]
  • Calculate oil rate for vertical well: Pi=4000, Pb=3500, API=35, k=100 mD
  • What is the gas rate for horizontal well with these parameters...

[cyan]Simulation Tools:[/cyan]
  • Generate relative permeability table (SWOF) using Corey correlation
  • Create aquifer influence table for dimensionless radius 10.0

[cyan]Component Properties:[/cyan]
  • What are the critical properties of methane?
  • Get ethane properties from component library

[dim]Commands: 'help' - show this, 'quit'/'exit'/'q' - exit[/dim]
    """
    return Panel(
        help_text,
        title="[bold]Help[/bold]",
        border_style="yellow",
        box=box.ROUNDED
    )


def display_tool_call(tool_name: str, arguments: dict[str, Any]) -> None:
    """Display a tool call in a simple, clean format."""
    # Show just the tool name and key parameters
    args_str = ", ".join([f"{k}={v}" for k, v in list(arguments.items())[:3]])
    if len(arguments) > 3:
        args_str += f" ... (+{len(arguments) - 3} more)"
    
    console.print(f"[bold cyan]🔧 Calling tool:[/bold cyan] [green]{tool_name}[/green] [dim]({args_str})[/dim]")


def display_tool_result(tool_name: str, result: Any) -> None:
    """Display a tool result in a simple format."""
    result_str = str(result)
    if len(result_str) > 150:
        result_str = result_str[:150] + "..."
    
    console.print(f"[bold green]✓[/bold green] [dim]{tool_name}[/dim] → [white]{result_str}[/white]")


def create_tool_tracker() -> dict[str, list]:
    """Create a tool call tracker."""
    return {"calls": [], "results": []}


async def run_with_tool_tracking(agent: Agent, query: str, conversation_history: list) -> tuple[Any, dict]:
    """Run agent and track tool calls."""
    tool_tracker = create_tool_tracker()
    
    # We'll use the agent's iter method to track tool calls
    # Note: This is a simplified version - actual tool tracking would require
    # hooking into the agent's execution flow
    
    result = await agent.run(
        query,
        message_history=conversation_history,
        usage_limits=UsageLimits(
            request_limit=10,
            total_tokens_limit=300000,
            response_tokens_limit=2000,
            tool_calls_limit=20,
        )
    )
    
    return result, tool_tracker


async def interactive_session():
    """Run an interactive session with the agent."""
    # Clear screen and show welcome
    console.clear()
    console.print(create_welcome_panel())
    console.print()
    
    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        console.print(
            Panel(
                "[bold red]ERROR: OPENAI_API_KEY not set![/bold red]\n\n"
                "Please set it with: [cyan]export OPENAI_API_KEY='your-key'[/cyan]\n"
                "Or create a .env file with: [cyan]OPENAI_API_KEY=your-key[/cyan]",
                title="[bold red]Configuration Error[/bold red]",
                border_style="red"
            )
        )
        return
    
    # Create agent
    with console.status("[bold cyan]Initializing agent and connecting to MCP server...", spinner="dots"):
        try:
            agent = create_agent()
            # Try to enable MCP sampling
            try:
                agent.set_mcp_sampling_model()
                mcp_sampling = True
            except Exception:
                mcp_sampling = False
        except Exception as e:
            console.print(
                Panel(
                    f"[bold red]Failed to create agent:[/bold red]\n{str(e)}",
                    title="[bold red]Error[/bold red]",
                    border_style="red"
                )
            )
            return
    
    console.print(
        Panel(
            f"[bold green]✓ Agent initialized successfully[/bold green]\n"
            f"[dim]MCP Sampling: {'Enabled' if mcp_sampling else 'Disabled'}[/dim]\n"
            f"[dim]Conversation Memory: Enabled[/dim]",
            border_style="green",
            box=box.ROUNDED
        )
    )
    console.print()
    
    # Show tips panel
    console.print(create_tips_panel())
    console.print()
    
    # Initialize conversation history for memory
    conversation_history = []
    
    while True:
        try:
            # Get user input with rich prompt
            console.print()
            user_input = Prompt.ask(
                "[bold cyan]You[/bold cyan]",
                default="",
                show_default=False
            ).strip()
            
            if not user_input:
                continue
            
            # Handle special commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                console.print()
                console.print(
                    Panel(
                        "[bold green]Thank you for using pyResToolbox Interactive Agent![/bold green]\n"
                        "[dim]Goodbye! 👋[/dim]",
                        border_style="green",
                        box=box.ROUNDED
                    )
                )
                break
            
            if user_input.lower() == 'help':
                console.print()
                console.print(create_help_panel())
                continue
            
            # Show thinking indicator and track tool calls
            console.print()
            
            # Run agent and display tool calls from messages
            console.print("[dim]🤔 Thinking...[/dim]")
            
            result = await agent.run(
                user_input,
                message_history=conversation_history,
                usage_limits=UsageLimits(
                    request_limit=10,
                    total_tokens_limit=2000000,
                    response_tokens_limit=4000,
                    tool_calls_limit=30,
                )
            )
            
            # Extract and display tool calls from result messages (simplified)
            tool_calls_shown = set()
            for msg in result.new_messages():
                # Check for tool calls
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    for tool_call in msg.tool_calls:
                        tool_id = getattr(tool_call, 'id', None) or str(tool_call)
                        if tool_id not in tool_calls_shown:
                            tool_calls_shown.add(tool_id)
                            tool_name = getattr(tool_call, 'name', 'unknown')
                            tool_args = getattr(tool_call, 'arguments', {}) if hasattr(tool_call, 'arguments') else {}
                            
                            display_tool_call(tool_name, tool_args)
                
                # Check for tool results
                if hasattr(msg, 'tool_results') and msg.tool_results:
                    for tool_result in msg.tool_results:
                        tool_name = getattr(tool_result, 'tool_name', 'unknown')
                        result_content = getattr(tool_result, 'content', '')
                        if isinstance(result_content, list) and result_content:
                            result_text = result_content[0].text if hasattr(result_content[0], 'text') else str(result_content[0])
                        else:
                            result_text = str(result_content) if result_content else 'Completed'
                        
                        display_tool_result(tool_name, result_text)
            
            # Display response
            console.print()
            console.print(
                Panel(
                    Markdown(result.output),
                    title="[bold green]Agent Response[/bold green]",
                    border_style="green",
                    box=box.ROUNDED
                )
            )
            
            # Update conversation history to maintain memory across turns
            # This includes both user messages and agent responses
            conversation_history = result.new_messages()
            
            # Show memory indicator if conversation has history
            if len(conversation_history) > 2:
                console.print(f"[dim]💭 Conversation memory: {len(conversation_history)} messages[/dim]")
            
        except KeyboardInterrupt:
            console.print()
            console.print(
                Panel(
                    "[yellow]Interrupted. Type 'quit' to exit or continue with your query.[/yellow]",
                    border_style="yellow",
                    box=box.ROUNDED
                )
            )
        except Exception as e:
            console.print()
            console.print(
                Panel(
                    f"[bold red]Error:[/bold red]\n{str(e)}",
                    title="[bold red]Error[/bold red]",
                    border_style="red",
                    box=box.ROUNDED
                )
            )
            import traceback
            console.print(Syntax(traceback.format_exc(), "python", theme="monokai"))


async def main():
    """Main entry point."""
    try:
        await interactive_session()
    except FileNotFoundError as e:
        console.print(
            Panel(
                f"[bold red]Error:[/bold red]\n{str(e)}\n\n"
                "[yellow]Please ensure:[/yellow]\n"
                "  1. The pyrestoolbox-mcp directory exists in the parent directory\n"
                "  2. The MCP server is properly installed\n"
                "  3. You have the necessary dependencies installed",
                title="[bold red]Configuration Error[/bold red]",
                border_style="red"
            )
        )
        sys.exit(1)
    except Exception as e:
        console.print(
            Panel(
                f"[bold red]Unexpected error:[/bold red]\n{str(e)}",
                title="[bold red]Error[/bold red]",
                border_style="red"
            )
        )
        import traceback
        console.print(Syntax(traceback.format_exc(), "python", theme="monokai"))
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

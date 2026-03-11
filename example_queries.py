#!/usr/bin/env python3
"""Example queries for the pyResToolbox interactive agent.

This script demonstrates how to programmatically use the agent
without the interactive interface. Includes examples for:
- PVT calculations
- Well performance
- Geomechanics (original and new tools)
"""

import asyncio
from pathlib import Path
import os
import sys
import warnings

warnings.filterwarnings('ignore', category=UserWarning)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
from pydantic_ai.usage import UsageLimits


def get_mcp_server_path() -> str:
    """Get the path to the pyResToolbox MCP server."""
    script_dir = Path(__file__).parent.absolute()
    mcp_dir = script_dir.parent / "pyrestoolbox-mcp"
    server_path = mcp_dir / "server.py"

    if not server_path.exists():
        raise FileNotFoundError(
            f"MCP server not found at {server_path}"
        )

    return str(server_path)


def create_agent() -> Agent:
    """Create a Pydantic AI agent with pyResToolbox MCP tools."""
    mcp_server_path = get_mcp_server_path()

    env = {
        **os.environ,
        'PYTHONPATH': str(Path(mcp_server_path).parent),
        'PYTHONWARNINGS': 'ignore',
        'FASTMCP_SHOW_CLI_BANNER': 'false',
        'FASTMCP_LOG_LEVEL': 'WARNING',
    }
    env.pop('VIRTUAL_ENV', None)

    mcp_server = MCPServerStdio(
        'uv',
        args=[
            'run',
            '--directory', str(Path(mcp_server_path).parent),
            'fastmcp',
            'run',
            '--no-banner',
            'server.py'
        ],
        env=env
    )

    agent = Agent(
        'openai:gpt-4o',
        toolsets=[mcp_server],
        system_prompt=(
            "You are an expert reservoir engineering assistant with deep expertise in "
            "PVT analysis, well performance, and geomechanics. Use the available tools "
            "to perform calculations accurately. Always include units and explain your "
            "results clearly. You have access to 60+ specialized tools."
        ),
    )

    return agent


async def run_examples():
    """Run example queries from different domains."""

    # Check API key
    if not os.getenv('OPENAI_API_KEY'):
        print("ERROR: OPENAI_API_KEY not set!")
        print("Please set it with: export OPENAI_API_KEY='your-key'")
        return

    agent = create_agent()

    # Organize examples by category
    examples = {
        "PVT Calculations": [
            "Calculate the bubble point pressure for oil with API 35, temperature 180F, solution GOR 800 scf/stb, gas gravity 0.75",
            "What is the Z-factor for gas with specific gravity 0.7 at 3500 psia and 180F?",
        ],
        "Component Properties": [
            "Get the critical properties of methane from the component library",
        ],
        "Original Geomechanics Tools": [
            "Calculate vertical stress at 10,000 ft depth with average formation density 144 lb/ft3",
            "Calculate horizontal stresses for normal faulting at 8,500 psi vertical stress, 4,200 psi pore pressure, Poisson ratio 0.25",
            "Calculate fracture gradient with sigma_h_min 6,500 psi, pore pressure 4,000 psi at 8,000 ft depth",
            "Calculate safe mud weight window with pore pressure 4,500 psi, fracture pressure 7,500 psi at 10,000 ft",
        ],
        "New Advanced Geomechanics Tools": [
            "Calculate stress polygon bounds for sigma_v 10,000 psi, pore pressure 4,500 psi, friction coefficient 0.6",
            "Predict sand production risk: sigma_h_max 8,500 psi, sigma_h_min 6,500 psi, pore pressure 4,500 psi, UCS 3,000 psi, cohesion 500 psi, friction angle 30 degrees, permeability 100 mD, porosity 0.20",
            "Analyze fault stability: sigma_1 10,000 psi, sigma_3 6,000 psi, pore pressure 4,500 psi, fault dip 60 degrees, friction coefficient 0.6",
            "Calculate stress path during depletion from 5,000 to 3,000 psi pore pressure with sigma_v 10,000 psi, initial sigma_h 7,000 psi, Poisson ratio 0.25",
            "Estimate UCS from sonic log: transit time 70 us/ft for sandstone",
            "Calculate critical drawdown: sigma_h_max 8,500 psi, sigma_h_min 6,500 psi, reservoir pressure 5,000 psi, UCS 3,000 psi, cohesion 500 psi, friction angle 30 degrees",
        ],
    }

    print("=" * 80)
    print("pyResToolbox Example Queries")
    print("Demonstrating PVT, Well Performance, and Geomechanics Tools")
    print("=" * 80)
    print()

    example_num = 0
    for category, queries in examples.items():
        print("\n" + "=" * 80)
        print(f"Category: {category}")
        print("=" * 80)

        for query in queries:
            example_num += 1
            print(f"\nExample {example_num}: {query}")
            print("-" * 80)

            try:
                result = await agent.run(
                    query,
                    usage_limits=UsageLimits(
                        request_limit=10,
                        total_tokens_limit=200000,
                        response_tokens_limit=4000,
                        tool_calls_limit=10,
                    )
                )

                print(result.output)
                print()

                usage = result.usage()
                if usage:
                    print(f"[Usage: {usage.input_tokens} input, {usage.output_tokens} output tokens, {usage.tool_calls} tool calls]")

            except Exception as e:
                print(f"Error: {e}")
                import traceback
                traceback.print_exc()

            print()

    print("\n" + "=" * 80)
    print("Example queries completed!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_examples())

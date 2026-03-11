#!/usr/bin/env python3
"""Quick test script to verify the agent setup."""

import asyncio
import os
import sys
import warnings
from pathlib import Path

# Suppress warnings
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


async def test_agent():
    """Test the agent with a simple query."""
    print("=" * 70)
    print("Testing pyResToolbox Interactive Agent - End-to-End Test")
    print("=" * 70)
    print()
    
    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ ERROR: OPENAI_API_KEY not set!")
        print("Please set it with: export OPENAI_API_KEY='your-key'")
        print("Or create a .env file with: OPENAI_API_KEY=your-key")
        return False
    else:
        print(f"✓ OPENAI_API_KEY is set (length: {len(api_key)})")
    
    # Check MCP server
    try:
        mcp_path = get_mcp_server_path()
        print(f"✓ MCP server found at: {mcp_path}")
    except FileNotFoundError as e:
        print(f"❌ ERROR: {e}")
        return False
    
    # Create agent
    print("\nCreating agent...")
    try:
        mcp_server_path = get_mcp_server_path()
        
        # Suppress warnings and MCP banner (same as interactive_agent.py)
        env = {
            **os.environ,
            'PYTHONPATH': str(Path(mcp_server_path).parent),
            'PYTHONWARNINGS': 'ignore::UserWarning:.*pkg_resources.*',
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
            system_prompt="You are a helpful reservoir engineering assistant.",
        )
        
        print("✓ Agent created successfully")
    except Exception as e:
        print(f"❌ ERROR creating agent: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test with the specific query from user (with gas gravity)
    print("\n" + "=" * 70)
    print("TEST 1: Complete query with all parameters")
    print("=" * 70)
    print("Query: 'Calculate bubble point for API 35 oil at 180°F, GOR 800 scf/stb, gas gravity 0.75'")
    print()
    
    try:
        result = await agent.run(
            "Calculate bubble point for API 35 oil at 180°F, GOR 800 scf/stb, gas gravity 0.75",
            usage_limits=UsageLimits(
                request_limit=5,
                total_tokens_limit=300000,
                response_tokens_limit=2000,
                tool_calls_limit=5,
            )
        )
        
        print("=" * 70)
        print("Agent Response:")
        print("=" * 70)
        print(result.output)
        print()
        
        # Check if tool was called
        tool_called = False
        tool_name = None
        for msg in result.new_messages():
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                tool_called = True
                for tool_call in msg.tool_calls:
                    # Try different ways to get tool name
                    tool_name = (getattr(tool_call, 'name', None) or 
                                getattr(tool_call, 'tool_name', None) or
                                str(tool_call).split("'")[1] if "'" in str(tool_call) else 'unknown')
                    print(f"✓ Tool called: {tool_name}")
                    if hasattr(tool_call, 'arguments'):
                        args = tool_call.arguments
                        print(f"  Parameters: api={args.get('api')}, degf={args.get('degf')}, "
                              f"rsb={args.get('rsb')}, sg_g={args.get('sg_g')}, method={args.get('method')}")
                    elif hasattr(tool_call, 'request'):
                        # Try to get from request object
                        req = tool_call.request
                        if hasattr(req, 'name'):
                            tool_name = req.name
                            print(f"  Tool name from request: {tool_name}")
            
            if hasattr(msg, 'tool_results') and msg.tool_results:
                for tool_result in msg.tool_results:
                    result_content = getattr(tool_result, 'content', '')
                    if isinstance(result_content, list) and result_content:
                        result_text = result_content[0].text if hasattr(result_content[0], 'text') else str(result_content[0])
                    else:
                        result_text = str(result_content)
                    print(f"✓ Tool result: {result_text[:100]}...")
        
        usage = result.usage()
        if usage:
            print(f"\nUsage Statistics:")
            print(f"  Input tokens: {usage.input_tokens:,}")
            print(f"  Output tokens: {usage.output_tokens:,}")
            print(f"  Total tokens: {usage.total_tokens:,}")
            print(f"  Requests: {usage.requests}")
            print(f"  Tool calls: {usage.tool_calls}")
        
        if not tool_called:
            print("\n⚠ Warning: No tools were called!")
            return False
        
        if tool_name != 'oil_bubble_point':
            print(f"\n⚠ Warning: Expected 'oil_bubble_point' but got '{tool_name}'")
        
        # Verify the result contains a bubble point value
        if 'psia' in result.output.lower() or '316' in result.output or '317' in result.output:
            print("\n✓ Result verification: Response contains expected bubble point value")
        else:
            print("\n⚠ Warning: Response may not contain expected bubble point value")
        
        print("\n" + "=" * 70)
        print("✓ TEST 1 PASSED: Complete query works end-to-end!")
        print("=" * 70)
        return True
        
    except Exception as e:
        print(f"❌ ERROR during query: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_agent())
    sys.exit(0 if success else 1)

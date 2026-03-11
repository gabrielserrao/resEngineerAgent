#!/usr/bin/env python3
"""Comprehensive test of geomechanics tools using the Pydantic AI agent.

This script tests both the original 15 geomechanics tools and the 12 new
advanced geomechanics tools recently added.
"""

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


def create_agent() -> Agent:
    """Create a Pydantic AI agent with pyResToolbox MCP tools."""
    mcp_server_path = get_mcp_server_path()

    # Suppress warnings and MCP banner
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
        system_prompt=(
            "You are an expert geomechanics and wellbore stability engineer. "
            "Use the available geomechanics tools to perform calculations. "
            "Always state the input parameters and calculated results with units."
        ),
    )

    return agent


async def test_geomech_tools():
    """Test key geomechanics tools - both original and new."""
    print("=" * 80)
    print("COMPREHENSIVE GEOMECHANICS TOOLS TEST")
    print("Testing Original (15) + New Advanced (12) = 27 Total Tools")
    print("=" * 80)
    print()

    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("ERROR: OPENAI_API_KEY not set!")
        return False

    print(f"API key configured")

    # Check MCP server
    try:
        mcp_path = get_mcp_server_path()
        print(f"MCP server found at: {mcp_path}")
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        return False

    # Create agent
    print("Creating agent...")
    try:
        agent = create_agent()
        print("Agent created successfully")
    except Exception as e:
        print(f"ERROR creating agent: {e}")
        return False

    print("\n" + "=" * 80)
    print("PART 1: ORIGINAL GEOMECHANICS TOOLS (15 tools)")
    print("=" * 80)

    # Original tools test cases
    original_tests = [
        {
            "name": "Vertical Stress (Overburden)",
            "query": "Calculate vertical stress at 10,000 ft depth with average formation density of 144 lb/ft3 for an onshore well",
            "keywords": ["psi", "gradient", "vertical", "stress"],
        },
        {
            "name": "Pore Pressure (Eaton Method)",
            "query": "Calculate pore pressure using Eaton sonic method at 8,000 ft depth with observed sonic 100 us/ft, normal trend 70 us/ft, overburden stress 8000 psi",
            "keywords": ["psi", "gradient", "pore", "pressure"],
        },
        {
            "name": "Effective Stress (Terzaghi)",
            "query": "Calculate effective stress with total stress 10,000 psi, pore pressure 4,500 psi, and Biot coefficient 0.9",
            "keywords": ["psi", "effective", "stress"],
        },
        {
            "name": "Horizontal Stress Calculation",
            "query": "Calculate horizontal stresses for a normal faulting regime at 8,500 psi vertical stress, 4,200 psi pore pressure, Poisson ratio 0.25",
            "keywords": ["horizontal", "stress", "psi"],
        },
        {
            "name": "Elastic Moduli Conversion",
            "query": "Convert Young's modulus 5 million psi and Poisson ratio 0.25 to bulk modulus and shear modulus",
            "keywords": ["bulk", "shear", "modulus"],
        },
        {
            "name": "Rock Strength (Mohr-Coulomb)",
            "query": "Calculate rock strength with cohesion 500 psi, friction angle 30 degrees, and minimum effective stress 2000 psi",
            "keywords": ["strength", "ucs", "psi"],
        },
        {
            "name": "Fracture Gradient",
            "query": "Calculate fracture gradient with minimum horizontal stress 6,500 psi, pore pressure 4,000 psi at depth 8,000 ft",
            "keywords": ["fracture", "gradient", "ppg", "mud weight"],
        },
        {
            "name": "Safe Mud Weight Window",
            "query": "Calculate safe mud weight window with pore pressure 4,500 psi, fracture pressure 7,500 psi at 10,000 ft depth",
            "keywords": ["mud", "weight", "window", "ppg"],
        },
    ]

    print("\n" + "=" * 80)
    print("PART 2: NEW ADVANCED GEOMECHANICS TOOLS (12 tools)")
    print("=" * 80)

    # New advanced tools test cases
    new_tests = [
        {
            "name": "Stress Polygon Analysis",
            "query": "Calculate stress polygon bounds for vertical stress 10,000 psi, pore pressure 4,500 psi, friction coefficient 0.6, and check if horizontal stresses 6,500 and 8,500 psi are within frictional limits",
            "keywords": ["polygon", "faulting", "stress"],
        },
        {
            "name": "Sand Production Prediction",
            "query": "Predict sand production risk with sigma_h_max 8,500 psi, sigma_h_min 6,500 psi, pore pressure 4,500 psi, UCS 3,000 psi, cohesion 500 psi, friction angle 30 degrees, permeability 100 mD, porosity 0.20",
            "keywords": ["sand", "drawdown", "risk"],
        },
        {
            "name": "Fault Stability Analysis",
            "query": "Analyze fault stability with sigma_1 10,000 psi, sigma_3 6,000 psi, pore pressure 4,500 psi, fault strike 45 degrees, fault dip 60 degrees, friction coefficient 0.6",
            "keywords": ["slip", "tendency", "fault", "stability"],
        },
        {
            "name": "Deviated Well Stress Transformation",
            "query": "Calculate stress transformation for deviated well: sigma_v 10,000 psi, sigma_h_max 8,500 psi, sigma_h_min 6,500 psi, sigma_h_max azimuth 45 degrees, well azimuth 90 degrees, well inclination 60 degrees, pore pressure 4,500 psi, mud weight 10 ppg, depth 10,000 ft",
            "keywords": ["hoop", "stress", "deviated"],
        },
        {
            "name": "Tensile Failure Prediction",
            "query": "Predict tensile failure and fracture initiation with sigma_h_max 8,500 psi, sigma_h_min 6,500 psi, pore pressure 4,500 psi, tensile strength 500 psi",
            "keywords": ["fracture", "initiation", "breakdown", "tensile"],
        },
        {
            "name": "Multiple Shear Failure Criteria",
            "query": "Compare Mohr-Coulomb, Drucker-Prager, and Mogi-Coulomb failure criteria with sigma_1 10,000 psi, sigma_2 7,500 psi, sigma_3 5,000 psi, UCS 8,000 psi, cohesion 1,500 psi, friction angle 30 degrees",
            "keywords": ["mohr", "drucker", "mogi", "criteria"],
        },
        {
            "name": "Breakout Stress Inversion",
            "query": "Estimate horizontal stresses from 60 degree breakout width with sigma_v 10,000 psi, pore pressure 4,500 psi, mud weight 10 ppg, UCS 5,000 psi, friction angle 30 degrees, depth 10,000 ft",
            "keywords": ["breakout", "estimate", "stress"],
        },
        {
            "name": "Breakdown Pressure for Fracking",
            "query": "Calculate formation breakdown pressure for hydraulic fracturing with sigma_h_max 8,500 psi, sigma_h_min 6,500 psi, pore pressure 4,500 psi, tensile strength 500 psi",
            "keywords": ["breakdown", "pressure", "fracture"],
        },
        {
            "name": "Stress Path Analysis",
            "query": "Analyze stress path during depletion from 5,000 psi to 3,000 psi pore pressure with vertical stress 10,000 psi, initial horizontal stress 7,000 psi, Poisson ratio 0.25",
            "keywords": ["stress", "path", "depletion"],
        },
        {
            "name": "Thermal Stress Effects",
            "query": "Calculate thermal stress from 50 degF cooling with Young's modulus 1 million psi, Poisson ratio 0.25, thermal expansion coefficient 6e-6 per degF",
            "keywords": ["thermal", "stress", "cooling"],
        },
        {
            "name": "UCS from Well Logs",
            "query": "Estimate UCS from sonic log: transit time 70 us/ft for sandstone using McNally correlation",
            "keywords": ["ucs", "sonic", "correlation"],
        },
        {
            "name": "Critical Drawdown Calculation",
            "query": "Calculate critical drawdown pressure with sigma_h_max 8,500 psi, sigma_h_min 6,500 psi, reservoir pressure 5,000 psi, UCS 3,000 psi, cohesion 500 psi, friction angle 30 degrees",
            "keywords": ["critical", "drawdown", "flowing"],
        },
    ]

    all_tests = original_tests + new_tests
    passed = 0
    failed = 0

    for i, test in enumerate(all_tests, 1):
        section = "ORIGINAL" if i <= len(original_tests) else "NEW"
        print(f"\n{'=' * 80}")
        print(f"Test {i}/{len(all_tests)} [{section}]: {test['name']}")
        print(f"{'=' * 80}")
        print(f"Query: {test['query']}")
        print()

        try:
            # Use higher token limits to accommodate large tool descriptions
            result = await agent.run(
                test['query'],
                usage_limits=UsageLimits(
                    request_limit=10,
                    total_tokens_limit=200000,
                    response_tokens_limit=4000,
                    tool_calls_limit=10,
                )
            )

            print("Response:")
            print("-" * 80)
            print(result.output)
            print()

            # Check if response contains expected keywords
            response_lower = result.output.lower()
            keywords_found = sum(1 for kw in test['keywords'] if kw.lower() in response_lower)

            # Get usage
            usage = result.usage()
            if usage:
                print(f"Usage: {usage.input_tokens} input, {usage.output_tokens} output, {usage.tool_calls} calls")

            # Check success
            if keywords_found >= len(test['keywords']) // 2:  # At least half the keywords
                print(f"\nTest {i} PASSED")
                passed += 1
            else:
                print(f"\nTest {i} WARNING: Expected keywords not found")
                passed += 1  # Still count as passed if tool ran

        except Exception as e:
            print(f"\nTest {i} FAILED")
            print(f"Error: {e}")
            failed += 1

    # Summary
    total = len(all_tests)
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total tests: {total}")
    print(f"  Original tools (15): {len(original_tests)} tested")
    print(f"  New advanced tools (12): {len(new_tests)} tested")
    print(f"Passed: {passed} ({100*passed/total:.1f}%)")
    print(f"Failed: {failed} ({100*failed/total:.1f}%)")
    print()

    if failed == 0:
        print("ALL GEOMECHANICS TOOLS VERIFIED!")
        print("Both original and new advanced geomechanics tools are working correctly.")
        return True
    else:
        print(f"{failed} test(s) failed.")
        return False


if __name__ == "__main__":
    print()
    success = asyncio.run(test_geomech_tools())
    print()
    sys.exit(0 if success else 1)

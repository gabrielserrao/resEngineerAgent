#!/usr/bin/env python3
"""Comprehensive test script for geomechanics tools in the pyResToolbox MCP server.

This script tests all 15 geomechanics tools with realistic petroleum engineering scenarios.
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
            "Use the available geomechanics tools to perform calculations accurately. "
            "Always include units and explain your results clearly. "
            "For each calculation, state the input parameters and the calculated result."
        ),
    )

    return agent


async def test_geomechanics_tools():
    """Test all 15 geomechanics tools with realistic scenarios."""
    print("=" * 80)
    print("COMPREHENSIVE GEOMECHANICS TOOLS TEST")
    print("Testing all 15 analytical geomechanics tools in pyResToolbox MCP Server")
    print("=" * 80)
    print()

    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ ERROR: OPENAI_API_KEY not set!")
        print("Please set it with: export OPENAI_API_KEY='your-key'")
        print("Or create a .env file with: OPENAI_API_KEY=your-key")
        return False

    print(f"✓ OPENAI_API_KEY is set")

    # Check MCP server
    try:
        mcp_path = get_mcp_server_path()
        print(f"✓ MCP server found at: {mcp_path}")
    except FileNotFoundError as e:
        print(f"❌ ERROR: {e}")
        return False

    # Create agent
    print("\n✓ Creating agent...")
    try:
        agent = create_agent()
        print("✓ Agent created successfully")
    except Exception as e:
        print(f"❌ ERROR creating agent: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n" + "=" * 80)
    print("STARTING GEOMECHANICS TESTS")
    print("=" * 80)
    print()

    # Define comprehensive test cases for all 15 geomechanics tools
    test_cases = [
        {
            "name": "Test 1: Vertical Stress (Overburden) - Onshore Well",
            "query": "Calculate vertical stress at 10,000 ft depth for an onshore well with average formation density 144 lb/ft³",
            "expected_tool": "geomech_vertical_stress",
            "validation": ["psi", "gradient", "10000", "144"],
        },
        {
            "name": "Test 2: Vertical Stress - Offshore Well",
            "query": "Calculate vertical stress at 12,000 ft depth for offshore well with 5,000 ft water depth, formation density 150 lb/ft³, water density 64 lb/ft³",
            "expected_tool": "geomech_vertical_stress",
            "validation": ["psi", "gradient", "12000", "5000"],
        },
        {
            "name": "Test 3: Pore Pressure (Eaton Method) - From Sonic",
            "query": "Calculate pore pressure using Eaton method at 8,000 ft depth with observed sonic DT 100 µs/ft, normal trend DT 70 µs/ft, vertical stress 7200 psi, normal pore pressure 3500 psi, Eaton exponent 3.0",
            "expected_tool": "geomech_pore_pressure_eaton",
            "validation": ["psia", "gradient", "8000", "sonic"],
        },
        {
            "name": "Test 4: Pore Pressure (Eaton Method) - From Resistivity",
            "query": "Calculate pore pressure using Eaton resistivity method at 9,000 ft with observed resistivity 2.5 ohm-m, normal resistivity 4.0 ohm-m, vertical stress 8100 psi, normal pore pressure 4000 psi, Eaton exponent 1.2",
            "expected_tool": "geomech_pore_pressure_eaton",
            "validation": ["psia", "resistivity", "9000"],
        },
        {
            "name": "Test 5: Effective Stress - Terzaghi's Principle",
            "query": "Calculate effective stress with total stress 8000 psi, pore pressure 4500 psi, and Biot coefficient 0.85",
            "expected_tool": "geomech_effective_stress",
            "validation": ["psi", "8000", "4500", "effective"],
        },
        {
            "name": "Test 6: Horizontal Stress - Normal Faulting",
            "query": "Calculate minimum horizontal stress for normal faulting regime with vertical stress 8500 psi, pore pressure 4200 psi, Poisson's ratio 0.25, tectonic stress 200 psi",
            "expected_tool": "geomech_horizontal_stress",
            "validation": ["psi", "8500", "normal"],
        },
        {
            "name": "Test 7: Horizontal Stress - Strike-Slip Faulting",
            "query": "Calculate horizontal stresses for strike-slip regime with vertical stress 9000 psi, pore pressure 4500 psi, Poisson's ratio 0.30, tectonic stress 500 psi",
            "expected_tool": "geomech_horizontal_stress",
            "validation": ["psi", "9000", "strike-slip", "maximum"],
        },
        {
            "name": "Test 8: Elastic Moduli Conversion",
            "query": "Convert elastic moduli: given Young's modulus 5,000,000 psi and Poisson's ratio 0.25, calculate bulk modulus, shear modulus, and Lame's first parameter",
            "expected_tool": "geomech_elastic_moduli_conversion",
            "validation": ["psi", "5000000", "bulk", "shear"],
        },
        {
            "name": "Test 9: Rock Strength - Mohr-Coulomb",
            "query": "Calculate rock strength using Mohr-Coulomb criterion with UCS 8000 psi, cohesion 1500 psi, friction angle 30 degrees, minimum stress 4000 psi, maximum stress 9000 psi, pore pressure 3500 psi",
            "expected_tool": "geomech_rock_strength_mohr_coulomb",
            "validation": ["8000", "30", "factor", "strength"],
        },
        {
            "name": "Test 10: Dynamic to Static Moduli Conversion",
            "query": "Convert dynamic elastic moduli from logs to static values: dynamic Young's modulus 6,000,000 psi, dynamic Poisson's ratio 0.28, using Horsrud correlation",
            "expected_tool": "geomech_dynamic_to_static_moduli",
            "validation": ["6000000", "static", "correlation"],
        },
        {
            "name": "Test 11: Breakout Width - Stable Wellbore",
            "query": "Calculate breakout width with max horizontal stress 9000 psi, min horizontal stress 6500 psi, vertical stress 8000 psi, pore pressure 4000 psi, mud weight 9.5 ppg, wellbore radius 6 inches, UCS 8000 psi, friction angle 30 degrees",
            "expected_tool": "geomech_breakout_width",
            "validation": ["9000", "6500", "breakout", "degrees"],
        },
        {
            "name": "Test 12: Breakout Width - Unstable Wellbore",
            "query": "Calculate breakout width with max horizontal stress 10000 psi, min horizontal stress 6000 psi, vertical stress 8500 psi, pore pressure 4200 psi, mud weight 8.5 ppg, wellbore radius 6 inches, UCS 5000 psi, friction angle 25 degrees",
            "expected_tool": "geomech_breakout_width",
            "validation": ["10000", "6000", "breakout", "unstable"],
        },
        {
            "name": "Test 13: Fracture Gradient",
            "query": "Calculate fracture gradient with minimum horizontal stress 6500 psi, pore pressure 4000 psi, at depth 8000 ft",
            "expected_tool": "geomech_fracture_gradient",
            "validation": ["6500", "4000", "8000", "ppg", "gradient"],
        },
        {
            "name": "Test 14: Safe Mud Weight Window",
            "query": "Calculate safe mud weight window with pore pressure 4500 psi, min horizontal stress 6800 psi, max horizontal stress 9200 psi, vertical stress 8500 psi, wellbore radius 6 inches, UCS 7000 psi, friction angle 28 degrees, depth 9000 ft",
            "expected_tool": "geomech_safe_mud_weight_window",
            "validation": ["4500", "6800", "9200", "mud weight", "window"],
        },
        {
            "name": "Test 15: Critical Mud Weight for Collapse",
            "query": "Calculate critical mud weight to prevent wellbore collapse with max horizontal stress 9500 psi, min horizontal stress 6500 psi, vertical stress 8200 psi, pore pressure 4100 psi, wellbore radius 6 inches, UCS 6500 psi, friction angle 27 degrees, depth 8500 ft",
            "expected_tool": "geomech_critical_mud_weight_collapse",
            "validation": ["9500", "6500", "critical", "collapse", "ppg"],
        },
        {
            "name": "Test 16: Reservoir Compaction",
            "query": "Calculate reservoir compaction from pressure depletion: initial pressure 5000 psi, final pressure 3000 psi, reservoir thickness 100 ft, pore compressibility 5e-6 psi⁻¹, formation compressibility 3e-6 psi⁻¹",
            "expected_tool": "geomech_reservoir_compaction",
            "validation": ["5000", "3000", "100", "compaction", "feet"],
        },
        {
            "name": "Test 17: Pore Compressibility from Elastic Properties",
            "query": "Calculate pore compressibility using elastic properties: porosity 0.20, bulk modulus 3,000,000 psi, grain bulk modulus 6,000,000 psi",
            "expected_tool": "geomech_pore_compressibility",
            "validation": ["0.20", "3000000", "compressibility", "psi"],
        },
        {
            "name": "Test 18: Pore Compressibility from Hall Correlation",
            "query": "Calculate pore compressibility using Hall correlation for sandstone with porosity 0.18",
            "expected_tool": "geomech_pore_compressibility",
            "validation": ["0.18", "sandstone", "hall", "compressibility"],
        },
        {
            "name": "Test 19: Leak-Off Pressure (LOT)",
            "query": "Calculate leak-off pressure from LOT test: test pressure 4800 psi, mud hydrostatic 3500 psi, at depth 7000 ft",
            "expected_tool": "geomech_leak_off_pressure",
            "validation": ["4800", "3500", "7000", "gradient", "ppg"],
        },
        {
            "name": "Test 20: Leak-Off Pressure (FIT)",
            "query": "Calculate formation integrity test pressure: FIT pressure 5200 psi, mud hydrostatic 3800 psi, at depth 7500 ft",
            "expected_tool": "geomech_leak_off_pressure",
            "validation": ["5200", "3800", "7500", "integrity"],
        },
        {
            "name": "Test 21: Hydraulic Fracture Width - PKN Model",
            "query": "Calculate fracture width using PKN model: injection rate 40 bpm, fluid viscosity 50 cp, Young's modulus 4,000,000 psi, fracture height 100 ft, fracture length 500 ft",
            "expected_tool": "geomech_hydraulic_fracture_width",
            "validation": ["40", "50", "4000000", "PKN", "width", "inches"],
        },
        {
            "name": "Test 22: Hydraulic Fracture Width - KGD Model",
            "query": "Calculate fracture width using KGD model: injection rate 35 bpm, fluid viscosity 100 cp, Young's modulus 3,500,000 psi, fracture height 80 ft, fracture length 600 ft",
            "expected_tool": "geomech_hydraulic_fracture_width",
            "validation": ["35", "100", "3500000", "KGD", "width"],
        },
    ]

    # Track results
    passed = 0
    failed = 0
    total = len(test_cases)

    # Run each test
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'=' * 80}")
        print(f"{test['name']}")
        print(f"{'=' * 80}")
        print(f"Query: {test['query']}")
        print()

        try:
            result = await agent.run(
                test['query'],
                usage_limits=UsageLimits(
                    request_limit=5,
                    total_tokens_limit=100000,
                    response_tokens_limit=2000,
                    tool_calls_limit=5,
                )
            )

            print("Response:")
            print("-" * 80)
            print(result.output)
            print()

            # Verify tool was called
            tool_called = False
            correct_tool = False

            for msg in result.new_messages():
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    tool_called = True
                    for tool_call in msg.tool_calls:
                        tool_name = (getattr(tool_call, 'name', None) or
                                    getattr(tool_call, 'tool_name', None) or
                                    str(tool_call).split("'")[1] if "'" in str(tool_call) else 'unknown')

                        if test['expected_tool'] in tool_name:
                            correct_tool = True
                            print(f"✓ Correct tool called: {tool_name}")
                        else:
                            print(f"⚠ Tool called: {tool_name} (expected: {test['expected_tool']})")

            # Validate response content
            validation_passed = True
            response_lower = result.output.lower()

            for keyword in test['validation']:
                if keyword.lower() not in response_lower:
                    print(f"⚠ Validation keyword missing: '{keyword}'")
                    validation_passed = False

            # Get usage stats
            usage = result.usage()
            if usage:
                print(f"\nUsage: {usage.input_tokens} input, {usage.output_tokens} output tokens, {usage.tool_calls} tool calls")

            # Determine if test passed
            if tool_called and correct_tool and validation_passed:
                print(f"\n✓ TEST {i}/{total} PASSED")
                passed += 1
            else:
                print(f"\n✗ TEST {i}/{total} FAILED")
                if not tool_called:
                    print("  Reason: No tool was called")
                elif not correct_tool:
                    print(f"  Reason: Wrong tool called (expected {test['expected_tool']})")
                elif not validation_passed:
                    print("  Reason: Response validation failed")
                failed += 1

        except Exception as e:
            print(f"\n✗ TEST {i}/{total} FAILED with exception")
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    # Final summary
    print("\n" + "=" * 80)
    print("GEOMECHANICS TEST SUITE SUMMARY")
    print("=" * 80)
    print(f"Total tests: {total}")
    print(f"Passed: {passed} ({100*passed/total:.1f}%)")
    print(f"Failed: {failed} ({100*failed/total:.1f}%)")
    print()

    if failed == 0:
        print("✓ ALL GEOMECHANICS TOOLS VERIFIED SUCCESSFULLY!")
        print("All 15 geomechanics tools are working correctly with realistic scenarios.")
        return True
    else:
        print(f"✗ {failed} test(s) failed. Please review the output above.")
        return False


if __name__ == "__main__":
    print()
    success = asyncio.run(test_geomechanics_tools())
    print()
    sys.exit(0 if success else 1)

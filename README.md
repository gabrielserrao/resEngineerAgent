<div align="center">

# Reservoir Engineering AI Agent

### Natural Language Interface for Petroleum Engineering Calculations

**Ask questions in plain English. Get industry-standard reservoir engineering answers.**

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Pydantic AI](https://img.shields.io/badge/Pydantic%20AI-0.0.49+-red.svg)](https://ai.pydantic.dev/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--5.4-green.svg)](https://openai.com/)
[![Built with pyResToolbox](https://img.shields.io/badge/Built%20with-pyResToolbox-orange.svg)](https://github.com/mwburgoyne/pyResToolbox)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Support-yellow.svg?logo=buy-me-a-coffee)](https://buymeacoffee.com/gabrielsero)

**[Quick Start](#quick-start)** • **[Features](#features)** • **[Examples](#example-queries)** • **[Configuration](#configuration)** • **[Architecture](#architecture)**

---

### 108 Tools | Conversation Memory | Rich Terminal UI | Field & Metric Units

**PVT Analysis** • **Well Performance** • **Nodal Analysis** • **DCA** • **Material Balance** • **Simulation Support** • **Brine Properties** • **Geomechanics** • **Heterogeneity Analysis**

---

</div>

An interactive AI agent powered by [Pydantic AI](https://ai.pydantic.dev/) that connects to the [pyResToolbox MCP server](https://github.com/gabrielserrao/pyrestoolbox-mcp) and gives you a natural-language interface to 108 production-ready petroleum engineering tools. Ask about bubble points, Z-factors, relative permeability, material balance, decline curves, or geomechanics — the agent selects the right tool, runs the calculation, and explains the result.

---

<div align="center">

## Support This Project

If you find this project useful, consider buying me a coffee! Your support helps maintain and improve this open-source tool.

<a href="https://buymeacoffee.com/gabrielsero" target="_blank">
  <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" >
</a>

</div>

---

## What Can You Do?

Instead of writing code or remembering function signatures, just ask:

> *"Calculate the bubble point pressure for API 35° oil at 180°F with solution GOR of 800 scf/stb and gas gravity 0.75"*

> *"Generate an IPR curve for my well: Pi=4000 psia, Pb=3500 psia, API 38°, 175°F, 75 ft pay, 150 mD"*

> *"What is the Z-factor for gas SG 0.7 at 3500 psia and 180°F using the DAK correlation?"*

> *"Run a decline curve analysis: qi=500 STB/day, Di=0.3/year, b=1.2, for 5 years"*

The agent remembers your conversation — ask follow-up questions without repeating parameters.

---

## Features

- **108 Production-Ready Tools** — Complete coverage of petroleum engineering workflows
- **Conversation Memory** — Agent tracks context across turns; reference previous values naturally
- **Rich Terminal UI** — Color-coded output, tool call tracking, markdown-rendered responses
- **Industry-Standard Correlations** — Standing, Valko-McCain, Velarde, DAK, Beggs-Robinson, Corey, LET, Arps, and more
- **Dual Unit Support** — Field units (psia, °F, ft) and Metric units (barsa, °C, m)
- **Any OpenAI-compatible LLM** — Swap to GPT-4o-mini, Claude, Gemini, or any compatible model
- **GPL-3.0 Licensed** — Free and open source

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│          Reservoir Engineering AI Agent          │  ← You are here
│  (res-pydantic-agent / interactive_agent.py)     │
│                                                  │
│  • Pydantic AI orchestration                     │
│  • Conversation memory                           │
│  • Rich terminal UI                              │
└───────────────────┬─────────────────────────────┘
                    │ MCP (STDIO)
                    ▼
┌─────────────────────────────────────────────────┐
│         pyResToolbox MCP Server                  │
│  (github.com/gabrielserrao/pyrestoolbox-mcp)    │
│                                                  │
│  108 tools: PVT, Well Performance, Nodal,        │
│  DCA, Material Balance, Simulation, Brine,       │
│  Geomechanics, Heterogeneity Analysis            │
└───────────────────┬─────────────────────────────┘
                    │ Python
                    ▼
┌─────────────────────────────────────────────────┐
│           pyResToolbox Library                   │
│  (github.com/mwburgoyne/pyResToolbox)           │
│                                                  │
│  Industry-standard reservoir engineering         │
│  calculations by Mark Burgoyne                   │
└─────────────────────────────────────────────────┘
```

---

## Quick Start

### Prerequisites

- Python 3.11+
- [UV package manager](https://docs.astral.sh/uv/) (recommended)
- An OpenAI API key
- The [pyRestoolbox MCP server](https://github.com/gabrielserrao/pyrestoolbox-mcp) cloned as a sibling directory

### 1. Clone both repos side by side

```bash
# Clone the MCP server
git clone https://github.com/gabrielserrao/pyrestoolbox-mcp.git

# Clone this agent
git clone https://github.com/gabrielserrao/resEngineerAgent.git res-pydantic-agent

# Your directory structure should look like:
# some-folder/
# ├── pyrestoolbox-mcp/     ← MCP server
# └── res-pydantic-agent/   ← This repo
```

### 2. Set up the MCP server

```bash
cd pyrestoolbox-mcp
uv sync
cd ..
```

### 3. Set up the agent

```bash
cd res-pydantic-agent
uv sync
```

### 4. Configure your API key

```bash
cp .env.example .env
# Edit .env and set your OpenAI API key:
# OPENAI_API_KEY=sk-...
```

### 5. Run

```bash
uv run interactive_agent.py
```

---

## Example Queries

### PVT Calculations

```
Calculate bubble point for API 35 oil at 180°F, GOR 800 scf/stb, gas gravity 0.75

What is the Z-factor for gas SG 0.7 at 3500 psia and 180°F?

Calculate oil FVF and viscosity at 3000 psia for that same oil
```

### Well Performance

```
Calculate oil rate for vertical well: Pi=4000 psia, Pb=3500 psia,
API=35, 180°F, k=100 mD, h=50 ft, re=1000 ft, rw=0.35 ft

Generate an IPR curve for a gas well with reservoir pressure 5000 psia
```

### Simulation Tools

```
Generate a SWOF relative permeability table using Corey correlation,
25 rows, Swc=0.15, Sorw=0.15, no=2.5, nw=1.5

Create an aquifer influence table for dimensionless radius 10
```

### Decline Curve Analysis

```
Run Arps decline analysis: qi=500 STB/day, Di=0.3/year, b=1.2, for 5 years

What is EUR for this well at 10 STB/day economic limit?
```

### Geomechanics

```
Calculate vertical stress gradient at 10,000 ft with average overburden density 2.4 g/cc

What is the fracture gradient at 8000 ft?
```

### Material Balance

```
Run gas material balance P/Z analysis with these production data...

Estimate OGIP using Havlena-Odeh method
```

---

## Configuration

### Change the LLM model

Edit `interactive_agent.py`:

```python
agent = Agent(
    'openai:gpt-5.4',         # GPT-5.4 (default)
    # 'openai:gpt-4o',        # previous generation
    # 'openai:gpt-4o-mini',   # cheaper / faster
    # 'anthropic:claude-sonnet-4-5',  # Claude
    # 'google-gla:gemini-2.0-flash-exp',
    toolsets=[mcp_server],
    system_prompt=system_prompt,
)
```

### Usage limits

Adjust in `interactive_agent.py` → `interactive_session()`:

```python
usage_limits=UsageLimits(
    request_limit=10,
    total_tokens_limit=2000000,
    response_tokens_limit=4000,
    tool_calls_limit=30,
)
```

---

## Claude Code Skill

The `SKILL/` directory contains a ready-to-use Claude Code skill for the pyResToolbox MCP server:

| File | Description |
|---|---|
| `SKILL/SKILL.md` | Skill definition — teaches Claude which tools to use and when |
| `SKILL/tools-reference.md` | Full reference for all 108 tools with parameters and examples |
| `SKILL/pyrestoolbox-mcp.skill` | Packaged skill file for direct import into Claude Code |

To install the skill in Claude Code, import `SKILL/pyrestoolbox-mcp.skill` via the Claude Code skill manager.

---

## Project Structure

```
res-pydantic-agent/
├── interactive_agent.py   # Main interactive agent (entry point)
├── example_queries.py     # Programmatic usage examples
├── test_agent.py          # End-to-end agent test
├── pyproject.toml         # Dependencies (pydantic-ai, rich, python-dotenv)
├── .env.example           # Environment variable template
├── SKILL/
│   ├── SKILL.md                  # Claude Code skill definition
│   ├── tools-reference.md        # Full 108-tool reference
│   └── pyrestoolbox-mcp.skill    # Packaged skill for import
├── .gitignore
├── LICENSE                # GPL-3.0
└── README.md
```

---

## Troubleshooting

**MCP server not found**
Ensure `pyrestoolbox-mcp/` is a sibling directory of this repo (same parent folder).

**Token limit exceeded**
The MCP server exposes 108 tools — their schemas alone consume ~160k tokens per request. The default limits in `interactive_agent.py` account for this. If you hit limits, increase `total_tokens_limit`.

**API key errors**
Verify `OPENAI_API_KEY` is set in your `.env` file and has sufficient credits.

**Tool execution errors**
Run `cd ../pyrestoolbox-mcp && uv run python test_server.py` to verify the MCP server is working correctly.

---

## Related Projects

- [pyResToolbox MCP Server](https://github.com/gabrielserrao/pyrestoolbox-mcp) — The MCP server providing 108 tools
- [pyResToolbox](https://github.com/mwburgoyne/pyResToolbox) — The underlying reservoir engineering library by Mark Burgoyne

---

## Contributing

Pull requests welcome. For major changes, open an issue first to discuss what you'd like to change.

---

## License

This project is licensed under the **GNU General Public License v3.0** — see the [LICENSE](LICENSE) file for details.

In short: you are free to use, modify, and distribute this software, but any derivative work must also be open-sourced under GPL-3.0.

---

<div align="center">

Built with [Pydantic AI](https://ai.pydantic.dev/) • [pyResToolbox](https://github.com/mwburgoyne/pyResToolbox) • [FastMCP](https://github.com/jlowin/fastmcp)

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-gabrielsero-yellow.svg?logo=buy-me-a-coffee)](https://buymeacoffee.com/gabrielsero)

</div>

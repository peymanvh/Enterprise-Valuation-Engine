---
name: enterprise-valuation
description: Institutional Corporate Enterprise, Venture Capital, Project Feasibility, and Patent Valuation Engine based on McKinsey 8th Ed, Damodaran, and UNIDO standards.
author: Lead Financial Architect & AI Systems Engineer
version: 1.0.0
---

# Enterprise Valuation Engine (Claude Code Skill)

Use this skill whenever asked to value a company, startup, industrial feasibility study, or patent asset.

## Core Capabilities & Scripts
The underlying Python engines reside in `skills/enterprise-valuation/scripts/`:
- `dcf_mckinsey.py`: McKinsey 8th Edition Key Value Driver DCF, NOPAT, Invested Capital, ROIC, and Damodaran distress overlay.
- `multiples_valuation.py`: Peer group trading multiples using harmonic mean ratios and value-driver regression.
- `startup_venture.py`: VC Method, Scorecard Method, Berkus Method, First Chicago scenarios, and SaaS unit economics audit.
- `commercial_project.py`: UNIDO project feasibility, dynamic CCC, CFADS, DSCR covenants, and break-even analysis.
- `ip_patent_val.py`: Relief-from-Royalty, MPEEM, and Black-Scholes Real Options.
- `monte_carlo_simulator.py`: Probabilistic distribution engine and Tornado sensitivity ranking.

## Usage Protocol
1. Format input financial parameters into JSON matching schemas in `models/`.
2. Run the appropriate script via Python CLI with `--format markdown` or `--format json`.
3. Synthesize the findings into an executive report with valuation tables, debt bridge, and risk warnings.

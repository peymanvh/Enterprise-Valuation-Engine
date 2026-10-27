---
name: enterprise-valuation
description: Institutional Corporate Enterprise, Venture Capital, Project Feasibility, and Patent Valuation Engine based on McKinsey 8th Ed, Damodaran, and UNIDO standards.
author: Lead Financial Architect & AI Systems Engineer
version: 1.0.0
---

# Enterprise Valuation Engine (Antigravity Native Skill)

Equips Antigravity agents with mathematically verified valuation capabilities adhering to McKinsey 8th Edition, Damodaran, and UNIDO standards.

## Script Invocation
Execute standalone scripts via CLI from the workspace:
- Corporate DCF: `python skills/enterprise-valuation/scripts/dcf_mckinsey.py --input models/sample_corporate_dcf.json`
- Multiples: `python skills/enterprise-valuation/scripts/multiples_valuation.py --input models/sample_peers_multiples.json`
- Startup & VC: `python skills/enterprise-valuation/scripts/startup_venture.py --input models/sample_startup_saas.json`
- Feasibility: `python skills/enterprise-valuation/scripts/commercial_project.py --input models/sample_trade_project.json`
- Patents & IP: `python skills/enterprise-valuation/scripts/ip_patent_val.py --input models/sample_patent_ip.json`
- Monte Carlo: `python skills/enterprise-valuation/scripts/monte_carlo_simulator.py --input models/sample_monte_carlo.json`

## Audit Standards
- **Invested Capital:** Operating Cash + OWC + Net PP&E + Capitalized R&D/Leases - NIBCL.
- **Key Value Driver:** Value = NOPAT * (1 - g/ROIC) / (WACC - g).
- **Harmonic Mean:** Harmonic mean used for multiples to prevent positive denomination bias.
- **Bankability:** Covenants require DSCR >= 1.30x and LLCR >= 1.40x.

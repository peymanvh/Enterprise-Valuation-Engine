---
name: mna-valuation
description: M&A Transaction Structuring, Acquired Asset Valuation, Synergy Modeling, and Purchase Price Allocation (PPA) based on Evans & Mellen and McKinsey 8th Edition.
author: Lead Financial Architect & AI Systems Engineer
version: 1.0.0
---

# M&A & Acquired Asset Valuation Skill (Claude Code)

Use this skill when analyzing corporate mergers, acquisitions, acquired asset portfolios, or PPA fair value accounting.

## Script Invocation
Execute the M&A deal engine:
```bash
python skills/enterprise-valuation/scripts/mna_deal_valuation.py --input models/sample_mna_deal.json --format markdown
```

## Core Standards
- **Value Created for Acquirer:** Net PV of Synergies - Control Premium Paid.
- **Synergy Risk Spread:** Cost synergies at Target WACC; revenue synergies at WACC + 2.5% execution penalty.
- **PPA Balance Sheet:** Tangible FV Step-Up + Identifiable Intangibles (Patents, Customer lists, Brands) + Residual Goodwill.

---
name: mna-valuation
version: 1.0.0
description: M&A Transaction Structuring, Acquired Asset Valuation, Synergy Modeling, and Purchase Price Allocation (PPA) based on Evans & Mellen and McKinsey 8th Edition.
author: Lead Financial Architect & AI Systems Engineer
license: MIT
metadata:
  frameworks:
    - Frank Evans & Chris Mellen (Valuation for M&A, Wiley Finance)
    - McKinsey Valuation (8th Edition, Part V: Portfolio Strategy & M&A)
    - IFRS 3 Business Combinations & US GAAP ASC 805 / ASC 820
---

# 🤝 M&A, Acquired Assets & Corporate Transaction Valuation Skill

## 1. Overview & Capabilities
The `mna-valuation` skill specializes in evaluating business combinations, asset mergers, and corporate acquisitions for both public corporations and private mid-market enterprises:
1. **Synergies Valuation & Risk Phasing:** Disaggregates and values cost, revenue, capex, and financial synergies under differential risk-adjusted hurdle rates (McKinsey 8th Ed.).
2. **Value Creation Bridge & Winner's Curse Detection:** Computes maximum walk-away purchase price and determines whether transaction consideration destroys acquirer shareholder value.
3. **Private Target Normalization (Evans & Mellen):** Officer compensation normalization, Discount for Lack of Marketability (DLOM), and Discount for Lack of Control (DLOC).
4. **Purchase Price Allocation (PPA - IFRS 3 / ASC 805):** Allocates transaction consideration to tangible asset fair value step-ups, identifiable intangible assets (patents, customer relationships, trade names), and residual goodwill.

---

## 2. Trigger Conditions
Activate this skill when the user asks for:
- M&A valuation, merger feasibility, or acquisition offer pricing.
- Synergy estimation (cost vs. revenue synergies, net PV of synergies).
- Purchase Price Allocation (PPA) or acquired asset accounting (IFRS 3 / ASC 805).
- Private company valuation adjustments, DLOM, DLOC, or Control Premium.
- Accretion/dilution analysis or winner's curse audit in an acquisition.

---

## 3. CLI Execution Engine
Execute the standalone engine directly:
```bash
python skills/enterprise-valuation/scripts/mna_deal_valuation.py --input models/sample_mna_deal.json --format markdown
```

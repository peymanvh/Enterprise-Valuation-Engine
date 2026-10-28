---
name: mergers-acquisitions-valuation
version: 1.0.0
description: M&A, Acquired Assets, Private Company Valuation, Synergies, DLOM/DLOC, and Distressed Liquidation Engine based on Chris Mellen & Frank Evans, ASC 805 / IFRS 3, and McKinsey M&A strategy.
author: Lead Financial Architect & AI Systems Engineer
license: MIT
metadata:
  frameworks:
    - Mellen & Evans Valuation for M&A (2nd/3rd Ed)
    - McKinsey M&A Strategy & Value Creation
    - ASC 805 / IFRS 3 Purchase Price Allocation (PPA)
    - AICPA / ASA Private Company Valuation (DLOM/DLOC)
    - Turnaround Management Association (TMA) Distressed Liquidation
---

# 🏢 Mergers & Acquisitions and Acquired Assets Valuation Engine

## 1. Overview & Capabilities
The `mergers-acquisitions-valuation` skill equips AI agents to execute rigorous, institutional-grade valuation, deal structuring, and asset recovery assessments:
1. **Private Company Valuation & 5 Levels of Value:** Complete hierarchical valuation from Synergistic Value down to Private Minority Non-Marketable Value based on Mellen & Evans framework.
2. **Discounts & Premiums Quantification:** Calculation of Control Premiums, Discount for Lack of Control (DLOC), and empirical + option-based Discount for Lack of Marketability (DLOM via Chaffe Put Option model).
3. **Synergy Valuation & Risk Haircut Modeling:** Disaggregation of Cost Synergies (higher realization, lower risk discount rate) vs. Revenue Synergies (lower realization, execution spread), net of integration and restructuring costs.
4. **Max Purchase Price & Walk-Away Discipline:** Standalone value plus risk-adjusted net synergies to prevent the "Winner's Curse" and determine value captured by acquirer vs. target.
5. **Accretion / Dilution (EPS Analysis):** Detailed pro-forma earnings analysis under cash, debt, and stock transaction structures, identifying break-even synergy hurdles.
6. **Distressed & Acquired Assets Liquidation Waterfall:** Valuation of distressed, pledged, or foreclosed business assets under Orderly Liquidation Value (OLV) and Forced Liquidation Value (FLV / fire-sale), followed by absolute priority claims distribution.
7. **Purchase Price Allocation (PPA - ASC 805 / IFRS 3):** Fair value allocation across tangible net assets, identifiable intangibles (technology, customer relationships, trade names), step-up deferred tax liabilities (DTL), and residual goodwill.

---

## 2. Trigger Conditions
Activate this skill when the user asks for:
- Valuation of a private company or non-marketable equity interest.
- Mergers and acquisitions (M&A) pricing, purchase offer analysis, or transaction structuring.
- Modeling cost or revenue synergies, integration costs, or maximum walk-away purchase price.
- Quantification of Control Premium, DLOC, or DLOM (Chaffe put option or restricted stock benchmarks).
- EPS accretion or dilution analysis for cash, debt, or equity-financed acquisitions.
- Valuation of distressed assets, foreclosed assets, or collateral liquidation (Orderly Liquidation Value vs. Forced Liquidation Value).
- Purchase Price Allocation (PPA), goodwill calculation, or intangible asset recognition under ASC 805 / IFRS 3.

---

## 3. Tool & Script Execution Directory
All quantitative engines are implemented as pure Python scripts located in `scripts/`:

| Script File | Primary Capability | Key Outputs |
| :--- | :--- | :--- |
| `scripts/ma_synergy_valuation.py` | Risk-Adjusted Synergy & Max Walk-Away Price | PV of Cost/Rev Synergies, Net Synergy Value, Max Purchase Price, Buyer Value Creation |
| `scripts/private_dlom_dloc.py` | 5 Levels of Value & DLOM/DLOC Engine | DLOC, Chaffe Option DLOM, Full 5-tier Value Hierarchy |
| `scripts/distressed_asset_liquidation.py` | Distressed & Acquired Asset Liquidation Waterfall | Gross OLV/FLV, Wind-Down Costs, Priority Claims Recovery %, Equity Residual |
| `scripts/accretion_dilution.py` | Pro-Forma EPS Accretion / Dilution Engine | Pro-Forma EPS, Dilution %, Financing Drag, Breakeven Synergy Required |

---

## 4. Execution Workflow
When executing an M&A or Acquired Asset valuation:
1. **Identify the Standard and Level of Value:** Determine whether the transaction requires Standalone Marketable Value, Controlling Private Value, or Synergistic Strategic Value.
2. **Run Synergy Valuation:** Separate cost and revenue synergies, apply probabilistic realization haircuts (e.g., $80\%$ cost, $40\%$ revenue), and discount at risk-adjusted rates.
3. **Establish Pricing Bounds:** Determine Target Reservation Price (minimum offer) and Acquirer Walk-Away Price (standalone + net synergies).
4. **Evaluate Funding Mix & EPS Impact:** Run accretion/dilution analysis to identify impact on buyer EPS and required synergy hurdles.
5. **For Distressed / Asset Transactions:** Apply recovery rates to current asset categories, deduct administrative wind-down fees, and run the priority claims waterfall.

# 📘 M&A Deal Structuring, Private Valuation & Purchase Price Allocation (PPA)

> **Core References:**
> - Frank C. Evans & David M. Bishop / Chris M. Mellen — *Valuation for M&A: Building and Measuring Private Company Value*, 3rd Edition (Wiley Finance).
> - McKinsey & Company — *Valuation: Measuring and Managing the Value of Companies*, 8th Edition (Part V: Corporate Portfolio Strategy & M&A).
> - IFRS 3 (*Business Combinations*) & US GAAP ASC 805 / ASC 820.

---

## 1. The Fundamental Equation of M&A Value Creation
Under the McKinsey and Evans/Mellen frameworks, an acquisition creates value for the buyer's shareholders **if and only if** the present value of net synergies exceeds the acquisition premium paid to target shareholders:

$$\text{Value Created for Acquirer} = \text{PV of Synergies (Net of Integration Costs)} - \text{Acquisition Premium Paid}$$

### Maximum Purchase Price (Walk-Away Price):
$$\text{Max Offer Price} = \text{Standalone Target Value} + \text{Net PV of Synergies}$$

If an acquirer pays more than the Max Offer Price, the transaction destroys shareholder value (the classic **"Winner's Curse"**).

---

## 2. Synergies Decomposition & Risk-Adjusted Discounting
McKinsey 8th Ed. emphasizes that synergies must not be discounted at a single blended WACC because different synergy streams possess radically different risk profiles:

1. **Cost Synergies (Headcount redundancy, procurement economies, duplicate ERP consolidation):**
   - High certainty of realization.
   - Discounted at: **Target WACC** or $\text{Target WACC} + 1.0\%$.
2. **Revenue Synergies (Cross-selling, pricing power, new geography entry):**
   - High execution and customer attrition risk.
   - Discounted at: **Target Cost of Equity** or $\text{Target WACC} + 2.5\% \text{ to } 4.0\%$.
3. **Integration Capex & Disruption Costs:**
   - Severance, platform migration, rebranding.
   - Deducted directly from gross synergies on an after-tax basis: $\text{Cost} \times (1 - T)$.

---

## 3. Private Company Valuation Adjustments (Evans & Mellen)
Valuing private targets requires adjusting public market benchmarks for liquidity and governance control:

### A. Owner/Officer Compensation Normalization:
Private company owners often take above-market distributions as salary to minimize corporate tax, or below-market salary to show inflated profits. Adjust reported EBITDA to arm's-length executive replacement compensation:
$$\Delta \text{EBITDA} = \text{Reported Officer Comp} - \text{Market Replacement Comp}$$

### B. Control Premium and Discount for Lack of Control (DLOC):
$$\text{DLOC} = 1 - \frac{1}{1 + \text{Control Premium}}$$
- Typical transaction control premium: $20\% - 35\%$ ($\text{DLOC} \approx 16\% - 26\%$).

### C. Discount for Lack of Marketability (DLOM):
Private shares cannot be sold within days on a public exchange. DLOM reflects the cost of an illiquid holding period:
- **Restricted Stock & Pre-IPO Studies:** DLOM typically ranges from $15\%$ to $30\%$.
- **Quantitative Option Pricing (Finnerty / Chaffe Put Models):** Pricing the restriction as an Asian lookback put option on the asset's volatility over holding horizon $T$.

---

## 4. Purchase Price Allocation (PPA - IFRS 3 / ASC 805)
Upon closing, the total purchase consideration must be allocated to the fair value of acquired assets and liabilities:

$$\text{Total Purchase Price} = \text{Book Value of Net Assets} + \text{Tangible FV Step-Up} + \sum \text{Identifiable Intangible Assets} + \text{Goodwill}$$

### Hierarchy of Identifiable Intangibles:
1. **Technology & Patents:** Valued via Relief-from-Royalty or MPEEM.
2. **Customer Contracts & Relationships:** Valued via MPEEM.
3. **Trademarks & Brand Names:** Valued via Relief-from-Royalty.
4. **Residual Goodwill:** Excess of purchase price over net identifiable fair value. Goodwill is not amortized under IFRS/US GAAP, but tested annually for impairment.

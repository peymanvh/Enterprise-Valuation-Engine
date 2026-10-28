# 🏢 Valuation for M&A: Building and Measuring Private Company Value
> **Primary Source:** Chris M. Mellen & Frank C. Evans (*Valuation for M&A: Building and Measuring Private Company Value*, 2nd/3rd Edition, Wiley Finance), complemented by McKinsey M&A Valuation and AICPA Valuation Standards.

---

## 1. The Five Levels of Value Framework
In M&A and private company valuation, value is not a single number; it depends on the standard of value, the degree of control, and marketability:

1. **Synergistic / Strategic Value:** Value to a specific strategic acquirer including unique operating, financial, and tax synergies.
2. **Controlling Interest Marketable Value:** Value of a controlling 100% interest as if freely traded in an active public market.
3. **Controlling Interest Non-Marketable Value:** Value of a controlling interest in a private enterprise lacking an immediate public trading mechanism (reflecting illiquidity during exit).
4. **Minority Interest Marketable Value (As-if-freely-traded):** Value of a non-controlling block in a publicly traded company.
5. **Minority Interest Non-Marketable Value:** Value of a non-controlling block in a privately held firm (subject to both DLOC and DLOM).

---

## 2. Discounts and Premiums Mathematical Formulations

### A. Discount for Lack of Control (DLOC) & Control Premium (CP)
Derived from observed merger transactions (e.g., Mergerstat / DealStats):
$$\text{DLOC} = 1 - \frac{1}{1 + \text{Control Premium}}$$

Example: If median control premium is $35\%$:
$$\text{DLOC} = 1 - \frac{1}{1 + 0.35} = 1 - 0.7407 = 25.93\%$$

### B. Discount for Lack of Marketability (DLOM)
Represents the impairment to value resulting from the absence of a ready, liquid public market:
$$\text{Private Minority Value} = \text{Control Marketable Value} \times (1 - \text{DLOC}) \times (1 - \text{DLOM})$$

**Quantification Methods:**
1. **Restricted Stock Studies (SEC Rule 144):** Empirical discounts historically range from $15\%$ to $35\%$.
2. **Pre-IPO Studies (Emory / Valuation Advisors):** Discounts observed between pre-IPO transaction prices and IPO prices ($25\% - 45\%$).
3. **Quantitative Option-Pricing Models:**
   - **Chaffe European Put Option Model:** DLOM equals the cost of an at-the-money put option divided by the stock price:
     $$\text{DLOM} \approx \frac{P_{\text{put}}(S, K=S, T, \sigma, r)}{S}$$
   - **Finnerty Strike-Averaging Asian Put Model:** Calculates the option to sell at the average price over the holding period, eliminating extreme volatility bias.

---

## 3. Synergy Valuation & Realization Haircuts

### Synergy Categories:
1. **Cost Synergies (Higher certainty, lower risk):**
   - Headcount rationalization (SG&A overlap).
   - Supply chain and volume procurement economies.
   - IT/ERP system consolidation and facility closure.
   - Historical realization rate: $70\% - 90\%$.
2. **Revenue Synergies (Lower certainty, higher execution risk):**
   - Cross-selling across customer bases.
   - Geographic market expansion.
   - Pricing power enhancement.
   - Historical realization rate: $30\% - 50\%$.
3. **Financial / Tax Synergies:**
   - Increased debt capacity (lower composite WACC).
   - Utilization of accumulated Net Operating Losses (NOLs).

### Mathematical Valuation:
$$\text{PV}(\text{Synergies}) = \sum_{t=1}^n \frac{(\text{Cost Synergies}_t \times p_{\text{cost}} + \text{Revenue Synergies}_t \times \text{Margin} \times p_{\text{rev}}) \times (1 - T) - \text{Integration Cost}_t}{(1 + \text{WACC}_{\text{synergy}})^t} + \text{Terminal Synergy Value}$$

> **Key Rule (Mellen & Evans):** Always discount revenue synergies at a higher discount rate ($\text{WACC} + 200\text{ to }400\text{ bps}$) due to heightened execution failure rates.

---

## 4. Maximum Purchase Price (Walk-Away Price)
$$\text{Max Purchase Price} = \text{Standalone Target Value} + \text{PV}(\text{Net Synergies})$$
- **Target Reservation Price:** Lowest price the target shareholders will accept (typically Standalone Value + minimum control premium).
- **Acquirer Value Capture:** The value created for the buyer is $\text{PV}(\text{Net Synergies}) - \text{Premium Paid}$. If Premium Paid exceeds Net Synergies, the transaction destroys buyer equity value (the "Winner's Curse").

---

## 5. Accretion / Dilution Analysis (EPS Impact)
Evaluates whether pro-forma earnings per share (EPS) increase or decrease post-transaction:

$$\text{Pro-Forma Net Income} = \text{Acquirer Net Income} + \text{Target Net Income} + \text{After-Tax Synergies} - \text{After-Tax New Interest Expense} - \text{Foregone Interest on Cash Used}$$

$$\text{Pro-Forma Shares} = \text{Acquirer Existing Shares} + \text{New Shares Issued to Finance Purchase}$$

$$\text{Pro-Forma EPS} = \frac{\text{Pro-Forma Net Income}}{\text{Pro-Forma Shares}}$$

$$\text{Accretion / Dilution \%} = \frac{\text{Pro-Forma EPS} - \text{Acquirer Standalone EPS}}{\text{Acquirer Standalone EPS}} \times 100$$

---

## 6. Acquired & Distressed Assets Valuation (Asset Recovery / Liquidation)
In distressed M&A, asset-based transactions, or foreclosed corporate asset purchases:

1. **Orderly Liquidation Value (OLV):** The gross amount of proceeds expected from a commercial liquidation sale conducted with a reasonable time to find a buyer (typically 6–12 months).
2. **Forced Liquidation Value (FLV / Fire-Sale):** The gross amount expected under immediate auction or pressure conditions (typically 30–90 days).
3. **Net Realizable Liquidation Value (NRLV):**
   $$\text{NRLV} = \sum (\text{Asset Recovery Factor}_i \times \text{Book Value}_i) - \text{Liquidation Expenses} - \text{Priority & Senior Claims}$$

Typical recovery benchmarks for distressed assets:
- **Cash & Equivalents:** $100\%$
- **Accounts Receivable:** $60\% - 85\%$ (discounted for bad debt, uncollectible dispute accounts)
- **Inventory (Raw materials):** $40\% - 65\%$
- **Inventory (Work in progress - WIP):** $10\% - 30\%$
- **Inventory (Finished goods):** $50\% - 75\%$
- **Machinery & Specialized Equipment:** $25\% - 50\%$ (FLV) / $50\% - 70\%$ (OLV)
- **Real Estate:** $65\% - 80\%$ (FLV) / $80\% - 95\%$ (OLV)
- **Unpatented Intangibles / General Goodwill:** $0\% - 5\%$

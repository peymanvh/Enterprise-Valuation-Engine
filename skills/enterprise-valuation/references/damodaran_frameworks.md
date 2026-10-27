# 📘 Damodaran Valuation Frameworks: Risk, Distress & Narrative

> **Primary Source:** Prof. Aswath Damodaran (NYU Stern School of Business) — *Investment Valuation*, *The Dark Side of Valuation*, *Narrative and Numbers*.

---

## 1. Free Cash Flow to Firm (FCFF) vs. Equity (FCFE)

### Free Cash Flow to Firm (FCFF):
Cash flow available to all capital providers (equity, debt, preferred) after operating expenses, taxes, and capital investments:
$$\text{FCFF} = \text{EBIT}(1 - T) + \text{Depreciation} - \text{Capex} - \Delta \text{Working Capital}$$
Discounted at the **WACC**.

### Free Cash Flow to Equity (FCFE):
Cash flow available strictly to common shareholders after interest payments and net debt repayments:
$$\text{FCFE} = \text{Net Income} + \text{Depreciation} - \text{Capex} - \Delta \text{Working Capital} + (\text{New Debt Issued} - \text{Debt Repaid})$$
Discounted at the **Cost of Equity ($K_e$)**.

---

## 2. Country Risk Premium (CRP) in Emerging & Global Markets
When valuing multinational corporations or operations in emerging markets, add Country Risk Premium:

$$K_e = R_f + \beta \times \text{Mature Market ERP} + \lambda \times \text{CRP}$$

Where:
- $\lambda$: Relative exposure factor ($\text{Revenues}_{\text{country}} / \text{Revenues}_{\text{total}}$).
- $\text{CRP} = \text{Country Sovereign Default Spread} \times \left(\frac{\sigma_{\text{Equity}}}{\sigma_{\text{Govt Bond}}}\right)$.

---

## 3. Synthetic Credit Ratings & Synthetic Cost of Debt
For unrated private companies or emerging startups with debt:
1. Compute the **Interest Coverage Ratio**:
   $$\text{ICR} = \frac{\text{EBIT}}{\text{Interest Expense}}$$
2. Map to Damodaran's Institutional Rating Matrix:

| Interest Coverage Ratio (Large Firms) | Synthetic Rating | Typical Default Spread |
| :---: | :---: | :---: |
| $> 8.50$ | AAA | 0.65% |
| $6.50 - 8.50$ | AA | 0.85% |
| $5.50 - 6.50$ | A+ | 1.10% |
| $4.25 - 5.50$ | A | 1.25% |
| $3.00 - 4.25$ | BBB | 1.60% |
| $2.50 - 3.00$ | BB+ | 2.50% |
| $2.00 - 2.50$ | BB | 3.00% |
| $1.50 - 2.00$ | B+ | 4.00% |
| $1.25 - 1.50$ | B | 5.50% |
| $0.80 - 1.25$ | CCC | 8.00% |
| $< 0.80$ | D / Insolvent | 12.00%+ |

Pre-tax Cost of Debt:
$$K_d = R_f + \text{Default Spread} + \text{Country Default Spread}$$

---

## 4. Distressed Asset & Probability of Failure Overlay
In distressed situations, standard DCF models overstate value by implicitly assuming perpetual survival (going-concern bias). 

### The Dual-State Distress Model:
$$\text{Enterprise Value} = \text{DCF Going Concern Value} \times (1 - P_{\text{distress}}) + \text{Liquidation Value} \times P_{\text{distress}}$$

Where:
- $P_{\text{distress}}$: Estimated via bond yield spreads, credit ratings, or Altman Z-score.
- $\text{Liquidation Value}$: Proceeds realized in a forced auction, typically $30\% - 50\%$ of book value of assets.

---

## 5. Narrative and Numbers Matrix
Every financial projection corresponds to a testable corporate narrative:
1. **The Size of the Market:** Imposes a ceiling on long-term terminal revenues.
2. **The Nature of Competition:** Determines whether operating margins expand or decay toward the industry average.
3. **The Capital Intensity:** Dictates the sales-to-capital ratio and reinvestment required for each dollar of revenue growth.

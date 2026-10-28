# 📘 Intellectual Property & Patent Valuation: IFRS 13, WIPO & Real Options

> **Standards & Guidelines:** IFRS 13 (Fair Value Measurement), US GAAP ASC 820 / ASC 805, WIPO (World Intellectual Property Organization), USPTO IP Valuation Manuals.

---

## 1. Hierarchy of IP Valuation Approaches
Under international accounting standards, patent and intangible asset valuation follows three recognized approaches:
1. **Income Approach:** Relief-from-Royalty, Multi-Period Excess Earnings Method (MPEEM), and Real Options.
2. **Market Approach:** Comparable licensing transaction databases (RoyaltyStat, ktMINE).
3. **Cost Approach:** Depreciated Replacement Cost (DRC) — primarily applicable only to early software code or pre-clinical formulations.

---

## 2. Relief-from-Royalty Method
Hypothesizes what the owner would pay in licensing royalties to a third party if it did not own the intellectual property.

### Mathematical Formulation:
$$\text{Value}_{\text{Pre-TAB}} = \sum_{t=1}^T \frac{\text{Projected Revenue}_t \times r_{\text{royalty}} \times (1 - T)}{(1 + k_{\text{IP}})^t}$$

Where:
- $r_{\text{royalty}}$: Arm's-length royalty rate determined via comparable transactions or the **25% Rule of Thumb** (royalty equals $25\%$ of expected operating profit margin).
- $T$: Corporate marginal tax rate.
- $k_{\text{IP}}$: Discount rate incorporating technology obsolescence and IP risk premium ($k_{\text{IP}} = \text{WACC} + 2\% \text{ to } 6\%$).

### Tax Amortization Benefit (TAB):
Because patents are amortizable for tax purposes (e.g. 15 years under US IRC § 197), the tax shelter adds incremental fair value:

$$\text{TAB Factor} = \frac{1}{1 - \frac{T}{n \cdot k_{\text{IP}}} \left[1 - (1 + k_{\text{IP}})^{-n}\right]}$$
$$\text{Fair Value}_{\text{Post-TAB}} = \text{Value}_{\text{Pre-TAB}} \times \text{TAB Factor}$$

---

## 3. Multi-Period Excess Earnings Method (MPEEM)
Used when the patent or core proprietary technology is the primary driver of excess economic earnings.

### Contributory Asset Charges (CAC):
Deduct fair returns on supporting assets required to generate cash flow:
$$\text{Excess Earnings}_t = \text{NOPAT}_t - \sum \text{CAC}_t$$

$$\sum \text{CAC}_t = (\text{Working Capital}_t \times r_{\text{wc}}) + (\text{Net PPE}_t \times r_{\text{ppe}}) + (\text{Assembled Workforce}_t \times r_{\text{wf}}) + (\text{Brand}_t \times r_{\text{brand}})$$

Typical Hurdle Rates for CAC:
- Working Capital ($r_{\text{wc}}$): Short-term borrowing cost ($4\% - 6\%$).
- Net PP&E ($r_{\text{ppe}}$): Secured asset financing ($7\% - 9\%$).
- Assembled Workforce ($r_{\text{wf}}$): Cost of Equity ($10\% - 14\%$).

---

## 4. Real Options Valuation (Black-Scholes Model)
R&D and early-stage patent portfolios represent valuable managerial flexibility: management has the right (but not the obligation) to commit commercialization capital after technical feasibility is proven.

### Black-Scholes Mapping:
| Financial Call Option Parameter | Patent / R&D Analog |
| :--- | :--- |
| **Stock Price ($S$)** | Present Value of future commercial net cash flows upon launch |
| **Strike Price ($K$)** | Capital expenditure required to commercialize / scale manufacturing |
| **Time to Expiry ($T$)** | Remaining patent protection window or competitive exclusivity window |
| **Risk-Free Rate ($r$)** | Sovereign yield matching horizon $T$ |
| **Volatility ($\sigma$)** | Annualized volatility of expected commercial cash flows ($35\% - 60\%$) |

### Equations:
$$C = S \cdot N(d_1) - K \cdot e^{-rT} \cdot N(d_2)$$
$$d_1 = \frac{\ln(S / K) + \left(r + \frac{\sigma^2}{2}\right)T}{\sigma \sqrt{T}}, \quad d_2 = d_1 - \sigma \sqrt{T}$$

# 📑 Purchase Price Allocation (PPA) & Intangible Asset Recognition (ASC 805 / IFRS 3)

---

## 1. Core Principles of Business Combinations Accounting
Under ASC 805 and IFRS 3:
1. **Acquisition Method:** All business combinations must be accounted for by identifying the acquirer, determining the acquisition date, and recognizing the identifiable assets acquired, liabilities assumed, and non-controlling interests at **Fair Value**.
2. **Purchase Consideration:** Total consideration transferred includes cash, fair value of shares issued, debt assumed, and the fair value of contingent consideration (earnout).

---

## 2. Purchase Price Allocation (PPA) Mechanics
The allocation follows a strict waterfall:

$$\text{Purchase Price (Consideration Transferred)}$$
$$- \quad \text{Fair Value of Tangible Net Assets (Working Capital, PP\&E, Leases)}$$
$$- \quad \text{Fair Value of Identifiable Intangibles (IP, Brands, Customer Contracts, Technology)}$$
$$+ \quad \text{Deferred Tax Liabilities (DTL) created by Fair Value Step-Up}$$
$$\mathbf{= \quad \text{Goodwill (Residual)}}$$

### Deferred Tax Liability (DTL) on Asset Step-Up:
In a stock purchase (non-Section 338(h)(10) in US tax code), the tax basis of assets is not stepped up for tax purposes, creating a temporary taxable difference:
$$\text{DTL} = (\text{Fair Value of Identified Intangibles and Tangible Step-Up}) \times \text{Marginal Tax Rate}$$
This DTL increases recorded Goodwill dollar-for-dollar.

---

## 3. Valuation Methods for Acquired Intangible Assets

| Intangible Category | Primary Valuation Method | Secondary / Cross-Check Method |
| :--- | :--- | :--- |
| **Customer Relationships** | Multi-Period Excess Earnings Method (MPEEM) | With-and-Without Method |
| **Developed Technology / Software** | Multi-Period Excess Earnings Method (MPEEM) | Relief-from-Royalty / Replacement Cost |
| **Brand / Trademark / Trade Names** | Relief-from-Royalty Method | Premium Profit Method |
| **Non-Compete Agreements** | With-and-Without Method | Lost Profits Method |
| **Patents & Proprietary Algorithms** | Relief-from-Royalty or MPEEM | Greenfield Method |

### A. Multi-Period Excess Earnings Method (MPEEM)
Used for the primary income-generating "primary asset":
$$\text{Excess Earnings}_t = \text{Operating Cash Flow}_t - \text{Contributory Asset Charges (CAC)}_t$$
Where Contributory Asset Charges (CAC) represent the fair economic return required on all supporting assets:
- Working capital charge ($r_{\text{wc}} \times \text{NWC}$)
- PP&E fixed asset charge ($r_{\text{ppe}} \times \text{PP\&E}$)
- Brand charge ($r_{\text{brand}} \times \text{Revenues}$)
- Assembled workforce charge

### B. Relief-from-Royalty Method
Measures the hypothetical royalty savings obtained by owning the asset rather than licensing it:
$$\text{Value} = \sum_{t=1}^T \frac{\text{Revenue}_t \times \text{Royalty Rate} \times (1 - \text{Tax Rate})}{(1 + \text{Discount Rate})^t} + \text{Tax Amortization Benefit (TAB)}$$

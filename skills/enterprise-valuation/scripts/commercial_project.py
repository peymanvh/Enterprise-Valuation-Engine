#!/usr/bin/env python3
"""
commercial_project.py - Commercial Trade & Industrial Project Feasibility Engine
Based on UNIDO (Manual for the Preparation of Industrial Feasibility Studies).
Computes Cash Conversion Cycle (CCC), Trade Finance costs, CFADS, DSCR, LLCR, PLCR,
NPV, IRR, MIRR, Payback Periods, and Break-Even thresholds.
"""

import sys
import json
import math
import argparse
from typing import Dict, List, Any, Optional

def compute_npv(rate: float, cash_flows: List[float]) -> float:
    return sum(cf / math.pow(1.0 + rate, t) for t, cf in enumerate(cash_flows))

def compute_irr(cash_flows: List[float], max_iter: int = 1000, tol: float = 1e-7) -> Optional[float]:
    """
    Newton-Raphson solver for IRR.
    """
    # Quick sanity check for sign changes
    has_pos = any(cf > 0 for cf in cash_flows)
    has_neg = any(cf < 0 for cf in cash_flows)
    if not (has_pos and has_neg):
        return None

    rate = 0.10  # Initial guess
    for _ in range(max_iter):
        npv_val = 0.0
        deriv = 0.0
        for t, cf in enumerate(cash_flows):
            denom = math.pow(1.0 + rate, t)
            npv_val += cf / denom
            if t > 0:
                deriv -= (t * cf) / (denom * (1.0 + rate))
        
        if abs(deriv) < 1e-12:
            break
        new_rate = rate - (npv_val / deriv)
        if abs(new_rate - rate) < tol:
            return new_rate
        rate = new_rate
        if rate < -0.99 or rate > 10.0:  # Escape runaway bounds
            break
            
    # Fallback bisection if Newton fails
    low, high = -0.90, 5.0
    for _ in range(100):
        mid = (low + high) / 2.0
        val = sum(cf / math.pow(1.0 + mid, t) for t, cf in enumerate(cash_flows))
        if abs(val) < tol:
            return mid
        val_low = sum(cf / math.pow(1.0 + low, t) for t, cf in enumerate(cash_flows))
        if (val_low > 0 and val > 0) or (val_low < 0 and val < 0):
            low = mid
        else:
            high = mid
    return mid

def compute_mirr(cash_flows: List[float], finance_rate: float, reinvestment_rate: float) -> Optional[float]:
    """
    Modified Internal Rate of Return (MIRR):
    MIRR = (FV(positive CFs @ reinvestment) / PV(negative CFs @ finance))^(1/n) - 1
    """
    n = len(cash_flows) - 1
    if n <= 0:
        return None
    
    pv_negative = 0.0
    fv_positive = 0.0
    for t, cf in enumerate(cash_flows):
        if cf < 0:
            pv_negative += abs(cf) / math.pow(1.0 + finance_rate, t)
        else:
            fv_positive += cf * math.pow(1.0 + reinvestment_rate, n - t)
            
    if pv_negative <= 0 or fv_positive <= 0:
        return None
        
    return math.pow(fv_positive / pv_negative, 1.0 / n) - 1.0

class CommercialProjectEngine:
    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.project_name = data.get("project_name", "Feasibility Project")
        self.currency = data.get("currency", "USD")
        self.discount_rate = float(data.get("discount_rate", 0.10))
        self.equity_discount_rate = float(data.get("equity_discount_rate", 0.13))
        self.reinvestment_rate = float(data.get("reinvestment_rate", self.discount_rate))
        self.cost_of_debt = float(data.get("cost_of_debt", 0.07))
        self.initial_investment = float(data.get("initial_investment", 10_000_000))
        self.initial_debt = float(data.get("initial_debt", 6_000_000))
        self.initial_equity = float(data.get("initial_equity", self.initial_investment - self.initial_debt))
        self.covenants = data.get("covenants", {"min_dscr": 1.30, "min_llcr": 1.40})
        self.periods = data.get("periods", [])
        self.warnings: List[str] = []

    def evaluate(self) -> Dict[str, Any]:
        project_cfs = [-self.initial_investment]
        equity_cfs = [-self.initial_equity]

        period_evaluations = []
        dscr_list = []
        debt_balance = self.initial_debt
        
        # Working capital & CCC analysis
        ccc_records = []

        for p in self.periods:
            t = int(p["year"])
            revenue = float(p.get("revenue", 0.0))
            cogs = float(p.get("cogs", 0.0))
            operating_expenses = float(p.get("operating_expenses", 0.0))
            ebitda = float(p.get("ebitda", revenue - cogs - operating_expenses))
            taxes = float(p.get("taxes", 0.0))
            capex = float(p.get("capex", 0.0))
            
            # Working capital / Trade Cycle calculations
            ar = float(p.get("accounts_receivable", 0.0))
            inv = float(p.get("inventory", 0.0))
            ap = float(p.get("accounts_payable", 0.0))
            change_in_wc = float(p.get("change_in_working_capital", 0.0))
            
            # CCC components
            dso = (ar / revenue * 365.0) if revenue > 0 else 0.0
            dio = (inv / cogs * 365.0) if cogs > 0 else 0.0
            dpo = (ap / cogs * 365.0) if cogs > 0 else 0.0
            ccc = dso + dio - dpo
            ccc_records.append({"year": t, "dso": dso, "dio": dio, "dpo": dpo, "ccc_days": ccc})

            # Trade financing costs (LC, bill discounting, FX reserve)
            trade_finance_fees = float(p.get("trade_finance_costs", 0.0))

            # CFADS = EBITDA - Taxes - Capex - Change in Working Capital - Trade Finance Costs
            cfads = ebitda - taxes - capex - change_in_wc - trade_finance_fees
            
            # Debt Service
            principal = float(p.get("debt_principal_payment", 0.0))
            interest = float(p.get("debt_interest_payment", debt_balance * self.cost_of_debt if debt_balance > 0 else 0.0))
            debt_service = principal + interest
            
            # Bankability & Cash Sweep / Dividend Lockup Mechanism
            # In institutional project finance, if DSCR < covenant, lenders trigger dividend lockup
            min_covenant_dscr = self.covenants.get("min_dscr", 1.30)
            dividend_lockup = False
            cash_sweep_amount = 0.0

            if debt_service > 0:
                dscr = cfads / debt_service
                dscr_list.append(dscr)
                if dscr < min_covenant_dscr:
                    dividend_lockup = True
                    excess_over_service = max(cfads - debt_service, 0.0)
                    cash_sweep_amount = excess_over_service  # 100% swept to reserve or debt prepayment
                    self.warnings.append(
                        f"Year {t}: DSCR ({dscr:.2f}x) breaches bank covenant ({min_covenant_dscr:.2f}x). "
                        "LENDER COVENANT TRIGGERED: Mandatory Dividend Lockup enforced. 100% of excess cash swept to Debt Service Reserve."
                    )
            else:
                dscr = None

            # Distributable Free Cash Flow to Equity (FCFE):
            raw_fcfe = cfads - debt_service
            distributable_fcfe = 0.0 if dividend_lockup else max(raw_fcfe, 0.0)
            
            project_cfs.append(cfads)
            equity_cfs.append(distributable_fcfe if not dividend_lockup else min(raw_fcfe, 0.0))

            period_evaluations.append({
                "year": t,
                "revenue": revenue,
                "ebitda": ebitda,
                "taxes": taxes,
                "capex": capex,
                "trade_finance_costs": trade_finance_fees,
                "cfads": cfads,
                "debt_service": debt_service,
                "principal": principal,
                "interest": interest,
                "dscr": dscr,
                "raw_fcfe": raw_fcfe,
                "dividend_lockup": dividend_lockup,
                "cash_sweep_amount": cash_sweep_amount,
                "distributable_fcfe": distributable_fcfe,
                "opening_debt": debt_balance,
                "closing_debt": max(debt_balance - principal - cash_sweep_amount, 0.0)
            })
            debt_balance = max(debt_balance - principal - cash_sweep_amount, 0.0)

        # Loan Life Coverage Ratio (LLCR) and Project Life Coverage Ratio (PLCR)
        # LLCR = NPV of CFADS over loan life / Outstanding Debt
        llcr_list = []
        for idx, pe in enumerate(period_evaluations):
            op_debt = pe["opening_debt"]
            if op_debt > 0:
                # Remaining CFADS in loan horizon
                remaining_cfads = [p["cfads"] for p in period_evaluations[idx:] if p["opening_debt"] > 0 or p["principal"] > 0]
                npv_rem_cfads = sum(c / math.pow(1.0 + self.cost_of_debt, step + 1) for step, c in enumerate(remaining_cfads))
                llcr_val = npv_rem_cfads / op_debt
                llcr_list.append(llcr_val)
                pe["llcr"] = llcr_val
                if llcr_val < self.covenants["min_llcr"]:
                    self.warnings.append(f"Year {pe['year']}: LLCR ({llcr_val:.2f}x) breaches covenant threshold ({self.covenants['min_llcr']:.2f}x).")
            else:
                pe["llcr"] = None

        # Project NPV, IRR, MIRR
        project_npv = compute_npv(self.discount_rate, project_cfs)
        project_irr = compute_irr(project_cfs)
        project_mirr = compute_mirr(project_cfs, self.discount_rate, self.reinvestment_rate)

        # Equity NPV, IRR, MIRR
        equity_npv = compute_npv(self.equity_discount_rate, equity_cfs)
        equity_irr = compute_irr(equity_cfs)
        equity_mirr = compute_mirr(equity_cfs, self.equity_discount_rate, self.reinvestment_rate)

        # Payback period calculation
        cum_cf = 0.0
        simple_payback = None
        for idx, cf in enumerate(project_cfs):
            cum_cf += cf
            if cum_cf >= 0 and simple_payback is None:
                # Interpolate fraction
                prev = cum_cf - cf
                simple_payback = (idx - 1) + (abs(prev) / cf) if cf > 0 else float(idx)

        cum_disc_cf = 0.0
        disc_payback = None
        for idx, cf in enumerate(project_cfs):
            disc_cf = cf / math.pow(1.0 + self.discount_rate, idx)
            cum_disc_cf += disc_cf
            if cum_disc_cf >= 0 and disc_payback is None:
                prev = cum_disc_cf - disc_cf
                disc_payback = (idx - 1) + (abs(prev) / disc_cf) if disc_cf > 0 else float(idx)

        # Break-Even Analysis on Year 1
        y1 = self.periods[0] if self.periods else {}
        y1_rev = float(y1.get("revenue", 1.0))
        y1_fixed = float(y1.get("fixed_operating_costs", float(y1.get("operating_expenses", 0.0)) * 0.60))
        y1_var = float(y1.get("variable_costs", float(y1.get("cogs", 0.0)) + float(y1.get("operating_expenses", 0.0)) * 0.40))
        cm_ratio = (1.0 - (y1_var / y1_rev)) if y1_rev > 0 else 0.0
        be_sales = (y1_fixed / cm_ratio) if cm_ratio > 0 else 0.0
        be_capacity = (be_sales / y1_rev) if y1_rev > 0 else 0.0

        return {
            "project_name": self.project_name,
            "currency": self.currency,
            "project_metrics": {
                "initial_investment": self.initial_investment,
                "project_npv": project_npv,
                "project_irr": project_irr,
                "project_mirr": project_mirr,
                "simple_payback_years": simple_payback,
                "discounted_payback_years": disc_payback
            },
            "equity_metrics": {
                "initial_equity": self.initial_equity,
                "equity_npv": equity_npv,
                "equity_irr": equity_irr,
                "equity_mirr": equity_mirr
            },
            "debt_and_coverage": {
                "initial_debt": self.initial_debt,
                "min_dscr": min(dscr_list) if dscr_list else None,
                "avg_dscr": (sum(dscr_list) / len(dscr_list)) if dscr_list else None,
                "min_llcr": min(llcr_list) if llcr_list else None,
                "covenant_status": "COMPLIANT" if not self.warnings else "BREACH_WARNING"
            },
            "break_even_analysis": {
                "break_even_sales": be_sales,
                "break_even_capacity_utilization": be_capacity,
                "contribution_margin_ratio": cm_ratio
            },
            "cash_conversion_cycle": ccc_records,
            "schedule": period_evaluations,
            "warnings": self.warnings
        }

    def generate_markdown_report(self, res: Dict[str, Any]) -> str:
        lines = []
        c = res["currency"]
        pm = res["project_metrics"]
        em = res["equity_metrics"]
        dc = res["debt_and_coverage"]
        be = res["break_even_analysis"]

        lines.append(f"# 🏭 Commercial & Project Feasibility Report: {res['project_name']}")
        lines.append("**Framework:** UNIDO Industrial Feasibility & Project Finance Standards")
        lines.append("")

        lines.append("## 📌 Key Financial & Investment Returns")
        lines.append("| Metric | Project-Level (All-Equity) | Equity-Level (Levered) | Institutional Benchmark |")
        lines.append("| :--- | :---: | :---: | :---: |")
        lines.append(f"| **Initial Capital** | {c} {pm['initial_investment']:,.0f} | {c} {em['initial_equity']:,.0f} | — |")
        lines.append(f"| **NPV** | **{c} {pm['project_npv']:,.2f}** | **{c} {em['equity_npv']:,.2f}** | $> 0$ |")
        lines.append(f"| **IRR** | **{pm['project_irr']:.2%}** | **{em['equity_irr']:.2%}** | $> \\text{{Discount Rate}}$ |")
        lines.append(f"| **MIRR** | {pm['project_mirr']:.2%} | {em['equity_mirr']:.2%} | Reinvestment realism |")
        pb_str = f"{pm['simple_payback_years']:.1f} yrs" if pm['simple_payback_years'] else "N/A"
        dpb_str = f"{pm['discounted_payback_years']:.1f} yrs" if pm['discounted_payback_years'] else "N/A"
        lines.append(f"| **Payback (Simple / Disc.)** | {pb_str} / {dpb_str} | — | $< \\text{{Debt Tenor}}$ |")
        lines.append("")

        lines.append("## 🛡️ Debt Service & Bankability Metrics")
        lines.append("| Metric | Achieved Value | Covenant Limit | Bankability Audit |")
        lines.append("| :--- | :---: | :---: | :---: |")
        min_d = f"{dc['min_dscr']:.2f}x" if dc['min_dscr'] else "N/A"
        avg_d = f"{dc['avg_dscr']:.2f}x" if dc['avg_dscr'] else "N/A"
        min_l = f"{dc['min_llcr']:.2f}x" if dc['min_llcr'] else "N/A"
        lines.append(f"| **Minimum DSCR** | **{min_d}** | $\\ge 1.30x$ | {'✅ Pass' if dc['min_dscr'] and dc['min_dscr'] >= 1.30 else '⚠️ Breach'} |")
        lines.append(f"| **Average DSCR** | {avg_d} | $\\ge 1.50x$ | {'✅ Healthy' if dc['avg_dscr'] and dc['avg_dscr'] >= 1.50 else '🟡 Tight'} |")
        lines.append(f"| **Minimum LLCR** | {min_l} | $\\ge 1.40x$ | {'✅ Pass' if dc['min_llcr'] and dc['min_llcr'] >= 1.40 else '⚠️ Breach'} |")
        lines.append("")

        lines.append("## 🔄 Working Capital & Cash Conversion Cycle (CCC)")
        lines.append("| Year | DSO (Days) | DIO (Days) | DPO (Days) | Net CCC (Days) |")
        lines.append("| :---: | :---: | :---: | :---: | :---: |")
        for cc in res["cash_conversion_cycle"]:
            lines.append(f"| {cc['year']} | {cc['dso']:.1f} | {cc['dio']:.1f} | {cc['dpo']:.1f} | **{cc['ccc_days']:.1f}** |")
        lines.append("")

        lines.append("## ⚖️ Break-Even Operating Threshold")
        lines.append(f"- **Break-Even Revenue:** {c} {be['break_even_sales']:,.2f}")
        lines.append(f"- **Break-Even Capacity Utilization:** **{be['break_even_capacity_utilization']:.1%}**")
        lines.append(f"- **Contribution Margin Ratio:** {be['contribution_margin_ratio']:.1%}")
        lines.append("")

        if res["warnings"]:
            lines.append("## ⚠️ Project Risk & Covenant Warnings")
            for w in res["warnings"]:
                lines.append(f"- ⚠️ {w}")
            lines.append("")

        return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="Commercial Project & Feasibility Engine")
    parser.add_argument("--input", "-i", type=str, required=True, help="Input JSON file")
    parser.add_argument("--output", "-o", type=str, default=None, help="Output JSON file")
    parser.add_argument("--report", "-r", type=str, default=None, help="Output Markdown report")
    parser.add_argument("--format", "-f", choices=["json", "markdown"], default="markdown")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    engine = CommercialProjectEngine(data)
    results = engine.evaluate()

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

    report_md = engine.generate_markdown_report(results)
    if args.report:
        with open(args.report, "w", encoding="utf-8") as f:
            f.write(report_md)

    if args.format == "json":
        print(json.dumps(results, indent=2))
    else:
        print(report_md)

if __name__ == "__main__":
    main()

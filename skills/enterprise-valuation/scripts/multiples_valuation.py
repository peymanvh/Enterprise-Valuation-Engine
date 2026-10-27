#!/usr/bin/env python3
"""
multiples_valuation.py - Trading & Transaction Multiples Valuation Engine
Harmonized Peer Group Analysis, Harmonic Mean Averaging (McKinsey Standard),
and Linear Value-Driver Regression.
"""

import sys
import json
import math
import argparse
from typing import Dict, List, Any, Optional

def harmonic_mean(values: List[float]) -> float:
    """
    Harmonic mean: n / sum(1/x).
    McKinsey Ch. 14 recommends Harmonic Mean for valuation multiples (P/E, EV/EBITDA)
    to prevent upward statistical distortion caused by small denominators.
    """
    valid = [v for v in values if v > 0]
    if not valid:
        return 0.0
    return len(valid) / sum(1.0 / v for v in valid)

def median(values: List[float]) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    n = len(s)
    mid = n // 2
    if n % 2 == 1:
        return s[mid]
    else:
        return (s[mid - 1] + s[mid]) / 2.0

def linear_regression(x: List[float], y: List[float]):
    """
    Computes slope, intercept, and R-squared for single variable OLS.
    """
    n = len(x)
    if n < 2 or len(y) != n:
        return None
    sum_x = sum(x)
    sum_y = sum(y)
    sum_x2 = sum(xi * xi for xi in x)
    sum_xy = sum(xi * yi for xi, yi in zip(x, y))
    
    denominator = (n * sum_x2 - sum_x * sum_x)
    if abs(denominator) < 1e-12:
        return None
    
    slope = (n * sum_xy - sum_x * sum_y) / denominator
    intercept = (sum_y - slope * sum_x) / n
    
    # R-squared
    mean_y = sum_y / n
    ss_tot = sum((yi - mean_y) ** 2 for yi in y)
    ss_res = sum((yi - (intercept + slope * xi)) ** 2 for xi, yi in zip(x, y))
    r_squared = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
    
    return {"slope": slope, "intercept": intercept, "r_squared": r_squared}

class MultiplesValuationEngine:
    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.company_name = data.get("company_name", "Target Company")
        self.currency = data.get("currency", "USD")
        self.target_metrics = data.get("target_metrics", {})
        self.peer_group = data.get("peers", [])
        self.bridge = data.get("balance_sheet_bridge", {})
        self.shares_outstanding = float(self.bridge.get("shares_outstanding", 1.0))
        self.net_debt = (
            float(self.bridge.get("total_debt", 0.0)) +
            float(self.bridge.get("operating_lease_liabilities", 0.0)) +
            float(self.bridge.get("pension_deficits", 0.0)) +
            float(self.bridge.get("minority_interests", 0.0)) -
            float(self.bridge.get("cash_and_marketable_securities", 0.0)) -
            float(self.bridge.get("non_operating_assets", 0.0))
        )

    def analyze(self) -> Dict[str, Any]:
        multiple_keys = ["ev_to_ebitda", "ev_to_ebit", "ev_to_sales", "p_to_e", "p_to_b", "peg_ratio"]
        summary_stats: Dict[str, Dict[str, float]] = {}
        
        for m in multiple_keys:
            raw_vals = [p[m] for p in self.peer_group if m in p and p[m] is not None and p[m] > 0]
            if not raw_vals:
                continue
            mean_val = sum(raw_vals) / len(raw_vals)
            med_val = median(raw_vals)
            harm_val = harmonic_mean(raw_vals)
            summary_stats[m] = {
                "mean": mean_val,
                "median": med_val,
                "harmonic_mean": harm_val,
                "min": min(raw_vals),
                "max": max(raw_vals),
                "count": len(raw_vals)
            }

        # Value target based on Harmonic Mean (primary) and Median (secondary)
        valuations = {}
        # 1. EV / EBITDA
        if "ev_to_ebitda" in summary_stats and "ebitda" in self.target_metrics:
            ebitda = float(self.target_metrics["ebitda"])
            mult = summary_stats["ev_to_ebitda"]["harmonic_mean"]
            implied_ev = ebitda * mult
            implied_equity = implied_ev - self.net_debt
            valuations["ev_to_ebitda"] = {
                "multiple_used": mult,
                "target_metric": ebitda,
                "implied_ev": implied_ev,
                "implied_equity": implied_equity,
                "implied_share_price": implied_equity / max(self.shares_outstanding, 0.001)
            }

        # 2. EV / EBIT
        if "ev_to_ebit" in summary_stats and "ebit" in self.target_metrics:
            ebit = float(self.target_metrics["ebit"])
            mult = summary_stats["ev_to_ebit"]["harmonic_mean"]
            implied_ev = ebit * mult
            implied_equity = implied_ev - self.net_debt
            valuations["ev_to_ebit"] = {
                "multiple_used": mult,
                "target_metric": ebit,
                "implied_ev": implied_ev,
                "implied_equity": implied_equity,
                "implied_share_price": implied_equity / max(self.shares_outstanding, 0.001)
            }

        # 3. EV / Sales
        if "ev_to_sales" in summary_stats and "sales" in self.target_metrics:
            sales = float(self.target_metrics["sales"])
            mult = summary_stats["ev_to_sales"]["harmonic_mean"]
            implied_ev = sales * mult
            implied_equity = implied_ev - self.net_debt
            valuations["ev_to_sales"] = {
                "multiple_used": mult,
                "target_metric": sales,
                "implied_ev": implied_ev,
                "implied_equity": implied_equity,
                "implied_share_price": implied_equity / max(self.shares_outstanding, 0.001)
            }

        # 4. P / E
        if "p_to_e" in summary_stats and "net_income" in self.target_metrics:
            net_income = float(self.target_metrics["net_income"])
            mult = summary_stats["p_to_e"]["harmonic_mean"]
            implied_equity = net_income * mult
            implied_ev = implied_equity + self.net_debt
            valuations["p_to_e"] = {
                "multiple_used": mult,
                "target_metric": net_income,
                "implied_ev": implied_ev,
                "implied_equity": implied_equity,
                "implied_share_price": implied_equity / max(self.shares_outstanding, 0.001)
            }

        # Regression: EV/EBITDA vs ROIC or Revenue Growth
        reg_data = []
        reg_x, reg_y = [], []
        for p in self.peer_group:
            if "ev_to_ebitda" in p and "roic" in p and p["ev_to_ebitda"] is not None and p["roic"] is not None:
                reg_x.append(float(p["roic"]))
                reg_y.append(float(p["ev_to_ebitda"]))
        regression_result = linear_regression(reg_x, reg_y) if len(reg_x) >= 3 else None

        # Harmonized blended valuation (weighted average of available EV multiples)
        weights = {"ev_to_ebitda": 0.40, "ev_to_ebit": 0.35, "ev_to_sales": 0.10, "p_to_e": 0.15}
        total_w = 0.0
        blended_equity = 0.0
        for k, v in valuations.items():
            if k in weights:
                w = weights[k]
                blended_equity += v["implied_equity"] * w
                total_w += w
        if total_w > 0:
            blended_equity /= total_w
        else:
            blended_equity = 0.0

        return {
            "company_name": self.company_name,
            "currency": self.currency,
            "summary_multiples": summary_stats,
            "valuations_by_multiple": valuations,
            "blended_equity_value": blended_equity,
            "blended_share_price": blended_equity / max(self.shares_outstanding, 0.001),
            "net_debt": self.net_debt,
            "shares_outstanding": self.shares_outstanding,
            "regression_ev_ebitda_vs_roic": regression_result
        }

    def generate_markdown_report(self, res: Dict[str, Any]) -> str:
        lines = []
        c = res["currency"]
        lines.append(f"# 📊 Comparable Company Analysis: {res['company_name']}")
        lines.append(f"**Methodology:** McKinsey-standard Harmonic Mean Ratios & Peer Group Regression")
        lines.append("")

        lines.append("## 📌 Summary Valuation Outcomes")
        lines.append(f"| Valuation Multiple | Harmonic Mean | Target Metric | Implied EV ({c}) | Implied Equity ({c}) | Share Price ({c}) |")
        lines.append("| :--- | :---: | :---: | :---: | :---: | :---: |")
        for k, v in res["valuations_by_multiple"].items():
            lines.append(
                f"| **{k.upper()}** | {v['multiple_used']:.2f}x | {v['target_metric']:,.1f} | "
                f"{v['implied_ev']:,.2f} | {v['implied_equity']:,.2f} | **{v['implied_share_price']:,.2f}** |"
            )
        lines.append(f"| **BLENDED BENCHMARK** | — | — | — | **{res['blended_equity_value']:,.2f}** | **{res['blended_share_price']:,.2f}** |")
        lines.append("")

        lines.append("## 📈 Peer Group Multiples Statistics")
        lines.append("| Metric | Harmonic Mean | Arithmetic Mean | Median | Min | Max | Sample Size |")
        lines.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: |")
        for m, s in res["summary_multiples"].items():
            lines.append(
                f"| {m.upper()} | **{s['harmonic_mean']:.2f}x** | {s['mean']:.2f}x | {s['median']:.2f}x | "
                f"{s['min']:.2f}x | {s['max']:.2f}x | {s['count']} |"
            )
        lines.append("")

        reg = res.get("regression_ev_ebitda_vs_roic")
        if reg:
            lines.append("## 🔬 Value-Driver OLS Regression (EV/EBITDA vs. ROIC)")
            lines.append(f"- **Formula:** $\\text{{EV/EBITDA}} = {reg['intercept']:.2f} + {reg['slope']:.2f} \\times \\text{{ROIC}}$")
            lines.append(f"- **Goodness of Fit ($R^2$):** {reg['r_squared']:.2%}")
            lines.append("")

        return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="Trading Multiples & Peer Valuation Engine")
    parser.add_argument("--input", "-i", type=str, required=True, help="Input JSON file")
    parser.add_argument("--output", "-o", type=str, default=None, help="Output JSON path")
    parser.add_argument("--report", "-r", type=str, default=None, help="Output Markdown report path")
    parser.add_argument("--format", "-f", choices=["json", "markdown"], default="markdown")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    engine = MultiplesValuationEngine(data)
    results = engine.analyze()

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

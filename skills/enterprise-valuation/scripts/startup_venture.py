#!/usr/bin/env python3
"""
startup_venture.py - Early-Stage Venture & High-Growth Startup Valuation Engine
Venture Capital (VC) Method, Scorecard Method (Payne), Berkus Method,
First Chicago Method, and SaaS Unit Economics Diagnostics.
"""

import sys
import json
import math
import argparse
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

class StartupVentureEngine:
    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.startup_name = data.get("startup_name", "Venture Target")
        self.currency = data.get("currency", "USD")
        self.audit_alerts: List[str] = []

    def run_vc_method(self) -> Dict[str, Any]:
        vc_data = self.data.get("vc_method", {})
        if not vc_data:
            return {}

        investment_amount = float(vc_data.get("investment_amount", 1_000_000))
        horizon_years = float(vc_data.get("horizon_years", 5))
        target_irr = float(vc_data.get("target_irr", 0.40))  # 40% target IRR
        target_moic = float(vc_data.get("target_moic", 0.0))
        if target_moic <= 0:
            target_moic = math.pow(1.0 + target_irr, horizon_years)

        # Terminal Value determination
        exit_val = float(vc_data.get("terminal_exit_value", 0.0))
        if exit_val <= 0:
            exit_revenue = float(vc_data.get("terminal_revenue", 0.0))
            exit_multiple = float(vc_data.get("terminal_revenue_multiple", 5.0))
            exit_val = exit_revenue * exit_multiple

        # Future dilution modeling
        future_dilution_rounds = vc_data.get("future_dilution_rounds", [0.20, 0.15])  # e.g., Series B 20%, Series C 15%
        retention_rate = 1.0
        for d in future_dilution_rounds:
            retention_rate *= (1.0 - float(d))

        # Required final ownership at exit
        # Target MOIC = (Exit Ownership * Exit Value) / Investment
        # Exit Ownership = Investment * Target MOIC / Exit Value
        if exit_val <= 0:
            return {"error": "Exit value must be positive to run VC Method"}

        required_exit_ownership = (investment_amount * target_moic) / exit_val
        # Required current ownership adjusted for dilution: Current = Exit / Retention
        required_current_ownership = required_exit_ownership / retention_rate if retention_rate > 0 else 1.0

        if required_current_ownership > 1.0:
            self.audit_alerts.append(
                f"VC Method: Required current ownership ({required_current_ownership:.1%}) exceeds 100%! "
                "The targeted MOIC is mathematically impossible given the exit valuation and dilution assumptions."
            )

        post_money_val = investment_amount / required_current_ownership if required_current_ownership > 0 else 0.0
        pre_money_val = post_money_val - investment_amount

        return {
            "investment_amount": investment_amount,
            "horizon_years": horizon_years,
            "target_irr": target_irr,
            "target_moic": target_moic,
            "terminal_exit_value": exit_val,
            "retention_rate": retention_rate,
            "required_current_ownership": required_current_ownership,
            "required_exit_ownership": required_exit_ownership,
            "post_money_valuation": post_money_val,
            "pre_money_valuation": pre_money_val
        }

    def run_scorecard_method(self) -> Dict[str, Any]:
        sc_data = self.data.get("scorecard_method", {})
        if not sc_data:
            return {}

        benchmark_pre_money = float(sc_data.get("benchmark_pre_money", 3_000_000))
        factors = sc_data.get("factors", {
            "management_team": {"weight": 0.30, "score": 1.20},
            "size_of_opportunity": {"weight": 0.25, "score": 1.10},
            "product_technology": {"weight": 0.15, "score": 1.00},
            "competitive_environment": {"weight": 0.10, "score": 0.90},
            "marketing_sales_partnerships": {"weight": 0.10, "score": 1.00},
            "need_for_additional_investment": {"weight": 0.05, "score": 1.00},
            "other": {"weight": 0.05, "score": 1.00}
        })

        weighted_factor_sum = 0.0
        factor_breakdown = []
        for k, v in factors.items():
            w = float(v.get("weight", 0.0))
            s = float(v.get("score", 1.0))
            contrib = w * s
            weighted_factor_sum += contrib
            factor_breakdown.append({
                "criterion": k,
                "weight": w,
                "score": s,
                "weighted_contribution": contrib
            })

        implied_pre_money = benchmark_pre_money * weighted_factor_sum
        return {
            "benchmark_pre_money": benchmark_pre_money,
            "composite_multiplier": weighted_factor_sum,
            "implied_pre_money_valuation": implied_pre_money,
            "factor_breakdown": factor_breakdown
        }

    def run_berkus_method(self) -> Dict[str, Any]:
        b_data = self.data.get("berkus_method", {})
        if not b_data:
            return {}

        categories = {
            "sound_idea": float(b_data.get("sound_idea", 500_000)),
            "prototype": float(b_data.get("prototype", 500_000)),
            "quality_management_team": float(b_data.get("quality_management_team", 500_000)),
            "strategic_relationships": float(b_data.get("strategic_relationships", 250_000)),
            "product_rollout_or_sales": float(b_data.get("product_rollout_or_sales", 250_000))
        }
        implied_pre_money = sum(categories.values())
        return {
            "breakdown": categories,
            "implied_pre_money_valuation": implied_pre_money
        }

    def run_first_chicago_method(self) -> Dict[str, Any]:
        fc_data = self.data.get("first_chicago_method", {})
        if not fc_data:
            return {}

        scenarios = fc_data.get("scenarios", [
            {"name": "Bull / Success", "probability": 0.20, "valuation": 25_000_000},
            {"name": "Base / Normal", "probability": 0.50, "valuation": 8_000_000},
            {"name": "Bear / Failure", "probability": 0.30, "valuation": 500_000}
        ])

        total_prob = sum(float(s["probability"]) for s in scenarios)
        if abs(total_prob - 1.0) > 1e-4 and total_prob > 0:
            for s in scenarios:
                s["probability"] = float(s["probability"]) / total_prob

        weighted_valuation = sum(float(s["probability"]) * float(s["valuation"]) for s in scenarios)

        return {
            "scenarios": scenarios,
            "probability_weighted_valuation": weighted_valuation
        }

    def analyze_saas_metrics(self) -> Dict[str, Any]:
        s = self.data.get("saas_metrics", {})
        if not s:
            return {}

        mrr = float(s.get("mrr", 0.0))
        arr = float(s.get("arr", mrr * 12.0))
        arpu_annual = float(s.get("arpu_annual", 1200.0))
        gross_margin = float(s.get("gross_margin", 0.80))
        annual_churn_rate = float(s.get("annual_churn_rate", 0.08))
        cac = float(s.get("cac", 2000.0))
        nrr = float(s.get("net_revenue_retention", 1.15))
        yoy_growth_rate = float(s.get("yoy_growth_rate", 0.50))
        fcf_margin = float(s.get("fcf_margin", -0.10))
        quarterly_arr_delta = float(s.get("quarterly_arr_delta", 50_000))
        prev_quarter_sm_spend = float(s.get("prev_quarter_sm_spend", 60_000))

        # LTV = (ARPU * Gross Margin) / Churn
        ltv = (arpu_annual * gross_margin) / annual_churn_rate if annual_churn_rate > 0 else 0.0
        ltv_to_cac = ltv / cac if cac > 0 else 0.0

        # CAC Payback in Months: CAC / (Monthly ARPU * Gross Margin)
        monthly_arpu_gp = (arpu_annual / 12.0) * gross_margin
        cac_payback_months = (cac / monthly_arpu_gp) if monthly_arpu_gp > 0 else 0.0

        # Rule of 40: Growth Rate % + FCF Margin %
        rule_of_40_score = (yoy_growth_rate + fcf_margin) * 100.0

        # Magic Number: (Quarterly ARR Delta * 4) / Prev Quarter S&M
        magic_number = (quarterly_arr_delta * 4.0) / prev_quarter_sm_spend if prev_quarter_sm_spend > 0 else 0.0

        # Benchmarks & Audits
        if ltv_to_cac < 3.0:
            self.audit_alerts.append(f"SaaS Health: LTV/CAC ({ltv_to_cac:.2f}x) is below the institutional benchmark of 3.0x.")
        if cac_payback_months > 12.0:
            self.audit_alerts.append(f"SaaS Health: CAC Payback ({cac_payback_months:.1f} months) exceeds the healthy target of 12 months.")
        if nrr < 1.0:
            self.audit_alerts.append(f"SaaS Health: Net Revenue Retention ({nrr:.1%}) is < 100%, indicating net contraction in customer accounts.")
        if rule_of_40_score < 40.0:
            self.audit_alerts.append(f"SaaS Health: Rule of 40 score ({rule_of_40_score:.1f}%) is below 40.0%.")

        return {
            "arr": arr,
            "mrr": mrr,
            "gross_margin": gross_margin,
            "annual_churn_rate": annual_churn_rate,
            "cac": cac,
            "ltv": ltv,
            "ltv_to_cac_ratio": ltv_to_cac,
            "cac_payback_months": cac_payback_months,
            "net_revenue_retention": nrr,
            "rule_of_40_score": rule_of_40_score,
            "magic_number": magic_number
        }

    def evaluate_all(self) -> Dict[str, Any]:
        vc_res = self.run_vc_method()
        sc_res = self.run_scorecard_method()
        bk_res = self.run_berkus_method()
        fc_res = self.run_first_chicago_method()
        saas_res = self.analyze_saas_metrics()

        # Synthesis of Pre-Money Valuations across available angel/venture methods
        pre_money_estimates = []
        if "pre_money_valuation" in vc_res:
            pre_money_estimates.append({"method": "VC Method", "pre_money": vc_res["pre_money_valuation"]})
        if "implied_pre_money_valuation" in sc_res:
            pre_money_estimates.append({"method": "Scorecard Method", "pre_money": sc_res["implied_pre_money_valuation"]})
        if "implied_pre_money_valuation" in bk_res:
            pre_money_estimates.append({"method": "Berkus Method", "pre_money": bk_res["implied_pre_money_valuation"]})
        if "probability_weighted_valuation" in fc_res:
            pre_money_estimates.append({"method": "First Chicago Method", "pre_money": fc_res["probability_weighted_valuation"]})

        avg_pre_money = (sum(e["pre_money"] for e in pre_money_estimates) / len(pre_money_estimates)) if pre_money_estimates else 0.0

        return {
            "startup_name": self.startup_name,
            "currency": self.currency,
            "vc_method": vc_res,
            "scorecard_method": sc_res,
            "berkus_method": bk_res,
            "first_chicago_method": fc_res,
            "saas_unit_economics": saas_res,
            "pre_money_summary": pre_money_estimates,
            "consensus_pre_money_valuation": avg_pre_money,
            "audit_alerts": self.audit_alerts
        }

    def generate_markdown_report(self, res: Dict[str, Any]) -> str:
        lines = []
        c = res["currency"]
        lines.append(f"# 🚀 Startup & Venture Valuation Report: {res['startup_name']}")
        lines.append("**Methodologies:** VC Method, Bill Payne Scorecard, Berkus Model, First Chicago & SaaS Unit Economics")
        lines.append("")

        lines.append("## 📌 Multi-Method Pre-Money Valuation Synthesis")
        lines.append(f"| Valuation Framework | Implied Pre-Money ({c}) | Key Mechanism |")
        lines.append("| :--- | :---: | :--- |")
        for e in res["pre_money_summary"]:
            lines.append(f"| **{e['method']}** | **{c} {e['pre_money']:,.2f}** | Model-specific formulation |")
        lines.append(f"| **CONSENSUS PRE-MONEY** | **{c} {res['consensus_pre_money_valuation']:,.2f}** | Arithmetic average of active methods |")
        lines.append("")

        # VC Method Details
        vc = res.get("vc_method", {})
        if vc and "post_money_valuation" in vc:
            lines.append("## 💼 Venture Capital (VC) Method Dynamics")
            lines.append(f"- **Investment Requested:** {c} {vc['investment_amount']:,.2f}")
            lines.append(f"- **Target MOIC:** {vc['target_moic']:.2f}x ({vc['target_irr']:.1%} IRR over {vc['horizon_years']:.0f} years)")
            lines.append(f"- **Exit Terminal Valuation:** {c} {vc['terminal_exit_value']:,.2f}")
            lines.append(f"- **Dilution Retention Rate:** {vc['retention_rate']:.1%}")
            lines.append(f"- **Required Ownership Today:** **{vc['required_current_ownership']:.2%}**")
            lines.append(f"- **Implied Post-Money:** **{c} {vc['post_money_valuation']:,.2f}**")
            lines.append(f"- **Implied Pre-Money:** **{c} {vc['pre_money_valuation']:,.2f}**")
            lines.append("")

        # SaaS Unit Economics
        s = res.get("saas_unit_economics", {})
        if s:
            lines.append("## ⚙️ SaaS Unit Economics Diagnostic")
            lines.append("| Metric | Result | Benchmark | Status |")
            lines.append("| :--- | :---: | :---: | :---: |")
            lines.append(f"| **ARR** | {c} {s['arr']:,.0f} | — | — |")
            lines.append(f"| **LTV / CAC** | **{s['ltv_to_cac_ratio']:.2f}x** | $\\ge 3.0x$ | {'✅ Pass' if s['ltv_to_cac_ratio'] >= 3.0 else '⚠️ Warning'} |")
            lines.append(f"| **CAC Payback Period** | **{s['cac_payback_months']:.1f} mos** | $< 12.0$ mos | {'✅ Pass' if s['cac_payback_months'] <= 12.0 else '⚠️ Warning'} |")
            lines.append(f"| **Net Revenue Retention (NRR)** | **{s['net_revenue_retention']:.1%}** | $> 110.0\\%$ | {'✅ Strong' if s['net_revenue_retention'] >= 1.10 else ('🟡 Adequate' if s['net_revenue_retention'] >= 1.0 else '🚨 Contraction')} |")
            lines.append(f"| **Rule of 40 Score** | **{s['rule_of_40_score']:.1f}%** | $\\ge 40.0\\%$ | {'✅ Pass' if s['rule_of_40_score'] >= 40.0 else '⚠️ Warning'} |")
            lines.append(f"| **Magic Number** | **{s['magic_number']:.2f}** | $> 0.75x$ | {'✅ Pass' if s['magic_number'] >= 0.75 else '🟡 Low Efficiency'} |")
            lines.append("")

        if res["audit_alerts"]:
            lines.append("## ⚠️ Venture Governance Alerts")
            for alert in res["audit_alerts"]:
                lines.append(f"- ⚠️ **Alert:** {alert}")
            lines.append("")

        return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="Startup & Venture Valuation Engine")
    parser.add_argument("--input", "-i", type=str, required=True, help="Input JSON path")
    parser.add_argument("--output", "-o", type=str, default=None, help="Output JSON path")
    parser.add_argument("--report", "-r", type=str, default=None, help="Output Markdown report path")
    parser.add_argument("--format", "-f", choices=["json", "markdown"], default="markdown")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    engine = StartupVentureEngine(data)
    results = engine.evaluate_all()

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

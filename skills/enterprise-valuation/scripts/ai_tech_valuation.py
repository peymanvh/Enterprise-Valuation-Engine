#!/usr/bin/env python3
"""
ai_tech_valuation.py - McKinsey 8th Edition (2025) AI, Digital Assets & Macro Rate Regime Engine
Features:
- Generative AI Unit Economics: Token pricing, Inference COGS, GPU cluster Capex & 3-year accelerated obsolescence.
- Training Compute Capitalization vs Expensing audit.
- High Interest Rate Macro Regime & Debt Rollover / Refinancing Cliff Stress Test.
"""

import sys
import json
import math
import argparse
from typing import Dict, List, Any, Optional

class AITechValuationEngine:
    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.company_name = data.get("company_name", "AI Enterprise Target")
        self.currency = data.get("currency", "USD")
        self.ai_metrics = data.get("ai_unit_economics", {})
        self.compute_capex_data = data.get("compute_and_gpu_capex", {})
        self.debt_rollover_data = data.get("debt_rollover_stress_test", {})
        self.warnings: List[str] = []

    def evaluate_ai_unit_economics(self) -> Dict[str, Any]:
        if not self.ai_metrics:
            return {}

        monthly_active_users = float(self.ai_metrics.get("monthly_active_users", 500_000))
        queries_per_user_month = float(self.ai_metrics.get("queries_per_user_month", 60))
        avg_tokens_per_query = float(self.ai_metrics.get("avg_tokens_per_query", 1_500))  # Input + Output
        
        # Pricing and Costs per Million Tokens
        price_per_million_tokens = float(self.ai_metrics.get("revenue_per_million_tokens", 8.0))  # USD 8.00 / M tokens
        inference_cost_per_million_tokens = float(self.ai_metrics.get("inference_cost_per_million_tokens", 3.20)) # GPU compute & electricity

        total_monthly_queries = monthly_active_users * queries_per_user_month
        total_monthly_tokens_m = (total_monthly_queries * avg_tokens_per_query) / 1_000_000.0

        monthly_ai_revenue = total_monthly_tokens_m * price_per_million_tokens
        monthly_inference_cogs = total_monthly_tokens_m * inference_cost_per_million_tokens
        monthly_gross_profit = monthly_ai_revenue - monthly_inference_cogs

        annual_ai_arr = monthly_ai_revenue * 12.0
        annual_inference_cogs = monthly_inference_cogs * 12.0
        annual_gross_profit = monthly_gross_profit * 12.0
        token_gross_margin = (monthly_gross_profit / monthly_ai_revenue) if monthly_ai_revenue > 0 else 0.0

        # GPU Utilization & Efficiency
        gpu_utilization_rate = float(self.ai_metrics.get("gpu_utilization_rate", 0.65)) # 65% active duty cycle
        if gpu_utilization_rate < 0.60:
            self.warnings.append(
                f"Low GPU Cluster Utilization ({gpu_utilization_rate:.1%}): Idle cluster capacity severely erodes Return on Invested Capital (ROIC)."
            )
        if token_gross_margin < 0.50:
            self.warnings.append(
                f"Thin AI Token Gross Margin ({token_gross_margin:.1%}): Unlike traditional 80% SaaS gross margins, "
                "heavy inference compute costs commoditize margin structure per McKinsey 8th Ed."
            )

        return {
            "total_monthly_tokens_million": total_monthly_tokens_m,
            "annual_ai_revenue": annual_ai_arr,
            "annual_inference_cogs": annual_inference_cogs,
            "annual_gross_profit": annual_gross_profit,
            "token_gross_margin": token_gross_margin,
            "gpu_utilization_rate": gpu_utilization_rate
        }

    def evaluate_compute_and_gpu_depreciation(self) -> Dict[str, Any]:
        """
        McKinsey 8th Ed:
        GPU clusters (H100, B200) face accelerated technological obsolescence (3-year economic life),
        contrasted with legacy enterprise data centers (5-7 years).
        """
        if not self.compute_capex_data:
            return {}

        annual_gpu_capex = float(self.compute_capex_data.get("annual_gpu_capex", 25_000_000))
        gpu_economic_life_years = float(self.compute_capex_data.get("gpu_economic_life_years", 3.0)) # 3 years
        traditional_server_life = float(self.compute_capex_data.get("traditional_server_life_years", 5.0))

        # Accelerated depreciation per year
        gpu_depreciation_annual = annual_gpu_capex / gpu_economic_life_years
        traditional_depreciation_annual = annual_gpu_capex / traditional_server_life
        ebit_drag = gpu_depreciation_annual - traditional_depreciation_annual

        training_run_capex = float(self.compute_capex_data.get("model_training_run_capex", 15_000_000))
        training_accounting_treatment = str(self.compute_capex_data.get("training_accounting_treatment", "capitalize")).lower()

        return {
            "annual_gpu_capex": annual_gpu_capex,
            "gpu_economic_life_years": gpu_economic_life_years,
            "annual_gpu_depreciation": gpu_depreciation_annual,
            "traditional_server_depreciation": traditional_depreciation_annual,
            "annual_ebit_depreciation_drag": ebit_drag,
            "training_run_cost": training_run_capex,
            "training_accounting_treatment": training_accounting_treatment
        }

    def evaluate_debt_rollover_cliff(self) -> Dict[str, Any]:
        """
        McKinsey 8th Ed (Higher Cost of Capital Regime):
        Stress tests debt issued during the ZIRP (Zero Interest Rate Policy) era (2-3.5%)
        refinancing at current institutional yields (6.5-8.5%).
        """
        if not self.debt_rollover_data:
            return {}

        total_debt = float(self.debt_rollover_data.get("total_debt", 150_000_000))
        debt_maturing_next_2_years = float(self.debt_rollover_data.get("debt_maturing_next_2_years", 90_000_000))
        current_historical_interest_rate = float(self.debt_rollover_data.get("historical_interest_rate", 0.035)) # 3.5%
        new_refinancing_interest_rate = float(self.debt_rollover_data.get("new_refinancing_interest_rate", 0.075)) # 7.5%
        ebit_available = float(self.debt_rollover_data.get("annual_ebit", 25_000_000))

        # Current annual interest
        current_interest_expense = total_debt * current_historical_interest_rate
        current_icr = ebit_available / current_interest_expense if current_interest_expense > 0 else 999.0

        # Post-rollover annual interest
        unmatured_debt = total_debt - debt_maturing_next_2_years
        new_interest_expense = (unmatured_debt * current_historical_interest_rate) + (debt_maturing_next_2_years * new_refinancing_interest_rate)
        post_rollover_icr = ebit_available / new_interest_expense if new_interest_expense > 0 else 999.0
        incremental_cash_interest = new_interest_expense - current_interest_expense

        if post_rollover_icr < 2.50:
            self.warnings.append(
                f"🚨 DEBT ROLLOVER CLIFF: Post-refinancing Interest Coverage Ratio drops to {post_rollover_icr:.2f}x "
                f"(Annual interest increases by {self.currency} {incremental_cash_interest:,.2f}). "
                "Company risks credit downgrade or covenant default under higher rate macro regime."
            )

        return {
            "total_debt": total_debt,
            "maturing_debt_volume": debt_maturing_next_2_years,
            "historical_interest_rate": current_historical_interest_rate,
            "new_refinancing_rate": new_refinancing_interest_rate,
            "current_annual_interest": current_interest_expense,
            "current_interest_coverage_ratio": current_icr,
            "post_rollover_annual_interest": new_interest_expense,
            "post_rollover_interest_coverage_ratio": post_rollover_icr,
            "incremental_annual_cash_drain": incremental_cash_interest
        }

    def evaluate_all(self) -> Dict[str, Any]:
        ai_res = self.evaluate_ai_unit_economics()
        compute_res = self.evaluate_compute_and_gpu_depreciation()
        rollover_res = self.evaluate_debt_rollover_cliff()

        return {
            "company_name": self.company_name,
            "currency": self.currency,
            "ai_unit_economics": ai_res,
            "compute_and_gpu_depreciation": compute_res,
            "debt_rollover_stress_test": rollover_res,
            "warnings": self.warnings
        }

    def generate_markdown_report(self, res: Dict[str, Any]) -> str:
        lines = []
        c = res["currency"]
        ai = res.get("ai_unit_economics", {})
        comp = res.get("compute_and_gpu_depreciation", {})
        roll = res.get("debt_rollover_stress_test", {})

        lines.append(f"# 🤖 AI Asset Valuation & Macro High-Interest Rate Diagnostic")
        lines.append(f"**Enterprise:** {res['company_name']}")
        lines.append("**Standards:** McKinsey 8th Edition (May 2025) — AI Compute Economics & High-Rate Refinancing Cliffs")
        lines.append("")

        if ai:
            lines.append("## ⚡ Generative AI Token Economics & Margin Structure")
            lines.append("| Metric | Value | Reference / Benchmark |")
            lines.append("| :--- | :---: | :--- |")
            lines.append(f"| **Annual AI Token Revenue (ARR)** | {c} {ai['annual_ai_revenue']:,.2f} | Based on {ai['total_monthly_tokens_million']:,.1f}M tokens/month |")
            lines.append(f"| **Inference Compute COGS** | {c} {ai['annual_inference_cogs']:,.2f} | GPU compute runtime expenses |")
            lines.append(f"| **Token Gross Margin** | **{ai['token_gross_margin']:.1%}** | {'✅ Healthy' if ai['token_gross_margin'] >= 0.65 else '⚠️ Squeezed by inference'} |")
            lines.append(f"| **GPU Cluster Utilization** | **{ai['gpu_utilization_rate']:.1%}** | Target $\\ge 75\\%$ for high ROIC |")
            lines.append("")

        if comp:
            lines.append("## 💻 GPU Cluster Capex & Accelerated 3-Year Obsolescence")
            lines.append(f"- **Annual GPU Capex:** {c} {comp['annual_gpu_capex']:,.2f}")
            lines.append(f"- **GPU Economic Life:** **{comp['gpu_economic_life_years']:.0f} years** (vs {comp['gpu_economic_life_years'] + 2:.0f} years legacy servers)")
            lines.append(f"- **Annual GPU Depreciation:** {c} {comp['annual_gpu_depreciation']:,.2f}")
            lines.append(f"- **Incremental EBIT Drag:** **{c} {comp['annual_ebit_depreciation_drag']:,.2f}** per year")
            lines.append("")

        if roll:
            lines.append("## 📉 Macro Debt Rollover & Refinancing Stress Test")
            lines.append("| Metric | Current / ZIRP Regime | Post-Rollover High-Rate Regime | Delta / Impact |")
            lines.append("| :--- | :---: | :---: | :---: |")
            lines.append(f"| **Weighted Borrowing Rate** | {roll['historical_interest_rate']:.2%} | **{roll['new_refinancing_rate']:.2%}** | +{(roll['new_refinancing_rate'] - roll['historical_interest_rate']) * 10000:.0f} bps |")
            lines.append(f"| **Annual Cash Interest** | {c} {roll['current_annual_interest']:,.2f} | **{c} {roll['post_rollover_annual_interest']:,.2f}** | +{c} {roll['incremental_annual_cash_drain']:,.2f} |")
            lines.append(f"| **Interest Coverage Ratio (ICR)** | **{roll['current_interest_coverage_ratio']:.2f}x** | **{roll['post_rollover_interest_coverage_ratio']:.2f}x** | {'🚨 Severe Strain' if roll['post_rollover_interest_coverage_ratio'] < 2.5 else '🟡 Adequate'} |")
            lines.append("")

        if res["warnings"]:
            lines.append("## ⚠️ 8th Edition Governance Alerts")
            for w in res["warnings"]:
                lines.append(f"- {w}")
            lines.append("")

        return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="AI Valuation & Macro High-Interest Rate Engine")
    parser.add_argument("--input", "-i", type=str, required=True, help="Input JSON path")
    parser.add_argument("--output", "-o", type=str, default=None, help="Output JSON path")
    parser.add_argument("--report", "-r", type=str, default=None, help="Output Markdown report path")
    parser.add_argument("--format", "-f", choices=["json", "markdown"], default="markdown")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    engine = AITechValuationEngine(data)
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

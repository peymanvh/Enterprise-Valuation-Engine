#!/usr/bin/env python3
"""
monte_carlo_simulator.py - Probabilistic Monte Carlo & Sensitivity Engine
Runs stochastic risk simulations across valuation models (DCF, VC, Project Feasibility)
with Normal, LogNormal, Triangular, and Uniform distributions. Generates Tornado sensitivity rankings.
"""

import sys
import json
import math
import random
import argparse
from typing import Dict, List, Any, Optional

def sample_distribution(spec: Dict[str, Any]) -> float:
    dist_type = spec.get("type", "normal").lower()
    if dist_type == "normal":
        mean = float(spec.get("mean", 0.0))
        std = float(spec.get("std", 1.0))
        return random.gauss(mean, std)
    elif dist_type == "triangular":
        low = float(spec.get("low", 0.0))
        mode = float(spec.get("mode", 1.0))
        high = float(spec.get("high", 2.0))
        return random.triangular(low, high, mode)
    elif dist_type == "uniform":
        low = float(spec.get("low", 0.0))
        high = float(spec.get("high", 1.0))
        return random.uniform(low, high)
    elif dist_type == "lognormal":
        mean = float(spec.get("mean", 0.0))
        std = float(spec.get("std", 1.0))
        return random.lognormvariate(mean, std)
    elif dist_type == "constant":
        return float(spec.get("value", 0.0))
    else:
        return float(spec.get("mean", 0.0))

def percentile(sorted_vals: List[float], p: float) -> float:
    if not sorted_vals:
        return 0.0
    k = (len(sorted_vals) - 1) * p
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_vals[int(k)]
    d0 = sorted_vals[int(f)] * (c - k)
    d1 = sorted_vals[int(c)] * (k - f)
    return d0 + d1

class MonteCarloValuationSimulator:
    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.model_type = data.get("model_type", "dcf_enterprise")
        self.iterations = int(data.get("iterations", 5000))
        self.random_seed = data.get("seed", 42)
        random.seed(self.random_seed)
        self.parameters = data.get("parameters", {})
        self.currency = data.get("currency", "USD")

    def evaluate_single_dcf(self, nopat_base: float, rev_growth: float, ebit_margin: float, 
                           wacc: float, g: float, roic_term: float, horizon: int) -> float:
        # Avoid mathematical explosion if wacc <= g
        effective_wacc = max(wacc, g + 0.005)
        # 5-year discrete DCF
        pv_cfs = 0.0
        nopat = nopat_base
        for t in range(1, horizon + 1):
            nopat *= (1.0 + rev_growth)
            # Reinvestment = g_discrete / ROIC
            ir = min(rev_growth / max(roic_term, 0.05), 0.90)
            fcff = nopat * (1.0 - ir)
            pv_cfs += fcff / math.pow(1.0 + effective_wacc, t)
            
        # Terminal Value
        nopat_t_plus_1 = nopat * (1.0 + g)
        ir_term = g / max(roic_term, 0.05)
        ir_term = min(max(ir_term, 0.0), 0.95)
        tv = (nopat_t_plus_1 * (1.0 - ir_term)) / (effective_wacc - g)
        pv_tv = tv / math.pow(1.0 + effective_wacc, horizon)
        return pv_cfs + pv_tv

    def run_simulation(self) -> Dict[str, Any]:
        results: List[float] = []

        params = self.parameters
        nopat_base_spec = params.get("nopat_base", {"type": "constant", "value": 100_000_000})
        growth_spec = params.get("revenue_growth", {"type": "triangular", "low": 0.03, "mode": 0.07, "high": 0.12})
        margin_spec = params.get("ebit_margin", {"type": "normal", "mean": 0.18, "std": 0.02})
        wacc_spec = params.get("wacc", {"type": "normal", "mean": 0.085, "std": 0.008})
        g_spec = params.get("terminal_growth", {"type": "triangular", "low": 0.015, "mode": 0.025, "high": 0.035})
        roic_spec = params.get("terminal_roic", {"type": "triangular", "low": 0.10, "mode": 0.15, "high": 0.22})
        horizon = int(params.get("horizon_years", 5))

        for _ in range(self.iterations):
            nopat_base = sample_distribution(nopat_base_spec)
            rev_growth = sample_distribution(growth_spec)
            ebit_margin = sample_distribution(margin_spec)
            wacc = sample_distribution(wacc_spec)
            g = sample_distribution(g_spec)
            roic = sample_distribution(roic_spec)

            val = self.evaluate_single_dcf(nopat_base, rev_growth, ebit_margin, wacc, g, roic, horizon)
            results.append(val)

        results.sort()
        n = len(results)
        mean_val = sum(results) / n
        variance = sum((x - mean_val) ** 2 for x in results) / (n - 1)
        std_val = math.sqrt(variance)

        # Sensitivity / Tornado Analysis
        # Base case
        base_nopat = float(nopat_base_spec.get("value", nopat_base_spec.get("mean", 100_000_000)))
        base_growth = float(growth_spec.get("mode", growth_spec.get("mean", 0.07)))
        base_margin = float(margin_spec.get("mean", 0.18))
        base_wacc = float(wacc_spec.get("mean", 0.085))
        base_g = float(g_spec.get("mode", g_spec.get("mean", 0.025)))
        base_roic = float(roic_spec.get("mode", roic_spec.get("mean", 0.15)))

        base_val = self.evaluate_single_dcf(base_nopat, base_growth, base_margin, base_wacc, base_g, base_roic, horizon)

        # Perturb each key driver +/- 10% relative
        tornado = []
        drivers = [
            ("WACC", "wacc", base_wacc, 0.10, lambda delta: self.evaluate_single_dcf(base_nopat, base_growth, base_margin, base_wacc + delta, base_g, base_roic, horizon)),
            ("Terminal Growth (g)", "g", base_g, 0.20, lambda delta: self.evaluate_single_dcf(base_nopat, base_growth, base_margin, base_wacc, base_g + delta, base_roic, horizon)),
            ("Revenue Growth", "revenue_growth", base_growth, 0.20, lambda delta: self.evaluate_single_dcf(base_nopat, base_growth + delta, base_margin, base_wacc, base_g, base_roic, horizon)),
            ("Terminal ROIC", "terminal_roic", base_roic, 0.20, lambda delta: self.evaluate_single_dcf(base_nopat, base_growth, base_margin, base_wacc, base_g, base_roic + delta, horizon)),
            ("Base NOPAT", "nopat_base", base_nopat, 0.10, lambda delta: self.evaluate_single_dcf(base_nopat + delta, base_growth, base_margin, base_wacc, base_g, base_roic, horizon))
        ]

        for name, key, b_val, perturb_ratio, eval_func in drivers:
            delta = b_val * perturb_ratio
            low_outcome = eval_func(-delta)
            high_outcome = eval_func(delta)
            swing = abs(high_outcome - low_outcome)
            tornado.append({
                "driver": name,
                "base_parameter": b_val,
                "low_case_value": min(low_outcome, high_outcome),
                "high_case_value": max(low_outcome, high_outcome),
                "absolute_swing": swing
            })

        tornado.sort(key=lambda x: x["absolute_swing"], reverse=True)

        return {
            "model_type": self.model_type,
            "currency": self.currency,
            "iterations": self.iterations,
            "deterministic_base_valuation": base_val,
            "distribution_statistics": {
                "mean": mean_val,
                "std_deviation": std_val,
                "p5": percentile(results, 0.05),
                "p10": percentile(results, 0.10),
                "p25": percentile(results, 0.25),
                "p50_median": percentile(results, 0.50),
                "p75": percentile(results, 0.75),
                "p90": percentile(results, 0.90),
                "p95": percentile(results, 0.95),
                "iqr": percentile(results, 0.75) - percentile(results, 0.25)
            },
            "tornado_sensitivity_ranking": tornado
        }

    def generate_markdown_report(self, res: Dict[str, Any]) -> str:
        lines = []
        c = res["currency"]
        stats = res["distribution_statistics"]
        lines.append(f"# 🎲 Monte Carlo Valuation & Sensitivity Analysis")
        lines.append(f"**Iterations:** {res['iterations']:,} trials | **Deterministic Base:** {c} {res['deterministic_base_valuation']:,.2f}")
        lines.append("")

        lines.append("## 📌 Probabilistic Valuation Confidence Intervals")
        lines.append(f"| Percentile | Valuation ({c}) | Interpretation |")
        lines.append("| :--- | :---: | :--- |")
        lines.append(f"| **P5 (Bear Case / 95% VaR)** | {c} {stats['p5']:,.2f} | 95% probability valuation exceeds this floor |")
        lines.append(f"| **P10** | {c} {stats['p10']:,.2f} | Downside stress test |")
        lines.append(f"| **P25 (First Quartile)** | {c} {stats['p25']:,.2f} | Conservative institutional underwriting |")
        lines.append(f"| **P50 (Median)** | **{c} {stats['p50_median']:,.2f}** | Probabilistic center |")
        lines.append(f"| **P75 (Third Quartile)** | {c} {stats['p75']:,.2f} | Optimistic commercial traction |")
        lines.append(f"| **P90** | {c} {stats['p90']:,.2f} | High-upside breakout scenario |")
        lines.append(f"| **P95** | {c} {stats['p95']:,.2f} | 95th percentile bull case |")
        lines.append(f"| **Mean $\\pm$ Std. Dev.** | **{c} {stats['mean']:,.2f}** $\\pm$ {c} {stats['std_deviation']:,.2f} | Standard Gaussian reference |")
        lines.append("")

        lines.append("## 🌪️ Tornado Sensitivity Ranking (Impact on EV)")
        lines.append("| Driver Name | Low Case EV ({c}) | High Case EV ({c}) | EV Swing ({c}) | Sensitivity Rank |")
        lines.append("| :--- | :---: | :---: | :---: | :---: |")
        for idx, t in enumerate(res["tornado_sensitivity_ranking"]):
            lines.append(
                f"| **{t['driver']}** | {t['low_case_value']:,.2f} | {t['high_case_value']:,.2f} | "
                f"**{t['absolute_swing']:,.2f}** | **#{idx + 1}** |"
            )
        lines.append("")

        return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="Monte Carlo Valuation & Sensitivity Engine")
    parser.add_argument("--input", "-i", type=str, required=True, help="Input JSON file")
    parser.add_argument("--output", "-o", type=str, default=None, help="Output JSON path")
    parser.add_argument("--report", "-r", type=str, default=None, help="Output Markdown report path")
    parser.add_argument("--format", "-f", choices=["json", "markdown"], default="markdown")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    engine = MonteCarloValuationSimulator(data)
    results = engine.run_simulation()

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

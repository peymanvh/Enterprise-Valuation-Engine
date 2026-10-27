#!/usr/bin/env python3
"""
ip_patent_val.py - Intellectual Property, Patent & Technology Valuation Engine
Implements Relief-from-Royalty, Multi-Period Excess Earnings Method (MPEEM),
and Black-Scholes / Binomial Lattice Real Options Valuation for Patents & R&D.
"""

import sys
import json
import math
import argparse
from typing import Dict, List, Any, Optional

def norm_cdf(x: float) -> float:
    """Cumulative distribution function for standard normal distribution using math.erf."""
    return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0

def black_scholes_call(s: float, k: float, t: float, r: float, sigma: float) -> Dict[str, float]:
    """
    Black-Scholes European Call Option formula for Patent Valuation:
    S: Present Value of commercial cash flows upon launch
    K: Commercialization capital expenditure / exercise price
    T: Time to patent expiry or option decision horizon
    r: Risk-free rate
    sigma: Volatility of commercial cash flows
    """
    if t <= 0 or sigma <= 0 or s <= 0 or k <= 0:
        intrinsic = max(s - k, 0.0)
        return {"call_value": intrinsic, "d1": 0.0, "d2": 0.0, "intrinsic_value": intrinsic, "time_value": 0.0}

    d1 = (math.log(s / k) + (r + 0.5 * sigma * sigma) * t) / (sigma * math.sqrt(t))
    d2 = d1 - sigma * math.sqrt(t)

    call_val = (s * norm_cdf(d1)) - (k * math.exp(-r * t) * norm_cdf(d2))
    intrinsic = max(s - k, 0.0)
    time_val = max(call_val - intrinsic, 0.0)

    return {
        "call_value": call_val,
        "d1": d1,
        "d2": d2,
        "nd1": norm_cdf(d1),
        "nd2": norm_cdf(d2),
        "intrinsic_value": intrinsic,
        "time_value": time_val
    }

class IPPatentValuationEngine:
    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.patent_name = data.get("patent_name", "Technology Asset / Patent")
        self.currency = data.get("currency", "USD")
        self.tax_rate = float(data.get("tax_rate", 0.25))
        self.ip_discount_rate = float(data.get("ip_discount_rate", 0.14))  # Typically higher than WACC
        self.amortization_years = int(data.get("tax_amortization_years", 15))  # US IRS Sec 197 standard = 15 yrs

    def calculate_tab_factor(self, discount_rate: float, tax_rate: float, years: int) -> float:
        """
        Calculates the Tax Amortization Benefit (TAB) factor.
        TAB Factor = 1 / (1 - (PV of tax deductions over n years))
        """
        if years <= 0 or tax_rate <= 0:
            return 1.0
        # PV of an annuity factor for n years at discount rate
        pv_annuity = sum(1.0 / math.pow(1.0 + discount_rate, t) for t in range(1, years + 1))
        annual_deduction_pv = (tax_rate / years) * pv_annuity
        if annual_deduction_pv >= 1.0:
            return 1.0
        return 1.0 / (1.0 - annual_deduction_pv)

    def evaluate_relief_from_royalty(self) -> Dict[str, Any]:
        rfr = self.data.get("relief_from_royalty", {})
        if not rfr:
            return {}

        royalty_rate = float(rfr.get("royalty_rate", 0.05))  # e.g. 5% royalty
        revenues = rfr.get("projected_revenues", [])
        
        tab_factor = self.calculate_tab_factor(self.ip_discount_rate, self.tax_rate, self.amortization_years)

        schedule = []
        pv_royalty_savings_pre_tab = 0.0

        for idx, rev in enumerate(revenues):
            t = idx + 1
            rev_val = float(rev)
            pre_tax_royalty = rev_val * royalty_rate
            after_tax_royalty = pre_tax_royalty * (1.0 - self.tax_rate)
            disc_factor = 1.0 / math.pow(1.0 + self.ip_discount_rate, t)
            pv_royalty = after_tax_royalty * disc_factor
            pv_royalty_savings_pre_tab += pv_royalty

            schedule.append({
                "year": t,
                "projected_revenue": rev_val,
                "pre_tax_royalty": pre_tax_royalty,
                "after_tax_royalty": after_tax_royalty,
                "discount_factor": disc_factor,
                "pv_royalty_savings": pv_royalty
            })

        value_with_tab = pv_royalty_savings_pre_tab * tab_factor

        return {
            "royalty_rate": royalty_rate,
            "ip_discount_rate": self.ip_discount_rate,
            "tax_amortization_factor": tab_factor,
            "pv_royalty_savings_pre_tab": pv_royalty_savings_pre_tab,
            "patent_value_post_tab": value_with_tab,
            "schedule": schedule
        }

    def evaluate_mpeem(self) -> Dict[str, Any]:
        mpeem = self.data.get("mpeem", {})
        if not mpeem:
            return {}

        periods = mpeem.get("periods", [])
        cac_working_capital_rate = float(mpeem.get("cac_working_capital_rate", 0.06))
        cac_ppe_rate = float(mpeem.get("cac_ppe_rate", 0.09))
        cac_workforce_rate = float(mpeem.get("cac_workforce_rate", 0.12))

        tab_factor = self.calculate_tab_factor(self.ip_discount_rate, self.tax_rate, self.amortization_years)

        schedule = []
        pv_excess_earnings_pre_tab = 0.0

        for p in periods:
            t = int(p["year"])
            nopat = float(p.get("nopat", 0.0))
            wc = float(p.get("working_capital", 0.0))
            ppe = float(p.get("net_ppe", 0.0))
            workforce = float(p.get("assembled_workforce_value", 0.0))

            cac_wc = wc * cac_working_capital_rate
            cac_ppe = ppe * cac_ppe_rate
            cac_wf = workforce * cac_workforce_rate
            total_cac = cac_wc + cac_ppe + cac_wf

            excess_earnings = nopat - total_cac
            disc_factor = 1.0 / math.pow(1.0 + self.ip_discount_rate, t)
            pv_ee = excess_earnings * disc_factor
            pv_excess_earnings_pre_tab += pv_ee

            schedule.append({
                "year": t,
                "nopat": nopat,
                "cac_working_capital": cac_wc,
                "cac_ppe": cac_ppe,
                "cac_workforce": cac_wf,
                "total_cac": total_cac,
                "excess_earnings": excess_earnings,
                "pv_excess_earnings": pv_ee
            })

        value_with_tab = pv_excess_earnings_pre_tab * tab_factor

        return {
            "ip_discount_rate": self.ip_discount_rate,
            "tax_amortization_factor": tab_factor,
            "pv_excess_earnings_pre_tab": pv_excess_earnings_pre_tab,
            "patent_value_post_tab": value_with_tab,
            "schedule": schedule
        }

    def evaluate_real_options(self) -> Dict[str, Any]:
        ro = self.data.get("real_options", {})
        if not ro:
            return {}

        pv_cash_flows_s = float(ro.get("pv_expected_cash_flows", 50_000_000))
        commercialization_capex_k = float(ro.get("commercialization_capex", 35_000_000))
        time_to_expiry_t = float(ro.get("time_to_expiration_years", 4.0))
        risk_free_rate_r = float(ro.get("risk_free_rate", 0.04))
        volatility_sigma = float(ro.get("volatility", 0.45))  # 45% annual volatility for commercial tech

        bs_res = black_scholes_call(
            s=pv_cash_flows_s,
            k=commercialization_capex_k,
            t=time_to_expiry_t,
            r=risk_free_rate_r,
            sigma=volatility_sigma
        )

        # Staged Phase Gates (Decision Tree / Binomial Logic)
        staged_phases = ro.get("staged_phases", [])
        staged_expected_npv = None
        if staged_phases:
            # Evaluate backward induction on staged R&D
            # Each stage has cost C_i, duration T_i, and probability of success P_i
            cum_prob = 1.0
            expected_cost_pv = 0.0
            t_acc = 0.0
            for stage in staged_phases:
                c = float(stage.get("cost", 0.0))
                prob = float(stage.get("prob_success", 1.0))
                dur = float(stage.get("duration_years", 1.0))
                t_acc += dur
                expected_cost_pv += (c * cum_prob) / math.pow(1.0 + risk_free_rate_r, t_acc)
                cum_prob *= prob

            pv_payoff = (pv_cash_flows_s * cum_prob) / math.pow(1.0 + risk_free_rate_r, t_acc)
            staged_expected_npv = pv_payoff - expected_cost_pv

        return {
            "black_scholes": {
                "pv_commercial_cash_flows_s": pv_cash_flows_s,
                "commercialization_capex_k": commercialization_capex_k,
                "time_to_expiration_years": time_to_expiry_t,
                "risk_free_rate": risk_free_rate_r,
                "volatility": volatility_sigma,
                "option_value": bs_res["call_value"],
                "intrinsic_value": bs_res["intrinsic_value"],
                "time_value": bs_res["time_value"],
                "d1": bs_res["d1"],
                "d2": bs_res["d2"]
            },
            "staged_r_and_d_expected_npv": staged_expected_npv
        }

    def evaluate_all(self) -> Dict[str, Any]:
        rfr = self.evaluate_relief_from_royalty()
        mpeem = self.evaluate_mpeem()
        ro = self.evaluate_real_options()

        summary_values = []
        if "patent_value_post_tab" in rfr:
            summary_values.append({"method": "Relief-from-Royalty", "value": rfr["patent_value_post_tab"]})
        if "patent_value_post_tab" in mpeem:
            summary_values.append({"method": "MPEEM", "value": mpeem["patent_value_post_tab"]})
        if "black_scholes" in ro and "option_value" in ro["black_scholes"]:
            summary_values.append({"method": "Black-Scholes Real Option", "value": ro["black_scholes"]["option_value"]})

        con_val = (sum(v["value"] for v in summary_values) / len(summary_values)) if summary_values else 0.0

        return {
            "patent_name": self.patent_name,
            "currency": self.currency,
            "relief_from_royalty": rfr,
            "mpeem": mpeem,
            "real_options": ro,
            "summary_methods": summary_values,
            "consensus_ip_value": con_val
        }

    def generate_markdown_report(self, res: Dict[str, Any]) -> str:
        lines = []
        c = res["currency"]
        lines.append(f"# 💡 Intellectual Property & Patent Valuation: {res['patent_name']}")
        lines.append("**Methodologies:** Relief-from-Royalty, MPEEM & Black-Scholes Real Options")
        lines.append("")

        lines.append("## 📌 IP Valuation Summary")
        lines.append(f"| Valuation Standard | Implied Value ({c}) | Treatment & Basis |")
        lines.append("| :--- | :---: | :--- |")
        for v in res["summary_methods"]:
            lines.append(f"| **{v['method']}** | **{c} {v['value']:,.2f}** | Post-Tax Amortization Benefit (TAB) |")
        lines.append(f"| **CONSENSUS IP VALUE** | **{c} {res['consensus_ip_value']:,.2f}** | Synthesis across active models |")
        lines.append("")

        # Relief from Royalty
        rfr = res.get("relief_from_royalty", {})
        if rfr and "patent_value_post_tab" in rfr:
            lines.append("## 📜 Relief-from-Royalty Model Breakdown")
            lines.append(f"- **Benchmark Royalty Rate:** {rfr['royalty_rate']:.2%}")
            lines.append(f"- **IP Discount Rate:** {rfr['ip_discount_rate']:.2%}")
            lines.append(f"- **Tax Amortization Benefit (TAB) Multiplier:** {rfr['tax_amortization_factor']:.4f}x")
            lines.append(f"- **Pre-TAB Present Value:** {c} {rfr['pv_royalty_savings_pre_tab']:,.2f}")
            lines.append(f"- **Final IP Value (Post-TAB):** **{c} {rfr['patent_value_post_tab']:,.2f}**")
            lines.append("")

        # Real Options
        ro = res.get("real_options", {}).get("black_scholes", {})
        if ro:
            lines.append("## 🔬 Real Options Valuation (Black-Scholes Model)")
            lines.append(f"- **PV of Commercial Market Payoff ($S$):** {c} {ro['pv_commercial_cash_flows_s']:,.2f}")
            lines.append(f"- **Commercialization Capex ($K$):** {c} {ro['commercialization_capex_k']:,.2f}")
            lines.append(f"- **Patent Window ($T$):** {ro['time_to_expiration_years']:.1f} years")
            lines.append(f"- **Technology Cash Flow Volatility ($\\sigma$):** {ro['volatility']:.1%}")
            lines.append(f"- **Intrinsic Value:** {c} {ro['intrinsic_value']:,.2f}")
            lines.append(f"- **Time Option Value:** {c} {ro['time_value']:,.2f}")
            lines.append(f"- **Total Patent Option Value:** **{c} {ro['option_value']:,.2f}**")
            lines.append("")

        return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="IP, Patent & Technology Valuation Engine")
    parser.add_argument("--input", "-i", type=str, required=True, help="Input JSON file")
    parser.add_argument("--output", "-o", type=str, default=None, help="Output JSON path")
    parser.add_argument("--report", "-r", type=str, default=None, help="Output Markdown report path")
    parser.add_argument("--format", "-f", choices=["json", "markdown"], default="markdown")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    engine = IPPatentValuationEngine(data)
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

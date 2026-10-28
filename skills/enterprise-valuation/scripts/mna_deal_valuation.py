#!/usr/bin/env python3
"""
mna_deal_valuation.py - M&A, Deal Structuring, Synergies & Acquired Asset Valuation Engine
Based on:
- McKinsey & Company (Valuation, 8th Edition, Part V: Corporate Portfolio Strategy & M&A)
- Frank C. Evans & David M. Bishop / Chris M. Mellen (Valuation for M&A: Building and Measuring Private Company Value, 3rd Edition, Wiley Finance)
- IFRS 3 / ASC 805 Business Combinations (Purchase Price Allocation - PPA)
"""

import sys
import json
import math
import argparse
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class SynergyItem:
    name: str
    category: str  # "cost", "revenue", "capex", "financial"
    annual_amounts: List[float]  # Phased over forecast horizon
    margin_percentage: float = 1.0  # For revenue synergies, margin to convert to operating profit
    tax_rate: float = 0.25
    discount_rate_premium: float = 0.0  # Spread above base WACC to reflect execution risk

@dataclass
class IntegrationCost:
    name: str
    annual_cash_outlays: List[float]

class MNADealValuationEngine:
    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.deal_name = data.get("deal_name", "Strategic Acquisition")
        self.currency = data.get("currency", "USD")
        self.acquirer_name = data.get("acquirer_name", "Acquirer Corp")
        self.target_name = data.get("target_name", "Target Ltd")
        
        # Financial baselines
        self.target_standalone_equity = float(data.get("target_standalone_equity_value", 100_000_000))
        self.target_shares_outstanding = float(data.get("target_shares_outstanding", 10_000_000))
        self.target_wacc = float(data.get("target_wacc", 0.09))
        self.acquirer_wacc = float(data.get("acquirer_wacc", 0.08))
        self.marginal_tax_rate = float(data.get("tax_rate", 0.25))
        self.terminal_synergy_growth = float(data.get("terminal_synergy_growth", 0.02))

        # Deal Terms
        self.acquisition_premium_pct = float(data.get("acquisition_premium_percentage", 0.25))  # 25% control premium
        self.cash_consideration_pct = float(data.get("cash_consideration_percentage", 0.70))  # 70% cash, 30% stock
        
        # Private Company Valuation Parameters (Evans & Mellen)
        self.private_target_adjustments = data.get("private_target_adjustments", {})
        self.apply_private_discounts = bool(self.private_target_adjustments.get("enabled", False))
        self.officer_comp_adjustment = float(self.private_target_adjustments.get("annual_officer_comp_normalization", 0.0))
        self.dlom = float(self.private_target_adjustments.get("discount_lack_of_marketability", 0.20))  # 20% DLOM
        self.control_premium = float(self.private_target_adjustments.get("control_premium", 0.25))

        # Synergies and Costs
        self.synergies = self._parse_synergies(data.get("synergies", []))
        self.integration_costs = self._parse_integration_costs(data.get("integration_costs", []))
        
        # Balance Sheet & PPA (IFRS 3 / ASC 805)
        self.ppa_data = data.get("purchase_price_allocation", {})
        self.warnings: List[str] = []

    def _parse_synergies(self, raw_list: List[Dict[str, Any]]) -> List[SynergyItem]:
        items = []
        for s in raw_list:
            items.append(SynergyItem(
                name=s.get("name", "Synergy"),
                category=s.get("category", "cost").lower(),
                annual_amounts=[float(x) for x in s.get("annual_amounts", [])],
                margin_percentage=float(s.get("margin_percentage", 1.0)),
                tax_rate=float(s.get("tax_rate", self.marginal_tax_rate)),
                discount_rate_premium=float(s.get("discount_rate_premium", 0.0))
            ))
        return items

    def _parse_integration_costs(self, raw_list: List[Dict[str, Any]]) -> List[IntegrationCost]:
        items = []
        for c in raw_list:
            items.append(IntegrationCost(
                name=c.get("name", "Integration"),
                annual_cash_outlays=[float(x) for x in c.get("annual_cash_outlays", [])]
            ))
        return items

    def compute_synergies_npv(self) -> Dict[str, Any]:
        """
        McKinsey 8th Ed. Standard:
        - Cost synergies discounted at WACC (or WACC + 1% execution spread).
        - Revenue synergies discounted at WACC + 3-4% (higher commercial friction).
        - Integration expenses after tax deducted.
        """
        max_years = 0
        for s in self.synergies:
            max_years = max(max_years, len(s.annual_amounts))
        for c in self.integration_costs:
            max_years = max(max_years, len(c.annual_cash_outlays))
        if max_years == 0:
            max_years = 5

        synergy_breakdown = []
        total_pv_synergies = 0.0
        total_terminal_pv_synergies = 0.0

        for s in self.synergies:
            # Risk-adjusted hurdle rate per McKinsey & Evans/Mellen
            effective_discount_rate = self.target_wacc + s.discount_rate_premium
            if s.category == "revenue" and s.discount_rate_premium == 0.0:
                effective_discount_rate += 0.025  # Automatic 2.5% execution penalty on revenue synergies

            pv_annual = 0.0
            annual_after_tax_flows = []
            
            for t_idx, amt in enumerate(s.annual_amounts):
                t = t_idx + 1
                if s.category == "revenue":
                    operating_flow = amt * s.margin_percentage * (1.0 - s.tax_rate)
                elif s.category == "cost":
                    operating_flow = amt * (1.0 - s.tax_rate)
                elif s.category == "capex":
                    operating_flow = amt  # Direct cash savings
                else:  # financial
                    operating_flow = amt
                
                annual_after_tax_flows.append(operating_flow)
                pv_annual += operating_flow / math.pow(1.0 + effective_discount_rate, t)

            # Terminal synergy value (sustaining run-rate synergies into perpetuity)
            last_flow = annual_after_tax_flows[-1] if annual_after_tax_flows else 0.0
            g = self.terminal_synergy_growth
            if effective_discount_rate > g and last_flow > 0:
                terminal_flow = last_flow * (1.0 + g)
                terminal_val = terminal_flow / (effective_discount_rate - g)
                pv_terminal = terminal_val / math.pow(1.0 + effective_discount_rate, len(annual_after_tax_flows))
            else:
                terminal_val = 0.0
                pv_terminal = 0.0

            total_s_pv = pv_annual + pv_terminal
            total_pv_synergies += total_s_pv
            total_terminal_pv_synergies += pv_terminal

            synergy_breakdown.append({
                "name": s.name,
                "category": s.category,
                "effective_discount_rate": effective_discount_rate,
                "pv_discrete_flows": pv_annual,
                "pv_terminal_synergy": pv_terminal,
                "total_pv": total_s_pv
            })

        # Integration Costs
        total_pv_integration = 0.0
        integration_breakdown = []
        for c in self.integration_costs:
            pv_cost = 0.0
            for t_idx, outlay in enumerate(c.annual_cash_outlays):
                t = t_idx + 1
                after_tax_cost = outlay * (1.0 - self.marginal_tax_rate)
                pv_cost += after_tax_cost / math.pow(1.0 + self.target_wacc, t)
            total_pv_integration += pv_cost
            integration_breakdown.append({"name": c.name, "pv_after_tax_cost": pv_cost})

        net_pv_synergies = total_pv_synergies - total_pv_integration

        return {
            "synergy_breakdown": synergy_breakdown,
            "gross_pv_synergies": total_pv_synergies,
            "pv_terminal_component": total_terminal_pv_synergies,
            "integration_breakdown": integration_breakdown,
            "pv_integration_costs": total_pv_integration,
            "net_pv_synergies": net_pv_synergies
        }

    def evaluate_deal(self) -> Dict[str, Any]:
        # 1. Private Company Standalone Adjustments (Evans & Mellen)
        standalone_equity = self.target_standalone_equity
        if self.apply_private_discounts:
            # Add normalized officer compensation: PV of annual savings
            if self.officer_comp_adjustment != 0:
                pv_comp = (self.officer_comp_adjustment * (1.0 - self.marginal_tax_rate)) / self.target_wacc
                standalone_equity += pv_comp

            # DLOC = 1 - 1/(1 + Control Premium)
            dloc = 1.0 - (1.0 / (1.0 + self.control_premium)) if self.control_premium > 0 else 0.0
            # For private firm: Apply DLOM on minority interest
            standalone_equity_minority_illiquid = standalone_equity * (1.0 - dloc) * (1.0 - self.dlom)
        else:
            standalone_equity_minority_illiquid = standalone_equity

        # 2. Synergies & Integration
        syn_res = self.compute_synergies_npv()
        net_synergies = syn_res["net_pv_synergies"]

        # 3. Maximum Offer Price (Breakeven Price)
        # Max Price = Standalone Equity Value + Net Synergies
        max_purchase_price = standalone_equity + net_synergies

        # 4. Negotiated Offer Price based on Acquisition Premium
        # Evans & Mellen: Offer Price = Standalone Equity * (1 + Premium)
        actual_offer_price = standalone_equity * (1.0 + self.acquisition_premium_pct)
        dollar_premium_paid = actual_offer_price - standalone_equity

        # 5. Value Creation Bridge (McKinsey Theorem of M&A Value Creation)
        # Value Created for Acquirer = Net Synergies - Premium Paid
        value_created_acquirer = net_synergies - dollar_premium_paid
        value_created_target = dollar_premium_paid

        # Governance Warnings (Winner's Curse audit)
        if dollar_premium_paid > net_synergies:
            self.warnings.append(
                f"🚨 WINNER'S CURSE DETECTED: Acquisition premium paid ({self.currency} {dollar_premium_paid:,.2f}) "
                f"exceeds the entire Net PV of Synergies ({self.currency} {net_synergies:,.2f}) by "
                f"{self.currency} {abs(value_created_acquirer):,.2f}! Value is destroyed for {self.acquirer_name} shareholders."
            )
        elif value_created_acquirer < (net_synergies * 0.20):
            self.warnings.append(
                f"⚠️ TIGHT DEAL MARGIN: Acquirer captures only {value_created_acquirer / net_synergies:.1%} of total synergy value; "
                "the majority of economic value created is transferred to target shareholders."
            )

        # 6. Purchase Price Allocation (PPA - IFRS 3 / ASC 805)
        # Allocation of total purchase price to fair value of net identifiable assets & goodwill
        book_val_net_assets = float(self.ppa_data.get("target_book_value_net_assets", standalone_equity * 0.50))
        tangible_fv_stepup = float(self.ppa_data.get("tangible_assets_fair_value_step_up", standalone_equity * 0.10))
        
        # Identifiable Intangibles recognized at fair value
        identifiable_intangibles = self.ppa_data.get("identifiable_intangibles", {
            "developed_technology_patents": standalone_equity * 0.15,
            "customer_relationships_contracts": standalone_equity * 0.10,
            "trademarks_brand_names": standalone_equity * 0.05
        })
        total_identifiable_intangibles = sum(float(v) for v in identifiable_intangibles.values())

        fair_value_net_identifiable_assets = (
            book_val_net_assets +
            tangible_fv_stepup +
            total_identifiable_intangibles
        )

        residual_goodwill = max(actual_offer_price - fair_value_net_identifiable_assets, 0.0)

        # Per share metrics
        shares = max(self.target_shares_outstanding, 0.001)
        standalone_per_share = standalone_equity / shares
        offer_per_share = actual_offer_price / shares
        max_offer_per_share = max_purchase_price / shares

        return {
            "deal_name": self.deal_name,
            "currency": self.currency,
            "acquirer_name": self.acquirer_name,
            "target_name": self.target_name,
            "target_shares_outstanding": shares,
            "target_standalone_equity_value": standalone_equity,
            "standalone_per_share": standalone_per_share,
            "acquisition_premium_percentage": self.acquisition_premium_pct,
            "dollar_premium_paid": dollar_premium_paid,
            "actual_offer_price": actual_offer_price,
            "offer_price_per_share": offer_per_share,
            "maximum_purchase_price": max_purchase_price,
            "maximum_offer_per_share": max_offer_per_share,
            "synergies_and_costs": syn_res,
            "value_creation": {
                "net_pv_synergies": net_synergies,
                "premium_paid_to_target": dollar_premium_paid,
                "net_value_created_for_acquirer": value_created_acquirer,
                "value_distribution_pct_target": (dollar_premium_paid / net_synergies * 100.0) if net_synergies > 0 else 0.0,
                "value_distribution_pct_acquirer": (value_created_acquirer / net_synergies * 100.0) if net_synergies > 0 else 0.0
            },
            "purchase_price_allocation_ifrs3": {
                "total_purchase_price": actual_offer_price,
                "book_value_net_assets": book_val_net_assets,
                "tangible_assets_step_up": tangible_fv_stepup,
                "identifiable_intangibles": identifiable_intangibles,
                "total_identifiable_intangibles": total_identifiable_intangibles,
                "fair_value_net_identifiable_assets": fair_value_net_identifiable_assets,
                "residual_goodwill": residual_goodwill,
                "goodwill_percentage_of_price": (residual_goodwill / actual_offer_price) if actual_offer_price > 0 else 0.0
            },
            "private_target_adjustments": {
                "applied": self.apply_private_discounts,
                "dlom_percentage": self.dlom if self.apply_private_discounts else 0.0,
                "control_premium": self.control_premium if self.apply_private_discounts else 0.0
            },
            "warnings": self.warnings
        }

    def generate_markdown_report(self, res: Dict[str, Any]) -> str:
        lines = []
        c = res["currency"]
        vc = res["value_creation"]
        ppa = res["purchase_price_allocation_ifrs3"]

        lines.append(f"# 🤝 M&A Deal Structuring & Synergy Valuation Report")
        lines.append(f"**Transaction:** {res['acquirer_name']} ➔ {res['target_name']} ({res['deal_name']})")
        lines.append("**Standards:** McKinsey 8th Ed. Part V, Evans & Mellen Private Valuation & IFRS 3 / ASC 805 PPA")
        lines.append("")

        lines.append("## 📌 Executive Deal Summary & Value Creation Bridge")
        lines.append(f"| Transaction Metric | Value ({c}) | Per Share ({c}) | Strategic Benchmark |")
        lines.append("| :--- | :---: | :---: | :--- |")
        lines.append(f"| **Standalone Target Value** | {res['target_standalone_equity_value']:,.2f} | {res['standalone_per_share']:,.2f} | Unaffected market/intrinsic price |")
        lines.append(f"| **(+) Net PV of Synergies** | +{vc['net_pv_synergies']:,.2f} | +{vc['net_pv_synergies'] / max(res['target_shares_outstanding'], 1.0):,.2f} | After integration costs & execution discount |")
        lines.append(f"| **(=) Maximum Walk-Away Price** | **{res['maximum_purchase_price']:,.2f}** | **{res['maximum_offer_per_share']:,.2f}** | Zero-NPV ceiling for Acquirer |")
        lines.append(f"| **(-) Negotiated Offer Price** | **{res['actual_offer_price']:,.2f}** | **{res['offer_price_per_share']:,.2f}** | {res['acquisition_premium_percentage']:.1%} Control Premium |")
        status_symbol = "✅" if vc['net_value_created_for_acquirer'] > 0 else "🚨"
        lines.append(f"| **{status_symbol} Net Value Created for Acquirer** | **{vc['net_value_created_for_acquirer']:,.2f}** | — | **Acquirer Shareholder Gain** |")
        lines.append("")

        # Synergy Breakdown Table
        lines.append("## ⚡ Synergies & Integration Capital Phasing")
        lines.append(f"| Synergy Stream | Category | Hurdle Rate | Discrete PV ({c}) | Terminal PV ({c}) | Total PV ({c}) |")
        lines.append("| :--- | :---: | :---: | :---: | :---: | :---: |")
        for s in res["synergies_and_costs"]["synergy_breakdown"]:
            lines.append(
                f"| {s['name']} | {s['category'].upper()} | {s['effective_discount_rate']:.2%} | "
                f"{s['pv_discrete_flows']:,.2f} | {s['pv_terminal_synergy']:,.2f} | **{s['total_pv']:,.2f}** |"
            )
        lines.append(f"| **Gross Synergies PV** | — | — | — | — | **{res['synergies_and_costs']['gross_pv_synergies']:,.2f}** |")
        lines.append(f"| **(-) PV of Integration Costs** | One-time | {self.target_wacc:.2%} | — | — | **-{res['synergies_and_costs']['pv_integration_costs']:,.2f}** |")
        lines.append(f"| **(=) Net Synergies Available** | Net | — | — | — | **{vc['net_pv_synergies']:,.2f}** |")
        lines.append("")

        # Purchase Price Allocation Table (IFRS 3 / ASC 805)
        lines.append("## 📑 Purchase Price Allocation (PPA - IFRS 3 / ASC 805)")
        lines.append(f"| Balance Sheet Item / Acquired Asset | Allocated Fair Value ({c}) | % of Purchase Price |")
        lines.append("| :--- | :---: | :---: |")
        lines.append(f"| Book Value of Net Assets Acquired | {ppa['book_value_net_assets']:,.2f} | {ppa['book_value_net_assets'] / ppa['total_purchase_price']:.1%} |")
        lines.append(f"| Tangible Asset Fair Value Step-Up | {ppa['tangible_assets_step_up']:,.2f} | {ppa['tangible_assets_step_up'] / ppa['total_purchase_price']:.1%} |")
        for k, v in ppa["identifiable_intangibles"].items():
            clean_k = k.replace("_", " ").title()
            lines.append(f"| Identifiable Intangible: {clean_k} | {v:,.2f} | {v / ppa['total_purchase_price']:.1%} |")
        lines.append(f"| **Fair Value of Net Identifiable Assets** | **{ppa['fair_value_net_identifiable_assets']:,.2f}** | **{ppa['fair_value_net_identifiable_assets'] / ppa['total_purchase_price']:.1%}** |")
        lines.append(f"| **Residual Accounting Goodwill** | **{ppa['residual_goodwill']:,.2f}** | **{ppa['goodwill_percentage_of_price']:.1%}** |")
        lines.append(f"| **Total Transaction Consideration** | **{ppa['total_purchase_price']:,.2f}** | **100.0%** |")
        lines.append("")

        if res["warnings"]:
            lines.append("## ⚠️ M&A Deal Governance & Risk Warnings")
            for w in res["warnings"]:
                lines.append(f"- {w}")
            lines.append("")

        return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="M&A Deal Structuring, Synergies & PPA Valuation Engine")
    parser.add_argument("--input", "-i", type=str, required=True, help="Input JSON file")
    parser.add_argument("--output", "-o", type=str, default=None, help="Output JSON path")
    parser.add_argument("--report", "-r", type=str, default=None, help="Output Markdown report path")
    parser.add_argument("--format", "-f", choices=["json", "markdown"], default="markdown")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    engine = MNADealValuationEngine(data)
    results = engine.evaluate_deal()

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

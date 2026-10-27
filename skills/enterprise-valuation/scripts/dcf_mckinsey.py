#!/usr/bin/env python3
"""
dcf_mckinsey.py - Corporate Enterprise Valuation Engine
Based on McKinsey & Company (Valuation: Measuring and Managing the Value of Companies, 8th Edition)
and Damodaran Frameworks (Distress probability, synthetic rating, country risk premium).
"""

import sys
import json
import math
import argparse
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class PeriodForecast:
    year: int
    revenue: float
    ebit: float
    tax_rate: float
    depreciation_amortization: float
    capex: float
    change_in_nwc: float
    maintenance_capex: Optional[float] = None
    stock_based_compensation: float = 0.0
    invested_capital: Optional[float] = None

@dataclass
class ValuationAssumptions:
    cost_of_equity: float  # Ke
    pre_tax_cost_of_debt: float  # Kd
    tax_rate: float
    market_equity_weight: float  # E / V
    market_debt_weight: float  # D / V
    terminal_growth_rate: float  # g
    terminal_roic: Optional[float] = None
    long_term_gdp_growth: float = 0.03
    risk_free_rate: float = 0.04
    discounting_convention: str = "mid_year"  # "mid_year" (McKinsey standard) or "end_of_year"
    economic_moat: str = "narrow"  # "wide", "narrow", "none" (Buffett Moat classification)
    margin_of_safety: float = 0.25  # Buffett 25% Margin of Safety discount
    probability_of_distress: float = 0.0
    distress_liquidation_recovery_rate: float = 0.40  # % of book value or invested capital recovered

@dataclass
class BalanceSheetBridge:
    cash_and_marketable_securities: float = 0.0
    non_operating_assets: float = 0.0
    total_debt: float = 0.0
    operating_lease_liabilities: float = 0.0
    pension_deficits: float = 0.0
    contingent_litigation_liabilities: float = 0.0
    minority_interests: float = 0.0
    shares_outstanding: float = 1.0

class McKinseyDCFEngine:
    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.company_name = data.get("company_name", "Enterprise")
        self.currency = data.get("currency", "USD")
        self.assumptions = self._parse_assumptions(data.get("assumptions", {}))
        self.bridge = self._parse_bridge(data.get("balance_sheet_bridge", {}))
        self.forecasts = self._parse_forecasts(data.get("forecasts", []))
        self.initial_invested_capital = data.get("initial_invested_capital", None)
        self.sanity_warnings: List[str] = []

    def _parse_assumptions(self, raw: Dict[str, Any]) -> ValuationAssumptions:
        return ValuationAssumptions(
            cost_of_equity=float(raw.get("cost_of_equity", 0.09)),
            pre_tax_cost_of_debt=float(raw.get("pre_tax_cost_of_debt", 0.05)),
            tax_rate=float(raw.get("tax_rate", 0.25)),
            market_equity_weight=float(raw.get("market_equity_weight", 0.80)),
            market_debt_weight=float(raw.get("market_debt_weight", 0.20)),
            terminal_growth_rate=float(raw.get("terminal_growth_rate", 0.025)),
            terminal_roic=float(raw["terminal_roic"]) if "terminal_roic" in raw and raw["terminal_roic"] is not None else None,
            long_term_gdp_growth=float(raw.get("long_term_gdp_growth", 0.03)),
            risk_free_rate=float(raw.get("risk_free_rate", 0.04)),
            discounting_convention=str(raw.get("discounting_convention", "mid_year")).lower(),
            economic_moat=str(raw.get("economic_moat", "narrow")).lower(),
            margin_of_safety=float(raw.get("margin_of_safety", 0.25)),
            probability_of_distress=float(raw.get("probability_of_distress", 0.0)),
            distress_liquidation_recovery_rate=float(raw.get("distress_liquidation_recovery_rate", 0.40))
        )

    def _parse_bridge(self, raw: Dict[str, Any]) -> BalanceSheetBridge:
        return BalanceSheetBridge(
            cash_and_marketable_securities=float(raw.get("cash_and_marketable_securities", 0.0)),
            non_operating_assets=float(raw.get("non_operating_assets", 0.0)),
            total_debt=float(raw.get("total_debt", 0.0)),
            operating_lease_liabilities=float(raw.get("operating_lease_liabilities", 0.0)),
            pension_deficits=float(raw.get("pension_deficits", 0.0)),
            contingent_litigation_liabilities=float(raw.get("contingent_litigation_liabilities", 0.0)),
            minority_interests=float(raw.get("minority_interests", 0.0)),
            shares_outstanding=float(raw.get("shares_outstanding", 1.0))
        )

    def _parse_forecasts(self, raw_list: List[Dict[str, Any]]) -> List[PeriodForecast]:
        periods = []
        for item in raw_list:
            periods.append(PeriodForecast(
                year=int(item["year"]),
                revenue=float(item.get("revenue", 0.0)),
                ebit=float(item.get("ebit", 0.0)),
                tax_rate=float(item.get("tax_rate", self.assumptions.tax_rate)),
                depreciation_amortization=float(item.get("depreciation_amortization", 0.0)),
                capex=float(item.get("capex", 0.0)),
                change_in_nwc=float(item.get("change_in_nwc", 0.0)),
                maintenance_capex=float(item["maintenance_capex"]) if "maintenance_capex" in item and item["maintenance_capex"] is not None else None,
                stock_based_compensation=float(item.get("stock_based_compensation", 0.0)),
                invested_capital=float(item["invested_capital"]) if "invested_capital" in item and item["invested_capital"] is not None else None
            ))
        return periods

    def calculate_wacc(self) -> float:
        """
        WACC = (E/V) * Ke + (D/V) * Kd * (1 - T)
        """
        ke = self.assumptions.cost_of_equity
        kd = self.assumptions.pre_tax_cost_of_debt
        t = self.assumptions.tax_rate
        we = self.assumptions.market_equity_weight
        wd = self.assumptions.market_debt_weight
        
        # Normalize weights if sum != 1.0
        total_weight = we + wd
        if abs(total_weight - 1.0) > 1e-4 and total_weight > 0:
            we /= total_weight
            wd /= total_weight
            
        wacc = (we * ke) + (wd * kd * (1.0 - t))
        return wacc

    def run_valuation(self) -> Dict[str, Any]:
        wacc = self.calculate_wacc()
        g = self.assumptions.terminal_growth_rate

        # Sanity Checks
        if g >= wacc:
            raise ValueError(f"Terminal growth rate ({g:.2%}) cannot be greater than or equal to WACC ({wacc:.2%}).")
        if g > self.assumptions.risk_free_rate:
            self.sanity_warnings.append(
                f"Terminal growth rate ({g:.2%}) exceeds the risk-free rate ({self.assumptions.risk_free_rate:.2%}). "
                "Per Damodaran's Golden Rule of Valuation, no firm can grow faster than the risk-free rate in perpetuity without becoming larger than the entire economy."
            )
        if g > self.assumptions.long_term_gdp_growth:
            self.sanity_warnings.append(
                f"Terminal growth rate ({g:.2%}) exceeds projected long-term GDP growth ({self.assumptions.long_term_gdp_growth:.2%}). "
                "Per McKinsey Ch. 12, a perpetual growth rate above sustainable macroeconomic GDP implies the firm outgrows the economy."
            )

        # Forecast computations
        period_results = []
        cumulative_pv_fcff = 0.0
        cumulative_pv_ep = 0.0
        total_owner_earnings = 0.0
        
        prev_ic = self.initial_invested_capital
        is_mid_year = self.assumptions.discounting_convention == "mid_year"
        
        for idx, p in enumerate(self.forecasts):
            t = idx + 1
            nopat = p.ebit * (1.0 - p.tax_rate)
            # FCFF = NOPAT + D&A - Capex - Change in NWC - Stock-Based Compensation
            net_investment = (p.capex - p.depreciation_amortization) + p.change_in_nwc
            fcff = nopat - net_investment - p.stock_based_compensation
            
            # Buffett Owner Earnings: NOPAT + D&A - Maintenance Capex - Change in NWC - SBC
            maint_capex = p.maintenance_capex if p.maintenance_capex is not None else min(p.capex, p.depreciation_amortization)
            growth_capex = max(p.capex - maint_capex, 0.0)
            owner_earnings = nopat + p.depreciation_amortization - maint_capex - p.change_in_nwc - p.stock_based_compensation
            total_owner_earnings += owner_earnings

            # Discount Factor (Mid-Year vs End-of-Year)
            discount_power = (t - 0.5) if is_mid_year else float(t)
            discount_factor = 1.0 / math.pow(1.0 + wacc, discount_power)
            pv_fcff = fcff * discount_factor
            cumulative_pv_fcff += pv_fcff
            
            # Invested capital tracking & ROIC
            ic = p.invested_capital
            if ic is None:
                if prev_ic is not None:
                    ic = prev_ic + net_investment
                else:
                    ic = 0.0
            
            roic = (nopat / ic) if ic and ic > 0 else 0.0
            
            # Economic profit: EP = Invested Capital_{t-1} * (ROIC - WACC) = NOPAT - (IC_{t-1} * WACC)
            base_ic_for_ep = prev_ic if (prev_ic is not None and prev_ic > 0) else ic
            economic_profit = nopat - (base_ic_for_ep * wacc)
            pv_ep = economic_profit * discount_factor
            cumulative_pv_ep += pv_ep

            period_results.append({
                "period": t,
                "year": p.year,
                "revenue": p.revenue,
                "ebit": p.ebit,
                "nopat": nopat,
                "depreciation_amortization": p.depreciation_amortization,
                "capex": p.capex,
                "maintenance_capex": maint_capex,
                "growth_capex": growth_capex,
                "stock_based_compensation": p.stock_based_compensation,
                "change_in_nwc": p.change_in_nwc,
                "net_investment": net_investment,
                "fcff": fcff,
                "owner_earnings": owner_earnings,
                "invested_capital": ic,
                "roic": roic,
                "economic_profit": economic_profit,
                "discount_factor": discount_factor,
                "pv_fcff": pv_fcff,
                "pv_economic_profit": pv_ep
            })
            prev_ic = ic

        # Terminal Value Calculation (McKinsey Key Value Driver Formula & Buffett Moat Fade)
        last_forecast = period_results[-1]
        nopat_terminal_base = last_forecast["nopat"] * (1.0 + g)
        
        raw_terminal_roic = self.assumptions.terminal_roic
        if raw_terminal_roic is None:
            raw_terminal_roic = last_forecast["roic"] if last_forecast["roic"] > 0 else wacc

        # Buffett Moat Durability Adjustment
        moat = self.assumptions.economic_moat
        if moat == "none":
            terminal_roic = wacc
            self.sanity_warnings.append(
                f"Buffett Moat Rating = 'NONE': Terminal ROIC faded from {raw_terminal_roic:.1%} directly to WACC ({wacc:.1%}). "
                "Without a defensible competitive moat, free-market competition erodes all excess returns."
            )
        elif moat == "narrow":
            terminal_roic = wacc + 0.50 * max(raw_terminal_roic - wacc, 0.0)
            self.sanity_warnings.append(
                f"Buffett Moat Rating = 'NARROW': Terminal ROIC adjusted to {terminal_roic:.1%} (50% fade toward WACC {wacc:.1%}) to reflect medium-term competitive decay."
            )
        else:  # wide moat
            terminal_roic = raw_terminal_roic
            if terminal_roic > (wacc + 0.12):
                self.sanity_warnings.append(
                    f"Buffett Moat Rating = 'WIDE': Terminal ROIC ({terminal_roic:.1%}) exceeds WACC by >12%. "
                    "Ensure high pricing power, patents, or insurmountable network effects justify this premium."
                )

        # Key Value Driver: Value = NOPAT * (1 - g/ROIC) / (WACC - g)
        investment_rate_terminal = (g / terminal_roic) if terminal_roic > 0 else 0.0
        if investment_rate_terminal > 1.0:
            self.sanity_warnings.append(
                f"Terminal investment rate (g / ROIC = {investment_rate_terminal:.2%}) exceeds 100%. Adjusting to standard FCF growth."
            )
            terminal_fcf = nopat_terminal_base * (1.0 - investment_rate_terminal)
            terminal_value = terminal_fcf / (wacc - g)
        else:
            terminal_fcf = nopat_terminal_base * (1.0 - investment_rate_terminal)
            terminal_value = (nopat_terminal_base * (1.0 - (g / terminal_roic))) / (wacc - g)

        n_years = len(period_results)
        terminal_discount_factor = 1.0 / math.pow(1.0 + wacc, n_years)
        pv_terminal_value = terminal_value * terminal_discount_factor
        
        # Enterprise Value (Going Concern)
        ev_going_concern = cumulative_pv_fcff + pv_terminal_value
        
        # Economic Profit (EVA) Valuation Model Reconciliation:
        terminal_ep = (nopat_terminal_base - (last_forecast["invested_capital"] * (1.0 + g) * wacc))
        terminal_ep_value = terminal_ep / (wacc - g) if (wacc - g) > 0 else 0.0
        pv_terminal_ep = terminal_ep_value * terminal_discount_factor
        initial_ic = self.initial_invested_capital if self.initial_invested_capital is not None else (self.forecasts[0].invested_capital or 0.0)
        ev_economic_profit = initial_ic + cumulative_pv_ep + pv_terminal_ep

        # Distress Probability Adjustment (Damodaran)
        p_distress = self.assumptions.probability_of_distress
        liquidation_value = initial_ic * self.assumptions.distress_liquidation_recovery_rate
        adjusted_ev = (ev_going_concern * (1.0 - p_distress)) + (liquidation_value * p_distress)

        # Equity Value Bridge
        debt_equivalents = (
            self.bridge.operating_lease_liabilities +
            self.bridge.pension_deficits +
            self.bridge.contingent_litigation_liabilities
        )
        total_debt_and_equivalents = self.bridge.total_debt + debt_equivalents
        non_operating_assets_total = self.bridge.cash_and_marketable_securities + self.bridge.non_operating_assets
        
        equity_value = (
            adjusted_ev +
            non_operating_assets_total -
            total_debt_and_equivalents -
            self.bridge.minority_interests
        )
        
        shares = max(self.bridge.shares_outstanding, 0.0001)
        equity_value_per_share = equity_value / shares

        # Buffett Margin of Safety & Owner Earnings Yield
        mos = self.assumptions.margin_of_safety
        buffett_safe_equity_value = equity_value * (1.0 - mos)
        buffett_safe_entry_price = buffett_safe_equity_value / shares
        avg_owner_earnings = total_owner_earnings / len(self.forecasts) if self.forecasts else 0.0
        owner_earnings_yield = (avg_owner_earnings / adjusted_ev) if adjusted_ev > 0 else 0.0

        return {
            "company_name": self.company_name,
            "currency": self.currency,
            "wacc": wacc,
            "discounting_convention": self.assumptions.discounting_convention,
            "economic_moat": self.assumptions.economic_moat,
            "terminal_growth_rate": g,
            "terminal_roic": terminal_roic,
            "terminal_value": terminal_value,
            "pv_discrete_fcff": cumulative_pv_fcff,
            "pv_terminal_value": pv_terminal_value,
            "enterprise_value_going_concern": ev_going_concern,
            "probability_of_distress": p_distress,
            "distress_adjusted_enterprise_value": adjusted_ev,
            "economic_profit_ev_reconciliation": ev_economic_profit,
            "balance_sheet_bridge": {
                "cash_and_marketable_securities": self.bridge.cash_and_marketable_securities,
                "non_operating_assets": self.bridge.non_operating_assets,
                "total_debt": self.bridge.total_debt,
                "debt_equivalents": debt_equivalents,
                "minority_interests": self.bridge.minority_interests,
                "net_debt_and_claims": total_debt_and_equivalents + self.bridge.minority_interests - non_operating_assets_total
            },
            "equity_value": equity_value,
            "shares_outstanding": shares,
            "equity_value_per_share": equity_value_per_share,
            "buffett_owner_earnings_metrics": {
                "average_owner_earnings": avg_owner_earnings,
                "owner_earnings_yield": owner_earnings_yield,
                "margin_of_safety_percentage": mos,
                "buffett_margin_of_safety_equity_value": buffett_safe_equity_value,
                "buffett_safe_entry_share_price": buffett_safe_entry_price
            },
            "forecast_periods": period_results,
            "sanity_warnings": self.sanity_warnings
        }

    def generate_markdown_report(self, results: Dict[str, Any]) -> str:
        lines = []
        c = results["currency"]
        b_metrics = results["buffett_owner_earnings_metrics"]
        lines.append(f"# 🏛️ Enterprise Valuation Report: {results['company_name']}")
        lines.append(f"**Methodology:** McKinsey 8th Ed. DCF, Damodaran Risk Bridge & Buffett Owner Earnings")
        lines.append("")
        
        # Summary Box
        lines.append("## 📌 Executive Summary")
        lines.append("| Metric | Value | Reference / Notes |")
        lines.append("| :--- | :--- | :--- |")
        lines.append(f"| **WACC** | **{results['wacc']:.2%}** | Weighted Average Cost of Capital |")
        lines.append(f"| **Discounting Convention** | {results['discounting_convention'].upper()} | McKinsey standard mid-year convention |")
        lines.append(f"| **Economic Moat** | **{results['economic_moat'].upper()}** | Berkshire Hathaway competitive advantage tier |")
        lines.append(f"| **Perpetual Growth ($g$)** | {results['terminal_growth_rate']:.2%} | Long-term sustainable growth |")
        lines.append(f"| **Terminal ROIC** | {results['terminal_roic']:.2%} | Post-moat reinvestment efficiency |")
        lines.append(f"| **PV of Discrete Cash Flows** | {c} {results['pv_discrete_fcff']:,.2f} | Forecast horizon |")
        lines.append(f"| **PV of Terminal Value** | {c} {results['pv_terminal_value']:,.2f} | McKinsey Key Value Driver |")
        lines.append(f"| **Enterprise Value (EV)** | **{c} {results['distress_adjusted_enterprise_value']:,.2f}** | Adjusted for distress risk ({results['probability_of_distress']:.1%}) |")
        lines.append(f"| **Equity Value** | **{c} {results['equity_value']:,.2f}** | Net of debt & non-operating claims |")
        lines.append(f"| **Intrinsic Value Per Share** | **{c} {results['equity_value_per_share']:,.2f}** | Shares: {results['shares_outstanding']:,.0f} |")
        lines.append("")

        # Buffett Moat & Margin of Safety Box
        lines.append("## 🛡️ Warren Buffett Owner Earnings & Margin of Safety")
        lines.append("| Metric | Value | Buffett / Munger Rule |")
        lines.append("| :--- | :---: | :--- |")
        lines.append(f"| **Average Owner Earnings** | {c} {b_metrics['average_owner_earnings']:,.2f} | NOPAT + D&A - Maint. Capex - $\\Delta$NWC - SBC |")
        lines.append(f"| **Owner Earnings Yield** | **{b_metrics['owner_earnings_yield']:.2%}** | Target $\\ge 10\\%$ unlevered cash yield |")
        lines.append(f"| **Margin of Safety (MOS)** | {b_metrics['margin_of_safety_percentage']:.1%} | Graham-Buffett margin of safety discount |")
        lines.append(f"| **Safe Entry Equity Value** | {c} {b_metrics['buffett_margin_of_safety_equity_value']:,.2f} | Equity value at {b_metrics['margin_of_safety_percentage']:.0%} discount |")
        lines.append(f"| **Max Safe Entry Share Price** | **{c} {b_metrics['buffett_safe_entry_share_price']:,.2f}** | **Maximum buy price with Margin of Safety** |")
        lines.append("")

        # Discrete Forecasts Table
        lines.append("## 📊 Forecast Horizon Cash Flows & Invested Capital")
        lines.append("| Year | Revenue | EBIT | NOPAT | Net Inv. | FCFF | Owner Earn. | ROIC | Disc. FCFF |")
        lines.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
        for p in results["forecast_periods"]:
            lines.append(
                f"| {p['year']} | {p['revenue']:,.0f} | {p['ebit']:,.0f} | {p['nopat']:,.0f} | "
                f"{p['net_investment']:,.0f} | {p['fcff']:,.0f} | {p['owner_earnings']:,.0f} | "
                f"{p['roic']:.1%} | {p['pv_fcff']:,.1f} |"
            )
        lines.append("")

        # Equity Bridge Table
        b = results["balance_sheet_bridge"]
        lines.append("## 🌉 Enterprise Value to Equity Value Bridge")
        lines.append(f"| Component | Amount ({c}) | Treatment |")
        lines.append("| :--- | :---: | :--- |")
        lines.append(f"| **Enterprise Value** | {results['distress_adjusted_enterprise_value']:,.2f} | Operating Asset Base |")
        lines.append(f"| (+) Cash & Liquid Securities | +{b['cash_and_marketable_securities']:,.2f} | Non-operating cash |")
        lines.append(f"| (+) Non-Operating Assets | +{b['non_operating_assets']:,.2f} | Real estate, JV equity, investments |")
        lines.append(f"| (-) Financial Debt | -{b['total_debt']:,.2f} | Short & Long term interest debt |")
        lines.append(f"| (-) Debt Equivalents | -{b['debt_equivalents']:,.2f} | Capitalized Leases, Pensions, Legal |")
        lines.append(f"| (-) Minority Interest | -{b['minority_interests']:,.2f} | Non-controlling shareholder claim |")
        lines.append(f"| **(=) Equity Value** | **{results['equity_value']:,.2f}** | Total common shareholder equity |")
        lines.append("")

        # Sanity Warnings
        if results["sanity_warnings"]:
            lines.append("## ⚠️ Valuation Sanity & Governance Alerts")
            for w in results["sanity_warnings"]:
                lines.append(f"- ⚠️ **Audit Alert:** {w}")
            lines.append("")

        return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="McKinsey 8th Edition Corporate DCF Valuation Engine")
    parser.add_argument("--input", "-i", type=str, required=True, help="Path to input JSON file")
    parser.add_argument("--output", "-o", type=str, default=None, help="Path to write JSON output")
    parser.add_argument("--report", "-r", type=str, default=None, help="Path to write Markdown report")
    parser.add_argument("--format", "-f", choices=["json", "markdown"], default="markdown", help="Console output format")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    engine = McKinseyDCFEngine(data)
    results = engine.run_valuation()

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

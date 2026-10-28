"""
M&A Synergy & Transaction Valuation Engine
Compliant with McKinsey M&A framework and Mellen & Evans 'Valuation for M&A'
"""

from typing import List, Dict, Any, Optional

def calculate_ma_synergy(
    standalone_target_value: float,
    standalone_acquirer_value: float,
    cost_synergies: List[float],
    revenue_synergies: List[float],
    operating_margin_on_rev_synergies: float,
    integration_costs: List[float],
    tax_rate: float,
    wacc_cost_synergies: float,
    wacc_rev_synergies: float,
    cost_synergy_probability: float = 0.80,
    revenue_synergy_probability: float = 0.40,
    terminal_synergy_growth: float = 0.02,
    offer_price: Optional[float] = None
) -> Dict[str, Any]:
    """
    Calculates detailed M&A synergy present value, risk-adjusted realization,
    maximum walk-away purchase price, and buyer value creation.
    """
    n_years = len(cost_synergies)
    if len(revenue_synergies) != n_years or len(integration_costs) != n_years:
        raise ValueError("cost_synergies, revenue_synergies, and integration_costs must have the same length.")

    cost_synergy_pv = 0.0
    rev_synergy_pv = 0.0
    integration_cost_pv = 0.0
    yearly_breakdown = []

    for t in range(n_years):
        year = t + 1
        
        # After-tax risk-adjusted cost synergy
        adj_cost_syn = cost_synergies[t] * cost_synergy_probability * (1.0 - tax_rate)
        pv_cost = adj_cost_syn / ((1.0 + wacc_cost_synergies) ** year)
        cost_synergy_pv += pv_cost

        # After-tax risk-adjusted revenue synergy
        adj_rev_syn = (revenue_synergies[t] * operating_margin_on_rev_synergies * 
                       revenue_synergy_probability * (1.0 - tax_rate))
        pv_rev = adj_rev_syn / ((1.0 + wacc_rev_synergies) ** year)
        rev_synergy_pv += pv_rev

        # After-tax integration cost (deductible)
        adj_int_cost = integration_costs[t] * (1.0 - tax_rate)
        pv_int = adj_int_cost / ((1.0 + wacc_cost_synergies) ** year)
        integration_cost_pv += pv_int

        net_synergy_cashflow = adj_cost_syn + adj_rev_syn - adj_int_cost

        yearly_breakdown.append({
            "year": year,
            "cost_synergies_nominal": cost_synergies[t],
            "cost_synergies_risk_adjusted_after_tax": round(adj_cost_syn, 2),
            "revenue_synergies_nominal": revenue_synergies[t],
            "revenue_synergies_risk_adjusted_after_tax": round(adj_rev_syn, 2),
            "integration_costs_after_tax": round(adj_int_cost, 2),
            "net_synergy_cashflow": round(net_synergy_cashflow, 2)
        })

    # Terminal value of ongoing synergies (assuming stabilized cost and revenue synergies in year n)
    terminal_cost_cf = cost_synergies[-1] * cost_synergy_probability * (1.0 - tax_rate) * (1.0 + terminal_synergy_growth)
    terminal_rev_cf = (revenue_synergies[-1] * operating_margin_on_rev_synergies * 
                       revenue_synergy_probability * (1.0 - tax_rate) * (1.0 + terminal_synergy_growth))

    tv_cost = terminal_cost_cf / (wacc_cost_synergies - terminal_synergy_growth)
    tv_rev = terminal_rev_cf / (wacc_rev_synergies - terminal_synergy_growth)

    pv_tv_cost = tv_cost / ((1.0 + wacc_cost_synergies) ** n_years)
    pv_tv_rev = tv_rev / ((1.0 + wacc_rev_synergies) ** n_years)

    total_cost_synergy_value = cost_synergy_pv + pv_tv_cost
    total_rev_synergy_value = rev_synergy_pv + pv_tv_rev
    net_synergies_pv = total_cost_synergy_value + total_rev_synergy_value - integration_cost_pv

    max_purchase_price = standalone_target_value + net_synergies_pv

    result = {
        "standalone_target_value": round(standalone_target_value, 2),
        "pv_cost_synergies": round(total_cost_synergy_value, 2),
        "pv_revenue_synergies": round(total_rev_synergy_value, 2),
        "pv_integration_costs": round(integration_cost_pv, 2),
        "net_synergies_pv": round(net_synergies_pv, 2),
        "max_walkaway_purchase_price": round(max_purchase_price, 2),
        "combined_pro_forma_enterprise_value": round(standalone_acquirer_value + standalone_target_value + net_synergies_pv, 2),
        "yearly_schedule": yearly_breakdown
    }

    if offer_price is not None:
        premium_paid = offer_price - standalone_target_value
        premium_pct = (premium_paid / standalone_target_value) * 100.0 if standalone_target_value > 0 else 0.0
        buyer_value_capture = net_synergies_pv - premium_paid
        target_value_capture = premium_paid

        result["transaction_analysis"] = {
            "offer_price": round(offer_price, 2),
            "premium_paid": round(premium_paid, 2),
            "premium_percent": round(premium_pct, 2),
            "buyer_value_created": round(buyer_value_capture, 2),
            "target_value_captured": round(target_value_capture, 2),
            "deal_verdict": "Value Accretive for Acquirer" if buyer_value_capture > 0 else "Value Destructive (Winner's Curse)"
        }

    return result

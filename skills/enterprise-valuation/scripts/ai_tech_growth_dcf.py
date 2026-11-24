"""
AI, Digital Infrastructure & High-Growth Reverse DCF Engine
Compliant with McKinsey 8th Edition (May 2025/2026) Contemporary Valuation Standards.
"""

import math
from typing import List, Dict, Any, Optional

def calculate_ai_capex_and_depreciation(
    annual_revenues: List[float],
    traditional_capex_pct: float,
    ai_compute_capex_pct: float,
    traditional_useful_life_years: int = 7,
    ai_compute_useful_life_years: int = 3
) -> Dict[str, Any]:
    """
    Models split capital expenditures and accelerated depreciation for AI/GPU compute infrastructure.
    McKinsey 8th Ed highlights that AI hardware depreciates within 2-3 years due to rapid silicon obsolescence.
    """
    n_years = len(annual_revenues)
    schedule = []
    
    # Track capital asset pools
    trad_pool = [0.0] * n_years
    ai_pool = [0.0] * n_years

    for t in range(n_years):
        rev = annual_revenues[t]
        trad_capex = rev * traditional_capex_pct
        ai_capex = rev * ai_compute_capex_pct
        total_capex = trad_capex + ai_capex

        trad_depr = trad_capex / traditional_useful_life_years
        ai_depr = ai_capex / ai_compute_useful_life_years
        total_depr = trad_depr + ai_depr

        schedule.append({
            "year": t + 1,
            "revenue": round(rev, 2),
            "traditional_capex": round(trad_capex, 2),
            "ai_compute_capex": round(ai_capex, 2),
            "total_capex": round(total_capex, 2),
            "traditional_depreciation": round(trad_depr, 2),
            "ai_accelerated_depreciation": round(ai_depr, 2),
            "total_depreciation": round(total_depr, 2),
            "net_capex_impact": round(total_capex - total_depr, 2)
        })

    return {
        "useful_life_assumptions": {
            "traditional_it_years": traditional_useful_life_years,
            "ai_compute_years": ai_compute_useful_life_years
        },
        "annual_schedule": schedule
    }

def reverse_dcf_high_growth(
    current_enterprise_value: float,
    current_revenue: float,
    target_tam: float,
    target_year: int,
    terminal_operating_margin: float,
    terminal_roic: float,
    wacc: float,
    terminal_growth: float,
    corporate_tax_rate: float
) -> Dict[str, Any]:
    """
    Reverse DCF for high-growth tech & AI platforms per McKinsey 8th Ed.
    Starts from current valuation to deduce implied market share and required CAGR.
    """
    if target_year <= 0 or current_revenue <= 0:
        raise ValueError("Target year and current revenue must be positive.")

    # Terminal Key Value Driver Multiple: (1 - g/ROIC) / (WACC - g)
    if terminal_roic <= 0 or wacc <= terminal_growth:
        raise ValueError("Terminal ROIC must be > 0 and WACC must exceed terminal growth.")

    ir = terminal_growth / terminal_roic
    terminal_nopat_multiple = (1.0 - ir) / (wacc - terminal_growth)

    # Discount factor from target year to present
    discount_factor = (1.0 + wacc) ** target_year
    implied_terminal_ev_at_target_year = current_enterprise_value * discount_factor

    # Required NOPAT in target year to justify terminal EV
    required_target_nopat = implied_terminal_ev_at_target_year / terminal_nopat_multiple
    required_target_ebita = required_target_nopat / (1.0 - corporate_tax_rate)
    required_target_revenue = required_target_ebita / terminal_operating_margin

    # Implied CAGR
    implied_cagr = (required_target_revenue / current_revenue) ** (1.0 / target_year) - 1.0

    # Implied Market Share of TAM
    implied_tam_share = (required_target_revenue / target_tam) * 100.0

    # Feasibility check
    feasibility = "Realistic"
    if implied_tam_share > 50.0:
        feasibility = "Highly Unlikely (>50% market monopoly implied)"
    elif implied_tam_share > 25.0:
        feasibility = "Aggressive / Requires Dominant Market Leadership"
    elif implied_cagr > 0.60:
        feasibility = "Speculative (>60% sustained CAGR)"

    return {
        "current_inputs": {
            "current_enterprise_value": round(current_enterprise_value, 2),
            "current_revenue": round(current_revenue, 2),
            "target_tam": round(target_tam, 2),
            "projection_horizon_years": target_year
        },
        "implied_milestones_at_target_year": {
            "required_target_revenue": round(required_target_revenue, 2),
            "required_target_ebita": round(required_target_ebita, 2),
            "required_target_nopat": round(required_target_nopat, 2),
            "implied_revenue_cagr": f"{round(implied_cagr * 100, 2)}%",
            "implied_market_share_of_tam": f"{round(implied_tam_share, 2)}%",
            "feasibility_assessment": feasibility
        },
        "terminal_multiples": {
            "reinvestment_rate_ir": f"{round(ir * 100, 2)}%",
            "terminal_nopat_multiple": round(terminal_nopat_multiple, 2)
        }
    }

def dynamic_wacc_high_rate_environment(
    risk_free_rate: float,
    equity_risk_premium: float,
    unlevered_beta: float,
    pre_tax_cost_of_debt: float,
    corporate_tax_rate: float,
    target_debt_to_capital: float,
    interest_deduction_limit_pct: Optional[float] = None
) -> Dict[str, Any]:
    """
    Calculates cost of capital in a 'Higher-For-Longer' interest rate regime.
    Accounts for interest deductibility limits (e.g. US Sec 163(j) or international EBITDA caps).
    """
    if target_debt_to_capital >= 1.0 or target_debt_to_capital < 0:
        raise ValueError("target_debt_to_capital must be between 0 and 1.")

    debt_weight = target_debt_to_capital
    equity_weight = 1.0 - debt_weight
    debt_to_equity = debt_weight / equity_weight if equity_weight > 0 else 0.0

    # Hamada relevered beta
    levered_beta = unlevered_beta * (1.0 + (1.0 - corporate_tax_rate) * debt_to_equity)

    # Cost of equity (CAPM)
    cost_of_equity = risk_free_rate + (levered_beta * equity_risk_premium)

    # Effective tax shield under high rates
    effective_tax_rate = corporate_tax_rate
    if interest_deduction_limit_pct is not None:
        effective_tax_rate = min(corporate_tax_rate, corporate_tax_rate * interest_deduction_limit_pct)

    after_tax_cost_of_debt = pre_tax_cost_of_debt * (1.0 - effective_tax_rate)

    wacc = (equity_weight * cost_of_equity) + (debt_weight * after_tax_cost_of_debt)

    return {
        "macro_parameters": {
            "risk_free_rate": round(risk_free_rate, 4),
            "equity_risk_premium": round(equity_risk_premium, 4),
            "pre_tax_cost_of_debt": round(pre_tax_cost_of_debt, 4),
            "marginal_tax_rate": round(corporate_tax_rate, 4)
        },
        "capital_structure": {
            "equity_weight": round(equity_weight, 4),
            "debt_weight": round(debt_weight, 4),
            "debt_to_equity_ratio": round(debt_to_equity, 4),
            "levered_beta": round(levered_beta, 4)
        },
        "hurdle_rates": {
            "cost_of_equity": round(cost_of_equity, 4),
            "after_tax_cost_of_debt": round(after_tax_cost_of_debt, 4),
            "calculated_wacc": round(wacc, 4),
            "wacc_percentage": f"{round(wacc * 100, 2)}%"
        }
    }

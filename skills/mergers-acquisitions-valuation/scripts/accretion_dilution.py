"""
M&A Accretion / Dilution & EPS Impact Analysis Engine
Calculates Pro-Forma EPS, Purchase Funding Mix, and Breakeven Synergy Targets.
"""

from typing import Dict, Any

def calculate_accretion_dilution(
    acquirer_share_price: float,
    acquirer_diluted_shares: float,
    acquirer_net_income: float,
    target_purchase_equity_value: float,
    target_net_income: float,
    cash_used: float,
    debt_issued: float,
    stock_issued_value: float,
    cost_of_new_debt_pct: float,
    foregone_interest_on_cash_pct: float,
    marginal_tax_rate: float,
    annual_after_tax_synergies: float = 0.0
) -> Dict[str, Any]:
    """
    Performs full M&A accretion/dilution analysis under variable financing mixes.
    """
    total_funding = cash_used + debt_issued + stock_issued_value
    if abs(total_funding - target_purchase_equity_value) > 1.0:
        raise ValueError(
            f"Funding total ({total_funding}) does not match target equity purchase value ({target_purchase_equity_value})."
        )

    # Standalone Acquirer EPS
    acquirer_eps = acquirer_net_income / acquirer_diluted_shares

    # New Shares Issued
    new_shares_issued = stock_issued_value / acquirer_share_price if acquirer_share_price > 0 else 0.0
    pro_forma_shares = acquirer_diluted_shares + new_shares_issued

    # Financing Costs (After-Tax)
    after_tax_new_interest = (debt_issued * cost_of_new_debt_pct) * (1.0 - marginal_tax_rate)
    after_tax_foregone_cash_interest = (cash_used * foregone_interest_on_cash_pct) * (1.0 - marginal_tax_rate)

    # Pro-Forma Net Income
    pro_forma_net_income = (
        acquirer_net_income
        + target_net_income
        + annual_after_tax_synergies
        - after_tax_new_interest
        - after_tax_foregone_cash_interest
    )

    # Pro-Forma EPS
    pro_forma_eps = pro_forma_net_income / pro_forma_shares if pro_forma_shares > 0 else 0.0
    eps_difference = pro_forma_eps - acquirer_eps
    accretion_pct = (eps_difference / acquirer_eps) * 100.0 if acquirer_eps > 0 else 0.0

    # Required after-tax synergy to break even if dilutive
    target_breakeven_income = (acquirer_eps * pro_forma_shares) - (
        acquirer_net_income + target_net_income - after_tax_new_interest - after_tax_foregone_cash_interest
    )
    breakeven_synergies_needed = max(target_breakeven_income, 0.0)

    return {
        "standalone_acquirer": {
            "share_price": round(acquirer_share_price, 2),
            "shares_outstanding": round(acquirer_diluted_shares, 2),
            "net_income": round(acquirer_net_income, 2),
            "standalone_eps": round(acquirer_eps, 4)
        },
        "transaction_financing": {
            "purchase_equity_value": round(target_purchase_equity_value, 2),
            "cash_used": round(cash_used, 2),
            "cash_pct": f"{round((cash_used / target_purchase_equity_value)*100, 1)}%",
            "new_debt_issued": round(debt_issued, 2),
            "debt_pct": f"{round((debt_issued / target_purchase_equity_value)*100, 1)}%",
            "new_stock_issued_value": round(stock_issued_value, 2),
            "stock_pct": f"{round((stock_issued_value / target_purchase_equity_value)*100, 1)}%",
            "new_shares_issued": round(new_shares_issued, 2),
            "after_tax_financing_drag": round(after_tax_new_interest + after_tax_foregone_cash_interest, 2)
        },
        "pro_forma_results": {
            "pro_forma_net_income": round(pro_forma_net_income, 2),
            "pro_forma_shares": round(pro_forma_shares, 2),
            "pro_forma_eps": round(pro_forma_eps, 4),
            "eps_change_nominal": round(eps_difference, 4),
            "accretion_dilution_percentage": f"{round(accretion_pct, 2)}%",
            "deal_classification": "Accretive" if accretion_pct > 0 else ("Dilutive" if accretion_pct < 0 else "Neutral"),
            "breakeven_after_tax_synergy_required": round(breakeven_synergies_needed, 2)
        }
    }

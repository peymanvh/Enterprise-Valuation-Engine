"""
Distressed Asset & Foreclosure Valuation Engine (Liquidation Waterfall)
Covers Orderly Liquidation Value (OLV), Forced Liquidation Value (FLV), and Priority Recovery.
"""

from typing import Dict, Any, List

DEFAULT_RECOVERY_FACTORS = {
    "cash_and_equivalents": {"olv": 1.00, "flv": 1.00},
    "accounts_receivable": {"olv": 0.80, "flv": 0.60},
    "inventory_raw_materials": {"olv": 0.60, "flv": 0.40},
    "inventory_work_in_progress": {"olv": 0.25, "flv": 0.10},
    "inventory_finished_goods": {"olv": 0.70, "flv": 0.50},
    "machinery_and_equipment": {"olv": 0.60, "flv": 0.35},
    "real_estate_commercial": {"olv": 0.85, "flv": 0.65},
    "vehicles_and_fleet": {"olv": 0.75, "flv": 0.55},
    "intellectual_property_patents": {"olv": 0.30, "flv": 0.10},
    "general_goodwill": {"olv": 0.00, "flv": 0.00}
}

def calculate_liquidation_value(
    assets: Dict[str, float],
    senior_secured_debt: float,
    subordinated_debt: float,
    trade_accounts_payable: float,
    wind_down_admin_costs_pct: float = 0.08,
    employee_severance_tax_liens: float = 0.0,
    custom_recovery_factors: Dict[str, Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Computes Orderly Liquidation Value (OLV) and Forced Liquidation Value (FLV)
    across assets and executes an absolute priority claims waterfall.
    """
    factors = DEFAULT_RECOVERY_FACTORS.copy()
    if custom_recovery_factors:
        for k, v in custom_recovery_factors.items():
            factors[k] = v

    total_book_value = 0.0
    gross_olv = 0.0
    gross_flv = 0.0
    asset_breakdown = []

    for asset_name, book_val in assets.items():
        total_book_value += book_val
        rec = factors.get(asset_name, {"olv": 0.50, "flv": 0.30})
        olv_val = book_val * rec["olv"]
        flv_val = book_val * rec["flv"]
        gross_olv += olv_val
        gross_flv += flv_val

        asset_breakdown.append({
            "asset_name": asset_name,
            "book_value": round(book_val, 2),
            "olv_recovery_pct": f"{round(rec['olv']*100, 1)}%",
            "olv_value": round(olv_val, 2),
            "flv_recovery_pct": f"{round(rec['flv']*100, 1)}%",
            "flv_value": round(flv_val, 2)
        })

    def run_waterfall(gross_proceeds: float):
        admin_expenses = gross_proceeds * wind_down_admin_costs_pct
        net_after_admin = max(gross_proceeds - admin_expenses, 0.0)

        # Priority taxes & employee claims
        paid_priority_claims = min(net_after_admin, employee_severance_tax_liens)
        rem_after_priority = max(net_after_admin - paid_priority_claims, 0.0)

        # Senior secured debt
        paid_senior = min(rem_after_priority, senior_secured_debt)
        rem_after_senior = max(rem_after_priority - paid_senior, 0.0)

        # Subordinated debt
        paid_sub = min(rem_after_senior, subordinated_debt)
        rem_after_sub = max(rem_after_senior - paid_sub, 0.0)

        # General unsecured (trade payables)
        paid_trade = min(rem_after_sub, trade_accounts_payable)
        rem_for_equity = max(rem_after_sub - paid_trade, 0.0)

        return {
            "gross_proceeds": round(gross_proceeds, 2),
            "wind_down_admin_costs": round(admin_expenses, 2),
            "net_distributable_cash": round(net_after_admin, 2),
            "priority_claims_paid": round(paid_priority_claims, 2),
            "priority_recovery_pct": round((paid_priority_claims / employee_severance_tax_liens * 100) if employee_severance_tax_liens else 100.0, 1),
            "senior_debt_paid": round(paid_senior, 2),
            "senior_recovery_pct": round((paid_senior / senior_secured_debt * 100) if senior_secured_debt else 100.0, 1),
            "subordinated_debt_paid": round(paid_sub, 2),
            "subordinated_recovery_pct": round((paid_sub / subordinated_debt * 100) if subordinated_debt else 100.0, 1),
            "trade_payables_paid": round(paid_trade, 2),
            "trade_recovery_pct": round((paid_trade / trade_accounts_payable * 100) if trade_accounts_payable else 100.0, 1),
            "residual_equity_recovery": round(rem_for_equity, 2)
        }

    return {
        "summary": {
            "total_assets_book_value": round(total_book_value, 2),
            "gross_orderly_liquidation_value": round(gross_olv, 2),
            "gross_forced_liquidation_value": round(gross_flv, 2),
            "olv_discount_from_book": f"{round((1.0 - gross_olv / total_book_value) * 100, 2)}%" if total_book_value else "0%",
            "flv_discount_from_book": f"{round((1.0 - gross_flv / total_book_value) * 100, 2)}%" if total_book_value else "0%"
        },
        "orderly_liquidation_waterfall": run_waterfall(gross_olv),
        "forced_liquidation_waterfall": run_waterfall(gross_flv),
        "asset_breakdown": asset_breakdown
    }

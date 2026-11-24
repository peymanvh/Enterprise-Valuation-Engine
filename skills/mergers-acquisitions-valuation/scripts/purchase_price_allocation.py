"""
Purchase Price Allocation (PPA) Engine under ASC 805 / IFRS 3
Calculates Fair Value Step-Up, Deferred Tax Liabilities (DTL), and Residual Goodwill.
"""

from typing import Dict, Any, List, Optional

def calculate_purchase_price_allocation(
    cash_paid: float,
    stock_value_transferred: float,
    debt_assumed: float,
    contingent_earnout_fair_value: float,
    book_value_tangible_assets: float,
    fair_value_step_up_tangibles: float,
    book_value_liabilities_assumed: float,
    identified_intangibles: Dict[str, float],
    marginal_tax_rate: float,
    transaction_structure_is_asset_deal: bool = False
) -> Dict[str, Any]:
    """
    Executes ASC 805 / IFRS 3 Purchase Price Allocation:
    Goodwill = Purchase Consideration - Fair Value of Net Identifiable Assets
    
    If transaction is a stock purchase, fair value step-up creates a Deferred Tax Liability (DTL).
    In an asset purchase (or 338(h)(10) election), step-up is deductible and DTL = 0.
    """
    # 1. Total Consideration Transferred
    total_consideration = cash_paid + stock_value_transferred + contingent_earnout_fair_value

    # 2. Fair Value of Tangible Assets
    fv_tangible_assets = book_value_tangible_assets + fair_value_step_up_tangibles

    # 3. Total Fair Value of Identified Intangible Assets
    total_identified_intangibles = sum(identified_intangibles.values())

    # 4. Total Gross Fair Value of Assets Acquired (excluding goodwill)
    gross_acquired_assets = fv_tangible_assets + total_identified_intangibles

    # 5. Deferred Tax Liability (DTL) on Step-Up (Applicable to stock sales)
    total_step_up = fair_value_step_up_tangibles + total_identified_intangibles
    if transaction_structure_is_asset_deal:
        dtl_created = 0.0
    else:
        dtl_created = max(total_step_up * marginal_tax_rate, 0.0)

    # 6. Total Net Identifiable Assets at Fair Value
    total_liabilities_recognized = book_value_liabilities_assumed + debt_assumed + dtl_created
    net_identifiable_assets = gross_acquired_assets - total_liabilities_recognized

    # 7. Residual Goodwill (or Bargain Purchase Gain)
    residual_goodwill = total_consideration - net_identifiable_assets

    bargain_purchase_gain = 0.0
    recorded_goodwill = 0.0

    if residual_goodwill >= 0:
        recorded_goodwill = residual_goodwill
    else:
        bargain_purchase_gain = abs(residual_goodwill)

    return {
        "consideration_summary": {
            "cash_consideration": round(cash_paid, 2),
            "stock_consideration": round(stock_value_transferred, 2),
            "contingent_earnout_fv": round(contingent_earnout_fair_value, 2),
            "total_purchase_consideration": round(total_consideration, 2)
        },
        "balance_sheet_allocation": {
            "book_tangible_assets": round(book_value_tangible_assets, 2),
            "tangible_step_up": round(fair_value_step_up_tangibles, 2),
            "total_fair_value_tangible_assets": round(fv_tangible_assets, 2),
            "identified_intangibles": {k: round(v, 2) for k, v in identified_intangibles.items()},
            "total_identified_intangibles": round(total_identified_intangibles, 2),
            "total_gross_assets_excluding_goodwill": round(gross_acquired_assets, 2),
            "book_liabilities_assumed": round(book_value_liabilities_assumed, 2),
            "debt_assumed": round(debt_assumed, 2),
            "deferred_tax_liability_dtl": round(dtl_created, 2),
            "net_identifiable_assets_acquired": round(net_identifiable_assets, 2)
        },
        "goodwill_result": {
            "recorded_goodwill": round(recorded_goodwill, 2),
            "bargain_purchase_gain": round(bargain_purchase_gain, 2),
            "goodwill_as_pct_of_consideration": f"{round((recorded_goodwill / total_consideration) * 100, 2)}%" if total_consideration else "0%",
            "accounting_treatment": "Goodwill Capitalized under ASC 805 / IFRS 3" if recorded_goodwill > 0 else "Bargain Purchase Gain (Recognized in P&L)"
        }
    }

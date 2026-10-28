"""
Unit Tests for M&A, Private Company Valuation, Synergies, and Distressed Assets
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../skills/mergers-acquisitions-valuation/scripts")))

from ma_synergy_valuation import calculate_ma_synergy
from private_dlom_dloc import calculate_dloc, chaffe_put_option_dlom, calculate_levels_of_value
from distressed_asset_liquidation import calculate_liquidation_value
from accretion_dilution import calculate_accretion_dilution

class TestMAValuation(unittest.TestCase):

    def test_ma_synergy_calculation(self):
        result = calculate_ma_synergy(
            standalone_target_value=100.0,
            standalone_acquirer_value=500.0,
            cost_synergies=[10.0, 10.0],
            revenue_synergies=[10.0, 10.0],
            operating_margin_on_rev_synergies=0.20,
            integration_costs=[5.0, 2.0],
            tax_rate=0.25,
            wacc_cost_synergies=0.10,
            wacc_rev_synergies=0.12,
            cost_synergy_probability=0.80,
            revenue_synergy_probability=0.50,
            terminal_synergy_growth=0.02,
            offer_price=120.0
        )
        self.assertGreater(result["pv_cost_synergies"], 0)
        self.assertGreater(result["pv_revenue_synergies"], 0)
        self.assertGreater(result["net_synergies_pv"], 0)
        self.assertEqual(result["max_walkaway_purchase_price"], 100.0 + result["net_synergies_pv"])
        self.assertIn("transaction_analysis", result)
        self.assertEqual(result["transaction_analysis"]["premium_paid"], 20.0)

    def test_dloc_and_levels_of_value(self):
        # 30% control premium -> DLOC = 1 - 1/1.30 = 23.08%
        dloc = calculate_dloc(0.30)
        self.assertAlmostEqual(dloc, 0.230769, places=4)

        levels = calculate_levels_of_value(
            controlling_marketable_value=100.0,
            control_premium=0.30,
            volatility=0.40,
            time_to_liquidity_years=2.0,
            risk_free_rate=0.045,
            strategic_synergy_value=25.0
        )
        val = levels["levels_of_value"]
        # Verify Level 1 >= Level 2 >= Level 3 >= Level 4 >= Level 5
        self.assertGreaterEqual(val["1_synergistic_strategic_value"], val["2_controlling_interest_marketable_value"])
        self.assertGreaterEqual(val["2_controlling_interest_marketable_value"], val["3_controlling_interest_non_marketable_value"])
        self.assertGreaterEqual(val["3_controlling_interest_non_marketable_value"], val["4_minority_interest_marketable_value"])
        self.assertGreaterEqual(val["4_minority_interest_marketable_value"], val["5_minority_interest_non_marketable_value"])

    def test_distressed_liquidation_waterfall(self):
        assets = {
            "cash_and_equivalents": 10.0,
            "accounts_receivable": 20.0,
            "machinery_and_equipment": 50.0
        }
        res = calculate_liquidation_value(
            assets=assets,
            senior_secured_debt=30.0,
            subordinated_debt=20.0,
            trade_accounts_payable=20.0,
            wind_down_admin_costs_pct=0.10,
            employee_severance_tax_liens=5.0
        )
        summary = res["summary"]
        self.assertEqual(summary["total_assets_book_value"], 80.0)
        self.assertGreater(summary["gross_orderly_liquidation_value"], summary["gross_forced_liquidation_value"])
        
        olv_waterfall = res["orderly_liquidation_waterfall"]
        self.assertGreater(olv_waterfall["net_distributable_cash"], 0)
        self.assertGreaterEqual(olv_waterfall["priority_recovery_pct"], 100.0)

    def test_accretion_dilution(self):
        res = calculate_accretion_dilution(
            acquirer_share_price=50.0,
            acquirer_diluted_shares=10.0, # Net Income = 20.0 -> EPS = 2.0
            acquirer_net_income=20.0,
            target_purchase_equity_value=60.0,
            target_net_income=6.0,
            cash_used=20.0,
            debt_issued=20.0,
            stock_issued_value=20.0, # 20 / 50 = 0.4 new shares -> total 10.4 shares
            cost_of_new_debt_pct=0.06,
            foregone_interest_on_cash_pct=0.04,
            marginal_tax_rate=0.25,
            annual_after_tax_synergies=2.0
        )
        self.assertEqual(res["standalone_acquirer"]["standalone_eps"], 2.0)
        self.assertIn("deal_classification", res["pro_forma_results"])
        self.assertIn(res["pro_forma_results"]["deal_classification"], ["Accretive", "Dilutive", "Neutral"])

if __name__ == "__main__":
    unittest.main()

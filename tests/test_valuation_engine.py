#!/usr/bin/env python3
"""
test_valuation_engine.py - Automated Institutional Test Suite
Verifies mathematical precision across McKinsey DCF, Damodaran Risk Bridge,
VC & Startup Economics, UNIDO Project Feasibility, and Patent Real Options.
"""

import sys
import os
import math
import unittest
import json

# Add scripts directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "skills", "enterprise-valuation", "scripts")))

from dcf_mckinsey import McKinseyDCFEngine
from multiples_valuation import MultiplesValuationEngine, harmonic_mean, linear_regression
from startup_venture import StartupVentureEngine
from commercial_project import CommercialProjectEngine, compute_npv, compute_irr, compute_mirr
from ip_patent_val import IPPatentValuationEngine, black_scholes_call, norm_cdf
from monte_carlo_simulator import MonteCarloValuationSimulator, percentile
from mna_deal_valuation import MNADealValuationEngine
from ai_tech_valuation import AITechValuationEngine

class TestMcKinseyDCFEngine(unittest.TestCase):
    def setUp(self):
        self.sample_data = {
            "company_name": "TestCorp",
            "currency": "USD",
            "initial_invested_capital": 1000.0,
            "assumptions": {
                "cost_of_equity": 0.10,
                "pre_tax_cost_of_debt": 0.05,
                "tax_rate": 0.20,
                "market_equity_weight": 0.80,
                "market_debt_weight": 0.20,
                "terminal_growth_rate": 0.02,
                "terminal_roic": 0.15,
                "long_term_gdp_growth": 0.03,
                "risk_free_rate": 0.04,
                "discounting_convention": "end_of_year",
                "economic_moat": "wide",
                "margin_of_safety": 0.25,
                "probability_of_distress": 0.05,
                "distress_liquidation_recovery_rate": 0.40
            },
            "balance_sheet_bridge": {
                "cash_and_marketable_securities": 100.0,
                "non_operating_assets": 50.0,
                "total_debt": 300.0,
                "operating_lease_liabilities": 50.0,
                "pension_deficits": 20.0,
                "contingent_litigation_liabilities": 10.0,
                "minority_interests": 15.0,
                "shares_outstanding": 100.0
            },
            "forecasts": [
                {
                    "year": 2027,
                    "revenue": 2000.0,
                    "ebit": 300.0,
                    "tax_rate": 0.20,
                    "depreciation_amortization": 80.0,
                    "capex": 100.0,
                    "change_in_nwc": 20.0,
                    "invested_capital": 1040.0
                },
                {
                    "year": 2028,
                    "revenue": 2200.0,
                    "ebit": 330.0,
                    "tax_rate": 0.20,
                    "depreciation_amortization": 90.0,
                    "capex": 110.0,
                    "change_in_nwc": 25.0,
                    "invested_capital": 1085.0
                }
            ]
        }
        self.engine = McKinseyDCFEngine(self.sample_data)

    def test_wacc_calculation(self):
        # WACC = 0.8 * 0.10 + 0.2 * 0.05 * (1 - 0.20) = 0.08 + 0.008 = 0.088 (8.8%)
        wacc = self.engine.calculate_wacc()
        self.assertAlmostEqual(wacc, 0.088, places=5)

    def test_key_value_driver_and_equity_bridge(self):
        res = self.engine.run_valuation()
        wacc = res["wacc"]
        self.assertAlmostEqual(wacc, 0.088, places=5)
        
        # Verify terminal value formula: NOPAT_{T+1} * (1 - g/ROIC) / (WACC - g)
        last_nopat = res["forecast_periods"][-1]["nopat"]
        g = 0.02
        roic_t = 0.15
        nopat_t_plus_1 = last_nopat * (1.0 + g)
        expected_tv = (nopat_t_plus_1 * (1.0 - (g / roic_t))) / (wacc - g)
        self.assertAlmostEqual(res["terminal_value"], expected_tv, places=2)

        # Verify Equity Value Bridge:
        # Adjusted EV + Cash(100) + Non-op(50) - Debt(300) - Leases(50) - Pension(20) - Litigation(10) - Minority(15)
        adj_ev = res["distress_adjusted_enterprise_value"]
        expected_equity = adj_ev + 100.0 + 50.0 - 300.0 - 50.0 - 20.0 - 10.0 - 15.0
        self.assertAlmostEqual(res["equity_value"], expected_equity, places=2)
        self.assertAlmostEqual(res["equity_value_per_share"], expected_equity / 100.0, places=2)

    def test_buffett_moat_fade_and_margin_of_safety(self):
        # Test zero moat: terminal ROIC must collapse to WACC
        no_moat_data = dict(self.sample_data)
        no_moat_data["assumptions"] = dict(self.sample_data["assumptions"])
        no_moat_data["assumptions"]["economic_moat"] = "none"
        engine_no_moat = McKinseyDCFEngine(no_moat_data)
        res = engine_no_moat.run_valuation()
        self.assertAlmostEqual(res["terminal_roic"], res["wacc"], places=4)
        
        # Verify Margin of Safety discount (25%)
        b_metrics = res["buffett_owner_earnings_metrics"]
        self.assertAlmostEqual(b_metrics["margin_of_safety_percentage"], 0.25, places=2)
        self.assertAlmostEqual(b_metrics["buffett_margin_of_safety_equity_value"], res["equity_value"] * 0.75, places=2)

class TestMultiplesEngine(unittest.TestCase):
    def test_harmonic_mean(self):
        # Values: 10.0, 20.0 -> Harmonic Mean = 2 / (1/10 + 1/20) = 2 / (0.15) = 13.3333
        vals = [10.0, 20.0]
        h_mean = harmonic_mean(vals)
        self.assertAlmostEqual(h_mean, 13.333333, places=4)
        # Arithmetic mean would be 15.0 (overstating multiple by 12.5%)
        self.assertTrue(h_mean < sum(vals) / len(vals))

    def test_linear_regression(self):
        # Y = 2X + 1
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        y = [3.0, 5.0, 7.0, 9.0, 11.0]
        reg = linear_regression(x, y)
        self.assertIsNotNone(reg)
        self.assertAlmostEqual(reg["slope"], 2.0, places=5)
        self.assertAlmostEqual(reg["intercept"], 1.0, places=5)
        self.assertAlmostEqual(reg["r_squared"], 1.0, places=5)

class TestStartupVentureEngine(unittest.TestCase):
    def setUp(self):
        self.data = {
            "startup_name": "TestSeed",
            "currency": "USD",
            "vc_method": {
                "investment_amount": 1000000.0,
                "horizon_years": 5.0,
                "target_irr": 0.40,
                "target_moic": 0.0,  # auto-computed: (1+0.4)^5 = 5.37824
                "terminal_exit_value": 50000000.0,
                "future_dilution_rounds": [0.20]  # retention = 0.80
            },
            "scorecard_method": {
                "benchmark_pre_money": 3000000.0,
                "factors": {
                    "management": {"weight": 0.50, "score": 1.20},
                    "market": {"weight": 0.50, "score": 1.10}
                }
            },
            "berkus_method": {
                "sound_idea": 500000.0,
                "prototype": 500000.0,
                "quality_management_team": 500000.0,
                "strategic_relationships": 250000.0,
                "product_rollout_or_sales": 250000.0
            },
            "saas_metrics": {
                "arr": 1200000.0,
                "mrr": 100000.0,
                "arpu_annual": 1200.0,
                "gross_margin": 0.80,
                "annual_churn_rate": 0.08,
                "cac": 3000.0,
                "net_revenue_retention": 1.15,
                "yoy_growth_rate": 0.50,
                "fcf_margin": 0.10,
                "quarterly_arr_delta": 100000.0,
                "prev_quarter_sm_spend": 100000.0
            }
        }
        self.engine = StartupVentureEngine(self.data)

    def test_vc_method_math(self):
        vc = self.engine.run_vc_method()
        target_moic = math.pow(1.40, 5)
        self.assertAlmostEqual(vc["target_moic"], target_moic, places=4)
        # Required exit ownership = (1M * 5.37824) / 50M = 10.7565%
        req_exit = (1000000.0 * target_moic) / 50000000.0
        self.assertAlmostEqual(vc["required_exit_ownership"], req_exit, places=5)
        # Current ownership = req_exit / 0.80
        req_curr = req_exit / 0.80
        self.assertAlmostEqual(vc["required_current_ownership"], req_curr, places=5)
        # Post money = 1M / req_curr
        expected_post = 1000000.0 / req_curr
        self.assertAlmostEqual(vc["post_money_valuation"], expected_post, places=2)
        self.assertAlmostEqual(vc["pre_money_valuation"], expected_post - 1000000.0, places=2)

    def test_saas_metrics(self):
        s = self.engine.analyze_saas_metrics()
        # LTV = (1200 * 0.80) / 0.08 = 960 / 0.08 = 12,000
        self.assertAlmostEqual(s["ltv"], 12000.0, places=2)
        # LTV/CAC = 12000 / 3000 = 4.0x
        self.assertAlmostEqual(s["ltv_to_cac_ratio"], 4.0, places=2)
        # Rule of 40: 50% + 10% = 60%
        self.assertAlmostEqual(s["rule_of_40_score"], 60.0, places=2)

class TestUNIDOCommercialProject(unittest.TestCase):
    def test_npv_and_irr(self):
        # Initial: -100, Year 1: 50, Year 2: 70
        # At 10%: NPV = -100 + 50/1.1 + 70/1.21 = -100 + 45.4545 + 57.8512 = 3.3058
        cfs = [-100.0, 50.0, 70.0]
        npv_val = compute_npv(0.10, cfs)
        self.assertAlmostEqual(npv_val, 3.305785, places=4)

        irr_val = compute_irr(cfs)
        self.assertIsNotNone(irr_val)
        # Confirm NPV at IRR is zero
        npv_at_irr = compute_npv(irr_val, cfs)
        self.assertAlmostEqual(npv_at_irr, 0.0, places=4)

    def test_mirr(self):
        cfs = [-100.0, 50.0, 70.0]
        mirr_val = compute_mirr(cfs, 0.10, 0.10)
        self.assertIsNotNone(mirr_val)
        # FV(pos) = 50 * 1.1 + 70 = 125. PV(neg) = 100. (125/100)^(1/2) - 1 = sqrt(1.25) - 1 = 11.803%
        self.assertAlmostEqual(mirr_val, math.sqrt(1.25) - 1.0, places=5)

class TestIPPatentValuation(unittest.TestCase):
    def test_black_scholes_call(self):
        # Known benchmark test:
        # S = 100, K = 100, T = 1, r = 0.05, sigma = 0.20
        # Standard BS Call value is approx 10.4506
        res = black_scholes_call(s=100.0, k=100.0, t=1.0, r=0.05, sigma=0.20)
        self.assertAlmostEqual(res["call_value"], 10.4506, places=3)
        self.assertAlmostEqual(res["intrinsic_value"], 0.0, places=3)
        self.assertAlmostEqual(res["time_value"], res["call_value"], places=3)

    def test_norm_cdf(self):
        # N(0) = 0.5, N(1.96) ~ 0.975
        self.assertAlmostEqual(norm_cdf(0.0), 0.5, places=5)
        self.assertAlmostEqual(norm_cdf(1.96), 0.975002, places=4)

class TestMonteCarloPercentile(unittest.TestCase):
    def test_percentile(self):
        data = list(range(1, 101))  # 1 to 100
        p50 = percentile(data, 0.50)
        self.assertAlmostEqual(p50, 50.5, places=2)
        p10 = percentile(data, 0.10)
        self.assertAlmostEqual(p10, 10.9, places=2)

class TestMNADealValuation(unittest.TestCase):
    def setUp(self):
        self.data = {
            "deal_name": "Test M&A Deal",
            "currency": "USD",
            "target_standalone_equity_value": 100.0,
            "target_shares_outstanding": 10.0,
            "target_wacc": 0.10,
            "tax_rate": 0.20,
            "acquisition_premium_percentage": 0.20,
            "synergies": [
                {
                    "name": "Cost Synergy",
                    "category": "cost",
                    "annual_amounts": [10.0, 10.0],
                    "discount_rate_premium": 0.0
                }
            ],
            "integration_costs": [
                {
                    "name": "Integration",
                    "annual_cash_outlays": [2.0]
                }
            ],
            "purchase_price_allocation": {
                "target_book_value_net_assets": 50.0,
                "tangible_assets_fair_value_step_up": 10.0,
                "identifiable_intangibles": {
                    "patents": 20.0
                }
            }
        }
        self.engine = MNADealValuationEngine(self.data)

    def test_mna_value_creation_and_ppa(self):
        res = self.engine.evaluate_deal()
        # Offer price = 100 * (1 + 0.20) = 120.0
        self.assertAlmostEqual(res["actual_offer_price"], 120.0, places=2)
        self.assertAlmostEqual(res["dollar_premium_paid"], 20.0, places=2)
        # Max purchase price = Standalone (100) + Net Synergies
        self.assertAlmostEqual(res["maximum_purchase_price"], 100.0 + res["value_creation"]["net_pv_synergies"], places=2)
        # Value created for acquirer = Net Synergies - Premium Paid (20.0)
        self.assertAlmostEqual(res["value_creation"]["net_value_created_for_acquirer"], res["value_creation"]["net_pv_synergies"] - 20.0, places=2)

        # PPA: Net Identifiable Assets = 50 (book) + 10 (step-up) + 20 (patents) = 80.0
        # Goodwill = 120 (offer) - 80 = 40.0
        ppa = res["purchase_price_allocation_ifrs3"]
        self.assertAlmostEqual(ppa["fair_value_net_identifiable_assets"], 80.0, places=2)
        self.assertAlmostEqual(ppa["residual_goodwill"], 40.0, places=2)

class TestAITechValuation(unittest.TestCase):
    def setUp(self):
        self.data = {
            "company_name": "Test AI",
            "currency": "USD",
            "ai_unit_economics": {
                "monthly_active_users": 100000.0,
                "queries_per_user_month": 10.0,
                "avg_tokens_per_query": 1000.0,
                "revenue_per_million_tokens": 10.0,
                "inference_cost_per_million_tokens": 4.0,
                "gpu_utilization_rate": 0.80
            },
            "compute_and_gpu_capex": {
                "annual_gpu_capex": 30.0,
                "gpu_economic_life_years": 3.0,
                "traditional_server_life_years": 5.0
            },
            "debt_rollover_stress_test": {
                "total_debt": 100.0,
                "debt_maturing_next_2_years": 60.0,
                "historical_interest_rate": 0.03,
                "new_refinancing_interest_rate": 0.08,
                "annual_ebit": 20.0
            }
        }
        self.engine = AITechValuationEngine(self.data)

    def test_ai_economics_and_depreciation(self):
        res = self.engine.evaluate_all()
        ai = res["ai_unit_economics"]
        # Gross margin = (10 - 4) / 10 = 60%
        self.assertAlmostEqual(ai["token_gross_margin"], 0.60, places=3)

        # GPU depreciation: 30 / 3 = 10 per year vs 30 / 5 = 6 per year -> EBIT drag = 4
        comp = res["compute_and_gpu_depreciation"]
        self.assertAlmostEqual(comp["annual_gpu_depreciation"], 10.0, places=2)
        self.assertAlmostEqual(comp["annual_ebit_depreciation_drag"], 4.0, places=2)

        # Debt rollover: 40 unmatured @ 3% (1.2) + 60 @ 8% (4.8) = 6.0 interest
        # Original: 100 @ 3% = 3.0 -> incremental interest = 3.0
        # Post-rollover ICR = 20 / 6.0 = 3.333x
        roll = res["debt_rollover_stress_test"]
        self.assertAlmostEqual(roll["post_rollover_annual_interest"], 6.0, places=2)
        self.assertAlmostEqual(roll["incremental_annual_cash_drain"], 3.0, places=2)
        self.assertAlmostEqual(roll["post_rollover_interest_coverage_ratio"], 20.0 / 6.0, places=3)

if __name__ == "__main__":
    unittest.main()

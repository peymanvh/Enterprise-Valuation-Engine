"""
Private Company Valuation Engine: DLOM, DLOC & Five Levels of Value
Based on Chris M. Mellen & Frank C. Evans ('Valuation for M&A: Building and Measuring Private Company Value')
"""

import math
from typing import Dict, Any, Optional

def norm_cdf(x: float) -> float:
    """Standard normal cumulative distribution function (Abramowitz & Stegun approximation)."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

def calculate_dloc(control_premium: float) -> float:
    """
    Calculates Discount for Lack of Control (DLOC) from Control Premium.
    Formula: DLOC = 1 - (1 / (1 + CP))
    """
    if control_premium < 0:
        raise ValueError("Control premium must be non-negative.")
    return 1.0 - (1.0 / (1.0 + control_premium))

def chaffe_put_option_dlom(volatility: float, time_to_liquidity: float, risk_free_rate: float) -> float:
    """
    Estimates DLOM using Chaffe European At-The-Money Put Option Model:
    DLOM = P / S where S = K = 1.
    """
    if time_to_liquidity <= 0 or volatility <= 0:
        return 0.0
    
    s = 1.0
    k = 1.0
    t = time_to_liquidity
    r = risk_free_rate
    sigma = volatility

    d1 = (math.log(s / k) + (r + 0.5 * sigma ** 2) * t) / (sigma * math.sqrt(t))
    d2 = d1 - sigma * math.sqrt(t)

    put_price = k * math.exp(-r * t) * norm_cdf(-d2) - s * norm_cdf(-d1)
    dlom = min(max(put_price / s, 0.0), 0.90)  # Bound reasonably
    return dlom

def calculate_levels_of_value(
    controlling_marketable_value: float,
    control_premium: float = 0.30,
    dlom_rate: Optional[float] = None,
    volatility: float = 0.40,
    time_to_liquidity_years: float = 2.0,
    risk_free_rate: float = 0.045,
    strategic_synergy_value: float = 0.0
) -> Dict[str, Any]:
    """
    Generates the Mellen & Evans 5 Levels of Value hierarchy:
    1. Synergistic / Strategic Value
    2. Controlling Interest Marketable
    3. Controlling Interest Non-Marketable (Private control)
    4. Minority Interest Marketable (Public minority)
    5. Minority Interest Non-Marketable (Private minority)
    """
    dloc = calculate_dloc(control_premium)
    
    if dlom_rate is None:
        dlom = chaffe_put_option_dlom(volatility, time_to_liquidity_years, risk_free_rate)
    else:
        dlom = dlom_rate

    # 1. Synergistic Value
    synergistic_value = controlling_marketable_value + strategic_synergy_value

    # 2. Controlling Marketable Value
    ctrl_marketable = controlling_marketable_value

    # 3. Controlling Non-Marketable Value (subject to partial DLOM for private controlling ownership illiquidity, typically 5-15%)
    ctrl_dlom = dlom * 0.40 # Controlling owners have power to force liquidation/sale, reducing illiquidity penalty
    ctrl_non_marketable = ctrl_marketable * (1.0 - ctrl_dlom)

    # 4. Minority Marketable Value (freely traded equivalent)
    minority_marketable = ctrl_marketable * (1.0 - dloc)

    # 5. Minority Non-Marketable Value (private minority subjected to both DLOC and DLOM)
    minority_non_marketable = minority_marketable * (1.0 - dlom)

    return {
        "inputs": {
            "control_premium": round(control_premium, 4),
            "calculated_dloc": round(dloc, 4),
            "dlom_rate": round(dlom, 4),
            "dlom_model": "Custom Input" if dlom_rate is not None else "Chaffe Put Option Model",
            "volatility": volatility,
            "time_to_liquidity_years": time_to_liquidity_years,
            "risk_free_rate": risk_free_rate
        },
        "levels_of_value": {
            "1_synergistic_strategic_value": round(synergistic_value, 2),
            "2_controlling_interest_marketable_value": round(ctrl_marketable, 2),
            "3_controlling_interest_non_marketable_value": round(ctrl_non_marketable, 2),
            "4_minority_interest_marketable_value": round(minority_marketable, 2),
            "5_minority_interest_non_marketable_value": round(minority_non_marketable, 2)
        },
        "per_share_indicators": {
            "dloc_percentage": f"{round(dloc * 100, 2)}%",
            "dlom_percentage": f"{round(dlom * 100, 2)}%",
            "total_combined_discount_minority_private": f"{round((1.0 - (1.0 - dloc) * (1.0 - dlom)) * 100, 2)}%"
        }
    }

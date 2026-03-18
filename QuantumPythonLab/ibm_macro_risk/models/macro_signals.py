import numpy as np

# ============================================
# VIX VOLATILITY REGIME DETECTION
# ============================================

def detect_vix_regime(returns):

    if "VIX" not in returns.columns:
        return "unknown", 0

    vix_vol = returns["VIX"].std() * np.sqrt(252)

    if vix_vol < 0.15:
        regime = "low_vol"
    elif vix_vol < 0.30:
        regime = "normal_vol"
    else:
        regime = "crisis_vol"

    return regime, vix_vol


# ============================================
# OIL SHOCK PROPAGATION
# ============================================

def oil_shock_index(returns):

    if "Oil" not in returns.columns:
        return 0

    oil_vol = returns["Oil"].std() * np.sqrt(252)
    oil_trend = returns["Oil"].mean()

    shock = oil_vol * 0.6 + abs(oil_trend) * 0.4

    return shock


# ============================================
# FED LIQUIDITY PROXY
# MOVE = Treasury volatility
# ============================================

def fed_liquidity_proxy(returns):

    if "MOVE" not in returns.columns:
        return 0

    move_vol = returns["MOVE"].std()

    # High MOVE = tightening
    liquidity = -move_vol

    return liquidity

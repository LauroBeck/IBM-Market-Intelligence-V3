import numpy as np
import pandas as pd

def compute_global_liquidity_index(returns):

    weights = {
        "USD_CNY": -0.2,
        "USD_KRW": -0.2,
        "Gold": 0.2,
        "Silver": 0.1,
        "Copper": 0.4,
        "Platinum": 0.1
    }

    factors = []

    for asset, w in weights.items():
        if asset in returns.columns:
            factors.append(returns[asset].mean() * w)

    gli = np.sum(factors)

    return gli

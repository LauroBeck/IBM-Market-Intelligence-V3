import numpy as np

def compute_fed_liquidity(returns):

    move = returns["MOVE"].tail(5).mean()

    yield_curve = returns["US10Y"] - returns["US2Y"]

    liquidity = -move + yield_curve

    return liquidity

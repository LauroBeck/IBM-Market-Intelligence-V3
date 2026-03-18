import numpy as np

def compute_oil_shock(returns):

    oil_vol = returns["Oil"].std() * np.sqrt(252)

    oil_momentum = returns["Oil"].tail(10).mean()

    shock = oil_vol * oil_momentum

    return shock

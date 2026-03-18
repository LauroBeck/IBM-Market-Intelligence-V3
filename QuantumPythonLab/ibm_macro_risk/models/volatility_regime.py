import numpy as np

def detect_vix_regime(returns):

    vix_series = returns["VIX"].rolling(20).std() * np.sqrt(252)

    latest_vol = vix_series.iloc[-1]

    if latest_vol < 0.15:
        regime = "LOW_VOL"

    elif latest_vol < 0.30:
        regime = "NORMAL_VOL"

    else:
        regime = "CRISIS_VOL"

    return regime, latest_vol

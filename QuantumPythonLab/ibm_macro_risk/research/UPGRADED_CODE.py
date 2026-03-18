import numpy as np
import pandas as pd
import yfinance as yf

# =========================
# MARKET DATA
# =========================

def load_market_data():

    tickers = {
        "MSCI_Asia": "AAXJ",
        "SP500": "^GSPC",
        "NASDAQ": "^IXIC",
        "DOW": "^DJI",
        "Gold": "GC=F",
        "Copper": "HG=F",
        "USD_CNY": "CNY=X"
    }

    raw = yf.download(list(tickers.values()),
                      period="1y",
                      auto_adjust=True,
                      progress=False)

    if isinstance(raw.columns, pd.MultiIndex):
        data = raw["Close"]
    else:
        data = raw

    data.columns = tickers.keys()
    data = data.ffill()

    returns = data.pct_change().dropna()

    return data, returns


# =========================
# RISK SCORE
# =========================

def compute_risk_score(returns):

    latest = returns.iloc[-1]

    score = 0

    if latest["MSCI_Asia"] > 0:
        score += 1

    us_avg = np.mean([latest["SP500"],
                      latest["NASDAQ"],
                      latest["DOW"]])

    if latest["MSCI_Asia"] > 0 and us_avg < 0:
        score += 1

    if latest["Gold"] > 0 and latest["Copper"] > 0:
        score += 1

    return score


# =========================
# ADVANCED SOVEREIGN MODEL
# =========================

def sovereign_model(risk_score, returns):

    simulations = 10000
    maturity = 5

    # Initial conditions
    debt_ratio_start = 0.85
    base_gdp = 0.04

    short_rate = 0.04
    long_rate = 0.05

    # GDP adjustment from risk regime
    adjustment_map = {
        0: -0.02,
        1: -0.01,
        2: 0.005,
        3: 0.015
    }

    gdp_drift = base_gdp + adjustment_map[risk_score]

    # Commodity beta (Copper)
    copper_beta = 0.3
    copper_vol = returns["Copper"].std() * np.sqrt(252)

    # Volatilities
    gdp_vol = 0.02
    short_vol = 0.015
    long_vol = 0.02

    # Correlation: GDP ↔ Short ↔ Long
    corr = np.array([
        [1.0, -0.4, -0.3],
        [-0.4, 1.0, 0.7],
        [-0.3, 0.7, 1.0]
    ])

    L = np.linalg.cholesky(corr)

    default_count = 0

    for _ in range(simulations):

        debt_ratio = debt_ratio_start
        s_rate = short_rate
        l_rate = long_rate

        for t in range(maturity):

            shocks = L @ np.random.normal(size=3)

            copper_shock = copper_vol * np.random.normal()

            gdp_growth = (
                gdp_drift
                + gdp_vol * shocks[0]
                + copper_beta * copper_shock
            )

            s_rate += short_vol * shocks[1]
            l_rate += long_vol * shocks[2]

            avg_rate = (s_rate + l_rate) / 2

            debt_ratio = debt_ratio * (1 + avg_rate) / (1 + gdp_growth)

        if debt_ratio > 1.2:
            default_count += 1

    pd_5y = default_count / simulations

    # =========================
    # CDS Spread Pricing
    # =========================

    recovery = 0.4
    duration = 5

    cds_spread = (pd_5y * (1 - recovery)) / duration

    return pd_5y, cds_spread


# =========================
# MAIN
# =========================

if __name__ == "__main__":

    prices, returns = load_market_data()

    risk_score = compute_risk_score(returns)

    pd_5y, cds = sovereign_model(risk_score, returns)

    print("\n=== ADVANCED SOVEREIGN STRESS ENGINE ===\n")

    print("Global Risk Score:", risk_score, "/ 3")
    print("5Y Default Probability:", round(pd_5y * 100, 2), "%")
    print("Implied CDS Spread:", round(cds * 10000, 1), "bps")

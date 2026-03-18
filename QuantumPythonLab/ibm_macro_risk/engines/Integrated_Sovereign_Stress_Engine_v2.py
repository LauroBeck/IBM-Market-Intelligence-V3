import numpy as np
import pandas as pd
import yfinance as yf

# =========================
# 1️⃣ MARKET DATA + SIGNAL
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


def compute_risk_score(returns):

    latest = returns.iloc[-1]

    risk_score = 0

    # Asia Risk-On
    if latest["MSCI_Asia"] > 0:
        risk_score += 1

    # US Divergence
    us_avg = np.mean([latest["SP500"],
                      latest["NASDAQ"],
                      latest["DOW"]])

    if latest["MSCI_Asia"] > 0 and us_avg < 0:
        risk_score += 1

    # Liquidity expansion
    if latest["Gold"] > 0 and latest["Copper"] > 0:
        risk_score += 1

    return risk_score


# =========================
# 2️⃣ SOVEREIGN MONTE CARLO
# =========================

def sovereign_stress_model(risk_score):

    # Base macro assumptions
    base_gdp_growth = 0.04
    debt_to_gdp_start = 0.85
    interest_rate = 0.05
    maturity = 5
    simulations = 10000

    # GDP adjustment from risk score
    adjustment_map = {
        0: -0.02,
        1: -0.01,
        2: 0.005,
        3: 0.015
    }

    gdp_drift = base_gdp_growth + adjustment_map[risk_score]

    # Volatility assumptions
    gdp_vol = 0.02
    rate_vol = 0.015

    # Correlation matrix (GDP ↔ rates)
    corr = np.array([[1.0, -0.4],
                     [-0.4, 1.0]])

    L = np.linalg.cholesky(corr)

    default_count = 0

    for _ in range(simulations):

        debt_ratio = debt_to_gdp_start

        for t in range(maturity):

            shocks = L @ np.random.normal(size=2)

            gdp_growth = gdp_drift + gdp_vol * shocks[0]
            rate = interest_rate + rate_vol * shocks[1]

            debt_ratio = debt_ratio * (1 + rate) / (1 + gdp_growth)

        if debt_ratio > 1.2:
            default_count += 1

    default_prob = default_count / simulations

    return default_prob


# =========================
# MAIN
# =========================

if __name__ == "__main__":

    prices, returns = load_market_data()

    risk_score = compute_risk_score(returns)

    default_probability = sovereign_stress_model(risk_score)

    print("\n=== MACRO-LINKED SOVEREIGN STRESS ENGINE ===\n")

    print("Global Risk Score:", risk_score, "/ 3")

    print("Estimated 5Y Default Probability:",
          round(default_probability * 100, 2), "%")

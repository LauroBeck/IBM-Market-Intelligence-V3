import numpy as np
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

# ============================================
# 1️⃣ LOAD REAL MARKET DATA
# ============================================

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

    raw = yf.download(
        list(tickers.values()),
        period="1y",
        auto_adjust=True,
        progress=False
    )

    if isinstance(raw.columns, pd.MultiIndex):
        data = raw["Close"]
    else:
        data = raw

    data.columns = tickers.keys()
    data = data.ffill()

    returns = data.pct_change().dropna()

    return data, returns


# ============================================
# 2️⃣ GLOBAL RISK SCORE ENGINE
# ============================================

def compute_risk_score(returns):

    latest = returns.iloc[-1]
    score = 0

    # Asia Risk-On
    if latest["MSCI_Asia"] > 0:
        score += 1

    # US Divergence
    us_avg = np.mean([
        latest["SP500"],
        latest["NASDAQ"],
        latest["DOW"]
    ])

    if latest["MSCI_Asia"] > 0 and us_avg < 0:
        score += 1

    # Commodity Liquidity
    if latest["Gold"] > 0 and latest["Copper"] > 0:
        score += 1

    return score


# ============================================
# 3️⃣ GLOBAL LIQUIDITY INDEX (NEW)
# ============================================

def compute_global_liquidity_index(returns):

    weights = {
        "MSCI_Asia": 0.25,
        "SP500": 0.25,
        "NASDAQ": 0.20,
        "Gold": 0.15,
        "Copper": 0.15
    }

    latest = returns.iloc[-5:].mean()

    gli = sum(latest[k] * w for k, w in weights.items())

    return gli


# ============================================
# 4️⃣ SOVEREIGN MONTE CARLO ENGINE
# ============================================

def sovereign_model(risk_score, returns, gli, scenario="baseline"):

    simulations = 10000
    maturity = 5

    debt_ratio_start = 0.85
    base_gdp = 0.04
    short_rate = 0.04
    long_rate = 0.05

    adjustment_map = {
        0: -0.02,
        1: -0.01,
        2: 0.005,
        3: 0.015
    }

    gdp_drift = base_gdp + adjustment_map[risk_score]

    copper_beta = 0.3
    copper_vol = returns["Copper"].std() * np.sqrt(252)

    gdp_vol = 0.02
    short_vol = 0.015
    long_vol = 0.02

    if scenario == "hard_landing":
        gdp_drift -= 0.03
        gdp_vol *= 1.8
        short_rate += 0.01
        long_rate += 0.015

    elif scenario == "semiconductor_bust":
        gdp_drift -= 0.025
        copper_beta = 0.6
        long_rate -= 0.01

    elif scenario == "liquidity_supercycle":
        gdp_drift += 0.02
        copper_beta = 0.4

    corr = np.array([
        [1.0, -0.4, -0.3],
        [-0.4, 1.0, 0.7],
        [-0.3, 0.7, 1.0]
    ])

    L = np.linalg.cholesky(corr)

    default_events = 0
    debt_paths = []

    for _ in range(simulations):

        debt_ratio = debt_ratio_start
        s_rate = short_rate
        l_rate = long_rate

        path = []

        for _ in range(maturity):

            shocks = L @ np.random.normal(size=3)
            copper_shock = copper_vol * np.random.normal()

            gdp_growth = (
                gdp_drift +
                gdp_vol * shocks[0] +
                copper_beta * copper_shock
            )

            s_rate += short_vol * shocks[1]
            l_rate += long_vol * shocks[2]

            avg_rate = (s_rate + l_rate) / 2

            debt_ratio = debt_ratio * (1 + avg_rate) / (1 + gdp_growth)

            path.append(debt_ratio)

        debt_paths.append(path)

        if debt_ratio > 1.2:
            default_events += 1

    base_default_prob = default_events / simulations

    # ======================================
    # LIQUIDITY ADJUSTMENT (GLI)
    # ======================================

    liquidity_adjustment = -0.5 * gli

    adjusted_default_prob = base_default_prob + liquidity_adjustment
    adjusted_default_prob = max(0, min(1, adjusted_default_prob))

    recovery = 0.4
    duration = 5

    cds_spread = (adjusted_default_prob * (1 - recovery)) / duration

    return adjusted_default_prob, cds_spread, np.array(debt_paths)


# ============================================
# 5️⃣ DASHBOARD
# ============================================

def dashboard(results):

    fig = go.Figure()

    for scenario, data in results.items():

        mean_path = data["debt_paths"].mean(axis=0)

        fig.add_trace(go.Scatter(
            y=mean_path,
            mode="lines",
            name=f"{scenario} (CDS {round(data['cds']*10000,1)} bps)"
        ))

    fig.update_layout(
        title="Sovereign Macro Stress Dashboard",
        xaxis_title="Year",
        yaxis_title="Debt / GDP",
        template="plotly_dark"
    )

    fig.write_image("sovereign_dashboard.png", width=1200, height=800)

    print("\nDashboard saved as sovereign_dashboard.png")


# ============================================
# 6️⃣ MAIN TERMINAL
# ============================================

if __name__ == "__main__":

    print("\nLoading Market Data...")

    prices, returns = load_market_data()

    risk_score = compute_risk_score(returns)

    gli = compute_global_liquidity_index(returns)

    print("Global Risk Score:", risk_score, "/ 3")
    print("Global Liquidity Index:", round(gli, 4))

    scenarios = [
        "baseline",
        "hard_landing",
        "semiconductor_bust",
        "liquidity_supercycle"
    ]

    results = {}

    for s in scenarios:

        pd_5y, cds, debt_paths = sovereign_model(
            risk_score,
            returns,
            gli,
            scenario=s
        )

        print("\nScenario:", s)
        print("Default Probability:", round(pd_5y * 100, 2), "%")
        print("Implied CDS Spread:", round(cds * 10000, 1), "bps")

        results[s] = {
            "pd": pd_5y,
            "cds": cds,
            "debt_paths": debt_paths
        }

    dashboard(results)

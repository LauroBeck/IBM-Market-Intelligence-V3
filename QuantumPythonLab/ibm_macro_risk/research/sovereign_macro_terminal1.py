import numpy as np
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

# =====================================
# MARKET DATA
# =====================================

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


# =====================================
# GLOBAL RISK SCORE
# =====================================

def compute_risk_score(returns):

    latest = returns.iloc[-1]

    score = 0

    if latest["MSCI_Asia"] > 0:
        score += 1

    us_avg = np.mean([
        latest["SP500"],
        latest["NASDAQ"],
        latest["DOW"]
    ])

    if latest["MSCI_Asia"] > 0 and us_avg < 0:
        score += 1

    if latest["Gold"] > 0 and latest["Copper"] > 0:
        score += 1

    return score


# =====================================
# SOVEREIGN MONTE CARLO MODEL
# =====================================

def sovereign_model(risk_score, returns, scenario="baseline"):

    simulations = 10000
    maturity = 5

    debt_start = 0.85

    base_gdp = 0.04

    short_rate = 0.04
    long_rate = 0.05

    adjustment = {
        0: -0.02,
        1: -0.01,
        2: 0.005,
        3: 0.015
    }

    gdp_drift = base_gdp + adjustment[risk_score]

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

    defaults = 0

    paths = []

    for _ in range(simulations):

        debt = debt_start
        s_rate = short_rate
        l_rate = long_rate

        path = []

        for _ in range(maturity):

            shocks = L @ np.random.normal(size=3)

            copper_shock = copper_vol * np.random.normal()

            gdp = gdp_drift + gdp_vol * shocks[0] + copper_beta * copper_shock

            s_rate += short_vol * shocks[1]
            l_rate += long_vol * shocks[2]

            avg_rate = (s_rate + l_rate) / 2

            debt = debt * (1 + avg_rate) / (1 + gdp)

            path.append(debt)

        paths.append(path)

        if debt > 1.2:
            defaults += 1

    pd5 = defaults / simulations

    recovery = 0.4

    cds = (pd5 * (1 - recovery)) / 5

    return pd5, cds, np.array(paths)


# =====================================
# DASHBOARD
# =====================================

def dashboard(results):

    fig = go.Figure()

    for scenario, data in results.items():

        mean_path = data["paths"].mean(axis=0)

        fig.add_trace(
            go.Scatter(
                y=mean_path,
                mode="lines",
                name=f"{scenario} (CDS {round(data['cds']*10000,1)} bps)"
            )
        )

    fig.update_layout(
        title="Sovereign Macro Stress Dashboard",
        xaxis_title="Year",
        yaxis_title="Debt / GDP",
        template="plotly_dark"
    )

    fig.write_image(
        "sovereign_dashboard.png",
        width=1400,
        height=900
    )

    print("\nDashboard saved as sovereign_dashboard.png")


# =====================================
# MAIN
# =====================================

if __name__ == "__main__":

    print("\nLoading market data...")

    prices, returns = load_market_data()

    risk_score = compute_risk_score(returns)

    print("Global Risk Score:", risk_score, "/ 3")

    scenarios = [
        "baseline",
        "hard_landing",
        "semiconductor_bust",
        "liquidity_supercycle"
    ]

    results = {}

    for s in scenarios:

        pd5, cds, paths = sovereign_model(
            risk_score,
            returns,
            scenario=s
        )

        print("\nScenario:", s)
        print("Default Probability:", round(pd5*100,2), "%")
        print("Implied CDS:", round(cds*10000,1), "bps")

        results[s] = {
            "pd": pd5,
            "cds": cds,
            "paths": paths
        }

    dashboard(results)

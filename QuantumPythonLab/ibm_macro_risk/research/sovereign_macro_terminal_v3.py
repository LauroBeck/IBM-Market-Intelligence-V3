import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# -----------------------------
# 1. LOAD MARKET DATA
# -----------------------------

def load_market_data():

    tickers = {
        "MSCI_ASIA": "AAXJ",
        "USD_CNY": "CNY=X",
        "USD_KRW": "KRW=X",
        "Gold": "GC=F",
        "Silver": "SI=F",
        "Copper": "HG=F",
        "Platinum": "PL=F"
    }

    data = yf.download(list(tickers.values()), period="2y")["Adj Close"]
    data.columns = tickers.keys()

    returns = data.pct_change().dropna()

    return data, returns


# -----------------------------
# 2. ASIA CAPITAL FLOW INDEX
# -----------------------------

def asia_capital_flow_index(data):

    asia_equity_momentum = data["MSCI_ASIA"].pct_change(60).iloc[-1]

    cny_trend = -data["USD_CNY"].pct_change(30).iloc[-1]
    krw_trend = -data["USD_KRW"].pct_change(30).iloc[-1]

    metals_cycle = (
        data["Copper"].pct_change(60).iloc[-1] +
        data["Platinum"].pct_change(60).iloc[-1]
    ) / 2

    flow_index = (
        0.4 * asia_equity_momentum +
        0.3 * cny_trend +
        0.2 * krw_trend +
        0.1 * metals_cycle
    )

    return flow_index


# -----------------------------
# 3. GLOBAL RISK SCORE
# -----------------------------

def global_risk_score(data):

    score = 0

    if data["Gold"].pct_change(30).iloc[-1] > 0:
        score += 1

    if data["Copper"].pct_change(30).iloc[-1] > 0:
        score += 1

    if data["MSCI_ASIA"].pct_change(30).iloc[-1] > 0:
        score += 1

    return score


# -----------------------------
# 4. COMMODITY GDP BETA
# -----------------------------

def commodity_gdp_beta(data):

    copper_growth = data["Copper"].pct_change(90).iloc[-1]
    gold_defensive = data["Gold"].pct_change(90).iloc[-1]

    beta = 0.6 * copper_growth - 0.3 * gold_defensive

    return beta


# -----------------------------
# 5. YIELD CURVE SIMULATION
# -----------------------------

def simulate_yield_curve():

    short_rate = np.random.normal(0.035, 0.01)
    long_rate = short_rate + np.random.normal(0.01, 0.005)

    slope = long_rate - short_rate

    return short_rate, long_rate, slope


# -----------------------------
# 6. MONTE CARLO SOVEREIGN STRESS
# -----------------------------

def sovereign_default_model(gdp_growth, debt_ratio, slope):

    risk = (
        0.35 * debt_ratio
        - 0.4 * gdp_growth
        - 0.2 * slope
    )

    probability = 1 / (1 + np.exp(-risk))

    return probability


# -----------------------------
# 7. CDS PRICING
# -----------------------------

def cds_spread(default_prob):

    recovery = 0.4
    spread = default_prob * (1 - recovery) * 10000

    return spread


# -----------------------------
# 8. MONTE CARLO ENGINE
# -----------------------------

def run_monte_carlo(base_gdp, debt_ratio, iterations=5000):

    probs = []

    for _ in range(iterations):

        short_rate, long_rate, slope = simulate_yield_curve()

        gdp = np.random.normal(base_gdp, 0.01)

        p = sovereign_default_model(gdp, debt_ratio, slope)

        probs.append(p)

    return np.mean(probs)


# -----------------------------
# 9. MACRO SCENARIOS
# -----------------------------

def scenario_parameters():

    return {
        "baseline": 0.025,
        "hard_landing": -0.01,
        "semiconductor_bust": 0.005,
        "liquidity_supercycle": 0.04
    }


# -----------------------------
# 10. DASHBOARD
# -----------------------------

def build_dashboard(results):

    scenarios = list(results.keys())
    probs = [results[s]["prob"] for s in scenarios]
    cds = [results[s]["cds"] for s in scenarios]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=scenarios,
        y=probs,
        name="Default Probability"
    ))

    fig.add_trace(go.Scatter(
        x=scenarios,
        y=cds,
        name="CDS Spread",
        yaxis="y2"
    ))

    fig.update_layout(
        title="Sovereign Stress Dashboard",
        yaxis=dict(title="Default Probability"),
        yaxis2=dict(
            title="CDS Spread (bps)",
            overlaying="y",
            side="right"
        )
    )

    fig.write_html("sovereign_dashboard.html")
    fig.write_image("sovereign_dashboard.png", width=1200, height=800)

    print("\nDashboard saved:")
    print("sovereign_dashboard.html")
    print("sovereign_dashboard.png")


# -----------------------------
# MAIN
# -----------------------------

if __name__ == "__main__":

    print("\nLoading Market Data...\n")

    prices, returns = load_market_data()

    flow_index = asia_capital_flow_index(prices)
    risk_score = global_risk_score(prices)
    commodity_beta = commodity_gdp_beta(prices)

    print("Asia Capital Flow Index:", round(flow_index,4))
    print("Global Risk Score:", risk_score, "/ 3")
    print("Commodity GDP Beta:", round(commodity_beta,4))

    base_debt = 0.9

    scenarios = scenario_parameters()

    results = {}

    for name, base_gdp in scenarios.items():

        adjusted_gdp = base_gdp + commodity_beta + flow_index

        prob = run_monte_carlo(adjusted_gdp, base_debt)

        spread = cds_spread(prob)

        results[name] = {
            "prob": prob,
            "cds": spread
        }

        print("\nScenario:", name)
        print("Adjusted GDP:", round(adjusted_gdp,4))
        print("Default Probability:", round(prob*100,2), "%")
        print("Implied CDS Spread:", round(spread,1), "bps")

    build_dashboard(results)

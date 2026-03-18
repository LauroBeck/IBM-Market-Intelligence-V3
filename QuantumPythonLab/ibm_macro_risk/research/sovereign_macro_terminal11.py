import numpy as np
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression

# ----------------------------------------------------
# MARKET DATA LOADER
# ----------------------------------------------------

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

    raw = yf.download(
        list(tickers.values()),
        period="2y",
        auto_adjust=True,
        progress=False
    )

    if isinstance(raw.columns, pd.MultiIndex):
        data = raw["Close"]
    else:
        data = raw

    data.columns = tickers.keys()

    returns = data.pct_change().dropna()

    return data, returns


# ----------------------------------------------------
# ASIA CAPITAL FLOW INDEX
# ----------------------------------------------------

def compute_asia_capital_flow(returns):

    asia = returns["MSCI_ASIA"]
    fx_pressure = returns["USD_CNY"] + returns["USD_KRW"]

    flow = asia - fx_pressure

    return flow.mean()


# ----------------------------------------------------
# COMMODITY GDP BETA
# ----------------------------------------------------

def compute_commodity_beta(returns):

    metals = returns[["Copper", "Platinum"]].mean(axis=1)

    asia = returns["MSCI_ASIA"]

    model = LinearRegression()
    model.fit(metals.values.reshape(-1,1), asia.values)

    beta = model.coef_[0]

    return beta


# ----------------------------------------------------
# GLOBAL RISK SCORE
# ----------------------------------------------------

def global_risk_score(returns):

    score = 0

    if returns["MSCI_ASIA"].mean() > 0:
        score += 1

    if returns["Copper"].mean() > 0:
        score += 1

    if returns["Gold"].mean() > 0:
        score += 1

    return score


# ----------------------------------------------------
# YIELD CURVE SIMULATION
# ----------------------------------------------------

def simulate_yield_curve():

    beta0 = np.random.normal(0.03,0.01)
    beta1 = np.random.normal(-0.02,0.01)
    beta2 = np.random.normal(0.01,0.005)

    tau = 1.5

    maturities = np.array([1,2,5,10])

    yields = beta0 + beta1*np.exp(-maturities/tau) + beta2*(maturities/tau)*np.exp(-maturities/tau)

    return yields.mean()


# ----------------------------------------------------
# MONTE CARLO SOVEREIGN MODEL
# ----------------------------------------------------

def sovereign_simulation(gdp_growth, rate, debt0=80, sims=5000, years=10):

    debt_paths = np.zeros((sims,years))

    for s in range(sims):

        debt = debt0

        for t in range(years):

            g = np.random.normal(gdp_growth,0.02)
            r = np.random.normal(rate,0.01)

            debt = debt*(1+r)/(1+g)

            debt_paths[s,t] = debt

    return debt_paths


# ----------------------------------------------------
# DEFAULT PROBABILITY
# ----------------------------------------------------

def default_probability(debt_paths):

    final_debt = debt_paths[:,-1]

    default = np.mean(final_debt > 120)

    return default


# ----------------------------------------------------
# CDS SPREAD
# ----------------------------------------------------

def cds_spread(pd):

    recovery = 0.4

    spread = pd*(1-recovery)

    return spread


# ----------------------------------------------------
# SCENARIO ENGINE
# ----------------------------------------------------

def run_scenarios(risk_score, commodity_beta, capital_flow):

    scenarios = {

        "baseline":{
            "gdp":0.03 + commodity_beta*0.01,
            "rate":0.03
        },

        "hard_landing":{
            "gdp":-0.01,
            "rate":0.04
        },

        "semiconductor_bust":{
            "gdp":0.00,
            "rate":0.035
        },

        "liquidity_supercycle":{
            "gdp":0.05 + capital_flow*0.1,
            "rate":0.025
        }
    }

    results = {}

    for name,params in scenarios.items():

        rate = simulate_yield_curve()

        paths = sovereign_simulation(params["gdp"],rate)

        pd = default_probability(paths)

        cds = cds_spread(pd)

        results[name] = {
            "debt_paths":paths,
            "pd":pd,
            "cds":cds
        }

    return results


# ----------------------------------------------------
# DASHBOARD
# ----------------------------------------------------

def dashboard(results):

    fig = go.Figure()

    for scenario,data in results.items():

        mean_path = data["debt_paths"].mean(axis=0)

        fig.add_trace(go.Scatter(
            y=mean_path,
            mode='lines',
            name=f"{scenario} (CDS {round(data['cds']*10000,1)} bps)"
        ))

    fig.update_layout(
        title="Sovereign Macro Stress Dashboard",
        xaxis_title="Year",
        yaxis_title="Debt / GDP",
        template="plotly_dark"
    )

    fig.write_html("sovereign_dashboard.html")

    try:
        fig.write_image("sovereign_dashboard.png",width=1200,height=800)
    except:
        print("PNG export requires kaleido")

    print("\nDashboard saved as sovereign_dashboard.html")


# ----------------------------------------------------
# MAIN
# ----------------------------------------------------

if __name__ == "__main__":

    print("\nLoading Market Data...")

    prices,returns = load_market_data()

    capital_flow = compute_asia_capital_flow(returns)

    commodity_beta = compute_commodity_beta(returns)

    risk_score = global_risk_score(returns)

    print("\nAsia Capital Flow Index:",round(capital_flow,4))
    print("Commodity GDP Beta:",round(commodity_beta,4))
    print("Global Risk Score:",risk_score,"/ 3")

    results = run_scenarios(risk_score,commodity_beta,capital_flow)

    for s,data in results.items():

        print("\nScenario:",s)
        print("Default Probability:",round(data["pd"]*100,2),"%")
        print("Implied CDS Spread:",round(data["cds"]*10000,1),"bps")

    dashboard(results)

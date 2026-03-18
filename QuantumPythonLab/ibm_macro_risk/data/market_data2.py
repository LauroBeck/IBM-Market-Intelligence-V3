import yfinance as yf
import pandas as pd
import numpy as np

def load_market_data():

    tickers = {
        # Asia Equity Proxy
        "MSCI_Asia": "AAXJ",        # Asia ETF proxy
        
        # US Futures Proxies
        "SP500": "^GSPC",
        "NASDAQ": "^IXIC",
        "DOW": "^DJI",

        # Europe
        "FTSE": "^FTSE",
        "CAC": "^FCHI",

        # Commodities
        "Gold": "GC=F",
        "Copper": "HG=F",

        # FX
        "USD_CNY": "CNY=X",
        "USD_KRW": "KRW=X"
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


# ----------------------------
# SIGNAL ENGINE
# ----------------------------

def compute_signals(data, returns):

    latest = returns.iloc[-1]
    one_year = returns.rolling(252).sum().iloc[-1]

    signals = {}

    # 1️⃣ Asia Risk-On
    if latest["MSCI_Asia"] > 0:
        signals["Asia_Risk"] = "RISK-ON"
    else:
        signals["Asia_Risk"] = "RISK-OFF"

    # 2️⃣ US Futures Divergence
    us_avg = np.mean([latest["SP500"], latest["NASDAQ"], latest["DOW"]])

    if latest["MSCI_Asia"] > 0 and us_avg < 0:
        signals["Capital_Rotation"] = "Asia Outperforming US"
    else:
        signals["Capital_Rotation"] = "No clear rotation"

    # 3️⃣ Commodity Liquidity Signal
    if latest["Gold"] > 0 and latest["Copper"] > 0:
        signals["Liquidity_Regime"] = "Liquidity Expansion"
    elif latest["Gold"] > 0:
        signals["Liquidity_Regime"] = "Defensive Bid"
    else:
        signals["Liquidity_Regime"] = "Neutral"

    # 4️⃣ FX Pressure
    if latest["USD_CNY"] > 0:
        signals["CNY_Pressure"] = "Depreciation Pressure"
    else:
        signals["CNY_Pressure"] = "Stable/Appreciating"

    return signals


# ----------------------------
# MAIN
# ----------------------------

if __name__ == "__main__":

    prices, returns = load_market_data()

    signals = compute_signals(prices, returns)

    print("\n=== GLOBAL MARKET SIGNAL DASHBOARD ===\n")

    for k, v in signals.items():
        print(f"{k}: {v}")

    print("\nLatest Daily Returns:\n")
    print(returns.tail(1).T)

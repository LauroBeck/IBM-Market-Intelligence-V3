import yfinance as yf
import pandas as pd

def load_market_data():

    tickers = {
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


if __name__ == "__main__":
    prices, returns = load_market_data()
    print(prices.tail())
    print("\nCorrelation Matrix:\n")
    print(returns.corr())

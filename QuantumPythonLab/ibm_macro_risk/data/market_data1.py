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

    # Download with auto_adjust to avoid Adj Close problems
    raw = yf.download(
        list(tickers.values()),
        period="2y",
        auto_adjust=True,
        progress=False
    )

    # Handle MultiIndex structure safely
    if isinstance(raw.columns, pd.MultiIndex):
        if "Close" in raw.columns.levels[0]:
            data = raw["Close"]
        else:
            raise ValueError("Close column not found in downloaded data.")
    else:
        data = raw

    # Rename columns to readable names
    data.columns = tickers.keys()

    # Drop rows with all NaN values
    data = data.dropna(how="all")

    # Calculate returns
    returns = data.pct_change().dropna()

    return data, returns


if __name__ == "__main__":
    prices, returns = load_market_data()

    print("\nLatest Prices:\n")
    print(prices.tail())

    print("\nCorrelation Matrix:\n")
    print(returns.corr())

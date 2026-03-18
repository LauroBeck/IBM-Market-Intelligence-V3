import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# 1. Prices as of March 4, 2026
tickers = {
    'IBM Evolution': 'IBM',        # Last: $249.71
    'S&P 500': '^GSPC',            # Last: 6,869.50
    'Nasdaq Composite': '^IXIC',   # Last: 22,807.48
    'Dow Jones': '^DJI',           # Last: 48,739.41
    'VIX Index': '^VIX'            # Last: 21.15
}

# 2. Setup Figure
fig = make_subplots(rows=len(tickers), cols=1, shared_xaxes=True, vertical_spacing=0.04)

# 3. Build Charts
for i, (name, symbol) in enumerate(tickers.items(), 1):
    data = yf.download(symbol, start='2026-01-01', end='2026-03-05', auto_adjust=False)
    if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(0)

    # Calculate YTD
    ytd = ((data['Close'].iloc[-1] - data['Close'].iloc[0]) / data['Close'].iloc[0]) * 100
    
    # Add Trace
    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name=name, line=dict(width=2)), row=i, col=1)
    
    # Add Fixed Label
    xref_val = "x domain" if i == 1 else f"x{i} domain"
    yref_val = "y domain" if i == 1 else f"y{i} domain"
    fig.add_annotation(text=f"{name} YTD: {ytd:+.2f}%", xref=xref_val, yref=yref_val,
                       x=1.01, y=0.5, showarrow=False, font=dict(color="cyan"))

# 4. Global Styling
fig.update_layout(template='plotly_dark', height=1500, width=1100, title="IBM vs Bloomberg Scorecard", margin=dict(r=150))

# 5. THE FIX: Explicit Path Saving
current_dir = os.getcwd()
html_path = os.path.join(current_dir, "market_scorecard_fixed.html")
png_path = os.path.join(current_dir, "market_scorecard_fixed.png")

# Save HTML (Always works)
fig.write_html(html_path)
print(f"CHECK 1: Interactive file saved at -> {html_path}")

# Save PNG (Requires kaleido)
try:
    fig.write_image(png_path, engine="kaleido")
    print(f"CHECK 2: Static image saved at -> {png_path}")
except Exception as e:
    print(f"PNG FAILED: Likely missing 'kaleido'. Fix with: pip install -U kaleido")

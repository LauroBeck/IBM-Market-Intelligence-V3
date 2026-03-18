import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# 1. Configuration
tickers = {
    'IBM Evolution': 'IBM',
    'S&P 500 Index': '^GSPC',
    'Nasdaq Composite': '^IXIC',
    'Dow Jones Industrial': '^DJI',
    'VIX Fear Gauge': '^VIX'
}

# 2. Setup Figure
fig = make_subplots(
    rows=len(tickers), cols=1, 
    shared_xaxes=True, 
    vertical_spacing=0.03,
    subplot_titles=[f"<b>{k}</b>" for k in tickers.keys()]
)

# 3. Processing Loop
for i, (name, symbol) in enumerate(tickers.items(), 1):
    # Fetch data starting from start of the year for YTD calc
    data = yf.download(symbol, start='2026-01-01', end='2026-03-05', auto_adjust=False)
    
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # Calculate YTD % Change
    start_price = data['Close'].iloc[0]
    current_price = data['Close'].iloc[-1]
    ytd_change = ((current_price - start_price) / start_price) * 100
    color_label = "#00ff88" if ytd_change >= 0 else "#ff3333"

    # A. Add Main Visual (Line for IBM, Candles for others)
    if 'IBM' in name:
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], line=dict(color='#00bfff', width=3)), row=i, col=1)
    else:
        fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], 
                                     low=data['Low'], close=data['Close'],
                                     increasing_line_color='#00ff88', decreasing_line_color='#ff3333'), row=i, col=1)

    # B. Add YTD Label Annotation
    fig.add_annotation(
        text=f"YTD: {ytd_change:+.2f}%",
        xref=f"x{i} domain", yref=f"y{i} domain",
        x=1.05, y=0.5,
        showarrow=False,
        font=dict(size=14, color=color_label, family="Arial Black"),
        align="left"
    )

# 4. Global Refined Styling
fig.update_layout(
    template='plotly_dark',
    title=f"<b>Global Macro Scorecard: March 4, 2026</b>",
    height=1800, width=1350, # Slightly wider for labels
    showlegend=False,
    paper_bgcolor='#050505', plot_bgcolor='#050505',
    margin=dict(l=50, r=150, t=100, b=50) # Extra right margin for YTD labels
)

# Scale Precision
for i in range(2, 5): # Log scale for big indices
    fig.update_yaxes(type="log", row=i, col=1, gridcolor='#222', showline=True)
for i in [1, 5]: # Linear for IBM and VIX
    fig.update_yaxes(type="linear", row=i, col=1, gridcolor='#222', showline=True)

fig.update_xaxes(rangeslider_visible=False, showgrid=False)

# 5. EXPORT
try:
    fig.write_image("market_scorecard_2026.png", scale=2)
    fig.write_html("market_scorecard_2026.html")
    print("-" * 50)
    print("SUCCESS: Market Scorecard Dashboard Generated!")
    print(f"IBM Current: ${current_price:.2f}")
    print("Check: market_scorecard_2026.png")
    print("-" * 50)
except Exception as e:
    print(f"Error: {e}")

import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. Configuration
tickers = {
    'IBM Evolution (Price + Bands)': 'IBM',
    'S&P 500 Index': '^GSPC',
    'Nasdaq Composite': '^IXIC',
    'Dow Jones Industrial': '^DJI',
    'VIX Index (Fear Gauge)': '^VIX'
}

# 2. Setup Figure (Giving more vertical room for Volume bars)
fig = make_subplots(
    rows=len(tickers), cols=1, 
    shared_xaxes=True, 
    vertical_spacing=0.04,
    subplot_titles=[f"<b>{k}</b>" for k in tickers.keys()],
    row_heights=[0.25, 0.2, 0.2, 0.2, 0.15] # Adjusted for visual priority
)

# 3. Add Data Traces
for i, (name, symbol) in enumerate(tickers.items(), 1):
    data = yf.download(symbol, start='2024-06-01', end='2026-03-04', auto_adjust=False)
    
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # A. Price Logic
    if 'IBM' in name:
        # Bollinger Bands
        sma = data['Close'].rolling(window=20).mean()
        std = data['Close'].rolling(window=20).std()
        upper_band, lower_band = sma + (std * 2), sma - (std * 2)

        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name='Price', line=dict(color='#006699', width=2.5)), row=i, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=upper_band, line=dict(color='rgba(173,216,230,0.2)'), showlegend=False), row=i, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=lower_band, line=dict(color='rgba(173,216,230,0.2)'), fill='tonexty', fillcolor='rgba(173,216,230,0.03)', showlegend=False), row=i, col=1)
    else:
        fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name=name, increasing_line_color='#26a69a', decreasing_line_color='#ef5350'), row=i, col=1)

    # B. Volume Logic (Small bars at the bottom of each subplot)
    # Using 'secondary_y=False' but overlaying it by creating a separate axis isn't needed here; 
    # we just use a Bar chart and Plotly will handle the scale if we use a separate Y-axis or just keep it simple.
    # To keep it terminal-style, we will place volume on a separate invisible axis overlay.
    colors = ['#26a69a' if row['Close'] >= row['Open'] else '#ef5350' for index, row in data.iterrows()]
    fig.add_trace(go.Bar(x=data.index, y=data['Volume'], name='Volume', marker_color=colors, opacity=0.3, showlegend=False), row=i, col=1)

# 4. Final Terminal Styling
fig.update_layout(
    template='plotly_dark',
    title="<b>Global Market Liquidity & Price Evolution Dashboard</b>",
    height=2000, width=1200,
    showlegend=False,
    paper_bgcolor='black', plot_bgcolor='black',
    margin=dict(l=60, r=60, t=100, b=60)
)

fig.update_xaxes(rangeslider_visible=False, showgrid=False)
fig.update_yaxes(showgrid=True, gridcolor='#222', zeroline=False)

# 5. EXPORT
try:
    fig.write_image("terminal_liquidity_dashboard.png", scale=2)
    fig.write_html("terminal_liquidity_dashboard.html")
    print("-" * 40)
    print("SUCCESS: Full Liquidity Dashboard Exported!")
    print("Check: terminal_liquidity_dashboard.png")
    print("-" * 40)
except Exception as e:
    print(f"Export error: {e}")

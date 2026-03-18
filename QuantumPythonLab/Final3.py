import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
    data = yf.download(symbol, start='2026-01-01', end='2026-03-05', auto_adjust=False)
    
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # Calculate YTD % Change
    start_price = data['Close'].iloc[0]
    current_price = data['Close'].iloc[-1]
    ytd_change = ((current_price - start_price) / start_price) * 100
    color_label = "#00ff88" if ytd_change >= 0 else "#ff3333"

    # A. Add Main Visual
    if 'IBM' in name:
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], line=dict(color='#00bfff', width=3)), row=i, col=1)
    else:
        fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], 
                                     low=data['Low'], close=data['Close'],
                                     increasing_line_color='#00ff88', decreasing_line_color='#ff3333'), row=i, col=1)

    # B. FIXED ANNOTATION LOGIC
    # Subplot 1 must use 'x domain', subplots 2+ use 'xN domain'
    xref_val = "x domain" if i == 1 else f"x{i} domain"
    yref_val = "y domain" if i == 1 else f"y{i} domain"

    fig.add_annotation(
        text=f"YTD: {ytd_change:+.2f}%",
        xref=xref_val, yref=yref_val,
        x=1.02, y=0.5, # Positioned just inside the right margin
        showarrow=False,
        font=dict(size=14, color=color_label, family="Arial Black"),
        align="left"
    )

# 4. Global Styling
fig.update_layout(
    template='plotly_dark',
    title="<b>Global Macro Scorecard: March 4, 2026</b>",
    height=1800, width=1300,
    showlegend=False,
    paper_bgcolor='#050505', plot_bgcolor='#050505',
    margin=dict(l=50, r=150, t=100, b=50) 
)

fig.update_xaxes(rangeslider_visible=False, showgrid=False)
fig.update_yaxes(gridcolor='#222', showline=True)

# 5. EXPORT
fig.write_image("market_scorecard_fixed.png", scale=2)
print("SUCCESS: Dashboard generated with fixed labels.")

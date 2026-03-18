import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. Define Tickers
tickers = {
    'S&P 500': '^GSPC',
    'Nasdaq': '^IXIC',
    'Russell 2k': '^RUT',
    'Dow Jones': '^DJI',
    'VIX': '^VIX'
}

# 2. Setup Figure with subplots
fig = make_subplots(
    rows=len(tickers), cols=1, 
    shared_xaxes=True, 
    vertical_spacing=0.04, # Increased spacing slightly for titles
    subplot_titles=[f"<b>{k}</b>" for k in tickers.keys()]
)

# 3. Fetch Data and Add Traces
for i, (name, symbol) in enumerate(tickers.items(), 1):
    data = yf.download(symbol, start='2024-01-01', end='2026-03-04', auto_adjust=False)
    
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    fig.add_trace(
        go.Candlestick(
            x=data.index,
            open=data['Open'], high=data['High'],
            low=data['Low'], close=data['Close'],
            name=name,
            increasing_line_color='#26a69a', 
            decreasing_line_color='#ef5350'
        ),
        row=i, col=1
    )

# 4. Global Styling
fig.update_layout(
    template='plotly_dark',
    title="<b>Global Indices Performance Dashboard (March 2026)</b>",
    height=1500,  # Taller height for 5 detailed subplots
    width=1200,   # Fixed width for consistent image export
    showlegend=False,
    paper_bgcolor='black',
    plot_bgcolor='black',
    margin=dict(l=50, r=50, t=100, b=50)
)

# Clean up axes
fig.update_xaxes(rangeslider_visible=False)
fig.update_yaxes(showgrid=True, gridcolor='#333')

# 5. SAVE AS IMAGE (Headless Linux Friendly)
try:
    # Save as interactive HTML
    fig.write_html("multi_index_dashboard.html")
    
    # Save as high-res PNG
    # Note: Requires 'pip install kaleido'
    fig.write_image("multi_index_dashboard.png", scale=2)
    
    print("-" * 40)
    print("SUCCESS: Dashboard exported!")
    print("Files created: 'multi_index_dashboard.png' and 'multi_index_dashboard.html'")
    print("-" * 40)
except Exception as e:
    print(f"Error during export: {e}")

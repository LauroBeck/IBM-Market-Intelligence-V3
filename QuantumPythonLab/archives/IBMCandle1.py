import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. Configuration
tickers = {
    'IBM Evolution': 'IBM',
    'S&P 500': '^GSPC',
    'Nasdaq Composite': '^IXIC',
    'Dow Jones': '^DJI',
    'Russell 2k': '^RUT',
    'VIX Index': '^VIX'
}

# 2. Setup Figure
fig = make_subplots(
    rows=len(tickers), cols=1, 
    shared_xaxes=True, 
    vertical_spacing=0.03,
    subplot_titles=[f"<b>{k}</b>" for k in tickers.keys()]
)

# 3. Add Data Traces
for i, (name, symbol) in enumerate(tickers.items(), 1):
    data = yf.download(symbol, start='2024-06-01', end='2026-03-04', auto_adjust=False)
    
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # IBM is shown as a bold Line 'Evolution'
    if name == 'IBM Evolution':
        fig.add_trace(
            go.Scatter(x=data.index, y=data['Close'], name=name, 
                       line=dict(color='#006699', width=3),
                       fill='tozeroy', fillcolor='rgba(0, 102, 153, 0.1)'),
            row=i, col=1
        )
    # Indices are shown as Candlesticks
    else:
        fig.add_trace(
            go.Candlestick(
                x=data.index, open=data['Open'], high=data['High'],
                low=data['Low'], close=data['Close'], name=name,
                increasing_line_color='#26a69a', decreasing_line_color='#ef5350'
            ),
            row=i, col=1
        )

# 4. Professional Terminal Styling
fig.update_layout(
    template='plotly_dark',
    title="<b>IBM vs. Bloomberg Index Evolution Dashboard</b>",
    height=1600, width=1200,
    showlegend=False,
    paper_bgcolor='black', plot_bgcolor='black',
    margin=dict(l=60, r=60, t=100, b=60)
)

fig.update_xaxes(rangeslider_visible=False, showgrid=False)
fig.update_yaxes(showgrid=True, gridcolor='#333', zeroline=False)

# 5. EXPORT
try:
    # Save as high-res Image (Requires: pip install kaleido)
    fig.write_image("ibm_bloomberg_evolution.png", scale=2)
    # Save as interactive HTML
    fig.write_html("ibm_bloomberg_evolution.html")
    print("-" * 40)
    print("SUCCESS: Evolution dashboard exported!")
    print("Files: ibm_bloomberg_evolution.png, ibm_bloomberg_evolution.html")
    print("-" * 40)
except Exception as e:
    print(f"Export error: {e}")

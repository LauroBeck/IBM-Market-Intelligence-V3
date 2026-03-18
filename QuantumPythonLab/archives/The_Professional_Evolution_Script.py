import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. Configuration
tickers = {
    'IBM Evolution (with Bollinger Bands)': 'IBM',
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

    # IBM: Bollinger Bands + Line Evolution
    if 'IBM' in name:
        # Calculate Bollinger Bands (20-day SMA +/- 2 Std Dev)
        sma = data['Close'].rolling(window=20).mean()
        std = data['Close'].rolling(window=20).std()
        upper_band = sma + (std * 2)
        lower_band = sma - (std * 2)

        # Main Price Line
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name='IBM Price', 
                                 line=dict(color='#006699', width=3)), row=i, col=1)
        # Upper Band
        fig.add_trace(go.Scatter(x=data.index, y=upper_band, name='Upper BB',
                                 line=dict(color='rgba(173, 216, 230, 0.3)', width=1)), row=i, col=1)
        # Lower Band
        fig.add_trace(go.Scatter(x=data.index, y=lower_band, name='Lower BB',
                                 line=dict(color='rgba(173, 216, 230, 0.3)', width=1),
                                 fill='tonexty', fillcolor='rgba(173, 216, 230, 0.05)'), row=i, col=1)

    # Indices: Standard Candlesticks
    else:
        fig.add_trace(
            go.Candlestick(
                x=data.index, open=data['Open'], high=data['High'],
                low=data['Low'], close=data['Close'], name=name,
                increasing_line_color='#26a69a', decreasing_line_color='#ef5350'
            ),
            row=i, col=1
        )

# 4. Final Styling & Layout
fig.update_layout(
    template='plotly_dark',
    title="<b>IBM Reversal Analysis vs. Bloomberg Indices</b>",
    height=1800, width=1200,
    showlegend=False,
    paper_bgcolor='black', plot_bgcolor='black',
    margin=dict(l=60, r=60, t=100, b=60)
)

fig.update_xaxes(rangeslider_visible=False, showgrid=False)
fig.update_yaxes(showgrid=True, gridcolor='#333', zeroline=False)

# 5. EXPORT
try:
    fig.write_image("ibm_bollinger_evolution.png", scale=2)
    fig.write_html("ibm_bollinger_evolution.html")
    print("-" * 40)
    print("SUCCESS: Dashboard exported with Bollinger Bands!")
    print("Files: ibm_bollinger_evolution.png, ibm_bollinger_evolution.html")
    print("-" * 40)
except Exception as e:
    print(f"Export error: {e}")

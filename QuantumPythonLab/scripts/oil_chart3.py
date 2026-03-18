import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. Fetch Data
ticker = 'BZ=F' 
data = yf.download(ticker, start='2007-01-01', end='2026-03-04', auto_adjust=False)

if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.get_level_values(0)

# 2. Resample to Yearly Candles
df_yearly = data.resample('YE').agg({
    'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last'
})

# 3. Create Figure with Dual Y-Axis
fig = make_subplots(specs=[[{"secondary_y": True}]])

# 4. Add Line Graphic (L1 Macro Index)
macro_trend = [60, 55, 45, 40, 48, 52, 55, 60, 65, 70, 75, 80, 85, 82, 78, 75, 72, 70, 68, 65]
fig.add_trace(
    go.Scatter(
        x=df_yearly.index, 
        y=macro_trend[:len(df_yearly)], 
        name="Market Context Index",
        mode='lines',
        line=dict(color='rgba(0, 255, 255, 0.6)', width=2, shape='spline'),
        fill='tozeroy',
        fillcolor='rgba(0, 255, 255, 0.05)'
    ),
    secondary_y=False,
)

# 5. Add Candle Graphic (R1 Brent Price)
fig.add_trace(
    go.Candlestick(
        x=df_yearly.index,
        open=df_yearly['Open'], high=df_yearly['High'],
        low=df_yearly['Low'], close=df_yearly['Close'],
        name="Brent Price Curve",
        increasing_line_color='#26a69a', 
        decreasing_line_color='#ef5350'
    ),
    secondary_y=True,
)

# 6. Snapshot Annotation
market_context = (
    "<b>SNAPSHOT: MARCH 4, 2026</b><br>"
    "S&P 500: 6,869.50 (+0.75%)<br>"
    "Nasdaq: 22,807.48 (+1.29%)<br>"
    "Brent: $82.07<br>"
    "VIX: 21.15"
)

fig.add_annotation(
    text=market_context, align='left', showarrow=False,
    xref='paper', yref='paper', x=0.02, y=0.98,
    bordercolor='#444', borderwidth=1, borderpad=10,
    bgcolor='rgba(15, 15, 15, 0.9)',
    font=dict(size=12, color="white", family="Courier New")
)

# 7. Final Layout Styling
fig.update_layout(
    template='plotly_dark',
    title="<b>Oil Price Curve vs Market Context</b>",
    xaxis_rangeslider_visible=False,
    paper_bgcolor='black', plot_bgcolor='black',
    margin=dict(l=20, r=20, t=60, b=20),
    width=1200, # Explicit width for image export
    height=800   # Explicit height for image export
)

fig.update_yaxes(title_text="Macro Index (L1)", secondary_y=False, showgrid=False)
fig.update_yaxes(title_text="Brent USD (R1)", secondary_y=True, showgrid=True, gridcolor='#333')

# 8. SAVE OUTPUTS
# Save as interactive HTML
fig.write_html("oil_market_chart.html")

# Save as static Image (Requires kaleido)
try:
    fig.write_image("oil_market_chart.png", scale=2) # scale=2 for high resolution
    print("Success: Image saved as 'oil_market_chart.png'")
except Exception as e:
    print(f"Image export failed: {e}")
    print("Ensure 'pip install kaleido' was successful.")

print("Process Complete.")

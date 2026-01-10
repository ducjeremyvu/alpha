# app.py
import datetime as dt
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

try:
    import yfinance as yf

    YF_AVAILABLE = True
except ImportError:
    YF_AVAILABLE = False

st.set_page_config(page_title="Financial Dashboard", layout="wide")
st.title("📊 Financial Dashboard")

# Sidebar
st.sidebar.header("Settings")
ticker = st.sidebar.text_input("Ticker", value="AAPL").upper()
start_date = st.sidebar.date_input(
    "Start Date", dt.date.today() - dt.timedelta(days=120)
)
end_date = st.sidebar.date_input("End Date", dt.date.today())
interval = st.sidebar.selectbox("Interval", ["1d", "1h", "30m", "15m", "5m"])


@st.cache_data
def load_data(t, start, end, interval):
    if YF_AVAILABLE:
        df = yf.download(t, start=start, end=end, interval=interval)
        if df.empty:
            raise ValueError("No data returned.")
    else:
        # Synthetic fallback data
        rng = pd.date_range(start, end, freq="D")
        price = np.cumsum(np.random.randn(len(rng))) + 150
        df = pd.DataFrame(
            {
                "Open": price + np.random.randn(len(rng)),
                "High": price + np.random.rand(len(rng)),
                "Low": price - np.random.rand(len(rng)),
                "Close": price + np.random.randn(len(rng)),
                "Volume": np.random.randint(10_000, 200_000, len(rng)),
            },
            index=rng,
        )
    df.index.name = "Datetime"
    return df


try:
    data = load_data(ticker, start_date, end_date, interval)
except Exception:
    st.error("Could not load data. Try another ticker or date range.")
    st.stop()

# KPIs
latest = data.iloc[-1]
prev = data.iloc[-2] if len(data) > 1 else latest

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Close", f"{latest['Close']:.2f}")
c2.metric("Open", f"{latest['Open']:.2f}")
c3.metric("High", f"{latest['High']:.2f}")
c4.metric("Low", f"{latest['Low']:.2f}")
c5.metric("Volume", f"{int(latest['Volume']):,}")

# Candlestick Chart
fig = go.Figure(
    data=[
        go.Candlestick(
            x=data.index,
            open=data["Open"],
            high=data["High"],
            low=data["Low"],
            close=data["Close"],
            name=ticker,
        )
    ]
)

fig.update_layout(
    title=f"{ticker} Price Chart", xaxis_title="Date", yaxis_title="Price", height=500
)

st.plotly_chart(fig, use_container_width=True)

st.caption(f"Data from: {data.index.min().date()} to {data.index.max().date()}")


from src.edge_tools.logger import setup_logging

from src.edge_tools.database import get_duckdb_connection
from src.edge_tools.utils.dir import get_sql_query

import plotly.graph_objs as go
import logging
import streamlit as st
import pandas as pd

logger = logging.getLogger(__name__)

setup_logging(logging.DEBUG) 



st.title("📊 Pre-Market Analyse")
st.write("## Pre-Market Prices and Changes")

st.sidebar.header("Settings")

# date_input = st.sidebar.date_input(
#     "Select date",
#     min_value=dates_available[1],
#     max_value=dates_available[-1]
# )


def get_daily_data():
    """
    Pull minute data from DuckDB, convert timestamp to NY timezone,
    resample to daily OHLCV, and return a clean DataFrame.
    """
    query = get_sql_query("get_ny_business_time")

    with get_duckdb_connection() as con:
        df = con.execute(query).df()

    # Ensure timestamp is a proper datetime
    df["ts_ny"] = pd.to_datetime(df["ts_ny"], utc=True).dt.tz_convert("America/New_York")

    # Use timestamp as index
    df = df.set_index("ts_ny").sort_index()

    logger.debug("Minute data preview:\n%s", df.tail())

    # Resample to daily OHLCV
    daily = df.resample("1D").agg({
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
    })

    # Drop days with no data (weekends, holidays)
    daily = daily.dropna(subset=["open"])

    logger.debug("Daily data preview:\n%s", daily.tail())

    return daily


symbol = "US500"


first_30_min_data = get_daily_data()
logger.info(first_30_min_data.head())

def create_candlestick_chart(df: pd.DataFrame, symbol: str) -> go.Figure:
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        increasing_line_color='green',
        decreasing_line_color='red'
    )])
    fig.update_layout(
        title='Daily Candle Stick',
        yaxis_title='Price',
        xaxis_title='Time (NY Time)',
        xaxis_rangeslider_visible=False
    )
    return fig


# at_30_min = filtered_data["close"].iloc[-1]
# logger.debug(f"Price at 30 minutes: {at_30_min}")
# at_open = filtered_data["open"].iloc[0]
# logger.debug(f"Price at open: {at_open}")

# changer_after_30_min = at_30_min - at_open
# logger.debug(f"Change after 30 minutes: {changer_after_30_min}")    
# percent_change_after_30_min = (changer_after_30_min / at_open) * 100
# logger.debug(f"Percent change after 30 minutes: {percent_change_after_30_min}")

# max_distance = filtered_data["high"].max() - filtered_data["low"].min()
# max_distance_percentage = (max_distance / at_open) * 100

# Display candlestick chart
if first_30_min_data is not None:
    # Extract data for plotting

    fig = create_candlestick_chart(first_30_min_data, symbol)
    # Display the chart using Streamlit
    st.plotly_chart(fig)
else:
    st.error("Failed to fetch historical data. Please check your API key and selected instrument.")

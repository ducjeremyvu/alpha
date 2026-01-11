from edge_tools.logger import setup_logging
from edge_tools.time_series.premarket import (
    compute_metrics,
    filter_today_first_30_minutes,
)
from edge_tools.db.database import get_all_available_dates

import plotly.graph_objs as go
import logging
import streamlit as st
import pandas as pd

logger = logging.getLogger(__name__)

setup_logging(logging.DEBUG)

dates_available = get_all_available_dates()

st.title("📊 Pre-Market Analyse")
st.write("## Pre-Market Prices and Changes")

st.sidebar.header("Settings")

# date_input = st.sidebar.date_input(
#     "Select date",
#     min_value=dates_available[1],
#     max_value=dates_available[-1]
# )

date_input = st.sidebar.slider(
    "Select date",
    min_value=dates_available[1],
    max_value=dates_available[-1],
    value=dates_available[-1],
    format="YYYY-MM-DD",
)


symbol = st.sidebar.text_input("Symbol", value="US500")

metrics, data = compute_metrics(symbol=symbol, selected_date=date_input)

filtered_data = filter_today_first_30_minutes(data)


col_open, col_metrics = st.columns([3, 1])

first_30_min_data = filtered_data


def create_candlestick_chart(df: pd.DataFrame, symbol: str) -> go.Figure:
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=df["ny_time"],
                open=df["open"],
                high=df["high"],
                low=df["low"],
                close=df["close"],
                increasing_line_color="green",
                decreasing_line_color="red",
            )
        ]
    )
    fig.update_layout(
        title=f"First 30 Minutes Candlestick Chart for {symbol} on {date_input}",
        yaxis_title="Price",
        xaxis_title="Time (NY Time)",
        xaxis_rangeslider_visible=False,
    )
    return fig


at_30_min = filtered_data["close"].iloc[-1]
logger.debug(f"Price at 30 minutes: {at_30_min}")
at_open = filtered_data["open"].iloc[0]
logger.debug(f"Price at open: {at_open}")

changer_after_30_min = at_30_min - at_open
logger.debug(f"Change after 30 minutes: {changer_after_30_min}")
percent_change_after_30_min = (changer_after_30_min / at_open) * 100
logger.debug(f"Percent change after 30 minutes: {percent_change_after_30_min}")

max_distance = filtered_data["high"].max() - filtered_data["low"].min()
max_distance_percentage = (max_distance / at_open) * 100

# Display candlestick chart
if first_30_min_data is not None:
    # Extract data for plotting

    fig = create_candlestick_chart(first_30_min_data, symbol)
    # Display the chart using Streamlit
    col_open.plotly_chart(fig)
else:
    st.error(
        "Failed to fetch historical data. Please check your API key and selected instrument."
    )


container_metrics = col_metrics.container()


container_metrics.header("Metrics")
container_metrics.metric("Change After 30 Min", f"{percent_change_after_30_min:.2f} %")
container_metrics.metric("Max Distance (%)", f"{max_distance_percentage:.2f} %")


# container_metrics.metric("Tokyo Change (%)", f"{metrics['tokyo_change_percent']:.2f}%")
# container_metrics.metric("London Change (%)", f"{metrics['london_change_percent']:.2f}%")
# container_metrics.metric("T-60 Change (%)", f"{metrics['t_minus_60_change_percent']:.2f}%")
st.json(metrics)

st.dataframe(filtered_data)

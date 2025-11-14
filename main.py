# base modules 
from src.edge_tools.logger import setup_logging
from src.edge_tools.database import get_duckdb_connection
from src.edge_tools.dir import get_sql_query

# importing testing modules from
from src.edge_tools.database import insert_minute_file_data
from src.edge_tools.open import candlestick_plot, ny_open_30_minute, plot_all_us500_and_save

from src.edge_tools.analytics.normalize import add_midpoint_value, normalize_data

import logging

# python modules 
from datetime import datetime
import streamlit as st
from datetime import date, time
import pandas as pd
from typing import List, Dict

import mplfinance as mpf

import subprocess
import typer

logger = logging.getLogger(__name__)

selected_date = datetime(2025, 11, 5)


def normalizing_data():
    df = ny_open_30_minute()

    df["typical_price"] = df.apply(lambda x: add_midpoint_value(x), axis=1)
    logger.info(df.head())

    dates = df["time"].dt.date.unique()

    normalized_df = pd.DataFrame()
    for dt in dates[:3]: 
        filtered_data = df[df["time"].dt.date == dt]
        logger.debug(f"Filtered data: {filtered_data}")
        open_price = filtered_data[filtered_data["time"].dt.time == time(9,30)].iloc[0]["typical_price"]
        logger.debug(f"Assigned Open Price {open_price}")
        normalized_data = normalize_data(filtered_data, open_price)
        logger.debug(normalized_data)
        normalized_df = pd.concat([normalized_df, normalized_data])

    logger.debug(normalized_df.reset_index())
    
    
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



def main():
    setup_logging(logging.DEBUG) 

    logger.info("NEW PROCESS: running insert minute data")
    insert_minute_file_data()

    # normalizing_data()
    logger.info(get_daily_data())

if __name__=='__main__':
    main()

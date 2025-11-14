from src.edge_tools.database import insert_minute_file_data, get_duckdb_connection
from src.edge_tools.dir import get_sql_query

from typing import List
from datetime import datetime
import pandas as pd
import logging
import mplfinance as mpf

logger = logging.getLogger(__name__)

def ny_open_30_minute():
    with get_duckdb_connection() as con:
        query = get_sql_query("get_first_30_min.sql")
        result = con.execute(query).df()
        logger.debug(f"Last 5 df results: {result.tail()}")
        result.rename(columns={"ts_ny":"time"}, inplace=True)        
        return result

def get_data_from_specific_date(opening_data: pd.DataFrame, selected_date: datetime) -> pd.DataFrame:
    return opening_data[opening_data["time"].dt.date == selected_date]


def get_available_dates(df: pd.DataFrame) -> List[datetime]:
    dates = df["time"].dt.date.unique()
    logger.debug(f"Total number of available dates: {len(dates)}")
    logger.debug(f"Last 5 Entries of available dates: {dates[-5:]}")
    return dates

def plot_and_save(df: pd.DataFrame, date_string: str = None):
    if date_string is None: 
        date_string = date.today().strftime("%Y%m%d")

    logger.debug(f"Created Date String: {date_string}")

    mother_path = "/Users/ducjeremyvu/trading/images/US500/"
    filename = "US500_" + date_string +"_opening.png"
    file_path = mother_path + filename
    logger.debug(f"Path and Filename: {file_path}")
    plot = mpf.plot(df,type='candle',style='yahoo',savefig=file_path)
    return plot



def candlestick_plot(opening_data: pd.DataFrame):
    dates_available = get_available_dates(opening_data)
    opening_data.index = opening_data["time"]

    for dt in dates_available: #get the most recent 5 dates
        date_string = dt.strftime("%Y%m%d")
        logger.debug(f"Datestring created: {date_string}")
        date_specific_data = get_data_from_specific_date(opening_data, dt)
        logger.debug(f"Head of date specific data: {date_specific_data.head()}")
        plot_and_save(date_specific_data, date_string)


def plot_all_us500_and_save():
    """
    Wrapper function that plots all available dates for US500 for first 30 min open
    
    """
    opening_data = ny_open_30_minute()
    candlestick_plot(opening_data)

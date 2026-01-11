from ..load import ny_open_30_minute_by_date
from ..analytics.open import ny_open_30_minute
from datetime import date
import pandas as pd
import logging
import mplfinance as mpf
from ..analytics.utils import get_available_dates, get_data_from_specific_date

logger = logging.getLogger(__name__)

__all__ = ["ny_open_30_minute_by_date"]


def plot_and_save(df: pd.DataFrame, date_string: str = None):
    if date_string is None:
        date_string = date.today().strftime("%Y%m%d")

    logger.debug(f"Created Date String: {date_string}")

    mother_path = "/Users/ducjeremyvu/trading/images/US500/"
    filename = "US500_" + date_string + "_opening.png"
    file_path = mother_path + filename
    logger.debug(f"Path and Filename: {file_path}")
    plot = mpf.plot(df, type="candle", style="yahoo", savefig=file_path)
    return plot


def candlestick_plot(opening_data: pd.DataFrame):
    dates_available = get_available_dates(opening_data)
    opening_data.index = opening_data["time"]

    for dt in dates_available:  # get the most recent 5 dates
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

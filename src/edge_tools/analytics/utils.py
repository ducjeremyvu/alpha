import pandas as pd
import logging
from datetime import datetime
from typing import List

logger = logging.getLogger(__name__)


def get_data_from_specific_date(
    opening_data: pd.DataFrame, selected_date: datetime
) -> pd.DataFrame:
    return opening_data[opening_data["time"].dt.date == selected_date]


def get_available_dates(df: pd.DataFrame) -> List[datetime]:
    dates = df["time"].dt.date.unique()
    logger.debug(f"Total number of available dates: {len(dates)}")
    logger.debug(f"Last 5 Entries of available dates: {dates[-5:]}")
    return dates

def convert_to_timestamp(df):
    """
    convert ny time zone to utc, need to rename
    """
    if df["time"].dt.tz is None:
        df["time"] = df["time"].dt.tz_localize("America/New_York")
    df["time"] = df["time"].dt.tz_convert("UTC")
    df["time"] = df["time"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    logger.debug(f"Converted datetime to timestamp   \n {df.head(10)}")
    return df
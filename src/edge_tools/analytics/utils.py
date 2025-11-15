import pandas as pd
import logging
from datetime import datetime
from typing import List

logger = logging.getLogger(__name__)


def get_data_from_specific_date(opening_data: pd.DataFrame, selected_date: datetime) -> pd.DataFrame:
    return opening_data[opening_data["time"].dt.date == selected_date]


def get_available_dates(df: pd.DataFrame) -> List[datetime]:
    dates = df["time"].dt.date.unique()
    logger.debug(f"Total number of available dates: {len(dates)}")
    logger.debug(f"Last 5 Entries of available dates: {dates[-5:]}")
    return dates
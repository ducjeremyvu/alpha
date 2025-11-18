from edge_tools.open import ny_open_30_minute

import logging
import pandas as pd
from datetime import time

logger = logging.getLogger(__name__)


def add_midpoint_value(row):
    """
    function to calculate midpoint value
    """
    typical_price = (row["high"] + row["low"] + row["close"]) / 3
    return round(typical_price, 2)


def normalize_data(df: pd.DataFrame, anchor_price) -> pd.DataFrame:
    """
    adding a column with no
    """
    df["normalized_price"] = df.apply(
        lambda x: (x["typical_price"] / anchor_price) - 1, axis=1
    )
    return df


def normalizing_data():
    df = ny_open_30_minute()

    df["typical_price"] = df.apply(lambda x: add_midpoint_value(x), axis=1)
    logger.info(df.head())

    dates = df["time"].dt.date.unique()

    normalized_df = pd.DataFrame()
    for dt in dates[:3]:
        filtered_data = df[df["time"].dt.date == dt]
        logger.debug(f"Filtered data: {filtered_data}")
        open_price = filtered_data[filtered_data["time"].dt.time == time(9, 30)].iloc[
            0
        ]["typical_price"]
        logger.debug(f"Assigned Open Price {open_price}")
        normalized_data = normalize_data(filtered_data, open_price)
        logger.debug(normalized_data)
        normalized_df = pd.concat([normalized_df, normalized_data])

    logger.debug(normalized_df.reset_index())

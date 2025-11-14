import logging
import pandas as pd

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
    df["normalized_price"] = df.apply(lambda x: (x["typical_price"]/anchor_price) - 1, axis=1)
    return df

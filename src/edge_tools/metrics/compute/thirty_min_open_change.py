from ..base import MetricDefinition
import logging

logger = logging.getLogger(__name__)


def calculate_change(df, start_value: str = "open", end_value: str = "close"):
    """
    Calculates absolute and relative change between two OHLCV columns
    on a given df slice (e.g., first 30 minutes).

    Returns:
        {
            "absolute_change": float,
            "relative_change": float
        }
    """
    if df.shape[0] == 0:
        logger.info("df has no data")
        return {"absolute_change": None, "relative_change": None}

    starting_price = df.iloc[0][start_value]
    ending_price = df.iloc[-1][end_value]

    logger.debug(f"Starting price: {starting_price}, Ending price: {ending_price}")

    absolute_change = ending_price - starting_price
    relative_change = absolute_change / starting_price

    return {
        "absolute_change": round(absolute_change, 2),
        "relative_change": round(relative_change, 4),
    }


def compute_thirty_min_open_change_absolute(df):
    return calculate_change(df)["absolute_change"]


def compute_thirty_min_open_change_relative(df):
    return calculate_change(df)["relative_change"] * 100


metric_thirty_min_open_change_abs = MetricDefinition(
    name="thirty_min_us_open_change_abs",
    description="Absolute $ change from US open to 30-minute close",
    dataset="us_open_30m",
    unit="$",
    compute=compute_thirty_min_open_change_absolute,
)

metric_thirty_min_open_change_rel = MetricDefinition(
    name="thirty_min_us_open_change_rel",
    description="Relative % change from US open to 30-minute close",
    dataset="us_open_30m",
    unit="%",
    compute=compute_thirty_min_open_change_relative,
)

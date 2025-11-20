"""Supporting helpers for the context replay analysis pipeline."""

from duckdb import DuckDBPyConnection
from pandas import DataFrame
import pandas as pd
from pandas.api.types import (
    is_datetime64_any_dtype,
    is_object_dtype,
    is_timedelta64_dtype,
)
from edge_tools.utils.dir import get_sql_query
from edge_tools.db import get_duckdb_connection
from edge_tools.utils.logger import setup_logging
from edge_tools.analytics.utils import convert_to_timestamp
# from edge_tools.load import ny_open_30_minute_by_date # see idea intention below

from pathlib import Path
from typing import Any, Sequence, Dict

import logging
import json

logger = logging.getLogger(__name__)


SQL_FILENAME = "query_context_replay"

#### idea intention is to add 30 min data, instead of making frontend run 2 api requests.
# def load_thirty_minutes(con, date):
#     res = ny_open_30_minute_by_date(con, date)


def read_query_in_same_directory(query_name: str, **params: Any) -> str:
    """
    Load an SQL query that lives next to this script file.

    Args:
        query_name: The SQL filename (without path) to resolve.
        **params: Template parameters that are forwarded to `get_sql_query`.

    Returns:
        Rendered SQL text.
    """
    HERE = Path(__file__).resolve().parent
    logger.debug(f"HERE variable: {HERE}")
    query = get_sql_query(query_name, HERE, **params)
    logger.debug("Loaded context replay query next to module", extra={"query_name": query_name, **params})
    return query


def get_context_replay_data(
    con: DuckDBPyConnection, date: str, symbol: str = "US500"
) -> DataFrame:
    """
    Query the context replay dataset via DuckDB.

    Args:
        con: DuckDB connection used to execute the SQL.
        date: Date string to parameterize the query.
        symbol: Symbol identifier to scope the returned rows.

    Returns:
        Context replay rows in a pandas DataFrame.
    """
    params = {"symbol": symbol, "datestring": date}

    query = read_query_in_same_directory(SQL_FILENAME, **params)
    data = con.execute(query).df()
    logger.info("Fetched context replay rows", extra={"symbol": symbol, "date": date, "row_count": len(data)})
    return data


def slice_last_sixty_minutes(df: DataFrame) -> DataFrame:
    """Return the last 60 rows to focus on the most recent hour."""
    return df.iloc[-60:]


def get_prev_day_business_hours(df: DataFrame) -> DataFrame:
    if df.empty:
        return df
    """Return the rows covering the prior business day (30 + 6h of 60m bars)."""
    selection_rows = 30 + 6 * 60
    selected = df.iloc[:selection_rows]
    logger.debug("Previous day business hours slice", extra={"row_count": len(selected)})
    return selected


def infer_timestamp_column(
    df: DataFrame, fallback_names: Sequence[str] | None = None
) -> str:
    """
    Choose the most likely timestamp column in `df`, using dtype detection and optional fallbacks.
    """
    fallback_names = fallback_names or (
        "ts_ny",
        "time",
        "timestamp",
        "datetime",
        "time_ny",
    )
    datetime_columns = [
        col
        for col in df.columns
        if is_datetime64_any_dtype(df[col].dtype) or is_timedelta64_dtype(df[col].dtype)
    ]

    convertible_columns = []
    if len(datetime_columns) != 1:
        for col in df.columns:
            if col in datetime_columns or not is_object_dtype(df[col].dtype):
                continue
            sample = df[col].dropna()
            if sample.empty:
                continue
            sample = sample.head(5)
            try:
                pd.to_datetime(sample, errors="raise")
            except (ValueError, TypeError):
                continue
            convertible_columns.append(col)
            if len(convertible_columns) > 1:
                break

    timestamp_candidates = list(dict.fromkeys(datetime_columns + convertible_columns))
    if len(timestamp_candidates) == 1:
        return timestamp_candidates[0]

    lowered_columns = {col.lower(): col for col in df.columns}
    for candidate in fallback_names:
        if candidate in lowered_columns:
            return lowered_columns[candidate]

    raise ValueError("expected timestamp column when resampling to 15 min")


def resample_mfifteen(df: DataFrame) -> DataFrame:
    """
    Resample minute-level bars to 15 minute OHLCV buckets.
    """
    if df.empty:
        logger.debug("Skipping 15min resample because frame is empty")
        return df.copy()

    timestamp_column = infer_timestamp_column(df)

    frame = df.assign(
        **{
            timestamp_column: pd.to_datetime(df[timestamp_column], errors="coerce"),
        }
    ).set_index(timestamp_column)

    agg = {
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
    }

    result = (
        frame.resample("15min", label="left", closed="left")
        .agg(agg)
        .dropna(subset=["open"])
        .reset_index()
    )
    logger.debug("Resampled 15min bars", extra={"result_rows": len(result)})
    return result


def resample_hourly(df: DataFrame) -> DataFrame:
    """
    Resample minute-level bars to hourly OHLCV buckets.
    """
    if df.empty:
        logger.debug("Skipping hourly resample because frame is empty")
        return df.copy()

    timestamp_column = infer_timestamp_column(df)

    frame = df.assign(
        **{
            timestamp_column: pd.to_datetime(df[timestamp_column], errors="coerce"),
        }
    ).set_index(timestamp_column)

    agg = {
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
    }

    result = (
        frame.resample("1h", label="left", closed="left")
        .agg(agg)
        .dropna(subset=["open"])
        .reset_index()
    )
    logger.debug("Resampled hourly bars", extra={"result_rows": len(result)})
    return result


def fetch_context_replay_data_and_calculate_metrics(
    con: DuckDBPyConnection,
    date: str
) -> Dict[str, Any]:
    """
    Load context replay rows for `date` then resample and compute previous-day metrics.

    Args:
        con: DuckDB connection to run the context replay query.
        date: Date string parameter that matches the dataset query.

    Returns:
        A payload with raw, sliced, and resampled data plus previous-day metrics.
    """

    data = get_context_replay_data(con, date=date)
    data.rename(columns={"ts_ny": "time"}, inplace=True)
    logger.info(data.head())
    data.drop(columns=["symbol"], inplace=True)
    data = convert_to_timestamp(data)
    logger.info(data.head())
    data_t_minus_sixty = slice_last_sixty_minutes(data)
    data_prev_day_business_hours = resample_mfifteen(get_prev_day_business_hours(data))
    data_resampled_m15 = resample_mfifteen(data)
    data_resampled_hourly = resample_hourly(data)

    logger.info(
        "Built derived dataset for context replay",
        extra={
            "total_rows": len(data),
            "last_60_rows": len(data_t_minus_sixty),
            "prev_day_rows": len(data_prev_day_business_hours),
            "m15_rows": len(data_resampled_m15),
            "hourly_rows": len(data_resampled_hourly),
        },
    )

    ###############
    ### METRICS ###
    ###############

    ###### PREVIOUS DAY ######

    # data_prev_day_business_hours["absolute_candle_change"] = (data_prev_day_business_hours["close"] - data_prev_day_business_hours["open"]).abs()

    # prev_day_avg_candle_size = data_prev_day_business_hours["absolute_candle_change"].mean()

    if data_prev_day_business_hours.empty:
        logger.warning("Previous day business hours slice is empty, cannot compute metrics")
        prev_day_metrics = {}
    else:
        prev_day_high = data_prev_day_business_hours["high"].max()
        prev_day_low = data_prev_day_business_hours["low"].min()
        prev_day_close = data_prev_day_business_hours.iloc[-1]["close"]
        prev_day_open = data_prev_day_business_hours.iloc[0]["open"]
        prev_day_change = round(prev_day_close - prev_day_open,2)
        prev_day_change_perc = round((prev_day_change / prev_day_open) * 100, 2)
        prev_day_range = round(prev_day_high - prev_day_low, 2)
        prev_day_change_to_range = abs(round(prev_day_change / prev_day_range,2))

        prev_day_metrics = {
            "prev_day_open": prev_day_open,
            "prev_day_high": prev_day_high,
            "prev_day_low": prev_day_low,
            "prev_day_close": prev_day_close,
            "prev_day_change": prev_day_change,
            "prev_day_change_perc": prev_day_change_perc,
            "prev_day_range": prev_day_range,
            "prev_day_change_to_range": prev_day_change_to_range,
            # "prev_day_avg_candle_size" : prev_day_avg_candle_size
        }

    ###############
    ### Response ###
    ###############

    response = {
        "symbol": "US500",
        "data": {
            "all": data.to_dict("records"),
            "t_minus_60": data_t_minus_sixty.to_dict("records"),
            "prev_day_business_hours": data_prev_day_business_hours.to_dict("records"),
            "m15": data_resampled_m15.to_dict("records"),
            "h1": data_resampled_hourly.to_dict("records"),
        },
        "metrics": {"prev_day": prev_day_metrics},
    }

    logger.info("Context replay prev day metrics", extra={"prev_day": prev_day_metrics})
    return response


if __name__ == "__main__":
    setup_logging(logging.DEBUG)

    con = get_duckdb_connection()
    fetch_context_replay_data_and_calculate_metrics(con)
    con.close()

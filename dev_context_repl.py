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

from pathlib import Path
from typing import Any, Sequence

import logging


logger = logging.getLogger(__name__)


# starting this script, functions are always written, taking a con object.


SQL_FILENAME = "query_context_replay"


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
    logger.debug(f"Loaded the following query: \n {query}")
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
    logger.debug(f"Created data for context_replay: \n {data}")
    return data


def slice_last_sixty_minutes(df: DataFrame) -> DataFrame:
    return df.iloc[-60:]


def get_prev_day_business_hours(df):
    # 30 + 6*60 min
    selection_rows = 30 + 6 * 60
    return df.iloc[:selection_rows]


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
        return df.copy()

    timestamp_column = infer_timestamp_column(df)

    frame = df.assign(
        **{
            timestamp_column: pd.to_datetime(df[timestamp_column], errors="coerce"),
        }
    ).set_index(timestamp_column)

    agg = {
        "symbol": "first",
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
    return result


def resample_hourly(df: DataFrame) -> DataFrame:
    """
    Resample minute-level bars to hourly OHLCV buckets.
    """
    if df.empty:
        return df.copy()

    timestamp_column = infer_timestamp_column(df)

    frame = df.assign(
        **{
            timestamp_column: pd.to_datetime(df[timestamp_column], errors="coerce"),
        }
    ).set_index(timestamp_column)

    agg = {
        "symbol": "first",
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
    }

    return (
        frame.resample("1h", label="left", closed="left")
        .agg(agg)
        .dropna(subset=["open"])
        .reset_index()
    )


def main() -> None:
    """Entry point that configures logging and fetches context replay data."""
    setup_logging(logging.DEBUG)
    con = get_duckdb_connection()

    ##############
    #### DATA ####
    ##############

    data = get_context_replay_data(con, date="2025-11-06")
    data.rename(columns={"ts_ny": "time"}, inplace=True)
    data_t_minus_sixty = slice_last_sixty_minutes(data)
    data_prev_day_business_hours = get_prev_day_business_hours(data)
    data_resampled_m15 = resample_mfifteen(data)
    data_resampled_hourly = resample_hourly(data)

    ###############
    ### METRICS ###
    ###############

    ###### PREVIOUS DAY ######

    # data_prev_day_business_hours["absolute_candle_change"] = (data_prev_day_business_hours["close"] - data_prev_day_business_hours["open"]).abs()

    # prev_day_avg_candle_size = data_prev_day_business_hours["absolute_candle_change"].mean()

    prev_day_high = data_prev_day_business_hours["high"].max()
    prev_day_low = data_prev_day_business_hours["low"].min()
    prev_day_close =data_prev_day_business_hours.iloc[-1]["close"]
    prev_day_open = data_prev_day_business_hours.iloc[0]["open"]
    prev_day_change = prev_day_close - prev_day_open
    prev_day_change_perc = round(prev_day_change / prev_day_open, 4)*100
    prev_day_range = round(prev_day_high - prev_day_low, 2)
    prev_day_change_to_range = prev_day_change / prev_day_range
    
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


    response = {
        "data": {
            "all": data.to_dict(),
            "t_minus_60": data_t_minus_sixty.to_dict(),
            "prev_day_business_hours": data_prev_day_business_hours.to_dict(),
            "m15": data_resampled_m15.to_dict(),
            "h1": data_resampled_hourly.to_dict(),
        },
        "metrics": {
            "prev_day":prev_day_metrics
        },
    }

    logger.info(response["metrics"])


if __name__ == "__main__":

    main()


#########################################
#### Project Context replay dashboard ###
#########################################


"""
# Context Replay dashboard 
    - This gonna be a dashboard for my daily 30 min scalping 
    - I need data from previous day open to current day open. (done)
    - data_whole_day (open)
    - Need to chop to differen parts (done)
    - Resampled by m15  (done)
    - Resampled by h1   (done)
    - Last 60 min. In m1 (done)
    - premarket: prev close to cur day open in hours 

values: 
    - Prev day: requires previous day data 
	    - ohlc 
	    - change and percentage change (done)
        - added range from low to high
    - Premarket volatility 

optional:
	- values for different times 

"""


"""
First Step: create query the data given the day 

input date > query > data
"""

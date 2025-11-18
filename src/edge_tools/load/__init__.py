from ..db import get_duckdb_connection
from ..utils.dir import get_sql_query


import pandas as pd
import logging


logger = logging.getLogger(__name__)


def ny_open_30_minute_by_date(datestring: str) -> pd.DataFrame:
    """
    This function downloads first US Open data for 30 Minutes for the CFD US500
    filtered by inputstring date in the form of '2025-11-06

    # maybe add checker for format

    result: Pandas DataFrame wiht timestamp as index, open, high, low, volume values

    """
    with get_duckdb_connection() as con:
        params = {"datestring": datestring}
        query = get_sql_query("query_us500_first_30_min_by_date", **params)
        result = con.execute(query).df()
        logger.debug(f"Last 5 df results: {result.tail()}")
        result.rename(columns={"ts_ny": "time"}, inplace=True)
        return result.drop(columns=["symbol"])


def load_us_open_thirty_minute_data():
    """
    Loads all data of the first 30 min after us open
    """

    pass



def get_daily_data():
    """
    Pull minute data from DuckDB, convert timestamp to NY timezone,
    resample to daily OHLCV, and return a clean DataFrame.
    """
    query = get_sql_query("get_ny_business_time")

    with get_duckdb_connection() as con:
        df = con.execute(query).df()

    # Ensure timestamp is a proper datetime
    df["ts_ny"] = (
        pd
        .to_datetime(df["ts_ny"], utc=True)
        .dt
        .tz_convert("America/New_York")
    )

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

# base modules 
from src.edge_tools.logger import setup_logging
from src.edge_tools.database import get_duckdb_connection
from src.edge_tools.dir import get_sql_query

# importing testing modules from
from src.edge_tools.open import ny_open_30_minute
from src.edge_tools.db.data import ny_open_30_minute_by_date
from src.edge_tools.analytics.normalize import add_midpoint_value, normalize_data

import logging

# python modules 
from datetime import datetime
from datetime import time
import pandas as pd
from typing import List, Dict

import duckdb


logger = logging.getLogger(__name__)

selected_date = datetime(2025, 11, 5)


def normalizing_data():
    df = ny_open_30_minute()

    df["typical_price"] = df.apply(lambda x: add_midpoint_value(x), axis=1)
    logger.info(df.head())

    dates = df["time"].dt.date.unique()

    normalized_df = pd.DataFrame()
    for dt in dates[:3]: 
        filtered_data = df[df["time"].dt.date == dt]
        logger.debug(f"Filtered data: {filtered_data}")
        open_price = filtered_data[
                        filtered_data["time"].dt.time == time(9,30)
                        ].iloc[0]["typical_price"]
        logger.debug(f"Assigned Open Price {open_price}")
        normalized_data = normalize_data(filtered_data, open_price)
        logger.debug(normalized_data)
        normalized_df = pd.concat([normalized_df, normalized_data])

    logger.debug(normalized_df.reset_index())
    

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



# MENU = {
#     "1": ("Run File Insertion", run_file_insertion),
#     "2": ("Run API", run_api),
#     "3": ("Ingest Data", ingest_data),
#     "4": ("Run Streamlit App", run_streamlit),
#     "x": ("Exit", exit_program),
# }

# def show_menu():
#     print("\n=== DJV Control Panel ===")
#     for key, (label, _) in MENU.items():
#         print(f"{key}. {label}")
#     print()


#######
"""
I want to call data, (open data) and then compute metrics. 

- first i need to create table where i can put the metrics, 
- then i need some naming convention 

"""

def calcualate_change(df, start_value: str = "open", end_value: str = "close"):
    # moved to metrics/compute/thirty_min_open_change.py
    """
    In:
        df: dataframe with ohlcv values, 
        start_value: compute the change from open or close value, defaults to open
        end_value: compute change to open or close value, defaults to close

    Returns: 
        dictionary with absolute and relative change
        {
            absolute: 40.00, #2 decimal precision
            relative: 0.0324 #4 decimal precision
        }
    """
    
    starting_price = df.iloc[0, :][start_value]
    ending_price = df.iloc[-1, :][end_value]
    logger.debug(f"""
                 \n select starting price: {starting_price}  
                 \n selected ending price: {ending_price}
    """)

    absolute_change = ending_price - starting_price
    percentage_change = absolute_change / starting_price
    return {
        "absolute_change": round(absolute_change, 2), 
        "percentage_change": round(percentage_change, 4)
    }


"""
Current Goals: 

- write process for computing change 
    
- write process to store that data 
    - first probably need a query writing data. 
    - need a query that creates the table 

    - requires Metric Definition 
        - i will instantiate metrics and metrics_store     

- write loop so it stores for multiple dates 
    this would be fairly easy to write a system that checks for the 
    date dates available, then queries dates 
    for the metric, then fetch and write values for missing dates 



"""

from src.edge_tools.metrics.compute.thirty_min_open_change import (
    metric_thirty_min_open_change_abs, 
    metric_thirty_min_open_change_rel,
    compute_thirty_min_open_change_absolute,
    compute_thirty_min_open_change_relative
    )

from src.edge_tools.metrics.base import MetricDefinition
from src.edge_tools.metrics.registry import ensure_metric_registered

metrics = [metric_thirty_min_open_change_abs, metric_thirty_min_open_change_rel]

def compute_metric_for_date(
        con: duckdb.DuckDBPyConnection, 
        metric: MetricDefinition, 
        date_str: str, 
        symbol: str
    ):

    if metric.dataset == "us_open_30m":
        params = {
            "symbol": symbol,
            "datestring": date_str
        }
        query = get_sql_query("query_us_open_30_min_m1_by_symbol_and_date", **params)
        logger.debug(query)
        data = con.execute(query).df()

    metric_id = ensure_metric_registered(con, metric)
    value = metric.compute(data)
    
        # Store event
    row = con.execute("""
        INSERT OR IGNORE INTO metric_events (date, symbol, metric_id, metric_value)
        VALUES (?, ?, ?, ?)
        RETURNING date, symbol, metric_id;
    """, [date_str, symbol, metric_id, value])

    df = row.df() 
    # the cursor if, run again, wont show the data twice, so u have to store immediately
    # after calling row.df(), calling it a second time yields None

    logger.debug(df)
    # if df.shape
    if df.empty:
        logger.info(f"{metric.name} for {symbol} for {date_str} ignored due to existence of data.")
    else:
        logger.info(f"{metric.name} for {symbol} for {date_str} Inserted.")
    return value
#### creating the tables 

import functools

def ensure_connection(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        user_provided = "con" in kwargs and kwargs["con"] is not None

        # If con not provided, create our own
        if not user_provided:
            con = get_duckdb_connection()
            kwargs["con"] = con
            try:
                logger.debug("Running creating a new con")
                return func(*args, **kwargs)
            finally:
                con.close()
        else:
            logger.debug("Running with provided con")
            return func(*args, **kwargs)

    return wrapper

@ensure_connection
def get_n_dates(
    symbol: str = "US500", 
    n: int = 50, 
    order: str = "desc", 
    con = None,
    start: str = '09:30',
    end: str = '10:00'
):
    """
    description, describe the inputs
    
    """
    dates = con.execute(f""" 
        SELECT distinct (time AT TIME ZONE 'America/New_York')::date AS date
        FROM ohlcv_minute
        WHERE (
                time AT TIME ZONE 'America/New_York'
            )::time >= time '{start}'
            AND (
                time AT TIME ZONE 'America/New_York'
            )::time < time '{end}'
            AND symbol == '{symbol}'                            
        order by date {order}
        limit {n};                
    """).df()["date"].to_list()

    output_logger = f"""Output for function get_dates \n {dates}"""

    logger.info(output_logger)
    return dates

@ensure_connection
def check_available_dates(metric: MetricDefinition, con = None) -> List[datetime]:
    metric_id = ensure_metric_registered(con, metric=metric)
    
    dates_processed = con.execute(
        f"""
            SELECT date from metric_events where metric_id == {metric_id} order by date
        """
    ).df()

    return dates_processed

"""
ive written a function to check all the dates present with 

goal: want to write automation, to check available dates to automate that. 
but neither do i have an automated system nor do i need that kind of automation, so i could just manually do these 
i could write interfaces for that.
TODO: 

"""
def pivot_metrics(con):

    merged_cte = """
        WITH merged AS (
            SELECT 
                me.date,
                me.symbol,
                m.metric_name,
                me.metric_value AS value
            FROM metric_events me
            LEFT JOIN metrics m USING (metric_id)
        )
    """

    # Create the column list with manually quoted identifiers
    cols = con.execute(f"""
        {merged_cte}
        SELECT string_agg('"' || metric_name || '"', ', ')
        FROM (SELECT DISTINCT metric_name FROM merged)
    """).fetchone()[0]

    sql = f"""
        {merged_cte}
        SELECT *
        FROM merged
        PIVOT (
            ANY_VALUE(value)
            FOR metric_name IN ({cols})
        )
        ORDER BY date, symbol;
    """
    logger.debug(sql)
    return con.execute(sql).df()


def main():
    setup_logging(logging.DEBUG) 

    # df = ny_open_30_minute_by_date("2025-11-06")

    con = get_duckdb_connection()

    dates_available = get_n_dates(n=60,con=con)

    date_strings = [date.strftime("%Y-%m-%d") for date in dates_available]
    # logger.debug(date_strings)

    # for metric in metrics:
    #     logger.debug(f"Processing the following metric: {metrics}")
    #     written_dates = check_available_dates(metric=metric_thirty_min_open_change_abs)["date"].to_list()
    #     written_dates = [date.strftime("%Y-%m-%d") for date in written_dates]
    #     logger.debug(f"Written Dates: {written_dates}")
    #     pending_dates = set(date_strings) - set(written_dates)
    #     logger.debug(f"Pending Dates to be processed: {pending_dates}")
    #     for date in pending_dates:
    #         compute_metric_for_date(
    #             con, 
    #             metric,
    #             date_str = date,
    #             symbol = "US500"
    #         )
    data = pivot_metrics(con)
    logger.info(data)
    con.close()

    

if __name__=='__main__':
    main()

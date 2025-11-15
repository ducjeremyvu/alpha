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
        result.rename(columns={"ts_ny":"time"}, inplace=True)        
        return result.drop(columns=["symbol"])

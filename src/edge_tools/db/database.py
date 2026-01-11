### soon to be deprecated

from ..utils.dir import get_sql_query

from . import get_duckdb_connection

from ..ingest import insert_minute_file_data

import logging

__all__ = ["insert_minute_file_data"]

logger = logging.getLogger(__name__)


def get_all_available_dates():
    with get_duckdb_connection() as con:
        query = get_sql_query("get_all_dates.sql")
        result = con.execute(query).fetchall()
        # logger.debug(f"Query Result: {result}")
        dates = sorted([row[0] for row in result])
        logger.debug(
            f"Available dates in database: {dates[0:5]}"
        )  # Log the last few dates
        logger.info(f"Total available dates: {len(dates)}")
    return dates[1:]  # Exclude the first date if needed


if __name__ == "__main__":
    pass

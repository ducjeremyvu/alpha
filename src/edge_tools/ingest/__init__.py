from .files import (
    assign_data_path,
    get_unwritten_files,
    map_symbols_to_files,
    build_symbol_file_records,
    mark_file_as_done,
)
from ..db import get_duckdb_connection
from ..utils.dir import get_sql_query


import logging
from pathlib import Path

HERE = Path(__file__).resolve().parent

TIMEFRAMES = ["Minute", "Daily", "Weekly", "Hour"]

logger = logging.getLogger(__name__)


def insert_minute_file_data():
    """
    Inserts file data into the DuckDB database from CSV files in the data folder.
    Processes files that have not been marked as done, extracts symbols, builds records,
    executes SQL insert queries, and marks files as done after processing.

    Args:
        None

    Returns:
        None
    """
    query_name = "import_minute_data_with_symbol_from_csv.sql"

    with get_duckdb_connection() as con:
        folder = assign_data_path()
        files = get_unwritten_files(folder)

        if files == []:
            logger.info("No new files to process.")
            return

        symbols_extracted = map_symbols_to_files(files)
        records_list = build_symbol_file_records(symbols_extracted)

        for records in records_list:
            params = records.get("parameter")
            path = records.get("path")
            query = get_sql_query(query_name, **params)
            logger.debug("Query : {query}")
            con.execute(query)
            logger.info(
                f"Inserted data for symbol: {params.get('symbol')} from file: {params.get('file_path_csv')}"
            )

            mark_file_as_done(path)


def insert_file_data():
    """
    Inserts file data into the DuckDB database from CSV files in the data folder.
    Processes files that have not been marked as done, extracts symbols, builds records,
    executes SQL insert queries, and marks files as done after processing.

    Args:
        None

    Returns:
        None
    """

    query_file_name = "import_data_with_symbol_from_csv"

    with get_duckdb_connection() as con:
        for timeframe in TIMEFRAMES:
            timeframe_lower = timeframe.lower()
            logger.debug(f"Running for Timeframe: {timeframe}")
            folder = assign_data_path()
            files = get_unwritten_files(folder, interval=timeframe)

            if files == []:
                logger.info("No new files to process.")
                pass

            symbols_extracted = map_symbols_to_files(files)
            records_list = build_symbol_file_records(symbols_extracted)

            for records in records_list:
                params = records.get("parameter")
                params["timeframe"] = timeframe_lower
                path = records.get("path")
                query = get_sql_query(query_file_name, HERE, **params)
                logger.debug("Query : {query}")
                con.execute(query)
                logger.info(
                    f"Inserted data for symbol: {params.get('symbol')}, timeframe: {timeframe_lower} from file: {params.get('file_path_csv')}"
                )

                mark_file_as_done(path)

from .files import (
    assign_data_path,
    get_unwritten_files,
    map_symbols_to_files,
    build_symbol_file_records,
    mark_file_as_done,
)
from .resample import align_resample_window, resample_minute_ranges
from ..constants import RESAMPLE_TIMEFRAMES, TIMEFRAME_SOURCE
from ..db.migrations import load_all_tables
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

    load_all_tables()

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
    resample_timeframes = [
        timeframe.strip()
        for timeframe in RESAMPLE_TIMEFRAMES.split(",")
        if timeframe.strip()
    ]

    load_all_tables()

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
                file_start = params.get("file_start")
                file_end = params.get("file_end")
                query = get_sql_query(query_file_name, HERE, **params)
                logger.debug("Query : {query}")
                con.execute(query)
                logger.info(
                    f"Inserted data for symbol: {params.get('symbol')}, timeframe: {timeframe_lower} from file: {params.get('file_path_csv')}"
                )

                if (
                    timeframe_lower == "minute"
                    and TIMEFRAME_SOURCE != "download"
                    and file_start
                    and file_end
                ):
                    aligned_start, aligned_end = align_resample_window(
                        str(file_start), str(file_end)
                    )
                    resample_minute_ranges(
                        resample_timeframes,
                        aligned_start,
                        aligned_end,
                    )

                mark_file_as_done(path)

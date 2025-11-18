from edge_tools.utils.dir import load_query_path
from edge_tools.db import get_duckdb_connection
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

HERE = Path(__file__).resolve().parent

TABLE_REGISTRY = ["create_table_ohlcv_minute", "create_table_metrics"]


def load_all_tables():
    for table in TABLE_REGISTRY:
        create_tables_from_query(table)


def create_tables_from_query(query_name: str) -> None:
    """
    loads the query for creating metrics tables and writes them if they
    do not exit yet.
    """

    logger.debug(HERE)
    path_to_create_metrics_tables = f"{HERE}/{query_name}.sql"
    logger.debug(
        f"Path to the create metrics table query {path_to_create_metrics_tables}"
    )
    query = load_query_path(path_to_create_metrics_tables)

    with get_duckdb_connection() as con:
        res = con.execute(query)
        logger.info(res)

    logger.info(f"Finished running query *{query_name}*")

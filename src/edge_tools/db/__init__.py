import logging
import duckdb
import functools

logger = logging.getLogger(__name__)


def get_duckdb_connection(
    duck_db_path: str = "local.duckdb",
    read_only: bool = False,
) -> duckdb.DuckDBPyConnection:
    """Establishes and returns a connection to a DuckDB database.
    Args:
        duck_db_path (str, optional): Path to the DuckDB database file. Defaults to "local.duckdb".
    Returns:
        duckdb.DuckDBPyConnection: A connection object to the DuckDB database.
    """
    logger.debug(f"Connecting to DuckDB at path: {duck_db_path}")
    con = duckdb.connect(duck_db_path, read_only=read_only)  # ← single file  database
    return con


def delete_table(table_name: str, con: duckdb.DuckDBPyConnection = None) -> None:
    """
    delete a table by entering the table name
    """
    logger.debug(f"Checking if con exist or not: {con}")
    if not con:
        with get_duckdb_connection() as con:
            con.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")
        logger.info(f"Deleted the table {table_name} with external con")

    else:
        con.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")
        logger.info(f"Deleted the table {table_name} with internal con")


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


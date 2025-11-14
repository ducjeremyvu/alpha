import logging
import duckdb


logger = logging.getLogger(__name__)

def get_duckdb_connection(duck_db_path: str = "local.duckdb") -> duckdb.DuckDBPyConnection:
    """Establishes and returns a connection to a DuckDB database.
    Args:
        duck_db_path (str, optional): Path to the DuckDB database file. Defaults to "local.duckdb".
    Returns:
        duckdb.DuckDBPyConnection: A connection object to the DuckDB database.
    """
    logger.debug(f"Connecting to DuckDB at path: {duck_db_path}")
    con = duckdb.connect(duck_db_path)  # ← single file  database
    return con 


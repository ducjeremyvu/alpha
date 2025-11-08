import duckdb


def get_duckdb_connection(duck_db_path: str = "local.duckdb") -> duckdb.DuckDBPyConnection:
    con = duckdb.connect("local.duckdb")  # ← single file  database
    return con 
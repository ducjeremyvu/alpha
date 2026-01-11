import duckdb
import pandas as pd

from edge_tools.db import database as db_database


def test_get_all_available_dates(tmp_path, monkeypatch):
    db_path = tmp_path / "test.duckdb"
    con = duckdb.connect(str(db_path))
    con.execute(
        """
        CREATE TABLE ohlcv_minute (
            symbol TEXT,
            time TIMESTAMPTZ,
            open DOUBLE,
            high DOUBLE,
            low DOUBLE,
            close DOUBLE,
            volume BIGINT
        )
        """
    )
    data = pd.DataFrame(
        {
            "symbol": ["US500", "US500"],
            "time": ["2024-01-02T14:00:00Z", "2024-01-03T14:00:00Z"],
            "open": [1, 1],
            "high": [1, 1],
            "low": [1, 1],
            "close": [1, 1],
            "volume": [1, 1],
        }
    )
    con.register("data", data)
    con.execute("INSERT INTO ohlcv_minute SELECT * FROM data")

    def _get_con():
        return duckdb.connect(str(db_path))

    monkeypatch.setattr(db_database, "get_duckdb_connection", _get_con)

    dates = db_database.get_all_available_dates()

    assert len(dates) == 1
    assert str(dates[0]) == "2024-01-03"

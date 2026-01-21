import duckdb
import pandas as pd

from edge_tools.ingest import resample as resample_module


def _build_db(tmp_path):
    db_path = tmp_path / "resample.duckdb"
    con = duckdb.connect(str(db_path))
    con.execute(
        """
        CREATE TABLE ohlcv_minute (
            symbol TEXT NOT NULL,
            time TIMESTAMPTZ NOT NULL,
            open DOUBLE,
            high DOUBLE,
            low DOUBLE,
            close DOUBLE,
            volume BIGINT,
            PRIMARY KEY (symbol, time)
        )
        """
    )
    con.execute(
        """
        CREATE TABLE ohlcv_hour (
            symbol TEXT NOT NULL,
            time TIMESTAMPTZ NOT NULL,
            open DOUBLE,
            high DOUBLE,
            low DOUBLE,
            close DOUBLE,
            volume BIGINT,
            PRIMARY KEY (symbol, time)
        )
        """
    )
    con.execute(
        """
        CREATE TABLE ohlcv_daily (
            symbol TEXT NOT NULL,
            time TIMESTAMPTZ NOT NULL,
            open DOUBLE,
            high DOUBLE,
            low DOUBLE,
            close DOUBLE,
            volume BIGINT,
            PRIMARY KEY (symbol, time)
        )
        """
    )
    con.execute(
        """
        CREATE TABLE ohlcv_weekly (
            symbol TEXT NOT NULL,
            time TIMESTAMPTZ NOT NULL,
            open DOUBLE,
            high DOUBLE,
            low DOUBLE,
            close DOUBLE,
            volume BIGINT,
            PRIMARY KEY (symbol, time)
        )
        """
    )
    data = pd.DataFrame(
        {
            "symbol": ["GER40", "GER40", "GER40", "GER40"],
            "time": [
                "2024-01-02T14:30:00Z",
                "2024-01-02T14:31:00Z",
                "2024-01-02T15:00:00Z",
                "2024-01-03T14:30:00Z",
            ],
            "open": [1.0, 2.0, 3.0, 4.0],
            "high": [2.0, 3.0, 4.0, 5.0],
            "low": [1.0, 1.5, 2.0, 3.0],
            "close": [1.0, 2.0, 3.0, 4.0],
            "volume": [10, 20, 30, 40],
        }
    )
    con.register("data", data)
    con.execute("INSERT INTO ohlcv_minute SELECT * FROM data")
    con.close()
    return db_path


def test_resample_minute_ranges(tmp_path, monkeypatch):
    db_path = _build_db(tmp_path)

    def _get_con(duck_db_path="local.duckdb", read_only=False):
        return duckdb.connect(str(db_path), read_only=read_only)

    monkeypatch.setattr(resample_module, "get_duckdb_connection", _get_con)

    aligned_start, aligned_end = resample_module.align_resample_window(
        "2024-01-02 14:30:00+00", "2024-01-03 14:31:00+00"
    )
    resample_module.resample_minute_ranges(
        ["15m", "30m", "1h", "1d", "1w", "1d_rth"],
        aligned_start,
        aligned_end,
    )

    con = duckdb.connect(str(db_path))
    assert con.execute("SELECT COUNT(*) FROM ohlcv_15m").fetchone()[0] == 3
    assert con.execute("SELECT COUNT(*) FROM ohlcv_30m").fetchone()[0] == 3
    assert con.execute("SELECT COUNT(*) FROM ohlcv_hour").fetchone()[0] == 3
    assert con.execute("SELECT COUNT(*) FROM ohlcv_daily").fetchone()[0] == 2
    assert con.execute("SELECT COUNT(*) FROM ohlcv_weekly").fetchone()[0] == 1
    assert con.execute("SELECT COUNT(*) FROM ohlcv_daily_rth").fetchone()[0] == 2

    row = con.execute(
        """
        SELECT open, high, low, close, volume
        FROM ohlcv_15m
        WHERE symbol = 'GER40'
          AND time = '2024-01-02T14:30:00Z'
        """
    ).fetchone()
    assert row == (1.0, 3.0, 1.0, 2.0, 30)

import duckdb
import pandas as pd

from edge_tools.backtest.optimizer import run_grid_search, run_walkforward


def _seed_ohlcv_tables(con: duckdb.DuckDBPyConnection) -> None:
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
    con.execute(
        """
        CREATE TABLE ohlcv_hour (
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
    con.execute(
        """
        CREATE TABLE ohlcv_daily (
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

    times_2023 = pd.date_range("2023-01-02 14:00", periods=6, freq="5min", tz="UTC")
    times_2024 = pd.date_range("2024-01-02 14:00", periods=6, freq="5min", tz="UTC")
    minute_data = pd.concat(
        [
            _build_minute_frame(times_2023),
            _build_minute_frame(times_2024),
        ],
        ignore_index=True,
    )
    hour_data = pd.DataFrame(
        {
            "symbol": ["US500", "US500"],
            "time": [
                pd.Timestamp("2023-01-02 14:00", tz="UTC"),
                pd.Timestamp("2024-01-02 14:00", tz="UTC"),
            ],
            "open": [100, 100],
            "high": [102, 102],
            "low": [95, 95],
            "close": [99, 99],
            "volume": [1, 1],
        }
    )
    daily_data = pd.DataFrame(
        {
            "symbol": ["US500", "US500"],
            "time": [
                pd.Timestamp("2023-01-02 00:00", tz="UTC"),
                pd.Timestamp("2024-01-02 00:00", tz="UTC"),
            ],
            "open": [95, 95],
            "high": [110, 110],
            "low": [94, 94],
            "close": [105, 105],
            "volume": [1, 1],
        }
    )

    con.register("minute_data", minute_data)
    con.register("hour_data", hour_data)
    con.register("daily_data", daily_data)
    con.execute("INSERT INTO ohlcv_minute SELECT * FROM minute_data")
    con.execute("INSERT INTO ohlcv_hour SELECT * FROM hour_data")
    con.execute("INSERT INTO ohlcv_daily SELECT * FROM daily_data")


def _build_minute_frame(times: pd.DatetimeIndex) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "symbol": ["US500"] * len(times),
            "time": times,
            "open": [98, 99, 100, 101, 100, 99],
            "high": [100, 101, 103, 102, 101, 100],
            "low": [95, 96, 99, 98, 96, 95],
            "close": [98, 100, 102, 100, 98, 97],
            "volume": [1] * len(times),
        }
    )


def test_run_grid_search_and_walkforward(tmp_path, monkeypatch):
    db_path = tmp_path / "test.duckdb"
    con = duckdb.connect(str(db_path))
    _seed_ohlcv_tables(con)
    con.close()

    def _get_con():
        return duckdb.connect(str(db_path))

    monkeypatch.setattr("edge_tools.backtest.engine.get_duckdb_connection", _get_con)
    monkeypatch.setattr("edge_tools.backtest.optimizer.get_duckdb_connection", _get_con)

    param_grid = {
        "stop_loss": [2],
        "take_profit": [3],
        "max_bars": [3],
        "breakout_lookback": [2],
        "entry_offset": [0.0],
        "daily_regime": ["trend_up"],
        "hourly_regime": ["trend_down"],
    }

    run_grid_search(param_grid=param_grid, worker_id=0, n_workers=1)

    with duckdb.connect(str(db_path)) as verify:
        count = verify.execute("SELECT COUNT(*) FROM strategy_runs").fetchone()[0]
        assert count == 1

    run_walkforward(top_n=1)

    with duckdb.connect(str(db_path)) as verify:
        count = verify.execute(
            "SELECT COUNT(*) FROM strategy_walkforward_results"
        ).fetchone()[0]
        assert count >= 1

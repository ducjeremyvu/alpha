from __future__ import annotations

from dataclasses import dataclass

import duckdb
import numpy as np
import pandas as pd

from edge_tools.db import get_duckdb_connection


DEFAULT_SYMBOL = "US500"
DEFAULT_TABLE = "daily_close_above_prev_high"
DEFAULT_FORWARD_HORIZONS = (1, 3, 6)


@dataclass(frozen=True)
class SignalSummary:
    total_rows: int
    signal_rows: int
    signal_rate: float


def load_daily_candles(
    symbol: str = DEFAULT_SYMBOL,
    con: duckdb.DuckDBPyConnection | None = None,
) -> pd.DataFrame:
    query = (
        "SELECT time, open, high, low, close, volume "
        "FROM ohlcv_daily WHERE symbol = ? ORDER BY time"
    )

    if con is None:
        with get_duckdb_connection() as con:
            data = con.execute(query, [symbol]).df()
    else:
        data = con.execute(query, [symbol]).df()

    data = data.sort_values("time").reset_index(drop=True)
    data["time"] = pd.to_datetime(data["time"], utc=True)
    return data


def build_signal_dataset(
    daily: pd.DataFrame,
    forward_horizons: tuple[int, ...] = DEFAULT_FORWARD_HORIZONS,
) -> pd.DataFrame:
    data = daily.copy()
    data = data.sort_values("time").reset_index(drop=True)

    candle_type = np.select(
        [data["close"] > data["open"], data["close"] < data["open"]],
        ["bullish", "bearish"],
        default="neutral",
    )
    data["candle_type"] = candle_type
    data["prev_high"] = data["high"].shift(1)
    data["next_candle_type"] = data["candle_type"].shift(-1)
    _add_forward_returns(data, forward_horizons)

    required = ["next_candle_type"] + [f"fwd_return_{h}" for h in forward_horizons]
    filtered = data[
        (data["close"] > data["prev_high"]) & data[required].notna().all(axis=1)
    ].copy()
    return filtered


def summarize_signal_dataset(daily: pd.DataFrame, signal: pd.DataFrame) -> SignalSummary:
    total_rows = int(len(daily))
    signal_rows = int(len(signal))
    signal_rate = float(signal_rows / total_rows) if total_rows else 0.0
    return SignalSummary(
        total_rows=total_rows,
        signal_rows=signal_rows,
        signal_rate=signal_rate,
    )


def save_signal_dataset(
    signal: pd.DataFrame,
    table_name: str = DEFAULT_TABLE,
    con: duckdb.DuckDBPyConnection | None = None,
    overwrite: bool = True,
) -> None:
    query = (
        f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM signal_df"
        if overwrite
        else f"CREATE TABLE IF NOT EXISTS {table_name} AS SELECT * FROM signal_df"
    )

    if con is None:
        with get_duckdb_connection() as con:
            con.register("signal_df", signal)
            con.execute(query)
    else:
        con.register("signal_df", signal)
        con.execute(query)


def _add_forward_returns(data: pd.DataFrame, horizons: tuple[int, ...]) -> None:
    for horizon in horizons:
        future_close = data["close"].shift(-horizon)
        data[f"fwd_return_{horizon}"] = (future_close - data["close"]) / data["close"]

from __future__ import annotations

from dataclasses import dataclass

import duckdb
import pandas as pd

from edge_tools.db import get_duckdb_connection


DEFAULT_SYMBOL = "US500"


@dataclass(frozen=True)
class CandleBundle:
    candles_5m: pd.DataFrame
    candles_1h: pd.DataFrame
    candles_1d: pd.DataFrame


def load_candles(
    symbol: str = DEFAULT_SYMBOL,
    con: duckdb.DuckDBPyConnection | None = None,
) -> CandleBundle:
    query_minute = _ohlcv_query("ohlcv_minute", symbol)
    query_hour = _ohlcv_query("ohlcv_hour", symbol)
    query_daily = _ohlcv_query("ohlcv_daily", symbol)

    if con is None:
        with get_duckdb_connection() as con:
            candles_5m = con.execute(query_minute).df()
            candles_1h = con.execute(query_hour).df()
            candles_1d = con.execute(query_daily).df()
    else:
        candles_5m = con.execute(query_minute).df()
        candles_1h = con.execute(query_hour).df()
        candles_1d = con.execute(query_daily).df()

    return CandleBundle(
        candles_5m=candles_5m,
        candles_1h=candles_1h,
        candles_1d=candles_1d,
    )


def _ohlcv_query(table: str, symbol: str) -> str:
    return (
        "SELECT time, open, high, low, close, volume "
        f"FROM {table} WHERE symbol = '{symbol}' ORDER BY time"
    )


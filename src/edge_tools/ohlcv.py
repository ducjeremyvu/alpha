from __future__ import annotations
import pandas as pd
from datetime import datetime, date

from .dir import get_sql_query
from .date import to_datetime
import logging

import duckdb

logger = logging.getLogger(__name__)

__all__ = ["normalize_ohlcv", "require_columns"]

ALIASES = {
    "open":   ["open", "Open", "o"],
    "high":   ["high", "High", "h"],
    "low":    ["low", "Low", "l"],
    "close":  ["close", "Close", "c"],
    "volume": ["volume", "Volume", "vol", "Vol", "v"],
    "time":   ["time", "Time", "date", "Date", "datetime", "Datetime", "timestamp"],
}

def ohlcv_for_date_and_prev(symbol: str, selected_date: str | int | float | datetime | date) -> pd.DataFrame:
    
    selected_date = to_datetime(selected_date).date()
    start_date = (selected_date - pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    end_date = (selected_date + pd.Timedelta(days=1)).strftime("%Y-%m-%d")

    params = {
        "symbol": symbol,
        "start_date": start_date,
        "end_date": end_date
    }
    logger.debug(f"SQL Query Parameters: {params}")
    
    filename = "ohlcv_data__by_ticker_and_date.sql"

    query = get_sql_query(filename, **params)

    with duckdb.connect("./local.duckdb") as con:
        data = con.execute(query).df()
    return data




def normalize_ohlcv(df: pd.DataFrame, style: str = "capitalized") -> pd.DataFrame:
    if style not in {"capitalized", "lowercase"}:
        raise ValueError("style must be 'capitalized' or 'lowercase'")

    target = lambda k: k.capitalize() if style == "capitalized" else k.lower()
    mapping = {k: target(k) for k in ALIASES.keys()}

    rename_map = {}
    for key, candidates in ALIASES.items():
        for cand in candidates:
            if cand in df.columns:
                rename_map[cand] = mapping[key]
                break

    out = df.rename(columns=rename_map)
    required = list(mapping.values())
    missing = [c for c in required if c not in out.columns]
    if missing:
        raise ValueError(f"Missing required columns after normalization: {missing}")
    return out

def require_columns(df: pd.DataFrame, cols: list[str]) -> None:
    lower_cols = {c.lower() for c in df.columns}
    missing = [c for c in cols if c.lower() not in lower_cols]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")



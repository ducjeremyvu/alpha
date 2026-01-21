from __future__ import annotations

import os

import numpy as np
import pandas as pd

from edge_tools.db import get_duckdb_connection
from edge_tools.research.daily_signals import load_daily_candles


def _label_candles(data: pd.DataFrame) -> pd.DataFrame:
    labeled = data.copy()
    labeled = labeled.sort_values("time").reset_index(drop=True)
    labeled["candle_type"] = np.select(
        [labeled["close"] > labeled["open"], labeled["close"] < labeled["open"]],
        ["green", "red"],
        default="neutral",
    )
    labeled["next_candle_type"] = labeled["candle_type"].shift(-1)
    return labeled


def _summarize_next_candle(data: pd.DataFrame) -> pd.DataFrame:
    summary = (
        data.dropna(subset=["next_candle_type"])
        .groupby(["candle_type", "next_candle_type"], as_index=False)
        .size()
        .rename(columns={"size": "count"})
    )
    summary["rate"] = summary["count"] / summary.groupby("candle_type")["count"].transform(
        "sum"
    )
    return summary


def main() -> None:
    symbol = os.getenv("SYMBOL", "US500")
    with get_duckdb_connection() as con:
        daily = load_daily_candles(symbol=symbol, con=con)

    labeled = _label_candles(daily)
    summary = _summarize_next_candle(labeled)

    print("Next candle behavior summary", {"symbol": symbol, "rows": len(labeled)})
    print(summary.to_string(index=False))

    pivot = summary.pivot(
        index="candle_type", columns="next_candle_type", values="rate"
    ).fillna(0.0)
    print("\nNext candle rates by prior candle")
    print(pivot.round(4).to_string())


if __name__ == "__main__":
    main()

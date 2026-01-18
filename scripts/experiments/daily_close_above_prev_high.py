from __future__ import annotations

import os

from edge_tools.db import get_duckdb_connection
from edge_tools.research.daily_signals import (
    DEFAULT_TABLE,
    build_signal_dataset,
    load_daily_candles,
    save_signal_dataset,
    summarize_signal_dataset,
)


def main() -> None:
    symbol = os.getenv("SYMBOL", "US500")
    table_name = os.getenv("OUTPUT_TABLE", DEFAULT_TABLE)

    with get_duckdb_connection() as con:
        daily = load_daily_candles(symbol=symbol, con=con)
        signal = build_signal_dataset(daily)
        save_signal_dataset(signal, table_name=table_name, con=con, overwrite=True)

    summary = summarize_signal_dataset(daily, signal)
    print(
        "Saved daily candle signal dataset",
        {
            "symbol": symbol,
            "table": table_name,
            "total_rows": summary.total_rows,
            "signal_rows": summary.signal_rows,
            "signal_rate": summary.signal_rate,
        },
    )


if __name__ == "__main__":
    main()

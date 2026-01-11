from __future__ import annotations

import os

from edge_tools.backtest.optimizer import run_grid_search


def main() -> None:
    worker_id = int(os.getenv("WORKER_ID", "0"))
    n_workers = int(os.getenv("N_WORKERS", "1"))
    symbol = os.getenv("SYMBOL", "US500")

    param_grid = {
        "stop_loss": [5, 10, 15],
        "take_profit": [5, 10, 20],
        "max_bars": [3, 6, 9],
        "breakout_lookback": [8, 12, 20],
        "entry_offset": [0.0, 0.5, 1.0],
        "daily_regime": ["any"],
        "hourly_regime": ["any"],
    }

    run_grid_search(
        param_grid=param_grid,
        worker_id=worker_id,
        n_workers=n_workers,
        symbol=symbol,
    )


if __name__ == "__main__":
    main()

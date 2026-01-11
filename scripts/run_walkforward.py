from __future__ import annotations

import os

from edge_tools.backtest.optimizer import run_walkforward


def main() -> None:
    symbol = os.getenv("SYMBOL", "US500")
    top_n = int(os.getenv("TOP_N", "50"))
    run_walkforward(top_n=top_n, symbol=symbol)


if __name__ == "__main__":
    main()

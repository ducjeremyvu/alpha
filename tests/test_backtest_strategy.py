import pandas as pd

from edge_tools.backtest.schemas import StrategyParams
from edge_tools.backtest.strategies import run_strategy


def test_run_strategy_failed_breakout_short():
    times = pd.date_range("2024-01-02 14:00", periods=6, freq="5min", tz="UTC")
    candles_5m = pd.DataFrame(
        {
            "time": times,
            "open": [98, 99, 100, 101, 100, 99],
            "high": [100, 101, 103, 102, 101, 100],
            "low": [95, 96, 99, 98, 96, 95],
            "close": [98, 100, 102, 100, 98, 97],
            "volume": [1] * 6,
        }
    )

    candles_1h = pd.DataFrame(
        {
            "time": ["2024-01-02 14:00Z"],
            "open": [100],
            "high": [102],
            "low": [95],
            "close": [99],
            "volume": [1],
        }
    )
    candles_1d = pd.DataFrame(
        {
            "time": ["2024-01-02 00:00Z"],
            "open": [95],
            "high": [110],
            "low": [94],
            "close": [105],
            "volume": [1],
        }
    )

    params = StrategyParams(
        stop_loss=2,
        take_profit=3,
        max_bars=3,
        breakout_lookback=2,
        entry_offset=0.0,
        daily_regime="trend_up",
        hourly_regime="trend_down",
    )

    trades = run_strategy(candles_5m, candles_1h, candles_1d, params)

    assert len(trades) == 1
    trade = trades[0]
    assert trade.direction == "short"
    assert trade.entry_price == 100.0
    assert trade.exit_price == 97.0

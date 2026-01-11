import pytest

from edge_tools.backtest.metrics import compute_metrics
from edge_tools.backtest.schemas import Trade


def test_compute_metrics_empty():
    metrics = compute_metrics([])

    assert metrics["trades"] == 0
    assert metrics["winrate"] == 0.0
    assert metrics["expectancy"] == 0.0


def test_compute_metrics_basic():
    trades = [
        Trade(
            entry_time="2024-01-02T14:00:00Z",
            entry_price=100.0,
            exit_time="2024-01-02T14:25:00Z",
            exit_price=110.0,
            mae=3.0,
            mfe=12.0,
            direction="long",
        ),
        Trade(
            entry_time="2024-01-03T14:00:00Z",
            entry_price=105.0,
            exit_time="2024-01-03T14:25:00Z",
            exit_price=110.0,
            mae=4.0,
            mfe=6.0,
            direction="short",
        ),
    ]

    metrics = compute_metrics(trades)

    assert metrics["trades"] == 2
    assert metrics["winrate"] == 0.5
    assert metrics["expectancy"] == pytest.approx(2.5)
    assert metrics["avg_MAE"] == pytest.approx(3.5)
    assert metrics["avg_MFE"] == pytest.approx(9.0)
    assert metrics["max_drawdown"] == pytest.approx(5.0)
    assert metrics["profit_factor"] == pytest.approx(2.0)
    assert metrics["sharpe"] == pytest.approx(0.333333, rel=1e-2)

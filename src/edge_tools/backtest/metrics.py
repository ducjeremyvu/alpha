from __future__ import annotations

import math

import numpy as np

from .schemas import Trade


def compute_metrics(trades: list[Trade]) -> dict:
    if not trades:
        return {
            "trades": 0,
            "winrate": 0.0,
            "expectancy": 0.0,
            "avg_MAE": 0.0,
            "avg_MFE": 0.0,
            "max_drawdown": 0.0,
            "profit_factor": 0.0,
            "sharpe": 0.0,
        }

    pnls = np.array([_trade_pnl(trade) for trade in trades], dtype=float)
    wins = pnls > 0
    losses = pnls < 0
    gross_profit = pnls[wins].sum()
    gross_loss = pnls[losses].sum()

    expectancy = pnls.mean()
    winrate = wins.mean() if pnls.size else 0.0
    avg_mae = float(np.mean([trade.mae for trade in trades]))
    avg_mfe = float(np.mean([trade.mfe for trade in trades]))

    profit_factor = _profit_factor(gross_profit, gross_loss)
    max_drawdown = _max_drawdown(pnls)
    sharpe = _sharpe(pnls)

    return {
        "trades": int(len(trades)),
        "winrate": float(winrate),
        "expectancy": float(expectancy),
        "avg_MAE": avg_mae,
        "avg_MFE": avg_mfe,
        "max_drawdown": float(max_drawdown),
        "profit_factor": float(profit_factor),
        "sharpe": float(sharpe),
    }


def _trade_pnl(trade: Trade) -> float:
    if trade.direction == "long":
        return trade.exit_price - trade.entry_price
    return trade.entry_price - trade.exit_price


def _profit_factor(gross_profit: float, gross_loss: float) -> float:
    if gross_loss == 0:
        return math.inf if gross_profit > 0 else 0.0
    return gross_profit / abs(gross_loss)


def _max_drawdown(pnls: np.ndarray) -> float:
    equity = np.cumsum(pnls)
    peaks = np.maximum.accumulate(equity)
    drawdowns = equity - peaks
    return abs(drawdowns.min(initial=0.0))


def _sharpe(pnls: np.ndarray) -> float:
    if pnls.size < 2:
        return 0.0
    std = pnls.std(ddof=1)
    if std == 0:
        return 0.0
    return float(pnls.mean() / std * math.sqrt(pnls.size))


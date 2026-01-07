from __future__ import annotations

import numpy as np
import pandas as pd


def backtest_patterns(
    data: pd.DataFrame,
    signals: pd.DataFrame,
    slippage: float = 0.2,
    spread: float = 0.2,
    stop_multiplier: float = 1.0,
) -> pd.DataFrame:
    if signals.empty:
        return pd.DataFrame()

    data = data.sort_values(["session_date", "time_ny"]).reset_index(drop=True)
    data["bar_id"] = data.groupby("session_date").cumcount()
    signals = signals.merge(
        data[["session_date", "time_ny", "bar_id", "open", "high", "low", "close", "rolling_range_mean"]],
        on=["session_date", "time_ny"],
        how="left",
        suffixes=("", "_bar"),
    )

    trades = []
    taken = set()
    for _, signal in signals.iterrows():
        day_key = (signal["session_date"], signal["direction"])
        if day_key in taken:
            continue
        session = data[data["session_date"] == signal["session_date"]]
        entry_bar = session[session["bar_id"] > signal["bar_id"]].head(1)
        if entry_bar.empty:
            continue
        entry_row = entry_bar.iloc[0]
        stop_distance = max(stop_multiplier * entry_row["rolling_range_mean"], 0.0)
        if np.isnan(stop_distance) or stop_distance == 0:
            continue
        direction = int(signal["direction"])
        entry_price = entry_row["open"] + direction * (spread + slippage)
        stop_price = entry_price - direction * stop_distance
        target_price = entry_price + direction * stop_distance * 2

        exit_price, exit_reason, exit_time = _simulate_exit(
            session,
            entry_row["bar_id"],
            direction,
            stop_price,
            target_price,
        )

        pnl = (exit_price - entry_price) * direction
        trades.append({
            "session_date": signal["session_date"],
            "pattern": signal["pattern"],
            "direction": direction,
            "entry_time": entry_row["time_ny"],
            "exit_time": exit_time,
            "entry_price": entry_price,
            "exit_price": exit_price,
            "pnl": pnl,
            "r_multiple": pnl / stop_distance,
            "exit_reason": exit_reason,
            "context_label": signal.get("context_label"),
        })
        taken.add(day_key)

    trades_df = pd.DataFrame(trades)
    if trades_df.empty:
        return trades_df
    trades_df["split"] = _split_by_date(trades_df["session_date"])
    return trades_df


def summarize_backtest(trades: pd.DataFrame) -> dict:
    if trades.empty:
        return {"trades": 0}
    summary = {
        "trades": int(len(trades)),
        "win_rate": float((trades["pnl"] > 0).mean()),
        "expectancy": float(trades["pnl"].mean()),
        "profit_factor": float(_profit_factor(trades["pnl"])),
        "max_drawdown": float(_max_drawdown(trades["pnl"])),
    }
    summary["by_split"] = {
        split: _split_summary(split_df)
        for split, split_df in trades.groupby("split")
    }
    summary["by_context"] = {
        ctx: _split_summary(ctx_df)
        for ctx, ctx_df in trades.groupby("context_label")
    }
    return summary


def _simulate_exit(
    session: pd.DataFrame,
    entry_bar_id: int,
    direction: int,
    stop_price: float,
    target_price: float,
) -> tuple[float, str, pd.Timestamp]:
    forward = session[session["bar_id"] >= entry_bar_id].head(7)
    for _, bar in forward.iterrows():
        if direction == 1:
            if bar["low"] <= stop_price:
                return stop_price, "stop", bar["time_ny"]
            if bar["high"] >= target_price:
                return target_price, "target", bar["time_ny"]
        else:
            if bar["high"] >= stop_price:
                return stop_price, "stop", bar["time_ny"]
            if bar["low"] <= target_price:
                return target_price, "target", bar["time_ny"]
    last_bar = forward.iloc[-1]
    return last_bar["close"], "time_stop", last_bar["time_ny"]


def _split_by_date(dates: pd.Series) -> pd.Series:
    unique = sorted(dates.unique())
    if not unique:
        return pd.Series([], dtype=str)
    n = len(unique)
    train_end = int(n * 0.6)
    val_end = int(n * 0.8)
    mapping = {}
    for idx, day in enumerate(unique):
        if idx < train_end:
            mapping[day] = "train"
        elif idx < val_end:
            mapping[day] = "validate"
        else:
            mapping[day] = "test"
    return dates.map(mapping)


def _split_summary(trades: pd.DataFrame) -> dict:
    if trades.empty:
        return {"trades": 0}
    return {
        "trades": int(len(trades)),
        "win_rate": float((trades["pnl"] > 0).mean()),
        "expectancy": float(trades["pnl"].mean()),
        "profit_factor": float(_profit_factor(trades["pnl"])),
    }


def _profit_factor(pnl: pd.Series) -> float:
    gains = pnl[pnl > 0].sum()
    losses = -pnl[pnl < 0].sum()
    if losses == 0:
        return float("inf")
    return float(gains / losses)


def _max_drawdown(pnl: pd.Series) -> float:
    cumulative = pnl.cumsum()
    peak = cumulative.cummax()
    drawdown = cumulative - peak
    return float(drawdown.min())

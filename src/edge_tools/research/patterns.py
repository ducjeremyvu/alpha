from __future__ import annotations

import json
from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class PatternDefinition:
    name: str
    description: str
    direction: str
    rules: str


PATTERN_DEFINITIONS = {
    "opening_drive": PatternDefinition(
        name="Opening Drive",
        description="First 30 minutes show strong directional move with limited pullbacks.",
        direction="with_trend",
        rules="First 6 bars efficiency > 0.65 and net move > 0.8 * early range.",
    ),
    "spike_fade": PatternDefinition(
        name="Spike + Fade",
        description="Early impulse quickly fades back toward the session open.",
        direction="counter",
        rules="Impulse > 2.0 then close returns within 25% of early range.",
    ),
    "compression_expansion": PatternDefinition(
        name="Compression to Expansion",
        description="Tight range compression followed by breakout expansion.",
        direction="with_breakout",
        rules="Compression < 0.7 for 4 bars then range > 1.5 * rolling mean.",
    ),
    "two_leg_trend": PatternDefinition(
        name="Two-Leg Trend",
        description="Push, shallow pullback, and continuation in same direction.",
        direction="with_trend",
        rules="Leg1 return > 1.0 * rolling vol, pullback < 40% of leg1.",
    ),
    "failed_breakout": PatternDefinition(
        name="Failed Breakout",
        description="Breaks early range then closes back inside within 2 bars.",
        direction="fade_breakout",
        rules="Break above/below first-hour range then close back inside.",
    ),
    "mean_reversion_open": PatternDefinition(
        name="Mean Reversion to Open",
        description="Price stretches far from open then reverts toward it.",
        direction="reversion",
        rules="Distance from open > 1.5 * rolling range mean then closes halfway back.",
    ),
    "sweep_proxy": PatternDefinition(
        name="Sweep Proxy",
        description="Local extreme followed by sharp opposite impulse.",
        direction="counter",
        rules="10-bar extreme then opposite impulse > 1.5 * rolling vol.",
    ),
}


def build_pattern_candidates(
    data: pd.DataFrame,
    context: pd.DataFrame,
) -> tuple[pd.DataFrame, dict]:
    data = data.copy()
    data = data.merge(context[["session_date", "context_label"]], on="session_date", how="left")
    data = data.sort_values(["session_date", "time_ny"]).reset_index(drop=True)

    signals = pd.concat(
        [
            _opening_drive(data),
            _spike_fade(data),
            _compression_expansion(data),
            _two_leg_trend(data),
            _failed_breakout(data),
            _mean_reversion_open(data),
            _sweep_proxy(data),
        ],
        ignore_index=True,
    )

    signals = signals.sort_values(["session_date", "time_ny"]).reset_index(drop=True)
    signals = _attach_forward_metrics(data, signals)
    summary = _summarize_patterns(signals)
    return signals, summary


def write_pattern_candidates(summary: dict, path: str) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)


def _opening_drive(data: pd.DataFrame) -> pd.DataFrame:
    signals = []
    for session_date, group in data.groupby("session_date", sort=True):
        group = group.reset_index(drop=True)
        early = group.iloc[:6]
        if len(early) < 6:
            continue
        early_range = early["high"].max() - early["low"].min()
        net_move = early["close"].iloc[-1] - early["open"].iloc[0]
        total_move = early["close_open"].abs().sum()
        efficiency = abs(net_move) / total_move if total_move else 0
        if efficiency > 0.65 and abs(net_move) > 0.8 * early_range:
            direction = 1 if net_move > 0 else -1
            signals.append(_signal_row(early.iloc[-1], session_date, "opening_drive", direction))
    return pd.DataFrame(signals)


def _spike_fade(data: pd.DataFrame) -> pd.DataFrame:
    signals = []
    for session_date, group in data.groupby("session_date", sort=True):
        group = group.reset_index(drop=True)
        early = group.iloc[:12]
        if early.empty:
            continue
        impulse_bar = early[early["impulse"] > 2.0]
        if impulse_bar.empty:
            continue
        first = impulse_bar.iloc[0]
        start_open = early["open"].iloc[0]
        early_range = early["high"].max() - early["low"].min()
        if early_range == 0:
            continue
        follow = group.iloc[first.name + 1: first.name + 4]
        if follow.empty:
            continue
        close_back = follow["close"].iloc[-1]
        if abs(close_back - start_open) < 0.25 * early_range:
            direction = -1 if first["close_open"] > 0 else 1
            signals.append(_signal_row(follow.iloc[-1], session_date, "spike_fade", direction))
    return pd.DataFrame(signals)


def _compression_expansion(data: pd.DataFrame) -> pd.DataFrame:
    signals = []
    for idx, row in data.iterrows():
        if row["compression"] < 0.7 and row["bar_index_in_session"] >= 4:
            recent = data.iloc[max(idx - 3, 0): idx + 1]
            if recent["compression"].max() < 0.7 and row["range"] > 1.5 * row["rolling_range_mean"]:
                direction = 1 if row["close_open"] > 0 else -1
                signals.append(_signal_row(row, row["session_date"], "compression_expansion", direction))
    return pd.DataFrame(signals)


def _two_leg_trend(data: pd.DataFrame) -> pd.DataFrame:
    signals = []
    for session_date, group in data.groupby("session_date", sort=True):
        group = group.reset_index(drop=True)
        for idx in range(4, len(group)):
            leg1 = group.iloc[idx - 4: idx - 2]
            pullback = group.iloc[idx - 2: idx]
            continuation = group.iloc[idx]
            leg1_return = leg1["close"].iloc[-1] - leg1["open"].iloc[0]
            if abs(leg1_return) < leg1["rolling_vol"].mean() * leg1["open"].iloc[0]:
                continue
            pullback_range = pullback["close_open"].abs().sum()
            if pullback_range > abs(leg1_return) * 0.4:
                continue
            direction = 1 if leg1_return > 0 else -1
            if direction == 1 and continuation["close"] > leg1["close"].iloc[-1]:
                signals.append(_signal_row(continuation, session_date, "two_leg_trend", direction))
            if direction == -1 and continuation["close"] < leg1["close"].iloc[-1]:
                signals.append(_signal_row(continuation, session_date, "two_leg_trend", direction))
    return pd.DataFrame(signals)


def _failed_breakout(data: pd.DataFrame) -> pd.DataFrame:
    signals = []
    for session_date, group in data.groupby("session_date", sort=True):
        group = group.reset_index(drop=True)
        if len(group) < 12:
            continue
        first_hour = group.iloc[:12]
        range_high = first_hour["high"].max()
        range_low = first_hour["low"].min()
        for idx in range(12, len(group) - 2):
            bar = group.iloc[idx]
            if bar["high"] > range_high and group.iloc[idx + 1]["close"] < range_high:
                signals.append(_signal_row(group.iloc[idx + 1], session_date, "failed_breakout", -1))
            if bar["low"] < range_low and group.iloc[idx + 1]["close"] > range_low:
                signals.append(_signal_row(group.iloc[idx + 1], session_date, "failed_breakout", 1))
    return pd.DataFrame(signals)


def _mean_reversion_open(data: pd.DataFrame) -> pd.DataFrame:
    signals = []
    for session_date, group in data.groupby("session_date", sort=True):
        group = group.reset_index(drop=True)
        session_open = group["open"].iloc[0]
        for idx in range(2, len(group) - 2):
            bar = group.iloc[idx]
            distance = bar["close"] - session_open
            if abs(distance) > 1.5 * bar["rolling_range_mean"]:
                follow = group.iloc[idx + 1: idx + 3]
                if follow.empty:
                    continue
                if abs(follow["close"].iloc[-1] - session_open) < abs(distance) * 0.5:
                    direction = -1 if distance > 0 else 1
                    signals.append(_signal_row(follow.iloc[-1], session_date, "mean_reversion_open", direction))
    return pd.DataFrame(signals)


def _sweep_proxy(data: pd.DataFrame) -> pd.DataFrame:
    signals = []
    for session_date, group in data.groupby("session_date", sort=True):
        group = group.reset_index(drop=True)
        for idx in range(10, len(group) - 1):
            window = group.iloc[idx - 10: idx]
            bar = group.iloc[idx]
            next_bar = group.iloc[idx + 1]
            if bar["high"] >= window["high"].max() and next_bar["impulse"] > 1.5 and next_bar["close_open"] < 0:
                signals.append(_signal_row(next_bar, session_date, "sweep_proxy", -1))
            if bar["low"] <= window["low"].min() and next_bar["impulse"] > 1.5 and next_bar["close_open"] > 0:
                signals.append(_signal_row(next_bar, session_date, "sweep_proxy", 1))
    return pd.DataFrame(signals)


def _signal_row(row: pd.Series, session_date, pattern: str, direction: int) -> dict:
    return {
        "session_date": session_date,
        "time_ny": row["time_ny"],
        "pattern": pattern,
        "direction": direction,
        "entry_price": row["close"],
        "context_label": row.get("context_label"),
    }


def _attach_forward_metrics(data: pd.DataFrame, signals: pd.DataFrame) -> pd.DataFrame:
    if signals.empty:
        return signals
    data = data.sort_values(["session_date", "time_ny"]).reset_index(drop=True)
    data["bar_id"] = data.groupby("session_date").cumcount()
    signals = signals.merge(
        data[["session_date", "time_ny", "bar_id", "close", "high", "low"]],
        on=["session_date", "time_ny"],
        how="left",
    )
    signals.rename(columns={"close": "signal_close"}, inplace=True)
    forward = []
    for _, signal in signals.iterrows():
        session = data[data["session_date"] == signal["session_date"]]
        bar_id = signal["bar_id"]
        future = session[session["bar_id"] > bar_id].head(6)
        forward_returns = {
            "fwd_1": _forward_return(future, 1, signal["signal_close"], signal["direction"]),
            "fwd_3": _forward_return(future, 3, signal["signal_close"], signal["direction"]),
            "fwd_6": _forward_return(future, 6, signal["signal_close"], signal["direction"]),
        }
        mae, mfe = _mae_mfe(future, signal["signal_close"], signal["direction"])
        forward.append({
            "mae": mae,
            "mfe": mfe,
            **forward_returns,
        })
    forward_df = pd.DataFrame(forward)
    return pd.concat([signals.reset_index(drop=True), forward_df], axis=1)


def _forward_return(future: pd.DataFrame, bars: int, entry: float, direction: int) -> float:
    if future.empty:
        return float("nan")
    selected = future.iloc[min(bars - 1, len(future) - 1)]
    raw = selected["close"] - entry
    return raw * direction


def _mae_mfe(future: pd.DataFrame, entry: float, direction: int) -> tuple[float, float]:
    if future.empty:
        return float("nan"), float("nan")
    if direction == 1:
        mfe = future["high"].max() - entry
        mae = entry - future["low"].min()
    else:
        mfe = entry - future["low"].min()
        mae = future["high"].max() - entry
    return float(mae), float(mfe)


def _summarize_patterns(signals: pd.DataFrame) -> dict:
    summary = {
        "total_signals": int(len(signals)),
        "patterns": {},
    }
    if signals.empty:
        return summary
    for pattern, group in signals.groupby("pattern"):
        summary["patterns"][pattern] = {
            "count": int(len(group)),
            "avg_fwd_1": float(group["fwd_1"].mean()),
            "avg_fwd_3": float(group["fwd_3"].mean()),
            "avg_fwd_6": float(group["fwd_6"].mean()),
            "avg_mae": float(group["mae"].mean()),
            "avg_mfe": float(group["mfe"].mean()),
            "contexts": group["context_label"].value_counts().to_dict(),
        }
    return summary

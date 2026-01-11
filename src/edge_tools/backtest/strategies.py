from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from edge_tools.time_series.ohlcv import require_columns

from .schemas import StrategyParams, Trade


@dataclass(frozen=True)
class _PendingBreakout:
    direction: str
    level: float
    start_index: int


def run_strategy(
    candles_5m: pd.DataFrame,
    candles_1h: pd.DataFrame,
    candles_1d: pd.DataFrame,
    params: StrategyParams,
) -> list[Trade]:
    candles_5m = _prepare_candles(candles_5m, label="5m")
    candles_1h = _prepare_candles(candles_1h, label="1h")
    candles_1d = _prepare_candles(candles_1d, label="1d")

    candles_1d = _ensure_regime_column(candles_1d, "daily_regime")
    candles_1h = _ensure_regime_column(candles_1h, "hourly_regime")

    candles_5m["session_date"] = candles_5m["time"].dt.date
    candles_5m["hour_bucket"] = candles_5m["time"].dt.floor("1h")
    candles_1d["session_date"] = candles_1d["time"].dt.date
    candles_1h["hour_bucket"] = candles_1h["time"].dt.floor("1h")

    daily_map = candles_1d.set_index("session_date")["daily_regime"]
    hourly_map = candles_1h.set_index("hour_bucket")["hourly_regime"]
    candles_5m["daily_regime"] = candles_5m["session_date"].map(daily_map)
    candles_5m["hourly_regime"] = candles_5m["hour_bucket"].map(hourly_map)

    eligible = _eligible_mask(candles_5m, params)

    highs = candles_5m["high"].to_numpy()
    lows = candles_5m["low"].to_numpy()
    closes = candles_5m["close"].to_numpy()
    times = candles_5m["time"].to_numpy()

    lookback = params.breakout_lookback
    rolling_high = (
        candles_5m["high"].shift(1).rolling(lookback, min_periods=lookback).max()
    ).to_numpy()
    rolling_low = (
        candles_5m["low"].shift(1).rolling(lookback, min_periods=lookback).min()
    ).to_numpy()

    trades: list[Trade] = []
    pending: _PendingBreakout | None = None
    active_trade: dict | None = None

    i = 0
    n = len(candles_5m)

    while i < n:
        if active_trade is not None:
            _update_trade(active_trade, highs[i], lows[i])
            exit_price = _check_exit(active_trade, highs[i], lows[i])
            timeout_hit = i - active_trade["entry_index"] >= params.max_bars
            if exit_price is not None or timeout_hit:
                if exit_price is None:
                    exit_price = closes[i]
                trades.append(
                    Trade(
                        entry_time=active_trade["entry_time"],
                        entry_price=active_trade["entry_price"],
                        exit_time=pd.Timestamp(times[i]).to_pydatetime(),
                        exit_price=float(exit_price),
                        mae=active_trade["mae"],
                        mfe=active_trade["mfe"],
                        direction=active_trade["direction"],
                    )
                )
                active_trade = None
            i += 1
            continue

        if pending is not None:
            if i - pending.start_index > params.max_bars:
                pending = None
                continue

            if not eligible[i]:
                i += 1
                continue

            if pending.direction == "short" and closes[i] <= pending.level:
                active_trade = _start_trade(
                    direction="short",
                    entry_index=i,
                    entry_price=closes[i],
                    entry_time=times[i],
                    stop_loss=params.stop_loss,
                    take_profit=params.take_profit,
                )
                pending = None
                i += 1
                continue

            if pending.direction == "long" and closes[i] >= pending.level:
                active_trade = _start_trade(
                    direction="long",
                    entry_index=i,
                    entry_price=closes[i],
                    entry_time=times[i],
                    stop_loss=params.stop_loss,
                    take_profit=params.take_profit,
                )
                pending = None
                i += 1
                continue

            i += 1
            continue

        if not eligible[i]:
            i += 1
            continue

        if np.isnan(rolling_high[i]) or np.isnan(rolling_low[i]):
            i += 1
            continue

        breakout_high = rolling_high[i] + params.entry_offset
        breakout_low = rolling_low[i] - params.entry_offset

        if highs[i] >= breakout_high:
            pending = _PendingBreakout(
                direction="short",
                level=rolling_high[i],
                start_index=i,
            )
            i += 1
            continue

        if lows[i] <= breakout_low:
            pending = _PendingBreakout(
                direction="long",
                level=rolling_low[i],
                start_index=i,
            )
            i += 1
            continue

        i += 1

    return trades


def _prepare_candles(candles: pd.DataFrame, label: str) -> pd.DataFrame:
    candles = candles.copy()
    candles = _standardize_columns(candles)
    require_columns(candles, ["open", "high", "low", "close", "time"])
    candles["time"] = pd.to_datetime(candles["time"], utc=True)
    candles = candles.sort_values("time")
    candles = candles.reset_index(drop=True)
    if candles.empty:
        raise ValueError(f"{label} candles are empty")
    return candles


def _standardize_columns(candles: pd.DataFrame) -> pd.DataFrame:
    columns = {col.lower(): col for col in candles.columns}
    mapping = {}
    for name in ("open", "high", "low", "close", "volume", "time"):
        if name in columns and columns[name] != name:
            mapping[columns[name]] = name
    if mapping:
        candles = candles.rename(columns=mapping)
    return candles


def _ensure_regime_column(frame: pd.DataFrame, column: str) -> pd.DataFrame:
    frame = frame.copy()
    if column in frame.columns:
        return frame
    for alt in ("regime", "Regime", "daily_trend", "hourly_trend"):
        if alt in frame.columns:
            frame[column] = frame[alt]
            return frame

    direction = np.where(
        frame["close"] > frame["open"],
        "trend_up",
        np.where(frame["close"] < frame["open"], "trend_down", "balance"),
    )
    frame[column] = direction
    return frame


def _eligible_mask(candles: pd.DataFrame, params: StrategyParams) -> np.ndarray:
    daily_ok = _matches_regime(candles["daily_regime"], params.daily_regime)
    hourly_ok = _matches_regime(candles["hourly_regime"], params.hourly_regime)
    return (daily_ok & hourly_ok).to_numpy()


def _matches_regime(series: pd.Series, regime: str) -> pd.Series:
    if regime.lower() in {"any", "all", "none", ""}:
        return pd.Series(True, index=series.index)
    return series.fillna("") == regime


def _start_trade(
    direction: str,
    entry_index: int,
    entry_price: float,
    entry_time: np.datetime64,
    stop_loss: int,
    take_profit: int,
) -> dict:
    if direction not in {"long", "short"}:
        raise ValueError("direction must be 'long' or 'short'")
    return {
        "direction": direction,
        "entry_index": entry_index,
        "entry_time": pd.Timestamp(entry_time).to_pydatetime(),
        "entry_price": float(entry_price),
        "stop_loss": float(stop_loss),
        "take_profit": float(take_profit),
        "mae": 0.0,
        "mfe": 0.0,
        "min_low": float(entry_price),
        "max_high": float(entry_price),
    }


def _update_trade(active_trade: dict, high: float, low: float) -> None:
    active_trade["max_high"] = max(active_trade["max_high"], float(high))
    active_trade["min_low"] = min(active_trade["min_low"], float(low))

    entry = active_trade["entry_price"]
    if active_trade["direction"] == "long":
        active_trade["mae"] = max(active_trade["mae"], entry - active_trade["min_low"])
        active_trade["mfe"] = max(active_trade["mfe"], active_trade["max_high"] - entry)
    else:
        active_trade["mae"] = max(active_trade["mae"], active_trade["max_high"] - entry)
        active_trade["mfe"] = max(active_trade["mfe"], entry - active_trade["min_low"])


def _check_exit(active_trade: dict, high: float, low: float) -> float | None:
    entry = active_trade["entry_price"]
    stop = active_trade["stop_loss"]
    target = active_trade["take_profit"]

    if active_trade["direction"] == "long":
        if low <= entry - stop:
            return entry - stop
        if high >= entry + target:
            return entry + target
    else:
        if high >= entry + stop:
            return entry + stop
        if low <= entry - target:
            return entry - target
    return None

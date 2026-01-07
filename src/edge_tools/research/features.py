from __future__ import annotations

import numpy as np
import pandas as pd


def build_feature_set(sliced: pd.DataFrame) -> pd.DataFrame:
    data = sliced.copy()
    data["return_pct"] = (
        data.groupby("session_date")["close"].pct_change()
    )
    data["return_log"] = (
        data.groupby("session_date")["close"].transform(lambda x: np.log(x).diff())
    )
    data["range"] = data["high"] - data["low"]
    data["body"] = (data["close"] - data["open"]).abs()
    data["close_open"] = data["close"] - data["open"]
    data["upper_wick"] = data["high"] - data[["open", "close"]].max(axis=1)
    data["lower_wick"] = data[["open", "close"]].min(axis=1) - data["low"]
    data["position_in_range"] = (data["close"] - data["low"]) / data["range"].replace(0, np.nan)

    data = _apply_session_rolling(data)
    daily_features = _build_daily_features(data)
    return data.merge(daily_features, on="session_date", how="left")


def _apply_session_rolling(data: pd.DataFrame) -> pd.DataFrame:
    data = data.sort_values(["session_date", "time_ny"])
    grouped = data.groupby("session_date", group_keys=False)
    data["rolling_vol"] = grouped["return_pct"].transform(lambda x: x.rolling(12, min_periods=5).std())
    data["rolling_range_mean"] = grouped["range"].transform(lambda x: x.rolling(12, min_periods=5).mean())
    data["impulse"] = data["return_pct"].abs() / data["rolling_vol"]
    data["compression"] = data["range"] / data["rolling_range_mean"]
    data["direction"] = np.where(data["close"] >= data["open"], 1, -1)
    data["direction_streak"] = grouped["direction"].transform(_streaks)
    return data


def _build_daily_features(data: pd.DataFrame) -> pd.DataFrame:
    grouped = data.groupby("session_date", sort=True)
    summary = grouped.agg(
        open_0930=("open", "first"),
        close_1200=("close", "last"),
        high_0930_1200=("high", "max"),
        low_0930_1200=("low", "min"),
        volume_sum=("volume", "sum"),
        total_movement=("close_open", lambda x: x.abs().sum()),
        realized_vol=("return_pct", "std"),
    )
    summary["range_0930_1200"] = summary["high_0930_1200"] - summary["low_0930_1200"]
    summary["net_move"] = summary["close_1200"] - summary["open_0930"]
    summary["efficiency_ratio"] = summary["net_move"].abs() / summary["total_movement"].replace(0, np.nan)
    summary["mfe_from_open"] = summary["high_0930_1200"] - summary["open_0930"]
    summary["mae_from_open"] = summary["open_0930"] - summary["low_0930_1200"]
    summary.reset_index(inplace=True)
    return summary


def _streaks(values: pd.Series) -> pd.Series:
    streak = 0
    output = []
    prev = None
    for value in values:
        if prev is None or value != prev:
            streak = 1
        else:
            streak += 1
        output.append(streak)
        prev = value
    return pd.Series(output, index=values.index)

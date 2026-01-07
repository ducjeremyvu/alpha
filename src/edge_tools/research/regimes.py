from __future__ import annotations

import numpy as np
import pandas as pd


def build_context_labels(
    sliced: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, pd.DataFrame], pd.DataFrame, pd.DataFrame]:
    resampled = _resample_data(sliced)
    daily_context = _daily_context(resampled["1d"])
    hourly_context = _hourly_context(resampled["1h"])
    context = daily_context.merge(hourly_context, on="session_date", how="left")
    context["context_label"] = (
        context["daily_trend"].fillna("unknown")
        + "_"
        + context["hourly_trend"].fillna("unknown")
    )
    return context, resampled, daily_context, hourly_context


def _resample_data(data: pd.DataFrame) -> dict[str, pd.DataFrame]:
    data = data.copy()
    data = data.sort_values("time_ny")
    data = data.set_index("time_ny")
    resampled = {
        "1h": data.resample("1h").agg(_ohlcv_agg()).dropna(subset=["open"]),
        "1d": data.resample("1D").agg(_ohlcv_agg()).dropna(subset=["open"]),
    }
    for key, frame in resampled.items():
        frame.reset_index(inplace=True)
        frame["session_date"] = frame["time_ny"].dt.date
    return resampled


def _daily_context(data: pd.DataFrame) -> pd.DataFrame:
    frame = data.copy()
    frame["daily_range"] = frame["high"] - frame["low"]
    frame["daily_return"] = frame["close"] - frame["open"]
    frame["efficiency_ratio"] = frame["daily_return"].abs() / frame["daily_range"].replace(0, np.nan)

    frame["daily_trend"] = np.where(
        (frame["daily_return"] > 0) & (frame["efficiency_ratio"] > 0.55),
        "trend_up",
        np.where(
            (frame["daily_return"] < 0) & (frame["efficiency_ratio"] > 0.55),
            "trend_down",
            "balance",
        ),
    )

    frame["vol_regime"] = _quantile_regime(frame["daily_range"], 3)
    rolling_high = frame["high"].rolling(20, min_periods=5).max()
    rolling_low = frame["low"].rolling(20, min_periods=5).min()
    frame["location_in_range"] = (
        frame["open"] - rolling_low
    ) / (rolling_high - rolling_low).replace(0, np.nan)

    return frame[[
        "session_date",
        "daily_trend",
        "vol_regime",
        "daily_range",
        "efficiency_ratio",
        "location_in_range",
    ]]


def _hourly_context(data: pd.DataFrame) -> pd.DataFrame:
    frame = data.copy()
    frame = frame.sort_values("time_ny")
    frame["hour_range"] = frame["high"] - frame["low"]
    frame["hour_return"] = frame["close"] - frame["open"]

    def summarize_day(group: pd.DataFrame) -> pd.Series:
        early = group.iloc[:2]
        if early.empty:
            return pd.Series({
                "hourly_trend": "unknown",
                "early_behavior": "unknown",
                "acceptance": "unknown",
                "compression_state": "unknown",
            })
        early_range = early["high"].max() - early["low"].min()
        early_return = early["close"].iloc[-1] - early["open"].iloc[0]
        efficiency = abs(early_return) / (early_range if early_range else np.nan)

        if efficiency >= 0.6:
            hourly_trend = "trend"
        elif efficiency <= 0.25:
            hourly_trend = "balance"
        else:
            hourly_trend = "mixed"

        if early_range >= group["hour_range"].median() * 1.5 and efficiency < 0.2:
            early_behavior = "spike_fade"
        elif efficiency >= 0.6:
            early_behavior = "drive"
        else:
            early_behavior = "chop"

        midpoint = (early["high"].max() + early["low"].min()) / 2
        acceptance = "above_mid" if early["close"].iloc[-1] > midpoint else "below_mid"
        compression_state = "compression" if early_range < group["hour_range"].median() else "expansion"

        return pd.Series({
            "hourly_trend": hourly_trend,
            "early_behavior": early_behavior,
            "acceptance": acceptance,
            "compression_state": compression_state,
        })

    hourly_summary = frame.groupby("session_date", sort=True).apply(summarize_day)
    hourly_summary.reset_index(inplace=True)
    return hourly_summary


def _quantile_regime(series: pd.Series, bins: int) -> pd.Series:
    labels = ["low", "mid", "high"][:bins]
    return pd.qcut(series.rank(method="first"), bins, labels=labels)


def _ohlcv_agg() -> dict:
    return {
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
    }

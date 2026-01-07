from __future__ import annotations

from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {"time", "open", "high", "low", "close", "volume"}


def load_us500_data(path: str) -> pd.DataFrame:
    data = pd.read_csv(path)
    data = _normalize_columns(data)
    data["time"] = pd.to_datetime(data["time"], errors="coerce")
    if data["time"].dt.tz is None:
        data["time"] = data["time"].dt.tz_localize("UTC")
        data.attrs["timezone_assumption"] = "Naive timestamps assumed UTC"
    else:
        data["time"] = data["time"].dt.tz_convert("UTC")
        data.attrs["timezone_assumption"] = "Timestamps converted to UTC"
    return data


def summarize_data_health(data: pd.DataFrame) -> dict:
    data = data.copy()
    data = data.sort_values("time")
    data["time"] = pd.to_datetime(data["time"], utc=True)
    time_deltas = data["time"].diff().dropna()
    expected = pd.Timedelta(minutes=5)
    missing_intervals = time_deltas[time_deltas > expected]
    duplicate_times = data["time"].duplicated().sum()
    null_counts = data.isna().sum().to_dict()
    day_counts = data["time"].dt.day_name().value_counts().to_dict()
    start = data["time"].min()
    end = data["time"].max()
    return {
        "rows": int(len(data)),
        "columns": list(data.columns),
        "start": str(start),
        "end": str(end),
        "duplicates": int(duplicate_times),
        "missing_intervals": int(len(missing_intervals)),
        "missing_interval_minutes": float(missing_intervals.dt.total_seconds().sum() / 60),
        "null_counts": {key: int(value) for key, value in null_counts.items()},
        "day_of_week_distribution": {key: int(value) for key, value in day_counts.items()},
        "timezone_note": data.attrs.get("timezone_assumption", ""),
    }


def _normalize_columns(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()
    data.columns = [col.strip().lower() for col in data.columns]
    missing = REQUIRED_COLUMNS.difference(set(data.columns))
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    return data

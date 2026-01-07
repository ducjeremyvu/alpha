from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_us500_csvs(paths: list[str] | str) -> pd.DataFrame:
    path_list = _expand_paths(paths)
    frames = [pd.read_csv(path) for path in path_list]
    data = pd.concat(frames, ignore_index=True)
    data["Time"] = pd.to_datetime(data["Time"], utc=True)
    return data


def filter_first_window(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()
    data["time_et"] = data["Time"].dt.tz_convert("America/New_York")
    data["date_et"] = data["time_et"].dt.date
    data["time_et_only"] = data["time_et"].dt.time
    start = pd.Timestamp("09:30").time()
    end = pd.Timestamp("12:00").time()
    return data[(data["time_et_only"] >= start) & (data["time_et_only"] < end)]


def compute_first_window_features(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()
    numeric_columns = ["Open", "High", "Low", "Close", "Volume"]
    data[numeric_columns] = data[numeric_columns].apply(pd.to_numeric, errors="coerce")
    grouped = data.groupby("date_et", sort=True)
    summary = grouped.agg(
        open_0930=("Open", "first"),
        close_1200=("Close", "last"),
        high_0930_1200=("High", "max"),
        low_0930_1200=("Low", "min"),
        volume_sum=("Volume", "sum"),
    )
    summary["range_0930_1200"] = summary["high_0930_1200"] - summary["low_0930_1200"]
    summary["return_0930_1200"] = summary["close_1200"] - summary["open_0930"]
    summary["return_pct_0930_1200"] = summary["return_0930_1200"] / summary["open_0930"]
    summary["vwap_0930_1200"] = (
        grouped.apply(_vwap)
        .reindex(summary.index)
        .astype(float)
    )
    summary.reset_index(inplace=True)
    return summary


def _expand_paths(paths: list[str] | str) -> list[Path]:
    if isinstance(paths, str):
        paths = [paths]
    expanded: list[Path] = []
    for path in paths:
        path_obj = Path(path)
        if "*" in path_obj.as_posix():
            expanded.extend(Path().glob(path))
        else:
            expanded.append(path_obj)
    if not expanded:
        raise FileNotFoundError(f"No CSVs found for: {paths}")
    return expanded


def _vwap(frame: pd.DataFrame) -> float:
    volume = frame["Volume"].sum()
    if volume == 0:
        return float("nan")
    return (frame["Close"] * frame["Volume"]).sum() / volume

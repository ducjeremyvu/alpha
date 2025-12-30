#!/usr/bin/env python3
"""Label each hour with simple intraday state and daily regime context."""

from __future__ import annotations

import argparse
import csv
import math
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Deque, Dict, Iterable, List, Optional


@dataclass
class Config:
    hourly_csv: Path
    daily_csv: Path
    output_csv: Path
    vol_window: int


class RollingStd:
    def __init__(self, window: int) -> None:
        self.window = window
        self.values: Deque[float] = deque()
        self.total = 0.0
        self.total_sq = 0.0

    def push(self, value: float) -> Optional[float]:
        self.values.append(value)
        self.total += value
        self.total_sq += value * value
        if len(self.values) > self.window:
            dropped = self.values.popleft()
            self.total -= dropped
            self.total_sq -= dropped * dropped
        if len(self.values) < self.window:
            return None
        mean = self.total / self.window
        variance = (self.total_sq / self.window) - (mean * mean)
        return math.sqrt(max(0.0, variance))


def parse_args() -> Config:
    parser = argparse.ArgumentParser(
        description="Label each hour with intraday state and daily regime context."
    )
    parser.add_argument(
        "--hourly",
        default="data/SPY_hourly.csv",
        help="Hourly bars CSV from Alpaca.",
    )
    parser.add_argument(
        "--daily",
        default="data/SPY_daily_labeled.csv",
        help="Daily labeled CSV (output of market_state_label.py).",
    )
    parser.add_argument(
        "--output",
        default="data/SPY_hourly_labeled.csv",
        help="Output CSV with hourly labels.",
    )
    parser.add_argument(
        "--vol-window",
        type=int,
        default=20,
        help="Rolling window for hourly return volatility.",
    )
    args = parser.parse_args()

    return Config(
        hourly_csv=Path(args.hourly),
        daily_csv=Path(args.daily),
        output_csv=Path(args.output),
        vol_window=args.vol_window,
    )


def read_rows(path: Path) -> List[Dict[str, str]]:
    with path.open("r", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def to_float(value: str) -> float:
    return float(value)


def date_key(timestamp: str) -> str:
    return timestamp.split(" ")[0]


def load_daily_map(rows: Iterable[Dict[str, str]]) -> Dict[str, Dict[str, str]]:
    daily_map: Dict[str, Dict[str, str]] = {}
    for row in rows:
        daily_map[date_key(row["timestamp"])]= row
    return daily_map


def build_time_buckets(hourly_rows: List[Dict[str, str]]) -> Dict[int, str]:
    day_to_indices: Dict[str, List[int]] = {}
    for idx, row in enumerate(hourly_rows):
        day = date_key(row["timestamp"])
        day_to_indices.setdefault(day, []).append(idx)

    index_to_bucket: Dict[int, str] = {}
    for indices in day_to_indices.values():
        count = len(indices)
        for pos, idx in enumerate(indices):
            if count == 1:
                bucket = "mid"
            else:
                ratio = pos / (count - 1)
                if ratio <= (1.0 / 3.0):
                    bucket = "morning"
                elif ratio <= (2.0 / 3.0):
                    bucket = "mid"
                else:
                    bucket = "late"
            index_to_bucket[idx] = bucket
    return index_to_bucket


def label_rows(
    hourly_rows: List[Dict[str, str]],
    daily_map: Dict[str, Dict[str, str]],
    cfg: Config,
) -> List[Dict[str, str]]:
    vol = RollingStd(cfg.vol_window)
    prev_close: Optional[float] = None
    bucket_by_index = build_time_buckets(hourly_rows)

    labeled: List[Dict[str, str]] = []
    for idx, row in enumerate(hourly_rows):
        close = to_float(row["close"])
        hourly_return = None
        if prev_close is not None:
            hourly_return = (close / prev_close) - 1.0

        hourly_vol = vol.push(hourly_return) if hourly_return is not None else None

        day = date_key(row["timestamp"])
        daily = daily_map.get(day)
        day_low = to_float(daily["low"]) if daily else None
        day_high = to_float(daily["high"]) if daily else None

        pos_in_range = None
        if day_low is not None and day_high is not None:
            day_range = day_high - day_low
            if day_range != 0:
                pos_in_range = (close - day_low) / day_range

        out = dict(row)
        out.update(
            {
                "hourly_return": "" if hourly_return is None else f"{hourly_return:.6f}",
                "hourly_vol": "" if hourly_vol is None else f"{hourly_vol:.6f}",
                "day_range_pos": "" if pos_in_range is None else f"{pos_in_range:.6f}",
                "tod_bucket": bucket_by_index.get(idx, ""),
                "daily_trend": "" if not daily else daily.get("trend", ""),
                "daily_volatility": "" if not daily else daily.get("volatility", ""),
                "daily_regime_label": "" if not daily else daily.get("regime_label", ""),
            }
        )
        labeled.append(out)
        prev_close = close

    return labeled


def write_rows(path: Path, rows: List[Dict[str, str]]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    cfg = parse_args()
    hourly_rows = read_rows(cfg.hourly_csv)
    daily_rows = read_rows(cfg.daily_csv)
    daily_map = load_daily_map(daily_rows)
    labeled = label_rows(hourly_rows, daily_map, cfg)
    write_rows(cfg.output_csv, labeled)
    print(f"Wrote {cfg.output_csv}")


if __name__ == "__main__":
    main()

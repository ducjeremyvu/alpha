#!/usr/bin/env python3
"""Label each day with a simple market state using daily bars."""

from __future__ import annotations

import argparse
import csv
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Deque, Dict, Iterable, List, Optional


@dataclass
class Config:
    input_csv: Path
    output_csv: Path
    atr_window: int
    short_ma: int
    long_ma: int
    vol_window: int
    trend_tolerance: float


class RollingMean:
    def __init__(self, window: int) -> None:
        self.window = window
        self.values: Deque[float] = deque()
        self.total = 0.0

    def push(self, value: float) -> Optional[float]:
        self.values.append(value)
        self.total += value
        if len(self.values) > self.window:
            self.total -= self.values.popleft()
        if len(self.values) < self.window:
            return None
        return self.total / self.window


def parse_args() -> Config:
    parser = argparse.ArgumentParser(
        description="Label each day with a market state using daily bars."
    )
    parser.add_argument(
        "--input",
        default="data/SPY_daily.csv",
        help="Input daily CSV from Alpaca.",
    )
    parser.add_argument(
        "--output",
        default="data/SPY_daily_labeled.csv",
        help="Output CSV with labels.",
    )
    parser.add_argument("--atr-window", type=int, default=14, help="ATR window.")
    parser.add_argument("--short-ma", type=int, default=20, help="Short SMA window.")
    parser.add_argument("--long-ma", type=int, default=50, help="Long SMA window.")
    parser.add_argument(
        "--vol-window",
        type=int,
        default=20,
        help="Rolling mean window for volatility regime.",
    )
    parser.add_argument(
        "--trend-tolerance",
        type=float,
        default=0.001,
        help="Tolerance for flat trend (fraction).",
    )
    args = parser.parse_args()

    return Config(
        input_csv=Path(args.input),
        output_csv=Path(args.output),
        atr_window=args.atr_window,
        short_ma=args.short_ma,
        long_ma=args.long_ma,
        vol_window=args.vol_window,
        trend_tolerance=args.trend_tolerance,
    )


def read_rows(path: Path) -> List[Dict[str, str]]:
    with path.open("r", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def to_float(value: str) -> float:
    return float(value)


def label_rows(rows: Iterable[Dict[str, str]], cfg: Config) -> List[Dict[str, str]]:
    tr_mean = RollingMean(cfg.atr_window)
    close_short = RollingMean(cfg.short_ma)
    close_long = RollingMean(cfg.long_ma)
    atr_mean = RollingMean(cfg.vol_window)

    labeled: List[Dict[str, str]] = []
    prev_close: Optional[float] = None

    for row in rows:
        high = to_float(row["high"])
        low = to_float(row["low"])
        close = to_float(row["close"])

        daily_return = None
        if prev_close is not None:
            daily_return = (close / prev_close) - 1.0

        daily_range = high - low

        if prev_close is None:
            true_range = daily_range
        else:
            true_range = max(
                daily_range,
                abs(high - prev_close),
                abs(low - prev_close),
            )

        atr = tr_mean.push(true_range)
        sma_short = close_short.push(close)
        sma_long = close_long.push(close)
        atr_sma = atr_mean.push(atr) if atr is not None else None

        trend = None
        if sma_short is not None and sma_long is not None:
            if sma_short > sma_long * (1 + cfg.trend_tolerance):
                trend = "up"
            elif sma_short < sma_long * (1 - cfg.trend_tolerance):
                trend = "down"
            else:
                trend = "flat"

        volatility = None
        if atr is not None and atr_sma is not None:
            volatility = "expanding" if atr >= atr_sma else "compressing"

        date = row["timestamp"].split(" ")[0]
        label = None
        if trend and volatility:
            label = f"{date} - {trend}trend + {volatility} volatility"

        out = dict(row)
        out.update(
            {
                "daily_return": "" if daily_return is None else f"{daily_return:.6f}",
                "daily_range": f"{daily_range:.6f}",
                "true_range": f"{true_range:.6f}",
                "atr": "" if atr is None else f"{atr:.6f}",
                "atr_sma": "" if atr_sma is None else f"{atr_sma:.6f}",
                "sma_short": "" if sma_short is None else f"{sma_short:.6f}",
                "sma_long": "" if sma_long is None else f"{sma_long:.6f}",
                "trend": "" if trend is None else trend,
                "volatility": "" if volatility is None else volatility,
                "regime_label": "" if label is None else label,
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
    rows = read_rows(cfg.input_csv)
    labeled = label_rows(rows, cfg)
    write_rows(cfg.output_csv, labeled)
    print(f"Wrote {cfg.output_csv}")


if __name__ == "__main__":
    main()

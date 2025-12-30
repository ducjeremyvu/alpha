#!/usr/bin/env python3
"""Download hourly and daily market data for a single asset."""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

from alpaca.data.historical import CryptoHistoricalDataClient, StockHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest, StockBarsRequest
from alpaca.data.timeframe import TimeFrame

load_dotenv()


@dataclass
class Config:
    symbol: str
    asset_class: str
    start: datetime
    end: datetime
    out_dir: Path
    api_key: Optional[str]
    api_secret: Optional[str]


def parse_args() -> Config:
    parser = argparse.ArgumentParser(
        description="Download hourly and daily bar data via Alpaca Market Data API."
    )
    parser.add_argument(
        "--symbol",
        default="AAPL",
        help="Asset symbol, e.g. AAPL or BTC/USD.",
    )
    parser.add_argument(
        "--asset-class",
        choices=["stocks", "crypto"],
        default="stocks",
        help="Market data asset class.",
    )
    parser.add_argument(
        "--start",
        required=True,
        help="Start date/time (ISO-8601), e.g. 2024-01-01 or 2024-01-01T00:00:00.",
    )
    parser.add_argument(
        "--end",
        required=True,
        help="End date/time (ISO-8601), e.g. 2024-01-31 or 2024-01-31T23:59:59.",
    )
    parser.add_argument(
        "--out-dir",
        default="data",
        help="Output directory for CSV files.",
    )
    args = parser.parse_args()

    start = datetime.fromisoformat(args.start)
    end = datetime.fromisoformat(args.end)

    api_key = os.environ.get("APCA_API_KEY_ID")
    api_secret = os.environ.get("APCA_API_SECRET_KEY")

    return Config(
        symbol=args.symbol,
        asset_class=args.asset_class,
        start=start,
        end=end,
        out_dir=Path(args.out_dir),
        api_key=api_key,
        api_secret=api_secret,
    )


def build_client(cfg: Config):
    if cfg.asset_class == "crypto":
        # Alpaca allows unauthenticated historical crypto data.
        return CryptoHistoricalDataClient()

    if not cfg.api_key or not cfg.api_secret:
        raise SystemExit(
            "Missing API keys. Set APCA_API_KEY_ID and APCA_API_SECRET_KEY for stocks."
        )

    return StockHistoricalDataClient(cfg.api_key, cfg.api_secret)


def fetch_bars(cfg: Config, timeframe: TimeFrame):
    if cfg.asset_class == "crypto":
        request = CryptoBarsRequest(
            symbol_or_symbols=[cfg.symbol],
            timeframe=timeframe,
            start=cfg.start,
            end=cfg.end,
        )
        return build_client(cfg).get_crypto_bars(request)

    request = StockBarsRequest(
        symbol_or_symbols=[cfg.symbol],
        timeframe=timeframe,
        start=cfg.start,
        end=cfg.end,
    )
    return build_client(cfg).get_stock_bars(request)


def save_bars_to_csv(bars, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df = bars.df
    df.to_csv(out_path)


def main() -> None:
    cfg = parse_args()

    hourly = fetch_bars(cfg, TimeFrame.Hour)
    daily = fetch_bars(cfg, TimeFrame.Day)

    hourly_path = cfg.out_dir / f"{cfg.symbol.replace('/', '-')}_hourly.csv"
    daily_path = cfg.out_dir / f"{cfg.symbol.replace('/', '-')}_daily.csv"

    save_bars_to_csv(hourly, hourly_path)
    save_bars_to_csv(daily, daily_path)

    print(f"Saved hourly bars to {hourly_path}")
    print(f"Saved daily bars to {daily_path}")


if __name__ == "__main__":
    main()

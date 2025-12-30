# Alpaca Market Data Download Script

This note explains how to use `scripts/market_data_download.py`, with runnable examples and expected outputs.

## What the script does

- Downloads hourly and daily bar data for a single asset.
- Writes two CSV files into an output directory.
- Supports `stocks` (requires API keys) and `crypto` (historical crypto can be unauthenticated).

## Prerequisites

- Python 3.10+ (or compatible with `alpaca-py`)
- Packages:
  - `alpaca-py`
  - `pandas`

Install:

```
pip install alpaca-py pandas
```

## API keys (stocks only)

Set these environment variables when using `--asset-class stocks`:

```
export APCA_API_KEY_ID="your_key"
export APCA_API_SECRET_KEY="your_secret"
```

## Basic usage

### Stocks example (AAPL)

```
uv run python scripts/market_data_download.py --symbol AAPL --asset-class stocks --start 2024-01-01 --end 2024-01-31
```

Output files:

- `data/AAPL_hourly.csv`
- `data/AAPL_daily.csv`

### Crypto example (BTC/USD)

```
uv run python scripts/market_data_download.py --symbol BTC/USD --asset-class crypto --start 2024-01-01 --end 2024-01-07
```

Output files:

- `data/BTC-USD_hourly.csv`
- `data/BTC-USD_daily.csv`

## Options and arguments

- `--symbol` Asset symbol, e.g. `AAPL` or `BTC/USD`.
- `--asset-class` `stocks` or `crypto`.
- `--start` Start datetime, ISO-8601 (e.g. `2024-01-01` or `2024-01-01T00:00:00`).
- `--end` End datetime, ISO-8601.
- `--out-dir` Output folder (default `data`).

## Notes

- The script writes CSVs using the DataFrame returned by `alpaca-py`.
- If you pass date-only values, they are interpreted as midnight local time.
- For other asset classes or endpoints, see `alpaca-market-data-api.md`.

## Suggested rename and location

- Suggested file name: `scripts/market_data_download.py`
- Reason: it is a runnable utility and matches the existing `scripts/` folder.
- If you rename or move it, update the examples in this doc accordingly.

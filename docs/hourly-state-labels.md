# Hourly State Labels (Intraday)

This guide explains how to label each hour with a simple intraday state and join it to the daily regime.

## What the script does

For each hourly bar, it computes:

- Hourly return (close vs previous close)
- Rolling hourly volatility (std dev of hourly returns)
- Position in the day range (0 to 1)
- Time-of-day bucket (morning / mid / late)

Then it joins daily context from the labeled daily file so every hour knows:

- The day trend (up / down / flat)
- The day volatility regime (expanding / compressing)
- The daily regime label

## Input

- Hourly bars CSV (default: `data/SPY_hourly.csv`)
- Daily labeled CSV (default: `data/SPY_daily_labeled.csv`)

## Output

- Labeled CSV (default: `data/SPY_hourly_labeled.csv`)
- Adds columns:
  - `hourly_return`
  - `hourly_vol`
  - `day_range_pos`
  - `tod_bucket`
  - `daily_trend`
  - `daily_volatility`
  - `daily_regime_label`

## Basic usage

```
uv run python scripts/hourly_state_label.py \
  --hourly data/SPY_hourly.csv \
  --daily data/SPY_daily_labeled.csv \
  --output data/SPY_hourly_labeled.csv
```

## Options

- `--vol-window` Rolling window for hourly volatility (default `20`)

## Notes

- Time-of-day buckets are assigned by splitting each trading day into thirds of the available hourly bars.
- Position in day range uses the daily high/low from the labeled daily file.
- This is intentionally simple and meant for context, not prediction.

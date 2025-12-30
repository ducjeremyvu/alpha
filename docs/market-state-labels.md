# Market State Labels (Daily)

This guide explains how to label each trading day with a simple market state using `scripts/market_state_label.py`.

## What the script does

For each daily bar, it computes:

- Daily return (close vs previous close)
- Daily range (high - low)
- True range and ATR (rolling mean of true range)
- Short SMA vs long SMA (trend proxy)
- Volatility regime (ATR vs rolling mean of ATR)

Then it assigns a regime label:

- Trend: `up`, `down`, `flat`
- Volatility: `expanding`, `compressing`

Example label:

```
2024-03-12 - uptrend + expanding volatility
```

## Input

- Daily bars CSV (default: `data/SPY_daily.csv`)
- Expected columns: `timestamp`, `open`, `high`, `low`, `close`

## Output

- Labeled CSV (default: `data/SPY_daily_labeled.csv`)
- Adds columns:
  - `daily_return`
  - `daily_range`
  - `true_range`
  - `atr`
  - `atr_sma`
  - `sma_short`
  - `sma_long`
  - `trend`
  - `volatility`
  - `regime_label`

## Basic usage

```
uv run python scripts/market_state_label.py \
  --input data/SPY_daily.csv \
  --output data/SPY_daily_labeled.csv
```

## Options

- `--atr-window` Rolling window for ATR (default `14`)
- `--short-ma` Short SMA window (default `20`)
- `--long-ma` Long SMA window (default `50`)
- `--vol-window` Rolling window for ATR mean (default `20`)
- `--trend-tolerance` Flat threshold as a fraction (default `0.001`)

Example with custom windows:

```
uv run python scripts/market_state_label.py \
  --input data/SPY_daily.csv \
  --output data/SPY_daily_labeled.csv \
  --atr-window 10 \
  --short-ma 15 \
  --long-ma 40 \
  --vol-window 15
```

## Notes

- The label is only available once enough data exists to compute the rolling metrics.
- This is intentionally simple: no market regime nuance beyond trend + volatility.

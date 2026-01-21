# Daily Next Candle Behavior

## Goal
Quickly summarize how the next daily candle behaves after a green or red candle.
"Green" means `close > open`, "red" means `close < open`, and anything else is
marked as neutral.

## Script
`scripts/experiments/daily_next_candle_behavior.py` loads daily candles from
`ohlcv_daily`, labels each candle, shifts the label to get the next candle type,
and prints counts plus per-group rates.

## Run
```bash
SYMBOL=US500 uv run python scripts/experiments/daily_next_candle_behavior.py
```

## Output
- A flat table of counts/rates by `candle_type` → `next_candle_type`.
- A pivot table of rates so you can read green/red follow-through at a glance.

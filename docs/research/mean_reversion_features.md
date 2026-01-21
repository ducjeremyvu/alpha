# Mean Reversion Feature Guide

This is a practical guide for which features in
`src/edge_tools/research/features.py` are most useful for mean-reversion
signals on 5-minute candles.

## Core (Necessary) Features

These are the minimum features you need for a basic mean-reversion signal.

- `close_open`: direction and magnitude of the candle body.
- `range`: volatility per candle for simple thresholds.
- `rolling_range_mean`: baseline range for “stretch” detection.
- `return_pct`: normalized move, useful for volatility scaling.

## Nice-to-Have Features

These help filter or improve signals but are not required.

- `position_in_range`: close location within the candle; helps detect exhaustion.
- `upper_wick` / `lower_wick`: rejection wicks, often helpful for fades.
- `rolling_vol`: volatility regime filtering.
- `compression`: identify pre-stretch consolidation before reversal.
- `direction_streak`: avoid fading strong multi-bar runs.

## Context/Session Features (Optional Filters)

Useful for session-level context and for filtering out choppy vs. trending days.

- `efficiency_ratio`: trendiness vs. chop in the session window.
- `net_move`: overall directional bias of the window.
- `range_0930_1200`: helps normalize stretch size by day.
- `mfe_from_open` / `mae_from_open`: tells how far price has already stretched.

## Practical Starting Rule (Example)

- Trigger when `abs(close - session_open) > 1.5 * rolling_range_mean`.
- Optional filter: `position_in_range` near extremes and wicks present.
- Exit on 3–6 bars forward or a partial reversion to the open.

# Daily Candle Signal Plan

## Goal
Build a daily-candle dataset that filters for days where **T0 closes above T-1 high**, then label the **T1 candle direction** (bullish/bearish) for later evaluation.

## Assumptions
- Data source: daily OHLCV candles in DuckDB (e.g., `ohlcv_daily`).
- Symbol filter (if needed): `US500`.
- Candle direction: bullish if `close > open`, bearish if `close < open`, neutral if equal.

## Plan
1. **Confirm data source**
   - Verify table name (`ohlcv_daily`) and required columns (`timestamp`, `open`, `high`, `low`, `close`).
   - Confirm symbol filtering column (e.g., `symbol`) and values.

2. **Define candle direction**
   - Create a derived column `candle_type` for each day using `close` vs `open`.
   - Decide how to treat equal close/open (set to `neutral` or drop).

3. **Add lag/lead features**
   - Compute `prev_high` = T-1 `high` (lag 1).
   - Compute `next_candle_type` = T+1 `candle_type` (lead 1).

4. **Filter for the signal**
   - Keep rows where `close > prev_high` (T0 close above T-1 high).
   - Drop rows without `next_candle_type` (last candle has no T1).

5. **Output dataset**
   - Store a filtered dataframe/table with:
     - T0 OHLCV
     - `prev_high`
     - `candle_type`
     - `next_candle_type`
   - Save as a DuckDB table (e.g., `daily_close_above_prev_high`).

6. **Sanity checks**
   - Count total rows vs filtered rows.
   - Validate a few samples manually to confirm lag/lead alignment.

## Future Extensions (Optional)
- Split by regimes, month, or weekday.
- Add forward return metrics (T+1, T+3, T+6).
- Compare conditional probability of bullish T1 vs baseline.

## Implementation Notes
- Core logic lives in `src/edge_tools/research/daily_signals.py`.
- Runner script lives in `scripts/experiments/daily_close_above_prev_high.py`.
- Output table defaults to `daily_close_above_prev_high` (override with `OUTPUT_TABLE`).
- Forward return columns default to 1, 3, 6 days (`fwd_return_1`, `fwd_return_3`, `fwd_return_6`).

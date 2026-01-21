# Ingest Resample Plan (Approval-Gated)

## Goal
Auto-derive higher timeframes from ingested minute data, only when missing, with idempotent inserts.

## Scope
- Source of truth: `ohlcv_minute`.
- Targets: `ohlcv_hour`, `ohlcv_daily`, `ohlcv_weekly` (optional: `ohlcv_15m`, `ohlcv_30m`).
- Preserve vendor-downloaded candles by inserting only when missing.

## Approval-Gated Steps
1. **Review ingest + schema**
   - Confirm current ingest flow and existing tables.
   - Check how minute data is inserted and how tables are defined.

2. **Define resampling rules + boundaries**
   - Canonical path: minute → hour/daily/weekly.
   - Default daily boundary: `date_trunc('day', time)` (UTC day).
   - Hourly boundary: `date_trunc('hour', time)`.
   - Weekly boundary: `date_trunc('week', time)`.
   - Optional 15m/30m use `date_bin` (or equivalent) if tables added.
   - OHLCV aggregation:
     - `open = min_by(open, time)`
     - `high = max(high)`
     - `low = min(low)`
     - `close = max_by(close, time)`
     - `volume = sum(volume)`

3. **Design missing-interval detection**
   - Align resample window to full hour boundaries before resampling.
   - Use idempotent inserts (`ON CONFLICT DO NOTHING`) so existing rows remain.

4. **Specify idempotent insert strategy**
   - Use `ON CONFLICT DO NOTHING` for resample inserts.
   - Capture `file_start`/`file_end` during ingest and align the resample window.

5. **Outline config + pipeline integration**
   - `TIMEFRAME_SOURCE=download|resample|auto` (default `auto`).
   - `RESAMPLE_TIMEFRAMES=15m,30m,1h,1d,1w,1d_rth` (comma separated).
   - Resample runs after minute ingest unless `TIMEFRAME_SOURCE=download`.

## Usage Notes
- Run `make ingest-minute` after dropping new minute CSVs in `price_data/` (or set `DATAPATH`).
- Derived tables created automatically: `ohlcv_15m`, `ohlcv_30m`, `ohlcv_hour`, `ohlcv_daily`, `ohlcv_daily_rth`, `ohlcv_weekly`.
- Daily full uses UTC day buckets; RTH daily uses NY 09:30–16:00.

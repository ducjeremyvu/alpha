# Pipeline Run Results (US500)

## Run Summary
- Input: `data/raw/us500/US500_Minute5_20260107_1319.csv`
- Session: 09:30–12:00 America/New_York (bars by open time)
- Context filter for backtest: `balance_trend`, `trend_up_balance`, `trend_up_mixed`

## Steps Executed
1. Load CSV, normalize columns, and validate data health.
2. Convert timestamps to America/New_York and slice 09:30–12:00 ET.
3. Generate per‑bar and per‑day features.
4. Resample to 1H/1D and label daily/hourly regimes.
5. Detect rule‑based pattern candidates.
6. Backtest with manual‑style constraints and chronological splits.
7. Produce playbook + report.

## Outputs Written
- `outputs/data_sliced.parquet`
- `outputs/features.parquet`
- `outputs/daily_summary.parquet`
- `outputs/data_1h.parquet`
- `outputs/data_1d.parquet`
- `outputs/daily_context.parquet`
- `outputs/hourly_context.parquet`
- `outputs/regime_labels.parquet`
- `outputs/pattern_candidates.json`
- `outputs/backtest_results.parquet`
- `outputs/playbook.md`
- `outputs/report.md`

## Results Snapshot
- Sessions analyzed: `264`
- Pattern signals: `1,104`
- Backtest trades (filtered contexts): `70`
- Win rate: `48.57%`
- Expectancy: `0.94`
- Profit factor: `1.26`

## Notes
- Missing intervals: `277` (see `outputs/report.md`).
- UTC timestamps were assumed when timestamps were naive.

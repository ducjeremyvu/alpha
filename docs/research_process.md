# US500 Intraday Research Process

## High-Level Goal
Build a slow, repeatable research pipeline that turns intraday 5-minute patterns into a discretionary trading playbook. The focus is interpretability, regime awareness, and manual execution rules — not ML prediction.

## Pipeline Outline
1. **Load & Inspect**
   - Read the CSV, normalize columns, infer timezone (assume UTC for naive timestamps), and report data health (duplicates, gaps, range).
2. **Session Slice**
   - Convert to America/New_York, keep 09:30–12:00 ET bars, add session metadata, save `outputs/data_sliced.parquet`.
3. **Feature Engineering**
   - Create interpretable per‑bar features (returns, range, wicks, impulse, compression) and per‑day summaries.
4. **Higher-Timeframe Context**
   - Resample to 1H and 1D, compute daily/hourly trend and volatility regimes.
5. **Pattern Library**
   - Detect rule‑based 5‑minute patterns and report frequency + forward metrics.
6. **Backtest**
   - Apply a simple manual‑trade template (1 trade per direction, stop/target, time exit), split chronologically.
7. **Robustness**
   - Run parameter sensitivity sweeps and track expectancy changes.
8. **Playbook + Report**
   - Convert winners into a human‑executable playbook and save a full report.

## How to Run
```bash
uv run python scripts/entrypoints/run_pipeline.py
```

## Outputs (Deterministic)
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

## High-Level Architecture
- **Core modules:** `src/edge_tools/research/*.py`
- **Orchestrator:** `scripts/entrypoints/run_pipeline.py`
- **Artifacts:** `outputs/`

The process is designed to be re-run as data grows, with consistent outputs and context-aware pattern evaluation.

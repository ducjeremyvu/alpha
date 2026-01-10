# Changelog

## 2026-01-08
### Added
- Documentation index at `docs/README.md` with quality commands.
- Cleanup notes in `docs/project_tidy_plan.md` with completed checklist.

### Changed
- Consolidated entrypoints under `scripts/entrypoints/` and Streamlit apps under `scripts/streamlit/`.
- Grouped scripts into `scripts/ingest/` and `scripts/maintenance/`.
- Moved experiments to `scripts/experiments/`.
- Organized notebooks into `notebooks/us500/` and `notebooks/exports/`.
- Renamed `frontend/` to `frontend-demo/`.
- Updated `Makefile`, docs, and summaries to reflect new paths.

### Maintenance
- Added project artifact ignores to `.gitignore` (DuckDB, outputs).
- Added data conventions to `DATASET.md`.

## 2026-01-07
### Added
- End-to-end intraday research pipeline under `src/edge_tools/research/`.
- `scripts/entrypoints/run_pipeline.py` orchestrator for loading, slicing, features, regimes, patterns, backtest, and report outputs.
- US500 pattern library, backtest engine, and playbook/report generators.
- Documentation: `docs/data_workflow.md` updates and new `docs/research_process.md`.
- Structured outputs under `outputs/` (parquet, json, markdown).

### Data
- Copied `price_data/US500_Minute5_20260107_1319.csv` to `data/raw/us500/`.

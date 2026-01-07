# Changelog

## 2026-01-07
### Added
- End-to-end intraday research pipeline under `src/edge_tools/research/`.
- `run_pipeline.py` orchestrator for loading, slicing, features, regimes, patterns, backtest, and report outputs.
- US500 pattern library, backtest engine, and playbook/report generators.
- Documentation: `docs/data_workflow.md` updates and new `docs/research_process.md`.
- Structured outputs under `outputs/` (parquet, json, markdown).

### Data
- Copied `price_data/US500_Minute5_20260107_1319.csv` to `data/raw/us500/`.

# src/edge_tools tidy-up plan

## Goals
- Separate time-series helpers into a single subpackage for discoverability.
- Consolidate DuckDB/database utilities under `edge_tools/db`.
- Reduce top-level module sprawl and make import paths predictable.

## Proposed target structure
```
edge_tools/
  api/
  backtest/
  db/
  ingest/
  analytics/
  metrics/
  research/
  time_series/
  utils/
  constants.py
  logger.py
```

## Planned moves
- `date.py` → `time_series/date.py`
- `time.py` → `time_series/time.py`
- `us_open.py` → `time_series/us_open.py`
- `ohlcv.py` → `time_series/ohlcv.py`
- `open.py` → `time_series/open.py`
- `premarket.py` → `time_series/premarket.py`
- `database.py` → `db/database.py`

## Import updates
- Replace `edge_tools.date` → `edge_tools.time_series.date` (or re-export in `time_series/__init__.py`).
- Replace `edge_tools.ohlcv` → `edge_tools.time_series.ohlcv`.
- Replace `edge_tools.database` → `edge_tools.db.database`.

## Notes
- Keep `backtest/` at top-level because it is production research infrastructure.
- Add `edge_tools/time_series/__init__.py` with re-exports for commonly used helpers.
- Avoid moving `regimes.py` for now; it is used both in core and research.

## Rollout checklist
- [x] Move modules and update imports.
- [x] Run `uv run pytest tests/test_ohlcv.py tests/test_us_open.py`.
- [x] Update README or docs if any paths are user-facing.

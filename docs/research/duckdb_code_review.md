# DuckDB Code Review

## Rating
**6.5 / 10** — Solid baseline (central connection helper, migrations, SQL files), but inconsistent connection usage, some string‑formatted SQL, and missing performance/robustness conventions.

## Scope Reviewed
- `src/edge_tools/db/__init__.py`
- `src/edge_tools/db/database.py`
- `src/edge_tools/time_series/ohlcv.py`
- `src/edge_tools/ingest/__init__.py`
- `src/edge_tools/backtest/engine.py`
- `src/edge_tools/backtest/optimizer.py`
- `src/edge_tools/research/daily_signals.py`
- `sql/` migrations and ingestion queries

## What’s Working Well
- Single helper (`get_duckdb_connection`) used in most modules.
- SQL kept in `sql/` for ingestion and migrations.
- Reasonable table naming (`ohlcv_*`, metrics tables).
- Simple, readable flow for data ingestion and research scripts.

## Gaps / Risks
- **Inconsistent connection creation:** `time_series/ohlcv.py` calls `duckdb.connect("./local.duckdb")` directly instead of the shared helper.
- **String formatted SQL:** `_ohlcv_query` and some ad‑hoc queries are formatted with f‑strings, which is brittle and risks injection or quoting bugs.
- **DB path hard‑coded:** `local.duckdb` is repeated; no environment/config fallback.
- **No transaction boundaries** for large inserts or multi‑statement jobs.
- **Missing runtime settings** (threads, memory, object cache) for large backtests.
- **Limited error handling** for empty tables, missing symbols, or schema drift.

## Improvements (Priority Order)
1. **Centralize connection usage**
   - Replace direct `duckdb.connect` calls with `get_duckdb_connection`.
   - Add optional `db_path` + `read_only` args to script entrypoints.

2. **Parameterize all queries**
   - Use `con.execute(query, [params])` instead of f‑strings for symbol filtering.
   - Example: `SELECT ... WHERE symbol = ?`.

3. **Add connection config helper**
   - Set `PRAGMA threads`, `memory_limit`, `enable_object_cache` once per connection for heavy backtests.
   - Provide a `configure_duckdb(con, profile="research")` helper.

4. **Transactional inserts**
   - Wrap ingestion and optimizer writes in `BEGIN/COMMIT`.
   - Use `executemany` where possible for bulk inserts.

5. **Schema guards**
   - Add `ensure_table_exists` or `validate_schema` helpers for research tables.
   - Add descriptive errors when tables/columns are missing.

6. **Standardize time columns**
   - Ensure `time` columns are always timezone‑aware when loaded into pandas.
   - Add a `normalize_time` utility for all query results.

## Quick Wins
- Update `src/edge_tools/time_series/ohlcv.py` to use `get_duckdb_connection`.
- Refactor `_ohlcv_query` in `src/edge_tools/backtest/engine.py` to use parameter binding.
- Allow `DUCKDB_PATH` env override in `get_duckdb_connection`.

## Suggested Follow‑up Tasks
- Add a `db/config.py` module that sets connection pragmas by profile.
- Add a `db/query.py` helper to run parameterized SQL + return pandas frames.
- Create a lightweight integration test that loads from `local.duckdb` and validates schema presence for `ohlcv_daily`.

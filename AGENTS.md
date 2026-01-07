# Repository Guidelines

## Project Structure & Module Organization
- `src/edge_tools/` houses the core Python package (analytics, ingest, DB helpers, utilities).
- `api/` contains the FastAPI entrypoint (`main.py`).
- `scripts/` holds one-off maintenance jobs (table creation, ingestion, metrics).
- `sql/` includes DuckDB query files used by scripts.
- `tests/` stores pytest-based unit tests for package modules.
- `front-svelte/` is the SvelteKit UI, while `frontend/` is a small static demo.
- `notebooks/` and `price_data/` are for research and local datasets—avoid committing large data files.

## Build, Test, and Development Commands
- `uv run python main.py` runs the main application entrypoint.
- `make db-create-tables` initializes the DuckDB schema in `local.duckdb`.
- `make ingest-minute` ingests minute-level CSV data.
- `make backend` / `make frontend` / `make dev` run the CLI orchestration modes.
- `make format` applies `black` and `isort` to `src/`.
- `uv run pytest` executes the test suite.
- `cd front-svelte && npm install && npm run dev` starts the SvelteKit UI.

## Coding Style & Naming Conventions
- Python uses 4-space indentation and `snake_case` for modules and functions.
- Keep package code under `src/edge_tools/` and import using the package name.
- Format with `black` and sort imports with `isort` via `make format` before committing.
- TypeScript/Svelte in `front-svelte/` uses the local ESLint + Prettier setup (`npm run lint`).

## Testing Guidelines
- Tests are written with `pytest` and live in `tests/`.
- Name test files `test_*.py` and mirror the module under test when possible.
- Run focused tests with `uv run pytest tests/test_ohlcv.py` before broader runs.

## Commit & Pull Request Guidelines
- Git history shows short, lightweight commit messages; keep them concise and imperative.
- PRs should include a summary, test results, and notes about DB/data impacts.
- Include screenshots or screen recordings for UI changes in `front-svelte/`.

## Configuration & Data Notes
- DuckDB state lives in `local.duckdb`; recreate with `make db-create-tables` if needed.
- Keep environment secrets in `.env` (loaded via `python-dotenv`), not in code or commits.

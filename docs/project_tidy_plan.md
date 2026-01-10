# Project Tidy Plan

This is a structured cleanup proposal to make the repo easier to navigate and
reduce clutter. Steps 1–2 have been implemented; the rest are suggestions.

## 1) Separate Production vs. Experiments ✅

- Keep one-off experiments and scratch files under `scripts/experiments/`
  (e.g., `scripts/experiments/try.py`).
- Keep the repo root for entrypoints and docs only.

## 2) Consolidate Entry Points ✅

- Keep a single canonical entrypoint (likely `main.py` or `api/main.py`).
- Keep Streamlit apps under `scripts/streamlit/` (e.g.
  `scripts/streamlit/main_st.py`).
- Document each entrypoint in `README.md` with a short purpose statement.

## 3) Standardize Data Locations ✅

- Use `data/` (raw), `outputs/` (derived), and `price_data/` (local datasets),
  but avoid mixing them with notebooks and scripts.
- Add clear naming conventions and a short `DATASET.md` section describing
  expected CSV formats.

## 4) Minimize Generated Files in Repo Root ✅

- Remove or ignore artifacts such as `__pycache__/`, `.DS_Store`, logs
  (`app.log`), DuckDB files (`local.duckdb`, `identifier.db`), and
  `edge_tools.egg-info/`.
- Add missing entries to `.gitignore` to keep the repo clean.

## 5) Organize Research Assets ✅

- Move research notebooks from `edge/` into `notebooks/` or
  `notebooks/us500/` for clearer grouping.
- Keep raw data out of notebooks directories to reduce git bloat.

## 6) Clarify Frontend Scope ✅

- Keep `front-svelte/` as the main UI and treat `frontend-demo/` as a demo.

## 7) Scripts Hygiene ✅

- Grouped scripts by purpose: `scripts/analyses/`, `scripts/ingest/`,
  `scripts/maintenance/`.

## 8) Documentation Index ✅

- Add a `docs/README.md` index linking key docs (research, workflows,
  strategy experiments, dataset conventions).
- Keep `README.md` as an overview and point to the docs index.

## 9) Testing & Formatting ✅

- Document a standard flow: `make format` → `uv run pytest`.
- Keep tests in `tests/` and mirror the module path they cover.

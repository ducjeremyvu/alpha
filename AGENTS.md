# AGENTS

Project-specific guidance for Codex and other automation tools.

## Overview

- Repo includes market data scripts, docs, and datasets.
- Prefer small, focused utilities in `scripts/` and docs in `docs/`.

## Data files

- Store generated CSV outputs in `data/` by default.
- Keep ad-hoc datasets (e.g., downloads or experiments) in `price_data/` or a clearly named subfolder.
- Avoid committing large or redundant CSVs unless explicitly requested.

## Scripts

- Runnable utilities live in `scripts/`.
- Example: `scripts/market_data_download.py` writes hourly/daily CSVs to `data/`.
- Run Python commands via `uv run python`, not `python` directly.

## Docs

- Usage guides live in `docs/`.
- Reference material can live at repo root (e.g., `alpaca-market-data-api.md`).

## Conventions

- Use ASCII-only unless a file already contains Unicode.
- Prefer short, descriptive commit messages; add a body only for non-obvious changes.

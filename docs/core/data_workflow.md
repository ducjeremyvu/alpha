# Data & Research Workflow

## Directory Layout
- `data/raw/<asset>/` stores original CSVs as received.
- `data/processed/<asset>/` holds cleaned/parquet outputs.
- `data/metadata/` tracks dataset notes and schema references.
- `notebooks/<asset>/` contains exploratory analysis per asset.
- `sql/<asset>/` keeps asset-specific queries.

## Ingesting New Data
1. Place raw files in `data/raw/<asset>/` using descriptive filenames.
2. Record the dataset in `DATASET.md` with path, label, and description.
3. Create/refresh tables with `make db-create-tables` if needed.
4. Run ingestion scripts (e.g., `make ingest-minute`).

## Analysis Conventions
- Keep exploratory work in `notebooks/<asset>/`.
- Move reusable logic into `src/edge_tools/analytics/`.
- Store derived queries in `sql/<asset>/` for repeatability.

## US500 First 2.5-Hour Analysis
- Script: `scripts/analyses/us500_first_150.py`
- Purpose: Converts UTC bars to ET, filters 09:30–12:00 ET, and outputs per-day features.
- Default input: `data/raw/us500/*.csv`
- Default output: `data/processed/us500/us500_first_150_features.csv`
- Run: `uv run python scripts/analyses/us500_first_150.py`

## Naming
- Use lowercase asset keys for folders (e.g., `us500`).
- Use descriptive labels like `us500_minute5_2026_full_year`.

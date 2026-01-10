# Dataset Index

## Conventions
- Raw files live in `data/raw/<asset>/`.
- Processed outputs live in `data/processed/<asset>/`.
- Local scratch data can stay in `price_data/` (not committed).
- CSVs should include `time`, `open`, `high`, `low`, `close`, `volume` columns.
- Timestamps are expected in UTC (or timezone-naive, assumed UTC).
- Recommended filename pattern: `{ASSET}_Minute5_{YYYYMMDD_HHMM}.csv`.

## US500 Minute 5 Data (2026)
- **Path:** `data/raw/us500/US500_Minute5_20260107_1319.csv`
- **Asset:** US500 CFD
- **Description:** Full-year minute-5 price data for the US500 asset.
- **Label:** `us500_minute5_2026_full_year`

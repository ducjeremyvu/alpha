# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

**Alpha** is a trading analytics project focused on computing pre-market price movements and analyzing OHLCV (Open, High, Low, Close, Volume) data for financial instruments (primarily US500/S&P 500 futures). The package name is `edge_tools`.

The system ingests minute-level price data from CSV files, stores it in DuckDB, and provides analytics for pre-market sessions across multiple timezones (Tokyo, London, NY).

## Environment Setup

```bash
# Create and activate virtual environment (using system venv)
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux

# Install package in editable mode with dev dependencies
pip install -e ".[dev]"

# Install Jupyter kernel for notebooks
python -m ipykernel install --user --name edge-env --display-name "Python (edge)"
```

**Important**: This project requires Python >=3.12.

## Common Commands

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_date.py

# Run tests with verbose output
pytest -v
```

### Running the Streamlit App
```bash
streamlit run scripts/streamlit/main_st.py
```

### Database Operations
The DuckDB database (`local.duckdb`) is managed through the `edge_tools` package. No direct SQL commands needed - use the provided functions.

## Code Architecture

### Core Package Structure (`src/edge_tools/`)

The `edge_tools` package uses **lazy loading** via `__getattr__` in `__init__.py` - modules are only imported when first accessed, keeping imports lightweight.

#### Database Layer (`database.py`)
- **Primary function**: `insert_minute_file_data()` - Core ETL function that scans the data folder for unprocessed CSV files, extracts symbols from filenames, renders SQL templates with Jinja2, inserts data into DuckDB, and marks files as processed by appending `_done` to the filename
- **Connection management**: `get_duckdb_connection()` returns a DuckDB connection to `local.duckdb`
- **File tracking**: Files are marked as processed by renaming with `_done` suffix to prevent duplicate imports

#### SQL Template System (`dir.py`)
- SQL queries are stored as **Jinja2 templates** in the `sql/` directory
- `get_sql_query(name, **params)` loads and renders templates with parameters
- Pattern: Load template → Render with params → Execute query
- Key templates:
  - `create_ohlcv_minute_table.sql` - Schema with composite primary key (symbol, time)
  - `import_minute_data_with_symbol_from_csv.sql` - CSV import with conflict handling
  - `ohlcv_data__by_ticker_and_date.sql` - Date range queries for specific symbols

#### Timezone Processing (`time.py`)
- **Critical design**: All data is stored in UTC in DuckDB, then converted to local timezones for analysis
- `preprocess_for_premarket_analysis()` - Main pipeline function that:
  1. Converts index to UTC via `convert_index_to_utc()`
  2. Adds timezone-specific columns (NY, Tokyo, London, Shanghai, Hong Kong)
  3. Each timezone gets 4 columns: `{tz}_time`, `{tz}_hour`, `{tz}_minute`, `{tz}_time_only`
- Used by pre-market analysis to identify market opens/closes across global sessions

#### Pre-market Analytics (`premarket.py`)
- **`PremarketPriceCalculator`** class: Core analytics engine that:
  - Validates data contains exactly 2 trading days (current + previous)
  - Defines price selection points: US close (previous day), Tokyo open, London open, T-60/T-30/T-15 (pre-market), US open/close (current day)
  - `compute_price(selection_key)` extracts price at specific timezone + time combinations
- **Workflow**: 
  1. `compute_metrics()` orchestrates: fetch OHLCV data → normalize → preprocess timezones → compute prices → compute percentage changes
  2. Returns dictionary with all prices and percentage changes from previous day's close
- Used for daily pre-market analysis to identify gaps and momentum shifts

#### Data Normalization (`ohlcv.py`)
- `normalize_ohlcv()` - Handles varying column name conventions (Open/open/o, High/high/h, etc.) by mapping to standardized names
- `ohlcv_for_date_and_prev()` - Fetches data for selected date + previous day (required for pre-market calculations)
- Uses alias mapping system to support multiple input formats

#### Utilities
- `date.py` - `to_datetime()` universal converter (handles strings, timestamps, date objects)
- `constants.py` - Contains `DATAPATH` (external data folder location)
- `logger.py` - Logging setup utilities

### Data Flow

1. **Ingestion**: CSV files → `insert_minute_file_data()` → DuckDB `ohlcv_minute` table
2. **Retrieval**: SQL template + params → rendered query → DuckDB → pandas DataFrame
3. **Processing**: DataFrame → UTC conversion → timezone columns added → analytics computed
4. **Output**: Metrics dictionary + processed DataFrame

### Key Patterns

- **Jinja2 templating for SQL**: All queries are parameterized templates in `sql/` directory
- **Timezone-aware processing**: Store in UTC, analyze in local timezones
- **Lazy module loading**: Package uses `__getattr__` for on-demand imports
- **File processing workflow**: Scan → Extract symbol → Insert → Mark done
- **Two-day analysis window**: Pre-market calculations require current + previous trading day

### External Dependencies

- **DuckDB**: Embedded analytical database (single file: `local.duckdb`)
- **pandas**: DataFrame operations and time series manipulation
- **Jinja2**: SQL template rendering
- **pytz**: Timezone conversions (via pandas)
- **streamlit**: Web UI for daily analysis (`scripts/streamlit/main_st.py`)
- **plotly**: Candlestick chart visualization

### Data Storage

- **Database**: `local.duckdb` (ignored by git)
- **Data files**: External folder at path specified in `constants.DATAPATH`
- **CSV naming convention**: `{SYMBOL}_Minute_{date}_{time}.csv`
- **Schema**: `ohlcv_minute` table with composite key (symbol, time) and OHLCV columns

### Development Workflow

1. **Data import**: Place CSV files in data folder → run `insert_minute_file_data()` → files auto-renamed with `_done`
2. **Analysis**: Use notebooks in `notebooks/` for exploratory work
3. **Testing**: Write tests in `tests/` following pytest conventions
4. **Visualization**: Run Streamlit app to view pre-market metrics and candlestick charts

### Testing Notes

- Tests use pytest framework
- Test files follow `test_*.py` naming convention
- Existing tests cover date conversion utilities (`test_date.py`)
- OHLCV and timezone processing tested in `test_ohlcv.py`, `test_us_open.py`

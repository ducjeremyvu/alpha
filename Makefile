# ============================
# ENVIRONMENT
# ============================
PYTHON=python3

# Activate your venv automatically if you want
VENV=.venv/bin
PIP=$(VENV)/pip
PY=$(VENV)/python

# ============================
# DATABASE TASKS
# ============================
db-shell:
# 	uv run duckdb local.duckdb

db-drop-metrics:
	uv run python scripts/delete_and_recreate_metric_tables.py

ingest-minute: 
	uv run python scripts/ingest_minute_data.py

# ============================
# DEVELOPMENT TASKS
# ============================
run-api:
# 	$(PY) api/main.py

run-frontend:
# 	cd frontend && npm run dev

main:
	uv run python main.py

dev:
	uv run python cli.py -d dev  

# ============================
# METRICS
# ============================
metrics-register:
	$(PY) scripts/register_all_metrics.py

metrics-run-daily:
	$(PY) scripts/calc_daily_metrics.py

# ============================
# UTILITIES
# ============================
format:
	$(PY) -m black src
	$(PY) -m isort src

# ============================
# SELF-DOCUMENTATION
# ============================
help:
	@grep -E '^[a-zA-Z_-]+:.*?## ' Makefile | sed 's/:.*## /: /'

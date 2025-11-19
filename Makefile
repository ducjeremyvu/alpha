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

run-backend:
	uv run python cli.py -d backend

run-frontend:
	uv run python cli.py -d frontend

main:
	uv run python main.py

dev:
	uv run python cli.py -d dev  

dev_cont_rp:
	uv run python dev_context_repl.py



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

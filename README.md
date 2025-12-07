
# Alpha / Edge Tools by Việt Đức Jeremy Vũ

i called the project alpha (to get trading alpha, still need to figure out what that even means)
but the package i write things with is called edge_tools for some reason.

## Update: using uv now, instead of pip

uv is a package manager and it let's me run things in a more stable environment. (I have fewer problems and it's dead simple), it feels quicker than running and manually altering virtual environments and dependencies (requirements.txt).

```
uv run python main.py
```

Above command will run the main project.

there is a package with functions, gotta create env and then install the package.

```
# create/activate your venv first
pip install -e ".[dev]"
python -m ipykernel install --user --name edge-env --display-name "Python (edge)"

```

## Startup

To make a working environment, I suggest your run the following commands

```
make db-create-table

```

This will create a duckdb database and tables that are used in this project.

You can the test ingest the example data into the duckdb database.

I would recommend setting up a dedicated folder where you place your csv files with price data. The csv files have to have a certain naming convention.
# TODO SHOW NAMING CONVENTION

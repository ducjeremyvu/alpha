# Initializing tables


Just run 

```
from edge_tools.db.migrations import load_all_tables
load_all_tables()
```

OUTPUT:

```
{...}
2025-11-16 18:07:40 DEBUG [edge_tools.db] Connecting to DuckDB at path: local.duckdb
2025-11-16 18:07:40 INFO [edge_tools.db.migrations] <_duckdb.DuckDBPyConnection object at 0x10cbadcb0>
2025-11-16 18:07:40 INFO [edge_tools.db.migrations] Finished running query *create_table_metrics*
```



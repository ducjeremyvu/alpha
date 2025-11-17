/*

Resources about primary key auto increment 

    https://duckdb.org/docs/stable/sql/statements/create_sequence#using-sequences-for-primary-keys
    https://github.com/duckdb/duckdb/discussions/18550

*/

CREATE SEQUENCE IF NOT EXISTS id_sequence_metrics START 1;

CREATE TABLE IF NOT EXISTS metrics (
    metric_id INTEGER PRIMARY KEY NOT NULL DEFAULT nextval('id_sequence_metrics'),
    metric_name TEXT UNIQUE NOT NULL,
    description TEXT NOT NULL,
    dataset TEXT NOT NULL,
    time_window TEXT,
    unit TEXT,
    category TEXT,
    added_at TIMESTAMPTZ DEFAULT (NOW() AT TIME ZONE 'UTC'),
    
);

CREATE TABLE IF NOT EXISTS metric_events (
    date DATE NOT NULL,
    symbol TEXT NOT NULL,
    metric_id INTEGER NOT NULL,
    metric_value DOUBLE,
    added_at TIMESTAMPTZ DEFAULT (NOW() AT TIME ZONE 'UTC'),
    FOREIGN KEY(metric_id) REFERENCES metrics(metric_id),
    PRIMARY KEY (date, symbol, metric_id)
);



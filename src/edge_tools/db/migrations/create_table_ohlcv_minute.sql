CREATE TABLE IF NOT EXISTS ohlcv_minute (
    symbol TEXT NOT NULL,
    time   TIMESTAMPTZ NOT NULL,
    open   DOUBLE,
    high   DOUBLE,
    low    DOUBLE,
    close  DOUBLE,
    volume BIGINT,
    added_at TIMESTAMPTZ DEFAULT (NOW() AT TIME ZONE 'UTC'),
    PRIMARY KEY (symbol, time)
);


CREATE TABLE IF NOT EXISTS ohlcv_hour (
    symbol TEXT NOT NULL,
    time   TIMESTAMPTZ NOT NULL,
    open   DOUBLE,
    high   DOUBLE,
    low    DOUBLE,
    close  DOUBLE,
    volume BIGINT,
    added_at TIMESTAMPTZ DEFAULT (NOW() AT TIME ZONE 'UTC'),
    PRIMARY KEY (symbol, time)
);


CREATE TABLE IF NOT EXISTS ohlcv_daily (
    symbol TEXT NOT NULL,
    time   TIMESTAMPTZ NOT NULL,
    open   DOUBLE,
    high   DOUBLE,
    low    DOUBLE,
    close  DOUBLE,
    volume BIGINT,
    added_at TIMESTAMPTZ DEFAULT (NOW() AT TIME ZONE 'UTC'),
    PRIMARY KEY (symbol, time)
);



CREATE TABLE IF NOT EXISTS ohlcv_weekly (
    symbol TEXT NOT NULL,
    time   TIMESTAMPTZ NOT NULL,
    open   DOUBLE,
    high   DOUBLE,
    low    DOUBLE,
    close  DOUBLE,
    volume BIGINT,
    added_at TIMESTAMPTZ DEFAULT (NOW() AT TIME ZONE 'UTC'),
    PRIMARY KEY (symbol, time)
);


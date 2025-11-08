CREATE TABLE ohlcv_minute (
    symbol TEXT NOT NULL,
    time   TIMESTAMPTZ NOT NULL,
    open   DOUBLE,
    high   DOUBLE,
    low    DOUBLE,
    close  DOUBLE,
    volume BIGINT,
    PRIMARY KEY (symbol, time)
);

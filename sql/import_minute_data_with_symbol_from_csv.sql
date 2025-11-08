
INSERT INTO ohlcv_minute (symbol, time, open, high, low, close, volume)
SELECT
    '{{symbol}}' AS symbol,  -- << your asset name here
    (CAST(Time AS TIMESTAMP) AT TIME ZONE 'UTC') AS time,
    CAST(Open AS DOUBLE) AS open,
    CAST(High AS DOUBLE) AS high,
    CAST(Low AS DOUBLE) AS low,
    CAST(Close AS DOUBLE) AS close,
    CAST(Volume AS BIGINT) AS volume
FROM read_csv_auto('{{file_path_csv}}')
ON CONFLICT (symbol, time) DO NOTHING;


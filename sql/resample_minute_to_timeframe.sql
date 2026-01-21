INSERT INTO {{target_table}} (symbol, time, open, high, low, close, volume)
SELECT
    symbol,
    bucket_time AS time,
    min_by(open, time) AS open,
    max(high) AS high,
    min(low) AS low,
    max_by(close, time) AS close,
    sum(volume) AS volume
FROM (
    SELECT
        symbol,
        time,
        {{bucket_expr}} AS bucket_time,
        open,
        high,
        low,
        close,
        volume
    FROM ohlcv_minute
    WHERE time >= '{{start_time}}'::TIMESTAMPTZ
      AND time < '{{end_time}}'::TIMESTAMPTZ
      {{extra_filter}}
) source
GROUP BY symbol, bucket_time
ON CONFLICT (symbol, time) DO UPDATE SET
    open = EXCLUDED.open,
    high = EXCLUDED.high,
    low = EXCLUDED.low,
    close = EXCLUDED.close,
    volume = EXCLUDED.volume;

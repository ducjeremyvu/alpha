SELECT time AT TIME ZONE 'America/New_York' AS ts_ny,
    symbol,
    open,
    high,
    low,
    close,
    volume
FROM ohlcv_minute
WHERE (
        time AT TIME ZONE 'America/New_York'
    )::time >= time '09:30'
    AND (
        time AT TIME ZONE 'America/New_York'
    )::time < time '10:00'
    AND symbol == 'US500'
order by ts_ny;
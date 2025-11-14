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
    )::time < time '16:00'
    AND symbol == 'US500'
    AND (
        time AT TIME ZONE 'America/New_York'
    )::date > '2025-11-01'
order by ts_ny;
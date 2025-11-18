SELECT time AT TIME ZONE 'America/New_York' AS ts_ny,
    symbol,
    open,
    high,
    low,
    close,
    volume
FROM ohlcv_minute
WHERE
    ts_ny >= (CAST((DATE('{{datestring}}') - INTERVAL '1 day') AS DATE)
              + TIME '09:30')
    AND
    ts_ny <  (CAST(DATE('{{datestring}}') AS DATE)
              + TIME '09:30')
    AND symbol = '{{symbol}}'
ORDER BY ts_ny;

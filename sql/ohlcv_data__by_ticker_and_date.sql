SELECT 
    symbol,     
    timezone('UTC',time) as time, 
    open,
    high,
    low,
    close,
    volume 
FROM ohlcv_minute 
WHERE timezone('UTC',time) >= '{{start_date}}' 
  AND timezone('UTC',time) <  '{{end_date}}'
  and symbol = '{{symbol}}'
order by time

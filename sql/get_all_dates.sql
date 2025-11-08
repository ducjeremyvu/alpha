select DISTINCT time::date as date
from ohlcv_minute
order by date desc
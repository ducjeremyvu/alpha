with first as (select date_trunc('day', time) as date, count (*)
from ohlcv_minute
group by date
order by date desc limit 5
    )

select * from ohlcv_minute limit 5

         



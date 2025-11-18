#########################################
#### Project Context replay dashboard ###
#########################################

"""
# Context Replay dashboard 
    - This gonna be a dashboard for my daily 30 min scalping 
    - I need data from previous day open to current day open. 
    - data_whole_day
    - Need to chop to different parts 
    - Resampled by m15
    - Resampled by h1   
    - Last 60 min. In m1 
    - premarket: prev close to cur day open in hours 

values: 
    - Prev day: requires previous day data 
	    - ohlc 
	    - change and percentage change 
    - Premarket volatility 

optional:
	- values for different times 

"""


"""
First Step: create query the data given the day 

input date > query > data

"""

from pandas import DataFrame
from edge_tools.utils.dir import get_sql_query
from edge_tools.db import get_duckdb_connection

# starting this script, functions are always written, taking a con object. 


def run_query(con, query_name, **params) -> DataFrame:
    pass



def main() -> None:
    pass


if __name__=='__main__':
    main()
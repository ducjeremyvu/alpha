import pandas as pd
from edge_tools.ohlcv import require_columns

def split_us_market_hours(df, market_open=True):
    require_columns(df, ["time"])  # Check for 'time' column
    
    # Convert 'Time' to datetime and set as index
    df['time'] = pd.to_datetime(df['time'])
    df = df.set_index('time')
    df.index = df.index.tz_localize("UTC")
    df['ny_time'] = df.index.tz_convert("America/New_York")
    df['ny_hour'] = df['ny_time'].dt.hour
    df['ny_minute'] = df['ny_time'].dt.minute
    df['ny_time_only'] = df['ny_time'].dt.time

    open_time = pd.to_datetime("09:30").time()
    close_time = pd.to_datetime("16:00").time()
    df['is_us_market_open'] = df['ny_time_only'].between(open_time, close_time)

    if market_open:
        return df[df['is_us_market_open']]
    else:
        return df[~df['is_us_market_open']]

# Example usage:
# data_us_open = split_us_market_hours(data, market_open=True)
# data_us_closed = split_us_market_hours(data, market_open=False)
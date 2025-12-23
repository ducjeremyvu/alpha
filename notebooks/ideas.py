# Convert Time to UTC and create NY time column
import pandas as pd


def add_timezones(df, time_col="Time"):
    df = df.copy()
    df[time_col] = pd.to_datetime(df[time_col], utc=True)
    df["Time_NY"] = df[time_col].dt.tz_convert("America/New_York")
    return df

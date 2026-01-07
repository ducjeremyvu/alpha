from __future__ import annotations

import pandas as pd


def slice_cash_session(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()
    data["time"] = pd.to_datetime(data["time"], utc=True)
    data["time_ny"] = data["time"].dt.tz_convert("America/New_York")
    data["session_date"] = data["time_ny"].dt.date
    data["time_ny_only"] = data["time_ny"].dt.time

    start = pd.Timestamp("09:30").time()
    end = pd.Timestamp("12:00").time()
    sliced = data[(data["time_ny_only"] >= start) & (data["time_ny_only"] < end)].copy()

    sliced["bar_index_in_session"] = (
        sliced.groupby("session_date").cumcount()
    )
    sliced["minutes_from_open"] = sliced["bar_index_in_session"] * 5
    return sliced

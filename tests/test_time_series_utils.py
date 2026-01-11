import pandas as pd

from edge_tools.time_series import (
    add_ny_columns,
    convert_index_to_utc,
    preprocess_for_premarket_analysis,
)
from edge_tools.time_series.premarket import filter_today_first_30_minutes


def test_convert_index_to_utc_localizes_naive_times():
    frame = pd.DataFrame({"time": ["2024-01-02 14:00", "2024-01-02 14:05"], "open": [1, 2]})
    converted = convert_index_to_utc(frame)

    assert converted.index.tz is not None
    assert str(converted.index.tz) == "UTC"


def test_add_ny_columns_after_utc_index():
    frame = pd.DataFrame({"time": ["2024-01-02 14:00", "2024-01-02 14:05"], "open": [1, 2]})
    converted = convert_index_to_utc(frame)
    with_ny = add_ny_columns(converted)

    assert "ny_time" in with_ny.columns
    assert "ny_time_only" in with_ny.columns


def test_filter_today_first_30_minutes():
    times = pd.date_range("2024-01-03 14:30", periods=10, freq="5min", tz="UTC")
    frame = pd.DataFrame(
        {
            "time": times,
            "open": [1] * 10,
            "high": [1] * 10,
            "low": [1] * 10,
            "close": [1] * 10,
            "volume": [1] * 10,
        }
    )
    prepared = preprocess_for_premarket_analysis(frame)
    filtered = filter_today_first_30_minutes(prepared)

    assert not filtered.empty
    assert filtered["ny_time_only"].min() >= pd.to_datetime("09:30").time()
    assert filtered["ny_time_only"].max() <= pd.to_datetime("10:00").time()

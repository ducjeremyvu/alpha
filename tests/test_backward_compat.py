from edge_tools import database, date, ohlcv, open as open_module, premarket, time, us_open


def test_backward_compat_exports():
    assert hasattr(ohlcv, "normalize_ohlcv")
    assert hasattr(date, "to_datetime")
    assert hasattr(us_open, "split_us_market_hours")
    assert hasattr(time, "convert_index_to_utc")
    assert hasattr(premarket, "premarket_data")
    assert hasattr(open_module, "ny_open_30_minute_by_date")
    assert hasattr(database, "insert_minute_file_data")

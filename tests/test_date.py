import pytest
from datetime import datetime, date
from edge_tools.date import to_datetime  # adjust import to your module


def test_datetime_input_passes_through():
    dt = datetime(2025, 1, 1, 12, 0, 0)
    assert to_datetime(dt) == dt


def test_date_input_becomes_datetime_midnight():
    d = date(2025, 1, 1)
    result = to_datetime(d)
    assert isinstance(result, datetime)
    assert result.year == 2025
    assert result.month == 1
    assert result.day == 1
    assert result.hour == 0
    assert result.minute == 0


def test_string_iso_date():
    result = to_datetime("2025-11-05")
    assert result.year == 2025
    assert result.month == 11
    assert result.day == 5


def test_string_with_time_and_timezone():
    result = to_datetime("2025-11-05 14:22:10+01:00")
    assert result.tzinfo is not None


def test_string_without_timezone_assigns_assume_tz():
    result = to_datetime("2025-11-05 14:22:10")
    assert str(result.tzinfo) == "UTC"


def test_unix_timestamp_seconds():
    ts = 1730780400  # example timestamp
    result = to_datetime(ts)
    assert isinstance(result, datetime)


def test_unix_timestamp_milliseconds():
    ts_ms = 1730780400000  # example timestamp in ms
    result = to_datetime(ts_ms)
    assert isinstance(result, datetime)


def test_invalid_type_raises():
    with pytest.raises(TypeError):
        to_datetime(object())

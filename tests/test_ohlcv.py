import pandas as pd
from edge_tools.time_series.ohlcv import normalize_ohlcv


def test_normalize_capitalized():
    df = pd.DataFrame(
        {
            "time": ["2025-08-21 09:30"],
            "open": [1],
            "high": [2],
            "low": [0],
            "close": [1.5],
            "volume": [100],
        }
    )
    out = normalize_ohlcv(df, style="capitalized")
    assert list(out.columns) == ["Time", "Open", "High", "Low", "Close", "Volume"]

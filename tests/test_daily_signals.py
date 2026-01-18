import pandas as pd

from edge_tools.research.daily_signals import build_signal_dataset


def test_build_signal_dataset_forward_returns():
    data = pd.DataFrame(
        {
            "time": pd.date_range("2024-01-01", periods=7, freq="D", tz="UTC"),
            "open": [100, 102, 104, 103, 105, 106, 107],
            "high": [103, 105, 106, 104, 107, 108, 109],
            "low": [99, 101, 103, 102, 104, 105, 106],
            "close": [102, 104, 103, 105, 106, 107, 108],
            "volume": [10, 10, 10, 10, 10, 10, 10],
        }
    )

    signal = build_signal_dataset(data, forward_horizons=(1, 3))

    assert not signal.empty
    assert "fwd_return_1" in signal.columns
    assert "fwd_return_3" in signal.columns
    assert (signal["next_candle_type"].notna()).all()
    assert (signal[["fwd_return_1", "fwd_return_3"]].notna().all(axis=1)).all()

    first_row = signal.iloc[0]
    expected_return_1 = (data.loc[2, "close"] - data.loc[1, "close"]) / data.loc[1, "close"]
    expected_return_3 = (data.loc[4, "close"] - data.loc[1, "close"]) / data.loc[1, "close"]
    assert first_row["fwd_return_1"] == expected_return_1
    assert first_row["fwd_return_3"] == expected_return_3

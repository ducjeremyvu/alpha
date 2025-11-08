import pandas as pd
from edge_tools.us_open import split_us_market_hours

def test_split_us_market_hours():
    # Create sample data
    df = pd.DataFrame({
        'time': [
            '2024-08-21 13:30:00',  # 09:30 NY time (market open)
            '2024-08-21 20:00:00',  # 16:00 NY time (market open)
            '2024-08-21 10:00:00',  # 06:00 NY time (market closed)
        ],
        'open': [1, 2, 3],
        'high': [2, 3, 4],
        'low': [0, 1, 2],
        'close': [1.5, 2.5, 3.5],
        'volume': [100, 200, 300]
    })

    # Test market open
    open_df = split_us_market_hours(df, market_open=True)
    assert len(open_df) == 2
    assert all(open_df['ny_hour'].isin([9, 16]))

    # Test market closed
    closed_df = split_us_market_hours(df, market_open=False)
    assert len(closed_df) == 1
    assert all(closed_df['ny_hour'] == 6)
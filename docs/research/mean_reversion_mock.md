# Mean Reversion Mockup (US500 M5)

This mockup script loads US500 5-minute candle data, slices the cash session
(09:30–12:00 ET), builds session-level features, and generates simple
mean-reversion signals. It then reports 3/6-bar forward returns and saves the
signal table for further analysis.

## Inputs

- CSV with columns: `time`, `open`, `high`, `low`, `close`, `volume`
- Timestamps can be UTC or timezone-naive (assumed UTC)

## What It Computes

- Session slicing: 09:30–12:00 ET (`slice_cash_session`)
- Feature set: rolling ranges, volatility proxies, and session stats
- Mean-reversion signals: price distance from session open exceeding a
  multiple of the rolling range mean
- Forward returns: 3- and 6-bar ahead returns, directionally adjusted

## Usage

```bash
uv run python scripts/experiments/mean_reversion_mock.py price_data/your_us500.csv \
  --forward-bars 3 6 \
  --distance-mult 1.5
```

Outputs:

- Console summary for data health and forward returns
- CSV written to `outputs/mean_reversion_signals.csv` (configurable via
  `--output`)

## Next Steps

- Add walk-forward splits (train/validate/test by date)
- Add context filters (e.g., early trend, volatility regime)
- Compare alternative thresholds and holding windows

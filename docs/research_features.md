# Research Feature Set

This describes the feature engineering logic used in
`src/edge_tools/research/features.py`.

## Per-Candle Features

- `return_pct`: percent return from prior close, computed within each session.
- `return_log`: log return per candle, useful for volatility modeling.
- `range`: `high - low`, captures intrabar volatility.
- `body`: absolute `close - open`, measures directional body size.
- `close_open`: signed `close - open`, directional move per candle.
- `upper_wick`: `high - max(open, close)`, measures upside rejection.
- `lower_wick`: `min(open, close) - low`, measures downside rejection.
- `position_in_range`: close location within bar range, normalized to `[0, 1]`.

## Session-Rolling Features

Computed with a rolling 12-bar window (min 5 bars), grouped by session.

- `rolling_vol`: rolling std of `return_pct`, local volatility.
- `rolling_range_mean`: rolling mean of `range`, normal movement baseline.
- `impulse`: `abs(return_pct) / rolling_vol`, strength vs. local vol.
- `compression`: `range / rolling_range_mean`, tight vs. expanded bars.
- `direction`: +1 if close >= open else -1.
- `direction_streak`: consecutive same-direction count within a session.

## Session Summary Features (09:30–12:00 ET)

Aggregated per session after slicing the cash window.

- `open_0930`: first open of the session window.
- `close_1200`: last close of the session window.
- `high_0930_1200`: session high.
- `low_0930_1200`: session low.
- `volume_sum`: total volume in the window.
- `total_movement`: sum of absolute candle bodies.
- `realized_vol`: std of `return_pct` in the window.
- `range_0930_1200`: session high-low range.
- `net_move`: `close_1200 - open_0930`, directional change.
- `efficiency_ratio`: `abs(net_move) / total_movement` (trendiness vs. chop).
- `mfe_from_open`: max favorable excursion from open.
- `mae_from_open`: max adverse excursion from open.

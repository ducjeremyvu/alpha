# US500 Intraday Research Report

## Data Health
- **rows**: 72411
- **columns**: ['time', 'open', 'high', 'low', 'close', 'volume']
- **start**: 2024-12-25 23:00:00+00:00
- **end**: 2026-01-07 13:15:00+00:00
- **duplicates**: 0
- **missing_intervals**: 277
- **missing_interval_minutes**: 183070.0
- **null_counts**: {'time': 0, 'open': 0, 'high': 0, 'low': 0, 'close': 0, 'volume': 0}
- **day_of_week_distribution**: {'Tuesday': 14846, 'Monday': 14690, 'Wednesday': 14420, 'Thursday': 14099, 'Friday': 13300, 'Sunday': 1056}
- **timezone_note**: Naive timestamps assumed UTC

## Feature Summary
- **rows**: 7920
- **sessions**: 264
- **columns**: ['time', 'open', 'high', 'low', 'close', 'volume', 'time_ny', 'session_date', 'time_ny_only', 'bar_index_in_session', 'minutes_from_open', 'return_pct', 'return_log', 'range', 'body', 'close_open', 'upper_wick', 'lower_wick', 'position_in_range', 'rolling_vol', 'rolling_range_mean', 'impulse', 'compression', 'direction', 'direction_streak', 'open_0930', 'close_1200', 'high_0930_1200', 'low_0930_1200', 'volume_sum', 'total_movement', 'realized_vol', 'range_0930_1200', 'net_move', 'efficiency_ratio', 'mfe_from_open', 'mae_from_open']

## Regime Distribution
- **daily_trend**: {'balance': 145, 'trend_up': 64, 'trend_down': 55}
- **vol_regime**: {'low': 88, 'mid': 88, 'high': 88}
- **hourly_trend**: {'trend': 104, 'mixed': 100, 'balance': 60}
- **context_label**: {'balance_mixed': 67, 'balance_balance': 52, 'trend_up_trend': 44, 'trend_down_trend': 34, 'balance_trend': 26, 'trend_down_mixed': 18, 'trend_up_mixed': 15, 'trend_up_balance': 5, 'trend_down_balance': 3}

## Pattern Library Summary
- **total_signals**: 1104
- **patterns**: {'failed_breakout': {'count': 484, 'avg_fwd_1': -0.047520661157021034, 'avg_fwd_3': 0.659504132231414, 'avg_fwd_6': 0.05909090909090984, 'avg_mae': 7.28966942148762, 'avg_mfe': 7.994628099173534, 'contexts': {'balance_mixed': 159, 'balance_balance': 84, 'balance_trend': 65, 'trend_up_trend': 62, 'trend_down_trend': 53, 'trend_down_mixed': 34, 'trend_up_mixed': 20, 'trend_up_balance': 5, 'trend_down_balance': 2}}, 'mean_reversion_open': {'count': 177, 'avg_fwd_1': -0.5105263157894429, 'avg_fwd_3': -0.26608187134498135, 'avg_fwd_6': -2.376608187134485, 'avg_mae': 11.401169590643256, 'avg_mfe': 9.304678362573117, 'contexts': {'balance_mixed': 78, 'balance_balance': 50, 'trend_up_trend': 15, 'balance_trend': 12, 'trend_down_trend': 7, 'trend_up_balance': 5, 'trend_down_mixed': 4, 'trend_down_balance': 4, 'trend_up_mixed': 2}}, 'opening_drive': {'count': 32, 'avg_fwd_1': 1.5250000000000625, 'avg_fwd_3': 0.790625000000091, 'avg_fwd_6': 2.190625000000068, 'avg_mae': 8.909374999999898, 'avg_mfe': 12.359375000000085, 'contexts': {'trend_up_trend': 8, 'balance_mixed': 7, 'trend_down_trend': 7, 'balance_trend': 4, 'balance_balance': 3, 'trend_up_mixed': 2, 'trend_down_mixed': 1}}, 'spike_fade': {'count': 8, 'avg_fwd_1': -3.0, 'avg_fwd_3': -0.625, 'avg_fwd_6': -5.8125, 'avg_mae': 20.962499999999977, 'avg_mfe': 15.325000000000045, 'contexts': {'balance_balance': 4, 'balance_mixed': 2, 'trend_up_mixed': 1, 'trend_down_balance': 1}}, 'sweep_proxy': {'count': 97, 'avg_fwd_1': -0.49565217391303756, 'avg_fwd_3': -0.31086956521738535, 'avg_fwd_6': 0.051086956521737156, 'avg_mae': 8.076086956521738, 'avg_mfe': 8.147826086956506, 'contexts': {'balance_mixed': 33, 'balance_balance': 17, 'trend_down_trend': 13, 'balance_trend': 12, 'trend_up_trend': 10, 'trend_up_mixed': 6, 'trend_down_mixed': 6}}, 'two_leg_trend': {'count': 306, 'avg_fwd_1': 0.22199999999999515, 'avg_fwd_3': -1.0379999999999958, 'avg_fwd_6': -0.35100000000002185, 'avg_mae': 8.899666666666684, 'avg_mfe': 8.136999999999986, 'contexts': {'trend_up_trend': 67, 'balance_mixed': 64, 'balance_balance': 59, 'trend_down_trend': 43, 'balance_trend': 31, 'trend_up_mixed': 19, 'trend_down_mixed': 14, 'trend_up_balance': 6, 'trend_down_balance': 3}}}

## Backtest Summary
- **trades**: 70
- **win_rate**: 0.4857142857142857
- **expectancy**: 0.9390542156257782
- **profit_factor**: 1.2576652311118512
- **max_drawdown**: -47.71746031745897
- **by_split**: {'test': {'trades': 14, 'win_rate': 0.42857142857142855, 'expectancy': 2.120588538445645, 'profit_factor': 1.5406834114068209}, 'train': {'trades': 41, 'win_rate': 0.5121951219512195, 'expectancy': 0.6803987611306739, 'profit_factor': 1.1867388204493454}, 'validate': {'trades': 15, 'win_rate': 0.4666666666666667, 'expectancy': 0.5432804232805211, 'profit_factor': 1.1603623301577677}}
- **by_context**: {'balance_trend': {'trades': 41, 'win_rate': 0.5121951219512195, 'expectancy': 1.0642547425475908, 'profit_factor': 1.266417464926368}, 'trend_up_balance': {'trades': 7, 'win_rate': 0.42857142857142855, 'expectancy': 1.0952380952380085, 'profit_factor': 1.2273850716757078}, 'trend_up_mixed': {'trades': 22, 'win_rate': 0.45454545454545453, 'expectancy': 0.6560310901221452, 'profit_factor': 1.2505053009640796}}
- **context_filter**: ['balance_trend', 'trend_up_balance', 'trend_up_mixed']

## Sensitivity Checks
- **base_expectancy**: 0.9390542156257782
- **tight_stop_expectancy**: 1.2145519686663386
- **wide_stop_expectancy**: 0.6950555349414441

## Next Steps
- Review top patterns with strongest context dependence.
- Validate execution assumptions on live charts.
- Iterate on regime filters and re-run sensitivity sweeps.
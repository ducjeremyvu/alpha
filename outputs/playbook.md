# US500 Intraday Playbook

## Spike + Fade

**Visual:** Early impulse quickly fades back toward the session open.
**Context Filter:** Trade only in `trend_up_mixed`; avoid `trend_up_mixed`.
**Entry Trigger:** Impulse > 2.0 then close returns within 25% of early range.
**Stop:** 1.0–1.5x rolling range mean behind structure.
**Target:** 2R or exit by 12:00 ET.
**Time Rules:** No new entries after 11:30 ET; flat by 12:00 ET.
**Risk:** 0.5–1R per trade, 2R max daily loss.
**Test Stats:** Win rate 100.00%, expectancy 12.96
**Don’t Trade If:** Context is mixed/unknown or volatility regime is extreme.

## Failed Breakout

**Visual:** Breaks early range then closes back inside within 2 bars.
**Context Filter:** Trade only in `trend_up_balance`; avoid `trend_up_mixed`.
**Entry Trigger:** Break above/below first-hour range then close back inside.
**Stop:** 1.0–1.5x rolling range mean behind structure.
**Target:** 2R or exit by 12:00 ET.
**Time Rules:** No new entries after 11:30 ET; flat by 12:00 ET.
**Risk:** 0.5–1R per trade, 2R max daily loss.
**Test Stats:** Win rate 56.00%, expectancy 3.32
**Don’t Trade If:** Context is mixed/unknown or volatility regime is extreme.

## Two-Leg Trend

**Visual:** Push, shallow pullback, and continuation in same direction.
**Context Filter:** Trade only in `balance_trend`; avoid `trend_up_balance`.
**Entry Trigger:** Leg1 return > 1.0 * rolling vol, pullback < 40% of leg1.
**Stop:** 1.0–1.5x rolling range mean behind structure.
**Target:** 2R or exit by 12:00 ET.
**Time Rules:** No new entries after 11:30 ET; flat by 12:00 ET.
**Risk:** 0.5–1R per trade, 2R max daily loss.
**Test Stats:** Win rate 54.55%, expectancy 1.67
**Don’t Trade If:** Context is mixed/unknown or volatility regime is extreme.

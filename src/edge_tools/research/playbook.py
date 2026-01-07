from __future__ import annotations

from typing import Iterable

import pandas as pd

from edge_tools.research.patterns import PATTERN_DEFINITIONS


def write_playbook(trades: pd.DataFrame, path: str, top_n: int = 3) -> None:
    lines = ["# US500 Intraday Playbook", ""]
    if trades.empty:
        lines.append("No strategies qualified for the playbook yet.")
        _write(path, lines)
        return

    ranked = _rank_patterns(trades)
    for pattern in ranked[:top_n]:
        definition = PATTERN_DEFINITIONS.get(pattern)
        lines.extend(_format_pattern_section(pattern, definition, trades))
    _write(path, lines)


def _rank_patterns(trades: pd.DataFrame) -> list[str]:
    test = trades[trades["split"] == "test"]
    if test.empty:
        test = trades
    ranked = (
        test.groupby("pattern")["pnl"].mean().sort_values(ascending=False).index.tolist()
    )
    return ranked


def _format_pattern_section(
    pattern: str,
    definition,
    trades: pd.DataFrame,
) -> list[str]:
    pattern_trades = trades[trades["pattern"] == pattern]
    best_context = _best_context(pattern_trades)
    worst_context = _worst_context(pattern_trades)
    stats = _summary_stats(pattern_trades)

    name = definition.name if definition else pattern.replace("_", " ").title()
    description = definition.description if definition else ""
    rules = definition.rules if definition else ""

    return [
        f"## {name}",
        "",
        f"**Visual:** {description}",
        f"**Context Filter:** Trade only in `{best_context}`; avoid `{worst_context}`.",
        f"**Entry Trigger:** {rules}",
        "**Stop:** 1.0–1.5x rolling range mean behind structure.",
        "**Target:** 2R or exit by 12:00 ET.",
        "**Time Rules:** No new entries after 11:30 ET; flat by 12:00 ET.",
        "**Risk:** 0.5–1R per trade, 2R max daily loss.",
        f"**Test Stats:** {stats}",
        "**Don’t Trade If:** Context is mixed/unknown or volatility regime is extreme.",
        "",
    ]


def _best_context(trades: pd.DataFrame) -> str:
    if trades.empty or trades["context_label"].isna().all():
        return "unknown"
    return trades.groupby("context_label")["pnl"].mean().idxmax()


def _worst_context(trades: pd.DataFrame) -> str:
    if trades.empty or trades["context_label"].isna().all():
        return "unknown"
    return trades.groupby("context_label")["pnl"].mean().idxmin()


def _summary_stats(trades: pd.DataFrame) -> str:
    if trades.empty:
        return "No trades."
    win_rate = (trades["pnl"] > 0).mean()
    expectancy = trades["pnl"].mean()
    return f"Win rate {win_rate:.2%}, expectancy {expectancy:.2f}"


def _write(path: str, lines: Iterable[str]) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))

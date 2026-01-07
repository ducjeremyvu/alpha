from __future__ import annotations

from typing import Iterable


def write_report(
    path: str,
    data_health: dict,
    feature_summary: dict,
    regime_summary: dict,
    pattern_summary: dict,
    backtest_summary: dict,
    sensitivity_summary: dict,
) -> None:
    lines = [
        "# US500 Intraday Research Report",
        "",
        "## Data Health",
        _format_kv(data_health),
        "",
        "## Feature Summary",
        _format_kv(feature_summary),
        "",
        "## Regime Distribution",
        _format_kv(regime_summary),
        "",
        "## Pattern Library Summary",
        _format_kv(pattern_summary),
        "",
        "## Backtest Summary",
        _format_kv(backtest_summary),
        "",
        "## Sensitivity Checks",
        _format_kv(sensitivity_summary),
        "",
        "## Next Steps",
        "- Review top patterns with strongest context dependence.",
        "- Validate execution assumptions on live charts.",
        "- Iterate on regime filters and re-run sensitivity sweeps.",
    ]
    _write(path, lines)


def _format_kv(payload: dict) -> str:
    if not payload:
        return "No data available."
    lines = []
    for key, value in payload.items():
        lines.append(f"- **{key}**: {value}")
    return "\n".join(lines)


def _write(path: str, lines: Iterable[str]) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))

from __future__ import annotations

from pathlib import Path

import pandas as pd

from edge_tools.research.backtest import backtest_patterns, summarize_backtest
from edge_tools.research.features import build_feature_set
from edge_tools.research.load_data import load_us500_data, summarize_data_health
from edge_tools.research.patterns import build_pattern_candidates, write_pattern_candidates
from edge_tools.research.playbook import write_playbook
from edge_tools.research.regimes import build_context_labels
from edge_tools.research.report import write_report
from edge_tools.research.slice_session import slice_cash_session


def main() -> None:
    output_dir = Path("outputs")
    output_dir.mkdir(parents=True, exist_ok=True)

    data = load_us500_data("data/raw/us500/US500_Minute5_20260107_1319.csv")
    data_health = summarize_data_health(data)
    print("Data Health Summary:")
    for key, value in data_health.items():
        print(f"- {key}: {value}")

    sliced = slice_cash_session(data)
    sliced.to_parquet(output_dir / "data_sliced.parquet", index=False)

    features = build_feature_set(sliced)
    features.to_parquet(output_dir / "features.parquet", index=False)
    daily_summary = features.groupby("session_date", as_index=False).first()
    daily_summary.to_parquet(output_dir / "daily_summary.parquet", index=False)

    context, resampled, daily_context, hourly_context = build_context_labels(features)
    context.to_parquet(output_dir / "regime_labels.parquet", index=False)
    resampled["1h"].to_parquet(output_dir / "data_1h.parquet", index=False)
    resampled["1d"].to_parquet(output_dir / "data_1d.parquet", index=False)
    daily_context.to_parquet(output_dir / "daily_context.parquet", index=False)
    hourly_context.to_parquet(output_dir / "hourly_context.parquet", index=False)

    pattern_signals, pattern_summary = build_pattern_candidates(features, context)
    write_pattern_candidates(pattern_summary, output_dir / "pattern_candidates.json")

    context_allowlist = {"trend_up_balance", "balance_trend", "trend_up_mixed"}
    filtered_signals = pattern_signals[
        pattern_signals["context_label"].isin(context_allowlist)
    ].copy()

    trades = backtest_patterns(features, filtered_signals)
    trades.to_parquet(output_dir / "backtest_results.parquet", index=False)
    backtest_summary = summarize_backtest(trades)
    backtest_summary["context_filter"] = sorted(context_allowlist)

    sensitivity_summary = _sensitivity(features, filtered_signals)
    write_playbook(trades, output_dir / "playbook.md")

    regime_summary = _regime_summary(context)
    feature_summary = {
        "rows": int(len(features)),
        "sessions": int(features["session_date"].nunique()),
        "columns": list(features.columns),
    }

    write_report(
        output_dir / "report.md",
        data_health=data_health,
        feature_summary=feature_summary,
        regime_summary=regime_summary,
        pattern_summary=pattern_summary,
        backtest_summary=backtest_summary,
        sensitivity_summary=sensitivity_summary,
    )


def _regime_summary(context: pd.DataFrame) -> dict:
    return {
        "daily_trend": context["daily_trend"].value_counts().to_dict(),
        "vol_regime": context["vol_regime"].value_counts().to_dict(),
        "hourly_trend": context["hourly_trend"].value_counts().to_dict(),
        "context_label": context["context_label"].value_counts().to_dict(),
    }


def _sensitivity(features: pd.DataFrame, signals: pd.DataFrame) -> dict:
    if signals.empty:
        return {"note": "No signals to test."}
    base = summarize_backtest(backtest_patterns(features, signals))
    tight = summarize_backtest(backtest_patterns(features, signals, stop_multiplier=0.8))
    wide = summarize_backtest(backtest_patterns(features, signals, stop_multiplier=1.2))
    return {
        "base_expectancy": base.get("expectancy"),
        "tight_stop_expectancy": tight.get("expectancy"),
        "wide_stop_expectancy": wide.get("expectancy"),
    }


if __name__ == "__main__":
    main()

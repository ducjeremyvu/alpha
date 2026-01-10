from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from edge_tools.research.features import build_feature_set
from edge_tools.research.load_data import load_us500_data, summarize_data_health
from edge_tools.research.slice_session import slice_cash_session


def build_mean_reversion_signals(
    data: pd.DataFrame,
    distance_mult: float = 1.5,
    min_bars: int = 2,
    forward_bars: tuple[int, ...] = (3, 6),
) -> pd.DataFrame:
    data = data.copy()
    data = data.sort_values(["session_date", "time_ny"]).reset_index(drop=True)
    data["bar_id"] = data.groupby("session_date").cumcount()
    for bars in forward_bars:
        data[f"fwd_{bars}"] = data.groupby("session_date")["close"].shift(-bars) - data["close"]

    signals = []
    for session_date, group in data.groupby("session_date", sort=True):
        session_open = group["open"].iloc[0]
        for _, row in group.iterrows():
            if row["bar_id"] < min_bars:
                continue
            distance = row["close"] - session_open
            threshold = distance_mult * row["rolling_range_mean"]
            if threshold == 0 or pd.isna(threshold):
                continue
            if abs(distance) > threshold:
                direction = -1 if distance > 0 else 1
                signals.append(
                    {
                        "session_date": session_date,
                        "time_ny": row["time_ny"],
                        "bar_id": row["bar_id"],
                        "distance": distance,
                        "direction": direction,
                        "entry_price": row["close"],
                    }
                )

    signals_df = pd.DataFrame(signals)
    if signals_df.empty:
        return signals_df

    fwd_cols = [f"fwd_{bars}" for bars in forward_bars]
    signals_df = signals_df.merge(
        data[["session_date", "bar_id", *fwd_cols]],
        on=["session_date", "bar_id"],
        how="left",
    )
    for bars in forward_bars:
        col = f"fwd_{bars}"
        signals_df[col] = signals_df[col] * signals_df["direction"]
    return signals_df


def summarize_forward_returns(signals: pd.DataFrame, forward_bars: tuple[int, ...]) -> dict:
    summary = {}
    for bars in forward_bars:
        col = f"fwd_{bars}"
        if col not in signals:
            continue
        summary[col] = signals[col].describe(
            percentiles=[0.1, 0.25, 0.5, 0.75, 0.9]
        ).to_dict()
    return summary


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mean reversion mockup for US500 M5 data")
    parser.add_argument("csv_path", help="CSV with time, open, high, low, close, volume")
    parser.add_argument("--distance-mult", type=float, default=1.5)
    parser.add_argument("--forward-bars", type=int, nargs="+", default=[3, 6])
    parser.add_argument("--output", default="outputs/mean_reversion_signals.csv")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    forward_bars = tuple(args.forward_bars)

    data = load_us500_data(args.csv_path)
    sliced = slice_cash_session(data)
    features = build_feature_set(sliced)

    health = summarize_data_health(features)
    print("Data health:", health)

    signals = build_mean_reversion_signals(
        features,
        distance_mult=args.distance_mult,
        forward_bars=forward_bars,
    )
    print(f"Signals: {len(signals)}")
    if signals.empty:
        return

    summary = summarize_forward_returns(signals, forward_bars)
    print("Forward return summary:", summary)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    signals.to_csv(output_path, index=False)
    print(f"Saved signals to {output_path}")


if __name__ == "__main__":
    main()

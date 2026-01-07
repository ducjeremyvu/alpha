from __future__ import annotations

import argparse
from pathlib import Path

from edge_tools.analytics.us500.first_window import (
    compute_first_window_features,
    filter_first_window,
    load_us500_csvs,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compute US500 09:30-12:00 ET features from UTC 5-min bars."
    )
    parser.add_argument(
        "--input",
        default="data/raw/us500/*.csv",
        help="CSV path or glob for US500 data.",
    )
    parser.add_argument(
        "--output",
        default="data/processed/us500/us500_first_150_features.csv",
        help="Output CSV path for per-day features.",
    )
    args = parser.parse_args()

    data = load_us500_csvs(args.input)
    window = filter_first_window(data)
    features = compute_first_window_features(window)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    features.to_csv(output_path, index=False)

    print(f"Saved {len(features)} rows to {output_path}")


if __name__ == "__main__":
    main()

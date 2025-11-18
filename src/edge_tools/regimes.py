import pandas as pd
import numpy as np
import pandas_ta as ta


def classify_regimes(
    df_daily: pd.DataFrame,
    atr_len: int = 14,
    roll_quant_window: int = 252,  # rolling window for adaptive quantiles
    vol_quantiles=(0.33, 0.67),  # splits ATR% into Low/Mid/High
    dmr_trend_thresh: float = 0.6,  # ≥ trend, ≤ range; 0.3–0.6 is "mixed"
    rvol_len: int = 20,
    session_col: str | None = None,  # optional: pass a column like 'US'/'EU' if present
):
    """
    Input df_daily must have columns: ['open','high','low','close','volume'] indexed by date (or with a date column).
    Returns df with added columns:
    ['ATR','ATR_pct','DMR','CLV','RVOL','Gap_pct','VolBucket','TrendDir','Trendiness','Regime'].
    """

    df = df_daily.copy()

    # --- Core features ---
    df["ATR"] = ta.atr(df["high"], df["low"], df["close"], length=atr_len)
    with np.errstate(divide="ignore", invalid="ignore"):
        df["ATR_pct"] = (df["ATR"] / df["close"]) * 100.0

    # True range denominator; guard zeros
    rng = (df["high"] - df["low"]).replace(0, np.nan)

    # Directional Move Ratio (trendiness)
    df["DMR"] = (df["close"] - df["open"]).abs() / rng

    # Close Location Value (directional finishing position)
    df["CLV"] = (df["close"] - df["low"]) / rng

    # Relative Volume (vs n‑day avg)
    df["RVOL"] = (
        df["volume"]
        / df["volume"].rolling(rvol_len, min_periods=max(5, rvol_len // 2)).mean()
    )

    # Gap vs prior close
    df["Gap_pct"] = (df["open"] - df["close"].shift(1)) / df["close"].shift(1) * 100.0

    # --- Rolling adaptive ATR% quantiles ---
    q_lo = (
        df["ATR_pct"]
        .rolling(roll_quant_window, min_periods=max(20, atr_len))
        .quantile(vol_quantiles[0])
    )
    q_hi = (
        df["ATR_pct"]
        .rolling(roll_quant_window, min_periods=max(20, atr_len))
        .quantile(vol_quantiles[1])
    )

    def vol_bucket(v, lo, hi):
        if pd.isna(v) or pd.isna(lo) or pd.isna(hi):
            return np.nan
        if v <= lo:
            return "LowVol"
        if v >= hi:
            return "HighVol"
        return "MidVol"

    df["VolBucket"] = [
        vol_bucket(v, lo, hi) for v, lo, hi in zip(df["ATR_pct"], q_lo, q_hi)
    ]

    # --- Trend direction bucket from CLV ---
    def trend_dir(clv):
        if np.isnan(clv):
            return np.nan
        if clv >= 2 / 3:
            return "TrendUp"
        if clv <= 1 / 3:
            return "TrendDown"
        return "Balanced"

    df["TrendDir"] = df["CLV"].apply(trend_dir)

    # --- Trendiness from DMR ---
    lo_thresh = 1 - dmr_trend_thresh

    def trendiness(dmr):
        if np.isnan(dmr):
            return "Unknown"
        if dmr >= dmr_trend_thresh:
            return "Trend"
        if dmr <= lo_thresh:
            return "Range"
        return "Mixed"

    df["Trendiness"] = df["DMR"].apply(trendiness)

    # --- Final regime label ---
    def label_row(row):
        vol = row["VolBucket"]
        if pd.isna(vol):
            return np.nan
        if row["Trendiness"] == "Trend":
            core = (
                row["TrendDir"]
                if row["TrendDir"] in ("TrendUp", "TrendDown")
                else "Trend"
            )
            return f"{vol}_{core}"
        if row["Trendiness"] == "Range":
            return f"{vol}_Range"
        return f"{vol}_Mixed"

    df["Regime"] = df.apply(label_row, axis=1)

    # Optional: keep session label for traceability
    if session_col and session_col in df.columns:
        df["Session"] = df[session_col]

    return df

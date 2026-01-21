from dataclasses import dataclass
from typing import Iterable

from ..db import get_duckdb_connection
from ..utils.dir import get_sql_query


@dataclass(frozen=True)
class ResampleConfig:
    target_table: str
    bucket_expr: str
    extra_filter: str = ""


RESAMPLE_CONFIGS = {
    "15m": ResampleConfig(
        target_table="ohlcv_15m",
        bucket_expr=(
            "date_trunc('hour', time) + INTERVAL '15 minutes' * "
            "floor(extract(minute from time) / 15)"
        ),
    ),
    "30m": ResampleConfig(
        target_table="ohlcv_30m",
        bucket_expr=(
            "date_trunc('hour', time) + INTERVAL '30 minutes' * "
            "floor(extract(minute from time) / 30)"
        ),
    ),
    "1h": ResampleConfig(
        target_table="ohlcv_hour",
        bucket_expr="date_trunc('hour', time)",
    ),
    "1d": ResampleConfig(
        target_table="ohlcv_daily",
        bucket_expr="date_trunc('day', time)",
    ),
    "1w": ResampleConfig(
        target_table="ohlcv_weekly",
        bucket_expr="date_trunc('week', time)",
    ),
    "1d_rth": ResampleConfig(
        target_table="ohlcv_daily_rth",
        bucket_expr=(
            "date_trunc('day', time AT TIME ZONE 'America/New_York') "
            "AT TIME ZONE 'America/New_York'"
        ),
        extra_filter=(
            "AND (time AT TIME ZONE 'America/New_York')::time >= time '09:30' "
            "AND (time AT TIME ZONE 'America/New_York')::time < time '16:00'"
        ),
    ),
}


def resample_minute_range(
    timeframe: str,
    start_time: str,
    end_time: str,
) -> None:
    config = RESAMPLE_CONFIGS[timeframe]
    query = get_sql_query(
        "resample_minute_to_timeframe",
        target_table=config.target_table,
        bucket_expr=config.bucket_expr,
        start_time=start_time,
        end_time=end_time,
        extra_filter=config.extra_filter,
    )
    with get_duckdb_connection() as con:
        _ensure_resample_tables(con)
        con.execute(query)


def resample_minute_ranges(
    timeframes: Iterable[str],
    start_time: str,
    end_time: str,
) -> None:
    for timeframe in timeframes:
        resample_minute_range(timeframe, start_time, end_time)


def align_resample_window(start_time: str, end_time: str) -> tuple[str, str]:
    query = get_sql_query(
        "align_resample_window",
        start_time=start_time,
        end_time=end_time,
    )
    with get_duckdb_connection() as con:
        row = con.execute(query).fetchone()
    if not row:
        return start_time, end_time
    aligned_start, aligned_end = row
    return aligned_start.isoformat(), aligned_end.isoformat()


def _ensure_resample_tables(con) -> None:
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS ohlcv_15m (
            symbol TEXT NOT NULL,
            time   TIMESTAMPTZ NOT NULL,
            open   DOUBLE,
            high   DOUBLE,
            low    DOUBLE,
            close  DOUBLE,
            volume BIGINT,
            added_at TIMESTAMPTZ DEFAULT (NOW() AT TIME ZONE 'UTC'),
            PRIMARY KEY (symbol, time)
        );
        """
    )
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS ohlcv_30m (
            symbol TEXT NOT NULL,
            time   TIMESTAMPTZ NOT NULL,
            open   DOUBLE,
            high   DOUBLE,
            low    DOUBLE,
            close  DOUBLE,
            volume BIGINT,
            added_at TIMESTAMPTZ DEFAULT (NOW() AT TIME ZONE 'UTC'),
            PRIMARY KEY (symbol, time)
        );
        """
    )
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS ohlcv_daily_rth (
            symbol TEXT NOT NULL,
            time   TIMESTAMPTZ NOT NULL,
            open   DOUBLE,
            high   DOUBLE,
            low    DOUBLE,
            close  DOUBLE,
            volume BIGINT,
            added_at TIMESTAMPTZ DEFAULT (NOW() AT TIME ZONE 'UTC'),
            PRIMARY KEY (symbol, time)
        );
        """
    )

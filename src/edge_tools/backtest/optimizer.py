from __future__ import annotations

import itertools
import uuid
from datetime import datetime

import duckdb
import pandas as pd

from edge_tools.db import get_duckdb_connection

from .engine import DEFAULT_SYMBOL, CandleBundle, load_candles
from .metrics import compute_metrics
from .schemas import StrategyParams
from .strategies import run_strategy


def run_grid_search(
    param_grid: dict,
    worker_id: int,
    n_workers: int,
    symbol: str = DEFAULT_SYMBOL,
) -> None:
    candle_bundle = load_candles(symbol=symbol)

    with get_duckdb_connection() as con:
        _ensure_strategy_runs_table(con)
        for index, params in _iter_params(param_grid):
            if index % n_workers != worker_id:
                continue
            run_id = uuid.uuid4().hex
            trades = run_strategy(
                candle_bundle.candles_5m,
                candle_bundle.candles_1h,
                candle_bundle.candles_1d,
                params,
            )
            metrics = compute_metrics(trades)
            _insert_run(con, run_id, params, metrics)


def run_walkforward(
    top_n: int = 50,
    symbol: str = DEFAULT_SYMBOL,
) -> None:
    candle_bundle = load_candles(symbol=symbol)
    candles_5m = candle_bundle.candles_5m.copy()
    candles_5m["time"] = pd.to_datetime(candles_5m["time"], utc=True)
    years = sorted(candles_5m["time"].dt.year.unique().tolist())
    if len(years) < 2:
        return

    with get_duckdb_connection() as con:
        _ensure_strategy_walkforward_table(con)
        top_params = con.execute(
            "SELECT * FROM strategy_runs ORDER BY expectancy DESC LIMIT ?",
            [top_n],
        ).df()

        if top_params.empty:
            return

        for _, row in top_params.iterrows():
            params = _row_to_params(row)
            parent_run_id = row["run_id"]
            for split_year in years[1:]:
                train_start = datetime(years[0], 1, 1)
                train_end = datetime(split_year, 1, 1)
                test_start = datetime(split_year, 1, 1)
                test_end = datetime(split_year + 1, 1, 1)

                train_bundle = _filter_bundle(
                    candle_bundle,
                    start=train_start,
                    end=train_end,
                )
                test_bundle = _filter_bundle(
                    candle_bundle,
                    start=test_start,
                    end=test_end,
                )

                if train_bundle.candles_5m.empty or test_bundle.candles_5m.empty:
                    continue

                train_metrics = compute_metrics(
                    run_strategy(
                        train_bundle.candles_5m,
                        train_bundle.candles_1h,
                        train_bundle.candles_1d,
                        params,
                    )
                )
                test_metrics = compute_metrics(
                    run_strategy(
                        test_bundle.candles_5m,
                        test_bundle.candles_1h,
                        test_bundle.candles_1d,
                        params,
                    )
                )

                _insert_walkforward(
                    con=con,
                    walk_id=uuid.uuid4().hex,
                    parent_run_id=parent_run_id,
                    params=params,
                    split_year=split_year,
                    train_metrics=train_metrics,
                    test_metrics=test_metrics,
                )


def _iter_params(param_grid: dict) -> itertools.chain:
    keys = list(param_grid.keys())
    values = [param_grid[key] for key in keys]
    for index, combo in enumerate(itertools.product(*values)):
        raw = dict(zip(keys, combo))
        params = StrategyParams(**raw)
        yield index, params


def _insert_run(
    con: duckdb.DuckDBPyConnection,
    run_id: str,
    params: StrategyParams,
    metrics: dict,
) -> None:
    con.execute(
        """
        INSERT INTO strategy_runs (
            run_id,
            stop_loss,
            take_profit,
            max_bars,
            breakout_lookback,
            entry_offset,
            daily_regime,
            hourly_regime,
            trades,
            winrate,
            expectancy,
            avg_MAE,
            avg_MFE,
            max_drawdown,
            profit_factor,
            sharpe
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            run_id,
            params.stop_loss,
            params.take_profit,
            params.max_bars,
            params.breakout_lookback,
            params.entry_offset,
            params.daily_regime,
            params.hourly_regime,
            metrics["trades"],
            metrics["winrate"],
            metrics["expectancy"],
            metrics["avg_MAE"],
            metrics["avg_MFE"],
            metrics["max_drawdown"],
            metrics["profit_factor"],
            metrics["sharpe"],
        ],
    )


def _ensure_strategy_runs_table(con: duckdb.DuckDBPyConnection) -> None:
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS strategy_runs (
            run_id TEXT,
            stop_loss INTEGER,
            take_profit INTEGER,
            max_bars INTEGER,
            breakout_lookback INTEGER,
            entry_offset DOUBLE,
            daily_regime TEXT,
            hourly_regime TEXT,
            trades INTEGER,
            winrate DOUBLE,
            expectancy DOUBLE,
            avg_MAE DOUBLE,
            avg_MFE DOUBLE,
            max_drawdown DOUBLE,
            profit_factor DOUBLE,
            sharpe DOUBLE
        )
        """
    )


def _ensure_strategy_walkforward_table(con: duckdb.DuckDBPyConnection) -> None:
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS strategy_walkforward_results (
            walk_id TEXT,
            parent_run_id TEXT,
            split_year INTEGER,
            stop_loss INTEGER,
            take_profit INTEGER,
            max_bars INTEGER,
            breakout_lookback INTEGER,
            entry_offset DOUBLE,
            daily_regime TEXT,
            hourly_regime TEXT,
            train_trades INTEGER,
            train_winrate DOUBLE,
            train_expectancy DOUBLE,
            train_avg_MAE DOUBLE,
            train_avg_MFE DOUBLE,
            train_max_drawdown DOUBLE,
            train_profit_factor DOUBLE,
            train_sharpe DOUBLE,
            test_trades INTEGER,
            test_winrate DOUBLE,
            test_expectancy DOUBLE,
            test_avg_MAE DOUBLE,
            test_avg_MFE DOUBLE,
            test_max_drawdown DOUBLE,
            test_profit_factor DOUBLE,
            test_sharpe DOUBLE
        )
        """
    )


def _insert_walkforward(
    con: duckdb.DuckDBPyConnection,
    walk_id: str,
    parent_run_id: str,
    params: StrategyParams,
    split_year: int,
    train_metrics: dict,
    test_metrics: dict,
) -> None:
    con.execute(
        """
        INSERT INTO strategy_walkforward_results (
            walk_id,
            parent_run_id,
            split_year,
            stop_loss,
            take_profit,
            max_bars,
            breakout_lookback,
            entry_offset,
            daily_regime,
            hourly_regime,
            train_trades,
            train_winrate,
            train_expectancy,
            train_avg_MAE,
            train_avg_MFE,
            train_max_drawdown,
            train_profit_factor,
            train_sharpe,
            test_trades,
            test_winrate,
            test_expectancy,
            test_avg_MAE,
            test_avg_MFE,
            test_max_drawdown,
            test_profit_factor,
            test_sharpe
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            walk_id,
            parent_run_id,
            split_year,
            params.stop_loss,
            params.take_profit,
            params.max_bars,
            params.breakout_lookback,
            params.entry_offset,
            params.daily_regime,
            params.hourly_regime,
            train_metrics["trades"],
            train_metrics["winrate"],
            train_metrics["expectancy"],
            train_metrics["avg_MAE"],
            train_metrics["avg_MFE"],
            train_metrics["max_drawdown"],
            train_metrics["profit_factor"],
            train_metrics["sharpe"],
            test_metrics["trades"],
            test_metrics["winrate"],
            test_metrics["expectancy"],
            test_metrics["avg_MAE"],
            test_metrics["avg_MFE"],
            test_metrics["max_drawdown"],
            test_metrics["profit_factor"],
            test_metrics["sharpe"],
        ],
    )


def _filter_bundle(
    bundle: CandleBundle,
    start: datetime,
    end: datetime,
) -> CandleBundle:
    return CandleBundle(
        candles_5m=_filter_by_time(bundle.candles_5m, start, end),
        candles_1h=_filter_by_time(bundle.candles_1h, start, end),
        candles_1d=_filter_by_time(bundle.candles_1d, start, end),
    )


def _filter_by_time(frame: pd.DataFrame, start: datetime, end: datetime) -> pd.DataFrame:
    if frame.empty:
        return frame
    local = frame.copy()
    local["time"] = pd.to_datetime(local["time"], utc=True)
    mask = (local["time"] >= start) & (local["time"] < end)
    return local.loc[mask].reset_index(drop=True)


def _row_to_params(row: pd.Series) -> StrategyParams:
    return StrategyParams(
        stop_loss=int(row["stop_loss"]),
        take_profit=int(row["take_profit"]),
        max_bars=int(row["max_bars"]),
        breakout_lookback=int(row["breakout_lookback"]),
        entry_offset=float(row["entry_offset"]),
        daily_regime=str(row["daily_regime"]),
        hourly_regime=str(row["hourly_regime"]),
    )

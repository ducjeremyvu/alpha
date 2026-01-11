from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class StrategyParams(BaseModel):
    stop_loss: int
    take_profit: int
    max_bars: int
    breakout_lookback: int
    entry_offset: float
    daily_regime: str
    hourly_regime: str


class Trade(BaseModel):
    entry_time: datetime
    entry_price: float
    exit_time: datetime
    exit_price: float
    mae: float
    mfe: float
    direction: Literal["long", "short"]


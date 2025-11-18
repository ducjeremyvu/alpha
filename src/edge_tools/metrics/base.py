from dataclasses import dataclass
from typing import Callable, Literal


@dataclass
class MetricDefinition:
    name: str
    description: str
    dataset: Literal["intraday", "daily", "us_open_30m"]  # which data source
    window: Literal["all", "us_open_30m", "us_business_hours"] = ""
    unit: str = ""
    category: str = ""
    compute: Callable = None

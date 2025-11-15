from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from edge_tools.api.data import ny_open_30_minute_by_date
from edge_tools.utils.logger import setup_logging

from utils import Cache

import pandas as pd
import logging

logger = logging.getLogger(__name__)

setup_logging(logging.DEBUG)

cache = Cache()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/items/{item_id}")
async def read_item(item_id):
    return {"item_id": item_id}


@app.get("/candles")
def get_candles(date: str):
    # caching 
    key = f"/candles?symbol=US500&date{date}"
    cached = cache.get(key)
    if cached is not None:
        logger.debug("Returning from cached values")
        # return {"cached": True, "data": cached}
        return cached
        
    df = ny_open_30_minute_by_date(date)
    logger.debug(df.head(10))
    if df["time"].dt.tz is None:
        df["time"] = df["time"].dt.tz_localize("America/New_York")
    df["time"] = df["time"].dt.tz_convert("UTC")
    df["time"] = df["time"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    logger.debug(f"/candles for {date}: \n {df.head(10)}")
    
    df = df.to_dict("records")
    cache.set(key, df)
    return df

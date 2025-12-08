from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from edge_tools.load import ny_open_30_minute_by_date
from edge_tools.utils.logger import setup_logging
from edge_tools.db import get_duckdb_connection
from edge_tools.analytics.context_replay import (
    fetch_context_replay_data_and_calculate_metrics,
)
from contextlib import asynccontextmanager

from .utils import Cache

import logging

logger = logging.getLogger(__name__)

setup_logging(logging.DEBUG)

cache = Cache()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Connecting DuckDB...")
    app.state.con = get_duckdb_connection(read_only=True)

    yield

    # Shutdown
    logger.info("🛑 Closing DuckDB...")
    app.state.con.close()


app = FastAPI(lifespan=lifespan)

#
# origins = [
#      "http://localhost:5173",
#      "http://127.0.0.1:5173",
#  ]


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/candles")
def get_candles(date: str, request: Request):
    con = request.app.state.con
    # caching
    key = f"/candles?symbol=US500&date{date}"
    cached = cache.get(key)
    if cached is not None:
        logger.debug("Returning from cached values")
        # return {"cached": True, "data": cached}
        return cached

    df = ny_open_30_minute_by_date(con, date)
    if df is None:
        return {
            "data": {},
            "metrics": {},
            "available": False,
            "message": "No data available for this date.",
        }
    logger.debug(df.head(10))

    ###################
    # Time Conversion #
    ###################
    if df["time"].dt.tz is None:
        df["time"] = df["time"].dt.tz_localize("America/New_York")
    df["time"] = df["time"].dt.tz_convert("UTC")
    df["time"] = df["time"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    logger.debug(f"/candles for {date}: \n {df.head(10)}")

    df = df.to_dict("records")

    response = {}
    response["data"] = df
    response["metrics"] = ""

    logger.debug(
        f"""
                 Get candles will output the following: 
                 {response}
    """
    )
    cache.set(key, response)

    return response


@app.get("/context_replay")
def get_context_replay(date: str, request: Request):
    con = request.app.state.con

    key = f"/context_replay?symbol=US500&date{date}"

    response = fetch_context_replay_data_and_calculate_metrics(con, date)
    cache.set(key, response)
    logger.debug(response.keys())
    return response


@app.get("/utils/latest_date")
def get_latest_date(request: Request):
    con = request.app.state.con

    df = con.execute("SELECT max(time)::date as max_date from ohlcv_minute").df()

    response = df.iloc[0]["max_date"].strftime("%Y-%m-%d")
    return response

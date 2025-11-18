import time
from typing import Any, Dict, Tuple


class Cache:
    def __init__(self, ttl_secs: int = 21600, max_items=500):
        self.ttl = ttl_secs
        self.max_items = max_items
        self.store: Dict[str, Tuple[float, Any]] = {}

    def _is_expired(self, timestamp: float) -> bool:
        return (time.time() - timestamp) > self.ttl

    def get(self, key: str):
        item = self.store.get(key)
        if not item:
            return None
        ts, data = item
        if self._is_expired(ts):
            del self.store[key]
            return None
        return data

    def set(self, key: str, data: Any):
        if len(self.store) >= self.max_items:
            # remove something arbitrary or oldest
            self.store.pop(next(iter(self.store)))
        self.store[key] = (time.time(), data)

    def clear(self):
        self.store.clear()


""" How to use:

from fastapi import FastAPI, Depends
from utils.cache import Cache

app = FastAPI()
cache = Cache(ttl_secs=300)

@app.get("/ohlcv")
def get_ohlcv(symbol: str, date: str):
    key = f"{symbol}:{date}"
    cached = cache.get(key)
    if cached is not None:
        return {"cached": True, "data": cached}

    data = compute_ohlcv(symbol, date)
    cache.set(key, data)
    return {"cached": False, "data": data}



"""

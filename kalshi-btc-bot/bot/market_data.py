"""Market discovery: finds the currently-open BTC 15-minute market on Kalshi."""
from __future__ import annotations

import logging
import time

from .config import KalshiConfig
from .kalshi_client import KalshiClient
from .models import Market, OrderBook

log = logging.getLogger("markets")


class KalshiMarketData:
    def __init__(self, client: KalshiClient, cfg: KalshiConfig):
        self.client = client
        self.cfg = cfg
        self._cache: list[Market] = []
        self._cache_ts = 0.0

    async def open_markets(self, max_age: float = 3.0) -> list[Market]:
        if time.time() - self._cache_ts > max_age:
            self._cache = await self.client.list_markets(self.cfg.series_ticker, self.cfg.up_side, status="open")
            self._cache_ts = time.time()
        return self._cache

    async def find_current_market(self, now: float) -> Market | None:
        markets = await self.open_markets()
        live = [m for m in markets if m.open_ts <= now < m.close_ts]
        good = [m for m in live
                if self.cfg.min_market_duration_seconds <= m.duration <= self.cfg.max_market_duration_seconds]
        if live and not good:
            log.debug("open markets found but none with a ~15 minute duration: %s", [m.ticker for m in live])
        if not good:
            return None
        return max(good, key=lambda m: m.open_ts)  # the newest one

    async def get_market(self, ticker: str) -> Market:
        return await self.client.get_market(ticker, self.cfg.up_side)

    async def get_orderbook(self, ticker: str) -> OrderBook:
        return await self.client.get_orderbook(ticker)

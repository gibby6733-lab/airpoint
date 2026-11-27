"""Real-time BTC price feed with automatic failover and reconnection.

Primary: Coinbase Exchange public websocket (`matches` channel: every trade with aggressor side).
Fallback: Kraken v2 public websocket (`trade` channel).
History is seeded from Coinbase 1-minute candles so volatility is available immediately.

Note: Kalshi settles BTC markets on the CF Benchmarks BRTI index, a composite of several exchanges.
Coinbase/Kraken track it closely but not exactly; the bot measures moves relative to the exchange's own
open price so the basis largely cancels out (see strategy.reference_mode).
"""
from __future__ import annotations

import asyncio
import bisect
import json
import logging
import time
from collections import deque
from datetime import datetime

import httpx

from .models import Tick
from .signals import vol_from_minute_closes

log = logging.getLogger("feed")

COINBASE_WS = "wss://ws-feed.exchange.coinbase.com"
COINBASE_REST = "https://api.exchange.coinbase.com"
KRAKEN_WS = "wss://ws.kraken.com/v2"


class TickBuffer:
    """Time-ordered tick store with 1-minute close bars for volatility estimation."""

    def __init__(self, max_age_seconds: float = 7200):
        self.max_age = max_age_seconds
        self.ticks: deque[Tick] = deque()
        self.minute_closes: dict[int, float] = {}
        self.last_update = 0.0
        self.source = "none"

    def add(self, tick: Tick, received_at: float | None = None):
        if self.ticks and tick.ts < self.ticks[-1].ts:
            tick.ts = self.ticks[-1].ts  # keep monotonic; exchanges occasionally deliver slightly out of order
        self.ticks.append(tick)
        self.minute_closes[int(tick.ts // 60)] = tick.price
        self.last_update = received_at if received_at is not None else tick.ts
        cutoff = tick.ts - self.max_age
        while self.ticks and self.ticks[0].ts < cutoff:
            self.ticks.popleft()
        if len(self.minute_closes) > self.max_age / 60 + 10:
            for k in sorted(self.minute_closes)[: len(self.minute_closes) - int(self.max_age / 60)]:
                del self.minute_closes[k]

    def seed_minute_close(self, minute_ts: float, close: float):
        self.minute_closes.setdefault(int(minute_ts // 60), close)

    def last_price(self) -> float | None:
        return self.ticks[-1].price if self.ticks else None

    def between(self, start: float, end: float) -> list[Tick]:
        if not self.ticks:
            return []
        lst = list(self.ticks)
        times = [t.ts for t in lst]
        i = max(0, bisect.bisect_left(times, start) - 1)  # include last tick before start (for open price)
        j = bisect.bisect_right(times, end)
        return lst[i:j]

    def vol_bps_per_min(self, lookback_minutes: int, end_ts: float) -> float | None:
        end_min = int(end_ts // 60)
        closes = []
        last = None
        for m in range(end_min - lookback_minutes, end_min + 1):
            v = self.minute_closes.get(m, last)
            if v is not None:
                closes.append(v)
                last = v
        return vol_from_minute_closes(closes)

    def is_stale(self, now: float, stale_after: float) -> bool:
        return (now - self.last_update) > stale_after

    def chart_points(self, start: float, end: float, step: float = 2.0) -> list[list[float]]:
        ticks = self.between(start, end)
        out, next_t = [], start
        for t in ticks:
            if t.ts >= next_t:
                out.append([round(t.ts, 2), t.price])
                next_t = t.ts + step
        if ticks and (not out or out[-1][0] != round(ticks[-1].ts, 2)):
            out.append([round(ticks[-1].ts, 2), ticks[-1].price])
        return out


class PriceFeed:
    def __init__(self, sources: list[str], buffer_minutes: int = 120, stale_after: float = 10.0):
        self.sources = sources or ["coinbase", "kraken"]
        self.buffer = TickBuffer(buffer_minutes * 60)
        self.stale_after = stale_after
        self.status = "starting"
        self.errors = 0
        self._stop = False

    # interface used by the engine
    def now(self) -> float:
        return time.time()

    async def seed_history(self, minutes: int = 90):
        end = int(time.time())
        start = end - minutes * 60
        try:
            async with httpx.AsyncClient(timeout=10) as http:
                r = await http.get(f"{COINBASE_REST}/products/BTC-USD/candles",
                                   params={"granularity": 60, "start": datetime.utcfromtimestamp(start).isoformat(),
                                           "end": datetime.utcfromtimestamp(end).isoformat()})
                r.raise_for_status()
                for row in sorted(r.json()):  # [time, low, high, open, close, volume]
                    self.buffer.seed_minute_close(row[0], float(row[4]))
            log.info("seeded %d minutes of BTC history", len(self.buffer.minute_closes))
        except Exception as exc:  # noqa: BLE001
            log.warning("could not seed BTC history (%s); volatility will warm up from live ticks", exc)

    async def run(self):
        import websockets  # local import keeps the backtester usable without it

        await self.seed_history()
        idx = 0
        while not self._stop:
            src = self.sources[idx % len(self.sources)]
            try:
                self.status = f"connecting:{src}"
                if src == "coinbase":
                    await self._run_coinbase(websockets)
                elif src == "kraken":
                    await self._run_kraken(websockets)
                else:
                    raise ValueError(f"unknown feed source {src}")
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # noqa: BLE001
                self.errors += 1
                log.warning("BTC feed %s failed: %s", src, exc)
            self.status = "reconnecting"
            idx += 1  # fail over to the next source
            await asyncio.sleep(min(10, 1 + self.errors * 0.5))

    async def _consume(self, ws, parse):
        while True:
            raw = await asyncio.wait_for(ws.recv(), timeout=self.stale_after * 2)
            for tick in parse(json.loads(raw)):
                self.buffer.add(tick, received_at=time.time())
            if self.buffer.is_stale(time.time(), self.stale_after * 3):
                raise TimeoutError("feed stale")

    async def _run_coinbase(self, websockets):
        async with websockets.connect(COINBASE_WS, ping_interval=20, ping_timeout=20, max_size=2**22) as ws:
            await ws.send(json.dumps({"type": "subscribe", "product_ids": ["BTC-USD"],
                                      "channels": ["matches", "heartbeat"]}))
            self.status = "live:coinbase"
            self.buffer.source = "coinbase"
            log.info("connected to Coinbase BTC-USD feed")

            def parse(msg):
                if msg.get("type") in ("match", "last_match") and msg.get("product_id") == "BTC-USD":
                    ts = datetime.fromisoformat(msg["time"].replace("Z", "+00:00")).timestamp()
                    # Coinbase `side` is the MAKER side; aggressor is the opposite.
                    aggressor = "buy" if msg.get("side") == "sell" else "sell"
                    yield Tick(ts, float(msg["price"]), float(msg.get("size", 0)), aggressor)
                elif msg.get("type") == "error":
                    raise RuntimeError(msg.get("message", "coinbase error"))

            await self._consume(ws, parse)

    async def _run_kraken(self, websockets):
        async with websockets.connect(KRAKEN_WS, ping_interval=20, ping_timeout=20) as ws:
            await ws.send(json.dumps({"method": "subscribe", "params": {"channel": "trade", "symbol": ["BTC/USD"]}}))
            self.status = "live:kraken"
            self.buffer.source = "kraken"
            log.info("connected to Kraken BTC/USD feed")

            def parse(msg):
                if msg.get("channel") == "trade":
                    for t in msg.get("data", []):
                        ts = datetime.fromisoformat(t["timestamp"].replace("Z", "+00:00")).timestamp()
                        yield Tick(ts, float(t["price"]), float(t.get("qty", 0)), t.get("side"))

            await self._consume(ws, parse)

    def stop(self):
        self._stop = True

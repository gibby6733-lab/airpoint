"""Offline simulator: synthetic BTC trades + synthetic Kalshi 15-minute markets.

For exercising the full pipeline (dashboard, risk, settlement) without network access or money.
The synthetic price has a slowly-varying drift (so momentum exists *by construction*) and a market maker
that quotes the pure random-walk fair value. Profits in the simulator therefore prove nothing about
the real market - use the backtester on real data and paper trading for that.
"""
from __future__ import annotations

import asyncio
import math
import random
import time

from .btc_feed import TickBuffer
from .models import BookLevel, Market, OrderBook, Tick, norm_cdf

MARKET_SECONDS = 900


class SimClock:
    def __init__(self, speed: float = 1.0, start: float | None = None):
        self.speed = max(0.01, speed)
        self._real0 = time.time()
        if start is None:
            now = time.time()
            start = (now // MARKET_SECONDS + 1) * MARKET_SECONDS - 20  # first market opens in ~20 sim seconds
        self._sim0 = start

    def now(self) -> float:
        return self._sim0 + (time.time() - self._real0) * self.speed

    async def sleep(self, seconds: float):
        await asyncio.sleep(seconds / self.speed)


class ManualClock:
    """Deterministic clock for tests."""

    def __init__(self, start: float):
        self.t = start

    def now(self) -> float:
        return self.t

    async def sleep(self, seconds: float):
        self.t += seconds


class SimWorld:
    def __init__(self, start_ts: float, seed: int | None = None, base_vol_bps_per_min: float = 7.0,
                 drift_std_bps_per_min: float = 0.9, drift_halflife_min: float = 8.0, tick_dt: float = 0.25,
                 history_minutes: int = 90):
        self.rng = random.Random(seed)
        self.vol = base_vol_bps_per_min
        self.tick_dt = tick_dt
        self.kappa = math.log(2) / (drift_halflife_min * 60)
        self.drift_std = drift_std_bps_per_min
        self.price = 95000.0
        self.mu = 0.0  # bps/min
        self.vol_regime = 1.0
        self.buffer = TickBuffer(history_minutes * 60 + 3 * 3600)
        self.t = start_ts - history_minutes * 60
        self._price_log: dict[int, float] = {}  # second -> price, for strikes/settlement
        self._bias: dict[str, float] = {}
        self.advance(start_ts)

    def _step(self):
        dt = self.tick_dt
        # OU drift (bps/min) - creates persistent trends
        eta = self.drift_std * math.sqrt(2 * self.kappa)
        self.mu += -self.kappa * self.mu * dt + eta * math.sqrt(dt) * self.rng.gauss(0, 1)
        # occasional volatility regime shifts
        if self.rng.random() < dt / 1800:
            self.vol_regime = self.rng.choice([0.6, 1.0, 1.0, 1.6])
        sigma_s = self.vol * self.vol_regime / math.sqrt(60) / 1e4
        mu_s = self.mu / 60 / 1e4
        self.price *= math.exp(mu_s * dt + sigma_s * math.sqrt(dt) * self.rng.gauss(0, 1))
        self.t += dt
        p_buy = 0.5 + 0.3 * math.tanh(self.mu / 1.5) + self.rng.uniform(-0.15, 0.15)
        side = "buy" if self.rng.random() < p_buy else "sell"
        size = round(self.rng.expovariate(1 / 0.08), 5)
        tick = Tick(self.t, round(self.price, 2), size, side)
        self.buffer.add(tick, received_at=self.t)
        self._price_log[int(self.t)] = tick.price

    def advance(self, until: float):
        while self.t + self.tick_dt <= until:
            self._step()
        cutoff = int(until) - 4 * 3600
        if len(self._price_log) > 20000:
            for k in [k for k in self._price_log if k < cutoff]:
                del self._price_log[k]

    def price_at(self, ts: float) -> float | None:
        s = int(ts)
        for k in range(s, s - 30, -1):
            if k in self._price_log:
                return self._price_log[k]
        return None

    # ------------------------------------------------------------ markets
    def market_for(self, open_ts: float) -> Market:
        open_ts = (open_ts // MARKET_SECONDS) * MARKET_SECONDS
        ticker = "KXBTC15M-SIM-" + time.strftime("%y%b%d%H%M", time.gmtime(open_ts + MARKET_SECONDS)).upper()
        close_ts = open_ts + MARKET_SECONDS
        strike = self.price_at(open_ts) if self.t >= open_ts else None
        result = None
        status = "active"
        if self.t >= close_ts + 5:
            final = self.price_at(close_ts)
            result = "yes" if (final is not None and strike is not None and final >= strike) else "no"
            status = "settled"
        elif self.t >= close_ts:
            status = "closed"
        return Market(ticker, ticker.rsplit("-", 1)[0], open_ts, close_ts, strike, status, "yes", result,
                      title="BTC price up in next 15 mins? (SIM)")

    def orderbook(self, m: Market) -> OrderBook:
        now = self.t
        if m.strike is None or now >= m.close_ts:
            return OrderBook(ts=now)
        dist = (self.price - m.strike) / m.strike * 1e4
        rem_min = max((m.close_ts - now) / 60, 0.05)
        fair = norm_cdf(dist / (self.vol * self.vol_regime * math.sqrt(rem_min)))
        bias = self._bias.setdefault(m.ticker, self.rng.gauss(0, 0.012))
        mid = min(0.985, max(0.015, fair + bias + self.rng.gauss(0, 0.004)))
        half = self.rng.choice([0.01, 0.01, 0.015, 0.02])
        yes_bid = max(0.01, math.floor((mid - half) * 100) / 100)
        yes_ask = min(0.99, math.ceil((mid + half) * 100) / 100)
        yes_bids = [BookLevel(round(yes_bid - i * 0.01, 2), self.rng.randint(40, 400))
                    for i in range(4) if yes_bid - i * 0.01 >= 0.01]
        no_bid = round(1 - yes_ask, 2)
        no_bids = [BookLevel(round(no_bid - i * 0.01, 2), self.rng.randint(40, 400))
                   for i in range(4) if no_bid - i * 0.01 >= 0.01]
        return OrderBook(yes_bids, no_bids, ts=now)


class SimMarketData:
    def __init__(self, world: SimWorld, clock):
        self.world = world
        self.clock = clock
        self._markets: dict[str, float] = {}

    def _sync(self):
        self.world.advance(self.clock.now())

    async def find_current_market(self, now: float) -> Market | None:
        self._sync()
        m = self.world.market_for(now)
        self._markets[m.ticker] = m.open_ts
        return m if m.open_ts <= now < m.close_ts else None

    async def get_market(self, ticker: str) -> Market:
        self._sync()
        return self.world.market_for(self._markets[ticker])

    async def get_orderbook(self, ticker: str) -> OrderBook:
        self._sync()
        return self.world.orderbook(self.world.market_for(self._markets[ticker]))


class SimFeed:
    """Feed adapter so the engine treats the simulator like a live exchange feed."""

    def __init__(self, world: SimWorld, clock, stale_after: float = 10.0):
        self.world = world
        self.clock = clock
        self.buffer = world.buffer
        self.buffer.source = "simulator"
        self.stale_after = stale_after
        self.status = "live:simulator"
        self._stop = False

    async def run(self):
        while not self._stop:
            self.world.advance(self.clock.now())
            await asyncio.sleep(0.2)

    def stop(self):
        self._stop = True

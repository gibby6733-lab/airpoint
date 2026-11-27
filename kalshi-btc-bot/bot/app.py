"""Wires components together and decides paper vs live (live only if the gate passes)."""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass

from .config import Config
from .engine import TradingEngine
from .execution import LiveExecutor, PaperExecutor
from .live_gate import evaluate_live_gate
from .risk import RiskManager
from .storage import Storage

log = logging.getLogger("app")


class RealClock:
    def now(self) -> float:
        return time.time()

    async def sleep(self, seconds: float):
        import asyncio
        await asyncio.sleep(seconds)


@dataclass
class Runtime:
    cfg: Config
    storage: Storage
    engine: TradingEngine
    feed: object
    client: object | None = None


def build_runtime(cfg: Config) -> Runtime:
    storage = Storage(cfg.data_dir / "bot.db")
    gate = evaluate_live_gate(cfg, storage)
    client = None

    if cfg.mode.data_source == "sim":
        from .simulator import SimClock, SimFeed, SimMarketData, SimWorld
        clock = SimClock(cfg.mode.sim_speed)
        world = SimWorld(clock.now())
        feed = SimFeed(world, clock, cfg.feed.stale_after_seconds)
        md = SimMarketData(world, clock)
        executor = PaperExecutor(md, cfg.execution, sleep=clock.sleep)
    else:
        from .btc_feed import PriceFeed
        from .kalshi_client import build_client
        from .market_data import KalshiMarketData
        clock = RealClock()
        client = build_client(cfg)
        feed = PriceFeed(cfg.feed.sources, cfg.feed.buffer_minutes, cfg.feed.stale_after_seconds)
        md = KalshiMarketData(client, cfg.kalshi)
        if cfg.mode.trading_mode == "live" and gate["allowed"]:
            log.warning("LIVE TRADING ENABLED - real orders will be sent to Kalshi")
            executor = LiveExecutor(client, cfg.execution, cfg.kalshi.price_format)
        else:
            if cfg.mode.trading_mode == "live":
                log.error("live trading requested but the live gate FAILED; running in PAPER mode:\n  %s",
                          "\n  ".join(gate["failing"]))
            executor = PaperExecutor(md, cfg.execution)

    risk = RiskManager(cfg.risk, storage, cfg.data_dir, executor.mode, clock=clock.now)
    engine = TradingEngine(cfg, storage, md, feed, executor, risk, clock, gate=gate)
    return Runtime(cfg, storage, engine, feed, client)

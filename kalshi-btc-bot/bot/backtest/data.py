"""Historical data for backtests: Coinbase 1-minute BTC candles, Kalshi settled BTC15M markets, or synthetic."""
from __future__ import annotations

import asyncio
import csv
import json
import logging
import math
import random
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import httpx

from ..models import parse_iso, price_field

log = logging.getLogger("backtest.data")

COINBASE_REST = "https://api.exchange.coinbase.com"


@dataclass(slots=True)
class Candle:
    ts: float      # minute start (unix seconds)
    open: float
    high: float
    low: float
    close: float
    volume: float


def _iso(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_candles_csv(path: Path) -> list[Candle]:
    with open(path) as fh:
        return [Candle(float(r["ts"]), float(r["open"]), float(r["high"]), float(r["low"]),
                       float(r["close"]), float(r["volume"])) for r in csv.DictReader(fh)]


def save_candles_csv(path: Path, candles: list[Candle]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["ts", "open", "high", "low", "close", "volume"])
        for c in candles:
            w.writerow([int(c.ts), c.open, c.high, c.low, c.close, c.volume])


async def fetch_coinbase_candles(start: float, end: float, cache_dir: Path) -> list[Candle]:
    start, end = int(start // 60 * 60), int(end // 60 * 60)
    cache = cache_dir / f"coinbase_btcusd_1m_{start}_{end}.csv"
    if cache.exists():
        return load_candles_csv(cache)
    out: dict[int, Candle] = {}
    chunk = 300 * 60
    async with httpx.AsyncClient(timeout=15, headers={"User-Agent": "btc15m-backtester/1.0"}) as http:
        t = start
        while t < end:
            t2 = min(end, t + chunk)
            for attempt in range(5):
                try:
                    r = await http.get(f"{COINBASE_REST}/products/BTC-USD/candles",
                                       params={"granularity": 60, "start": _iso(t), "end": _iso(t2)})
                    if r.status_code == 429:
                        await asyncio.sleep(1 + attempt)
                        continue
                    r.raise_for_status()
                    for row in r.json():  # [time, low, high, open, close, volume]
                        out[int(row[0])] = Candle(row[0], row[3], row[2], row[1], row[4], row[5])
                    break
                except httpx.HTTPError as exc:
                    if attempt == 4:
                        raise
                    log.warning("coinbase candles retry (%s)", exc)
                    await asyncio.sleep(1 + attempt)
            t = t2
            await asyncio.sleep(0.15)
    candles = [out[k] for k in sorted(out)]
    save_candles_csv(cache, candles)
    return candles


def synthetic_candles(days: float, seed: int = 7, base_vol_bps_per_min: float = 7.0,
                      drift_std_bps_per_min: float = 0.0, start: float | None = None) -> list[Candle]:
    """Random-walk candles with volatility regimes. drift_std=0 means NO real momentum: a correct
    backtester should then show no edge (useful sanity check)."""
    rng = random.Random(seed)
    start = start or (time.time() // 900 * 900 - days * 86400)
    n = int(days * 1440)
    price, mu, regime = 95000.0, 0.0, 1.0
    kappa = math.log(2) / (8 * 60)
    candles = []
    sub = 12
    dt = 60 / sub
    for i in range(n):
        if rng.random() < 1 / 600:
            regime = rng.choice([0.5, 1.0, 1.0, 1.8])
        o = h = l = price
        for _ in range(sub):
            eta = drift_std_bps_per_min * math.sqrt(2 * kappa)
            mu += -kappa * mu * dt + eta * math.sqrt(dt) * rng.gauss(0, 1)
            sig = base_vol_bps_per_min * regime / math.sqrt(60) / 1e4
            price *= math.exp(mu / 60 / 1e4 * dt + sig * math.sqrt(dt) * rng.gauss(0, 1))
            h, l = max(h, price), min(l, price)
        candles.append(Candle(start + i * 60, round(o, 2), round(h, 2), round(l, 2), round(price, 2),
                              round(rng.uniform(5, 40), 3)))
    return candles


async def fetch_kalshi_history(client, series: str, start: float, end: float, cache_dir: Path) -> dict[float, dict]:
    """Settled BTC 15m markets with the quote at minute 3 (from 1-minute market candlesticks).
    Returns {open_ts: {ticker, result, strike, yes_bid, yes_ask, up_side}}. Best effort."""
    cache = cache_dir / f"kalshi_{series}_{int(start)}_{int(end)}.json"
    if cache.exists():
        return {float(k): v for k, v in json.loads(cache.read_text()).items()}
    markets, cursor = [], None
    while True:
        data = await client.get_markets(series, status="settled", limit=200, cursor=cursor,
                                        min_close_ts=int(start), max_close_ts=int(end))
        markets.extend(data.get("markets", []))
        cursor = data.get("cursor")
        if not cursor or not data.get("markets"):
            break
    log.info("kalshi: %d settled %s markets", len(markets), series)
    out = {}
    for i, raw in enumerate(markets):
        open_ts, close_ts = parse_iso(raw.get("open_time")), parse_iso(raw.get("close_time"))
        result = (raw.get("result") or "").lower()
        if not open_ts or result not in ("yes", "no"):
            continue
        try:
            cs = await client.get_market_candlesticks(series, raw["ticker"], int(open_ts), int(open_ts + 300), 1)
        except Exception as exc:  # noqa: BLE001
            log.debug("candlesticks failed for %s: %s", raw["ticker"], exc)
            continue
        target = open_ts + 180
        best = None
        for c in cs:
            end_ts = c.get("end_period_ts")
            if end_ts is not None and end_ts <= target + 1:
                best = c
        if not best:
            continue
        ya = price_field(best.get("yes_ask") or {}, "close")
        yb = price_field(best.get("yes_bid") or {}, "close")
        if ya is None or yb is None:
            continue
        st = (raw.get("strike_type") or "").lower()
        out[open_ts] = {"ticker": raw["ticker"], "result": result, "strike": raw.get("floor_strike"),
                        "yes_ask": ya, "yes_bid": yb, "close_ts": close_ts,
                        "up_side": "no" if st in ("less", "less_or_equal") else "yes"}
        if i % 50 == 0:
            log.info("kalshi candlesticks %d/%d", i, len(markets))
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(out))
    return out

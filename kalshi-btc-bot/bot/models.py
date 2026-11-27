"""Shared data types and Kalshi payload parsing (handles both legacy cents and newer *_dollars fields)."""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class Direction(str, Enum):
    UP = "UP"
    DOWN = "DOWN"
    NONE = "NONE"


class Action(str, Enum):
    BUY_UP = "BUY UP"
    BUY_DOWN = "BUY DOWN"
    SKIP = "SKIP"


def other_side(side: str) -> str:
    return "no" if side == "yes" else "yes"


@dataclass(slots=True)
class Tick:
    ts: float
    price: float
    size: float = 0.0
    aggressor: str | None = None  # "buy" | "sell" | None


@dataclass(slots=True)
class BookLevel:
    price: float  # dollars, 0-1
    qty: int


@dataclass
class OrderBook:
    """Kalshi books contain bids only. A YES ask at p is a NO bid at 1-p and vice versa."""
    yes_bids: list[BookLevel] = field(default_factory=list)  # sorted best (highest) first
    no_bids: list[BookLevel] = field(default_factory=list)
    ts: float = 0.0

    def bids(self, side: str) -> list[BookLevel]:
        return self.yes_bids if side == "yes" else self.no_bids

    def asks(self, side: str) -> list[BookLevel]:
        opp = self.no_bids if side == "yes" else self.yes_bids
        return [BookLevel(round(1 - lvl.price, 4), lvl.qty) for lvl in opp]  # best (lowest) first

    def best_bid(self, side: str) -> float | None:
        b = self.bids(side)
        return b[0].price if b else None

    def best_ask(self, side: str) -> float | None:
        a = self.asks(side)
        return a[0].price if a else None

    def spread(self, side: str) -> float | None:
        ask, bid = self.best_ask(side), self.best_bid(side)
        if ask is None:
            return None
        return round(ask - (bid if bid is not None else 0.0), 4)

    def depth_at_or_below(self, side: str, limit: float) -> int:
        return sum(l.qty for l in self.asks(side) if l.price <= limit + 1e-9)

    def walk(self, side: str, contracts: int, limit: float) -> tuple[int, float]:
        """Simulate buying up to `contracts` at prices <= limit. Returns (filled, avg_price)."""
        filled, notional = 0, 0.0
        for lvl in self.asks(side):
            if lvl.price > limit + 1e-9 or filled >= contracts:
                break
            take = min(lvl.qty, contracts - filled)
            filled += take
            notional += take * lvl.price
        return filled, (notional / filled if filled else 0.0)

    def to_dict(self) -> dict:
        return {
            "yes_bid": self.best_bid("yes"), "yes_ask": self.best_ask("yes"),
            "no_bid": self.best_bid("no"), "no_ask": self.best_ask("no"),
            "yes_depth": sum(l.qty for l in self.yes_bids), "no_depth": sum(l.qty for l in self.no_bids),
        }


@dataclass
class Market:
    ticker: str
    event_ticker: str
    open_ts: float
    close_ts: float
    strike: float | None
    status: str
    up_side: str = "yes"
    result: str | None = None
    title: str = ""
    yes_bid: float | None = None
    yes_ask: float | None = None
    raw: dict = field(default_factory=dict, repr=False)

    @property
    def duration(self) -> float:
        return self.close_ts - self.open_ts

    @property
    def down_side(self) -> str:
        return other_side(self.up_side)

    def side_for(self, direction: Direction) -> str:
        return self.up_side if direction == Direction.UP else self.down_side

    @property
    def is_settled(self) -> bool:
        return self.result in ("yes", "no")


# ---------------------------------------------------------------- parsing helpers

def parse_iso(ts: str | None) -> float | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(timezone.utc).timestamp()
    except ValueError:
        return None


def price_field(obj: dict, name: str) -> float | None:
    """Read a Kalshi price in dollars from `<name>_dollars` (string) or `<name>` (integer cents)."""
    if obj is None:
        return None
    v = obj.get(f"{name}_dollars")
    if v not in (None, ""):
        try:
            return float(v)
        except (TypeError, ValueError):
            pass
    v = obj.get(name)
    if v in (None, ""):
        return None
    try:
        return float(v) / 100.0
    except (TypeError, ValueError):
        return None


def count_field(obj: dict, name: str) -> float | None:
    v = obj.get(f"{name}_fp")
    if v in (None, ""):
        v = obj.get(name)
    if v in (None, ""):
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def infer_up_side(raw: dict, default: str) -> str:
    st = (raw.get("strike_type") or "").lower()
    if st in ("greater", "greater_or_equal", "above"):
        return "yes"
    if st in ("less", "less_or_equal", "below"):
        return "no"
    return default


def parse_market(raw: dict, default_up_side: str = "yes") -> Market:
    strike = raw.get("floor_strike")
    if strike in (None, "") and raw.get("cap_strike") not in (None, ""):
        strike = raw.get("cap_strike")
    result = (raw.get("result") or "").lower() or None
    return Market(
        ticker=raw["ticker"],
        event_ticker=raw.get("event_ticker", ""),
        open_ts=parse_iso(raw.get("open_time")) or 0.0,
        close_ts=parse_iso(raw.get("close_time")) or parse_iso(raw.get("expiration_time")) or 0.0,
        strike=float(strike) if strike not in (None, "") else None,
        status=(raw.get("status") or "").lower(),
        up_side=infer_up_side(raw, default_up_side),
        result=result if result in ("yes", "no") else None,
        title=raw.get("title", ""),
        yes_bid=price_field(raw, "yes_bid"),
        yes_ask=price_field(raw, "yes_ask"),
        raw=raw,
    )


def _levels(raw_levels, dollars: bool) -> list[BookLevel]:
    out = []
    for lvl in raw_levels or []:
        try:
            p, q = lvl[0], lvl[1]
            price = float(p) if dollars else float(p) / 100.0
            qty = int(float(q))
        except (TypeError, ValueError, IndexError):
            continue
        if qty > 0 and 0 < price < 1:
            out.append(BookLevel(round(price, 4), qty))
    out.sort(key=lambda l: l.price, reverse=True)
    return out


def parse_orderbook(payload: dict, ts: float = 0.0) -> OrderBook:
    ob = payload.get("orderbook_fp") or payload.get("orderbook") or {}
    if ob.get("yes_dollars") is not None or ob.get("no_dollars") is not None:
        yes, no = _levels(ob.get("yes_dollars"), True), _levels(ob.get("no_dollars"), True)
    else:
        yes, no = _levels(ob.get("yes"), False), _levels(ob.get("no"), False)
    return OrderBook(yes_bids=yes, no_bids=no, ts=ts)


def norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

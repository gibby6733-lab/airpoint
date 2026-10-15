"""Broker adapter contract (platform-agnostic) and a bar-replay ``PaperBroker``.

The live layer never talks to a trading platform directly; it codes against the
:class:`Broker` protocol below. A real adapter (NinjaTrader 8 / Tradovate / ...) implements
the same nine methods; see ``docs/LIVE.md``.

Event model
-----------
* Bars are pushed to ``subscribe_bars`` callbacks once they are *complete* (``Bar.time`` is
  the bar OPEN time, like the research Bars format).
* Executions are pushed to ``subscribe_fills`` callbacks synchronously, as soon as they
  happen. Every fill of a bar is delivered BEFORE that bar's completion callback, so on a
  bar callback the broker position already reflects everything that happened inside it.
* ``place_bracket`` = market entry + protective stop + profit-target limit (OCO). The
  returned id identifies the bracket; ``modify_stop(id, px)`` moves its stop leg.

PaperBroker fill semantics (identical to :mod:`propbot.backtest`)
----------------------------------------------------------------
* Orders placed during a bar callback (i.e. on bar ``i``'s close) are queued and fill at
  the OPEN of the next bar ``i+1``: market entries/exits with ``slippage_ticks`` against you.
* Bracket legs are live from the fill, so they are checked against the full range of the
  fill bar and every later bar. Stop first when a bar touches both legs. Stops fill at the
  stop price (or the bar open if it gapped through) minus slippage; targets fill exactly.
* Stop/target prices are rounded to the contract tick.
* Commission ``commission_rt * qty`` is charged per round trip, on the closing fill.
* Unfilled orders expire at the end of a session (a signal on the session's last bar
  never fills); a position still open after the session's last bar is closed at that bar's
  close minus slippage (reason ``"eod"``). The engine/guardian normally flatten at 15:55
  so this never triggers.
"""
from __future__ import annotations

import itertools
import math
from dataclasses import dataclass, field
from typing import Callable, Optional, Protocol, runtime_checkable

import numpy as np
import pandas as pd

from ..interfaces import ContractSpec

__all__ = ["Bar", "Fill", "Position", "Broker", "PaperBroker", "BarCallback", "FillCallback",
           "INTRABAR_REASONS"]

ET = "America/New_York"

#: fill reasons that happen *inside* a bar (resting orders) rather than at its open
INTRABAR_REASONS = frozenset({"stop", "target"})


@dataclass(frozen=True)
class Bar:
    time: pd.Timestamp            # bar OPEN time (tz-aware, America/New_York)
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0
    symbol: str = ""
    duration: pd.Timedelta = field(default=pd.Timedelta(minutes=1))

    @property
    def close_time(self) -> pd.Timestamp:
        return self.time + self.duration


@dataclass(frozen=True)
class Fill:
    order_id: str
    symbol: str
    time: pd.Timestamp       # paper: open time of the bar the fill happened in
    side: int                # +1 bought, -1 sold
    qty: int
    price: float
    reason: str              # "entry" | "exit" | "stop" | "target" | "eod"
    commission: float = 0.0  # informational ($, charged on the closing fill in paper)


@dataclass(frozen=True)
class Position:
    symbol: str
    qty: int = 0             # signed contracts
    avg_price: float = 0.0


BarCallback = Callable[[Bar], None]
FillCallback = Callable[[Fill], None]


@runtime_checkable
class Broker(Protocol):
    """What every platform adapter must implement (paper, NinjaTrader 8, Tradovate, ...)."""

    def connect(self) -> None:
        """Open the session / authenticate. Must be called before anything else."""

    def subscribe_bars(self, symbol: str, callback: BarCallback) -> None:
        """Call ``callback(bar)`` for every COMPLETED 1-minute bar of ``symbol``."""

    def subscribe_fills(self, callback: FillCallback) -> None:
        """Call ``callback(fill)`` for every execution, as soon as it happens."""

    def get_position(self, symbol: str) -> Position:
        """Current signed position and average price."""

    def get_account_balance(self) -> float:
        """Realised cash balance of the account ($)."""

    def place_bracket(self, symbol: str, side: int, qty: int, stop: Optional[float],
                      target: Optional[float]) -> str:
        """Market entry ``side`` (+1 buy / -1 sell) x ``qty`` with an attached stop-market and
        target-limit OCO. Returns an order id identifying the bracket."""

    def modify_stop(self, order_id: str, price: float) -> None:
        """Move the stop leg of bracket ``order_id`` to ``price``."""

    def flatten(self, symbol: str) -> None:
        """Cancel every working order of ``symbol`` and close the position at market."""

    def cancel_all(self, symbol: str) -> None:
        """Cancel every working order of ``symbol`` (the position is left as is)."""


def _round_tick(px: Optional[float], tick: float) -> Optional[float]:
    if px is None or (isinstance(px, float) and math.isnan(px)):
        return None
    return round(float(px) / tick) * tick


class PaperBroker:
    """Replays a Bars DataFrame bar by bar and simulates fills like :mod:`propbot.backtest`.

    Usage::

        broker = PaperBroker(bars, CONTRACTS["MNQ"], slippage_ticks=1)
        engine = LiveEngine(strategy, broker, guardian, CONTRACTS["MNQ"], qty=2)
        engine.start()      # connect + subscribe
        broker.run()        # replay every bar
        engine.finish()     # close the last session's books
    """

    def __init__(self, bars: pd.DataFrame, contract: ContractSpec, slippage_ticks: float = 1,
                 start_balance: float = 25_000.0, symbol: Optional[str] = None,
                 bar_duration: Optional[pd.Timedelta] = None):
        if bars.index.tz is None:
            bars = bars.tz_localize(ET)
        self.bars = bars
        self.contract = contract
        self.symbol = symbol or contract.symbol
        self.tick = contract.tick_size
        self.slip = float(slippage_ticks) * contract.tick_size
        self.balance = float(start_balance)
        if bar_duration is None:
            from ..data import infer_bar_duration
            bar_duration = infer_bar_duration(bars.index)
        self.bar_duration = pd.Timedelta(bar_duration)
        self.connected = False
        self.fills: list[Fill] = []
        self.rejections: list[dict] = []
        self.orders_log: list[dict] = []
        self._bar_cbs: list[BarCallback] = []
        self._fill_cbs: list[FillCallback] = []
        self._ids = itertools.count(1)
        self._pending: list[dict] = []   # queued for the next bar's open
        self._side = 0
        self._qty = 0
        self._entry = 0.0
        self._bracket: Optional[dict] = None  # live legs of the open position
        self._now: Optional[Bar] = None

    # ------------------------------------------------------------------ Broker protocol
    def connect(self) -> None:
        self.connected = True

    def subscribe_bars(self, symbol: str, callback: BarCallback) -> None:
        self._check_symbol(symbol)
        self._bar_cbs.append(callback)

    def subscribe_fills(self, callback: FillCallback) -> None:
        self._fill_cbs.append(callback)

    def get_position(self, symbol: str) -> Position:
        self._check_symbol(symbol)
        return Position(self.symbol, self._side * self._qty, self._entry if self._qty else 0.0)

    def get_account_balance(self) -> float:
        return self.balance

    def place_bracket(self, symbol: str, side: int, qty: int, stop: Optional[float],
                      target: Optional[float]) -> str:
        self._check_symbol(symbol)
        if side not in (1, -1):
            raise ValueError(f"side must be +1/-1, got {side}")
        if int(qty) < 1:
            raise ValueError(f"qty must be >= 1, got {qty}")
        oid = f"B{next(self._ids)}"
        order = dict(type="bracket", id=oid, side=int(side), qty=int(qty),
                     stop=_round_tick(stop, self.tick), target=_round_tick(target, self.tick))
        self._pending.append(order)
        self.orders_log.append(dict(order, placed_at=self._now.time if self._now else None))
        return oid

    def modify_stop(self, order_id: str, price: float) -> None:
        px = _round_tick(price, self.tick)
        if self._bracket is not None and self._bracket["id"] == order_id:
            self._bracket["stop"] = px
            return
        for o in self._pending:
            if o["type"] == "bracket" and o["id"] == order_id:
                o["stop"] = px
                return
        raise KeyError(f"no working bracket {order_id!r}")

    def flatten(self, symbol: str) -> None:
        self.cancel_all(symbol)
        oid = f"X{next(self._ids)}"
        self._pending.append(dict(type="exit", id=oid))
        self.orders_log.append(dict(type="exit", id=oid,
                                    placed_at=self._now.time if self._now else None))

    def cancel_all(self, symbol: str) -> None:
        self._check_symbol(symbol)
        self._pending = []
        if self._bracket is not None:
            self._bracket["stop"] = None
            self._bracket["target"] = None

    # ------------------------------------------------------------------ replay
    def run(self) -> None:
        """Replay every bar: fills at the open, bracket legs intrabar, then bar callbacks."""
        if not self.connected:
            raise RuntimeError("PaperBroker.run() before connect()")
        bars = self.bars
        n = len(bars)
        if n == 0:
            return
        o = bars["open"].to_numpy(dtype=float)
        h = bars["high"].to_numpy(dtype=float)
        lo = bars["low"].to_numpy(dtype=float)
        c = bars["close"].to_numpy(dtype=float)
        v = bars["volume"].to_numpy(dtype=float) if "volume" in bars else np.zeros(n)
        idx = bars.index
        day = idx.normalize().tz_localize(None).asi8
        for k in range(n):
            if k > 0 and day[k] != day[k - 1]:
                self._pending = []  # orders do not carry over a session boundary
            bar = Bar(idx[k], o[k], h[k], lo[k], c[k], v[k], self.symbol, self.bar_duration)
            self._now = bar
            self._fill_pending(bar)
            self._check_bracket(bar)
            for cb in list(self._bar_cbs):
                cb(bar)
            last_of_day = k == n - 1 or day[k + 1] != day[k]
            if last_of_day and self._qty:
                self._close(bar.close - self._side * self.slip, bar, "eod",
                            self._bracket["id"] if self._bracket else "EOD")
        self._pending = []

    # ------------------------------------------------------------------ internals
    def _check_symbol(self, symbol: str) -> None:
        if symbol != self.symbol:
            raise ValueError(f"PaperBroker trades {self.symbol!r} only, got {symbol!r}")

    def _emit(self, fill: Fill) -> None:
        self.fills.append(fill)
        for cb in list(self._fill_cbs):
            cb(fill)

    def _close(self, px: float, bar: Bar, reason: str, order_id: str) -> None:
        side, qty, entry = self._side, self._qty, self._entry
        comm = self.contract.commission_rt * qty
        self.balance += (px - entry) * side * self.contract.point_value * qty - comm
        self._side, self._qty, self._entry = 0, 0, 0.0
        self._bracket = None
        self._emit(Fill(order_id, self.symbol, bar.time, -side, qty, px, reason, comm))

    def _fill_pending(self, bar: Bar) -> None:
        orders, self._pending = self._pending, []
        for od in orders:
            if od["type"] == "exit":
                if self._qty:
                    self._close(bar.open - self._side * self.slip, bar, "exit", od["id"])
            elif od["type"] == "bracket":
                if self._qty:
                    self.rejections.append(dict(od, time=bar.time, why="position not flat"))
                    continue
                side = od["side"]
                self._side, self._qty = side, od["qty"]
                self._entry = bar.open + side * self.slip
                self._bracket = dict(id=od["id"], stop=od["stop"], target=od["target"])
                self._emit(Fill(od["id"], self.symbol, bar.time, side, od["qty"], self._entry,
                                "entry"))

    def _check_bracket(self, bar: Bar) -> None:
        if not self._qty or self._bracket is None:
            return
        side = self._side
        stop, target = self._bracket["stop"], self._bracket["target"]
        if side > 0:
            stop_hit = stop is not None and bar.low <= stop
            tgt_hit = target is not None and bar.high >= target
        else:
            stop_hit = stop is not None and bar.high >= stop
            tgt_hit = target is not None and bar.low <= target
        if stop_hit:  # stop wins ties with the target (conservative, as in the backtester)
            gap_px = min(bar.open, stop) if side > 0 else max(bar.open, stop)
            self._close(gap_px - side * self.slip, bar, "stop", self._bracket["id"])
        elif tgt_hit:
            self._close(target, bar, "target", self._bracket["id"])

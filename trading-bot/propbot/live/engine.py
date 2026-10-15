"""LiveEngine: wires strategy agent -> risk guardian -> broker, one completed bar at a time.

Per completed 1-minute bar (``Broker.subscribe_bars`` callback):

1. Bars outside ``[session_start, session_end)`` ET are ignored (RTH only, like research).
2. A new calendar date rolls the session: the previous one is booked into the EvalAccount
   (``guardian.end_session``), the strategy is ``reset()`` and the guardian recomputes
   today's budget / profit cap from the account (``room_today``).
3. The bar is appended to the session frame.
4. ``guardian.on_bar`` runs first (kill switch, 15:55 flatten, daily stop, floor, pass).
5. If the guardian allows it, ``strategy.on_bar(i, session_bars, position)`` is called and
   its Signal is routed: ``side=0`` -> ``guardian.submit_exit``; same side as the position
   -> ignored; otherwise ``guardian.submit_entry`` (which may veto/shrink, and sends the
   bracket). Orders go out on the bar's close and fill at the next bar's open.
6. On the bar that closes at ``session_end`` (16:00) with nothing open the day is booked
   immediately; otherwise it is booked at the next roll or on ``finish()``.

Fills (``Broker.subscribe_fills``) go straight to ``guardian.on_fill``.
"""
from __future__ import annotations

from typing import Callable, Optional

import numpy as np
import pandas as pd

from ..data import sessions
from ..interfaces import ContractSpec, DayResult, Signal, Strategy
from .broker import Bar, Broker, Fill
from .events import EventLog
from .guardian import RiskGuardian, _hhmm, _tod

__all__ = ["LiveEngine"]

ET = "America/New_York"
_COLS = ["open", "high", "low", "close", "volume"]


class LiveEngine:
    def __init__(self, strategy: Strategy, broker: Broker, guardian: RiskGuardian,
                 contract: ContractSpec, qty: int, symbol: Optional[str] = None, *,
                 session_start: str = "09:30", session_end: str = "16:00",
                 log: Optional[EventLog] = None,
                 on_day_end: Optional[Callable[[DayResult, dict], None]] = None):
        if qty < 1:
            raise ValueError("qty must be >= 1")
        self.strategy = strategy
        self.broker = broker
        self.guardian = guardian
        self.contract = contract
        self.qty = int(qty)
        self.symbol = symbol or contract.symbol
        self.session_start = _hhmm(session_start)
        self.session_end = _hhmm(session_end)
        self.log = log or guardian.log
        self.on_day_end = on_day_end
        self.days: list[DayResult] = []
        self.statuses: list[dict] = []
        self._date: Optional[pd.Timestamp] = None
        self._ended = True
        self._n = 0
        self._t = np.empty(0, dtype=np.int64)
        self._v = np.empty((0, 5), dtype=float)
        self._tz = None
        self.started = False

    # ------------------------------------------------------------------ lifecycle
    def start(self) -> None:
        """Connect, subscribe, and reconcile any position the broker already holds."""
        self.broker.connect()
        self.guardian.attach(self.broker, self.symbol)
        self.broker.subscribe_fills(self._on_fill)
        self.broker.subscribe_bars(self.symbol, self._on_bar)
        self.started = True
        pos = self.broker.get_position(self.symbol)
        day = self.guardian.day
        known = day.seg.side * day.seg.qty if (day is not None and day.seg is not None) else 0
        self._emit("engine_started", strategy=getattr(self.strategy, "name", "?"),
                   params=getattr(self.strategy, "params", {}), qty=self.qty,
                   symbol=self.symbol, broker_position=pos.qty,
                   broker_balance=self.broker.get_account_balance())
        if pos.qty != known:
            self._emit("position_mismatch", level="error", broker=pos.qty, ledger=known,
                       reason="unknown position at startup -> guardian flattens it")
            self.guardian._flatten("reconcile: unknown position at startup")

    def finish(self) -> None:
        """Book the current session (end of replay / shutdown after the close)."""
        if self._date is not None and not self._ended:
            self._end_session()

    def warmup(self, bars: pd.DataFrame) -> None:
        """Feed past sessions to the strategy (no orders) so indicators that carry across
        sessions are warm before going live. Call before ``start()``."""
        for _, sess in sessions(bars):
            self.strategy.reset()
            for i in range(len(sess)):
                self.strategy.on_bar(i, sess.iloc[: i + 1], 0)
        self._emit("warmup_done", bars=len(bars))

    # ------------------------------------------------------------------ helpers
    def _emit(self, event: str, level: str = "info", ts=None, **fields) -> None:
        self.log.emit("engine", event, ts=ts, level=level, **fields)

    def _frame(self) -> pd.DataFrame:
        n = self._n
        idx = pd.DatetimeIndex(self._t[:n].view("M8[ns]")).tz_localize("UTC").tz_convert(self._tz)
        idx.name = "time"
        return pd.DataFrame(self._v[:n], index=idx, columns=_COLS)

    def _append(self, bar: Bar) -> None:
        if self._n == len(self._t):
            cap = max(512, 2 * len(self._t))
            t = np.empty(cap, dtype=np.int64)
            v = np.empty((cap, 5), dtype=float)
            t[: self._n], v[: self._n] = self._t[: self._n], self._v[: self._n]
            self._t, self._v = t, v
        ts = pd.Timestamp(bar.time)
        if self._tz is None:
            self._tz = ts.tz or ET
        self._t[self._n] = ts.value
        self._v[self._n] = (bar.open, bar.high, bar.low, bar.close, bar.volume)
        self._n += 1

    # ------------------------------------------------------------------ sessions
    def _begin_session(self, date: pd.Timestamp) -> None:
        self._date = date
        self._ended = False
        self._n = 0
        self.strategy.reset()
        self.guardian.begin_session(date)
        self._emit("session_start", date=date)

    def _end_session(self) -> None:
        self._ended = True
        dr = self.guardian.end_session()
        if dr is None:
            return
        st = self.guardian.status()
        st["broker_balance"] = self.broker.get_account_balance()
        self.days.append(dr)
        self.statuses.append(st)
        self._emit("session_end", date=dr.date, pnl=dr.pnl, trades=len(dr.trades),
                   balance=st["balance"], floor=st["floor"], status=st["status"],
                   broker_balance=st["broker_balance"])
        if self.on_day_end is not None:
            self.on_day_end(dr, st)

    def on_clock(self, now: pd.Timestamp) -> None:
        """Forward a wall-clock tick to the guardian (live adapters: call every few seconds)."""
        self.guardian.on_clock(now)

    # ------------------------------------------------------------------ callbacks
    def _on_fill(self, fill: Fill) -> None:
        self.guardian.on_fill(fill)

    def _on_bar(self, bar: Bar) -> None:
        tod = _tod(bar.time)
        if tod < self.session_start or tod >= self.session_end:
            return
        ts = pd.Timestamp(bar.time)
        local = ts.tz_convert(ET) if ts.tzinfo is not None else ts
        date = local.normalize().tz_localize(None) if local.tzinfo is not None else local.normalize()
        if date != self._date:
            if self._date is not None and not self._ended:
                self._end_session()
            self._begin_session(date)
        if self._ended:
            return  # the session was already booked (bars after the close)

        self._append(bar)
        i = self._n - 1
        g = self.guardian
        g.on_bar(bar, self.broker.get_position(self.symbol))

        if g.strategy_enabled(bar):
            pos = self.broker.get_position(self.symbol)
            try:
                sig = self.strategy.on_bar(i, self._frame(), pos.qty)
            except Exception as exc:
                # a broken strategy must not leave risk on: flatten and stand down for the day
                self._emit("strategy_error", level="error", ts=bar.close_time,
                           reason=f"strategy.on_bar raised {exc!r}")
                g.lock_day("strategy_error")
                sig = None
            if sig is not None:
                self._route(sig, bar, pos.qty)

        if _tod(bar.close_time) >= self.session_end:
            if self.broker.get_position(self.symbol).qty == 0 and not g._working:
                self._end_session()

    def _route(self, sig: Signal, bar: Bar, position: int) -> None:
        now = bar.close_time
        self._emit("signal", ts=now, side=sig.side, stop=sig.stop, target=sig.target,
                   tag=sig.tag, position=position, close=bar.close)
        if sig.side == 0:
            if position != 0:
                self.guardian.submit_exit(f"strategy_exit:{sig.tag}" if sig.tag else "strategy_exit")
            return
        side = 1 if sig.side > 0 else -1
        if position != 0 and (position > 0) == (side > 0):
            return  # already positioned that way (the backtester ignores it too)
        self.guardian.submit_entry(now, side, self.qty, sig.stop, sig.target, bar.close,
                                   tag=sig.tag, position=self.broker.get_position(self.symbol))

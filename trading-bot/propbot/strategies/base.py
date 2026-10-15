"""Shared machinery for propbot strategies (implements the ``interfaces.Strategy`` protocol).

Design rules enforced here for every strategy:
  * Strictly no lookahead: ``on_bar`` only reads rows ``<= i`` of ``bars`` (by position), so it
    is safe even if handed a frame that extends past ``i``.
  * Incremental: each new row is ingested once into per-session state (O(1) per bar); if ``i``
    jumps forward, the skipped rows are ingested (but no signals are produced for them).
  * Entries only when flat (no pyramiding / averaging down / reversal), at most
    ``max_trades`` entries per session, only inside [start, cutoff) by bar OPEN time.
  * Every entry carries a stop on the correct side of the signal bar's close (and a target on
    the other side); stops are rounded to the tick *away* from price.
  * Optional time exit: once a bar opens at/after ``exit_time`` any open position is flattened.
  * Cross-session state (prior-day levels, rolling day ranges) is updated in ``end_session``
    from the finished session's bars only -- i.e. strictly past data.
"""
from __future__ import annotations

import math
from typing import List, Optional

import pandas as pd

from ..interfaces import Signal
from .indicators import WilderATR, hhmm

SESSION_OPEN = 9 * 60 + 30
_PER_MIN = {"s": 60, "ms": 60_000, "us": 60_000_000, "ns": 60_000_000_000}


class BaseStrategy:
    name: str = "base"
    #: every accepted parameter with its default; subclasses extend this dict.
    default_params: dict = {
        "start": "09:30",       # earliest bar-open time an entry may be signalled
        "cutoff": "11:30",      # no entries on bars opening at/after this time
        "exit_time": "15:50",   # flatten any open position on bars opening at/after this
        "max_trades": 2,        # entries per session
        "atr_len": 14,          # 1-min Wilder ATR length (session-local)
        "tick": 0.25,
    }

    def __init__(self, **params):
        allowed = set(self.default_params)
        unknown = set(params) - allowed
        if unknown:
            raise TypeError(f"{type(self).__name__}: unknown params {sorted(unknown)}")
        self.params = {**self.default_params, **params}
        p = self.params
        self.tick = float(p["tick"])
        self._start_min = hhmm(p["start"])
        self._cutoff_min = hhmm(p["cutoff"])
        self._exit_min = hhmm(p["exit_time"]) if p["exit_time"] is not None else 10 ** 6
        self._max_trades = int(p["max_trades"])
        self._cols_obj = None
        self._col_pos = None
        self.init_state()
        self._last_i = -1
        self._new_session()

    # ------------------------------------------------------------------ hooks
    def init_state(self) -> None:
        """Cross-session state (survives reset)."""

    def session_reset(self) -> None:
        """Per-session state."""

    def end_session(self) -> None:
        """Called when a session with at least one bar finishes (before the next starts)."""

    def update(self, j: int) -> None:
        """Ingest row j (already appended to self.o/h/l/c/v/mins and ATR updated)."""

    def decide(self, i: int) -> Optional[Signal]:
        """Return an entry Signal for bar i, or None. Only called when flat & in window."""
        return None

    # ------------------------------------------------------------------ protocol
    def reset(self) -> None:
        if self._last_i >= 0:
            self.end_session()
        self._new_session()

    def _new_session(self) -> None:
        self._last_i = -1
        self._day = None
        self._off = None
        self.trades_today = 0
        self.last_entry_i = -10 ** 9
        self.bar_minutes = 1
        self.o: List[float] = []
        self.h: List[float] = []
        self.l: List[float] = []
        self.c: List[float] = []
        self.v: List[float] = []
        self.mins: List[int] = []
        self.atr = WilderATR(int(self.params["atr_len"]))
        self.session_reset()

    def _utc_offset(self, idx, i: int, per_min: int) -> int:
        off = idx[i].utcoffset()
        return 0 if off is None else int(off.total_seconds() // 60) * per_min

    def on_bar(self, i: int, bars: pd.DataFrame, position: int) -> Optional[Signal]:
        # Fast, lookahead-free access: raw epoch ints for the index and one 2-D ndarray view
        # for the OHLCV block; only rows <= i are ever read.
        idx = bars.index
        raw = idx.asi8
        per_min = _PER_MIN[getattr(idx, "unit", "ns")]
        if self._off is None:
            self._off = self._utc_offset(idx, i, per_min)
        day = ((raw[i] + self._off) // per_min) // 1440
        if self._day is not None and day != self._day:
            # new session without an explicit reset(): roll over safely
            self.reset()
            self._off = self._utc_offset(idx, i, per_min)
            day = ((raw[i] + self._off) // per_min) // 1440
        if i <= self._last_i:
            return None  # already processed this bar
        self._day = day
        cols = bars.columns
        if cols is not self._cols_obj:
            self._cols_obj = cols
            self._col_pos = [cols.get_loc(k) for k in ("open", "high", "low", "close", "volume")]
        vals = bars.to_numpy()
        po, ph, pl, pc, pv = self._col_pos
        off = self._off
        for j in range(self._last_i + 1, i + 1):
            m = int(((raw[j] + off) // per_min) % 1440)
            if len(self.mins) == 1:
                self.bar_minutes = max(1, m - self.mins[0])
            self.mins.append(m)
            row = vals[j]
            hj, lj, cj = float(row[ph]), float(row[pl]), float(row[pc])
            self.o.append(float(row[po]))
            self.h.append(hj)
            self.l.append(lj)
            self.c.append(cj)
            self.v.append(float(row[pv]))
            self.atr.update(hj, lj, cj)
            self._last_i = j
            self.update(j)

        minute = self.mins[-1]
        if position != 0:
            if minute >= self._exit_min:
                return Signal(0, tag=f"{self.name}_time_exit")
            return None
        if (self.trades_today >= self._max_trades or minute < self._start_min
                or minute >= self._cutoff_min or minute >= self._exit_min):
            return None
        sig = self.decide(i)
        if sig is not None and sig.side != 0:
            self.trades_today += 1
            self.last_entry_i = i
        return sig

    # ------------------------------------------------------------------ helpers
    def entry(self, side: int, stop: float, target: Optional[float], tag: str) -> Optional[Signal]:
        """Build a validated entry signal relative to the current close; None if invalid."""
        close = self.c[-1]
        t = self.tick
        if stop is None or not math.isfinite(stop):
            return None
        if side > 0:
            stop = math.floor(stop / t + 1e-9) * t
            if not stop < close:
                return None
            if target is not None:
                target = math.ceil(target / t - 1e-9) * t
                if not target > close:
                    return None
        elif side < 0:
            stop = math.ceil(stop / t - 1e-9) * t
            if not stop > close:
                return None
            if target is not None:
                target = math.floor(target / t + 1e-9) * t
                if not target < close:
                    return None
        else:
            return None
        if target is not None and not math.isfinite(target):
            return None
        return Signal(side=int(side), stop=float(stop), target=None if target is None else float(target),
                      tag=f"{self.name}_{tag}")

    def r_target(self, side: int, stop: float, r: float) -> float:
        close = self.c[-1]
        return close + side * r * abs(close - stop)

    @property
    def atr_value(self) -> float:
        return self.atr.value if self.atr.value is not None else 0.0

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.params})"

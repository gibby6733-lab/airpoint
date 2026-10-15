"""Account-state agent: the persisted evaluation account plus today's trade ledger.

* :class:`DayLedger` turns broker fills into realised P&L, ``Trade`` records and the day's
  worst intraday (open + closed) P&L, exactly like :func:`propbot.backtest.run_session`
  books them, and produces the session's :class:`~propbot.interfaces.DayResult`.
* :class:`AccountState` wraps :class:`propbot.rules.EvalAccount` (balance, EOD high, trailing
  floor, best day, days traded, status, history) and the current ledger, and persists both
  to a JSON file after every change so a restart keeps the trailing floor, the consistency
  bookkeeping, the intraday P&L and any lock/halt.
"""
from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict, dataclass, replace
from typing import Optional

import pandas as pd

from ..interfaces import ContractSpec, DayResult, EvalRules, Trade
from ..rules import EvalAccount, EvalOptions
from .broker import INTRABAR_REASONS, Bar, Fill

__all__ = ["DayLedger", "AccountState", "Segment"]

STATE_VERSION = 1


def _ts(x) -> Optional[str]:
    return None if x is None else pd.Timestamp(x).isoformat()


def _from_ts(x) -> Optional[pd.Timestamp]:
    return None if x is None else pd.Timestamp(x)


@dataclass(eq=False)
class Segment:
    """One open position (single entry, possibly averaged into)."""
    side: int
    qty: int
    entry: float
    entry_time: pd.Timestamp
    stop: Optional[float]
    target: Optional[float]
    base_realized: float   # day's realised P&L when the position was opened
    tag: str = ""
    order_id: str = ""


class DayLedger:
    """Today's fills -> realised P&L, trades, worst intraday P&L (backtest bookkeeping)."""

    def __init__(self, date, contract: ContractSpec):
        self.date = pd.Timestamp(date).normalize()
        if self.date.tzinfo is not None:
            self.date = self.date.tz_localize(None)
        self.contract = contract
        self.realized = 0.0
        self.worst = 0.0
        self.trades: list[Trade] = []
        self.entries = 0              # filled entries
        self.approved_entries = 0     # entries approved by the guardian (filled or not)
        self.seg: Optional[Segment] = None
        self._bar_segs: list[Segment] = []
        self.locked = False
        self.lock_reason: Optional[str] = None
        self.lock_flatten = False
        self.flatten_done = False
        self.applied = False

    # ------------------------------------------------------------------ marks
    def open_pnl(self, price: float) -> float:
        """Net $ of closing the open position at ``price`` (commission included)."""
        s = self.seg
        if s is None:
            return 0.0
        c = self.contract
        return (price - s.entry) * s.side * c.point_value * s.qty - c.commission_rt * s.qty

    def mark_bar(self, bar: Bar) -> None:
        """Worst open+closed P&L inside ``bar`` for every position live during its range
        (adverse extreme clamped at the resting stop, as in the backtester)."""
        c = self.contract
        for s in self._bar_segs:
            if s.side > 0:
                adverse = bar.low if s.stop is None else max(bar.low, s.stop)
            else:
                adverse = bar.high if s.stop is None else min(bar.high, s.stop)
            val = (s.base_realized + (adverse - s.entry) * s.side * c.point_value * s.qty
                   - c.commission_rt * s.qty)
            self.worst = min(self.worst, val)
        self._bar_segs = [self.seg] if self.seg is not None else []

    # ------------------------------------------------------------------ fills
    def on_fill(self, fill: Fill, tag: str = "", exit_reason: Optional[str] = None,
                stop: Optional[float] = None, target: Optional[float] = None) -> Optional[Trade]:
        """Book a fill. Returns the completed Trade when it closes the position."""
        c = self.contract
        s = self.seg
        qty = int(fill.qty)
        trade = None
        if s is not None and fill.side == -s.side:
            q = min(qty, s.qty)
            pnl = (fill.price - s.entry) * s.side * c.point_value * q - c.commission_rt * q
            self.realized += pnl
            reason = exit_reason or fill.reason
            trade = Trade(s.entry_time, fill.time, s.side, q, s.entry, fill.price, pnl,
                          reason if not s.tag else f"{s.tag}|{reason}")
            self.trades.append(trade)
            if fill.reason != "target":   # the backtester does not re-mark after a target
                self.worst = min(self.worst, self.realized)
            if q == s.qty:
                # keep ``s`` intact: it may still be marked against this bar's range
                self.seg = None
                if fill.reason not in INTRABAR_REASONS:
                    # closed at the bar open (or after its close): not live during the range
                    self._bar_segs = [x for x in self._bar_segs if x is not s]
            else:
                self.seg = replace(s, qty=s.qty - q)
                self._bar_segs = [self.seg if x is s else x for x in self._bar_segs]
            qty -= q
        if qty > 0:
            if self.seg is not None and fill.side == self.seg.side:   # add to the position
                s = self.seg
                s.entry = (s.entry * s.qty + fill.price * qty) / (s.qty + qty)
                s.qty += qty
            else:
                self.seg = Segment(fill.side, qty, float(fill.price), fill.time, stop, target,
                                   self.realized, tag, fill.order_id)
                self.entries += 1
                self._bar_segs.append(self.seg)
        return trade

    # ------------------------------------------------------------------ results
    def traded(self) -> bool:
        return bool(self.trades) or self.seg is not None or self.realized != 0.0

    def to_day_result(self) -> DayResult:
        return DayResult(date=self.date, pnl=float(self.realized), trades=list(self.trades),
                         max_intraday_drawdown=min(float(self.worst), 0.0))

    # ------------------------------------------------------------------ persistence
    def to_dict(self) -> dict:
        seg = None
        if self.seg is not None:
            seg = asdict(self.seg)
            seg["entry_time"] = _ts(seg["entry_time"])
        trades = []
        for t in self.trades:
            d = dict(vars(t))
            d["entry_time"], d["exit_time"] = _ts(t.entry_time), _ts(t.exit_time)
            trades.append(d)
        return dict(date=_ts(self.date), realized=self.realized, worst=self.worst,
                    trades=trades, entries=self.entries, approved_entries=self.approved_entries,
                    seg=seg, locked=self.locked, lock_reason=self.lock_reason,
                    lock_flatten=self.lock_flatten, flatten_done=self.flatten_done,
                    applied=self.applied)

    @classmethod
    def from_dict(cls, d: dict, contract: ContractSpec) -> "DayLedger":
        led = cls(_from_ts(d["date"]), contract)
        led.realized = float(d["realized"])
        led.worst = float(d["worst"])
        led.trades = [Trade(_from_ts(t["entry_time"]), _from_ts(t["exit_time"]), int(t["side"]),
                            int(t["qty"]), float(t["entry"]), float(t["exit"]), float(t["pnl"]),
                            t.get("reason", "")) for t in d.get("trades", [])]
        led.entries = int(d.get("entries", 0))
        led.approved_entries = int(d.get("approved_entries", 0))
        if d.get("seg"):
            s = dict(d["seg"])
            s["entry_time"] = _from_ts(s["entry_time"])
            led.seg = Segment(**s)
            led._bar_segs = [led.seg]
        led.locked = bool(d.get("locked", False))
        led.lock_reason = d.get("lock_reason")
        led.lock_flatten = bool(d.get("lock_flatten", False))
        led.flatten_done = bool(d.get("flatten_done", False))
        led.applied = bool(d.get("applied", False))
        return led


_ACCOUNT_FIELDS = ("balance", "eod_high", "floor", "days_traded", "days_used", "best_day",
                   "status", "reason", "fail_reason", "consistency_extended")


class AccountState:
    """Persisted evaluation account + today's ledger + the guardian's halt flag."""

    def __init__(self, contract: ContractSpec, rules: EvalRules = EvalRules(),
                 options: Optional[EvalOptions] = None, path: Optional[str] = None):
        self.contract = contract
        self.account = EvalAccount(rules, options)
        self.path = path
        self.halted = False
        self.halt_reason: Optional[str] = None
        self.day: Optional[DayLedger] = None

    @property
    def rules(self) -> EvalRules:
        return self.account.rules

    # ------------------------------------------------------------------ (de)serialise
    def to_dict(self) -> dict:
        a = self.account
        acc = {k: getattr(a, k) for k in _ACCOUNT_FIELDS}
        hist = []
        for h in a.history:
            h = dict(h)
            h["date"] = _ts(h.get("date"))
            hist.append({k: (bool(v) if hasattr(v, "dtype") and v.dtype == bool else v)
                         for k, v in h.items()})
        acc["history"] = hist
        return dict(version=STATE_VERSION, contract=self.contract.symbol,
                    rules=asdict(a.rules), options=asdict(a.options), account=acc,
                    halted=self.halted, halt_reason=self.halt_reason,
                    day=self.day.to_dict() if self.day is not None else None)

    def restore(self, d: dict) -> None:
        a = self.account
        acc = d["account"]
        for k in _ACCOUNT_FIELDS:
            setattr(a, k, acc[k])
        a.balance, a.eod_high, a.floor, a.best_day = (float(a.balance), float(a.eod_high),
                                                      float(a.floor), float(a.best_day))
        a.days_traded, a.days_used = int(a.days_traded), int(a.days_used)
        a.history = []
        for h in acc.get("history", []):
            h = dict(h)
            h["date"] = _from_ts(h.get("date"))
            a.history.append(h)
        self.halted = bool(d.get("halted", False))
        self.halt_reason = d.get("halt_reason")
        self.day = DayLedger.from_dict(d["day"], self.contract) if d.get("day") else None

    def save(self) -> None:
        """Atomic write (temp file + rename). No-op without a path."""
        if not self.path:
            return
        path = os.path.abspath(self.path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        fd, tmp = tempfile.mkstemp(prefix=".state-", dir=os.path.dirname(path))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(self.to_dict(), fh, indent=1, default=str)
            os.replace(tmp, path)
        except BaseException:
            if os.path.exists(tmp):
                os.unlink(tmp)
            raise

    @classmethod
    def load(cls, path: str, contract: ContractSpec, rules: EvalRules = EvalRules(),
             options: Optional[EvalOptions] = None) -> "AccountState":
        """Load ``path`` if it exists, else a fresh account that will be saved there."""
        st = cls(contract, rules, options, path)
        if path and os.path.exists(path):
            with open(path, encoding="utf-8") as fh:
                d = json.load(fh)
            if d.get("contract") not in (None, contract.symbol):
                raise ValueError(f"state file {path} is for {d.get('contract')}, "
                                 f"not {contract.symbol}")
            if d.get("rules") and d["rules"] != asdict(rules):
                raise ValueError(f"state file {path} was written with different EvalRules: "
                                 f"{d['rules']} != {asdict(rules)}")
            st.restore(d)
        return st

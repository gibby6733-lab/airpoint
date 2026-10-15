"""RiskGuardian: the independent risk agent between the strategy and the broker.

The strategy never touches the broker. Every entry goes through
:meth:`RiskGuardian.submit_entry`, which may approve, shrink or veto it, and the guardian
watches every fill and every bar on its own, flattening and locking whenever a rule is in
danger. Its account knowledge comes from :class:`propbot.rules.EvalAccount` (persisted by
:class:`~propbot.live.state.AccountState`) and :func:`propbot.rules.room_today`.

Per session the guardian derives two numbers (logged as ``session_limits``):

* ``budget`` -- the most the day may lose, worst case:
  ``min(room_to_floor - safety_buffer, daily_loss_limit - safety_buffer, bot_daily_stop)``
  (the first two are ``room_today(account, safety_buffer)["max_loss_today"]``).
* ``profit_cap`` -- once the day's REALISED profit reaches it, no new entries:
  ``min(daily_profit_cap, consistency_cap_fraction * max_profit_today_for_consistency)``.

Entry checks (:meth:`submit_entry`), in order, each logged with a reason:
halted / locked for the day / kill switch -> hours (the fill, i.e. the next bar's open, must
be in ``[trade_start, last_entry_time)``) -> max entries per day -> a valid stop (if
``require_stop``) -> size vs ``max_minis`` / ``max_qty`` -> commission alone would breach the
budget -> stop risk ``qty * (|ref - stop| + risk_slippage_ticks*tick) * point_value + commission``
must keep the day's worst case above ``-budget`` -> realised profit below ``profit_cap``.
Size and stop-risk violations are rejected (``size_policy="reject"``) or the quantity is
reduced to the largest that fits (``size_policy="reduce"``).

Every fill (:meth:`on_fill`): after an entry the resting stop is tightened to the price at
which the day's P&L would hit ``-budget`` (``arm_daily_stop``; same formula and rounding as the
backtester's ``daily_stop``). A stop-out at that level, realised P&L <= ``-budget`` or
realised P&L >= ``profit_cap`` lock the day.

Every bar (:meth:`on_bar`), in order: halted -> flatten; kill-switch file present -> flatten +
halt; bar close >= ``flatten_time`` (15:55 ET) -> flatten; open+realised <= ``-budget`` ->
flatten + lock; equity <= floor + ``floor_buffer`` -> flatten + lock; pass reached intraday
(target + consistency + min days, counting today) -> flatten + lock; realised >= cap -> lock.

End of session (:meth:`end_session`): the day's ``DayResult`` is applied to the
``EvalAccount``; on PASSED the guardian halts with ``"PASSED — stop trading"``; on FAILED it
halts too. Halts persist across restarts (a kill-switch halt is cleared on restart only once
the STOP file has been removed).
"""
from __future__ import annotations

import math
import os
from dataclasses import dataclass, field
from typing import Optional

import pandas as pd

from ..interfaces import ContractSpec, DayResult, EvalRules
from ..rules import ACTIVE, EPS, FAILED, PASSED, EvalOptions, effective_target, room_today
from .broker import Bar, Broker, Fill, Position
from .events import EventLog
from .state import AccountState, DayLedger

__all__ = ["GuardianConfig", "Decision", "RiskGuardian", "PASSED_MSG", "KILL_SWITCH"]

ET = "America/New_York"
PASSED_MSG = "PASSED — stop trading"
KILL_SWITCH = "kill_switch"
SIZE_POLICIES = ("reject", "reduce")


def _hhmm(s: str) -> float:
    hh, mm = s.split(":")[:2]
    return int(hh) * 60 + int(mm)


def _tod(ts: pd.Timestamp) -> float:
    ts = pd.Timestamp(ts)
    if ts.tzinfo is not None:
        ts = ts.tz_convert(ET)
    return ts.hour * 60 + ts.minute + ts.second / 60.0


@dataclass
class GuardianConfig:
    rules: EvalRules = field(default_factory=EvalRules)
    options: EvalOptions = field(default_factory=EvalOptions)
    #: $ kept between the worst case and the trailing floor / the firm's DLL
    safety_buffer: float = 50.0
    #: the bot's own daily stop ($, positive). None = only the account limits.
    bot_daily_stop: Optional[float] = 300.0
    #: explicit daily profit cap ($); combined (min) with the consistency cap
    daily_profit_cap: Optional[float] = None
    use_consistency_cap: bool = True
    #: use this fraction of room_today's consistency-safe cap (e.g. 0.9 for margin)
    consistency_cap_fraction: float = 1.0
    #: include room-to-floor / DLL in the budget and watch the floor (False = bot stop only)
    enforce_account_limits: bool = True
    #: veto/shrink entries whose stop risk does not fit the remaining budget
    check_stop_risk: bool = True
    size_policy: str = "reject"            # "reject" | "reduce"
    risk_slippage_ticks: float = 2.0       # entry + stop slippage assumed in the risk estimate
    max_qty: Optional[int] = None          # bot cap on top of rules.max_minis
    max_trades_per_day: Optional[int] = None
    require_stop: bool = True
    trade_start: str = "09:30"             # earliest fill time for an entry
    last_entry_time: Optional[str] = None  # no entry fills at/after this (default flatten_time)
    flatten_time: Optional[str] = None     # default rules.flatten_time (15:55 ET)
    arm_daily_stop: bool = True            # tighten the resting stop to the budget level
    floor_buffer: Optional[float] = None   # default safety_buffer
    halt_on_pass: bool = True
    halt_on_fail: bool = True
    kill_switch_path: Optional[str] = "STOP"
    state_path: Optional[str] = None

    def __post_init__(self):
        if self.size_policy not in SIZE_POLICIES:
            raise ValueError(f"size_policy must be one of {SIZE_POLICIES}")


@dataclass
class Decision:
    action: str                 # "allow" | "reduce" | "reject"
    qty: int
    reason: str
    order_id: Optional[str] = None
    details: dict = field(default_factory=dict)

    @property
    def allowed(self) -> bool:
        return self.action in ("allow", "reduce")


class RiskGuardian:
    def __init__(self, contract: ContractSpec, config: Optional[GuardianConfig] = None,
                 state: Optional[AccountState] = None, log: Optional[EventLog] = None):
        self.contract = contract
        self.cfg = cfg = config or GuardianConfig()
        if state is None:
            if cfg.state_path:
                state = AccountState.load(cfg.state_path, contract, cfg.rules, cfg.options)
            else:
                state = AccountState(contract, cfg.rules, cfg.options)
        self.state = state
        self.log = log or EventLog()
        self.broker: Optional[Broker] = None
        self.symbol = contract.symbol
        self.flatten_min = _hhmm(cfg.flatten_time or cfg.rules.flatten_time)
        self.last_entry_min = _hhmm(cfg.last_entry_time) if cfg.last_entry_time else self.flatten_min
        self.start_min = _hhmm(cfg.trade_start)
        self.floor_buffer = cfg.safety_buffer if cfg.floor_buffer is None else cfg.floor_buffer
        self.budget = math.inf
        self.profit_cap = math.inf
        self.room: dict = {}
        self.now: Optional[pd.Timestamp] = None
        self._working: dict[str, dict] = {}   # approved brackets not filled yet
        self._orders: dict[str, dict] = {}    # every approved bracket: tag/stop/target
        self._pos_order: Optional[str] = None
        self._ds_armed = False
        self._exit_reason: Optional[str] = None
        if self.state.halted and self.state.halt_reason == KILL_SWITCH and not self._kill_switch():
            self._emit("halt_cleared", reason="kill-switch file removed since the halt; resuming")
            self.state.halted, self.state.halt_reason = False, None
            self.state.save()

    # ================================================================== plumbing
    def attach(self, broker: Broker, symbol: Optional[str] = None) -> None:
        self.broker = broker
        if symbol:
            self.symbol = symbol

    def _emit(self, event: str, level: str = "info", **fields) -> None:
        self.log.emit("guardian", event, ts=self.now, level=level, **fields)

    @property
    def account(self):
        return self.state.account

    @property
    def day(self) -> Optional[DayLedger]:
        return self.state.day

    def _kill_switch(self) -> bool:
        p = self.cfg.kill_switch_path
        return bool(p) and os.path.exists(p)

    def _position(self) -> Position:
        if self.broker is None:
            return Position(self.symbol)
        return self.broker.get_position(self.symbol)

    def _flatten(self, reason: str) -> bool:
        """Cancel working orders and close the position. Returns True if anything was sent."""
        pos = self._position()
        if pos.qty == 0 and not self._working:
            return False
        if self.broker is not None:
            self.broker.flatten(self.symbol)
        self._working.clear()
        self._exit_reason = reason
        self._emit("flatten", level="warning", reason=reason, position=pos.qty)
        return True

    def lock_day(self, reason: str, flatten: bool = True, **fields) -> None:
        day = self.day
        if day is not None and not day.locked:
            day.locked, day.lock_reason, day.lock_flatten = True, reason, flatten
            self._emit("lock_day", level="warning", reason=reason, flatten=flatten, **fields)
        if flatten:
            self._flatten(reason)
        self.state.save()

    def halt(self, reason: str, **fields) -> None:
        if not self.state.halted:
            self.state.halted, self.state.halt_reason = True, reason
            lvl = "critical" if reason != PASSED_MSG else "warning"
            self._emit("halt", level=lvl, reason=reason, **fields)
        self._flatten(reason)
        self.state.save()

    # ================================================================== session lifecycle
    def begin_session(self, date) -> None:
        date = pd.Timestamp(date).normalize()
        if date.tzinfo is not None:
            date = date.tz_localize(None)
        st = self.state
        if st.day is not None and not st.day.applied and st.day.date != date:
            self._emit("stale_day", level="warning", date=st.day.date,
                       reason="applying a session that was never closed (restart?)")
            self.end_session()
        if st.day is not None and st.day.date == date:
            if st.day.applied:
                self._emit("session_already_closed", level="warning", date=date,
                           reason="this session was already booked; no trading today")
                st.day.locked, st.day.lock_reason = True, "session_already_closed"
            else:
                self._emit("session_resumed", date=date, realized=st.day.realized,
                           locked=st.day.locked, reason="restored intraday state from disk")
        else:
            st.day = DayLedger(date, self.contract)
        self._working.clear()
        self._compute_limits()
        acc = self.account
        if acc.status == PASSED and self.cfg.halt_on_pass:
            self.halt(PASSED_MSG)
        elif acc.status == FAILED and self.cfg.halt_on_fail:
            self.halt(f"account failed ({acc.fail_reason})")
        if self.budget <= 0 and not st.day.locked:
            self.lock_day("no_risk_room", flatten=False, budget=self.budget)
        st.save()

    def _compute_limits(self) -> None:
        cfg = self.cfg
        rt = room_today(self.account, cfg.safety_buffer)
        budget = rt["max_loss_today"] if cfg.enforce_account_limits else math.inf
        if cfg.bot_daily_stop is not None:
            budget = min(budget, float(cfg.bot_daily_stop))
        cap = math.inf
        if cfg.daily_profit_cap is not None:
            cap = float(cfg.daily_profit_cap)
        if cfg.use_consistency_cap:
            cap = min(cap, rt["max_profit_today_for_consistency"] * cfg.consistency_cap_fraction)
        self.budget, self.profit_cap, self.room = budget, cap, rt
        self._emit("session_limits", date=self.day.date if self.day else None,
                   budget=budget, profit_cap=cap, balance=rt["balance"], floor=rt["floor"],
                   room_to_floor=rt["room_to_floor"], profit_needed=rt["profit_needed"],
                   effective_target=rt["effective_target"], days_traded=rt["days_traded"],
                   status=rt["status"],
                   reason="budget=min(room-buffer, DLL-buffer, bot stop); cap=min(explicit, consistency)")

    def end_session(self) -> Optional[DayResult]:
        """Book today's DayResult into the EvalAccount (idempotent)."""
        day = self.day
        if day is None:
            return None
        if day.applied:
            return day.to_day_result()
        if day.seg is not None:
            self._emit("open_position_at_close", level="error", position=day.seg.side * day.seg.qty,
                       reason="position still open when the session was booked; its P&L is "
                              "not in this DayResult")
        dr = day.to_day_result()
        acc = self.account
        acc.apply_day(dr)
        day.applied = True
        self._emit("day_closed", date=day.date, pnl=dr.pnl, trades=len(dr.trades),
                   max_intraday_drawdown=dr.max_intraday_drawdown, balance=acc.balance,
                   floor=acc.floor, best_day=acc.best_day, days_traded=acc.days_traded,
                   status=acc.status, reason=acc.reason or "active")
        if acc.status == PASSED and self.cfg.halt_on_pass:
            self.halt(PASSED_MSG, balance=acc.balance, profit=acc.profit)
        elif acc.status == FAILED and self.cfg.halt_on_fail:
            self.halt(f"account failed ({acc.fail_reason})", balance=acc.balance)
        self.state.save()
        return dr

    # ================================================================== queries
    def strategy_enabled(self, bar: Bar) -> bool:
        """Should the strategy see this bar? (Same as the backtester: never once the day is
        halted/locked, nor on bars opening at/after the flatten time.)"""
        day = self.day
        return (not self.state.halted and day is not None and not day.locked
                and _tod(bar.time) < self.flatten_min)

    def status(self) -> dict:
        acc, day = self.account, self.day
        return dict(date=day.date if day else None, day_pnl=day.realized if day else 0.0,
                    trades=len(day.trades) if day else 0,
                    locked=bool(day and day.locked), lock_reason=day.lock_reason if day else None,
                    balance=acc.balance, floor=acc.floor, room_to_floor=acc.balance - acc.floor,
                    profit=acc.profit, best_day=acc.best_day,
                    effective_target=acc.effective_target, days_traded=acc.days_traded,
                    days_used=acc.days_used, status=acc.status, reason=acc.reason,
                    halted=self.state.halted, halt_reason=self.state.halt_reason,
                    budget=self.budget, profit_cap=self.profit_cap)

    # ================================================================== entries / exits
    def _reject(self, reason: str, qty: int, **details) -> Decision:
        self._emit("entry_rejected", reason=reason, qty=qty, **details)
        return Decision("reject", 0, reason, details=details)

    def submit_entry(self, now: pd.Timestamp, side: int, qty: int, stop: Optional[float],
                     target: Optional[float], ref_price: float, tag: str = "",
                     position: Optional[Position] = None) -> Decision:
        """Vet an entry and, if approved, send the bracket. ``now`` is the expected fill time
        (the close of the signal bar = the next bar's open); ``ref_price`` the signal bar's
        close, used to estimate the entry price."""
        self.now = now
        cfg, c, day = self.cfg, self.contract, self.day
        side = 1 if side > 0 else -1
        req = int(qty)
        det = dict(side=side, requested_qty=req, stop=stop, target=target, ref_price=ref_price,
                   tag=tag)
        if position is None:
            position = self._position()
        if self.state.halted:
            return self._reject(f"halted: {self.state.halt_reason}", req, **det)
        if self._kill_switch():
            self.halt(KILL_SWITCH, path=cfg.kill_switch_path)
            return self._reject("kill switch file present", req, **det)
        if day is None:
            return self._reject("no active session", req, **det)
        if day.locked:
            return self._reject(f"locked for the day: {day.lock_reason}", req, **det)
        t = _tod(now)
        if t < self.start_min or t >= self.last_entry_min:
            return self._reject(f"outside allowed hours: fill at {pd.Timestamp(now).strftime('%H:%M')} "
                                f"not in [{cfg.trade_start}, "
                                f"{cfg.last_entry_time or cfg.flatten_time or cfg.rules.flatten_time})",
                                req, **det)
        if cfg.max_trades_per_day is not None and day.approved_entries >= cfg.max_trades_per_day:
            return self._reject(f"max trades per day reached ({cfg.max_trades_per_day})", req, **det)
        if stop is not None and not math.isfinite(stop):
            stop = None
        if stop is not None and (stop - ref_price) * side >= 0:
            return self._reject("stop on the wrong side of the price", req, **det)
        if cfg.require_stop and stop is None:
            return self._reject("entry without a protective stop", req, **det)
        if req < 1:
            return self._reject("qty < 1", req, **det)

        q, notes = req, []
        # ---- size limit (firm max minis, bot max qty)
        max_q = int(math.floor(cfg.rules.max_minis / c.mini_equivalent + EPS))
        if cfg.max_qty is not None:
            max_q = min(max_q, int(cfg.max_qty))
        if q > max_q:
            msg = (f"size {q} x {c.symbol} = {q * c.mini_equivalent:g} minis exceeds the limit "
                   f"({max_q} contracts: max_minis={cfg.rules.max_minis:g}"
                   + (f", max_qty={cfg.max_qty}" if cfg.max_qty is not None else "") + ")")
            if cfg.size_policy == "reject" or max_q < 1:
                return self._reject(msg, req, **det)
            notes.append(f"{msg} -> reduced to {max_q}")
            q = max_q

        # ---- risk vs today's remaining budget
        open_now = day.open_pnl(ref_price) if position.qty != 0 else 0.0
        realized_eff = day.realized + open_now
        budget = self.budget
        if realized_eff - c.commission_rt * q <= -budget + EPS:
            return self._reject(f"no room: day P&L {realized_eff:.2f} minus commission would breach "
                                f"the budget {-budget:.2f}", req, **det)
        risk_pc = None
        if cfg.check_stop_risk and stop is not None and math.isfinite(budget):
            dist = abs(ref_price - stop) + cfg.risk_slippage_ticks * c.tick_size
            risk_pc = dist * c.point_value + c.commission_rt
            worst = realized_eff - q * risk_pc
            det.update(risk_per_contract=risk_pc, budget=budget, day_pnl=realized_eff)
            if worst <= -budget + EPS:
                fit = int(math.floor((realized_eff + budget) / risk_pc - 1e-9))
                msg = (f"stop risk {q} x ${risk_pc:.2f} = ${q * risk_pc:.2f} would take the day to "
                       f"{worst:.2f} <= -budget {-budget:.2f} (room left ${realized_eff + budget:.2f})")
                if cfg.size_policy == "reject" or fit < 1:
                    return self._reject(msg, req, **det)
                notes.append(f"{msg} -> reduced to {fit}")
                q = min(q, fit)
        elif cfg.check_stop_risk and stop is None and math.isfinite(budget):
            return self._reject("cannot size an entry without a stop against a finite budget",
                                req, **det)
        if day.realized >= self.profit_cap - EPS:
            return self._reject(f"daily profit cap reached: realised {day.realized:.2f} >= "
                                f"{self.profit_cap:.2f} (consistency-safe)", req, **det)

        # ---- approved: reverse if needed, then send the bracket
        if position.qty != 0:
            self._flatten(f"reverse:{tag}")
        oid = None
        if self.broker is not None:
            try:
                oid = self.broker.place_bracket(self.symbol, side, q, stop, target)
            except Exception as exc:  # broker refused / connection error: never retry blindly
                self._emit("order_error", level="error", reason=f"place_bracket failed: {exc!r}",
                           qty=q, **det)
                return Decision("reject", 0, f"broker error: {exc!r}", details=det)
            info = dict(tag=tag, stop=stop, target=target, side=side, qty=q)
            self._working[oid] = info
            self._orders[oid] = info
        day.approved_entries += 1
        action = "reduce" if q < req else "allow"
        reason = "; ".join(notes) if notes else "within limits"
        self._emit("entry_approved" if action == "allow" else "entry_reduced", reason=reason,
                   qty=q, order_id=oid, **det)
        self.state.save()
        return Decision(action, q, reason, oid, det)

    def submit_exit(self, reason: str = "strategy_exit") -> bool:
        """Exits are never vetoed."""
        return self._flatten(reason)

    # ================================================================== fills
    def on_fill(self, fill: Fill) -> None:
        self.now = fill.time
        day = self.day
        if day is None:
            self._emit("fill_outside_session", level="error", order_id=fill.order_id,
                       reason="fill received with no active session; not booked")
            return
        info = self._orders.get(fill.order_id, {})
        was_flat = day.seg is None
        exit_reason = None
        if not was_flat and fill.side == -day.seg.side:
            if fill.reason == "stop" and self._ds_armed:
                exit_reason = "daily_stop"
            elif fill.reason == "exit" and self._exit_reason:
                exit_reason = self._exit_reason
        trade = day.on_fill(fill, tag=info.get("tag", ""), exit_reason=exit_reason,
                            stop=info.get("stop"), target=info.get("target"))
        self._emit("fill", order_id=fill.order_id, side=fill.side, qty=fill.qty,
                   price=fill.price, fill_reason=fill.reason, realized=day.realized,
                   trade_pnl=trade.pnl if trade else None)
        if trade is not None:
            self._ds_armed = False
            if day.seg is None:
                self._pos_order = None
                self._exit_reason = None
            if exit_reason == "daily_stop":
                self.lock_day("daily_stop_hit", flatten=False, realized=day.realized)
            if day.realized <= -self.budget + EPS:
                self.lock_day("daily_stop", flatten=False, realized=day.realized,
                              budget=self.budget)
            if day.realized >= self.profit_cap - EPS:
                self.lock_day("profit_cap", flatten=False, realized=day.realized,
                              cap=self.profit_cap)
        if was_flat and day.seg is not None:   # a new position: arm the budget stop
            self._working.pop(fill.order_id, None)
            self._pos_order = fill.order_id
            self._arm_daily_stop()
        self.state.save()

    def _arm_daily_stop(self) -> None:
        cfg, c, s = self.cfg, self.contract, self.day.seg
        self._ds_armed = False
        if not cfg.arm_daily_stop or not math.isfinite(self.budget):
            return
        mult = c.point_value * s.qty
        comm = c.commission_rt * s.qty
        ds = s.entry - s.side * (self.budget + s.base_realized - comm) / mult
        tick = c.tick_size
        ds = math.ceil(ds / tick - EPS) * tick if s.side > 0 else math.floor(ds / tick + EPS) * tick
        if s.stop is None or (ds >= s.stop if s.side > 0 else ds <= s.stop):
            old = s.stop
            if self.broker is not None and ds != old:
                self.broker.modify_stop(s.order_id, ds)
            s.stop = ds
            self._ds_armed = True
            self._emit("stop_tightened", order_id=s.order_id, old_stop=old, new_stop=ds,
                       reason=f"resting stop moved to the daily budget level (-{self.budget:.2f})")

    # ================================================================== wall clock
    def on_clock(self, now: pd.Timestamp) -> None:
        """Time-only checks (kill switch, hard flatten time) for a live adapter to call from a
        timer every few seconds, so a stalled bar feed cannot keep a position past 15:55."""
        self.now = now
        day = self.day
        if self.state.halted:
            if self._position().qty != 0 or self._working:
                self._flatten(f"halted: {self.state.halt_reason}")
            return
        if self._kill_switch():
            self.halt(KILL_SWITCH, path=self.cfg.kill_switch_path)
            return
        if day is not None and not day.flatten_done and _tod(now) >= self.flatten_min:
            day.flatten_done = True
            self._emit("flatten_time", reason="hard flat time reached (clock)")
            self._flatten("flatten_time")
            self.state.save()

    # ================================================================== bars
    def on_bar(self, bar: Bar, position: Optional[Position] = None) -> None:
        """Called on every completed bar, after its fills and before the strategy."""
        self.now = bar.close_time
        day = self.day
        if day is None:
            return
        day.mark_bar(bar)
        if position is None:
            position = self._position()
        pos = position.qty
        if self.state.halted:
            if pos != 0 or self._working:
                self._flatten(f"halted: {self.state.halt_reason}")
            return
        if self._kill_switch():
            self.halt(KILL_SWITCH, path=self.cfg.kill_switch_path)
            return
        if not day.flatten_done and _tod(bar.close_time) >= self.flatten_min:
            day.flatten_done = True
            self._emit("flatten_time", reason=f"hard flat by {self.cfg.flatten_time or self.cfg.rules.flatten_time} ET",
                       position=pos)
            self._flatten("flatten_time")
            self.state.save()
        open_pnl = day.open_pnl(bar.close)
        day_pnl = day.realized + open_pnl
        acc = self.account
        if not day.locked:
            if day_pnl <= -self.budget + EPS:
                self.lock_day("daily_stop", day_pnl=day_pnl, budget=self.budget)
            elif (self.cfg.enforce_account_limits
                  and acc.balance + day_pnl <= acc.floor + self.floor_buffer + EPS):
                self.lock_day("floor_proximity", equity=acc.balance + day_pnl, floor=acc.floor,
                              buffer=self.floor_buffer)
            elif self.cfg.halt_on_pass and self._pass_reached(day_pnl):
                self._emit("pass_reached_intraday", level="warning", day_pnl=day_pnl,
                           reason="target + consistency + min days met if flat now; flattening")
                self.lock_day("pass_reached", day_pnl=day_pnl)
            elif day.realized >= self.profit_cap - EPS:
                self.lock_day("profit_cap", flatten=False, realized=day.realized,
                              cap=self.profit_cap)
        elif day.lock_flatten and (pos != 0 or self._working):
            self._flatten(f"locked: {day.lock_reason}")

    def _pass_reached(self, day_pnl: float) -> bool:
        acc = self.account
        if day_pnl <= 0 or acc.status != ACTIVE:
            return False
        best = max(acc.best_day, day_pnl)
        profit = acc.profit + day_pnl
        return (profit >= effective_target(acc.rules, best, acc.options) - EPS
                and acc.days_traded + 1 >= acc.rules.min_days)

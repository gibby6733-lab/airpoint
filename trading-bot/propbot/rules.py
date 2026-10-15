"""Prop-firm evaluation rule engine (Lucid Trading 25K, EOD trailing drawdown variant).

This module is the *scalar, readable reference implementation* of the evaluation rules.
``propbot.montecarlo.simulate_paths`` is a vectorised re-implementation of exactly the same
logic; ``tests/test_montecarlo.py`` checks that both agree path-for-path.

Rules as modelled (``EvalRules`` defaults in brackets)
------------------------------------------------------
* Start balance [$25,000]; profit target [$1,250]; ``min_days`` traded days [2].
* **EOD trailing max loss** [$1,000]: ``floor = (highest END-OF-DAY balance so far) - max_loss``.
  The floor starts at ``start_balance - max_loss`` (24,000) and is only updated at the end of
  each day; it never moves down. If ``trailing_lock_at`` is set, the floor stops rising once it
  reaches that balance: ``floor = max(floor, min(eod_high - max_loss, trailing_lock_at))``.
* **Breach**: the account fails if the balance *including open P&L* touches the floor at any
  time. Intraday open P&L is modelled through ``DayResult.max_intraday_drawdown``, interpreted
  as the *lowest cumulative (open + closed) P&L of the day relative to the start-of-day
  balance* (<= 0). Breach test: ``start_of_day_balance + intraday_low <= floor`` ("touch" is a
  breach, hence ``<=``). The intraday low is clamped to ``min(max_intraday_drawdown, pnl, 0)``
  because the day's close is itself a point on the path.
* **Daily loss limit (DLL)** [$600]: a day is "DLL-hit" when ``intraday_low <= -DLL``.

  - Soft (default, ``dll_is_hard_breach=False``, Lucid behaviour): trading stops for the day but
    the account is *not* failed.
  - Hard (``dll_is_hard_breach=True``): a DLL hit fails the account with reason
    ``"daily_loss_limit"``.
  - ``dll_flatten_at_limit`` decides what the DLL-hit day's P&L is:

    * ``False`` (default for DayResults coming from the backtester): the backtester already
      stopped the day, so the realised ``pnl`` / ``max_intraday_drawdown`` are recorded as-is.
    * ``True`` (default for the synthetic days built in ``montecarlo``/``sizing``, which do not
      embed the firm DLL): the firm liquidates exactly at the limit, so the day's effective P&L
      and intraday low both become ``-DLL`` (no gap-through modelled). Because the floor test
      then uses ``-DLL``, a soft DLL acts as a protective stop whenever ``balance - floor > DLL``.

  The trailing-floor breach takes precedence over the DLL when both occur on the same day.
* **Consistency** [50%]: when the target is reached, the largest single *winning* day must be
  ``<= consistency * total profit``. ``consistency_mode``:

  - ``"extend"`` (default, how Lucid applies it): the account does NOT fail; it simply cannot pass
    until the rule is satisfied, i.e. the *effective target* becomes
    ``max(profit_target, best_day / consistency)`` (2x the largest day at 50%). Every later day
    can still breach the floor. A pass that needed this is reported with reason
    ``"passed_after_consistency_extension"``.
  - ``"fail"``: reaching the target (with ``min_days`` met) while inconsistent fails the account
    (reason ``"consistency"``).
  - ``"ignore"``: no consistency rule.

  Note: with a 50% rule any pass already needs >= 2 winning days, so ``min_days=2`` is mostly
  implied by consistency.
* The pass check is done at end of day only (balance after the day's realised P&L).
* A "traded day" is one with any trade, non-zero P&L or a non-zero intraday excursion. Untraded
  days consume calendar days (``days_used``) but do not count toward ``min_days``.

``EvalRules`` is frozen and owned by ``interfaces.py``; the behavioural switches above live in
``EvalOptions`` (they would naturally belong in ``EvalRules``).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field, replace
from typing import Optional, Sequence

from .interfaces import DayResult, EvalRules

ACTIVE = "active"
PASSED = "passed"
FAILED = "failed"

CONSISTENCY_MODES = ("extend", "fail", "ignore")

# reason strings
R_PASSED = "passed"
R_PASSED_EXT = "passed_after_consistency_extension"
R_MAX_LOSS = "max_loss"
R_DLL = "daily_loss_limit"
R_CONSISTENCY = "consistency"
R_TIMEOUT = "timeout"

EPS = 1e-9  # float tolerance for $ comparisons


@dataclass(frozen=True)
class EvalOptions:
    """Behavioural switches not covered by ``EvalRules`` (see module docstring)."""
    dll_is_hard_breach: bool = False
    dll_flatten_at_limit: bool = False
    consistency_mode: str = "extend"

    def __post_init__(self):
        if self.consistency_mode not in CONSISTENCY_MODES:
            raise ValueError(f"consistency_mode must be one of {CONSISTENCY_MODES}, "
                             f"got {self.consistency_mode!r}")


def resolve_options(options: Optional[EvalOptions] = None, **overrides) -> EvalOptions:
    """``options`` (or defaults) with keyword overrides applied, e.g. ``dll_is_hard_breach=True``."""
    opts = options if options is not None else EvalOptions()
    return replace(opts, **overrides) if overrides else opts


def consistency_active(rules: EvalRules, options: EvalOptions) -> bool:
    c = rules.consistency
    return options.consistency_mode != "ignore" and c is not None and 0.0 < c < 1.0


def effective_target(rules: EvalRules, best_day: float, options: Optional[EvalOptions] = None) -> float:
    """Total profit needed to pass given the largest winning day so far.

    With the consistency rule in "extend" mode this is ``max(target, best_day / consistency)``.
    """
    opts = options or EvalOptions()
    if not consistency_active(rules, opts) or best_day <= 0:
        return rules.profit_target
    return max(rules.profit_target, best_day / rules.consistency)


def day_intraday_low(day: DayResult) -> float:
    """Lowest cumulative P&L of the day vs start-of-day balance: ``min(mdd, pnl, 0)``."""
    mdd = float(day.max_intraday_drawdown)
    if mdd > 1e-6:
        raise ValueError(f"DayResult.max_intraday_drawdown must be <= 0 (got {mdd}) for {day.date}")
    return min(mdd, float(day.pnl), 0.0)


def day_traded(day: DayResult) -> bool:
    return bool(day.trades) or float(day.pnl) != 0.0 or float(day.max_intraday_drawdown) != 0.0


class EvalAccount:
    """Stateful evaluation account. Feed it one ``DayResult`` per session via ``apply_day``.

    Attributes: ``balance``, ``floor``, ``eod_high``, ``days_traded``, ``days_used`` (calendar
    days applied, traded or not), ``best_day`` (largest winning day, 0 if none), ``status``
    ("active" / "passed" / "failed"), ``reason``, ``fail_reason`` (None unless failed),
    ``consistency_extended`` (target was reached while inconsistent at least once),
    ``history`` (one dict per applied day).
    """

    def __init__(self, rules: EvalRules = EvalRules(), options: Optional[EvalOptions] = None,
                 **overrides):
        self.rules = rules
        self.options = resolve_options(options, **overrides)
        self.balance = float(rules.start_balance)
        self.eod_high = float(rules.start_balance)
        self.floor = float(rules.start_balance - rules.max_loss)
        self.days_traded = 0
        self.days_used = 0
        self.best_day = 0.0
        self.status = ACTIVE
        self.reason: Optional[str] = None
        self.fail_reason: Optional[str] = None
        self.consistency_extended = False
        self.history: list[dict] = []

    # ------------------------------------------------------------------ derived state
    @property
    def profit(self) -> float:
        return self.balance - self.rules.start_balance

    @property
    def effective_target(self) -> float:
        return effective_target(self.rules, self.best_day, self.options)

    def is_consistent(self) -> bool:
        if not consistency_active(self.rules, self.options):
            return True
        return self.profit > 0 and self.best_day <= self.rules.consistency * self.profit + EPS

    # ------------------------------------------------------------------ transitions
    def _fail(self, reason: str) -> None:
        self.status = FAILED
        self.reason = reason
        self.fail_reason = reason

    def apply_day(self, day: DayResult) -> str:
        """Apply one session's result; returns the new status. No-op once passed/failed."""
        if self.status != ACTIVE:
            return self.status
        r, o = self.rules, self.options
        start = self.balance
        floor_before = self.floor
        pnl = float(day.pnl)
        low = day_intraday_low(day)
        traded = day_traded(day)
        self.days_used += 1
        if traded:
            self.days_traded += 1

        dll = r.daily_loss_limit
        dll_hit = dll is not None and low <= -dll + EPS
        pnl_eff, low_eff = pnl, low
        if dll_hit and o.dll_flatten_at_limit:
            pnl_eff, low_eff = -float(dll), -float(dll)

        if start + low_eff <= floor_before + EPS:
            # touched the trailing floor intraday -> liquidated at the floor
            self.balance = floor_before
            self._fail(R_MAX_LOSS)
        elif dll_hit and o.dll_is_hard_breach:
            self.balance = start + pnl_eff
            self._fail(R_DLL)
        else:
            self.balance = start + pnl_eff
            if pnl_eff > self.best_day:
                self.best_day = pnl_eff
            if self.balance <= floor_before + EPS:  # unreachable given low <= pnl; kept as a guard
                self._fail(R_MAX_LOSS)
            else:
                # EOD trailing update (floor never decreases)
                self.eod_high = max(self.eod_high, self.balance)
                new_floor = self.eod_high - r.max_loss
                if r.trailing_lock_at is not None:
                    new_floor = min(new_floor, r.trailing_lock_at)
                self.floor = max(self.floor, new_floor)
                self._check_pass()

        self.history.append(dict(
            day_index=self.days_used - 1, date=day.date, pnl=pnl, pnl_effective=pnl_eff,
            intraday_low=low_eff, start_balance=start, balance=self.balance,
            floor=self.floor, eod_high=self.eod_high, dll_hit=dll_hit, traded=traded,
            status=self.status, reason=self.reason,
        ))
        return self.status

    def _check_pass(self) -> None:
        r, o = self.rules, self.options
        if self.profit < r.profit_target - EPS:
            return
        consistent = self.is_consistent()
        if not consistent and o.consistency_mode == "extend":
            self.consistency_extended = True
        if self.days_traded < r.min_days:
            return
        if consistent:
            self.status = PASSED
            self.reason = R_PASSED_EXT if self.consistency_extended else R_PASSED
        elif o.consistency_mode == "fail":
            self._fail(R_CONSISTENCY)


@dataclass
class EvalOutcome:
    passed: bool
    failed: bool
    days_used: int
    final_balance: float
    reason: str
    days_traded: int = 0
    consistency_extended: bool = False

    @property
    def timed_out(self) -> bool:
        return not (self.passed or self.failed)


def simulate_eval(days: Sequence[DayResult], rules: EvalRules = EvalRules(),
                  max_days: Optional[int] = None, options: Optional[EvalOptions] = None,
                  **overrides) -> EvalOutcome:
    """Run an evaluation over ``days`` (in order) until pass, fail, or the days run out.

    ``max_days`` caps the number of calendar days consumed. If neither pass nor fail happens the
    outcome has ``reason="timeout"``.
    """
    acc = EvalAccount(rules, options, **overrides)
    for i, d in enumerate(days):
        if max_days is not None and i >= max_days:
            break
        if acc.apply_day(d) != ACTIVE:
            break
    return EvalOutcome(
        passed=acc.status == PASSED, failed=acc.status == FAILED, days_used=acc.days_used,
        final_balance=acc.balance, reason=acc.reason if acc.reason else R_TIMEOUT,
        days_traded=acc.days_traded, consistency_extended=acc.consistency_extended,
    )


def room_today(account: EvalAccount, safety_buffer: float = 0.0) -> dict:
    """Risk/profit envelope for the next session, for a live bot.

    Returns a dict with:

    * ``max_loss_today`` = ``min(balance - floor, daily_loss_limit) - safety_buffer`` (>= 0). The
      floor is a *touch* breach, so a bot must keep its worst open P&L strictly above
      ``-(balance - floor)``; use ``safety_buffer`` for slippage.
    * ``profit_needed`` = ``max(0, effective_target - profit)`` where
      ``effective_target = max(target, best_day / consistency)``.
    * ``max_profit_today_for_consistency``: the largest profit ``x`` you can bank today without
      increasing the total profit you will ultimately need. Derivation (c = consistency, P =
      current profit, B = best day so far, T = effective target = max(target, B/c)): after banking
      ``x > 0`` the new effective target is ``max(T, x/c)``. It is unchanged iff ``x <= c*T``.
      If ``x > c*T`` it rises to ``x/c``, but the new total ``P + x`` still meets it iff
      ``x <= c*P/(1-c)`` (you would pass today). Hence

          cap = max(c * T, c * P / (1 - c))

      With the defaults at the start (P=0, T=1250): cap = 625, i.e. to pass at exactly $1,250
      no day may exceed $625. At c=0.5 the second term is just P (today may match everything
      made so far). If P < 0 the cap stays c*T: losses must be recovered with more days, not
      bigger ones. ``inf`` when consistency is off.
    * ``can_pass_today``: ``profit_needed <= cap`` and at most one more traded day is required
      for ``min_days``.
    * plus ``balance``, ``floor``, ``room_to_floor``, ``effective_target``, ``days_traded``,
      ``min_days_remaining``, ``status``.
    """
    r = account.rules
    base = dict(status=account.status, balance=account.balance, floor=account.floor,
                room_to_floor=account.balance - account.floor,
                effective_target=account.effective_target, days_traded=account.days_traded,
                min_days_remaining=max(0, r.min_days - account.days_traded))
    if account.status != ACTIVE:
        base.update(max_loss_today=0.0, profit_needed=0.0, max_profit_today_for_consistency=0.0,
                    can_pass_today=False)
        return base
    room = account.balance - account.floor
    dll = r.daily_loss_limit
    max_loss = room if dll is None else min(room, float(dll))
    max_loss = max(0.0, max_loss - safety_buffer)
    T = account.effective_target
    P = account.profit
    needed = max(0.0, T - P)
    if consistency_active(r, account.options):
        c = r.consistency
        cap = max(c * T, c * P / (1.0 - c))
    else:
        cap = math.inf
    base.update(max_loss_today=max_loss, profit_needed=needed,
                max_profit_today_for_consistency=cap,
                can_pass_today=bool(needed <= cap + EPS and base["min_days_remaining"] <= 1))
    return base

"""Event-driven, per-session bar backtester.

Execution model (deliberately conservative; see ``run_backtest`` for details):

* A strategy sees bars ``0..i`` of the current session on bar ``i``'s close and may
  return a :class:`~propbot.interfaces.Signal`. It fills at the OPEN of bar ``i+1``
  with ``slippage_ticks`` against you. Signals from the last bar of a session or
  the bar before the flatten time are never filled.
* Protective stop / target orders are live from the moment of the fill, i.e. they
  are checked against the full range of the fill bar (all of which happens after
  its open) and every later bar. If a bar touches both, the STOP is assumed to hit
  first. Stops fill at the stop price (or the bar open if it gapped through) minus
  slippage; targets are limit orders that fill exactly at the target price.
* Positions are flattened at the open of the first bar at/after
  ``rules.flatten_time`` and at the last bar's close of the session (both with
  slippage). Overnight holding is impossible.
* ``commission_rt * qty`` is charged per round trip; P&L is in dollars, net.

The engine does not apply the prop-firm account rules (trailing drawdown, daily
loss limit, consistency); :mod:`propbot.rules` consumes the returned DayResults.
To mimic the firm's intraday daily-loss liquidation pass
``daily_stop=rules.daily_loss_limit`` (or something tighter).
"""
from __future__ import annotations

import math
from typing import Optional

import numpy as np
import pandas as pd

from .data import sessions
from .interfaces import ContractSpec, DayResult, EvalRules, Signal, Strategy, Trade

__all__ = ["run_backtest", "run_session", "summarize", "trades_frame"]

_EPS = 1e-9


def _minutes(hhmm: str) -> float:
    hh, mm = hhmm.split(":")[:2]
    return int(hh) * 60 + int(mm)


def _round_tick(px: Optional[float], tick: float) -> Optional[float]:
    if px is None or (isinstance(px, float) and math.isnan(px)):
        return None
    return round(float(px) / tick) * tick


def run_backtest(
    bars: pd.DataFrame,
    strategy: Strategy,
    contract: ContractSpec,
    qty: int,
    rules: EvalRules,
    slippage_ticks: float = 1,
    daily_stop: Optional[float] = None,
    daily_profit_cap: Optional[float] = None,
    max_trades_per_day: Optional[int] = None,
) -> list[DayResult]:
    """Backtest ``strategy`` over every session in ``bars`` (Bars format; normally RTH).

    Parameters
    ----------
    qty : contracts per trade (fixed). ``qty * contract.mini_equivalent`` must not
        exceed ``rules.max_minis``.
    slippage_ticks : ticks of adverse slippage on every market/stop fill.
    daily_stop : positive $; when realized + open P&L for the day reaches
        ``-daily_stop`` the position is closed at that price (a P&L-based stop,
        minus slippage) and no more trades are taken that day.
    daily_profit_cap : positive $; once realized day P&L >= cap, no new trades
        (the position is flat at that point, a reversal's new leg is skipped).
    max_trades_per_day : maximum number of entries per session (reversals count).

    Returns one :class:`DayResult` per session, including days with no trades.
    """
    if qty < 1:
        raise ValueError("qty must be >= 1")
    assert qty * contract.mini_equivalent <= rules.max_minis + _EPS, (
        f"{qty} x {contract.symbol} = {qty * contract.mini_equivalent:g} minis "
        f"> max {rules.max_minis:g}"
    )
    return [
        run_session(
            date, sess, strategy, contract, qty, rules, slippage_ticks,
            daily_stop, daily_profit_cap, max_trades_per_day,
        )
        for date, sess in sessions(bars)
    ]


def run_session(
    date: pd.Timestamp,
    sess: pd.DataFrame,
    strategy: Strategy,
    contract: ContractSpec,
    qty: int,
    rules: EvalRules,
    slippage_ticks: float = 1,
    daily_stop: Optional[float] = None,
    daily_profit_cap: Optional[float] = None,
    max_trades_per_day: Optional[int] = None,
) -> DayResult:
    """Simulate one session. Same semantics as :func:`run_backtest`."""
    strategy.reset()
    n = len(sess)
    if n == 0:
        return DayResult(date=date, pnl=0.0)

    o = sess["open"].to_numpy(dtype=float)
    h = sess["high"].to_numpy(dtype=float)
    lo = sess["low"].to_numpy(dtype=float)
    c = sess["close"].to_numpy(dtype=float)
    idx = sess.index
    tod = idx.hour.to_numpy() * 60 + idx.minute.to_numpy() + idx.second.to_numpy() / 60.0
    after = np.flatnonzero(tod >= _minutes(rules.flatten_time))
    flat_i = int(after[0]) if after.size else n

    tick = contract.tick_size
    slip = slippage_ticks * tick
    mult = contract.point_value * qty
    comm = contract.commission_rt * qty

    side = 0                     # -1 / 0 / +1
    entry = 0.0
    entry_time = None
    stop: Optional[float] = None
    target: Optional[float] = None
    entry_tag = ""
    realized = 0.0
    trades: list[Trade] = []
    entries = 0
    halted = False
    worst = 0.0
    pending: Optional[Signal] = None

    def close(px: float, i: int, reason: str) -> None:
        nonlocal side, realized, stop, target
        pnl = (px - entry) * side * mult - comm
        realized += pnl
        trades.append(Trade(entry_time, idx[i], side, qty, entry, px, pnl,
                            reason if not entry_tag else f"{entry_tag}|{reason}"))
        side, stop, target = 0, None, None

    def can_open() -> bool:
        if halted:
            return False
        if max_trades_per_day is not None and entries >= max_trades_per_day:
            return False
        if daily_profit_cap is not None and realized >= daily_profit_cap - _EPS:
            return False
        if daily_stop is not None and realized - comm <= -daily_stop + _EPS:
            return False
        return True

    for i in range(n):
        # ---- forced flatten at the flatten-time bar's open
        if i >= flat_i:
            if side:
                close(o[i] - side * slip, i, "flatten_time")
                worst = min(worst, realized)
            pending = None
            break

        # ---- execute the order from the previous bar's close at this open
        if pending is not None:
            sig, pending = pending, None
            if sig.side == 0:
                if side:
                    close(o[i] - side * slip, i, "exit")
            elif sig.side != side:
                if side:
                    close(o[i] - side * slip, i, "reverse")
                if daily_profit_cap is not None and realized >= daily_profit_cap - _EPS:
                    halted = True
                if daily_stop is not None and realized <= -daily_stop + _EPS:
                    halted = True
                if can_open():
                    side = 1 if sig.side > 0 else -1
                    entry = o[i] + side * slip
                    entry_time = idx[i]
                    stop = _round_tick(sig.stop, tick)
                    target = _round_tick(sig.target, tick)
                    entry_tag = sig.tag
                    entries += 1
            worst = min(worst, realized)

        # ---- intrabar stop / daily-stop / target, and adverse mark-to-market
        if side:
            eff_stop, stop_reason = stop, "stop"
            if daily_stop is not None:
                ds = entry - side * (daily_stop + realized - comm) / mult
                ds = math.ceil(ds / tick - _EPS) * tick if side > 0 else math.floor(ds / tick + _EPS) * tick
                if eff_stop is None or (ds >= eff_stop if side > 0 else ds <= eff_stop):
                    eff_stop, stop_reason = ds, "daily_stop"
            if side > 0:
                adverse = lo[i] if eff_stop is None else max(lo[i], eff_stop)
                stop_hit = eff_stop is not None and lo[i] <= eff_stop
                tgt_hit = target is not None and h[i] >= target
            else:
                adverse = h[i] if eff_stop is None else min(h[i], eff_stop)
                stop_hit = eff_stop is not None and h[i] >= eff_stop
                tgt_hit = target is not None and lo[i] <= target
            worst = min(worst, realized + (adverse - entry) * side * mult - comm)
            if stop_hit:  # stop wins ties with the target (conservative)
                gap_px = min(o[i], eff_stop) if side > 0 else max(o[i], eff_stop)
                close(gap_px - side * slip, i, stop_reason)
                worst = min(worst, realized)
                if stop_reason == "daily_stop":
                    halted = True
            elif tgt_hit:
                close(target, i, "target")

        if daily_stop is not None and realized <= -daily_stop + _EPS:
            halted = True
        if daily_profit_cap is not None and realized >= daily_profit_cap - _EPS:
            halted = True
        if halted and side == 0:
            break

        # ---- strategy decision on this bar's close (sees rows 0..i only)
        sig = strategy.on_bar(i, sess.iloc[: i + 1], side * qty)
        if sig is not None and i + 1 < flat_i and i + 1 < n:
            pending = sig
    else:
        if side:
            close(c[-1] - side * slip, n - 1, "eod")
            worst = min(worst, realized)

    return DayResult(date=date, pnl=realized, trades=trades, max_intraday_drawdown=min(worst, 0.0))


# --------------------------------------------------------------------------- reporting
def trades_frame(days: list[DayResult]) -> pd.DataFrame:
    """All trades as a DataFrame (one row per trade)."""
    rows = [vars(t) | {"date": d.date} for d in days for t in d.trades]
    cols = ["date", "entry_time", "exit_time", "side", "qty", "entry", "exit", "pnl", "reason"]
    return pd.DataFrame(rows, columns=cols)


def summarize(days: list[DayResult]) -> dict:
    """Headline statistics for a list of DayResults.

    Keys: n_days, n_trading_days, n_trades, trades_per_day, total_pnl, avg_day_pnl,
    day_win_rate (winning days / days with trades), trade_win_rate, avg_win,
    avg_loss (negative), expectancy (per trade), profit_factor, max_drawdown
    (peak-to-trough of cumulative closed daily P&L, <= 0), worst_intraday_drawdown,
    best_day, worst_day, sharpe (annualised, sqrt(252), on all days' P&L).
    """
    pnl = np.array([d.pnl for d in days], dtype=float)
    tp = np.array([t.pnl for d in days for t in d.trades], dtype=float)
    traded = np.array([bool(d.trades) for d in days], dtype=bool)
    n_days = len(days)

    eq = np.concatenate([[0.0], np.cumsum(pnl)])
    max_dd = float((eq - np.maximum.accumulate(eq)).min()) if n_days else 0.0
    wins, losses = tp[tp > 0], tp[tp < 0]
    if losses.size:
        pf = float(wins.sum() / -losses.sum())
    else:
        pf = float("inf") if wins.size else float("nan")
    sd = pnl.std(ddof=1) if n_days > 1 else 0.0
    traded_pnl = pnl[traded]

    def mean(a):
        return float(a.mean()) if a.size else 0.0

    return {
        "n_days": n_days,
        "n_trading_days": int(traded.sum()),
        "n_trades": int(tp.size),
        "trades_per_day": tp.size / n_days if n_days else 0.0,
        "total_pnl": float(pnl.sum()),
        "avg_day_pnl": mean(pnl),
        "day_win_rate": float((traded_pnl > 0).mean()) if traded_pnl.size else 0.0,
        "trade_win_rate": float((tp > 0).mean()) if tp.size else 0.0,
        "avg_win": mean(wins),
        "avg_loss": mean(losses),
        "expectancy": mean(tp),
        "profit_factor": pf,
        "max_drawdown": max_dd,
        "worst_intraday_drawdown": float(min((d.max_intraday_drawdown for d in days), default=0.0)),
        "best_day": float(pnl.max()) if n_days else 0.0,
        "worst_day": float(pnl.min()) if n_days else 0.0,
        "sharpe": float(pnl.mean() / sd * np.sqrt(252)) if sd > 0 else 0.0,
    }

"""Prior-day high/low levels: breakout-and-retest, or failed-breakout fade.

The prior RTH session's high (PDH) and low (PDL) are among the most watched intraday levels.
The prior session's high/low/close are stored on the instance when a session ends, so only past
data is used. Two modes:

``breakout_retest``
    A bar closes through the level (from the other side; a gap through the level counts as a
    break at the first bar). Later, price comes back to within ``tol_atr`` ATR of the level,
    holds it (close stays beyond the level) and prints a bar closing in the breakout direction
    -> enter with the breakout. Stop = beyond min(retest bar extreme, level) by ``stop_atr`` ATR.
    A close back through the level by more than ``tol_atr`` ATR cancels the breakout.

``fade``
    Price pokes beyond the level by at least ``poke_ticks`` but within ``fail_bars`` bars of the
    first poke closes back inside -> fade back toward the range. Stop = beyond the poke extreme by
    ``stop_atr`` ATR. If price holds beyond the level for ``fail_bars`` bars the break is
    accepted and the level is not faded that day.

Target = R multiple. One trade per level per session.
"""
from __future__ import annotations

from typing import Optional

from ..interfaces import Signal
from .base import BaseStrategy


class _LevelState:
    __slots__ = ("broke", "broke_i", "poke_i", "poke_ext", "done")

    def __init__(self):
        self.broke = False
        self.broke_i = -1
        self.poke_i = -1
        self.poke_ext = None
        self.done = False


class PriorDayLevels(BaseStrategy):
    name = "prior_day_levels"
    default_params = {
        **BaseStrategy.default_params,
        "mode": "breakout_retest",    # or "fade"
        "start": "09:35",
        "cutoff": "14:00",
        "max_trades": 2,
        "tol_atr": 0.5,
        "stop_atr": 1.0,
        "target_r": 1.5,
        "poke_ticks": 2,
        "fail_bars": 10,
        "max_stop_atr": 6.0,          # skip if the stop would be wider than this many ATR
    }

    def init_state(self) -> None:
        self.pdh = self.pdl = self.pdc = None

    def session_reset(self) -> None:
        self.up = _LevelState()     # PDH: breakout long / fade short
        self.dn = _LevelState()     # PDL: breakout short / fade long
        self.trigger = None         # (bar index, side, stop, tag)

    def end_session(self) -> None:
        if self.c:
            self.pdh = max(self.h)
            self.pdl = min(self.l)
            self.pdc = self.c[-1]

    # ------------------------------------------------------------------
    def update(self, j: int) -> None:
        if self.pdh is None:
            return
        if self.params["mode"] == "fade":
            self._fade(j, self.up, self.pdh, +1)
            self._fade(j, self.dn, self.pdl, -1)
        else:
            self._retest(j, self.up, self.pdh, +1)
            self._retest(j, self.dn, self.pdl, -1)

    def _retest(self, j: int, st: _LevelState, level: float, d: int) -> None:
        """d=+1: breakout above PDH -> long; d=-1: breakdown below PDL -> short."""
        if st.done:
            return
        p = self.params
        atr = self.atr_value
        c, o = self.c[j], self.o[j]
        prev_c = self.c[j - 1] if j > 0 else self.pdc
        tol = p["tol_atr"] * atr
        if not st.broke:
            if (c - level) * d > 0 and (prev_c - level) * d <= 0:
                st.broke, st.broke_i = True, j
            elif j == 0 and (c - level) * d > 0:
                st.broke, st.broke_i = True, j
            return
        if (level - c) * d > tol:          # closed back through the level: breakout failed
            st.broke = False
            return
        if j <= st.broke_i:
            return
        extreme = self.l[j] if d > 0 else self.h[j]
        touched = (extreme - level) * d <= tol
        holds = (c - level) * d > 0
        resumes = (c - o) * d > 0
        if touched and holds and resumes:
            base = min(extreme, level) if d > 0 else max(extreme, level)
            stop = base - d * p["stop_atr"] * atr
            self.trigger = (j, d, stop, "retest_long" if d > 0 else "retest_short")

    def _fade(self, j: int, st: _LevelState, level: float, d: int) -> None:
        """d=+1: pokes above PDH then fails -> short; d=-1: below PDL then fails -> long."""
        if st.done:
            return
        p = self.params
        poke = p["poke_ticks"] * self.tick
        extreme = self.h[j] if d > 0 else self.l[j]
        c = self.c[j]
        if st.poke_i < 0:
            if (extreme - level) * d >= poke:
                st.poke_i, st.poke_ext = j, extreme
            else:
                return
        else:
            st.poke_ext = max(st.poke_ext, extreme) if d > 0 else min(st.poke_ext, extreme)
        if (c - level) * d < 0:            # closed back inside: failed breakout
            stop = st.poke_ext + d * p["stop_atr"] * self.atr_value
            self.trigger = (j, -d, stop, "fade_short" if d > 0 else "fade_long")
            st.poke_i, st.poke_ext = -1, None   # re-arm (only used if this trigger is not taken)
        elif j - st.poke_i >= int(p["fail_bars"]):
            st.done = True                 # breakout accepted: do not fade

    def decide(self, i: int) -> Optional[Signal]:
        if self.trigger is None or self.trigger[0] != i:
            return None
        _, side, stop, tag = self.trigger
        atr = self.atr_value
        if atr <= 0 or abs(self.c[i] - stop) > self.params["max_stop_atr"] * atr:
            return None
        sig = self.entry(side, stop, self.r_target(side, stop, self.params["target_r"]), tag)
        if sig is not None:
            # one trade per level per day
            st = (self.up if side < 0 else self.dn) if self.params["mode"] == "fade" else \
                 (self.up if side > 0 else self.dn)
            st.done = True
        return sig


PARAM_GRID = {
    "mode": ["breakout_retest", "fade"],
    "stop_atr": [0.5, 1.0],
    "target_r": [1.0, 1.5, 2.0],
    "cutoff": ["11:30", "14:00"],
}  # 24 combos

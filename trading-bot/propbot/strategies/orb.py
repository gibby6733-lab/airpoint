"""Opening Range Breakout (ORB).

Classic Toby Crabel / "opening range breakout" day-trading setup: mark the high/low of the
first N minutes of RTH; go long on a bar CLOSE above the range high (+ optional buffer), short
on a close below the low. Stop at the opposite side of the range or at its midpoint; target is
a fixed R multiple of the initial risk. One trade per side per day, no new entries after the
cutoff (late breakouts have poor follow-through and leave little time to reach target before
the 15:55 flat rule).
"""
from __future__ import annotations

from typing import Optional

from ..interfaces import Signal
from .base import SESSION_OPEN, BaseStrategy


class OpeningRangeBreakout(BaseStrategy):
    name = "orb"
    default_params = {
        **BaseStrategy.default_params,
        "or_minutes": 15,          # 5 / 15 / 30
        "buffer_ticks": 0,         # close must exceed the range by this many ticks
        "stop_mode": "opposite",   # "opposite" side of range or range "mid"
        "target_r": 1.5,
        "cutoff": "11:30",
        "max_trades": 2,
        "max_range_atr": None,     # optional: skip day if OR range > this * 1-min ATR
    }

    def session_reset(self) -> None:
        self.or_high: Optional[float] = None
        self.or_low: Optional[float] = None
        self.or_done = False
        self.traded_long = False
        self.traded_short = False

    def update(self, j: int) -> None:
        if self.or_done:
            return
        end = SESSION_OPEN + int(self.params["or_minutes"])
        m = self.mins[j]
        if m < end:
            h, l = self.h[j], self.l[j]
            self.or_high = h if self.or_high is None else max(self.or_high, h)
            self.or_low = l if self.or_low is None else min(self.or_low, l)
        if m + self.bar_minutes >= end:
            self.or_done = True

    def decide(self, i: int) -> Optional[Signal]:
        if not self.or_done or self.or_high is None or self.mins[i] < SESSION_OPEN + int(self.params["or_minutes"]):
            return None
        hi, lo = self.or_high, self.or_low
        rng = hi - lo
        if rng <= 0:
            return None
        p = self.params
        mra = p["max_range_atr"]
        if mra is not None and self.atr_value > 0 and rng > mra * self.atr_value:
            return None
        buf = p["buffer_ticks"] * self.tick
        close = self.c[i]
        mid = 0.5 * (hi + lo)
        if not self.traded_long and close > hi + buf:
            stop = lo if p["stop_mode"] == "opposite" else mid
            sig = self.entry(+1, stop, self.r_target(+1, stop, p["target_r"]), "long")
            if sig is not None:
                self.traded_long = True
            return sig
        if not self.traded_short and close < lo - buf:
            stop = hi if p["stop_mode"] == "opposite" else mid
            sig = self.entry(-1, stop, self.r_target(-1, stop, p["target_r"]), "short")
            if sig is not None:
                self.traded_short = True
            return sig
        return None


PARAM_GRID = {
    "or_minutes": [5, 15, 30],
    "buffer_ticks": [0, 4],
    "stop_mode": ["opposite", "mid"],
    "target_r": [1.0, 1.5, 2.0],
}  # 36 combos

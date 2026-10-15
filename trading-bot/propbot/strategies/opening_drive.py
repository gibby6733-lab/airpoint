"""Opening-drive momentum continuation ("first pullback after an opening drive").

If the first ``drive_minutes`` of RTH move strongly in one direction -- more than ``drive_k``
times the median full-day range of recent prior sessions (kept on the instance, so only past
data is used) -- the day often trends. We do not chase the drive; we wait for the FIRST
pullback that retraces at least ``pb_frac`` of the drive (but less than ``pb_max``, which would
mean the drive failed) and enter when a bar closes back in the drive direction beyond the
previous bar's extreme. Stop just beyond the pullback extreme; target an R multiple.

Until ``min_history`` prior sessions have been seen, the reference range falls back to a
random-walk proxy from the current session's 1-min ATR (ATR * sqrt(390)), which is clearly
labelled as a rough fallback.
"""
from __future__ import annotations

import math
from typing import Optional

from ..interfaces import Signal
from .base import SESSION_OPEN, BaseStrategy
from .indicators import median


class OpeningDrive(BaseStrategy):
    name = "opening_drive"
    default_params = {
        **BaseStrategy.default_params,
        "cutoff": "11:30",
        "max_trades": 1,
        "drive_minutes": 30,
        "drive_k": 0.3,        # drive must exceed this fraction of the reference day range
        "pb_frac": 0.382,      # min retracement of the drive to count as a pullback
        "pb_max": 0.786,       # retracement beyond this invalidates the drive
        "stop_ticks": 4,       # stop beyond the pullback extreme
        "target_r": 2.0,
        "min_history": 3,
        "history": 20,
    }

    def init_state(self) -> None:
        self.range_hist = []

    def session_reset(self) -> None:
        self.drive_done = False
        self.dir = 0
        self.anchor = None      # session open price
        self.ext = None         # drive extreme
        self.in_pb = False
        self.pb_ext = None      # pullback extreme (low for longs)
        self.finished = False
        self.trigger = None     # (bar index, side, stop)
        self.s_high = -math.inf
        self.s_low = math.inf

    def end_session(self) -> None:
        if self.s_high > self.s_low:
            self.range_hist.append(self.s_high - self.s_low)
            del self.range_hist[: -int(self.params["history"])]

    def _reference(self) -> Optional[float]:
        if len(self.range_hist) >= int(self.params["min_history"]):
            return median(self.range_hist)
        a = self.atr_value
        return a * math.sqrt(390.0) if a > 0 else None

    def update(self, j: int) -> None:
        h, l, c, o = self.h[j], self.l[j], self.c[j], self.o[j]
        self.s_high = max(self.s_high, h)
        self.s_low = min(self.s_low, l)
        p = self.params
        if not self.drive_done:
            if j == 0:
                self.anchor = o
            if self.mins[j] + self.bar_minutes >= SESSION_OPEN + int(p["drive_minutes"]):
                self.drive_done = True
                move = c - self.anchor
                ref = self._reference()
                if ref and abs(move) >= p["drive_k"] * ref:
                    self.dir = 1 if move > 0 else -1
                    self.ext = self.s_high if self.dir > 0 else self.s_low
            return
        if self.dir == 0 or self.finished:
            return
        d = self.dir
        drive = (self.ext - self.anchor) * d
        if drive <= 0:
            self.finished = True
            return
        if d > 0:
            if not self.in_pb and h > self.ext:
                self.ext = h
                return
            retr = (self.ext - l) / drive
        else:
            if not self.in_pb and l < self.ext:
                self.ext = l
                return
            retr = (h - self.ext) / drive
        if retr >= p["pb_max"]:
            self.finished = True        # drive failed
            return
        if retr >= p["pb_frac"]:
            if not self.in_pb:
                self.in_pb = True
                self.pb_ext = l if d > 0 else h
            else:
                self.pb_ext = min(self.pb_ext, l) if d > 0 else max(self.pb_ext, h)
        if self.in_pb and j > 0:
            if d > 0 and c > self.h[j - 1] and c > o:
                self.trigger = (j, 1, self.pb_ext - p["stop_ticks"] * self.tick)
                self.finished = True    # first pullback only
            elif d < 0 and c < self.l[j - 1] and c < o:
                self.trigger = (j, -1, self.pb_ext + p["stop_ticks"] * self.tick)
                self.finished = True

    def decide(self, i: int) -> Optional[Signal]:
        if self.trigger is None or self.trigger[0] != i:
            return None
        _, side, stop = self.trigger
        return self.entry(side, stop, self.r_target(side, stop, self.params["target_r"]),
                          "long" if side > 0 else "short")


PARAM_GRID = {
    "drive_minutes": [15, 30],
    "drive_k": [0.2, 0.3, 0.4],
    "pb_frac": [0.236, 0.382],
    "target_r": [1.5, 2.0],
}  # 24 combos

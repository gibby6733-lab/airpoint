"""VWAP standard-deviation band mean reversion.

On balanced (non-trend) days price oscillates around session VWAP; stretches to the 2-3 sigma
volume-weighted bands tend to revert. Entry: the previous bar closed OUTSIDE the k-sigma band
and the current bar closes back INSIDE it (confirmation, not catching the knife). Target is
VWAP; stop is a fixed ATR multiple beyond the entry close. Only trades mid-session
(default 10:30-15:00) and skips trend days, which is where this setup bleeds:

  * one-sidedness: if more than ``side_frac`` of the session's closes have been on one side
    of VWAP the day is treated as trending;
  * opening-range expansion: if the first ``or_minutes`` range exceeds ``or_max_mult`` times
    the median opening range of prior sessions (kept on the instance -- past data only), or
    ``or_max_atr`` times the current 1-min ATR, skip the day.
"""
from __future__ import annotations

from typing import Optional

from ..interfaces import Signal
from .base import SESSION_OPEN, BaseStrategy
from .indicators import SessionVWAP, median


class VWAPReversion(BaseStrategy):
    name = "vwap_reversion"
    default_params = {
        **BaseStrategy.default_params,
        "start": "10:30",
        "cutoff": "15:00",
        "exit_time": "15:30",
        "max_trades": 2,
        "band_k": 2.0,
        "stop_atr": 1.5,
        "side_frac": 0.8,       # > this fraction of closes on one side of VWAP => trend day
        "or_minutes": 30,
        "or_max_mult": 1.75,    # vs median prior-session opening range (None = off)
        "or_max_atr": None,     # vs current 1-min ATR (None = off)
        "min_rr": 0.75,         # require (distance to VWAP) >= min_rr * risk
        "history": 20,
        "cooldown": 10,
    }

    def init_state(self) -> None:
        self.or_hist = []

    def session_reset(self) -> None:
        self.vwap = SessionVWAP()
        self.n_above = 0
        self.n_below = 0
        self.or_high = None
        self.or_low = None
        self.prev_band = None
        self.cur_band = None

    def end_session(self) -> None:
        if self.or_high is not None:
            self.or_hist.append(self.or_high - self.or_low)
            del self.or_hist[: -int(self.params["history"])]

    def update(self, j: int) -> None:
        h, l, c = self.h[j], self.l[j], self.c[j]
        vw = self.vwap.update(h, l, c, self.v[j])
        if c > vw:
            self.n_above += 1
        elif c < vw:
            self.n_below += 1
        if self.mins[j] < SESSION_OPEN + int(self.params["or_minutes"]):
            self.or_high = h if self.or_high is None else max(self.or_high, h)
            self.or_low = l if self.or_low is None else min(self.or_low, l)
        self.prev_band = self.cur_band
        self.cur_band = self.vwap.bands(float(self.params["band_k"]))

    def _trend_day(self) -> bool:
        p = self.params
        n = len(self.c)
        if n == 0:
            return True
        frac = p["side_frac"]
        if self.n_above > frac * n or self.n_below > frac * n:
            return True
        if self.or_high is not None:
            rng = self.or_high - self.or_low
            mult = p["or_max_mult"]
            if mult is not None and len(self.or_hist) >= 5 and rng > mult * median(self.or_hist):
                return True
            oma = p["or_max_atr"]
            if oma is not None and self.atr_value > 0 and rng > oma * self.atr_value:
                return True
        return False

    def decide(self, i: int) -> Optional[Signal]:
        p = self.params
        if self.prev_band is None or i < 1 or i - self.last_entry_i < int(p["cooldown"]):
            return None
        if self._trend_day():
            return None
        atr = self.atr_value
        if atr <= 0 or self.vwap.std <= 0:
            return None
        vw = self.vwap.value
        lo, hi = self.cur_band
        plo, phi = self.prev_band
        prev_c, close = self.c[i - 1], self.c[i]
        risk = p["stop_atr"] * atr
        if prev_c > phi and close <= hi and close > vw:
            if close - vw >= p["min_rr"] * risk:
                return self.entry(-1, close + risk, vw, "short")
        elif prev_c < plo and close >= lo and close < vw:
            if vw - close >= p["min_rr"] * risk:
                return self.entry(+1, close - risk, vw, "long")
        return None


PARAM_GRID = {
    "band_k": [2.0, 2.5, 3.0],
    "stop_atr": [1.0, 1.5, 2.0],
    "side_frac": [0.7, 0.85],
    "min_rr": [0.5, 1.0],
}  # 36 combos

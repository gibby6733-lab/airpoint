"""Trend-day VWAP pullback.

On trend days institutions defend session VWAP; the standard play is to wait (after 10:00, when
the open's noise has settled) for a market trading on one side of a sloping VWAP, let price pull
back into VWAP (or within ``touch_atr`` ATR of it), and enter when a bar closes back in the trend
direction (bullish bar closing above the prior bar's high for longs). Stop goes beyond the
pullback swing extreme plus an ATR buffer; target is an R multiple.

Trend definition: close and fast EMA on the trend side of VWAP and VWAP itself sloping that way
over the last ``slope_bars`` bars.
"""
from __future__ import annotations

from typing import Optional

from ..interfaces import Signal
from .base import BaseStrategy
from .indicators import EMA, SessionVWAP


class VWAPPullback(BaseStrategy):
    name = "vwap_pullback"
    default_params = {
        **BaseStrategy.default_params,
        "start": "10:00",
        "cutoff": "14:30",
        "max_trades": 2,
        "ema_len": 20,
        "slope_bars": 15,      # VWAP slope lookback (bars)
        "lookback": 5,         # bars that define the pullback swing
        "touch_atr": 0.5,      # pullback must come within this many ATR of VWAP
        "stop_atr": 0.5,       # buffer beyond the swing extreme
        "target_r": 1.5,
        "cooldown": 10,        # bars between entries
    }

    def session_reset(self) -> None:
        self.vwap = SessionVWAP()
        self.ema = EMA(int(self.params["ema_len"]))
        self.vw_hist = []

    def update(self, j: int) -> None:
        self.vw_hist.append(self.vwap.update(self.h[j], self.l[j], self.c[j], self.v[j]))
        self.ema.update(self.c[j])

    def decide(self, i: int) -> Optional[Signal]:
        p = self.params
        sb, lb = int(p["slope_bars"]), int(p["lookback"])
        if len(self.vw_hist) <= max(sb, lb) or not self.ema.ready:
            return None
        if i - self.last_entry_i < int(p["cooldown"]):
            return None
        atr = self.atr_value
        if atr <= 0:
            return None
        vw = self.vw_hist[-1]
        slope = vw - self.vw_hist[-1 - sb]
        close, opn, ema = self.c[i], self.o[i], self.ema.value
        zone = p["touch_atr"] * atr
        if close > vw and ema > vw and slope > 0:
            swing = min(self.l[-lb:])
            if swing <= vw + zone and close > opn and close > self.h[i - 1]:
                stop = swing - p["stop_atr"] * atr
                return self.entry(+1, stop, self.r_target(+1, stop, p["target_r"]), "long")
        elif close < vw and ema < vw and slope < 0:
            swing = max(self.h[-lb:])
            if swing >= vw - zone and close < opn and close < self.l[i - 1]:
                stop = swing + p["stop_atr"] * atr
                return self.entry(-1, stop, self.r_target(-1, stop, p["target_r"]), "short")
        return None


PARAM_GRID = {
    "touch_atr": [0.25, 0.5],
    "stop_atr": [0.5, 1.0],
    "target_r": [1.0, 1.5, 2.0],
    "slope_bars": [10, 20],
}  # 24 combos

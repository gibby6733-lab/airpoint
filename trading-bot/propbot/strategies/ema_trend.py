"""EMA trend pullback on 5-minute bars (9/21 EMA by default).

1-minute bars are aggregated incrementally into 5-minute bars; indicators update ONLY when a
5-minute bar is complete (the 1-min bar that closes the bucket has been seen), so there is no
lookahead. Setup (long; short is the mirror):
  * fast EMA > slow EMA, slow EMA rising (slope filter), and ADX >= ``adx_min`` with +DI > -DI;
  * the just-completed 5-min bar pulled back to the fast EMA (low <= fast EMA) but closed back
    above it as a bullish bar (close > open);
  * enter long; stop = that 5-min bar's low - ``stop_atr`` * 5-min ATR; target = R multiple.

By default (``carry=True``) the 5-min EMAs/ADX/ATR carry across sessions, as on a continuous
chart -- this only uses past sessions' data and avoids a ~2 hour ADX warm-up every morning.
"""
from __future__ import annotations

from typing import Optional

from ..interfaces import Signal
from .base import SESSION_OPEN, BaseStrategy
from .indicators import ADX, EMA, Resampler, WilderATR


class EMATrend(BaseStrategy):
    name = "ema_trend"
    default_params = {
        **BaseStrategy.default_params,
        "start": "09:45",
        "cutoff": "15:00",
        "max_trades": 3,
        "tf_minutes": 5,
        "fast": 9,
        "slow": 21,
        "adx_len": 14,
        "adx_min": 20.0,
        "stop_atr": 0.5,
        "target_r": 1.5,
        "carry": True,
    }

    def init_state(self) -> None:
        self._make_indicators()

    def _make_indicators(self) -> None:
        p = self.params
        self.fast = EMA(int(p["fast"]))
        self.slow = EMA(int(p["slow"]))
        self.adx = ADX(int(p["adx_len"]))
        self.atr5 = WilderATR(14)

    def session_reset(self) -> None:
        if not self.params["carry"]:
            self._make_indicators()
        self.rs = Resampler(int(self.params["tf_minutes"]), SESSION_OPEN)
        self.last5 = None
        self.new5_at = -1

    def update(self, j: int) -> None:
        for b in self.rs.update(self.mins[j], self.bar_minutes, self.o[j], self.h[j],
                                self.l[j], self.c[j], self.v[j]):
            self.fast.update(b.close)
            self.slow.update(b.close)
            self.adx.update(b.high, b.low, b.close)
            self.atr5.update(b.high, b.low, b.close)
            self.last5 = b
            self.new5_at = j

    def decide(self, i: int) -> Optional[Signal]:
        if self.new5_at != i or self.last5 is None:
            return None
        if not (self.slow.ready and self.fast.ready) or self.adx.adx is None or self.slow.prev is None:
            return None
        p = self.params
        b = self.last5
        f, s = self.fast.value, self.slow.value
        atr = self.atr5.value or 0.0
        if atr <= 0 or self.adx.adx < p["adx_min"]:
            return None
        if f > s and s > self.slow.prev and self.adx.plus_di > self.adx.minus_di:
            if b.low <= f and b.close > f and b.close > b.open:
                stop = b.low - p["stop_atr"] * atr
                return self.entry(+1, stop, self.r_target(+1, stop, p["target_r"]), "long")
        elif f < s and s < self.slow.prev and self.adx.minus_di > self.adx.plus_di:
            if b.high >= f and b.close < f and b.close < b.open:
                stop = b.high + p["stop_atr"] * atr
                return self.entry(-1, stop, self.r_target(-1, stop, p["target_r"]), "short")
        return None


PARAM_GRID = {
    "fast": [9, 13],
    "slow": [21, 34],
    "adx_min": [18.0, 25.0],
    "stop_atr": [0.5, 1.0],
    "target_r": [1.5, 2.0],
}  # 32 combos

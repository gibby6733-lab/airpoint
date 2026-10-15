"""Incremental (streaming) indicators for intraday strategies.

Every indicator here is updated one bar at a time and only ever sees data that has already
been passed to ``update`` -- so a strategy that feeds them bar-by-bar in order cannot leak
future information. All are O(1) per update.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional


def hhmm(t) -> int:
    """'HH:MM' (or an int already in minutes) -> minutes after midnight."""
    if isinstance(t, (int, float)):
        return int(t)
    h, m = str(t).split(":")
    return int(h) * 60 + int(m)


class EMA:
    """Exponential moving average seeded with the first value. ``ready`` after ``n`` updates."""

    __slots__ = ("n", "alpha", "value", "count", "prev")

    def __init__(self, n: int):
        self.n = int(n)
        self.alpha = 2.0 / (self.n + 1.0)
        self.value: Optional[float] = None
        self.prev: Optional[float] = None
        self.count = 0

    def update(self, x: float) -> float:
        self.prev = self.value
        if self.value is None:
            self.value = float(x)
        else:
            self.value += self.alpha * (x - self.value)
        self.count += 1
        return self.value

    @property
    def ready(self) -> bool:
        return self.count >= self.n


class WilderATR:
    """Average True Range with Wilder smoothing (simple average while warming up)."""

    __slots__ = ("n", "prev_close", "value", "count", "_sum")

    def __init__(self, n: int = 14):
        self.n = int(n)
        self.prev_close: Optional[float] = None
        self.value: Optional[float] = None
        self.count = 0
        self._sum = 0.0

    def update(self, h: float, l: float, c: float) -> float:
        pc = self.prev_close
        tr = h - l if pc is None else max(h - l, abs(h - pc), abs(l - pc))
        self.count += 1
        if self.count <= self.n:
            self._sum += tr
            self.value = self._sum / self.count
        else:
            self.value = (self.value * (self.n - 1) + tr) / self.n
        self.prev_close = c
        return self.value

    @property
    def ready(self) -> bool:
        return self.count >= self.n


class SessionVWAP:
    """Session VWAP of typical price with volume-weighted standard deviation bands.

    Uses West's weighted incremental mean/variance (numerically stable at index price
    levels). Zero-volume bars get a negligible weight so the VWAP stays defined.
    """

    __slots__ = ("w_sum", "mean", "_s", "count")

    def __init__(self):
        self.w_sum = 0.0
        self.mean: Optional[float] = None
        self._s = 0.0
        self.count = 0

    def update(self, h: float, l: float, c: float, v: float) -> float:
        tp = (h + l + c) / 3.0
        w = v if v > 0 else 1e-9
        self.count += 1
        if self.mean is None:
            self.w_sum = w
            self.mean = tp
            return tp
        new_w = self.w_sum + w
        delta = tp - self.mean
        self.mean += (w / new_w) * delta
        self._s += w * delta * (tp - self.mean)
        self.w_sum = new_w
        return self.mean

    @property
    def value(self) -> Optional[float]:
        return self.mean

    @property
    def std(self) -> float:
        if self.w_sum <= 0:
            return 0.0
        return math.sqrt(max(self._s / self.w_sum, 0.0))

    def bands(self, k: float):
        sd = self.std
        return self.mean - k * sd, self.mean + k * sd


class ADX:
    """Wilder's ADX / +DI / -DI, incremental. ``adx`` is None until ~2n bars."""

    __slots__ = ("n", "ph", "pl", "pc", "count", "s_tr", "s_pdm", "s_mdm",
                 "plus_di", "minus_di", "dx_count", "dx_sum", "adx")

    def __init__(self, n: int = 14):
        self.n = int(n)
        self.ph = self.pl = self.pc = None
        self.count = 0
        self.s_tr = self.s_pdm = self.s_mdm = 0.0
        self.plus_di: Optional[float] = None
        self.minus_di: Optional[float] = None
        self.dx_count = 0
        self.dx_sum = 0.0
        self.adx: Optional[float] = None

    def update(self, h: float, l: float, c: float) -> Optional[float]:
        if self.ph is None:
            self.ph, self.pl, self.pc = h, l, c
            return None
        up = h - self.ph
        dn = self.pl - l
        pdm = up if (up > dn and up > 0) else 0.0
        mdm = dn if (dn > up and dn > 0) else 0.0
        tr = max(h - l, abs(h - self.pc), abs(l - self.pc))
        self.ph, self.pl, self.pc = h, l, c
        n = self.n
        self.count += 1
        if self.count <= n:
            self.s_tr += tr
            self.s_pdm += pdm
            self.s_mdm += mdm
            if self.count < n:
                return None
        else:
            self.s_tr = self.s_tr - self.s_tr / n + tr
            self.s_pdm = self.s_pdm - self.s_pdm / n + pdm
            self.s_mdm = self.s_mdm - self.s_mdm / n + mdm
        if self.s_tr <= 0:
            self.plus_di = self.minus_di = 0.0
            dx = 0.0
        else:
            self.plus_di = 100.0 * self.s_pdm / self.s_tr
            self.minus_di = 100.0 * self.s_mdm / self.s_tr
            tot = self.plus_di + self.minus_di
            dx = 0.0 if tot <= 0 else 100.0 * abs(self.plus_di - self.minus_di) / tot
        self.dx_count += 1
        if self.dx_count <= n:
            self.dx_sum += dx
            if self.dx_count == n:
                self.adx = self.dx_sum / n
        else:
            self.adx = (self.adx * (n - 1) + dx) / n
        return self.adx


@dataclass
class RBar:
    """A completed resampled bar. ``start`` = minutes after midnight of the bucket open."""
    start: int
    open: float
    high: float
    low: float
    close: float
    volume: float


class Resampler:
    """Builds higher-timeframe bars from lower-timeframe bars, emitting a bar only once it is
    COMPLETE: either the bar that ends the bucket has been seen (minute + bar_minutes reaches
    the bucket end) or a bar from a later bucket arrives (gap in the data). Buckets are aligned
    to ``anchor`` (session open, minutes after midnight).
    """

    def __init__(self, period: int = 5, anchor: int = 570):
        self.period = int(period)
        self.anchor = int(anchor)
        self._cur: Optional[RBar] = None
        self._bucket: Optional[int] = None

    def reset(self):
        self._cur = None
        self._bucket = None

    def update(self, minute: int, bar_minutes: int, o, h, l, c, v) -> List[RBar]:
        out: List[RBar] = []
        bucket = (minute - self.anchor) // self.period
        if self._cur is not None and bucket != self._bucket:
            out.append(self._cur)
            self._cur = None
        if self._cur is None:
            self._bucket = bucket
            self._cur = RBar(self.anchor + bucket * self.period, o, h, l, c, v)
        else:
            cur = self._cur
            cur.high = max(cur.high, h)
            cur.low = min(cur.low, l)
            cur.close = c
            cur.volume += v
        if minute + bar_minutes >= self.anchor + (bucket + 1) * self.period:
            out.append(self._cur)
            self._cur = None
        return out


def median(xs) -> Optional[float]:
    if not xs:
        return None
    s = sorted(xs)
    n = len(s)
    m = n // 2
    return s[m] if n % 2 else 0.5 * (s[m - 1] + s[m])

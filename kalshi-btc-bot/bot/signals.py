"""Momentum feature extraction, scoring, and win-probability model.

Used identically by live/paper trading and the backtester, so backtests test the real logic.

Key idea (and the honest caveat): after 3 minutes, a 15-minute UP/DOWN market already "knows"
how far BTC is from the reference price. Under a pure random walk, P(UP) = Phi(distance / sigma_remaining).
The Kalshi market will usually price close to that. The bot only has an edge if momentum *persists*
beyond what the random walk implies (`momentum_persistence`) or if the market misprices. The backtester
reports an empirical calibration table so you can check whether that persistence actually exists.
"""
from __future__ import annotations

import bisect
import math
from dataclasses import asdict, dataclass, field

from .config import StrategyConfig
from .models import Direction, Tick, norm_cdf


@dataclass
class MomentumFeatures:
    open_price: float
    price_now: float
    reference_price: float
    elapsed_seconds: float
    n_ticks: int
    ret_pct: float                 # % change since open
    dist_bps: float                # (price_now - reference) / reference in bps
    slope_bps_per_min: float       # linear-regression slope of log price
    r2: float                      # trend quality 0..1
    accel_bps_per_min: float       # 2nd-half slope minus 1st-half slope
    efficiency: float              # |net move| / path length, 0..1
    consistency: float             # share of sub-windows moving with the net direction, 0..1
    flow_imbalance: float | None   # (buy_vol - sell_vol) / total, -1..1
    vol_bps_per_min: float         # sigma of 1-minute log returns
    z_score: float                 # dist / (vol * sqrt(elapsed minutes))
    high: float = 0.0
    low: float = 0.0

    def to_dict(self) -> dict:
        return {k: (round(v, 6) if isinstance(v, float) else v) for k, v in asdict(self).items()}


@dataclass
class MomentumSignal:
    direction: Direction
    confidence: float              # 0..100
    composite: float               # -1..1
    components: dict = field(default_factory=dict)
    contradictions: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "direction": self.direction.value,
            "confidence": round(self.confidence, 2),
            "composite": round(self.composite, 4),
            "components": {k: round(v, 4) for k, v in self.components.items()},
            "contradictions": list(self.contradictions),
        }


# ------------------------------------------------------------------ helpers

def resample(ticks: list[Tick], start: float, end: float, step: float = 1.0) -> list[float]:
    """Forward-filled price on a regular grid [start, end]."""
    if not ticks:
        return []
    times = [t.ts for t in ticks]
    out = []
    n = max(1, int(round((end - start) / step)))
    for i in range(n + 1):
        t = start + i * step
        idx = bisect.bisect_right(times, t) - 1
        out.append(ticks[idx].price if idx >= 0 else ticks[0].price)
    return out


def _linreg(ys: list[float]) -> tuple[float, float]:
    """Slope per index step and R^2."""
    n = len(ys)
    if n < 3:
        return 0.0, 0.0
    mx = (n - 1) / 2.0
    my = sum(ys) / n
    sxx = sum((i - mx) ** 2 for i in range(n))
    sxy = sum((i - mx) * (y - my) for i, y in enumerate(ys))
    syy = sum((y - my) ** 2 for y in ys)
    if sxx == 0 or syy == 0:
        return 0.0, 0.0
    slope = sxy / sxx
    r2 = (sxy * sxy) / (sxx * syy)
    return slope, max(0.0, min(1.0, r2))


def vol_from_minute_closes(closes: list[float]) -> float | None:
    """Std-dev of 1-minute log returns, in bps per minute."""
    rets = [math.log(b / a) for a, b in zip(closes, closes[1:]) if a > 0 and b > 0]
    if len(rets) < 5:
        return None
    m = sum(rets) / len(rets)
    var = sum((r - m) ** 2 for r in rets) / (len(rets) - 1)
    return math.sqrt(var) * 1e4


def price_at(ticks: list[Tick], ts: float) -> float | None:
    """Last traded price at or before ts (falls back to the first tick after)."""
    if not ticks:
        return None
    times = [t.ts for t in ticks]
    idx = bisect.bisect_right(times, ts) - 1
    return ticks[idx].price if idx >= 0 else ticks[0].price


# ------------------------------------------------------------------ features

def compute_features(
    ticks: list[Tick],
    open_ts: float,
    now_ts: float,
    reference_price: float | None,
    vol_bps_per_min: float,
    open_price: float | None = None,
) -> MomentumFeatures | None:
    window = [t for t in ticks if open_ts <= t.ts <= now_ts]
    if open_price is None:
        open_price = price_at(ticks, open_ts)
    if open_price is None or not window:
        return None
    reference = reference_price or open_price
    elapsed = max(1.0, now_ts - open_ts)
    # Include the open price as the first grid point.
    series_ticks = [Tick(open_ts, open_price)] + window
    grid = resample(series_ticks, open_ts, now_ts, step=1.0)
    logs = [math.log(p) for p in grid]
    price_now = window[-1].price

    slope_per_s, r2 = _linreg(logs)
    slope_bps_min = slope_per_s * 60 * 1e4
    half = len(logs) // 2
    s1, _ = _linreg(logs[: half + 1])
    s2, _ = _linreg(logs[half:])
    accel = (s2 - s1) * 60 * 1e4

    net = logs[-1] - logs[0]
    path = sum(abs(b - a) for a, b in zip(logs, logs[1:]))
    efficiency = abs(net) / path if path > 0 else 0.0

    k = 6
    seg = max(1, (len(logs) - 1) // k)
    agree = moved = 0
    for i in range(0, len(logs) - 1, seg):
        d = logs[min(i + seg, len(logs) - 1)] - logs[i]
        if abs(d) > 1e-12:
            moved += 1
            if (d > 0) == (net > 0):
                agree += 1
    consistency = agree / moved if moved else 0.0

    buy = sum(t.size for t in window if t.aggressor == "buy")
    sell = sum(t.size for t in window if t.aggressor == "sell")
    flow = (buy - sell) / (buy + sell) if (buy + sell) > 0 else None

    vol = max(vol_bps_per_min, 0.5)
    dist_bps = (price_now - reference) / reference * 1e4
    z = dist_bps / (vol * math.sqrt(elapsed / 60.0))
    prices = [t.price for t in series_ticks]
    return MomentumFeatures(
        open_price=open_price,
        price_now=price_now,
        reference_price=reference,
        elapsed_seconds=elapsed,
        n_ticks=len(window),
        ret_pct=(price_now - open_price) / open_price * 100,
        dist_bps=dist_bps,
        slope_bps_per_min=slope_bps_min,
        r2=r2,
        accel_bps_per_min=accel,
        efficiency=efficiency,
        consistency=consistency,
        flow_imbalance=flow,
        vol_bps_per_min=vol_bps_per_min,
        z_score=z,
        high=max(prices),
        low=min(prices),
    )


# ------------------------------------------------------------------ scoring

WEIGHTS = {"move": 0.35, "trend": 0.20, "efficiency": 0.15, "flow": 0.20, "accel": 0.10}


def score_momentum(f: MomentumFeatures, cfg: StrategyConfig) -> MomentumSignal:
    sgn = 1.0 if f.dist_bps > 0 else -1.0 if f.dist_bps < 0 else 0.0
    if sgn == 0.0 or abs(f.z_score) < 0.05:
        return MomentumSignal(Direction.NONE, 0.0, 0.0, {}, ["no net move from reference"])
    vol = max(f.vol_bps_per_min, 0.5)
    comps = {
        "move": math.tanh(f.z_score / 1.5),
        "trend": (1.0 if f.slope_bps_per_min > 0 else -1.0) * f.r2 if f.slope_bps_per_min else 0.0,
        "efficiency": sgn * f.efficiency,
        "accel": math.tanh(f.accel_bps_per_min / (2.0 * vol)),
    }
    weights = dict(WEIGHTS)
    if f.flow_imbalance is not None:
        comps["flow"] = max(-1.0, min(1.0, f.flow_imbalance * 2.0))
    else:
        weights.pop("flow")
    total_w = sum(weights.values())
    composite = sum(comps[k] * w for k, w in weights.items()) / total_w

    contradictions = []
    if composite * sgn <= 0:
        contradictions.append("composite score opposes the price move")
    if cfg.require_trend_agreement and f.slope_bps_per_min * sgn < 0:
        contradictions.append("regression trend opposes the net move")
    if f.flow_imbalance is not None and f.flow_imbalance * sgn < -cfg.max_flow_contradiction:
        contradictions.append(f"order flow opposes the move ({f.flow_imbalance:+.2f})")
    if comps["accel"] * sgn < -0.6:
        contradictions.append("momentum is sharply decelerating/reversing")

    direction = Direction.UP if sgn > 0 else Direction.DOWN
    confidence = max(0.0, composite * sgn) * 100.0
    return MomentumSignal(direction, confidence, composite, comps, contradictions)


def estimate_p_up(f: MomentumFeatures, seconds_remaining: float, cfg: StrategyConfig) -> float:
    """P(BTC finishes at/above reference). Random-walk baseline plus optional momentum persistence,
    shrunk toward 0.5 as a model-uncertainty haircut."""
    mins = max(seconds_remaining, 1.0) / 60.0
    vol = max(f.vol_bps_per_min, 0.5)
    sigma = vol * math.sqrt(mins)
    drift = cfg.momentum_persistence * f.slope_bps_per_min * mins * f.r2
    p_raw = norm_cdf((f.dist_bps + drift) / sigma)
    p = 0.5 + (p_raw - 0.5) * cfg.probability_shrink
    return min(0.97, max(0.03, p))


def random_walk_p_up(dist_bps: float, vol_bps_per_min: float, seconds_remaining: float) -> float:
    sigma = max(vol_bps_per_min, 0.5) * math.sqrt(max(seconds_remaining, 1.0) / 60.0)
    return norm_cdf(dist_bps / sigma)

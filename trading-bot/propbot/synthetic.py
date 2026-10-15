"""Synthetic MNQ/NQ regular-trading-hours bars for plumbing tests and null-hypothesis checks.

READ THIS BEFORE TRUSTING ANY RESULT PRODUCED ON THIS DATA
----------------------------------------------------------
Edges found on synthetic data are NOT evidence of a real edge. This generator
is a statistical cartoon of the Nasdaq-100 future, built only to

* exercise the backtester / Monte-Carlo / rules code on realistic-looking data
  (realistic volatility, tails, gaps, intraday seasonality), and
* act as a *fair* environment: no strategy-specific edge has been planted. With
  ``regimes=False`` the price is a pure martingale (zero drift, no return
  autocorrelation), so ANY strategy that is reliably profitable after costs on
  that setting reveals a lookahead/fill bug, not alpha.

With ``regimes=True`` (default) each day is randomly a trend, range or reversal
day (25 / 50 / 25 %). Trend days carry a drift plus mild positive return
autocorrelation; range days mean-revert toward the open with mild negative
autocorrelation; reversal days drift one way then the other. Day type and
direction are drawn independently of everything observable before the open, and
the autocorrelations roughly cancel across day types. Some strategy families
(breakouts on trend days, fades on range days) can still look good or bad
purely because of these hand-picked mixing proportions and drift sizes, which
are guesses, not estimates from real data. Treat synthetic P&L as a smoke test;
validate on real exported data (see :mod:`propbot.data`).

Model summary (all on a 1-minute base grid, 09:30-16:00 ET, 390 bars/day):

* Daily volatility follows a GARCH(1,1)-like recursion targeting ~1.15 % RTH
  open-to-close noise vol; close-to-close realises ~1.2-1.5 % with regimes on
  (~1.1-1.25 % for the martingale null), including the overnight gap.
* Intraday U-shaped volatility: highest after the open, lunch lull, rising into
  the close, plus slowly varying intraday volatility clustering.
* Student-t (df=4) innovations, scaled to unit variance.
* Overnight gaps (fat-tailed, ~40 % of the day's vol).
* ~10 % of days have a "news" jump (often at 10:00 or 14:00 ET) followed by
  decaying elevated volatility.
* High/low come from a Brownian bridge between open and close inside each bar,
  so bars are internally consistent; all prices are on 0.25 ticks.
* Weekends are skipped; exchange holidays are not modelled.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .data import resample

__all__ = ["generate_mnq"]

TICK = 0.25
BARS_PER_DAY = 390               # 1-minute bars 09:30-16:00
TARGET_DAY_VOL = 0.0115          # RTH open->close log-vol (unconditional)
GARCH_ALPHA, GARCH_BETA = 0.07, 0.90
GAP_VOL_FRAC = 0.40
T_DF = 4.0
P_DAY_TYPES = (0.25, 0.50, 0.25)  # trend, range, reversal
P_NEWS = 0.10
BRIDGE_STEPS = 8


def _intraday_variance_weights(n: int = BARS_PER_DAY) -> np.ndarray:
    """U-shaped per-minute variance weights summing to 1."""
    m = np.arange(n, dtype=float)
    w = 1.0 + 3.0 * np.exp(-m / 20.0) + 1.2 * np.exp(-(n - 1 - m) / 25.0)
    w *= 1.0 - 0.45 * np.exp(-(((m - 180.0) / 70.0) ** 2))  # lunch lull ~12:30
    return w / w.sum()


def _student_t(rng: np.random.Generator, size, df: float = T_DF) -> np.ndarray:
    return rng.standard_t(df, size=size) * np.sqrt((df - 2.0) / df)


def _simulate_day(rng, sigma_day, w, regimes):
    """Return (per-minute log returns, per-minute noise scale, sum of pure noise).

    The noise sum (no drift / mean reversion) drives the GARCH update so the
    regime structure does not feed back into the volatility level."""
    n = len(w)
    # intraday vol clustering: AR(1) log-vol factor with E[scale^2] = 1
    s_h = 0.25
    h = np.empty(n)
    h[0] = rng.normal(0, s_h)
    eta = rng.normal(0, s_h * np.sqrt(1 - 0.97**2), n)
    for k in range(1, n):
        h[k] = 0.97 * h[k - 1] + eta[k]
    scale = sigma_day * np.sqrt(w) * np.exp(h - s_h**2)

    if rng.random() < P_NEWS:
        k0 = int(rng.choice([30, 270, int(rng.integers(5, n - 20))], p=[0.4, 0.3, 0.3]))
        boost = 1.0 + 2.5 * np.exp(-np.maximum(np.arange(n) - k0, 0) / 10.0) * (np.arange(n) >= k0)
        scale = scale * boost
        jump_bar, jump = k0, rng.choice([-1, 1]) * sigma_day * rng.uniform(0.15, 0.5)
    else:
        jump_bar, jump = -1, 0.0

    noise = _student_t(rng, n) * scale
    if jump_bar >= 0:
        noise[jump_bar] += jump

    drift = np.zeros(n)
    phi, kappa = 0.0, 0.0
    if regimes:
        kind = rng.choice(3, p=P_DAY_TYPES)
        sgn = rng.choice([-1.0, 1.0])
        if kind == 0:  # trend
            total = sgn * rng.uniform(0.8, 1.6) * sigma_day
            shape = np.linspace(1.3, 0.7, n)
            drift = total * shape / shape.sum()
            phi = 0.06
        elif kind == 1:  # range / mean-reverting toward the open
            phi = -0.05
            kappa = np.log(2) / rng.uniform(60, 150)
        else:  # reversal
            f = rng.uniform(0.25, 0.55)
            k = max(int(f * n), 1)
            drift[:k] = sgn * rng.uniform(0.5, 1.0) * sigma_day / k
            drift[k:] = -sgn * rng.uniform(0.6, 1.3) * sigma_day / (n - k)

    noise_sum = float(noise.sum())
    if phi == 0.0 and kappa == 0.0:
        return drift + noise, scale, noise_sum

    r = np.empty(n)
    x = 0.0          # log price relative to the open
    prev_u = 0.0     # previous return's autocorrelated innovation
    for k in range(n):
        u = noise[k] + phi * prev_u
        rk = drift[k] + u - kappa * x
        r[k] = rk
        x += rk
        prev_u = u
    return r, scale, noise_sum


def generate_mnq(
    n_days: int,
    seed: int = 0,
    start_price: float = 20000.0,
    freq: str = "1min",
    *,
    start_date: str = "2023-01-03",
    regimes: bool = True,
) -> pd.DataFrame:
    """Generate ``n_days`` weekdays of RTH bars (09:30-16:00 ET) in the Bars format.

    Parameters
    ----------
    n_days : number of trading days (weekdays from ``start_date``).
    seed : RNG seed; same seed -> identical output.
    start_price : first open (roughly; the first day also gets a gap).
    freq : bar size, a whole number of minutes (``"1min"``, ``"5min"``, ...).
    regimes : ``False`` gives a pure martingale null (no drift/autocorrelation).

    See the module docstring: results on this data are not evidence of real edge.
    """
    if n_days <= 0:
        raise ValueError("n_days must be positive")
    step = pd.Timedelta(freq)
    if step < pd.Timedelta("1min") or step % pd.Timedelta("1min") != pd.Timedelta(0):
        raise ValueError("freq must be a whole number of minutes")

    rng = np.random.default_rng(seed)
    w = _intraday_variance_weights()
    n = BARS_PER_DAY
    omega = TARGET_DAY_VOL**2 * (1.0 - GARCH_ALPHA - GARCH_BETA)
    c_norm = 1.0 + GAP_VOL_FRAC**2  # approx. E[eps^2] / sigma^2

    logp = np.empty(n_days * n)
    scales = np.empty(n_days * n)
    opens_log = np.empty(n_days * n)
    sigma2 = TARGET_DAY_VOL**2 * np.exp(rng.normal(0, 0.3))
    prev_close = np.log(start_price)
    for d in range(n_days):
        sigma = float(np.clip(np.sqrt(sigma2), 0.004, 0.045))
        gap = float(_student_t(rng, 1)[0]) * GAP_VOL_FRAC * sigma
        day_open = prev_close + gap
        r, sc, noise_sum = _simulate_day(rng, sigma, w, regimes)
        path = day_open + np.cumsum(r)
        sl = slice(d * n, (d + 1) * n)
        logp[sl] = path
        scales[sl] = sc
        opens_log[sl] = np.concatenate([[day_open], path[:-1]])
        eps = gap + noise_sum
        z2 = min(eps**2 / (sigma**2 * c_norm), 25.0)
        sigma2 = omega + GARCH_ALPHA * sigma**2 * z2 + GARCH_BETA * sigma**2
        prev_close = path[-1]

    # intrabar extremes: Brownian bridge from open to close with the bar's scale
    K = BRIDGE_STEPS
    inc = rng.normal(size=(len(logp), K)) * (scales[:, None] / np.sqrt(K))
    walk = np.cumsum(inc, axis=1)
    frac = np.arange(1, K + 1) / K
    bridge = walk - frac[None, :] * walk[:, -1:]
    inner = opens_log[:, None] + frac[None, :] * (logp - opens_log)[:, None] + bridge
    hi_log = np.maximum(inner.max(axis=1), np.maximum(opens_log, logp))
    lo_log = np.minimum(inner.min(axis=1), np.minimum(opens_log, logp))

    def to_ticks(a):
        return np.round(np.exp(a) / TICK) * TICK

    o, c, h, lo = to_ticks(opens_log), to_ticks(logp), to_ticks(hi_log), to_ticks(lo_log)
    h = np.maximum(h, np.maximum(o, c))
    lo = np.minimum(lo, np.minimum(o, c))

    # volume: U-shaped profile, scales with vol regime and bar move, lognormal noise
    prof = np.tile(np.sqrt(w / w.mean()), n_days)
    absz = np.abs(logp - opens_log) / np.maximum(scales, 1e-12)
    vol_level = scales / np.tile(np.sqrt(w), n_days) / TARGET_DAY_VOL
    vol = 900.0 * prof * vol_level * (0.6 + 0.4 * absz) * rng.lognormal(0.0, 0.35, len(logp))
    vol = np.maximum(np.round(vol), 1.0)

    days = pd.bdate_range(start_date, periods=n_days)
    minutes = pd.to_timedelta(np.arange(n), unit="min") + pd.Timedelta(hours=9, minutes=30)
    naive = (days.values[:, None] + minutes.values[None, :]).ravel()
    idx = pd.DatetimeIndex(naive).tz_localize("America/New_York")
    idx.name = "time"
    bars = pd.DataFrame({"open": o, "high": h, "low": lo, "close": c, "volume": vol}, index=idx)
    if step != pd.Timedelta("1min"):
        bars = resample(bars, freq)
    return bars

"""Monte Carlo pass-probability estimation for prop-firm evaluations.

The core is ``simulate_paths``: a numpy re-implementation of ``propbot.rules.EvalAccount`` that
runs thousands of evaluation attempts at once (loop over days, vectorised over simulations).
It is tested to agree exactly with the scalar ``rules.simulate_eval``.

Public API
----------
* ``pass_rate(daily_results, rules, n_sims, max_days, block, seed)`` - block-bootstrap historical
  / backtested days and estimate pass / fail / timeout probabilities and cost per pass.
* ``pass_rate_from_trade_model(win_prob, avg_win, avg_loss, trades_per_day, ...)`` - what-if
  exploration from a simple binary trade distribution.
* ``random_walk_baseline(rules, daily_sigma, ...)`` - zero-edge pass probability (continuous
  Brownian intraday paths) plus analytic references.
* ``brownian_pass_probability`` - closed-form pass probability for a drifted Brownian P&L with a
  static or continuously-trailing floor.
* ``apply_day_limits`` / ``sample_trade_counts`` - build synthetic days from per-trade P&L with
  a bot-level daily stop / profit cap (shared with ``propbot.sizing``).

Accounting conventions (``summarize_paths``)
--------------------------------------------
Each simulated attempt ends in pass, fail, or *timeout* (still active after ``max_days`` calendar
days). Timeouts are counted as non-passing attempts, so ``expected_attempts_per_pass = 1 /
pass_prob`` and ``expected_cost_per_pass = eval_fee + reset_fee * (attempts - 1)`` (the first
attempt is bought with ``eval_fee``, every retry costs ``reset_fee``). ``pass_prob_resolved`` =
P(pass | resolved) is reported too, for evals without a time limit.
"""
from __future__ import annotations

import math
from typing import Optional, Sequence, Union

import numpy as np

from .interfaces import DayResult, EvalRules
from .rules import (EPS, R_CONSISTENCY, R_DLL, R_MAX_LOSS, R_PASSED, R_PASSED_EXT, R_TIMEOUT,
                    EvalOptions, consistency_active, day_intraday_low, day_traded,
                    resolve_options)

# outcome codes used by simulate_paths
ST_ACTIVE, ST_PASSED, ST_FAILED = 0, 1, 2
RC_TIMEOUT, RC_PASSED, RC_PASSED_EXT, RC_MAX_LOSS, RC_DLL, RC_CONSISTENCY = range(6)
REASON_NAMES = {RC_TIMEOUT: R_TIMEOUT, RC_PASSED: R_PASSED, RC_PASSED_EXT: R_PASSED_EXT,
                RC_MAX_LOSS: R_MAX_LOSS, RC_DLL: R_DLL, RC_CONSISTENCY: R_CONSISTENCY}

# Synthetic days built from trades (trade model, sizing, random walk) do not embed the firm's
# DLL liquidation, so for them the firm flattening at the limit is modelled explicitly.
SYNTHETIC_DAY_OPTIONS = EvalOptions(dll_flatten_at_limit=True)

ArrayLike = Union[Sequence[float], np.ndarray]


# ---------------------------------------------------------------------------- data plumbing
def days_to_arrays(days: Union[Sequence[DayResult], ArrayLike]):
    """DayResults -> (pnl, intraday_low, traded) float/float/bool arrays.

    A plain numeric 1-D sequence is accepted as daily P&L (intraday low = min(pnl, 0), every
    non-zero day counts as traded).
    """
    if len(days) == 0:
        raise ValueError("need at least one day")
    first = days[0]
    if isinstance(first, DayResult):
        pnl = np.array([float(d.pnl) for d in days])
        low = np.array([day_intraday_low(d) for d in days])
        traded = np.array([day_traded(d) for d in days], dtype=bool)
    else:
        pnl = np.asarray(days, dtype=float).ravel()
        low = np.minimum(pnl, 0.0)
        traded = pnl != 0.0
    return pnl, low, traded


def bootstrap_indices(n_obs: int, n_sims: int, n_days: int, block: int = 1,
                      rng: Optional[np.random.Generator] = None) -> np.ndarray:
    """(n_sims, n_days) indices from a circular block bootstrap with block length ``block``.

    Each block starts at a uniform random index and takes ``block`` consecutive observations
    (wrapping around), which preserves serial correlation up to lag ``block - 1``.
    """
    rng = rng if rng is not None else np.random.default_rng()
    block = max(1, min(int(block), n_obs))
    n_blocks = -(-n_days // block)
    starts = rng.integers(0, n_obs, size=(n_sims, n_blocks))
    idx = (starts[:, :, None] + np.arange(block)[None, None, :]) % n_obs
    return idx.reshape(n_sims, n_blocks * block)[:, :n_days]


# ---------------------------------------------------------------------------- core simulator
def simulate_paths(pnl: np.ndarray, low: Optional[np.ndarray] = None,
                   traded: Optional[np.ndarray] = None, rules: EvalRules = EvalRules(),
                   options: Optional[EvalOptions] = None, **overrides) -> dict:
    """Vectorised evaluation of many day-sequences. Row = one attempt, column = one day.

    ``pnl``/``low``/``traded`` have shape (n_sims, n_days). ``low`` is the intraday low of
    cumulative P&L (defaults to min(pnl, 0)); ``traded`` defaults to ``pnl != 0 or low != 0``.
    Semantics are identical to ``rules.EvalAccount.apply_day`` (see ``propbot.rules``).

    Returns a dict of arrays: ``status`` (0 active/timeout, 1 passed, 2 failed), ``reason``
    (codes, see ``REASON_NAMES``), ``days_used``, ``days_traded``, ``final_balance``,
    ``consistency_extended``, ``best_day``.
    """
    o = resolve_options(options, **overrides)
    pnl = np.atleast_2d(np.asarray(pnl, dtype=float))
    n, T = pnl.shape
    low = np.minimum(pnl, 0.0) if low is None else np.atleast_2d(np.asarray(low, dtype=float))
    low = np.minimum(np.minimum(low, pnl), 0.0)
    if traded is None:
        traded = (pnl != 0.0) | (low != 0.0)
    traded = np.atleast_2d(np.asarray(traded, dtype=bool))

    r = rules
    start = float(r.start_balance)
    bal = np.full(n, start)
    eod_high = bal.copy()
    floor = np.full(n, start - r.max_loss)
    best = np.zeros(n)
    dtr = np.zeros(n, dtype=np.int64)
    status = np.zeros(n, dtype=np.int8)
    reason = np.zeros(n, dtype=np.int8)
    used = np.zeros(n, dtype=np.int64)
    extended = np.zeros(n, dtype=bool)
    dll = r.daily_loss_limit
    cons_on = consistency_active(r, o)
    c = r.consistency

    for t in range(T):
        act = status == ST_ACTIVE
        if not act.any():
            break
        used[act] += 1
        dtr[act & traded[:, t]] += 1
        p = pnl[:, t]
        lo = low[:, t]
        if dll is not None:
            hit = lo <= -dll + EPS
            if o.dll_flatten_at_limit:
                p = np.where(hit, -float(dll), p)
                lo = np.where(hit, -float(dll), lo)
        else:
            hit = np.zeros(n, dtype=bool)

        breach = act & (bal + lo <= floor + EPS)
        bal[breach] = floor[breach]
        status[breach], reason[breach] = ST_FAILED, RC_MAX_LOSS
        act &= ~breach

        if o.dll_is_hard_breach:
            hard = act & hit
            bal[hard] += p[hard]
            status[hard], reason[hard] = ST_FAILED, RC_DLL
            act &= ~hard

        bal = np.where(act, bal + p, bal)
        best = np.where(act & (p > best), p, best)
        eod_breach = act & (bal <= floor + EPS)          # guard, mirrors rules.py
        status[eod_breach], reason[eod_breach] = ST_FAILED, RC_MAX_LOSS
        act &= ~eod_breach

        eod_high = np.where(act, np.maximum(eod_high, bal), eod_high)
        nf = eod_high - r.max_loss
        if r.trailing_lock_at is not None:
            nf = np.minimum(nf, r.trailing_lock_at)
        floor = np.where(act, np.maximum(floor, nf), floor)

        profit = bal - start
        at_tgt = act & (profit >= r.profit_target - EPS)
        if cons_on:
            consistent = (profit > 0) & (best <= c * profit + EPS)
        else:
            consistent = np.ones(n, dtype=bool)
        if o.consistency_mode == "extend":
            extended |= at_tgt & ~consistent
        ready = at_tgt & (dtr >= r.min_days)
        win = ready & consistent
        status[win] = ST_PASSED
        reason[win] = np.where(extended[win], RC_PASSED_EXT, RC_PASSED)
        if o.consistency_mode == "fail":
            cf = ready & ~consistent
            status[cf], reason[cf] = ST_FAILED, RC_CONSISTENCY

    return dict(status=status, reason=reason, days_used=used, days_traded=dtr,
                final_balance=bal, consistency_extended=extended, best_day=best)


def summarize_paths(res: dict, rules: EvalRules = EvalRules()) -> dict:
    """Aggregate ``simulate_paths`` output into probabilities, days and $ cost per pass."""
    status, reason, used = res["status"], res["reason"], res["days_used"]
    n = len(status)
    passed = status == ST_PASSED
    failed = status == ST_FAILED
    p = passed.mean()
    f = failed.mean()
    t = 1.0 - p - f
    pass_days = used[passed]
    attempts = 1.0 / p if p > 0 else math.inf
    cost = rules.eval_fee + rules.reset_fee * (attempts - 1.0) if p > 0 else math.inf
    mean_days_attempt = float(used.mean())
    fail_reasons = {}
    for code in (RC_MAX_LOSS, RC_DLL, RC_CONSISTENCY, RC_TIMEOUT):
        mask = reason == code
        if code == RC_TIMEOUT:
            mask = status == ST_ACTIVE
        if mask.any():
            fail_reasons[REASON_NAMES[code]] = float(mask.mean())
    return dict(
        pass_prob=float(p), fail_prob=float(f), timeout_prob=float(t),
        pass_prob_se=float(math.sqrt(p * (1 - p) / n)) if n else math.nan,
        pass_prob_resolved=float(p / (p + f)) if (p + f) > 0 else math.nan,
        median_days_to_pass=float(np.median(pass_days)) if pass_days.size else math.nan,
        mean_days_to_pass=float(pass_days.mean()) if pass_days.size else math.nan,
        mean_days_per_attempt=mean_days_attempt,
        expected_attempts_per_pass=float(attempts),
        expected_cost_per_pass=float(cost),
        expected_days_per_pass=float(mean_days_attempt * attempts) if p > 0 else math.inf,
        consistency_extension_rate=float(res["consistency_extended"][passed].mean())
        if pass_days.size else math.nan,
        fail_reasons=fail_reasons,
        n_sims=int(n),
    )


# ---------------------------------------------------------------------------- bootstrap
def pass_rate(daily_results: Union[Sequence[DayResult], ArrayLike], rules: EvalRules = EvalRules(),
              n_sims: int = 10_000, max_days: Optional[int] = 60, block: int = 1, seed: int = 0,
              options: Optional[EvalOptions] = None, **overrides) -> dict:
    """Bootstrap pass probability from observed (backtested) days.

    Day sequences of length ``max_days`` are drawn with a circular block bootstrap (block length
    ``block``; 1 = iid days) and each is run through the evaluation rules. ``max_days=None``
    means 1000 days (effectively "until resolved"). Default options treat DayResults as already
    reflecting any DLL stop (``dll_flatten_at_limit=False``); see ``propbot.rules``.

    Returns the ``summarize_paths`` dict: ``pass_prob``, ``fail_prob``, ``timeout_prob``,
    ``pass_prob_se``, ``pass_prob_resolved``, ``median_days_to_pass``, ``mean_days_to_pass``,
    ``mean_days_per_attempt``, ``expected_attempts_per_pass``, ``expected_cost_per_pass``,
    ``expected_days_per_pass``, ``consistency_extension_rate``, ``fail_reasons`` (fraction of
    all sims ending with each non-pass reason), ``n_sims``; plus ``mean_day_pnl``,
    ``std_day_pnl``, ``n_obs``, ``block``.
    """
    pnl, low, traded = days_to_arrays(daily_results)
    T = 1000 if max_days is None else int(max_days)
    rng = np.random.default_rng(seed)
    idx = bootstrap_indices(len(pnl), int(n_sims), T, block, rng)
    res = simulate_paths(pnl[idx], low[idx], traded[idx], rules, options, **overrides)
    out = summarize_paths(res, rules)
    out.update(mean_day_pnl=float(pnl.mean()), std_day_pnl=float(pnl.std()),
               n_obs=int(len(pnl)), block=int(block))
    return out


# ---------------------------------------------------------------------------- trades -> days
def sample_trade_counts(trades_per_day, size: int, rng: np.random.Generator) -> np.ndarray:
    """Draw ``size`` trades-per-day counts.

    ``trades_per_day``: int (fixed); non-integer float (Poisson mean); dict {count: prob};
    or a sequence of observed counts (resampled uniformly).
    """
    if isinstance(trades_per_day, dict):
        k = np.array(list(trades_per_day.keys()), dtype=np.int64)
        w = np.array(list(trades_per_day.values()), dtype=float)
        return rng.choice(k, size=size, p=w / w.sum())
    if np.isscalar(trades_per_day):
        x = float(trades_per_day)
        if x.is_integer():
            return np.full(size, int(x), dtype=np.int64)
        return rng.poisson(x, size=size).astype(np.int64)
    arr = np.asarray(trades_per_day, dtype=np.int64).ravel()
    return rng.choice(arr, size=size)


def apply_day_limits(trades: np.ndarray, valid: Optional[np.ndarray] = None,
                     daily_stop: Optional[float] = None, daily_profit_cap: Optional[float] = None,
                     mae: Optional[np.ndarray] = None):
    """Collapse per-trade P&L rows (one row = one day, in time order) into day P&L and low.

    Bot logic: after each *closed* trade, if cumulative day P&L <= -daily_stop or >=
    daily_profit_cap, no further trades are taken. The stop / cap can therefore be overshot by
    the trade that crosses it (that is what a closed-trade daily stop does in practice). The
    firm's DLL is *not* applied here; ``simulate_paths`` handles it.

    ``mae`` (same shape, <= 0): per-trade maximum adverse excursion in $, so that the intraday
    low includes open-trade drawdown: low = min over taken trades of
    (cum_before + mae, cum_after), and 0.

    Returns (pnl, low, n_taken) arrays of length n_rows.
    """
    trades = np.atleast_2d(np.asarray(trades, dtype=float))
    n, K = trades.shape
    if valid is None:
        valid = np.ones_like(trades, dtype=bool)
    if K == 0:
        z = np.zeros(n)
        return z, z.copy(), np.zeros(n, dtype=np.int64)
    t = np.where(valid, trades, 0.0)
    cum = np.cumsum(t, axis=1)
    hit = np.zeros_like(valid)
    if daily_stop is not None:
        hit |= cum <= -float(daily_stop) + EPS
    if daily_profit_cap is not None:
        hit |= cum >= float(daily_profit_cap) - EPS
    hit &= valid
    any_hit = hit.any(axis=1)
    last = np.where(any_hit, hit.argmax(axis=1), K - 1)
    taken = valid & (np.arange(K)[None, :] <= last[:, None])
    pnl = np.where(taken, t, 0.0).sum(axis=1)
    low = np.minimum(np.where(taken, cum, 0.0).min(axis=1), 0.0)
    if mae is not None:
        m = np.minimum(np.where(valid, np.asarray(mae, dtype=float), 0.0), 0.0)
        path_mae = np.where(taken, cum - t + m, 0.0)
        low = np.minimum(low, path_mae.min(axis=1))
    return pnl, low, taken.sum(axis=1)


def pass_rate_from_trade_model(win_prob: float, avg_win: float, avg_loss: float,
                               trades_per_day=3, rules: EvalRules = EvalRules(),
                               n_sims: int = 10_000, max_days: int = 60, seed: int = 0,
                               daily_stop: Optional[float] = None,
                               daily_profit_cap: Optional[float] = None,
                               options: Optional[EvalOptions] = None, **overrides) -> dict:
    """Pass probability for i.i.d. binary trades: +avg_win w.p. win_prob, else -|avg_loss|.

    ``trades_per_day`` as in ``sample_trade_counts``. Days are built with ``apply_day_limits``
    (bot daily stop / profit cap) and evaluated with the firm DLL liquidating at the limit
    (``SYNTHETIC_DAY_OPTIONS``) unless ``options`` says otherwise. Intraday low is at closed-trade
    granularity (avg_loss is treated as the stop, so open drawdown ~ realised loss).

    Returns the ``summarize_paths`` dict plus ``edge_per_trade``, ``mean_day_pnl``,
    ``std_day_pnl`` (of the capped synthetic days).
    """
    rng = np.random.default_rng(seed)
    n_days = int(n_sims) * int(max_days)
    counts = sample_trade_counts(trades_per_day, n_days, rng)
    K = int(counts.max()) if counts.size else 0
    wins = rng.random((n_days, K)) < win_prob
    tr = np.where(wins, float(avg_win), -abs(float(avg_loss)))
    valid = np.arange(K)[None, :] < counts[:, None]
    pnl, low, _ = apply_day_limits(tr, valid, daily_stop, daily_profit_cap)
    traded = counts > 0
    opts = options if options is not None else SYNTHETIC_DAY_OPTIONS
    shape = (int(n_sims), int(max_days))
    res = simulate_paths(pnl.reshape(shape), low.reshape(shape), traded.reshape(shape), rules,
                         opts, **overrides)
    out = summarize_paths(res, rules)
    out.update(edge_per_trade=float(win_prob * avg_win - (1 - win_prob) * abs(avg_loss)),
               mean_day_pnl=float(pnl.mean()), std_day_pnl=float(pnl.std()))
    return out


# ---------------------------------------------------------------------------- baselines
def brownian_pass_probability(daily_mean: float, daily_std: float, target: float,
                              max_loss: float, trailing: bool = False) -> float:
    """Closed-form P(reach +target before the floor) for P&L = Brownian motion with drift.

    gamma = 2 * mean / std^2.
    * static floor at -max_loss (gambler's ruin):
      (1 - exp(-gamma*D)) / (1 - exp(-gamma*(a+D)))  ->  D / (a + D) at zero drift.
    * continuously trailing floor (running max - D; Lehoczky 1977):
      exp(-a * gamma / (exp(gamma*D) - 1))  ->  exp(-a / D) at zero drift.

    The EOD-trailing rule sits between these two (it trails, but only at day ends). Ignores
    consistency, min days, DLL and time limits.
    """
    a, D = float(target), float(max_loss)
    if daily_std <= 0:
        return 1.0 if daily_mean > 0 else 0.0
    g = 2.0 * daily_mean / daily_std ** 2
    if abs(g) * (a + D) < 1e-9:
        return math.exp(-a / D) if trailing else D / (a + D)
    if trailing:
        return math.exp(-a * g / math.expm1(g * D))
    return -math.expm1(-g * D) / -math.expm1(-g * (a + D))


def random_walk_days(n_sims: int, n_days: int, daily_sigma: float, daily_mean: float = 0.0,
                     rng: Optional[np.random.Generator] = None):
    """(pnl, low) arrays for days whose intraday P&L is a continuous Brownian motion.

    The intraday minimum is sampled exactly from the Brownian-bridge minimum given the close X:
    ``min = (X - sqrt(X^2 - 2 sigma^2 ln U)) / 2``, U ~ Uniform(0, 1].
    """
    rng = rng if rng is not None else np.random.default_rng()
    x = rng.normal(daily_mean, daily_sigma, size=(n_sims, n_days))
    u = 1.0 - rng.random((n_sims, n_days))  # (0, 1]
    m = 0.5 * (x - np.sqrt(x * x - 2.0 * daily_sigma ** 2 * np.log(u)))
    return x, np.minimum(m, 0.0)


def random_walk_baseline(rules: EvalRules = EvalRules(), daily_sigma: float = 300.0,
                         n_sims: int = 10_000, max_days: int = 250, seed: int = 0,
                         daily_mean: float = 0.0, options: Optional[EvalOptions] = None,
                         **overrides) -> dict:
    """Pass probability of a zero-edge (by default) trader under ``rules``.

    Daily P&L ~ N(daily_mean, daily_sigma^2) with a continuous Brownian intraday path (so the
    intraday floor / DLL tests see the true path minimum). Every day counts as traded; the firm
    DLL flattens at the limit. Returns the ``summarize_paths`` dict plus analytic references:
    ``analytic_static_floor`` (gambler's ruin, max_loss / (max_loss + target) at zero drift =
    1000/2250 = 0.444) and ``analytic_trailing_continuous`` (exp(-target/max_loss) = 0.287).
    The real rules land below/around these because of EOD trailing, the DLL, consistency and
    the time limit.
    """
    rng = np.random.default_rng(seed)
    pnl, low = random_walk_days(int(n_sims), int(max_days), daily_sigma, daily_mean, rng)
    opts = options if options is not None else SYNTHETIC_DAY_OPTIONS
    res = simulate_paths(pnl, low, np.ones_like(pnl, dtype=bool), rules, opts, **overrides)
    out = summarize_paths(res, rules)
    out.update(
        daily_sigma=float(daily_sigma), daily_mean=float(daily_mean),
        analytic_static_floor=brownian_pass_probability(daily_mean, daily_sigma,
                                                        rules.profit_target, rules.max_loss),
        analytic_trailing_continuous=brownian_pass_probability(
            daily_mean, daily_sigma, rules.profit_target, rules.max_loss, trailing=True),
    )
    return out

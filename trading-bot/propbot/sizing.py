"""Position size and daily stop / profit-cap optimisation for passing the evaluation.

Key insight
-----------
The Lucid 25K EOD eval asks for +$1,250 before a $1,000 trailing drawdown: a target:drawdown
ratio of only 1.25:1. Model the account's P&L as a random walk with per-day mean ``mu`` and
standard deviation ``sigma``. Trading ``k`` contracts scales *both* by ``k``, so the per-day
Sharpe ``mu/sigma`` is unchanged, but the barriers (fixed in $) shrink in units of daily sigma.
The gambler's-ruin pass probability with drift depends on ``gamma = 2*mu/sigma^2`` -> ``2*mu /
(k*sigma^2)``: it *falls* as ``k`` grows and tends to the zero-edge value (~44% static floor,
~29% continuously trailing floor, lower still after consistency/DLL) when the size is so large
that a couple of days decide the outcome. A small, real edge only converts into a high pass
probability when the size is small enough that many days (many independent bets) are needed,
i.e. the edge gets time to dominate the noise. The cost of small size is time (more days ->
timeouts and subscription fees), so the optimum is the largest size whose pass probability has
not yet collapsed toward the coin-flip baseline.

Per-day caps reshape the day distribution:
* a **daily stop** truncates the left tail, so one bad day cannot consume the whole $1,000
  trailing room (and the firm's $600 DLL caps it anyway);
* a **daily profit cap** near ``consistency * target`` ($625) keeps every winning day consistency
  -compliant, so the target is not silently raised to 2x the best day, and it locks in good days
  before they give back open profit that would otherwise have lifted the EOD high-water mark.
  Too tight a cap cuts the right tail that pays for the losers and lowers expectancy.

``optimize_day_plan`` measures these trade-offs on *your* trade distribution by resampling
trades into synthetic days and running the evaluation Monte Carlo for every combination.
"""
from __future__ import annotations

import itertools
import math
from typing import Optional, Sequence

import numpy as np
import pandas as pd

from .interfaces import CONTRACTS, ContractSpec, EvalRules
from .montecarlo import (SYNTHETIC_DAY_OPTIONS, apply_day_limits, sample_trade_counts,
                         simulate_paths, summarize_paths)
from .rules import EPS, EvalOptions

_DEFAULT_QTY = (1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20)


def max_qty(rules: EvalRules, contract: ContractSpec) -> int:
    """Largest contract count allowed by ``rules.max_minis`` for ``contract``."""
    return int(math.floor(rules.max_minis / contract.mini_equivalent + EPS))


def default_qty_list(rules: EvalRules, contract: ContractSpec) -> list[int]:
    q = max_qty(rules, contract)
    if q <= 10:
        return list(range(1, q + 1))
    return sorted({x for x in _DEFAULT_QTY if x <= q} | {q})


def default_daily_stops(rules: EvalRules) -> list[Optional[float]]:
    dll = rules.daily_loss_limit if rules.daily_loss_limit is not None else 0.6 * rules.max_loss
    return [None, 0.25 * dll, 0.5 * dll, 0.75 * dll]


def default_profit_caps(rules: EvalRules) -> list[Optional[float]]:
    c = rules.consistency if rules.consistency and 0 < rules.consistency < 1 else 0.5
    base = c * rules.profit_target
    return [None, 0.5 * base, 0.8 * base, base]


def optimize_day_plan(trade_pnls_per_contract: Sequence[float], trades_per_day,
                      rules: EvalRules = EvalRules(),
                      contract: ContractSpec = CONTRACTS["MNQ"],
                      qty_list: Optional[Sequence[int]] = None,
                      daily_stops: Optional[Sequence[Optional[float]]] = None,
                      daily_profit_caps: Optional[Sequence[Optional[float]]] = None,
                      n_sims: int = 4000, max_days: int = 60, seed: int = 0,
                      trade_mae_per_contract: Optional[Sequence[float]] = None,
                      sort_by: str = "pass_prob", options: Optional[EvalOptions] = None,
                      **overrides) -> pd.DataFrame:
    """Rank (qty, daily_stop, daily_profit_cap) plans by evaluation pass probability.

    Parameters
    ----------
    trade_pnls_per_contract : per-trade *net* $ P&L for 1 contract (commissions + slippage
        included), e.g. ``[t.pnl / t.qty for t in trades]``. P&L scales linearly with qty.
    trades_per_day : int, Poisson mean (float), {count: prob} dict, or observed daily counts
        (see ``montecarlo.sample_trade_counts``). Zero-trade days consume calendar days but do
        not count as traded days.
    qty_list : contract counts to test; each must satisfy ``qty * mini_equivalent <= max_minis``
        (ValueError otherwise). Default: a spread up to the maximum.
    daily_stops / daily_profit_caps : $ thresholds on the day's closed P&L (None = off). After
        a closed trade crosses one, no new trades that day (so they can be overshot by one
        trade). Defaults: stops at 0/25/50/75% of the DLL, caps at 0/50/80/100% of
        ``consistency * target``.
    trade_mae_per_contract : optional per-trade max adverse excursion ($, <= 0, aligned with
        ``trade_pnls_per_contract``) so intraday lows include open-trade drawdown.

    Method: one common set of random draws (trade counts per day and which historical trades
    fill them, i.i.d. with replacement) is shared by every plan, so differences between plans
    are not Monte Carlo noise. For each plan the trades are scaled by qty, collapsed into days
    with the stop/cap logic (``apply_day_limits``) and run through the vectorised evaluation
    (firm DLL flattens at the limit unless ``options`` says otherwise). ``n_sims`` attempts of
    ``max_days`` calendar days each.

    Returns a DataFrame, one row per plan, sorted by ``sort_by`` (``pass_prob`` descending,
    any other column ascending), with columns: qty, mini_equivalent, daily_stop,
    daily_profit_cap, pass_prob, fail_prob, timeout_prob, pass_prob_se, mean_days_to_pass,
    median_days_to_pass, expected_attempts_per_pass, expected_cost_per_pass,
    expected_days_per_pass, consistency_extension_rate, fail_max_loss, fail_dll_hard,
    mean_day_pnl, std_day_pnl.
    """
    base = np.asarray(trade_pnls_per_contract, dtype=float).ravel()
    if base.size == 0:
        raise ValueError("trade_pnls_per_contract is empty")
    mae_base = None
    if trade_mae_per_contract is not None:
        mae_base = np.asarray(trade_mae_per_contract, dtype=float).ravel()
        if mae_base.shape != base.shape:
            raise ValueError("trade_mae_per_contract must align with trade_pnls_per_contract")

    qmax = max_qty(rules, contract)
    qtys = list(qty_list) if qty_list is not None else default_qty_list(rules, contract)
    bad = [q for q in qtys if q < 1 or q > qmax]
    if bad:
        raise ValueError(f"qty {bad} not allowed for {contract.symbol}: "
                         f"1 <= qty <= {qmax} (max_minis={rules.max_minis})")
    stops = list(daily_stops) if daily_stops is not None else default_daily_stops(rules)
    caps = list(daily_profit_caps) if daily_profit_caps is not None else default_profit_caps(rules)
    opts = options if options is not None else SYNTHETIC_DAY_OPTIONS

    rng = np.random.default_rng(seed)
    n_days = int(n_sims) * int(max_days)
    counts = sample_trade_counts(trades_per_day, n_days, rng)
    K = int(counts.max()) if counts.size else 0
    pick = rng.integers(0, base.size, size=(n_days, K))
    valid = np.arange(K)[None, :] < counts[:, None]
    unit = base[pick]
    unit_mae = mae_base[pick] if mae_base is not None else None
    traded = (counts > 0).reshape(n_sims, max_days)

    rows = []
    for q, stop, cap in itertools.product(qtys, stops, caps):
        mae = unit_mae * q if unit_mae is not None else None
        pnl, low, _ = apply_day_limits(unit * q, valid, stop, cap, mae)
        res = simulate_paths(pnl.reshape(n_sims, max_days), low.reshape(n_sims, max_days),
                             traded, rules, opts, **overrides)
        s = summarize_paths(res, rules)
        fr = s.pop("fail_reasons")
        s.pop("n_sims")
        rows.append(dict(
            qty=int(q), mini_equivalent=q * contract.mini_equivalent,
            daily_stop=stop, daily_profit_cap=cap, **s,
            fail_max_loss=fr.get("max_loss", 0.0), fail_dll_hard=fr.get("daily_loss_limit", 0.0),
            mean_day_pnl=float(pnl[counts > 0].mean()) if (counts > 0).any() else 0.0,
            std_day_pnl=float(pnl[counts > 0].std()) if (counts > 0).any() else 0.0,
        ))
    df = pd.DataFrame(rows)
    if sort_by == "pass_prob":
        df = df.sort_values(["pass_prob", "mean_days_to_pass"], ascending=[False, True],
                            kind="mergesort")
    else:
        df = df.sort_values(sort_by, ascending=True, kind="mergesort")
    return df.reset_index(drop=True)

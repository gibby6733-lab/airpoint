"""Strategy research pipeline: grid search in-sample, validate out-of-sample, rank by eval pass rate.

    python -m propbot.research --csv data/MNQ_1min.csv          # real data (recommended)
    python -m propbot.research --synthetic 750 --seed 1          # synthetic market with day regimes
    python -m propbot.research --synthetic 750 --null            # pure random walk (overfit check)

Steps
1. Split sessions chronologically: first ``--is-frac`` in-sample (IS), rest out-of-sample (OOS).
2. For every strategy x parameter combo, backtest IS at 1 contract with the firm's $600 DLL
   enforced intraday, then score the trades by the best eval pass probability over a small
   sizing grid (qty, daily stop, daily profit cap).
3. Keep the best IS combo per strategy, backtest it on OOS data it has never seen, and run the
   full sizing optimizer on the OOS trades. Only OOS numbers say anything about edge.
4. Compare with the zero-edge baseline (a coin-flip trader passes ~28% of the time).
"""
from __future__ import annotations

import argparse
import os
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd

from .backtest import run_backtest, summarize
from .data import load_csv, rth
from .interfaces import CONTRACTS, EvalRules
from .montecarlo import random_walk_baseline
from .sizing import optimize_day_plan
from .strategies import REGISTRY, iter_grid, make
from .synthetic import generate_mnq

MIN_TRADES = 30
FAST_PLAN = dict(qty_list=[1, 2, 4, 6, 10], daily_stops=[None, 300, 450],
                 daily_profit_caps=[None, 625])

_BARS: pd.DataFrame | None = None


def _init(bars: pd.DataFrame) -> None:
    global _BARS
    _BARS = bars


def _trades_and_counts(days):
    pnls = np.array([t.pnl / t.qty for d in days for t in d.trades], dtype=float)
    counts = np.array([len(d.trades) for d in days], dtype=int)
    return pnls, counts


def evaluate(name: str, params: dict, bars: pd.DataFrame, rules: EvalRules, contract,
             n_sims: int, plan: dict | None, seed: int = 0) -> dict:
    """Backtest one combo at 1 contract and score its trades by best eval pass probability."""
    days = run_backtest(bars, make(name, **params), contract, 1, rules,
                        daily_stop=rules.daily_loss_limit)
    stats = summarize(days)
    pnls, counts = _trades_and_counts(days)
    row = {"strategy": name, "params": params, "trades": len(pnls),
           "trades_per_day": stats["trades_per_day"], "total_pnl_1ct": stats["total_pnl"],
           "profit_factor": stats["profit_factor"], "trade_win_rate": stats["trade_win_rate"],
           "expectancy_1ct": stats["expectancy"], "pass_prob": np.nan, "plan": None}
    if len(pnls) < MIN_TRADES:
        return row
    table = optimize_day_plan(pnls, counts, rules, contract, n_sims=n_sims, seed=seed,
                              **(plan or {}))
    best = table.iloc[0]
    row.update(pass_prob=float(best["pass_prob"]),
               cost_per_pass=float(best["expected_cost_per_pass"]),
               days_to_pass=float(best["median_days_to_pass"]),
               plan={"qty": int(best["qty"]), "daily_stop": best["daily_stop"],
                     "daily_profit_cap": best["daily_profit_cap"]},
               _table=table)
    return row


def _job(args):
    name, params, rules, contract, n_sims = args
    row = evaluate(name, params, _BARS, rules, contract, n_sims, FAST_PLAN)
    row.pop("_table", None)
    return row


def run(bars: pd.DataFrame, rules: EvalRules, contract, is_frac: float, n_sims_is: int,
        n_sims_oos: int, workers: int, out_dir: Path, label: str) -> pd.DataFrame:
    dates = np.array(sorted(set(bars.index.date)))
    cut = dates[int(len(dates) * is_frac)]
    is_bars = bars[bars.index.date < cut]
    oos_bars = bars[bars.index.date >= cut]
    print(f"[{label}] {len(dates)} sessions: IS {dates[0]}..{cut} | OOS {cut}..{dates[-1]}")

    jobs = [(name, p, rules, contract, n_sims_is)
            for name, (_, grid) in REGISTRY.items() for p in iter_grid(grid)]
    print(f"[{label}] grid search: {len(jobs)} combos on {workers} workers ...")
    with ProcessPoolExecutor(workers, initializer=_init, initargs=(is_bars,)) as ex:
        is_rows = list(ex.map(_job, jobs, chunksize=2))
    is_df = pd.DataFrame(is_rows)
    out_dir.mkdir(parents=True, exist_ok=True)
    is_df.to_csv(out_dir / f"{label}_in_sample_grid.csv", index=False)

    results = []
    for name in REGISTRY:
        cand = is_df[(is_df.strategy == name) & is_df.pass_prob.notna()]
        if cand.empty:
            continue
        best = cand.sort_values("pass_prob", ascending=False).iloc[0]
        oos = evaluate(name, best.params, oos_bars, rules, contract, n_sims_oos, None, seed=1)
        table = oos.pop("_table", None)
        if table is not None:
            table.to_csv(out_dir / f"{label}_oos_sizing_{name}.csv", index=False)
        results.append({
            "strategy": name, "params": best.params,
            "is_pass_prob": best.pass_prob, "is_profit_factor": best.profit_factor,
            "oos_pass_prob": oos["pass_prob"], "oos_profit_factor": oos["profit_factor"],
            "oos_trades": oos["trades"], "oos_win_rate": oos["trade_win_rate"],
            "oos_expectancy_1ct": oos["expectancy_1ct"],
            "oos_cost_per_pass": oos.get("cost_per_pass", np.nan),
            "oos_days_to_pass": oos.get("days_to_pass", np.nan),
            "oos_best_plan": oos["plan"],
        })
    res = pd.DataFrame(results).sort_values("oos_pass_prob", ascending=False)
    res.to_csv(out_dir / f"{label}_summary.csv", index=False)
    return res


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--csv", help="1-minute bars exported from NinjaTrader/Tradovate/Databento")
    src.add_argument("--synthetic", type=int, metavar="DAYS", help="generate synthetic MNQ days")
    ap.add_argument("--null", action="store_true", help="synthetic pure random walk (no regimes)")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--symbol", default="MNQ", choices=sorted(CONTRACTS))
    ap.add_argument("--is-frac", type=float, default=0.6)
    ap.add_argument("--sims-is", type=int, default=1000)
    ap.add_argument("--sims-oos", type=int, default=5000)
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 1)
    ap.add_argument("--out", default="results")
    a = ap.parse_args(argv)

    if a.csv:
        bars, label = rth(load_csv(a.csv)), Path(a.csv).stem
    else:
        bars = generate_mnq(a.synthetic, seed=a.seed, regimes=not a.null)
        label = f"synthetic_{'null' if a.null else 'regimes'}_s{a.seed}"
    rules = EvalRules()
    base = random_walk_baseline(rules, n_sims=20000, max_days=60)
    res = run(bars, rules, CONTRACTS[a.symbol], a.is_frac, a.sims_is, a.sims_oos, a.workers,
              Path(a.out), label)
    pd.set_option("display.width", 200, "display.max_colwidth", 80)
    print(f"\nZero-edge baseline pass rate: {base['pass_prob']:.1%}")
    print(res.drop(columns=["params"]).to_string(index=False, float_format=lambda x: f"{x:.3f}"))
    for _, r in res.iterrows():
        print(f"  {r.strategy}: {r.params}")


if __name__ == "__main__":
    main()

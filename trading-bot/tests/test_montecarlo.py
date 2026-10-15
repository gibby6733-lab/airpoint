import math
import time

import numpy as np
import pandas as pd
import pytest

from propbot.interfaces import DayResult, EvalRules
from propbot.montecarlo import (apply_day_limits, bootstrap_indices, brownian_pass_probability,
                                pass_rate, pass_rate_from_trade_model, random_walk_baseline,
                                REASON_NAMES, simulate_paths)
from propbot.rules import simulate_eval


def D(pnl, low=None, trades=True):
    return DayResult(date=pd.Timestamp("2024-01-02"), pnl=float(pnl),
                     trades=["t"] if trades else [],
                     max_intraday_drawdown=float(min(pnl, 0) if low is None else low))


# ------------------------------------------------------------------ vectorised == scalar
@pytest.mark.parametrize("rules,opts", [
    (EvalRules(), {}),
    (EvalRules(), {"dll_flatten_at_limit": True}),
    (EvalRules(), {"dll_is_hard_breach": True}),
    (EvalRules(trailing_lock_at=25_100), {"consistency_mode": "fail"}),
    (EvalRules(daily_loss_limit=None, min_days=3), {"consistency_mode": "ignore"}),
])
def test_simulate_paths_matches_scalar(rules, opts):
    rng = np.random.default_rng(42)
    n, T = 300, 40
    pnl = np.round(rng.normal(40, 350, size=(n, T)), 2)
    low = np.minimum(pnl, 0) - np.round(np.abs(rng.normal(0, 200, size=(n, T))), 2)
    traded = rng.random((n, T)) > 0.1
    pnl[~traded] = 0.0
    low[~traded] = 0.0
    res = simulate_paths(pnl, low, traded, rules, **opts)
    for i in range(n):
        days = [DayResult(pd.Timestamp("2024-01-02"), pnl[i, t], ["x"] if traded[i, t] else [],
                          low[i, t]) for t in range(T)]
        out = simulate_eval(days, rules, **opts)
        assert out.passed == (res["status"][i] == 1)
        assert out.failed == (res["status"][i] == 2)
        assert out.days_used == res["days_used"][i]
        assert out.days_traded == res["days_traded"][i]
        assert out.final_balance == pytest.approx(res["final_balance"][i])
        assert out.reason == REASON_NAMES[int(res["reason"][i])]


# ------------------------------------------------------------------ deterministic cases
def test_all_winning_days_pass_in_two():
    out = pass_rate([D(700)] * 5, n_sims=200)
    assert out["pass_prob"] == 1.0 and out["median_days_to_pass"] == 2
    assert out["expected_attempts_per_pass"] == 1.0
    assert out["expected_cost_per_pass"] == pytest.approx(EvalRules().eval_fee)


def test_all_losing_days_fail():
    out = pass_rate([D(-300)] * 3, n_sims=200)
    assert out["fail_prob"] == 1.0 and out["fail_reasons"] == {"max_loss": 1.0}
    assert out["mean_days_per_attempt"] == 4
    assert math.isinf(out["expected_cost_per_pass"])


def test_cost_formula_and_mixed_outcomes():
    # day pool {+700, -1000}: a -1000 day before two +700 days fails; iid 50/50
    out = pass_rate([D(700), D(-1000)], n_sims=20_000, seed=1,
                    rules=EvalRules(daily_loss_limit=None))
    assert out["pass_prob"] == pytest.approx(0.25, abs=0.02)   # need +700,+700 first
    p = out["pass_prob"]
    r = EvalRules()
    assert out["expected_cost_per_pass"] == pytest.approx(r.eval_fee + r.reset_fee * (1 / p - 1))
    assert out["pass_prob"] + out["fail_prob"] + out["timeout_prob"] == pytest.approx(1.0)


def test_timeout():
    out = pass_rate([D(5)], n_sims=50, max_days=30)
    assert out["timeout_prob"] == 1.0 and out["fail_reasons"] == {"timeout": 1.0}
    assert math.isnan(out["median_days_to_pass"])


def test_plain_array_input():
    out = pass_rate(np.array([700.0, 700.0]), n_sims=10)
    assert out["pass_prob"] == 1.0


# ------------------------------------------------------------------ bootstrap
def test_block_bootstrap_indices_are_consecutive():
    rng = np.random.default_rng(0)
    idx = bootstrap_indices(10, n_sims=50, n_days=12, block=4, rng=rng)
    assert idx.shape == (50, 12)
    for b in range(3):
        blk = idx[:, 4 * b:4 * b + 4]
        assert np.all((np.diff(blk, axis=1) % 10) == 1)
    iid = bootstrap_indices(10, 50, 12, block=1, rng=rng)
    assert iid.min() >= 0 and iid.max() <= 9


def test_block_bootstrap_preserves_streaks():
    # alternating +700/-1000 history: with block=2 every pair contains one of each
    days = [D(700), D(-1000)] * 20
    iid = pass_rate(days, n_sims=4000, block=1, seed=3, rules=EvalRules(daily_loss_limit=None))
    blk = pass_rate(days, n_sims=4000, block=40, seed=3, rules=EvalRules(daily_loss_limit=None))
    assert iid["pass_prob"] > 0.15          # iid can draw +700,+700
    assert blk["pass_prob"] == 0.0          # in-order history never has two +700 in a row


def test_reproducible_with_seed():
    rng = np.random.default_rng(0)
    days = [D(x, low=min(x, 0) - 50) for x in rng.normal(30, 300, 120)]
    a = pass_rate(days, n_sims=2000, seed=7, block=3)
    b = pass_rate(days, n_sims=2000, seed=7, block=3)
    c = pass_rate(days, n_sims=2000, seed=8, block=3)
    assert a == b
    assert a["pass_prob"] != c["pass_prob"] or a["mean_days_to_pass"] != c["mean_days_to_pass"]
    assert random_walk_baseline(n_sims=500, seed=4) == random_walk_baseline(n_sims=500, seed=4)
    t1 = pass_rate_from_trade_model(0.5, 120, 100, 3, n_sims=500, seed=2)
    t2 = pass_rate_from_trade_model(0.5, 120, 100, 3, n_sims=500, seed=2)
    assert t1 == t2


def test_10k_sims_fast():
    rng = np.random.default_rng(0)
    days = [D(x, low=min(x, 0) - 80) for x in rng.normal(40, 300, 250)]
    t0 = time.perf_counter()
    out = pass_rate(days, n_sims=10_000, max_days=60, block=5)
    assert time.perf_counter() - t0 < 5.0
    assert 0 < out["pass_prob"] < 1


# ------------------------------------------------------------------ day limits
def test_apply_day_limits_stop_and_cap():
    trades = np.array([[-200, -200, -200, 500],
                       [200, 300, -100, 0],
                       [100, -50, 100, 0]], dtype=float)
    valid = np.array([[1, 1, 1, 1], [1, 1, 1, 0], [1, 1, 1, 0]], dtype=bool)
    pnl, low, n = apply_day_limits(trades, valid, daily_stop=300, daily_profit_cap=450)
    # row0 stops after -400 (overshoot), row1 caps after +500, row2 runs out of trades
    assert list(pnl) == [-400, 500, 150]
    assert list(low) == [-400, 0, 0]
    assert list(n) == [2, 2, 3]
    # low = min(cum_before + mae, cum_after): row0 -200-250, row1 0-250, row2 min(0-30, 100-120)
    mae = np.array([[-50, -250, 0, 0], [-250, 0, 0, 0], [-30, -120, 0, 0]], dtype=float)
    _, low2, _ = apply_day_limits(trades, valid, 300, 450, mae=mae)
    assert list(low2) == [-450, -250, -30]


def test_trade_model_deterministic():
    # always +400 once a day -> 400/800/1200/1600: passes on day 4 (best 400 <= 800)
    out = pass_rate_from_trade_model(1.0, 400, 300, 1, n_sims=100)
    assert out["pass_prob"] == 1 and out["mean_days_to_pass"] == 4
    # always -300 -> fails on day 4 (24,100 - 300 touches 24,000)
    out = pass_rate_from_trade_model(0.0, 400, 300, 1, n_sims=100)
    assert out["fail_prob"] == 1 and out["mean_days_per_attempt"] == 4
    # profit cap 300 with 2 x +400 trades: stops after the first trade -> still 400/day
    out = pass_rate_from_trade_model(1.0, 400, 300, 2, n_sims=100, daily_profit_cap=300)
    assert out["mean_day_pnl"] == 400 and out["mean_days_to_pass"] == 4


def test_trade_model_firm_dll_flattens():
    # 3 x -400 per day: closed-trade path -400, -800 -> firm flattens at -600 (soft DLL).
    out = pass_rate_from_trade_model(0.0, 100, 400, 3, n_sims=50)
    # 25,000 -> 24,400 -> room 400 < 600, next day touches floor on day 2
    assert out["fail_prob"] == 1 and out["mean_days_per_attempt"] == 2


# ------------------------------------------------------------------ baselines
def test_brownian_formula_limits():
    assert brownian_pass_probability(0, 300, 1250, 1000) == pytest.approx(1000 / 2250)
    assert brownian_pass_probability(0, 300, 1250, 1000, trailing=True) == \
        pytest.approx(math.exp(-1.25))
    assert brownian_pass_probability(1e-9, 300, 1250, 1000) == pytest.approx(1000 / 2250)
    assert brownian_pass_probability(50, 300, 1250, 1000) > 1000 / 2250
    assert brownian_pass_probability(-50, 300, 1250, 1000, trailing=True) < math.exp(-1.25)


def test_zero_edge_static_floor_matches_gamblers_ruin():
    # floor locked at 24,000 (static), no DLL / consistency / min days: P ~ 1000/2250
    static = EvalRules(trailing_lock_at=24_000, daily_loss_limit=None, consistency=1.0,
                       min_days=0)
    out = random_walk_baseline(static, daily_sigma=100, n_sims=4000, max_days=1000, seed=0)
    assert out["timeout_prob"] < 0.005
    # slightly below 0.444 because the target is only checked at EOD (no intraday pass)
    assert out["pass_prob"] == pytest.approx(1000 / 2250, abs=0.035)


def test_zero_edge_trailing_floor_between_bounds():
    trail = EvalRules(daily_loss_limit=None, consistency=1.0, min_days=0)
    out = random_walk_baseline(trail, daily_sigma=100, n_sims=4000, max_days=1000, seed=0)
    assert math.exp(-1.25) - 0.03 < out["pass_prob"] < 1000 / 2250
    # the full Lucid rules (DLL, consistency, 2 days) are no better than the plain trailing walk
    full = random_walk_baseline(EvalRules(), daily_sigma=100, n_sims=4000, max_days=1000, seed=0)
    assert full["pass_prob"] <= out["pass_prob"] + 0.02
    assert 0.2 < full["pass_prob"] < 0.35

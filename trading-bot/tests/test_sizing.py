import numpy as np
import pytest

from propbot.interfaces import CONTRACTS, EvalRules
from propbot.sizing import default_qty_list, max_qty, optimize_day_plan


def test_max_qty_respects_max_minis():
    r = EvalRules()
    assert max_qty(r, CONTRACTS["MNQ"]) == 20
    assert max_qty(r, CONTRACTS["NQ"]) == 2
    assert default_qty_list(r, CONTRACTS["NQ"]) == [1, 2]
    assert max(default_qty_list(r, CONTRACTS["MES"])) == 20


def test_invalid_qty_rejected():
    with pytest.raises(ValueError):
        optimize_day_plan([10.0], 1, contract=CONTRACTS["MNQ"], qty_list=[21])
    with pytest.raises(ValueError):
        optimize_day_plan([10.0], 1, contract=CONTRACTS["NQ"], qty_list=[3])


def test_deterministic_days_to_pass_by_qty():
    df = optimize_day_plan([100.0], 1, qty_list=[4, 7, 13], daily_stops=[None],
                           daily_profit_caps=[None], n_sims=50, max_days=20)
    assert (df["pass_prob"] == 1).all()
    days = dict(zip(df["qty"], df["mean_days_to_pass"]))
    assert days == {4: 4, 7: 2, 13: 2}     # 400x4=1600; 700x2=1400; 1300x2=2600 (best=50%)
    assert list(df["qty"])[0] in (7, 13)    # ties on pass_prob broken by fewer days
    assert df.loc[df.qty == 4, "mean_day_pnl"].item() == 400


def test_profit_cap_and_stop_shape_days():
    # two trades per day: +600 then -600. cap 500 stops after the winner -> +600/day.
    pnls = np.array([600.0, -600.0])
    df = optimize_day_plan(pnls, 2, qty_list=[1], daily_stops=[None],
                           daily_profit_caps=[None, 500], n_sims=500, max_days=30, seed=1)
    capped = df[df.daily_profit_cap == 500].iloc[0]
    uncapped = df[df.daily_profit_cap.isna()].iloc[0]
    assert capped["pass_prob"] > uncapped["pass_prob"]


def test_columns_sorting_and_combinations():
    rng = np.random.default_rng(0)
    pnls = rng.normal(8, 60, 500)
    df = optimize_day_plan(pnls, [2, 3, 4], qty_list=[1, 5, 10], n_sims=500, max_days=40)
    assert len(df) == 3 * 4 * 4
    for col in ("qty", "daily_stop", "daily_profit_cap", "pass_prob", "mean_days_to_pass",
                "expected_cost_per_pass", "expected_attempts_per_pass", "fail_prob",
                "timeout_prob"):
        assert col in df.columns
    assert df["pass_prob"].is_monotonic_decreasing
    by_cost = optimize_day_plan(pnls, [2, 3, 4], qty_list=[1, 5], n_sims=300, max_days=40,
                                sort_by="expected_cost_per_pass")
    assert by_cost["expected_cost_per_pass"].is_monotonic_increasing


def test_smaller_size_beats_max_size_with_positive_edge():
    # 55% win, +/-$5 per micro contract, 4 trades/day: small size lets the edge accumulate
    rng = np.random.default_rng(1)
    pnls = np.where(rng.random(5000) < 0.55, 25.0, -25.0)  # per contract
    df = optimize_day_plan(pnls, 4, qty_list=[2, 20], daily_stops=[None],
                           daily_profit_caps=[None], n_sims=3000, max_days=250, seed=0)
    p = dict(zip(df["qty"], df["pass_prob"]))
    assert p[2] > p[20] + 0.1


def test_mae_lowers_pass_rate():
    pnls = np.array([150.0, -100.0])
    mae = np.array([-400.0, -100.0])
    kw = dict(qty_list=[1], daily_stops=[None], daily_profit_caps=[None], n_sims=1000,
              max_days=60, seed=0)
    a = optimize_day_plan(pnls, 2, **kw)
    b = optimize_day_plan(pnls, 2, trade_mae_per_contract=mae, **kw)
    assert b["pass_prob"].item() <= a["pass_prob"].item()


def test_reproducible():
    rng = np.random.default_rng(5)
    pnls = rng.normal(5, 50, 300)
    a = optimize_day_plan(pnls, 3, qty_list=[2, 4], n_sims=300, seed=9)
    b = optimize_day_plan(pnls, 3, qty_list=[2, 4], n_sims=300, seed=9)
    assert a.equals(b)

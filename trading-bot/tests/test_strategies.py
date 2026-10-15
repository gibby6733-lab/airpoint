"""Tests for propbot.strategies: signal validity, time windows, and no-lookahead."""
from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest

from propbot.interfaces import Signal
from propbot.strategies import REGISTRY, iter_grid, make
from propbot.strategies.indicators import EMA, Resampler, SessionVWAP, WilderATR, hhmm

TZ = "America/New_York"


# --------------------------------------------------------------------------- synthetic data
def make_session(date: str, rng: np.random.Generator, start_price: float = 20000.0,
                 regime: str = "random", sigma: float = 6.0) -> pd.DataFrame:
    """One RTH session of 1-min bars 09:30-15:59 (390 bars) from a sub-sampled random walk."""
    n, sub = 390, 6
    idx = pd.date_range(f"{date} 09:30", periods=n, freq="1min", tz=TZ)
    steps = rng.normal(0.0, sigma / math.sqrt(sub), size=n * sub)
    if regime == "trend_up":
        steps += 2.0 * sigma / n * 10 / sub
    elif regime == "trend_down":
        steps -= 2.0 * sigma / n * 10 / sub
    path = np.empty(n * sub)
    x = start_price
    level = start_price
    for k in range(n * sub):
        if regime == "revert":
            x += steps[k] - 0.01 * (x - level)
        else:
            x += steps[k]
        path[k] = x
    path = path.reshape(n, sub)
    opens = np.r_[start_price, path[:-1, -1]]
    closes = path[:, -1]
    highs = np.maximum(path.max(axis=1), opens)
    lows = np.minimum(path.min(axis=1), opens)
    q = lambda a: np.round(a * 4) / 4  # tick-align
    t = np.linspace(-1, 1, n)
    vol = (800 + 1500 * t ** 2) * rng.uniform(0.5, 1.5, size=n)
    return pd.DataFrame({"open": q(opens), "high": q(highs), "low": q(lows), "close": q(closes),
                         "volume": np.round(vol)}, index=idx)


def make_sessions(seed: int = 7, n_days: int = 12):
    rng = np.random.default_rng(seed)
    regimes = ["trend_up", "revert", "random", "trend_down", "revert", "random"]
    dates = pd.bdate_range("2025-03-03", periods=n_days)
    out, price = [], 20000.0
    for d_i, d in enumerate(dates):
        df = make_session(d.strftime("%Y-%m-%d"), rng, price, regimes[d_i % len(regimes)])
        out.append(df)
        price = float(df["close"].iloc[-1]) + float(rng.normal(0, 15))
    return out


SESSIONS = make_sessions()


# --------------------------------------------------------------------------- tiny simulator
def run(strategy, sessions, full_frame: bool = False):
    """Minimal fill model (next-bar-open fills, intrabar stop/target), enough to drive `position`.
    Returns a list of (session_idx, i, position_passed, close_i, signal)."""
    recs = []
    for s_idx, df in enumerate(sessions):
        strategy.reset()
        o, h, l = df["open"].to_numpy(), df["high"].to_numpy(), df["low"].to_numpy()
        c = df["close"].to_numpy()
        pos, stop, target, pending = 0, None, None, None
        for i in range(len(df)):
            if pending is not None:
                if pending.side == 0:
                    pos = 0
                elif pos == 0:
                    pos, stop, target = pending.side, pending.stop, pending.target
                pending = None
            if pos > 0:
                if l[i] <= stop or (target is not None and h[i] >= target):
                    pos = 0
            elif pos < 0:
                if h[i] >= stop or (target is not None and l[i] <= target):
                    pos = 0
            bars = df if full_frame else df.iloc[: i + 1]
            sig = strategy.on_bar(i, bars, pos)
            recs.append((s_idx, i, pos, float(c[i]), sig))
            if sig is not None:
                pending = sig
    return recs


def sample_combos(grid: dict, k: int = 4):
    combos = list(iter_grid(grid))
    if len(combos) <= k:
        return combos
    pick = np.linspace(0, len(combos) - 1, k).round().astype(int)
    return [combos[j] for j in sorted(set(pick))]


CASES = [(name, combo) for name, (_, grid) in REGISTRY.items() for combo in sample_combos(grid)]
CASE_IDS = [f"{n}-{j}" for j, (n, _) in enumerate(CASES)]


# --------------------------------------------------------------------------- registry
def test_registry_shape():
    expected = {"orb", "vwap_pullback", "vwap_reversion", "opening_drive", "prior_day_levels", "ema_trend"}
    assert set(REGISTRY) == expected
    for name, (cls, grid) in REGISTRY.items():
        assert cls.name == name
        assert isinstance(grid, dict) and all(isinstance(v, list) and v for v in grid.values())
        combos = list(iter_grid(grid))
        assert 1 <= len(combos) <= 48, (name, len(combos))
        for combo in combos:
            assert set(combo) <= set(cls.default_params), name
            s = cls(**combo)
            assert s.name == name and isinstance(s.params, dict)
            for k, v in combo.items():
                assert s.params[k] == v


def test_unknown_param_rejected():
    with pytest.raises(TypeError):
        make("orb", not_a_param=1)


# --------------------------------------------------------------------------- signal validity
@pytest.mark.parametrize("name,combo", CASES, ids=CASE_IDS)
def test_signals_valid(name, combo):
    strat = make(name, **combo)
    recs = run(strat, SESSIONS)
    start, cutoff = hhmm(strat.params["start"]), hhmm(strat.params["cutoff"])
    exit_min = hhmm(strat.params["exit_time"])
    per_day = {}
    for s_idx, i, pos, close, sig in recs:
        if sig is None:
            continue
        assert isinstance(sig, Signal)
        assert sig.side in (-1, 0, 1)
        assert isinstance(sig.tag, str) and sig.tag
        ts = SESSIONS[s_idx].index[i]
        minute = ts.hour * 60 + ts.minute
        if sig.side == 0:
            assert pos != 0, "flatten signal while flat"
            assert minute >= exit_min
            continue
        # entries
        assert pos == 0, "entry while already in a position (no pyramiding/averaging)"
        assert start <= minute < cutoff, f"entry at {ts} outside [{start}, {cutoff})"
        assert minute < hhmm("15:55")
        assert sig.stop is not None and math.isfinite(sig.stop)
        if sig.side > 0:
            assert sig.stop < close
            assert sig.target is None or sig.target > close
        else:
            assert sig.stop > close
            assert sig.target is None or sig.target < close
        assert abs(sig.stop / 0.25 - round(sig.stop / 0.25)) < 1e-6
        per_day[s_idx] = per_day.get(s_idx, 0) + 1
    for n in per_day.values():
        assert n <= strat.params["max_trades"]


def test_every_strategy_trades_somewhere():
    """Guard against dead code: across a few grid points every strategy fires at least once."""
    for name, (cls, grid) in REGISTRY.items():
        total = 0
        for combo in sample_combos(grid, 6):
            recs = run(cls(**combo), SESSIONS)
            total += sum(1 for r in recs if r[4] is not None and r[4].side != 0)
        assert total > 0, f"{name} produced no entries on synthetic data"


# --------------------------------------------------------------------------- no lookahead
def _perturb_after(df: pd.DataFrame, cut: int, seed: int) -> pd.DataFrame:
    """Same rows 0..cut, a different random continuation afterwards."""
    rng = np.random.default_rng(seed)
    alt = make_session(df.index[0].strftime("%Y-%m-%d"), rng, float(df["close"].iloc[cut]),
                       regime=["trend_up", "trend_down", "revert"][seed % 3], sigma=9.0)
    out = df.copy()
    tail = alt.iloc[: len(df) - cut - 1]
    out.iloc[cut + 1:, :] = tail.to_numpy()
    return out


@pytest.mark.parametrize("name,combo", CASES, ids=CASE_IDS)
def test_no_lookahead(name, combo):
    sessions = SESSIONS[:8]
    base = run(make(name, **combo), sessions)
    # 1) handing the strategy the WHOLE session frame (rows beyond i present) changes nothing
    full = run(make(name, **combo), sessions, full_frame=True)
    assert base == full
    # 2) changing the future of a session never changes output up to the cut
    k = 6
    offset = sum(len(s) for s in sessions[:k])
    for cut in (20, 45, 95, 200, 330):
        alt_sessions = list(sessions)
        alt_sessions[k] = _perturb_after(sessions[k], cut, seed=cut)
        assert alt_sessions[k].iloc[: cut + 1].equals(sessions[k].iloc[: cut + 1])
        alt = run(make(name, **combo), alt_sessions)
        n = offset + cut + 1
        assert base[:n] == alt[:n], f"{name}: output up to bar {cut} depends on future rows"


def test_skipped_bars_and_auto_rollover():
    """Jumping i forward and omitting reset() must not crash or emit invalid signals."""
    for name, (cls, _) in REGISTRY.items():
        s = cls()
        for df in SESSIONS[:4]:
            for i in range(0, len(df), 7):   # no reset() between sessions on purpose
                sig = s.on_bar(i, df.iloc[: i + 1], 0)
                if sig is not None and sig.side != 0:
                    close = df["close"].iloc[i]
                    assert (sig.stop - close) * sig.side < 0


# --------------------------------------------------------------------------- indicators
def test_vwap_matches_pandas():
    df = SESSIONS[0]
    tp = (df.high + df.low + df.close) / 3
    exp_vwap = (tp * df.volume).cumsum() / df.volume.cumsum()
    exp_var = (tp ** 2 * df.volume).cumsum() / df.volume.cumsum() - exp_vwap ** 2
    v = SessionVWAP()
    got, got_sd = [], []
    for row in df.itertuples():
        got.append(v.update(row.high, row.low, row.close, row.volume))
        got_sd.append(v.std)
    np.testing.assert_allclose(got, exp_vwap.to_numpy(), rtol=0, atol=1e-6)
    np.testing.assert_allclose(got_sd, np.sqrt(np.maximum(exp_var.to_numpy(), 0)), atol=1e-3)


def test_ema_matches_pandas():
    x = SESSIONS[1]["close"]
    e = EMA(9)
    got = [e.update(v) for v in x]
    np.testing.assert_allclose(got, x.ewm(span=9, adjust=False).mean().to_numpy(), atol=1e-8)


def test_atr_positive():
    a = WilderATR(14)
    for row in SESSIONS[2].itertuples():
        a.update(row.high, row.low, row.close)
    assert a.ready and a.value > 0


def test_resampler_matches_pandas_and_only_completed():
    df = SESSIONS[3]
    rs = Resampler(5, 570)
    got, emitted_at = [], []
    for i, row in enumerate(df.itertuples()):
        m = row.Index.hour * 60 + row.Index.minute
        for b in rs.update(m, 1, row.open, row.high, row.low, row.close, row.volume):
            got.append((b.open, b.high, b.low, b.close, b.volume))
            emitted_at.append((i, b.start))
    exp = df.resample("5min").agg({"open": "first", "high": "max", "low": "min",
                                   "close": "last", "volume": "sum"})
    np.testing.assert_allclose(np.array(got), exp.to_numpy())
    for i, start in emitted_at:  # emitted on the last 1-min bar of the bucket, never earlier
        ts = df.index[i]
        assert ts.hour * 60 + ts.minute == start + 4

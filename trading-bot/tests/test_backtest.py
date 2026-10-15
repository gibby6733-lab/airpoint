import math

import numpy as np
import pandas as pd
import pytest

from propbot.backtest import run_backtest, summarize, trades_frame
from propbot.interfaces import CONTRACTS, ContractSpec, EvalRules, Signal

MNQ = CONTRACTS["MNQ"]
RULES = EvalRules()


def make_bars(rows, start="2024-01-02 09:30"):
    """rows: list of (open, high, low, close); 1-minute bars from ``start`` (ET)."""
    idx = pd.date_range(start, periods=len(rows), freq="1min", tz="America/New_York")
    df = pd.DataFrame(rows, columns=["open", "high", "low", "close"], index=idx, dtype=float)
    df["volume"] = 100.0
    return df


FLAT_ROWS = [(100.0, 101.0, 99.0, 100.0)] * 8


class Scripted:
    """Emits pre-scripted signals keyed by bar index; records what it was shown."""

    name = "scripted"
    params: dict = {}

    def __init__(self, script):
        self.script = script
        self.seen = []  # (i, len(bars), last index timestamp, position)

    def reset(self):
        self.seen_session = []

    def on_bar(self, i, bars, position):
        self.seen.append((i, len(bars), bars.index[-1], position))
        return self.script.get(i)


def run(bars, script, qty=1, contract=MNQ, rules=RULES, **kw):
    strat = Scripted(script)
    days = run_backtest(bars, strat, contract, qty, rules, **kw)
    return days, strat


def test_fill_at_next_bar_open_with_slippage():
    rows = [
        (100, 101, 99, 100),
        (102, 103, 101, 102),   # entry bar: open 102
        (104, 105, 103, 104),
        (106, 107, 105, 106),   # exit bar: open 106
        (108, 109, 107, 108),
    ]
    days, _ = run(make_bars(rows), {0: Signal(1), 2: Signal(0)}, slippage_ticks=1)
    (t,) = days[0].trades
    assert t.entry == 102 + 0.25
    assert t.exit == 106 - 0.25
    assert t.entry_time == make_bars(rows).index[1]
    assert t.exit_time == make_bars(rows).index[3]
    assert t.pnl == pytest.approx((105.75 - 102.25) * 2.0 - 1.04)
    assert days[0].pnl == pytest.approx(t.pnl)


def test_slippage_ticks_scale_and_short_side():
    rows = [(100, 101, 99, 100), (102, 103, 101, 102), (98, 99, 97, 98), (98, 99, 97, 98)]
    d0, _ = run(make_bars(rows), {0: Signal(-1), 1: Signal(0)}, slippage_ticks=0)
    d2, _ = run(make_bars(rows), {0: Signal(-1), 1: Signal(0)}, slippage_ticks=2)
    t0, t2 = d0[0].trades[0], d2[0].trades[0]
    assert (t0.entry, t0.exit) == (102, 98)
    assert (t2.entry, t2.exit) == (101.5, 98.5)       # short: sell lower, buy higher
    assert t0.pnl - t2.pnl == pytest.approx(4 * 0.25 * 2.0)


def test_commission_math_and_qty():
    rows = [(100, 101, 99, 100), (100, 101, 99, 100), (110, 111, 109, 110), (110, 111, 109, 110)]
    days, _ = run(make_bars(rows), {0: Signal(1), 1: Signal(0)}, qty=3, slippage_ticks=0)
    t = days[0].trades[0]
    assert t.qty == 3
    assert t.pnl == pytest.approx(10 * 2.0 * 3 - 1.04 * 3)
    nq = CONTRACTS["NQ"]
    days, _ = run(make_bars(rows), {0: Signal(1), 1: Signal(0)}, qty=2, contract=nq, slippage_ticks=0)
    assert days[0].trades[0].pnl == pytest.approx(10 * 20.0 * 2 - 4.0 * 2)


def test_max_minis_enforced():
    with pytest.raises(AssertionError):
        run(make_bars(FLAT_ROWS), {}, qty=3, contract=CONTRACTS["NQ"])
    with pytest.raises(AssertionError):
        run(make_bars(FLAT_ROWS), {}, qty=21, contract=MNQ)
    run(make_bars(FLAT_ROWS), {}, qty=20, contract=MNQ)  # exactly 2 minis is fine


def test_stop_wins_when_stop_and_target_in_same_bar():
    rows = [
        (100, 100.5, 99.5, 100),
        (100, 100.5, 99.5, 100),   # entry at 100 + slip; stop 97, target 103 not touched
        (100, 104, 96, 100),       # both inside -> stop first
        (100, 101, 99, 100),
    ]
    days, _ = run(make_bars(rows), {0: Signal(1, stop=97, target=103)}, slippage_ticks=1)
    (t,) = days[0].trades
    assert t.reason == "stop"
    assert t.exit == 97 - 0.25
    assert t.exit_time == make_bars(rows).index[2]


def test_target_fills_exactly_without_slippage():
    rows = [(100, 100.5, 99.5, 100), (100, 100.5, 99.5, 100), (100, 104, 99, 103), (100, 101, 99, 100)]
    days, _ = run(make_bars(rows), {0: Signal(1, stop=97, target=103)}, slippage_ticks=2)
    (t,) = days[0].trades
    assert t.reason == "target" and t.exit == 103


def test_stop_gap_through_fills_at_open():
    rows = [(100, 100.5, 99.5, 100), (100, 100.5, 99.5, 100), (95, 96, 94, 95), (95, 96, 94, 95)]
    days, _ = run(make_bars(rows), {0: Signal(1, stop=97)}, slippage_ticks=1)
    (t,) = days[0].trades
    assert t.reason == "stop" and t.exit == 95 - 0.25


def test_stop_live_on_fill_bar():
    # the whole fill bar trades after its open, so its range can hit the stop
    rows = [(100, 100.5, 99.5, 100), (100, 100.5, 96, 97), (97, 98, 96, 97)]
    days, _ = run(make_bars(rows), {0: Signal(1, stop=98)}, slippage_ticks=0)
    (t,) = days[0].trades
    assert t.reason == "stop" and t.exit_time == make_bars(rows).index[1] and t.exit == 98


def test_short_stop_and_target():
    rows = [(100, 100.5, 99.5, 100), (100, 100.5, 99.5, 100), (100, 100.5, 96.5, 97), (97, 98, 96, 97)]
    days, _ = run(make_bars(rows), {0: Signal(-1, stop=102, target=97)}, slippage_ticks=1)
    (t,) = days[0].trades
    assert t.side == -1 and t.reason == "target" and t.exit == 97
    assert t.pnl == pytest.approx((99.75 - 97) * 2.0 - 1.04)


def test_no_lookahead_strategy_sees_only_past_bars():
    bars = make_bars(FLAT_ROWS)
    days, strat = run(bars, {})
    assert [s[0] for s in strat.seen] == list(range(len(bars)))
    for i, n, last, pos in strat.seen:
        assert n == i + 1
        assert last == bars.index[i]


def test_strategy_receives_signed_position():
    days, strat = run(make_bars(FLAT_ROWS), {0: Signal(-1)}, qty=4)
    positions = {i: p for i, _, _, p in strat.seen}
    assert positions[0] == 0 and positions[1] == -4 and positions[5] == -4


def test_same_direction_ignored_and_reversal():
    rows = [(100 + k, 101 + k, 99 + k, 100 + k) for k in range(8)]
    script = {0: Signal(1), 1: Signal(1, stop=50), 3: Signal(-1), 5: Signal(0)}
    days, _ = run(make_bars(rows), script, slippage_ticks=0)
    t1, t2 = days[0].trades
    assert t1.side == 1 and t1.entry == 101 and t1.exit == 104 and t1.reason == "reverse"
    assert t2.side == -1 and t2.entry == 104 and t2.exit == 106 and t2.reason == "exit"


def test_flatten_time_forces_exit_and_blocks_later_signals():
    rows = [(100 + k, 101 + k, 99 + k, 100 + k) for k in range(8)]
    bars = make_bars(rows, start="2024-01-02 15:51")   # 15:51 .. 15:58; flatten at 15:55 (row 4)
    days, strat = run(bars, {0: Signal(1), 5: Signal(-1)}, slippage_ticks=1)
    (t,) = days[0].trades
    assert t.reason == "flatten_time"
    assert t.exit_time == bars.index[4] and t.exit == 104 - 0.25
    assert max(s[0] for s in strat.seen) == 3  # strategy not consulted after flatten


def test_signal_before_flatten_bar_not_filled():
    bars = make_bars(FLAT_ROWS, start="2024-01-02 15:51")
    days, _ = run(bars, {3: Signal(1)})
    assert days[0].trades == []


def test_end_of_session_exit_at_last_close():
    rows = [(100, 101, 99, 100), (100, 101, 99, 100), (100, 103, 99, 102.5)]
    days, _ = run(make_bars(rows), {0: Signal(1)}, slippage_ticks=1)
    (t,) = days[0].trades
    assert t.reason == "eod" and t.exit == 102.25


def test_daily_stop_exits_at_threshold_and_halts_day():
    # qty 10 MNQ -> $20/pt. daily_stop $200 => 10 pts adverse incl. commission.
    rows = [
        (100, 100.5, 99.5, 100),
        (100, 100.5, 99.5, 100),   # entry 100 (no slippage)
        (99, 99.5, 80, 85),        # crash through the daily stop
        (85, 86, 84, 85),
        (85, 86, 84, 85),
        (85, 86, 84, 85),
    ]
    days, strat = run(make_bars(rows), {0: Signal(1), 3: Signal(1)}, qty=10, slippage_ticks=0, daily_stop=200)
    (t,) = days[0].trades
    assert t.reason == "daily_stop"
    comm = 1.04 * 10
    expected_px = math.ceil((100 - (200 - comm) / 20.0) / 0.25) * 0.25
    assert t.exit == expected_px
    assert -200 - 1e-9 <= days[0].pnl <= -200 + 0.25 * 20
    assert days[0].max_intraday_drawdown == pytest.approx(days[0].pnl)
    assert max(s[0] for s in strat.seen) == 1  # trading halted after the stop


def test_daily_profit_cap_and_max_trades():
    rows = [(100 + 5 * k, 101 + 5 * k, 99 + 5 * k, 100 + 5 * k) for k in range(10)]
    script = {0: Signal(1), 1: Signal(0), 2: Signal(1), 3: Signal(0), 4: Signal(1), 5: Signal(0)}
    days, _ = run(make_bars(rows), script, slippage_ticks=0)
    assert len(days[0].trades) == 3
    days, _ = run(make_bars(rows), script, slippage_ticks=0, max_trades_per_day=2)
    assert len(days[0].trades) == 2
    days, _ = run(make_bars(rows), script, slippage_ticks=0, daily_profit_cap=5)
    assert len(days[0].trades) == 1


def test_max_intraday_drawdown_uses_adverse_extremes():
    rows = [(100, 100.5, 99.5, 100), (100, 100.5, 99.5, 100), (100, 100.5, 90, 99), (99, 120, 98, 119), (119, 120, 118, 119)]
    days, _ = run(make_bars(rows), {0: Signal(1), 3: Signal(0)}, slippage_ticks=0)
    assert days[0].max_intraday_drawdown == pytest.approx((90 - 100) * 2.0 - 1.04)
    assert days[0].pnl == pytest.approx((119 - 100) * 2.0 - 1.04)


def test_one_result_per_session_including_flat_days():
    a = make_bars(FLAT_ROWS, start="2024-01-02 09:30")
    b = make_bars(FLAT_ROWS, start="2024-01-03 09:30")
    c = make_bars(FLAT_ROWS, start="2024-01-04 09:30")
    bars = pd.concat([a, b, c])

    class FirstDayOnly(Scripted):
        def reset(self):
            self.day = getattr(self, "day", -1) + 1

        def on_bar(self, i, bars, position):
            return Signal(1) if (self.day == 1 and i == 0) else None

    days = run_backtest(bars, FirstDayOnly({}), MNQ, 1, RULES)
    assert [d.date for d in days] == list(pd.to_datetime(["2024-01-02", "2024-01-03", "2024-01-04"]))
    assert days[0].pnl == 0 and days[0].trades == []
    assert len(days[1].trades) == 1 and days[1].trades[0].reason == "eod"
    assert days[2].trades == []
    s = summarize(days)
    assert s["n_days"] == 3 and s["n_trades"] == 1 and s["n_trading_days"] == 1
    assert len(trades_frame(days)) == 1


def test_summarize_stats():
    from propbot.interfaces import DayResult, Trade

    ts = pd.Timestamp("2024-01-02 10:00", tz="America/New_York")

    def tr(p):
        return Trade(ts, ts, 1, 1, 0.0, 0.0, p)

    days = [
        DayResult(pd.Timestamp("2024-01-02"), 100.0, [tr(150.0), tr(-50.0)], -60.0),
        DayResult(pd.Timestamp("2024-01-03"), -200.0, [tr(-200.0)], -250.0),
        DayResult(pd.Timestamp("2024-01-04"), 0.0, [], 0.0),
        DayResult(pd.Timestamp("2024-01-05"), 300.0, [tr(300.0)], 0.0),
    ]
    s = summarize(days)
    assert s["total_pnl"] == 200.0
    assert s["n_trades"] == 4 and s["trade_win_rate"] == 0.5
    assert s["day_win_rate"] == pytest.approx(2 / 3)
    assert s["avg_win"] == 225.0 and s["avg_loss"] == -125.0
    assert s["profit_factor"] == pytest.approx(450 / 250)
    assert s["max_drawdown"] == -200.0
    assert s["worst_intraday_drawdown"] == -250.0
    pnl = np.array([100, -200, 0, 300.0])
    assert s["sharpe"] == pytest.approx(pnl.mean() / pnl.std(ddof=1) * np.sqrt(252))


def test_runs_on_synthetic_data_quickly():
    from propbot.synthetic import generate_mnq

    class EveryHour:
        name = "hourly"
        params: dict = {}

        def reset(self):
            pass

        def on_bar(self, i, bars, position):
            if i % 60 == 0:
                c = bars["close"].iloc[-1]
                return Signal(1 if (i // 60) % 2 == 0 else -1, stop=c - 20 if (i // 60) % 2 == 0 else c + 20)
            return None

    bars = generate_mnq(20, seed=1)
    days = run_backtest(bars, EveryHour(), MNQ, 2, RULES, daily_stop=600)
    assert len(days) == 20
    for d in days:
        assert d.max_intraday_drawdown <= 0
        assert d.max_intraday_drawdown <= min(0.0, d.pnl) + 1e-9
        for t in d.trades:
            assert t.exit_time.strftime("%H:%M") <= "15:55"

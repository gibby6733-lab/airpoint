import json
import math

import pandas as pd
import pytest

from propbot.backtest import run_backtest
from propbot.interfaces import CONTRACTS, EvalRules, Signal
from propbot.live import (PASSED_MSG, AccountState, Bar, EventLog, Fill, GuardianConfig,
                          LiveEngine, PaperBroker, Position, RiskGuardian)
from propbot.live.__main__ import main as cli_main
from propbot.rules import PASSED
from propbot.strategies import make
from propbot.synthetic import generate_mnq

MNQ = CONTRACTS["MNQ"]
NQ = CONTRACTS["NQ"]
ET = "America/New_York"
DAY = pd.Timestamp("2024-01-02")


# =========================================================================== helpers
class FakeBroker:
    """Records every call; the test sets ``pos`` by hand."""

    def __init__(self, symbol="MNQ"):
        self.symbol = symbol
        self.calls = []
        self.pos = Position(symbol)
        self.n = 0

    def connect(self):
        self.calls.append(("connect",))

    def subscribe_bars(self, symbol, cb):
        self.calls.append(("subscribe_bars", symbol))

    def subscribe_fills(self, cb):
        self.calls.append(("subscribe_fills",))

    def get_position(self, symbol):
        return self.pos

    def get_account_balance(self):
        return 25_000.0

    def place_bracket(self, symbol, side, qty, stop, target):
        self.n += 1
        oid = f"F{self.n}"
        self.calls.append(("bracket", oid, side, qty, stop, target))
        return oid

    def modify_stop(self, order_id, price):
        self.calls.append(("modify_stop", order_id, price))

    def flatten(self, symbol):
        self.calls.append(("flatten",))

    def cancel_all(self, symbol):
        self.calls.append(("cancel_all",))

    def kinds(self):
        return [c[0] for c in self.calls]


def bar(hhmm, o, h=None, lo=None, c=None, date="2024-01-02"):
    h = o if h is None else h
    lo = o if lo is None else lo
    c = o if c is None else c
    return Bar(pd.Timestamp(f"{date} {hhmm}", tz=ET), float(o), float(h), float(lo), float(c),
               100.0, "MNQ")


def at(hhmm, date="2024-01-02"):
    return pd.Timestamp(f"{date} {hhmm}", tz=ET)


def make_guardian(tmp_path, contract=MNQ, broker=None, state=None, **cfg):
    cfg.setdefault("kill_switch_path", str(tmp_path / "STOP"))
    g = RiskGuardian(contract, GuardianConfig(**cfg), state=state, log=EventLog())
    g.attach(broker if broker is not None else FakeBroker(contract.symbol), contract.symbol)
    return g


def fill(oid, side, qty, px, reason, hhmm="10:01"):
    return Fill(oid, "MNQ", at(hhmm), side, qty, float(px), reason)


def open_long(g, qty=2, px=100.0, stop=90.0, target=None, hhmm="10:00"):
    """Approve + fill a long entry; the fake broker position is updated."""
    d = g.submit_entry(at(hhmm), +1, qty, stop, target, ref_price=px, tag="t")
    assert d.allowed, d.reason
    g.on_fill(fill(d.order_id, +1, d.qty, px, "entry", hhmm))
    g.broker.pos = Position("MNQ", d.qty, px)
    return d


# =========================================================================== entry vetoes
def test_rejects_oversize(tmp_path):
    g = make_guardian(tmp_path)
    g.begin_session(DAY)
    d = g.submit_entry(at("10:00"), +1, 21, 99.0, 102.0, ref_price=100.0)
    assert d.action == "reject" and "minis" in d.reason
    assert "bracket" not in g.broker.kinds()
    ok = g.submit_entry(at("10:00"), +1, 20, 99.0, 102.0, ref_price=100.0)
    assert ok.action == "allow" and ok.qty == 20

    gn = make_guardian(tmp_path, contract=NQ, bot_daily_stop=None)
    gn.begin_session(DAY)
    assert gn.submit_entry(at("10:00"), -1, 3, 101.0, 98.0, ref_price=100.0).action == "reject"
    assert gn.submit_entry(at("10:00"), -1, 2, 100.25, 98.0, ref_price=100.0).allowed
    assert gn.log.find("entry_rejected")[0]["reason"].startswith("size 3 x NQ")


def test_rejects_entry_whose_stop_risk_breaches_remaining_room(tmp_path):
    st = AccountState(MNQ)
    st.account.balance = 24_300.0          # room to floor 300 -> budget min(300-50, 600-50, 300)
    g = make_guardian(tmp_path, state=st)
    g.begin_session(DAY)
    assert g.budget == pytest.approx(250.0)
    # 2 MNQ x (60 + 0.5 slip) pts x $2 + 2.08 commission = 244.08 fits ...
    assert g.submit_entry(at("10:00"), +1, 2, 40.0, None, ref_price=100.0).allowed
    # ... 2 x (65.5 * 2 + 1.04) = 264.08 does not
    g2 = make_guardian(tmp_path, state=st)
    g2.begin_session(DAY)
    d = g2.submit_entry(at("10:00"), +1, 2, 35.0, None, ref_price=100.0)
    assert d.action == "reject" and "stop risk" in d.reason
    assert "bracket" not in g2.broker.kinds()

    # realised losses shrink the room for later entries the same way
    g3 = make_guardian(tmp_path, bot_daily_stop=200.0)
    g3.begin_session(DAY)
    g3.day.realized = -150.0
    d = g3.submit_entry(at("11:00"), -1, 1, 125.0, None, ref_price=100.0)  # 52.04 risk > 50 left
    assert d.action == "reject"
    assert g3.submit_entry(at("11:00"), -1, 1, 120.0, None, ref_price=100.0).allowed


def test_reduces_qty_to_fit_when_configured(tmp_path):
    g = make_guardian(tmp_path, size_policy="reduce", bot_daily_stop=250.0)
    g.begin_session(DAY)
    # 25 MNQ: first cut to the 20-micro limit, then to the stop risk: per contract
    # (10 + 0.5) * 2 + 1.04 = 22.04 -> floor(250 / 22.04) = 11 contracts
    d = g.submit_entry(at("10:00"), +1, 25, 90.0, 120.0, ref_price=100.0)
    assert d.action == "reduce" and d.qty == 11
    assert ("bracket", d.order_id, 1, 11, 90.0, 120.0) in g.broker.calls
    assert g.log.find("entry_reduced")[0]["qty"] == 11
    # nothing fits at all -> still a reject
    g.day.realized = -240.0
    assert g.submit_entry(at("10:05"), +1, 5, 90.0, None, ref_price=100.0).action == "reject"


def test_rejects_outside_hours_and_after_profit_cap(tmp_path):
    g = make_guardian(tmp_path)
    g.begin_session(DAY)
    assert g.profit_cap == pytest.approx(625.0)   # consistency-safe cap on a fresh account
    assert g.submit_entry(at("09:25"), +1, 1, 99.0, None, 100.0).action == "reject"
    assert g.submit_entry(at("15:55"), +1, 1, 99.0, None, 100.0).action == "reject"
    assert "outside allowed hours" in g.log.find("entry_rejected")[-1]["reason"]
    assert g.submit_entry(at("15:54"), +1, 1, 99.0, None, 100.0).allowed
    g2 = make_guardian(tmp_path)
    g2.begin_session(DAY)
    g2.day.realized = 630.0
    d = g2.submit_entry(at("11:00"), +1, 1, 99.0, None, 100.0)
    assert d.action == "reject" and "profit cap" in d.reason


# =========================================================================== intraday overrides
def test_arms_stop_and_flattens_at_daily_stop(tmp_path):
    # stop-risk check off so the strategy stop can be wider than the budget: the guardian's
    # resting budget stop and its bar-close check are the backstops
    g = make_guardian(tmp_path, bot_daily_stop=200.0, safety_buffer=0.0, check_stop_risk=False)
    g.begin_session(DAY)
    open_long(g, qty=2, px=100.0, stop=10.0)   # strategy stop far away
    # resting stop tightened to the budget level: 100 - (200 - 2.08) / 4 = 50.52 -> 50.75
    assert ("modify_stop", "F1", 50.75) in g.broker.calls
    # bar-close safety net: open P&L (55 - 100) * 4 - 2.08 = -182 > -200 -> nothing
    g.on_bar(bar("10:01", 60, 61, 55, 55), g.broker.pos)
    assert not g.day.locked
    # close at 50.25: -201.08 <= -200 -> flatten + lock (stop did not fill, e.g. broker issue)
    g.on_bar(bar("10:02", 55, 55, 50.25, 50.25), g.broker.pos)
    assert g.day.locked and g.day.lock_reason == "daily_stop"
    assert g.broker.kinds()[-1] == "flatten"
    assert g.submit_entry(at("10:05"), -1, 1, 60.0, None, 50.0).action == "reject"
    assert not g.strategy_enabled(bar("10:03", 50))


def test_daily_stop_fill_locks_day(tmp_path):
    g = make_guardian(tmp_path, bot_daily_stop=200.0, safety_buffer=0.0, check_stop_risk=False)
    g.begin_session(DAY)
    d = open_long(g, qty=2, px=100.0, stop=10.0)
    g.on_fill(fill(d.order_id, -1, 2, 50.5, "stop", "10:03"))
    g.broker.pos = Position("MNQ")
    assert g.day.locked and g.day.lock_reason == "daily_stop_hit"
    assert g.day.trades[0].reason == "t|daily_stop"


def test_flattens_at_1555(tmp_path):
    g = make_guardian(tmp_path)
    g.begin_session(DAY)
    open_long(g, qty=1, px=100.0, stop=99.0, hhmm="15:30")
    g.on_bar(bar("15:53", 100), g.broker.pos)
    assert "flatten" not in g.broker.kinds()
    g.on_bar(bar("15:54", 100), g.broker.pos)        # closes 15:55 -> flat at the 15:55 open
    assert g.broker.kinds()[-1] == "flatten"
    assert g.log.find("flatten")[-1]["reason"] == "flatten_time"
    assert g.submit_entry(at("15:55"), +1, 1, 99.0, None, 100.0).action == "reject"
    assert not g.strategy_enabled(bar("15:55", 100))


def test_clock_flatten_without_bars(tmp_path):
    g = make_guardian(tmp_path)
    g.begin_session(DAY)
    open_long(g, qty=1, px=100.0, stop=99.0, hhmm="15:30")
    g.on_clock(at("15:54:59"))
    assert "flatten" not in g.broker.kinds()
    g.on_clock(at("15:55:00"))
    assert g.broker.kinds()[-1] == "flatten"


def test_strategy_error_flattens_and_locks():
    rows = pd.date_range("2024-01-02 10:00", periods=10, freq="1min", tz=ET)
    bars = pd.DataFrame({"open": 100.0, "high": 100.5, "low": 99.5, "close": 100.0,
                         "volume": 1.0}, index=rows)

    class Broken:
        name, params = "broken", {}

        def reset(self):
            pass

        def on_bar(self, i, b, pos):
            if i == 0:
                return Signal(1, stop=95.0, tag="b")
            raise RuntimeError("boom")

    g = RiskGuardian(MNQ, GuardianConfig(kill_switch_path=None), log=EventLog())
    br = PaperBroker(bars, MNQ)
    eng = LiveEngine(Broken(), br, g, MNQ, qty=1)
    eng.start()
    br.run()
    eng.finish()
    assert g.log.find("strategy_error")
    (t,) = eng.days[0].trades
    assert t.reason == "b|strategy_error" and t.exit_time == rows[2]


def test_engine_paper_flat_by_1555():
    rows = pd.date_range("2024-01-02 15:40", "2024-01-02 15:59", freq="1min", tz=ET)
    bars = pd.DataFrame({"open": 100.0, "high": 100.5, "low": 99.5, "close": 100.0,
                         "volume": 1.0}, index=rows)

    class Once:
        name, params = "once", {}

        def reset(self):
            pass

        def on_bar(self, i, b, pos):
            return Signal(1, stop=90.0, target=120.0, tag="once") if i == 0 else None

    g = RiskGuardian(MNQ, GuardianConfig(kill_switch_path=None), log=EventLog())
    br = PaperBroker(bars, MNQ, slippage_ticks=1)
    eng = LiveEngine(Once(), br, g, MNQ, qty=1)
    eng.start()
    br.run()
    eng.finish()
    (t,) = eng.days[0].trades
    assert t.entry_time == rows[1] and t.exit_time == at("15:55")
    assert t.reason == "once|flatten_time" and t.exit == 100.0 - 0.25
    assert br.get_position("MNQ").qty == 0
    assert g.account.days_used == 1 and g.account.balance == pytest.approx(25_000 + t.pnl)


def test_kill_switch_flattens_and_halts(tmp_path):
    path = tmp_path / "state.json"
    g = make_guardian(tmp_path, state_path=str(path))
    g.begin_session(DAY)
    open_long(g, qty=1, px=100.0, stop=99.0)
    (tmp_path / "STOP").write_text("stop")
    g.on_bar(bar("10:05", 100), g.broker.pos)
    assert g.state.halted and g.state.halt_reason == "kill_switch"
    assert g.broker.kinds()[-1] == "flatten"
    assert g.submit_entry(at("10:10"), +1, 1, 99.0, None, 100.0).action == "reject"
    assert not g.strategy_enabled(bar("10:06", 100))
    # the halt survives a restart while the file exists ...
    g2 = make_guardian(tmp_path, state_path=str(path))
    assert g2.state.halted
    # ... and is cleared on restart once it is removed
    (tmp_path / "STOP").unlink()
    assert g2.state.halted  # not in-process: a running bot stays halted
    g3 = make_guardian(tmp_path, state_path=str(path))
    assert not g3.state.halted


def test_halts_after_pass(tmp_path):
    st = AccountState(MNQ)
    a = st.account
    a.balance, a.eod_high, a.floor, a.best_day, a.days_traded, a.days_used = (
        25_700.0, 25_700.0, 24_700.0, 400.0, 2, 2)
    g = make_guardian(tmp_path, state=st, bot_daily_stop=None)
    g.begin_session(DAY)
    d = open_long(g, qty=2, px=100.0, stop=90.0)
    g.on_fill(fill(d.order_id, -1, 2, 300.0, "target", "11:00"))   # +797.92 realised
    g.broker.pos = Position("MNQ")
    dr = g.end_session()
    assert dr.pnl == pytest.approx(797.92)
    # best day 797.92 needs total >= 1595.84 for consistency: 700 + 797.92 = 1497.92 -> not yet
    assert a.status != PASSED and not g.state.halted

    g.begin_session(DAY + pd.Timedelta(days=1))
    d = open_long(g, qty=1, px=100.0, stop=90.0)
    g.on_fill(fill(d.order_id, -1, 1, 150.0, "target", "11:00"))   # +98.96 -> 1596.88 total
    g.broker.pos = Position("MNQ")
    g.end_session()
    assert a.status == PASSED
    assert g.state.halted and g.state.halt_reason == PASSED_MSG
    assert any(e["reason"] == PASSED_MSG for e in g.log.find("halt"))
    g.begin_session(DAY + pd.Timedelta(days=2))
    assert g.submit_entry(at("10:00"), +1, 1, 99.0, None, 100.0).action == "reject"


def test_flattens_when_pass_reached_intraday(tmp_path):
    st = AccountState(MNQ)
    a = st.account
    a.balance, a.eod_high, a.floor, a.best_day, a.days_traded, a.days_used = (
        25_700.0, 25_700.0, 24_700.0, 600.0, 2, 2)
    g = make_guardian(tmp_path, state=st, bot_daily_stop=None, use_consistency_cap=False)
    g.begin_session(DAY)
    open_long(g, qty=2, px=100.0, stop=90.0)
    g.on_bar(bar("10:30", 150, 150, 149, 150), g.broker.pos)   # +197.92 open: not yet
    assert not g.day.locked
    g.on_bar(bar("10:31", 240, 240, 239, 240), g.broker.pos)   # +557.92 -> 1257.92 >= 1250
    assert g.day.lock_reason == "pass_reached" and g.broker.kinds()[-1] == "flatten"


# =========================================================================== persistence
def test_state_persistence_round_trip(tmp_path):
    path = tmp_path / "acct" / "state.json"
    g = make_guardian(tmp_path, state_path=str(path))
    g.begin_session(DAY)
    d = open_long(g, qty=2, px=100.0, stop=95.0)
    g.on_fill(fill(d.order_id, -1, 2, 130.0, "target", "11:00"))
    g.broker.pos = Position("MNQ")
    g.end_session()
    g.begin_session(DAY + pd.Timedelta(days=1))
    d = open_long(g, qty=1, px=100.0, stop=95.0)
    g.on_fill(fill(d.order_id, -1, 1, 96.0, "exit", "10:30"))
    g.lock_day("manual test lock", flatten=False)

    g2 = make_guardian(tmp_path, state_path=str(path))
    a, b = g.account, g2.account
    for k in ("balance", "eod_high", "floor", "best_day", "days_traded", "days_used", "status",
              "consistency_extended"):
        assert getattr(a, k) == getattr(b, k), k
    assert b.balance == pytest.approx(25_000 + 117.92) and b.best_day == pytest.approx(117.92)
    assert b.floor == pytest.approx(24_117.92)
    assert len(b.history) == 1 and b.history[0]["date"] == DAY
    # intraday ledger and lock survive too; resuming the same date keeps them
    assert g2.day.realized == pytest.approx(g.day.realized) and g2.day.locked
    assert g2.day.trades[0].pnl == pytest.approx(g.day.trades[0].pnl)
    g2.begin_session(DAY + pd.Timedelta(days=1))
    assert g2.day.locked and g2.day.lock_reason == "manual test lock"
    # a restart on a later date books the unfinished day first
    g3 = make_guardian(tmp_path, state_path=str(path))
    g3.begin_session(DAY + pd.Timedelta(days=2))
    assert g3.account.days_used == 2
    assert g3.account.balance == pytest.approx(25_000 + 117.92 - 9.04)
    raw = json.loads(path.read_text())
    assert raw["account"]["days_used"] == 2 and raw["day"]["applied"] is False


# =========================================================================== parity
PASS_THROUGH = dict(use_consistency_cap=False, enforce_account_limits=False,
                    check_stop_risk=False, halt_on_pass=False, halt_on_fail=False,
                    kill_switch_path=None, safety_buffer=0.0)


@pytest.mark.parametrize("name", ["ema_trend", "orb", "vwap_reversion"])
@pytest.mark.parametrize("daily_stop,cap", [(None, None), (60.0, None), (250.0, 150.0)])
def test_paper_broker_matches_backtest(name, daily_stop, cap):
    """Same strategy, same bars, same costs: PaperBroker + LiveEngine + RiskGuardian (in a
    pass-through configuration that only applies the backtester's daily stop / profit cap)
    must reproduce run_backtest day by day and trade by trade."""
    bars = generate_mnq(8, seed=3)
    bt = run_backtest(bars, make(name), MNQ, 2, EvalRules(), slippage_ticks=1,
                      daily_stop=daily_stop, daily_profit_cap=cap)
    g = RiskGuardian(MNQ, GuardianConfig(bot_daily_stop=daily_stop, daily_profit_cap=cap,
                                         **PASS_THROUGH), log=EventLog())
    br = PaperBroker(bars, MNQ, slippage_ticks=1)
    eng = LiveEngine(make(name), br, g, MNQ, qty=2)
    eng.start()
    br.run()
    eng.finish()
    assert len(eng.days) == len(bt) == 8
    assert sum(len(d.trades) for d in bt) > 0
    for a, b in zip(bt, eng.days):
        assert a.date == b.date
        assert b.pnl == pytest.approx(a.pnl, abs=1e-6)
        assert b.max_intraday_drawdown == pytest.approx(a.max_intraday_drawdown, abs=1e-6)
        assert len(a.trades) == len(b.trades)
        for ta, tb in zip(a.trades, b.trades):
            assert (ta.entry_time, ta.exit_time, ta.side, ta.qty) == \
                (tb.entry_time, tb.exit_time, tb.side, tb.qty)
            assert (tb.entry, tb.exit, tb.pnl) == pytest.approx((ta.entry, ta.exit, ta.pnl))
            assert ta.reason.split("|")[0] == tb.reason.split("|")[0]
    assert br.get_account_balance() == pytest.approx(25_000 + sum(d.pnl for d in bt))


def test_full_guardian_run_books_every_session():
    bars = generate_mnq(10, seed=5)
    g = RiskGuardian(MNQ, GuardianConfig(kill_switch_path=None), log=EventLog())
    br = PaperBroker(bars, MNQ)
    eng = LiveEngine(make("vwap_reversion"), br, g, MNQ, qty=4)
    eng.start()
    br.run()
    eng.finish()
    a = g.account
    assert len(eng.days) == 10 and a.days_used <= 10
    assert a.balance == pytest.approx(br.get_account_balance())
    for d in eng.days:   # guardian budget (<= $300) holds up to stop slippage
        assert d.pnl >= -300 - 4 * 2 * 2.0 * 0.25 - 1e-9


def test_cli_smoke(tmp_path, capsys):
    log = tmp_path / "run.jsonl"
    rc = cli_main(["--strategy", "ema_trend", "--params", '{"fast": 9}', "--qty", "2",
                   "--synthetic", "3", "--log", str(log), "--kill-switch", str(tmp_path / "STOP")])
    out = capsys.readouterr().out
    assert rc == 0
    assert "2023-01-03" in out and "account:" in out
    recs = [json.loads(line) for line in log.read_text().splitlines()]
    assert any(r["event"] == "day_closed" for r in recs)
    assert all({"agent", "event", "wall"} <= set(r) for r in recs)

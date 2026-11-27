import math

import pytest

from bot.config import ExecutionConfig, RiskConfig, StrategyConfig
from bot.fees import kalshi_fee, trade_economics
from bot.models import Action, BookLevel, Direction, OrderBook, Tick, parse_market, parse_orderbook
from bot.risk import RiskManager
from bot.signals import compute_features, estimate_p_up, random_walk_p_up, score_momentum
from bot.strategy import evaluate_entry


# ------------------------------------------------------------------ fees
def test_fee_rounds_up_to_cent():
    assert kalshi_fee(10, 0.50, 0.07) == 0.18     # 0.175 -> 0.18
    assert kalshi_fee(1, 0.50, 0.07) == 0.02      # 0.0175 -> 0.02
    assert kalshi_fee(100, 0.90, 0.07) == 0.63    # exact
    assert kalshi_fee(0, 0.5, 0.07) == 0.0


def test_trade_economics():
    e = trade_economics(10, 0.60, 0.17, 0.70)
    assert e["cost"] == pytest.approx(6.17)
    assert e["profit_if_win"] == pytest.approx(3.83)
    assert e["loss_if_lose"] == pytest.approx(6.17)
    assert e["ev"] == pytest.approx(0.7 * 3.83 - 0.3 * 6.17, abs=1e-4)


# ------------------------------------------------------------------ parsing
def test_parse_orderbook_cents_and_dollars():
    ob = parse_orderbook({"orderbook": {"yes": [[40, 10], [42, 5]], "no": [[55, 7], [50, 3]]}})
    assert ob.best_bid("yes") == 0.42 and ob.best_bid("no") == 0.55
    assert ob.best_ask("yes") == 0.45 and ob.best_ask("no") == 0.58
    ob2 = parse_orderbook({"orderbook_fp": {"yes_dollars": [["0.4200", "5.00"]], "no_dollars": [["0.5500", "7.00"]]}})
    assert ob2.best_ask("yes") == 0.45 and ob2.asks("yes")[0].qty == 7


def test_book_walk_respects_limit():
    ob = OrderBook(yes_bids=[], no_bids=[BookLevel(0.55, 5), BookLevel(0.53, 10)])  # yes asks 0.45 x5, 0.47 x10
    assert ob.walk("yes", 8, 0.46) == (5, pytest.approx(0.45))
    filled, avg = ob.walk("yes", 8, 0.47)
    assert filled == 8 and avg == pytest.approx((5 * 0.45 + 3 * 0.47) / 8)


def test_parse_market_up_side_and_times():
    m = parse_market({"ticker": "KXBTC15M-X", "open_time": "2026-01-01T00:00:00Z", "close_time": "2026-01-01T00:15:00Z",
                      "floor_strike": 95000.5, "status": "active", "strike_type": "greater_or_equal",
                      "yes_bid_dollars": "0.4500", "result": ""})
    assert m.duration == 900 and m.up_side == "yes" and m.strike == 95000.5 and m.yes_bid == 0.45 and m.result is None
    assert parse_market({"ticker": "T", "strike_type": "less"}, "yes").up_side == "no"


# ------------------------------------------------------------------ signals
def _ticks(start, prices, aggressor=None, step=1.0):
    return [Tick(start + i * step, p, 0.1, aggressor) for i, p in enumerate(prices)]


def test_strong_uptrend_scores_up():
    t0 = 1_000_000.0
    prices = [95000 * (1 + 0.000012 * i) for i in range(181)]  # +~21 bps over 3 min, smooth
    f = compute_features(_ticks(t0, prices, "buy"), t0, t0 + 180, None, vol_bps_per_min=5.0)
    sig = score_momentum(f, StrategyConfig())
    assert sig.direction == Direction.UP and sig.confidence > 70 and not sig.contradictions
    assert f.efficiency > 0.95 and f.flow_imbalance == 1.0
    assert estimate_p_up(f, 720, StrategyConfig()) > 0.6


def test_flow_contradiction_detected():
    t0 = 1_000_000.0
    prices = [95000 * (1 + 0.000012 * i) for i in range(181)]
    f = compute_features(_ticks(t0, prices, "sell"), t0, t0 + 180, None, vol_bps_per_min=5.0)
    sig = score_momentum(f, StrategyConfig())
    assert any("order flow" in c for c in sig.contradictions)


def test_reversal_detected_as_contradiction():
    t0 = 1_000_000.0
    up = [95000 * (1 + 0.00002 * i) for i in range(120)]
    down = [up[-1] * (1 - 0.00003 * i) for i in range(1, 61)]
    f = compute_features(_ticks(t0, up + down), t0, t0 + 180, None, vol_bps_per_min=5.0)
    sig = score_momentum(f, StrategyConfig())
    assert sig.contradictions  # still above open, but reversing hard


def test_probability_is_random_walk_when_no_persistence():
    t0 = 1_000_000.0
    prices = [95000 + i for i in range(181)]
    f = compute_features(_ticks(t0, prices), t0, t0 + 180, None, vol_bps_per_min=6.0)
    s = StrategyConfig(momentum_persistence=0.0, probability_shrink=1.0)
    assert estimate_p_up(f, 720, s) == pytest.approx(random_walk_p_up(f.dist_bps, 6.0, 720), abs=1e-9)


# ------------------------------------------------------------------ strategy
def _features(z=1.5, vol=6.0):
    t0 = 1_000_000.0
    move_bps = z * vol * math.sqrt(3)
    prices = [95000 * (1 + move_bps / 1e4 * i / 180) for i in range(181)]
    return compute_features(_ticks(t0, prices, "buy"), t0, t0 + 180, None, vol)


def _book(yes_ask, yes_bid, qty=500):
    return OrderBook(yes_bids=[BookLevel(yes_bid, qty)], no_bids=[BookLevel(round(1 - yes_ask, 2), qty)])


def _eval(f, book, s=None, rem=720):
    s = s or StrategyConfig(momentum_persistence=0.3)
    sig = score_momentum(f, s)
    p = estimate_p_up(f, rem, s)
    return evaluate_entry(f, sig, p, book, "yes", rem, s, ExecutionConfig(), RiskConfig()), p


def test_buy_when_underpriced():
    f = _features()
    d, p = _eval(f, _book(0.55, 0.53))
    assert p > 0.7
    assert d.action == Action.BUY_UP, d.reasons
    assert d.side == "yes" and d.contracts == int(10 // 0.55)
    assert d.limit_price <= p - 0.04 + 1e-9 and d.economics["ev"] > 0


def test_skip_when_overpriced():
    f = _features()
    s = StrategyConfig(momentum_persistence=0.3, max_contract_price=0.95)
    _, p = _eval(f, _book(0.50, 0.48), s)
    ask = round(p - 0.01, 2)  # priced above fair value minus the required edge
    d, _ = _eval(f, _book(ask, round(ask - 0.02, 2)), s)
    assert d.action == Action.SKIP and any("overpriced" in r or "edge" in r for r in d.reasons)


def test_skip_wide_spread_and_late_entry():
    f = _features()
    d, _ = _eval(f, _book(0.55, 0.40))
    assert d.action == Action.SKIP and "spread" in d.checks and not d.checks["spread"]["ok"]
    d2, _ = _eval(f, _book(0.55, 0.53), rem=300)
    assert d2.action == Action.SKIP and not d2.checks["time_remaining"]["ok"]


def test_skip_weak_signal():
    f = _features(z=0.3)
    d, _ = _eval(f, _book(0.52, 0.50))
    assert d.action == Action.SKIP


def test_down_signal_buys_no_side():
    t0 = 1_000_000.0
    prices = [95000 * (1 - 0.000015 * i) for i in range(181)]
    f = compute_features(_ticks(t0, prices, "sell"), t0, t0 + 180, None, 6.0)
    d, p = _eval(f, OrderBook(yes_bids=[BookLevel(0.44, 500)], no_bids=[BookLevel(0.42, 500)]))  # NO ask 0.56
    assert d.direction == Direction.DOWN and d.side == "no"
    assert d.p_win == pytest.approx(1 - p)


# ------------------------------------------------------------------ risk
def test_risk_daily_loss_and_streak(storage, tmp_path):
    rc = RiskConfig(dollars_per_trade=10, max_daily_loss=25, max_consecutive_losses=2, max_trades_per_day=5)
    rm = RiskManager(rc, storage, tmp_path, "paper")
    ok, _ = rm.check_can_open(10)
    assert ok
    rm.record_settle(-10)
    ok, reasons = rm.check_can_open(16)  # 10 realized + 16 > 25
    assert not ok and any("daily loss" in r for r in reasons)
    rm.record_settle(-10)
    assert rm.halted_reason and "consecutive" in rm.halted_reason
    assert not rm.check_can_open(1)[0]
    assert rm.resume() and rm.consecutive_losses == 0
    rm.record_settle(-6)  # total -26 -> daily halt
    assert rm.halted_reason.startswith("daily") and rm.resume() is False
    assert rm.trade_dollars() == 10  # never scaled after losses


def test_kill_switch_file(storage, tmp_path):
    rm = RiskManager(RiskConfig(), storage, tmp_path, "paper")
    (tmp_path / "KILL").touch()
    ok, reasons = rm.check_can_open(1)
    assert not ok and rm.kill_engaged
    rm.clear_kill()
    assert rm.check_can_open(1)[0] and not (tmp_path / "KILL").exists()


def test_risk_state_persists(storage, tmp_path):
    rm = RiskManager(RiskConfig(), storage, tmp_path, "paper")
    rm.record_open()
    rm.record_settle(-5)
    rm2 = RiskManager(RiskConfig(), storage, tmp_path, "paper")
    assert rm2.trades_today == 1 and rm2.realized_today == -5 and rm2.consecutive_losses == 1

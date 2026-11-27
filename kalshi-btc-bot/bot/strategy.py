"""Entry decision: turns a momentum signal + order book into BUY UP / BUY DOWN / SKIP.

Every check is recorded so the dashboard and analytics can show exactly why a market was skipped.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from .config import ExecutionConfig, RiskConfig, StrategyConfig
from .fees import kalshi_fee, trade_economics
from .models import Action, Direction, OrderBook
from .signals import MomentumFeatures, MomentumSignal


@dataclass
class TradeDecision:
    action: Action
    direction: Direction
    confidence: float = 0.0
    p_up: float | None = None
    p_win: float | None = None
    side: str | None = None
    contracts: int = 0
    best_ask: float | None = None
    best_bid: float | None = None
    spread: float | None = None
    limit_price: float | None = None
    expected_avg_price: float | None = None
    depth: int = 0
    fee: float = 0.0
    economics: dict = field(default_factory=dict)
    checks: dict = field(default_factory=dict)   # name -> {"ok": bool, "detail": str}
    reasons: list = field(default_factory=list)  # failed checks (skip reasons)

    @property
    def is_buy(self) -> bool:
        return self.action != Action.SKIP

    def to_dict(self) -> dict:
        return {
            "action": self.action.value,
            "direction": self.direction.value,
            "confidence": round(self.confidence, 2),
            "p_up": None if self.p_up is None else round(self.p_up, 4),
            "p_win": None if self.p_win is None else round(self.p_win, 4),
            "side": self.side,
            "contracts": self.contracts,
            "best_ask": self.best_ask,
            "best_bid": self.best_bid,
            "spread": self.spread,
            "limit_price": self.limit_price,
            "expected_avg_price": None if self.expected_avg_price is None else round(self.expected_avg_price, 4),
            "depth": self.depth,
            "fee": self.fee,
            "economics": self.economics,
            "checks": self.checks,
            "reasons": self.reasons,
        }


def _check(d: TradeDecision, name: str, ok: bool, detail: str) -> bool:
    d.checks[name] = {"ok": bool(ok), "detail": detail}
    if not ok:
        d.reasons.append(f"{name}: {detail}")
    return ok


def evaluate_entry(
    features: MomentumFeatures | None,
    signal: MomentumSignal | None,
    p_up: float | None,
    book: OrderBook | None,
    up_side: str,
    seconds_remaining: float,
    s: StrategyConfig,
    ex: ExecutionConfig,
    risk: RiskConfig,
) -> TradeDecision:
    if features is None or signal is None:
        d = TradeDecision(Action.SKIP, Direction.NONE)
        _check(d, "data", False, "insufficient BTC price data")
        return d

    d = TradeDecision(Action.SKIP, signal.direction, confidence=signal.confidence, p_up=p_up)

    # ---- signal quality (all evaluated, so analytics see every failing reason)
    _check(d, "ticks", features.n_ticks >= s.min_ticks, f"{features.n_ticks} price updates (min {s.min_ticks})")
    _check(d, "direction", signal.direction != Direction.NONE, signal.direction.value)
    _check(d, "contradictions", not signal.contradictions,
           "; ".join(signal.contradictions) if signal.contradictions else "none")
    _check(d, "confidence", signal.confidence >= s.min_confidence,
           f"{signal.confidence:.1f} (min {s.min_confidence:.0f})")
    _check(d, "move_size", abs(features.z_score) >= s.min_abs_z, f"|z|={abs(features.z_score):.2f} (min {s.min_abs_z})")
    _check(d, "volatility", s.min_vol_bps_per_min <= features.vol_bps_per_min <= s.max_vol_bps_per_min,
           f"{features.vol_bps_per_min:.2f} bps/min (allowed {s.min_vol_bps_per_min}-{s.max_vol_bps_per_min})")
    _check(d, "time_remaining", seconds_remaining >= s.min_seconds_remaining,
           f"{seconds_remaining:.0f}s left (min {s.min_seconds_remaining}s)")

    if signal.direction == Direction.NONE or p_up is None:
        return d

    side = up_side if signal.direction == Direction.UP else ("no" if up_side == "yes" else "yes")
    p_win = p_up if signal.direction == Direction.UP else 1.0 - p_up
    d.side, d.p_win = side, p_win

    # ---- market / pricing
    if book is None:
        _check(d, "liquidity", False, "order book unavailable")
        return d
    ask, bid = book.best_ask(side), book.best_bid(side)
    d.best_ask, d.best_bid, d.spread = ask, bid, book.spread(side)
    if not _check(d, "liquidity", ask is not None, "ask available" if ask is not None else "no asks on our side"):
        return d
    _check(d, "spread", d.spread is not None and d.spread <= s.max_spread + 1e-9,
           f"{d.spread:.2f} (max {s.max_spread:.2f})" if d.spread is not None else "n/a")
    _check(d, "price_range", s.min_contract_price <= ask <= s.max_contract_price,
           f"ask {ask:.2f} (allowed {s.min_contract_price:.2f}-{s.max_contract_price:.2f})")

    # Never pay more than fair value minus required edge, best ask + slippage, or max price.
    fee_rate = ex.taker_fee_rate if ex.order_style == "ioc" else ex.maker_fee_rate
    limit = min(ask + ex.max_slippage, s.max_contract_price, p_win - s.min_edge)
    limit = math.floor(limit * 100 + 1e-9) / 100.0
    d.limit_price = limit
    target = int(risk.dollars_per_trade // ask) if ask > 0 else 0
    if not _check(d, "position_size", target >= 1, f"${risk.dollars_per_trade:.2f} buys {target} contracts at {ask:.2f}"):
        return d
    if limit < ask - 1e-9:
        _check(d, "overpriced", False,
               f"ask {ask:.2f} exceeds max acceptable {limit:.2f} (p_win {p_win:.3f} - edge {s.min_edge:.2f})")
        return d

    filled, avg = book.walk(side, target, limit)
    d.depth = book.depth_at_or_below(side, limit)
    if not _check(d, "depth", filled >= max(1, math.ceil(target * s.min_fill_ratio)),
                  f"{filled}/{target} contracts available at <= {limit:.2f}"):
        return d
    d.contracts, d.expected_avg_price = filled, avg
    d.fee = kalshi_fee(filled, avg, fee_rate)
    econ = trade_economics(filled, avg, d.fee, p_win)
    d.economics = econ
    _check(d, "edge", econ["edge_per_contract"] >= s.min_edge,
           f"{econ['edge_per_contract']:+.3f}/contract after fees (min {s.min_edge:.2f})")
    _check(d, "expected_value", econ["ev_per_dollar"] >= s.min_ev_per_dollar,
           f"EV {econ['ev']:+.2f} = {econ['ev_per_dollar']*100:+.1f}% of risk (min {s.min_ev_per_dollar*100:.0f}%)")

    if not d.reasons:
        d.action = Action.BUY_UP if signal.direction == Direction.UP else Action.BUY_DOWN
    return d

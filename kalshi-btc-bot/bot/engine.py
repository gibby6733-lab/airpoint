"""Trading engine: the per-market state machine.

  1. detect new BTC 15m market       -> OBSERVING
  2-3. observe BTC for 3 minutes     (live momentum shown on dashboard, no orders)
  4-6. at minute 3: features -> signal -> probability -> pricing/liquidity/fee/EV checks -> risk checks
  7. re-validate signal on fresh data, then send a limit order; record only confirmed fills
  8-9. after close: poll the market result, record P&L for trades and "shadow" P&L for skips
  10. move to the next market automatically
"""
from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from enum import Enum

from .config import Config
from .execution import FillResult, client_order_id_for
from .fees import kalshi_fee
from .models import Action, Direction, Market, OrderBook
from .risk import RiskManager
from .signals import (MomentumFeatures, MomentumSignal, compute_features, estimate_p_up, price_at,
                      score_momentum)
from .storage import Storage
from .strategy import TradeDecision, evaluate_entry

log = logging.getLogger("engine")


class Phase(str, Enum):
    WAITING = "WAITING_FOR_MARKET"
    OBSERVING = "OBSERVING"
    DECIDING = "DECIDING"
    IN_POSITION = "IN_POSITION"
    SKIPPED = "SKIPPED"
    MISSED = "MISSED"


@dataclass
class Session:
    market: Market
    phase: Phase
    btc_open: float | None = None
    features: MomentumFeatures | None = None
    signal: MomentumSignal | None = None
    p_up: float | None = None
    decision: TradeDecision | None = None
    fill: FillResult | None = None
    book: OrderBook | None = None
    book_ts: float = 0.0
    notes: list = field(default_factory=list)
    decided_at: float | None = None
    shadow_side: str | None = None
    shadow_price: float | None = None


class TradingEngine:
    def __init__(self, cfg: Config, storage: Storage, market_data, feed, executor, risk: RiskManager, clock,
                 gate: dict | None = None):
        self.cfg = cfg
        self.storage = storage
        self.md = market_data
        self.feed = feed
        self.executor = executor
        self.risk = risk
        self.clock = clock
        self.gate = gate or {}
        self.mode = executor.mode
        self.session: Session | None = None
        self.pending: dict[str, dict] = {}     # ticker -> {close_ts, up_side, next_poll}
        self.last_lookup = 0.0
        self.started_at = clock.now()
        self.errors: list[dict] = []
        self.balance: float | None = None
        self._kill_handled = False
        self._stop = False
        self._decision_log = cfg.data_dir / "decisions.jsonl"

    # ------------------------------------------------------------ lifecycle
    def recover(self):
        """Re-attach open positions and unsettled markets after a restart."""
        now = self.clock.now()
        for p in self.storage.open_positions(self.mode):
            m = self.storage.get_market(p["ticker"]) or {}
            self.pending[p["ticker"]] = {"close_ts": p["close_ts"] or m.get("close_ts") or now,
                                         "up_side": m.get("up_side", "yes"), "next_poll": now}
        for m in self.storage.unsettled_markets(now):
            self.pending.setdefault(m["ticker"], {"close_ts": m["close_ts"], "up_side": m["up_side"] or "yes",
                                                  "next_poll": now})
        if self.pending:
            log.info("recovered %d market(s) awaiting settlement", len(self.pending))

    async def run(self):
        self.recover()
        self.storage.log(None, "INFO", f"engine started in {self.mode.upper()} mode "
                                       f"(data source: {self.cfg.mode.data_source})")
        while not self._stop:
            try:
                await self.step()
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # noqa: BLE001 - the loop must survive any single failure
                log.exception("engine step failed")
                self._error(f"{type(exc).__name__}: {exc}")
                await self.clock.sleep(2.0)
            await self.clock.sleep(1.0)

    def stop(self):
        self._stop = True

    def _error(self, msg: str, ticker: str | None = None):
        self.errors.append({"ts": self.clock.now(), "message": msg})
        self.errors = self.errors[-20:]
        self.storage.log(ticker, "ERROR", msg)

    # ------------------------------------------------------------ main step
    async def step(self):
        now = self.clock.now()
        self.risk.tick()
        if self.risk.kill_engaged and not self._kill_handled:
            n = await self.executor.cancel_all()
            self._kill_handled = True
            self.storage.log(None, "CRITICAL", f"kill switch: cancelled {n} resting order(s); no new orders")
        elif not self.risk.kill_engaged:
            self._kill_handled = False

        # Retire an expired session to the settlement queue BEFORE looking for the next market.
        if self.session is not None and now >= self.session.market.close_ts:
            m = self.session.market
            self.pending[m.ticker] = {"close_ts": m.close_ts, "up_side": m.up_side, "next_poll": m.close_ts + 5}
            self.session = None
        await self._ensure_market(now)
        s = self.session
        if s is not None:
            if s.phase == Phase.OBSERVING:
                self._update_live_signal(s, now)
                if now >= s.market.open_ts + self.cfg.strategy.observation_seconds:
                    if now > s.market.open_ts + self.cfg.strategy.observation_seconds + self.cfg.strategy.max_entry_delay_seconds:
                        self._mark_missed(s, "decision window passed (bot was delayed)")
                    else:
                        await self._decide(s)
            if now - s.book_ts > 3 and now < s.market.close_ts:
                try:
                    s.book = await self.md.get_orderbook(s.market.ticker)
                    s.book_ts = now
                except Exception as exc:  # noqa: BLE001
                    log.debug("book refresh failed: %s", exc)
        await self._settle_pending(now)

    # ------------------------------------------------------------ market detection
    async def _ensure_market(self, now: float):
        s = self.session
        if s is not None and now < s.market.close_ts:
            return
        if now - self.last_lookup < 3:
            return
        self.last_lookup = now
        m = await self.md.find_current_market(now)
        if m is None:
            return
        if s is not None and s.market.ticker == m.ticker:
            return
        self._start_session(m, now)

    def _start_session(self, m: Market, now: float):
        st = self.cfg.strategy
        s = Session(m, Phase.OBSERVING)
        self.session = s
        ticks = self.feed.buffer.between(m.open_ts - 30, now)
        s.btc_open = price_at(ticks, m.open_ts)
        existing = self.storage.get_market(m.ticker)
        base = dict(event_ticker=m.event_ticker, mode=self.mode, open_ts=m.open_ts, close_ts=m.close_ts,
                    strike=m.strike, up_side=m.up_side, btc_open=s.btc_open)
        if existing and existing.get("mode") == self.mode and existing.get("decision"):
            # Restarted after the decision was already made for this market: never decide twice.
            s.phase = Phase.IN_POSITION if self.storage.has_position(m.ticker, self.mode) else Phase.SKIPPED
            s.notes.append("decision already recorded before restart")
            return
        self.storage.upsert_market(m.ticker, **base)
        self.storage.log(m.ticker, "INFO", f"new market detected, closes {time.strftime('%H:%M:%S', time.gmtime(m.close_ts))} UTC",
                         {"open_ts": m.open_ts, "close_ts": m.close_ts, "strike": m.strike})
        log.info("market %s open=%s close=%s strike=%s", m.ticker, m.open_ts, m.close_ts, m.strike)

        if not (self.cfg.kalshi.min_market_duration_seconds <= m.duration <= self.cfg.kalshi.max_market_duration_seconds):
            return self._mark_missed(s, f"unexpected market duration {m.duration:.0f}s")
        if now - m.open_ts > st.observation_seconds + st.max_entry_delay_seconds:
            return self._mark_missed(s, "joined after the observation window")
        first_tick_ts = ticks[0].ts if ticks else None
        if first_tick_ts is None or first_tick_ts > m.open_ts + 5:
            return self._mark_missed(s, "no BTC data from the market open (bot started mid-window)")

    def _mark_missed(self, s: Session, reason: str):
        s.phase = Phase.MISSED
        s.notes.append(reason)
        s.decision = TradeDecision(Action.SKIP, Direction.NONE, reasons=[f"missed: {reason}"])
        self.storage.upsert_market(s.market.ticker, decision="SKIP", skip_reasons=[f"missed: {reason}"])
        self.storage.log(s.market.ticker, "INFO", f"SKIP (missed): {reason}")

    # ------------------------------------------------------------ signal
    def _compute(self, s: Session, now: float):
        st = self.cfg.strategy
        ticks = self.feed.buffer.between(s.market.open_ts, now)
        vol = self.feed.buffer.vol_bps_per_min(st.vol_lookback_minutes, s.market.open_ts)
        if vol is None:
            return None, None, None
        ref = s.market.strike if (st.reference_mode == "kalshi_strike" and s.market.strike) else None
        f = compute_features(ticks, s.market.open_ts, now, ref, vol, open_price=s.btc_open)
        if f is None:
            return None, None, None
        sig = score_momentum(f, st)
        p = estimate_p_up(f, s.market.close_ts - now, st)
        return f, sig, p

    def _update_live_signal(self, s: Session, now: float):
        s.features, s.signal, s.p_up = self._compute(s, now)

    async def _decide(self, s: Session):
        st, now = self.cfg.strategy, self.clock.now()
        s.phase = Phase.DECIDING
        s.decided_at = now
        stale = self.feed.buffer.is_stale(now, self.feed.stale_after)
        s.features, s.signal, s.p_up = self._compute(s, now)
        try:
            book = await self.md.get_orderbook(s.market.ticker)
            s.book, s.book_ts = book, now
        except Exception as exc:  # noqa: BLE001
            book = None
            self._error(f"order book fetch failed: {exc}", s.market.ticker)
        d = evaluate_entry(s.features, s.signal, s.p_up, book, s.market.up_side, s.market.close_ts - now,
                           st, self.cfg.execution, self.cfg.risk)
        if stale:
            d.action = Action.SKIP
            d.reasons.append("feed: BTC price feed is stale")
        if s.signal and s.signal.direction != Direction.NONE and book is not None:
            s.shadow_side = s.market.side_for(s.signal.direction)
            s.shadow_price = book.best_ask(s.shadow_side)

        if d.is_buy:
            d = await self._pre_trade_checks(s, d)
        if d.is_buy:
            await self._execute(s, d)
        else:
            s.decision = d
            s.phase = Phase.SKIPPED
        self._persist_decision(s)

    async def _pre_trade_checks(self, s: Session, d: TradeDecision) -> TradeDecision:
        st = self.cfg.strategy
        if self.storage.has_position(s.market.ticker, self.mode):
            return self._block(d, "duplicate: a position already exists for this market")
        ok, reasons = self.risk.check_can_open(d.economics.get("loss_if_lose", 0.0))
        if not ok:
            return self._block(d, *[f"risk: {r}" for r in reasons])
        # Re-validate: the momentum must still hold on the freshest data and fresh prices.
        now2 = self.clock.now()
        f2, sig2, p2 = self._compute(s, now2)
        if f2 is None or sig2.direction != d.direction or abs(f2.z_score) < st.min_abs_z * st.revalidate_min_z_ratio:
            return self._block(d, "revalidate: momentum signal no longer valid at order time")
        try:
            book2 = await self.md.get_orderbook(s.market.ticker)
        except Exception as exc:  # noqa: BLE001
            return self._block(d, f"revalidate: order book unavailable ({exc})")
        d2 = evaluate_entry(f2, sig2, p2, book2, s.market.up_side, s.market.close_ts - now2,
                            st, self.cfg.execution, self.cfg.risk)
        if not d2.is_buy or d2.side != d.side:
            d.reasons = [f"revalidate: {r}" for r in (d2.reasons or ["decision changed"])]
            d.action = Action.SKIP
            return d
        ok, reasons = self.risk.check_can_open(d2.economics.get("loss_if_lose", 0.0))
        if not ok:
            return self._block(d2, *[f"risk: {r}" for r in reasons])
        if self.mode == "live":
            try:
                self.balance = await self.executor.client.get_balance()
            except Exception as exc:  # noqa: BLE001
                return self._block(d2, f"balance check failed: {exc}")
            need = d2.economics["cost"] + self.cfg.risk.min_balance_reserve
            if self.balance < need:
                return self._block(d2, f"insufficient balance ${self.balance:.2f} < ${need:.2f}")
        s.features, s.signal, s.p_up = f2, sig2, p2
        return d2

    @staticmethod
    def _block(d: TradeDecision, *reasons: str) -> TradeDecision:
        d.action = Action.SKIP
        d.reasons.extend(reasons)
        return d

    async def _execute(self, s: Session, d: TradeDecision):
        cid = client_order_id_for(s.market.ticker, d.side, self.mode)
        self.storage.log(s.market.ticker, "INFO",
                         f"placing {self.mode} limit BUY {d.contracts} {d.side.upper()} @ <= {d.limit_price:.2f}",
                         {"client_order_id": cid})
        fill = await self.executor.buy(s.market.ticker, d.side, d.contracts, d.limit_price, cid)
        s.fill = fill
        if fill.filled > 0:
            try:
                self.storage.open_position(ticker=s.market.ticker, mode=self.mode, side=d.side, contracts=fill.filled,
                                           avg_price=fill.avg_price, fees=fill.fees, cost=fill.cost,
                                           order_id=fill.order_id, client_order_id=cid, status="open",
                                           opened_at=self.clock.now(), close_ts=s.market.close_ts)
            except Exception as exc:  # noqa: BLE001 - UNIQUE constraint = duplicate guard
                self._error(f"position record failed (duplicate?): {exc}", s.market.ticker)
            self.risk.record_open()
            s.phase = Phase.IN_POSITION
            self.storage.log(s.market.ticker, "TRADE",
                             f"FILLED {fill.filled} {d.side.upper()} @ {fill.avg_price:.3f} fees ${fill.fees:.2f} "
                             f"({fill.status})")
        else:
            d.action = Action.SKIP
            d.reasons.append(f"execution: order not filled ({fill.status}: {fill.message})")
            s.phase = Phase.SKIPPED
        s.decision = d

    def _persist_decision(self, s: Session):
        d, f, sig = s.decision, s.features, s.signal
        row = dict(
            btc_at_decision=f.price_now if f else None,
            pct_change=f.ret_pct if f else None,
            direction=sig.direction.value if sig else None,
            confidence=sig.confidence if sig else None,
            z_score=f.z_score if f else None,
            volatility=f.vol_bps_per_min if f else None,
            slope=f.slope_bps_per_min if f else None,
            accel=f.accel_bps_per_min if f else None,
            efficiency=f.efficiency if f else None,
            flow_imbalance=f.flow_imbalance if f else None,
            p_up=s.p_up, p_win=d.p_win,
            decision="SKIP" if not d.is_buy else d.action.value,
            skip_reasons=d.reasons,
            side=d.side, entry_ask=d.best_ask, limit_price=d.limit_price,
            expected_ev=d.economics.get("ev"),
            shadow_side=s.shadow_side, shadow_price=s.shadow_price,
            features_json=f.to_dict() if f else None,
            decision_json={**d.to_dict(), "signal": sig.to_dict() if sig else None},
        )
        if s.fill and s.fill.filled > 0:
            row.update(exec_price=s.fill.avg_price, contracts=s.fill.filled, fees=s.fill.fees, cost=s.fill.cost)
        self.storage.upsert_market(s.market.ticker, **row)
        summary = (f"{'SKIP' if not d.is_buy else d.action.value} | dir={row['direction']} "
                   f"conf={row['confidence'] or 0:.0f} z={row['z_score'] or 0:+.2f} p_win={d.p_win or 0:.3f} "
                   f"ask={d.best_ask}")
        if d.reasons:
            summary += " | " + "; ".join(d.reasons[:3])
        self.storage.log(s.market.ticker, "DECISION", summary)
        try:
            with open(self._decision_log, "a") as fh:
                fh.write(json.dumps({"ts": self.clock.now(), "ticker": s.market.ticker, "mode": self.mode,
                                     "decision": row["decision_json"], "features": row["features_json"]},
                                    default=str) + "\n")
        except OSError:
            pass

    # ------------------------------------------------------------ settlement
    async def _settle_pending(self, now: float):
        for ticker, info in list(self.pending.items()):
            if now < info["next_poll"]:
                continue
            info["next_poll"] = now + 10
            if now - info["close_ts"] > 6 * 3600:
                self._error(f"settlement not available after 6h; giving up polling {ticker}", ticker)
                del self.pending[ticker]
                continue
            try:
                m = await self.md.get_market(ticker)
            except Exception as exc:  # noqa: BLE001
                log.debug("settlement poll failed for %s: %s", ticker, exc)
                continue
            if not m.is_settled:
                continue
            self._record_settlement(m, info)
            del self.pending[ticker]

    def _record_settlement(self, m: Market, info: dict):
        up_side = info.get("up_side") or m.up_side
        up_won = m.result == up_side
        btc_close = price_at(self.feed.buffer.between(m.close_ts - 30, m.close_ts + 1), m.close_ts)
        row = dict(outcome=m.result, up_won=int(up_won), btc_close=btc_close)
        pos = next((p for p in self.storage.open_positions(self.mode) if p["ticker"] == m.ticker), None)
        if pos:
            won = pos["side"] == m.result
            payout = float(pos["contracts"]) if won else 0.0
            pnl = round(payout - pos["cost"], 4)
            self.storage.settle_position(pos["id"], m.result, payout, pnl, won)
            self.risk.record_settle(pnl)
            row.update(won=int(won), pnl=pnl)
            self.storage.log(m.ticker, "SETTLE", f"{'WIN' if won else 'LOSS'} result={m.result.upper()} "
                                                 f"payout ${payout:.2f} P&L {pnl:+.2f}")
        else:
            mk = self.storage.get_market(m.ticker) or {}
            if mk.get("shadow_side") and mk.get("shadow_price"):
                price = mk["shadow_price"]
                fee1 = kalshi_fee(1, price, self.cfg.execution.taker_fee_rate)
                row["shadow_pnl"] = round((1 - price - fee1) if mk["shadow_side"] == m.result else (-price - fee1), 4)
            self.storage.log(m.ticker, "SETTLE", f"result={m.result.upper()} ({'UP' if up_won else 'DOWN'}) - no position")
        self.storage.upsert_market(m.ticker, **row)

    # ------------------------------------------------------------ dashboard snapshot
    def snapshot(self) -> dict:
        now = self.clock.now()
        buf = self.feed.buffer
        st = self.cfg.strategy
        s = self.session
        market = None
        chart_start = now - 20 * 60
        if s:
            m = s.market
            chart_start = min(chart_start, m.open_ts - 120)
            d = s.decision
            market = {
                "ticker": m.ticker, "title": m.title, "open_ts": m.open_ts, "close_ts": m.close_ts,
                "strike": m.strike, "up_side": m.up_side, "phase": s.phase.value,
                "seconds_to_close": max(0.0, m.close_ts - now),
                "seconds_to_decision": max(0.0, m.open_ts + st.observation_seconds - now),
                "observation_progress": min(1.0, max(0.0, (now - m.open_ts) / st.observation_seconds)),
                "btc_open": s.btc_open,
                "reference_price": (m.strike if st.reference_mode == "kalshi_strike" and m.strike else s.btc_open),
                "book": s.book.to_dict() if s.book else None,
                "notes": s.notes,
                "features": s.features.to_dict() if s.features else None,
                "signal": s.signal.to_dict() if s.signal else None,
                "p_up": s.p_up,
                "decision": d.to_dict() if d else None,
                "fill": ({"status": s.fill.status, "filled": s.fill.filled, "avg_price": s.fill.avg_price,
                          "fees": s.fill.fees, "cost": s.fill.cost} if s.fill else None),
            }
        open_pos = self.storage.open_positions(self.mode)
        for p in open_pos:
            p["potential_payout"] = float(p["contracts"])
            p["potential_profit"] = round(p["contracts"] - p["cost"], 4)
        return {
            "server_time": now,
            "mode": self.mode,
            "requested_mode": self.cfg.mode.trading_mode,
            "data_source": self.cfg.mode.data_source,
            "gate": self.gate,
            "btc": {"price": buf.last_price(), "last_update": buf.last_update, "source": buf.source,
                    "status": self.feed.status, "stale": buf.is_stale(now, self.feed.stale_after),
                    "vol_bps_per_min": buf.vol_bps_per_min(st.vol_lookback_minutes, now),
                    "chart": buf.chart_points(chart_start, now, step=2.0)},
            "market": market,
            "positions": open_pos,
            "pending_settlement": list(self.pending.keys()),
            "trades": self.storage.settled_positions(self.mode, limit=50),
            "markets": self.storage.recent_markets(40),
            "stats": self.storage.performance(self.mode, self.cfg.risk.timezone_offset_hours),
            "risk": self.risk.snapshot(),
            "logs": self.storage.recent_logs(40),
            "errors": self.errors[-5:],
            "balance": self.balance,
        }

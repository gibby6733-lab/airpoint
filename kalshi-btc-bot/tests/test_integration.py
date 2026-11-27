import asyncio
import base64
import json
import time

import httpx
import pytest
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from bot.backtest.data import synthetic_candles
from bot.backtest.engine import prepare_windows, run_backtest
from bot.config import ExecutionConfig
from bot.engine import Phase, TradingEngine
from bot.execution import LiveExecutor, PaperExecutor, client_order_id_for
from bot.kalshi_client import KalshiClient, KalshiSigner
from bot.live_gate import evaluate_live_gate
from bot.risk import RiskManager
from bot.simulator import ManualClock, SimFeed, SimMarketData, SimWorld


def run(coro):
    return asyncio.run(coro)


@pytest.fixture(scope="module")
def keypair():
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
    return key, pem


# ------------------------------------------------------------------ Kalshi auth + client
def test_signature_verifies(keypair):
    key, pem = keypair
    h = KalshiSigner("kid", pem).headers("POST", "/trade-api/v2/portfolio/orders?x=1", ts_ms=1700000000000)
    assert h["KALSHI-ACCESS-KEY"] == "kid" and h["KALSHI-ACCESS-TIMESTAMP"] == "1700000000000"
    key.public_key().verify(base64.b64decode(h["KALSHI-ACCESS-SIGNATURE"]),
                            b"1700000000000POST/trade-api/v2/portfolio/orders",
                            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.DIGEST_LENGTH),
                            hashes.SHA256())


def test_client_retries_and_parses(keypair):
    calls = {"n": 0}

    def handler(req: httpx.Request):
        if req.url.path.endswith("/markets"):
            calls["n"] += 1
            if calls["n"] == 1:
                return httpx.Response(503, json={"error": {"message": "busy"}})
            return httpx.Response(200, json={"markets": [{
                "ticker": "KXBTC15M-26NOV271215", "event_ticker": "KXBTC15M-26NOV271215",
                "open_time": "2026-11-27T12:00:00Z", "close_time": "2026-11-27T12:15:00Z",
                "status": "active", "floor_strike": 97000.0, "yes_ask": 52, "yes_bid": 50}]})
        if req.url.path.endswith("/portfolio/balance"):
            assert "KALSHI-ACCESS-SIGNATURE" in req.headers
            return httpx.Response(200, json={"balance": 12345})
        return httpx.Response(404, json={})

    async def go():
        c = KalshiClient("https://example.test", KalshiSigner("k", keypair[1]), transport=httpx.MockTransport(handler))
        ms = await c.list_markets("KXBTC15M", "yes")
        bal = await c.get_balance()
        await c.close()
        return ms, bal

    import bot.kalshi_client as kc
    orig = kc.asyncio.sleep
    kc.asyncio.sleep = lambda s: orig(0)
    try:
        ms, bal = run(go())
    finally:
        kc.asyncio.sleep = orig
    assert calls["n"] == 2 and ms[0].duration == 900 and ms[0].yes_ask == 0.52 and bal == 123.45


# ------------------------------------------------------------------ live executor (mock Kalshi)
class FakeKalshi:
    authenticated = True

    def __init__(self, fill_count=5, duplicate=False):
        self.fill_count, self.duplicate, self.orders = fill_count, duplicate, []

    async def create_order(self, body):
        from bot.kalshi_client import KalshiError
        self.orders.append(body)
        if self.duplicate:
            raise KalshiError(409, "duplicate client_order_id")
        return {"order": {"order_id": "o1", "status": "executed" if self.fill_count else "canceled"}}

    async def find_order_by_client_id(self, ticker, cid):
        return {"order_id": "o1", "status": "executed", "client_order_id": cid}

    async def get_order(self, oid):
        return {"order_id": oid, "status": "executed", "side": "yes", "count": 5, "fill_count": self.fill_count,
                "taker_fees": 9}

    async def get_fills(self, order_id=None, ticker=None):
        return [{"count": self.fill_count, "yes_price": 54}] if self.fill_count else []

    async def get_resting_orders(self):
        return []


def test_live_executor_confirms_fills():
    fk = FakeKalshi()
    ex = LiveExecutor(fk, ExecutionConfig(), sleep=lambda s: asyncio.sleep(0))
    r = run(ex.buy("T", "yes", 5, 0.55, "cid"))
    assert fk.orders[0]["time_in_force"] == "immediate_or_cancel" and fk.orders[0]["yes_price"] == 55
    assert fk.orders[0]["type"] == "limit" and fk.orders[0]["action"] == "buy"
    assert r.filled == 5 and r.avg_price == 0.54 and r.fees == 0.09 and r.status == "filled"


def test_live_executor_unfilled_and_duplicate():
    r = run(LiveExecutor(FakeKalshi(fill_count=0), ExecutionConfig(), sleep=lambda s: asyncio.sleep(0)).buy("T", "yes", 5, 0.55, "c"))
    assert r.status == "unfilled" and r.filled == 0
    r2 = run(LiveExecutor(FakeKalshi(duplicate=True), ExecutionConfig(), sleep=lambda s: asyncio.sleep(0)).buy("T", "yes", 5, 0.55, "c"))
    assert r2.order_id == "o1"  # recovered the existing order instead of placing another


def test_client_order_id_is_deterministic():
    assert client_order_id_for("T", "yes", "live") == client_order_id_for("T", "yes", "live")
    assert client_order_id_for("T", "yes", "live") != client_order_id_for("T2", "yes", "live")


# ------------------------------------------------------------------ engine end-to-end on the simulator
def _sim_engine(cfg, storage, seed=3, drift=2.5):
    start = (time.time() // 900) * 900 + 900 - 10  # 10s before a market opens
    clock = ManualClock(start)
    world = SimWorld(start, seed=seed, drift_std_bps_per_min=drift)
    md = SimMarketData(world, clock)
    feed = SimFeed(world, clock)
    ex = PaperExecutor(md, cfg.execution, sleep=clock.sleep)
    risk = RiskManager(cfg.risk, storage, cfg.data_dir, "paper", clock=clock.now)
    eng = TradingEngine(cfg, storage, md, feed, ex, risk, clock, gate={})
    return eng, clock, world


def _drive(eng, clock, world, seconds):
    async def go():
        eng.recover()
        for _ in range(int(seconds)):
            world.advance(clock.now())
            await eng.step()
            clock.t += 1.0
    run(go())


def test_engine_full_cycle(cfg, storage):
    cfg.strategy.momentum_persistence = 0.4  # sim has momentum by construction
    eng, clock, world = _sim_engine(cfg, storage)
    _drive(eng, clock, world, 900 * 8 + 60)
    markets = storage.recent_markets(50)
    assert len(markets) >= 8
    decided = [m for m in markets if m["decision"]]
    assert len(decided) >= 8
    for m in decided:
        if m["decision"].startswith("BUY"):
            assert m["contracts"] and m["exec_price"] and m["cost"] <= cfg.risk.dollars_per_trade + 1
    settled = [m for m in markets if m["outcome"]]
    assert len(settled) >= 7
    # every settled market has its BTC snapshot and analytics recorded
    for m in settled:
        assert m["btc_open"] and m["outcome"] in ("yes", "no")
    pos = storage.settled_positions("paper")
    tickers = [p["ticker"] for p in pos]
    assert len(tickers) == len(set(tickers))  # never two positions in one market
    perf = storage.performance("paper")
    assert perf["markets_observed"] >= 8
    snap = eng.snapshot()
    json.dumps(snap, default=str)  # dashboard payload must serialize


def test_engine_no_trade_until_minute_3(cfg, storage):
    eng, clock, world = _sim_engine(cfg, storage)
    _drive(eng, clock, world, 10 + 170)  # market open + 170s
    assert eng.session and eng.session.phase == Phase.OBSERVING and eng.session.decision is None
    assert not storage.open_positions("paper")
    _drive(eng, clock, world, 15)
    assert eng.session.phase in (Phase.SKIPPED, Phase.IN_POSITION)


def test_engine_kill_switch_blocks_orders(cfg, storage):
    cfg.strategy.min_confidence = 0
    cfg.strategy.min_abs_z = 0
    cfg.strategy.min_edge = -1
    cfg.strategy.min_ev_per_dollar = -1
    cfg.strategy.max_spread = 1
    eng, clock, world = _sim_engine(cfg, storage)
    eng.risk.engage_kill("test")
    _drive(eng, clock, world, 900 * 2)
    assert not storage.settled_positions("paper") and not storage.open_positions("paper")
    assert any("kill switch" in (m["skip_reasons"] or "") for m in storage.recent_markets(10))


def test_restart_does_not_redecide(cfg, storage):
    cfg.strategy.min_confidence = 0
    cfg.strategy.min_abs_z = 0
    cfg.strategy.min_edge = -1
    cfg.strategy.min_ev_per_dollar = -1
    cfg.strategy.max_spread = 1
    cfg.strategy.require_trend_agreement = False
    cfg.strategy.max_flow_contradiction = 2
    eng, clock, world = _sim_engine(cfg, storage)
    _drive(eng, clock, world, 10 + 200)
    ticker = eng.session.market.ticker
    n_before = len(storage.open_positions("paper"))
    # new engine instance (simulated restart) on the same storage, same market
    eng2 = TradingEngine(cfg, storage, eng.md, eng.feed, eng.executor,
                         RiskManager(cfg.risk, storage, cfg.data_dir, "paper", clock=clock.now), clock)
    _drive(eng2, clock, world, 30)
    assert eng2.session.market.ticker == ticker and "decision already recorded" in " ".join(eng2.session.notes)
    assert len(storage.open_positions("paper")) == n_before


# ------------------------------------------------------------------ live gate
def test_live_gate_blocked_by_default(cfg, storage):
    g = evaluate_live_gate(cfg, storage)
    assert not g["allowed"]
    names = {c["name"] for c in g["checks"] if not c["ok"]}
    assert {"trading_mode", "confirmation", "credentials", "backtest", "paper_trades"} <= names


def test_live_gate_passes_when_everything_satisfied(cfg, storage, keypair, tmp_path):
    keyfile = tmp_path / "k.pem"
    keyfile.write_bytes(keypair[1])
    cfg.mode.trading_mode = "live"
    cfg.secrets.live_confirm = cfg.live_gate.confirm_phrase
    cfg.secrets.kalshi_key_id = "kid"
    cfg.secrets.kalshi_private_key_path = str(keyfile)
    (cfg.data_dir / "backtest_report.json").write_text(json.dumps({
        "generated_at": time.time(), "data_source": "coinbase+kalshi", "fingerprint": cfg.strategy_fingerprint(),
        "base": {"stats": {"trades": 150, "profit_factor": 1.3}, "out_of_sample": {"trades": 40, "total_pnl": 12.0}}}))
    for i in range(30):
        pid = storage.open_position(ticker=f"T{i}", mode="paper", side="yes", contracts=10, avg_price=0.5, fees=0.18,
                                    cost=5.18, status="open", opened_at=time.time())
        storage.settle_position(pid, "yes" if i % 3 else "no", 10.0 if i % 3 else 0.0, 4.82 if i % 3 else -5.18, bool(i % 3))
    g = evaluate_live_gate(cfg, storage)
    assert g["allowed"], g["failing"]
    cfg.strategy.min_confidence += 1  # changing parameters invalidates the backtest
    assert not evaluate_live_gate(cfg, storage)["allowed"]


# ------------------------------------------------------------------ backtest
def test_backtest_has_no_lookahead(cfg):
    candles = synthetic_candles(2, seed=1)
    w1 = prepare_windows(candles, cfg)
    target = w1[len(w1) // 2]["open_ts"]
    # rewrite minutes 3..15 of one window: its minute-3 features must not change, but its outcome may
    altered = [type(c)(c.ts, c.open * 1.02, c.high * 1.02, c.low * 1.02, c.close * 1.02, c.volume)
               if target + 180 <= c.ts < target + 900 else c for c in candles]
    w2 = {w["open_ts"]: w for w in prepare_windows(altered, cfg)}
    orig = next(w for w in w1 if w["open_ts"] == target)
    assert w2[target]["features"].to_dict() == orig["features"].to_dict()
    assert w2[target]["vol"] == orig["vol"]


def test_backtest_report_shape(cfg):
    r = run_backtest(synthetic_candles(5, seed=2), cfg, data_source="synthetic", sweep=False)
    assert r["windows"] > 400 and r["calibration"] and "out_of_sample" in r["base"]
    assert r["fingerprint"] == cfg.strategy_fingerprint()

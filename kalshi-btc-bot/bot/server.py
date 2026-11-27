"""Dashboard server (FastAPI). Binds to localhost by default. The frontend only ever receives
public data: no API keys, no private key, no live-enable capability."""
from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import secrets as pysecrets
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .app import Runtime, build_runtime
from .config import Config
from .live_gate import load_backtest_report

log = logging.getLogger("server")
DASHBOARD_DIR = Path(__file__).resolve().parent.parent / "dashboard"


def create_app(cfg: Config, runtime: Runtime | None = None) -> FastAPI:
    rt_holder: dict = {}

    @contextlib.asynccontextmanager
    async def lifespan(app: FastAPI):
        rt = runtime or build_runtime(cfg)
        rt_holder["rt"] = rt
        tasks = [asyncio.create_task(rt.feed.run(), name="feed"),
                 asyncio.create_task(rt.engine.run(), name="engine")]
        try:
            yield
        finally:
            rt.engine.stop()
            rt.feed.stop()
            for t in tasks:
                t.cancel()
            for t in tasks:
                with contextlib.suppress(asyncio.CancelledError, Exception):
                    await t
            if rt.client:
                await rt.client.close()
            rt.storage.close()

    app = FastAPI(title="Kalshi BTC 15m Momentum Bot", lifespan=lifespan)

    def rt() -> Runtime:
        return rt_holder["rt"]

    def require_control(request: Request, token: str | None):
        expected = cfg.secrets.dashboard_token
        if expected:
            if not token or not pysecrets.compare_digest(token, expected):
                raise HTTPException(401, "invalid dashboard token")
            return
        host = request.client.host if request.client else ""
        if host not in ("127.0.0.1", "::1", "localhost", "testclient"):
            raise HTTPException(403, "control endpoints are localhost-only unless DASHBOARD_TOKEN is set")

    def state() -> dict:
        snap = rt().engine.snapshot()
        snap["config"] = cfg.public_dict()
        rep = load_backtest_report(cfg)
        if rep:
            snap["backtest"] = {"generated_at": rep.get("generated_at"), "data_source": rep.get("data_source"),
                                "windows": rep.get("windows"), "base": {k: rep["base"][k] for k in
                                ("stats", "in_sample", "out_of_sample", "by_volatility", "by_entry_price", "trade_rate")},
                                "calibration": rep.get("calibration"),
                                "fingerprint_matches": rep.get("fingerprint") == cfg.strategy_fingerprint()}
        else:
            snap["backtest"] = None
        return snap

    @app.get("/")
    async def index():
        return FileResponse(DASHBOARD_DIR / "index.html")

    app.mount("/static", StaticFiles(directory=DASHBOARD_DIR), name="static")

    @app.get("/api/state")
    async def api_state():
        return JSONResponse(json.loads(json.dumps(state(), default=str)))

    @app.get("/api/health")
    async def health():
        e = rt().engine
        return {"ok": True, "mode": e.mode, "feed": rt().feed.status, "market": e.session.market.ticker if e.session else None}

    @app.get("/api/markets")
    async def markets(limit: int = 200):
        return rt().storage.recent_markets(min(limit, 2000))

    @app.post("/api/kill")
    async def kill(request: Request, x_dashboard_token: str | None = Header(default=None)):
        # Engaging the kill switch is always allowed from localhost / with token; it only ever reduces risk.
        require_control(request, x_dashboard_token)
        rt().engine.risk.engage_kill("dashboard")
        return {"ok": True, "kill_engaged": True}

    @app.post("/api/kill/clear")
    async def kill_clear(request: Request, x_dashboard_token: str | None = Header(default=None)):
        require_control(request, x_dashboard_token)
        rt().engine.risk.clear_kill()
        return {"ok": True, "kill_engaged": False}

    @app.post("/api/risk/resume")
    async def resume(request: Request, x_dashboard_token: str | None = Header(default=None)):
        require_control(request, x_dashboard_token)
        ok = rt().engine.risk.resume()
        if not ok:
            raise HTTPException(409, "daily loss halt cannot be overridden; it clears at the next trading day")
        return {"ok": True}

    @app.websocket("/ws")
    async def ws(websocket: WebSocket):
        await websocket.accept()
        try:
            while True:
                await websocket.send_text(json.dumps(state(), default=str))
                await asyncio.sleep(1.0)
        except (WebSocketDisconnect, RuntimeError):
            return

    return app

"""CLI.

  python -m bot run [--sim] [--speed 10]       start engine + dashboard (paper by default)
  python -m bot backtest [--days 30] [--kalshi] [--synthetic] [--csv FILE]
  python -m bot check-live                     show the live-trading gate status
  python -m bot stats [--mode paper|live]      performance summary
  python -m bot kill | unkill | resume         kill switch / resume after consecutive-loss halt
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path

from .config import load_config


def setup_logging(data_dir: Path, verbose: bool = False):
    fmt = logging.Formatter("%(asctime)s %(levelname)-7s %(name)-8s %(message)s")
    root = logging.getLogger()
    root.setLevel(logging.DEBUG if verbose else logging.INFO)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    fh = RotatingFileHandler(data_dir / "bot.log", maxBytes=10_000_000, backupCount=5)
    fh.setFormatter(fmt)
    root.handlers = [sh, fh]
    for noisy in ("httpx", "httpcore", "websockets", "uvicorn.access"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def cmd_run(args, cfg):
    import uvicorn

    from .server import create_app
    if args.sim:
        cfg.mode.data_source = "sim"
        cfg.mode.trading_mode = "paper"
        cfg.data_dir = cfg.data_dir / "sim"
        cfg.data_dir.mkdir(parents=True, exist_ok=True)
    if args.speed:
        cfg.mode.sim_speed = args.speed
    if args.port:
        cfg.server.port = args.port
    setup_logging(cfg.data_dir, args.verbose)
    log = logging.getLogger("main")
    log.info("starting: trading_mode=%s data_source=%s dashboard=http://%s:%d", cfg.mode.trading_mode,
             cfg.mode.data_source, cfg.server.host, cfg.server.port)
    if cfg.server.host not in ("127.0.0.1", "localhost") and not cfg.secrets.dashboard_token:
        log.warning("dashboard is exposed on %s without DASHBOARD_TOKEN; control endpoints will be refused",
                    cfg.server.host)
    uvicorn.run(create_app(cfg), host=cfg.server.host, port=cfg.server.port, log_level="warning")


def cmd_backtest(args, cfg):
    from .backtest.data import fetch_coinbase_candles, fetch_kalshi_history, load_candles_csv, synthetic_candles
    from .backtest.engine import format_report, run_backtest
    from .live_gate import backtest_report_path
    setup_logging(cfg.data_dir, args.verbose)
    end = time.time() // 900 * 900
    start = end - args.days * 86400
    cache = cfg.data_dir / "cache"
    kalshi = None
    if args.synthetic:
        candles = synthetic_candles(args.days, seed=args.seed, drift_std_bps_per_min=args.synthetic_drift)
        source = "synthetic"
    elif args.csv:
        candles = load_candles_csv(Path(args.csv))
        source = f"csv:{Path(args.csv).name}"
    else:
        candles = asyncio.run(fetch_coinbase_candles(start - 3 * 3600, end, cache))
        source = "coinbase"
    if args.kalshi:
        from .kalshi_client import build_client

        async def _k():
            client = build_client(cfg)
            try:
                return await fetch_kalshi_history(client, cfg.kalshi.series_ticker, start, end, cache)
            finally:
                await client.close()
        kalshi = asyncio.run(_k())
        source += "+kalshi"
        print(f"loaded {len(kalshi)} Kalshi markets with minute-3 quotes")
    print(f"loaded {len(candles)} one-minute candles ({source})")
    report = run_backtest(candles, cfg, kalshi=kalshi, data_source=source, sweep=not args.no_sweep)
    out = backtest_report_path(cfg) if not args.out else Path(args.out)
    out.write_text(json.dumps(report, indent=1, default=str))
    print(format_report(report))
    print(f"\nreport saved to {out}")


def cmd_check_live(args, cfg):
    from .live_gate import evaluate_live_gate
    from .storage import Storage
    g = evaluate_live_gate(cfg, Storage(cfg.data_dir / "bot.db"))
    for c in g["checks"]:
        print(f"  [{'PASS' if c['ok'] else 'FAIL'}] {c['name']:<24} {c['detail']}")
    print(f"\nLIVE TRADING {'ALLOWED' if g['allowed'] else 'BLOCKED'}")
    return 0 if g["allowed"] else 1


def cmd_stats(args, cfg):
    from .storage import Storage
    p = Storage(cfg.data_dir / "bot.db").performance(args.mode, cfg.risk.timezone_offset_hours)
    p.pop("equity_curve", None)
    print(json.dumps(p, indent=2))


def cmd_kill(args, cfg, engage: bool):
    from .risk import RiskManager
    from .storage import Storage
    for mode in ("paper", "live"):
        rm = RiskManager(cfg.risk, Storage(cfg.data_dir / "bot.db"), cfg.data_dir, mode)
        rm.engage_kill("cli") if engage else rm.clear_kill()
    print("kill switch ENGAGED (a running bot stops placing orders within ~1s)" if engage else "kill switch cleared")


def cmd_resume(args, cfg):
    from .risk import RiskManager
    from .storage import Storage
    rm = RiskManager(cfg.risk, Storage(cfg.data_dir / "bot.db"), cfg.data_dir, args.mode)
    print("resumed" if rm.resume() else "daily-loss halt cannot be overridden (clears next trading day)")
    print("note: restart a running bot (or use the dashboard) for it to pick up the change")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="bot", description="Kalshi BTC 15-minute momentum bot")
    ap.add_argument("--config", default=None)
    ap.add_argument("-v", "--verbose", action="store_true")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--sim", action="store_true", help="offline simulator (paper only)")
    r.add_argument("--speed", type=float, default=None, help="simulator speed multiplier")
    r.add_argument("--port", type=int, default=None)
    b = sub.add_parser("backtest")
    b.add_argument("--days", type=float, default=30)
    b.add_argument("--kalshi", action="store_true", help="use real Kalshi settled markets + minute-3 quotes")
    b.add_argument("--synthetic", action="store_true", help="synthetic random-walk data (sanity check only)")
    b.add_argument("--synthetic-drift", type=float, default=0.0)
    b.add_argument("--seed", type=int, default=7)
    b.add_argument("--csv", default=None, help="1-minute candles CSV: ts,open,high,low,close,volume")
    b.add_argument("--no-sweep", action="store_true")
    b.add_argument("--out", default=None)
    sub.add_parser("check-live")
    s = sub.add_parser("stats")
    s.add_argument("--mode", default="paper", choices=["paper", "live"])
    sub.add_parser("kill")
    sub.add_parser("unkill")
    rs = sub.add_parser("resume")
    rs.add_argument("--mode", default="paper", choices=["paper", "live"])
    args = ap.parse_args(argv)
    cfg = load_config(args.config)
    if args.cmd == "run":
        return cmd_run(args, cfg)
    if args.cmd == "backtest":
        return cmd_backtest(args, cfg)
    if args.cmd == "check-live":
        return cmd_check_live(args, cfg)
    if args.cmd == "stats":
        return cmd_stats(args, cfg)
    if args.cmd == "kill":
        return cmd_kill(args, cfg, True)
    if args.cmd == "unkill":
        return cmd_kill(args, cfg, False)
    if args.cmd == "resume":
        return cmd_resume(args, cfg)


if __name__ == "__main__":
    sys.exit(main() or 0)

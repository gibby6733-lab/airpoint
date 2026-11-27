"""Live-trading gate. Real-money trading is only enabled when EVERY check passes.

1. config.toml: mode.trading_mode = "live" and data_source = "live"
2. .env: KALSHI_LIVE_CONFIRM equals the configured confirmation phrase
3. Kalshi credentials present and the private key loads
4. A recent backtest report exists, was run with the *current* strategy parameters, and meets the
   minimum trade count / profit factor / out-of-sample requirements
5. A paper-trading track record with enough trades and a non-losing profit factor

The dashboard can display this status but cannot enable live trading.
"""
from __future__ import annotations

import json
import time

from .config import Config
from .storage import Storage


def backtest_report_path(cfg: Config):
    return cfg.data_dir / "backtest_report.json"


def load_backtest_report(cfg: Config) -> dict | None:
    p = backtest_report_path(cfg)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except (OSError, ValueError):
        return None


def evaluate_live_gate(cfg: Config, storage: Storage) -> dict:
    g = cfg.live_gate
    checks: list[dict] = []

    def add(name, ok, detail):
        checks.append({"name": name, "ok": bool(ok), "detail": detail})

    add("trading_mode", cfg.mode.trading_mode == "live",
        f"config trading_mode = '{cfg.mode.trading_mode}'" + ("" if cfg.mode.trading_mode == "live" else " (paper is the default)"))
    add("data_source", cfg.mode.data_source == "live", f"data_source = '{cfg.mode.data_source}'")
    add("confirmation", cfg.secrets.live_confirm == g.confirm_phrase,
        "KALSHI_LIVE_CONFIRM matches" if cfg.secrets.live_confirm == g.confirm_phrase
        else f'set KALSHI_LIVE_CONFIRM="{g.confirm_phrase}" in .env')

    cred_ok, cred_detail = False, "KALSHI_API_KEY_ID / KALSHI_PRIVATE_KEY_PATH not set"
    if cfg.secrets.has_kalshi_credentials():
        try:
            from .kalshi_client import KalshiSigner
            KalshiSigner(cfg.secrets.kalshi_key_id, cfg.secrets.load_private_key_pem())
            cred_ok, cred_detail = True, "credentials load"
        except Exception as exc:  # noqa: BLE001
            cred_detail = f"private key failed to load: {type(exc).__name__}"
    add("credentials", cred_ok, cred_detail)

    report = load_backtest_report(cfg)
    bt_summary = None
    if g.require_backtest:
        if report is None:
            add("backtest", False, "no backtest report - run: python -m bot backtest")
        else:
            base = report.get("base", {})
            stats = base.get("stats", {})
            oos = base.get("out_of_sample", {})
            bt_summary = {"generated_at": report.get("generated_at"), "source": report.get("data_source"),
                          "stats": stats, "out_of_sample": oos}
            age_days = (time.time() - report.get("generated_at", 0)) / 86400
            add("backtest_age", age_days <= g.max_backtest_age_days, f"{age_days:.1f} days old (max {g.max_backtest_age_days})")
            add("backtest_params", report.get("fingerprint") == cfg.strategy_fingerprint(),
                "report matches current strategy parameters" if report.get("fingerprint") == cfg.strategy_fingerprint()
                else "strategy parameters changed since the backtest - re-run it")
            add("backtest_real_data", report.get("data_source") != "synthetic",
                f"data source: {report.get('data_source')}")
            n = stats.get("trades", 0)
            add("backtest_trades", n >= g.min_backtest_trades, f"{n} trades (min {g.min_backtest_trades})")
            pf = stats.get("profit_factor") or 0
            add("backtest_profit_factor", pf >= g.min_backtest_profit_factor, f"{pf:.2f} (min {g.min_backtest_profit_factor})")
            if g.require_backtest_oos_positive:
                add("backtest_out_of_sample", (oos.get("total_pnl") or 0) > 0,
                    f"out-of-sample P&L {oos.get('total_pnl', 0):+.2f} over {oos.get('trades', 0)} trades")

    paper = storage.performance("paper")
    if g.require_paper_record:
        add("paper_trades", paper["trades"] >= g.min_paper_trades, f"{paper['trades']} paper trades (min {g.min_paper_trades})")
        pf = paper["profit_factor"] or 0
        add("paper_profit_factor", paper["trades"] > 0 and pf >= g.min_paper_profit_factor,
            f"{pf:.2f} (min {g.min_paper_profit_factor})")

    return {
        "allowed": all(c["ok"] for c in checks),
        "checks": checks,
        "failing": [f"{c['name']}: {c['detail']}" for c in checks if not c["ok"]],
        "backtest": bt_summary,
        "paper": {k: paper[k] for k in ("trades", "wins", "win_rate", "total_pnl", "profit_factor", "max_drawdown")},
    }

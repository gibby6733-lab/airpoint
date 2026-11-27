"""SQLite persistence: every market (traded or skipped), positions, decision log, and risk state."""
from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS markets (
    ticker TEXT PRIMARY KEY,
    event_ticker TEXT,
    mode TEXT,
    open_ts REAL, close_ts REAL,
    strike REAL, up_side TEXT,
    btc_open REAL, btc_at_decision REAL, pct_change REAL,
    direction TEXT, confidence REAL, z_score REAL, volatility REAL,
    slope REAL, accel REAL, efficiency REAL, flow_imbalance REAL,
    p_up REAL, p_win REAL,
    decision TEXT, skip_reasons TEXT,
    side TEXT, entry_ask REAL, limit_price REAL, exec_price REAL, contracts INTEGER, fees REAL, cost REAL,
    expected_ev REAL,
    outcome TEXT, up_won INTEGER, won INTEGER, pnl REAL,
    shadow_side TEXT, shadow_price REAL, shadow_pnl REAL,
    btc_close REAL,
    features_json TEXT, decision_json TEXT,
    created_at REAL, updated_at REAL
);
CREATE TABLE IF NOT EXISTS positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    mode TEXT NOT NULL,
    side TEXT, contracts INTEGER, avg_price REAL, fees REAL, cost REAL,
    order_id TEXT, client_order_id TEXT,
    status TEXT,              -- open | settled | void
    opened_at REAL, close_ts REAL, settled_at REAL,
    result TEXT, payout REAL, pnl REAL, won INTEGER,
    UNIQUE(ticker, mode)      -- at most one position per market per mode: blocks duplicate entries
);
CREATE TABLE IF NOT EXISTS decision_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts REAL, ticker TEXT, level TEXT, message TEXT, data_json TEXT
);
CREATE TABLE IF NOT EXISTS kv (key TEXT PRIMARY KEY, value TEXT);
CREATE INDEX IF NOT EXISTS idx_markets_open ON markets(open_ts);
CREATE INDEX IF NOT EXISTS idx_positions_status ON positions(status);
"""

MARKET_COLS = None


class Storage:
    def __init__(self, path: str | Path):
        self.path = str(path)
        self.db = sqlite3.connect(self.path, check_same_thread=False, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.executescript(SCHEMA)
        self._market_cols = {r["name"] for r in self.db.execute("PRAGMA table_info(markets)")}

    def close(self):
        self.db.close()

    # ------------------------------------------------------------ markets
    def upsert_market(self, ticker: str, **fields):
        fields = {k: v for k, v in fields.items() if k in self._market_cols}
        for k in ("features_json", "decision_json"):
            if k in fields and not isinstance(fields[k], (str, type(None))):
                fields[k] = json.dumps(fields[k])
        if "skip_reasons" in fields and isinstance(fields["skip_reasons"], list):
            fields["skip_reasons"] = " | ".join(fields["skip_reasons"])
        now = time.time()
        fields["updated_at"] = now
        exists = self.db.execute("SELECT 1 FROM markets WHERE ticker=?", (ticker,)).fetchone()
        if exists:
            sets = ", ".join(f"{k}=?" for k in fields)
            self.db.execute(f"UPDATE markets SET {sets} WHERE ticker=?", (*fields.values(), ticker))
        else:
            fields["created_at"] = now
            cols = ", ".join(["ticker", *fields])
            qs = ", ".join("?" for _ in range(len(fields) + 1))
            self.db.execute(f"INSERT INTO markets ({cols}) VALUES ({qs})", (ticker, *fields.values()))

    def get_market(self, ticker: str) -> dict | None:
        r = self.db.execute("SELECT * FROM markets WHERE ticker=?", (ticker,)).fetchone()
        return dict(r) if r else None

    def recent_markets(self, limit: int = 50) -> list[dict]:
        rows = self.db.execute("SELECT * FROM markets ORDER BY open_ts DESC LIMIT ?", (limit,)).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            d.pop("features_json", None)
            d.pop("decision_json", None)
            out.append(d)
        return out

    def unsettled_markets(self, before_ts: float) -> list[dict]:
        rows = self.db.execute(
            "SELECT ticker, close_ts, up_side FROM markets WHERE outcome IS NULL AND close_ts < ? AND close_ts > ?",
            (before_ts, before_ts - 86400 * 3)).fetchall()
        return [dict(r) for r in rows]

    # ------------------------------------------------------------ positions
    def has_position(self, ticker: str, mode: str) -> bool:
        return self.db.execute("SELECT 1 FROM positions WHERE ticker=? AND mode=?", (ticker, mode)).fetchone() is not None

    def open_position(self, **p) -> int:
        cols = ", ".join(p)
        qs = ", ".join("?" for _ in p)
        cur = self.db.execute(f"INSERT INTO positions ({cols}) VALUES ({qs})", tuple(p.values()))
        return cur.lastrowid

    def open_positions(self, mode: str | None = None) -> list[dict]:
        q, args = "SELECT * FROM positions WHERE status='open'", ()
        if mode:
            q += " AND mode=?"
            args = (mode,)
        return [dict(r) for r in self.db.execute(q + " ORDER BY opened_at", args)]

    def settle_position(self, pos_id: int, result: str, payout: float, pnl: float, won: bool):
        self.db.execute(
            "UPDATE positions SET status='settled', settled_at=?, result=?, payout=?, pnl=?, won=? WHERE id=?",
            (time.time(), result, payout, pnl, int(won), pos_id))

    def settled_positions(self, mode: str | None = None, limit: int = 1000) -> list[dict]:
        q, args = "SELECT * FROM positions WHERE status='settled'", []
        if mode:
            q += " AND mode=?"
            args.append(mode)
        q += " ORDER BY settled_at DESC LIMIT ?"
        args.append(limit)
        return [dict(r) for r in self.db.execute(q, args)]

    # ------------------------------------------------------------ logs
    def log(self, ticker: str | None, level: str, message: str, data: dict | None = None):
        self.db.execute("INSERT INTO decision_log (ts, ticker, level, message, data_json) VALUES (?,?,?,?,?)",
                        (time.time(), ticker, level, message, json.dumps(data, default=str) if data else None))

    def recent_logs(self, limit: int = 40) -> list[dict]:
        rows = self.db.execute("SELECT ts, ticker, level, message FROM decision_log ORDER BY id DESC LIMIT ?", (limit,))
        return [dict(r) for r in rows]

    # ------------------------------------------------------------ kv
    def get_kv(self, key: str, default=None):
        r = self.db.execute("SELECT value FROM kv WHERE key=?", (key,)).fetchone()
        return json.loads(r["value"]) if r else default

    def set_kv(self, key: str, value):
        self.db.execute("INSERT INTO kv (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                        (key, json.dumps(value)))

    # ------------------------------------------------------------ analytics
    def performance(self, mode: str, tz_offset_hours: float = 0) -> dict:
        rows = self.settled_positions(mode, limit=100000)
        wins = [r for r in rows if r["won"]]
        losses = [r for r in rows if not r["won"]]
        gross_win = sum(r["pnl"] for r in wins)
        gross_loss = -sum(r["pnl"] for r in losses)
        by_day: dict[str, dict] = {}
        for r in rows:
            day = time.strftime("%Y-%m-%d", time.gmtime(r["settled_at"] + tz_offset_hours * 3600))
            d = by_day.setdefault(day, {"date": day, "trades": 0, "wins": 0, "pnl": 0.0, "fees": 0.0})
            d["trades"] += 1
            d["wins"] += int(bool(r["won"]))
            d["pnl"] = round(d["pnl"] + r["pnl"], 4)
            d["fees"] = round(d["fees"] + (r["fees"] or 0), 4)
        # equity curve (chronological)
        equity, curve, peak, max_dd = 0.0, [], 0.0, 0.0
        for r in sorted(rows, key=lambda r: r["settled_at"]):
            equity += r["pnl"]
            peak = max(peak, equity)
            max_dd = max(max_dd, peak - equity)
            curve.append([r["settled_at"], round(equity, 4)])
        mk = self.db.execute(
            "SELECT COUNT(*) n, SUM(decision='SKIP') skipped, SUM(decision LIKE 'BUY%') bought FROM markets WHERE mode=?",
            (mode,)).fetchone()
        skip_rows = self.db.execute(
            "SELECT skip_reasons FROM markets WHERE mode=? AND decision='SKIP' AND skip_reasons IS NOT NULL", (mode,))
        reason_counts: dict[str, int] = {}
        for r in skip_rows:
            for reason in (r["skip_reasons"] or "").split(" | "):
                key = reason.split(":")[0].strip()
                if key:
                    reason_counts[key] = reason_counts.get(key, 0) + 1
        shadow = self.db.execute(
            "SELECT COUNT(*) n, SUM(shadow_pnl) pnl, SUM(shadow_pnl>0) wins FROM markets "
            "WHERE mode=? AND decision='SKIP' AND shadow_pnl IS NOT NULL", (mode,)).fetchone()
        n = len(rows)
        return {
            "trades": n,
            "wins": len(wins),
            "losses": len(losses),
            "win_rate": round(len(wins) / n, 4) if n else None,
            "total_pnl": round(sum(r["pnl"] for r in rows), 4),
            "fees_paid": round(sum((r["fees"] or 0) for r in rows), 4),
            "avg_pnl": round(sum(r["pnl"] for r in rows) / n, 4) if n else None,
            # no losses yet -> report gross win as a large finite number (JSON has no Infinity)
            "profit_factor": round(gross_win / gross_loss, 3) if gross_loss > 0 else (None if not wins else 99.0),
            "max_drawdown": round(max_dd, 4),
            "by_day": sorted(by_day.values(), key=lambda d: d["date"], reverse=True)[:30],
            "equity_curve": curve[-500:],
            "markets_observed": mk["n"] or 0,
            "markets_skipped": mk["skipped"] or 0,
            "markets_traded": mk["bought"] or 0,
            "skip_reasons": dict(sorted(reason_counts.items(), key=lambda kv: -kv[1])),
            "shadow_skipped": {"n": shadow["n"] or 0, "pnl_per_contract_sum": round(shadow["pnl"] or 0, 4),
                               "wins": shadow["wins"] or 0},
        }

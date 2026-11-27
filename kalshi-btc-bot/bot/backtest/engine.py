"""Backtester: replays every 15-minute window through the SAME signal/strategy code used live.

Per window: observe minutes 0-3 -> features -> signal -> probability -> entry checks against
(a) real Kalshi minute-3 quotes when available, else (b) a market model quoting the random-walk fair
value plus spread/noise. Fees and slippage are included. Risk limits (daily loss, trades/day,
consecutive losses) are applied.

Limitations (reported in the output): 1-minute candles are coarser than live ticks and have no
buy/sell aggressor split, so the order-flow component is absent in backtests.
"""
from __future__ import annotations

import copy
import itertools
import math
import random
import time
from dataclasses import asdict, replace

from ..config import Config
from ..fees import kalshi_fee
from ..models import BookLevel, OrderBook, Tick
from ..signals import compute_features, estimate_p_up, random_walk_p_up, score_momentum, vol_from_minute_closes
from ..strategy import evaluate_entry
from .data import Candle

WINDOW = 900


def _candle_path(c: Candle) -> list[Tick]:
    """Approximate intra-minute path: O -> L -> H -> C for up candles, O -> H -> L -> C for down."""
    first, second = (c.low, c.high) if c.close >= c.open else (c.high, c.low)
    return [Tick(c.ts + 1, c.open), Tick(c.ts + 20, first), Tick(c.ts + 40, second), Tick(c.ts + 59, c.close)]


def prepare_windows(candles: list[Candle], cfg: Config, kalshi: dict | None = None, seed: int = 11) -> list[dict]:
    st, bt = cfg.strategy, cfg.backtest
    obs_min = st.observation_seconds // 60
    by_ts = {int(c.ts): c for c in candles}
    idx_of = {int(c.ts): i for i, c in enumerate(candles)}
    rng = random.Random(seed)
    windows = []
    if not candles:
        return windows
    t = math.ceil(candles[0].ts / WINDOW) * WINDOW
    end = candles[-1].ts
    while t + WINDOW <= end + 60:
        mins = [by_ts.get(int(t + 60 * k)) for k in range(WINDOW // 60)]
        i0 = idx_of.get(int(t))
        if any(m is None for m in mins) or i0 is None or i0 < st.vol_lookback_minutes:
            t += WINDOW
            continue
        hist = candles[i0 - st.vol_lookback_minutes:i0]
        vol = vol_from_minute_closes([c.close for c in hist] + [mins[0].open])
        if vol is None:
            t += WINDOW
            continue
        ticks = [Tick(t, mins[0].open)]
        for c in mins[:obs_min]:
            ticks.extend(_candle_path(c))
        decision_ts = t + st.observation_seconds
        f = compute_features(ticks, t, decision_ts, None, vol, open_price=mins[0].open)
        close_price = mins[-1].close
        k = kalshi.get(float(t)) if kalshi else None
        if kalshi is not None and k is None:
            t += WINDOW
            continue
        rem = WINDOW - st.observation_seconds
        rw = random_walk_p_up(f.dist_bps, vol, rem) if f else 0.5
        if k:
            yes_ask, yes_bid, up_side = k["yes_ask"], k["yes_bid"], k.get("up_side", "yes")
            up_won = (k["result"] == up_side)
            quote_src = "kalshi"
        else:
            noise = rng.gauss(0, bt.quote_noise)
            yes_ask = min(0.99, max(0.01, math.ceil((rw + bt.half_spread + noise) * 100 - 1e-9) / 100))
            yes_bid = min(yes_ask - 0.01, max(0.01, math.floor((rw - bt.half_spread + noise) * 100 + 1e-9) / 100))
            up_side, up_won, quote_src = "yes", close_price >= mins[0].open, "model"
        windows.append({
            "open_ts": t, "features": f, "vol": vol, "rw_p_up": rw, "up_side": up_side, "up_won": bool(up_won),
            "yes_ask": yes_ask, "yes_bid": yes_bid, "quote_src": quote_src,
            "seconds_remaining": rem, "open": mins[0].open, "close": close_price,
        })
        t += WINDOW
    return windows


def _book(w: dict, depth: int) -> OrderBook:
    yb, ya = w["yes_bid"], w["yes_ask"]
    yes = [BookLevel(round(yb, 4), depth)] if yb and yb > 0 else []
    no = [BookLevel(round(1 - ya, 4), depth)] if ya and ya < 1 else []
    return OrderBook(yes, no)


def simulate(windows: list[dict], cfg: Config) -> list[dict]:
    st, ex, rk, bt = cfg.strategy, cfg.execution, cfg.risk, cfg.backtest
    st = replace(st, min_ticks=0)  # tick count is a live-feed health check; candles have fixed resolution
    trades = []
    day, day_pnl, day_trades, consec, halted_day = None, 0.0, 0, 0, None
    fee_rate = ex.taker_fee_rate if ex.order_style == "ioc" else ex.maker_fee_rate
    for w in windows:
        f = w["features"]
        if f is None:
            continue
        d_key = time.strftime("%Y-%m-%d", time.gmtime(w["open_ts"] + rk.timezone_offset_hours * 3600))
        if d_key != day:
            day, day_pnl, day_trades = d_key, 0.0, 0
            if halted_day is not None:
                consec, halted_day = 0, None  # backtest approximation of a manual next-day resume
        if halted_day == day:
            continue
        sig = score_momentum(f, st)
        p_up = estimate_p_up(f, w["seconds_remaining"], st)
        d = evaluate_entry(f, sig, p_up, _book(w, bt.depth), w["up_side"], w["seconds_remaining"], st, ex, rk)
        if not d.is_buy:
            continue
        if day_trades >= rk.max_trades_per_day:
            continue
        price = min(0.99, d.expected_avg_price + bt.slippage)
        fee = kalshi_fee(d.contracts, price, fee_rate)
        cost = d.contracts * price + fee
        if -day_pnl + cost > rk.max_daily_loss + 1e-9:
            continue
        won = (d.side == w["up_side"]) == w["up_won"]
        pnl = (d.contracts - cost) if won else -cost
        day_pnl += pnl
        day_trades += 1
        consec = 0 if won else consec + 1
        if consec >= rk.max_consecutive_losses or -day_pnl >= rk.max_daily_loss:
            halted_day = day
        trades.append({
            "open_ts": w["open_ts"], "direction": d.direction.value, "side": d.side, "contracts": d.contracts,
            "price": round(price, 4), "fee": fee, "cost": round(cost, 4), "won": won, "pnl": round(pnl, 4),
            "p_win": round(d.p_win, 4), "confidence": round(d.confidence, 1), "vol": round(w["vol"], 3),
            "z": round(f.z_score, 3), "ask": d.best_ask, "quote_src": w["quote_src"],
        })
    return trades


def stats(trades: list[dict]) -> dict:
    n = len(trades)
    if n == 0:
        return {"trades": 0, "wins": 0, "win_rate": None, "total_pnl": 0.0, "avg_pnl": None, "profit_factor": None,
                "max_drawdown": 0.0, "fees": 0.0, "avg_price": None, "avg_p_win": None, "sharpe_per_trade": None}
    wins = [t for t in trades if t["won"]]
    gw = sum(t["pnl"] for t in wins)
    gl = -sum(t["pnl"] for t in trades if not t["won"])
    eq = peak = dd = 0.0
    for t in trades:
        eq += t["pnl"]
        peak = max(peak, eq)
        dd = max(dd, peak - eq)
    pnls = [t["pnl"] for t in trades]
    mean = sum(pnls) / n
    sd = math.sqrt(sum((p - mean) ** 2 for p in pnls) / (n - 1)) if n > 1 else 0.0
    return {
        "trades": n, "wins": len(wins), "win_rate": round(len(wins) / n, 4),
        "total_pnl": round(sum(pnls), 2), "avg_pnl": round(mean, 4),
        "profit_factor": round(gw / gl, 3) if gl > 0 else (99.0 if gw > 0 else None),
        "max_drawdown": round(dd, 2), "fees": round(sum(t["fee"] for t in trades), 2),
        "avg_price": round(sum(t["price"] for t in trades) / n, 4),
        "avg_p_win": round(sum(t["p_win"] for t in trades) / n, 4),
        "sharpe_per_trade": round(mean / sd, 4) if sd > 0 else None,
    }


def _bucket(trades, key, edges, labels):
    out = {}
    for t in trades:
        v = t[key]
        for (lo, hi), lab in zip(zip(edges, edges[1:]), labels):
            if lo <= v < hi:
                out.setdefault(lab, []).append(t)
                break
    return {lab: stats(out.get(lab, [])) for lab in labels}


def calibration(windows: list[dict], cfg: Config) -> list[dict]:
    """Does momentum persist? Compare the empirical continuation rate with the random-walk prediction."""
    edges = [0, 0.5, 1.0, 1.5, 2.0, 3.0, 99]
    rows = []
    for lo, hi in zip(edges, edges[1:]):
        sel = [w for w in windows if w["features"] and lo <= abs(w["features"].z_score) < hi]
        if not sel:
            continue
        cont = [(w["features"].dist_bps > 0) == w["up_won"] for w in sel]
        rw = [w["rw_p_up"] if w["features"].dist_bps > 0 else 1 - w["rw_p_up"] for w in sel]
        model = [estimate_p_up(w["features"], w["seconds_remaining"], cfg.strategy) for w in sel]
        model = [m if w["features"].dist_bps > 0 else 1 - m for m, w in zip(model, sel)]
        emp = sum(cont) / len(sel)
        se = math.sqrt(emp * (1 - emp) / len(sel)) if len(sel) > 1 else 0
        rows.append({"abs_z": f"{lo}-{hi if hi < 99 else '+'}", "n": len(sel),
                     "empirical_continue": round(emp, 4), "std_err": round(se, 4),
                     "random_walk_pred": round(sum(rw) / len(rw), 4),
                     "model_pred": round(sum(model) / len(model), 4)})
    return rows


SWEEP_GRID = {
    "min_confidence": [45.0, 55.0, 65.0, 75.0],
    "min_edge": [0.02, 0.04, 0.06],
    "max_contract_price": [0.65, 0.75, 0.85],
    "momentum_persistence": [0.0, 0.1, 0.25],
}


def _with_strategy(cfg: Config, **kw) -> Config:
    c = copy.copy(cfg)
    c.strategy = replace(cfg.strategy, **kw)
    return c


def run_backtest(candles: list[Candle], cfg: Config, kalshi: dict | None = None, data_source: str = "coinbase",
                 sweep: bool = True) -> dict:
    windows = prepare_windows(candles, cfg, kalshi)
    split = int(len(windows) * cfg.backtest.in_sample_fraction)
    w_is, w_oos = windows[:split], windows[split:]
    trades = simulate(windows, cfg)
    t_is = [t for t in trades if w_is and t["open_ts"] <= w_is[-1]["open_ts"]]
    t_oos = [t for t in trades if w_oos and t["open_ts"] >= w_oos[0]["open_ts"]]
    vols = sorted(w["vol"] for w in windows)
    if vols:
        v1, v2 = vols[len(vols) // 3], vols[2 * len(vols) // 3]
    else:
        v1 = v2 = 0
    report = {
        "generated_at": time.time(),
        "data_source": data_source,
        "period": {"start": windows[0]["open_ts"] if windows else None, "end": windows[-1]["open_ts"] if windows else None},
        "windows": len(windows),
        "fingerprint": cfg.strategy_fingerprint(),
        "params": {"strategy": asdict(cfg.strategy), "execution": asdict(cfg.execution), "risk": asdict(cfg.risk),
                   "backtest": asdict(cfg.backtest)},
        "base": {
            "stats": stats(trades),
            "in_sample": stats(t_is),
            "out_of_sample": stats(t_oos),
            "by_volatility": _bucket(trades, "vol", [0, v1, v2, 1e9], [f"low (<{v1:.1f})", f"mid", f"high (>{v2:.1f})"]),
            "by_entry_price": _bucket(trades, "price", [0, 0.35, 0.5, 0.65, 1.01], ["<0.35", "0.35-0.50", "0.50-0.65", ">=0.65"]),
            "by_confidence": _bucket(trades, "confidence", [0, 60, 70, 80, 101], ["<60", "60-70", "70-80", "80+"]),
            "trade_rate": round(len(trades) / len(windows), 4) if windows else 0,
            "recent_trades": trades[-25:],
        },
        "calibration": calibration(windows, cfg),
        "assumptions": {
            "quotes": "real Kalshi minute-3 quotes" if kalshi else
                      f"model: random-walk fair value +/- {cfg.backtest.half_spread} spread, noise sd {cfg.backtest.quote_noise}",
            "slippage_per_contract": cfg.backtest.slippage,
            "fees": f"taker {cfg.execution.taker_fee_rate} * C * P * (1-P), rounded up to the cent",
            "resolution": "1-minute candles (intra-minute path approximated); no order-flow data",
            "outcome": "Kalshi result" if kalshi else "Coinbase close at minute 15 >= Coinbase open (proxy for BRTI)",
        },
    }
    if sweep and windows:
        rows = []
        keys = list(SWEEP_GRID)
        for combo in itertools.product(*SWEEP_GRID.values()):
            params = dict(zip(keys, combo))
            if params["max_contract_price"] <= cfg.strategy.min_contract_price:
                continue
            c = _with_strategy(cfg, **params)
            s_is, s_oos = stats(simulate(w_is, c)), stats(simulate(w_oos, c))
            rows.append({"params": params, "in_sample": s_is, "out_of_sample": s_oos})
        eligible = [r for r in rows if r["in_sample"]["trades"] >= 20]
        eligible.sort(key=lambda r: r["in_sample"]["total_pnl"], reverse=True)
        report["sweep"] = {
            "grid": SWEEP_GRID,
            "combos": len(rows),
            "top_in_sample": eligible[:10],
            "note": "Parameters are chosen on the in-sample period only; judge them by their out-of-sample results. "
                    "Picking the best of many combos overstates expected performance.",
        }
    return report


def format_report(r: dict) -> str:
    lines = []
    b = r["base"]
    s = b["stats"]

    def fmt(st):
        if not st["trades"]:
            return "no trades"
        return (f"{st['trades']:>4} trades  win {st['win_rate']*100:5.1f}%  P&L {st['total_pnl']:+9.2f}  "
                f"PF {st['profit_factor'] or 0:5.2f}  maxDD {st['max_drawdown']:7.2f}  avg px {st['avg_price']:.2f}")

    lines.append(f"Backtest  source={r['data_source']}  windows={r['windows']}  trade rate={b['trade_rate']*100:.1f}%")
    lines.append(f"  all            {fmt(s)}")
    lines.append(f"  in-sample      {fmt(b['in_sample'])}")
    lines.append(f"  out-of-sample  {fmt(b['out_of_sample'])}")
    lines.append("  by volatility:")
    for k, v in b["by_volatility"].items():
        lines.append(f"    {k:<14} {fmt(v)}")
    lines.append("  by entry price:")
    for k, v in b["by_entry_price"].items():
        lines.append(f"    {k:<14} {fmt(v)}")
    lines.append("  Momentum calibration (does a minute-3 move persist beyond a random walk?)")
    lines.append("    |z|       n     empirical   +/-se   random-walk   model")
    for c in r["calibration"]:
        lines.append(f"    {c['abs_z']:<8}{c['n']:>5}    {c['empirical_continue']:.3f}    {c['std_err']:.3f}     "
                     f"{c['random_walk_pred']:.3f}       {c['model_pred']:.3f}")
    if r.get("sweep"):
        lines.append(f"  Parameter sweep ({r['sweep']['combos']} combos) - top 5 by in-sample P&L, with out-of-sample:")
        for row in r["sweep"]["top_in_sample"][:5]:
            p = row["params"]
            lines.append(f"    conf>={p['min_confidence']:.0f} edge>={p['min_edge']:.2f} maxpx={p['max_contract_price']:.2f} "
                         f"persist={p['momentum_persistence']:.2f} | IS {row['in_sample']['total_pnl']:+8.2f} "
                         f"({row['in_sample']['trades']}) | OOS {row['out_of_sample']['total_pnl']:+8.2f} "
                         f"({row['out_of_sample']['trades']})")
    return "\n".join(lines)

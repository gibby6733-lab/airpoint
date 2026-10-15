"""Paper-trade a registered strategy through the full live stack.

    python -m propbot.live --strategy ema_trend --params '{"fast":9}' --qty 2 --synthetic 20
    python -m propbot.live --strategy orb --qty 2 --csv data/MNQ_1min.csv --state paper.json

Bars are replayed by ``PaperBroker`` (fills identical to ``propbot.backtest``), every order
goes through the ``RiskGuardian``, and the evaluation account (Lucid 25K EOD rules by
default) is updated after each session. One status line is printed per day.
"""
from __future__ import annotations

import argparse
import json
import logging
import math
import os
import sys
from datetime import datetime, timezone

from ..interfaces import CONTRACTS, EvalRules
from ..strategies import REGISTRY, make
from .broker import PaperBroker
from .engine import LiveEngine
from .events import EventLog
from .guardian import GuardianConfig, RiskGuardian


def _opt_float(s: str):
    return None if s.lower() in ("none", "off", "") else float(s)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="python -m propbot.live",
                                description="Paper-trade a strategy through RiskGuardian + PaperBroker.")
    p.add_argument("--strategy", required=True, choices=sorted(REGISTRY))
    p.add_argument("--params", default="{}", help="JSON dict of strategy params")
    p.add_argument("--qty", type=int, default=1, help="contracts per entry")
    p.add_argument("--contract", default="MNQ", choices=sorted(CONTRACTS))
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--synthetic", type=int, metavar="DAYS", help="replay N synthetic MNQ days")
    src.add_argument("--csv", help="replay a bar CSV (propbot.data.load_csv formats), RTH only")
    p.add_argument("--seed", type=int, default=0, help="synthetic data seed")
    p.add_argument("--slippage", type=float, default=1.0, help="slippage ticks per market/stop fill")
    p.add_argument("--daily-stop", type=_opt_float, default=300.0,
                   help="bot daily stop $ (default 300; 'none' = account limits only)")
    p.add_argument("--profit-cap", type=_opt_float, default=None, help="explicit daily profit cap $")
    p.add_argument("--no-consistency-cap", action="store_true",
                   help="do not stop for the day at the consistency-safe profit cap")
    p.add_argument("--cap-fraction", type=float, default=1.0,
                   help="use this fraction of the consistency-safe cap")
    p.add_argument("--buffer", type=float, default=50.0, help="safety buffer $ vs floor / DLL")
    p.add_argument("--reduce", action="store_true",
                   help="shrink oversize / over-risk entries instead of rejecting them")
    p.add_argument("--max-trades", type=int, default=None, help="max entries per day")
    p.add_argument("--state", default=None,
                   help="account state JSON (persisted; default: fresh in-memory account)")
    p.add_argument("--log", default=None,
                   help="JSONL decision log (default logs/paper-<utc>.jsonl)")
    p.add_argument("--kill-switch", default="STOP", help="kill-switch file path")
    p.add_argument("--keep-going", action="store_true",
                   help="keep replaying after the account passed/failed (guardian stays halted)")
    p.add_argument("-v", "--verbose", action="store_true", help="echo guardian decisions")
    return p


def _fmt(x) -> str:
    return "inf" if isinstance(x, float) and math.isinf(x) else f"{x:,.2f}"


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(level=logging.INFO if args.verbose else logging.ERROR,
                        format="%(levelname)s %(message)s", stream=sys.stderr)
    params = json.loads(args.params)
    if not isinstance(params, dict):
        raise SystemExit("--params must be a JSON object")
    contract = CONTRACTS[args.contract]
    rules = EvalRules()

    if args.synthetic:
        from ..synthetic import generate_mnq
        bars = generate_mnq(args.synthetic, seed=args.seed)
        src = f"synthetic MNQ x {args.synthetic} days (seed {args.seed})"
    else:
        from ..data import load_csv, rth
        bars = rth(load_csv(args.csv))
        src = args.csv

    log_path = args.log or os.path.join(
        "logs", f"paper-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.jsonl")
    log = EventLog(log_path)
    cfg = GuardianConfig(
        rules=rules, safety_buffer=args.buffer, bot_daily_stop=args.daily_stop,
        daily_profit_cap=args.profit_cap, use_consistency_cap=not args.no_consistency_cap,
        consistency_cap_fraction=args.cap_fraction,
        size_policy="reduce" if args.reduce else "reject", max_trades_per_day=args.max_trades,
        kill_switch_path=args.kill_switch, state_path=args.state)
    guardian = RiskGuardian(contract, cfg, log=log)
    strategy = make(args.strategy, **params)
    broker = PaperBroker(bars, contract, slippage_ticks=args.slippage,
                         start_balance=guardian.account.balance)

    print(f"paper: {strategy!r} qty={args.qty} {contract.symbol} on {src}")
    print(f"log: {log_path}" + (f"   state: {args.state}" if args.state else ""))
    hdr = (f"{'date':<10} {'pnl':>9} {'trd':>3} {'balance':>10} {'floor':>10} {'room':>8} "
           f"{'best':>8} {'need':>8} {'days':>4} {'status':<7} note")
    print(hdr)
    print("-" * len(hdr))

    class _Stop(Exception):
        pass

    def on_day(dr, st):
        need = max(0.0, st["effective_target"] - st["profit"])
        note = []
        if st["lock_reason"]:
            note.append(f"locked:{st['lock_reason']}")
        if st["halted"]:
            note.append(f"HALT:{st['halt_reason']}")
        print(f"{dr.date.strftime('%Y-%m-%d'):<10} {dr.pnl:>9.2f} {len(dr.trades):>3} "
              f"{st['balance']:>10,.2f} {st['floor']:>10,.2f} {st['room_to_floor']:>8.2f} "
              f"{st['best_day']:>8.2f} {need:>8.2f} {st['days_traded']:>4} {st['status']:<7} "
              + " ".join(note))
        if st["halted"] and not args.keep_going:
            raise _Stop

    engine = LiveEngine(strategy, broker, guardian, contract, args.qty, log=log, on_day_end=on_day)
    engine.start()
    try:
        broker.run()
        engine.finish()
    except _Stop:
        pass
    finally:
        log.close()

    acc = guardian.account
    n_rej = len(log.find("entry_rejected"))
    n_red = len(log.find("entry_reduced"))
    print("-" * len(hdr))
    print(f"account: {acc.status}" + (f" ({acc.reason})" if acc.reason else "")
          + f"  balance {acc.balance:,.2f}  profit {acc.profit:,.2f}  floor {acc.floor:,.2f}"
          + f"  best day {acc.best_day:,.2f}  days traded {acc.days_traded}/{acc.days_used}")
    print(f"guardian: {n_rej} entries rejected, {n_red} reduced, "
          f"{len(log.find('lock_day'))} day locks, halted={guardian.state.halted}"
          + (f" ({guardian.state.halt_reason})" if guardian.state.halt_reason else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

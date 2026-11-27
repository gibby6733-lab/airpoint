"""Risk manager: hard limits that sit in front of every order.

Rules enforced here:
- fixed dollar size per trade (config only; never scaled by recent results - no martingale, no "recovery" sizing)
- max daily loss (counts worst-case loss of open positions AND the new trade, so the limit can't be breached)
- max trades per day, max open positions
- max consecutive losses -> halt until manually resumed
- kill switch (dashboard, CLI, or creating the file data/KILL) -> no new orders until manually cleared
"""
from __future__ import annotations

import logging
import time
from pathlib import Path

from .config import RiskConfig
from .storage import Storage

log = logging.getLogger("risk")


class RiskManager:
    def __init__(self, cfg: RiskConfig, storage: Storage, data_dir: Path, mode: str, clock=time.time):
        self.cfg = cfg
        self.storage = storage
        self.mode = mode
        self.clock = clock
        self.kill_file = Path(data_dir) / "KILL"
        st = storage.get_kv(f"risk_state:{mode}", {}) or {}
        self.day = st.get("day")
        self.realized_today = st.get("realized_today", 0.0)
        self.trades_today = st.get("trades_today", 0)
        self.consecutive_losses = st.get("consecutive_losses", 0)
        self.halted_reason = st.get("halted_reason")
        self.kill_engaged = st.get("kill_engaged", False)
        self.kill_reason = st.get("kill_reason")
        self.roll_day()

    # ------------------------------------------------------------ state
    def _today(self) -> str:
        return time.strftime("%Y-%m-%d", time.gmtime(self.clock() + self.cfg.timezone_offset_hours * 3600))

    def _save(self):
        self.storage.set_kv(f"risk_state:{self.mode}", {
            "day": self.day, "realized_today": self.realized_today, "trades_today": self.trades_today,
            "consecutive_losses": self.consecutive_losses, "halted_reason": self.halted_reason,
            "kill_engaged": self.kill_engaged, "kill_reason": self.kill_reason,
        })

    def roll_day(self):
        today = self._today()
        if self.day != today:
            if self.day is not None:
                log.info("new trading day %s: resetting daily counters", today)
            self.day = today
            self.realized_today = 0.0
            self.trades_today = 0
            if self.halted_reason and self.halted_reason.startswith("daily"):
                self.halted_reason = None
            self._save()

    def tick(self):
        self.roll_day()
        if self.kill_file.exists() and not self.kill_engaged:
            self.engage_kill("kill file present")

    # ------------------------------------------------------------ controls
    def engage_kill(self, reason: str = "manual"):
        self.kill_engaged = True
        self.kill_reason = reason
        self.kill_file.touch(exist_ok=True)
        log.critical("KILL SWITCH ENGAGED: %s", reason)
        self.storage.log(None, "CRITICAL", f"Kill switch engaged: {reason}")
        self._save()

    def clear_kill(self):
        self.kill_engaged = False
        self.kill_reason = None
        if self.kill_file.exists():
            self.kill_file.unlink()
        self.storage.log(None, "WARNING", "Kill switch cleared")
        self._save()

    def resume(self):
        """Manual resume after a consecutive-loss halt. Daily-loss halts cannot be overridden."""
        if self.halted_reason and self.halted_reason.startswith("daily"):
            return False
        self.halted_reason = None
        self.consecutive_losses = 0
        self.storage.log(None, "WARNING", "Trading resumed manually; consecutive loss counter reset")
        self._save()
        return True

    # ------------------------------------------------------------ checks
    def trade_dollars(self) -> float:
        """Always the configured fixed amount. Intentionally independent of P&L history."""
        return self.cfg.dollars_per_trade

    def open_exposure(self) -> float:
        return sum((p["cost"] or 0) for p in self.storage.open_positions(self.mode))

    def check_can_open(self, max_loss_of_trade: float) -> tuple[bool, list[str]]:
        self.tick()
        reasons = []
        if self.kill_engaged:
            reasons.append(f"kill switch engaged ({self.kill_reason})")
        if self.halted_reason:
            reasons.append(f"trading halted: {self.halted_reason}")
        open_pos = self.storage.open_positions(self.mode)
        if len(open_pos) >= self.cfg.max_open_positions:
            reasons.append(f"max open positions reached ({len(open_pos)})")
        if self.trades_today >= self.cfg.max_trades_per_day:
            reasons.append(f"max trades per day reached ({self.trades_today})")
        worst_case = -self.realized_today + self.open_exposure() + max_loss_of_trade
        if worst_case > self.cfg.max_daily_loss + 1e-9:
            reasons.append(
                f"daily loss limit: realized {self.realized_today:+.2f}, open risk {self.open_exposure():.2f}, "
                f"new trade risk {max_loss_of_trade:.2f} would exceed ${self.cfg.max_daily_loss:.2f}")
        if self.consecutive_losses >= self.cfg.max_consecutive_losses:
            reasons.append(f"max consecutive losses reached ({self.consecutive_losses})")
        return (not reasons), reasons

    def record_open(self):
        self.trades_today += 1
        self._save()

    def record_settle(self, pnl: float):
        self.roll_day()
        self.realized_today = round(self.realized_today + pnl, 4)
        if pnl < 0:
            self.consecutive_losses += 1
        elif pnl > 0:
            self.consecutive_losses = 0
        if -self.realized_today >= self.cfg.max_daily_loss - 1e-9:
            self.halted_reason = f"daily loss limit hit ({self.realized_today:+.2f})"
            self.storage.log(None, "CRITICAL", self.halted_reason)
        elif self.consecutive_losses >= self.cfg.max_consecutive_losses:
            self.halted_reason = f"consecutive losses ({self.consecutive_losses}) - resume manually"
            self.storage.log(None, "CRITICAL", self.halted_reason)
        self._save()

    def snapshot(self) -> dict:
        ok, reasons = self.check_can_open(0.0)
        return {
            "can_trade": ok,
            "blocking": reasons,
            "day": self.day,
            "realized_today": round(self.realized_today, 4),
            "trades_today": self.trades_today,
            "consecutive_losses": self.consecutive_losses,
            "open_exposure": round(self.open_exposure(), 4),
            "halted_reason": self.halted_reason,
            "kill_engaged": self.kill_engaged,
            "kill_reason": self.kill_reason,
            "limits": {
                "dollars_per_trade": self.cfg.dollars_per_trade,
                "max_daily_loss": self.cfg.max_daily_loss,
                "max_trades_per_day": self.cfg.max_trades_per_day,
                "max_consecutive_losses": self.cfg.max_consecutive_losses,
                "max_open_positions": self.cfg.max_open_positions,
            },
        }

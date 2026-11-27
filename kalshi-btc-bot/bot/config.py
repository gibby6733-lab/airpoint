"""Configuration loading: non-secret settings from config.toml, secrets from env / .env."""
from __future__ import annotations

import hashlib
import json
import os
import tomllib
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"

KALSHI_URLS = {
    "prod": "https://api.elections.kalshi.com",
    "demo": "https://demo-api.kalshi.co",
}
API_PREFIX = "/trade-api/v2"


@dataclass
class ModeConfig:
    trading_mode: str = "paper"
    data_source: str = "live"
    sim_speed: float = 1.0


@dataclass
class KalshiConfig:
    environment: str = "prod"
    series_ticker: str = "KXBTC15M"
    up_side: str = "yes"
    price_format: str = "cents"
    min_market_duration_seconds: int = 840
    max_market_duration_seconds: int = 960

    @property
    def base_url(self) -> str:
        return KALSHI_URLS[self.environment]


@dataclass
class FeedConfig:
    sources: list = field(default_factory=lambda: ["coinbase", "kraken"])
    stale_after_seconds: float = 10
    buffer_minutes: int = 120


@dataclass
class StrategyConfig:
    observation_seconds: int = 180
    max_entry_delay_seconds: int = 45
    min_seconds_remaining: int = 540
    reference_mode: str = "exchange_open"
    min_ticks: int = 20
    vol_lookback_minutes: int = 60
    min_vol_bps_per_min: float = 1.5
    max_vol_bps_per_min: float = 30.0
    min_confidence: float = 60.0
    min_abs_z: float = 0.75
    max_flow_contradiction: float = 0.25
    require_trend_agreement: bool = True
    momentum_persistence: float = 0.10
    probability_shrink: float = 0.85
    min_edge: float = 0.04
    min_ev_per_dollar: float = 0.05
    min_contract_price: float = 0.15
    max_contract_price: float = 0.80
    max_spread: float = 0.05
    min_fill_ratio: float = 0.5
    revalidate_min_z_ratio: float = 0.7


@dataclass
class ExecutionConfig:
    order_style: str = "ioc"
    max_slippage: float = 0.02
    passive_wait_seconds: float = 20
    taker_fee_rate: float = 0.07
    maker_fee_rate: float = 0.0175
    paper_extra_slippage: float = 0.0


@dataclass
class RiskConfig:
    dollars_per_trade: float = 10.0
    max_daily_loss: float = 40.0
    max_trades_per_day: int = 24
    max_consecutive_losses: int = 4
    max_open_positions: int = 1
    min_balance_reserve: float = 0.0
    timezone_offset_hours: float = 0


@dataclass
class LiveGateConfig:
    confirm_phrase: str = "I ACCEPT REAL MONEY RISK"
    require_backtest: bool = True
    min_backtest_trades: int = 100
    min_backtest_profit_factor: float = 1.10
    require_backtest_oos_positive: bool = True
    max_backtest_age_days: float = 14
    require_paper_record: bool = True
    min_paper_trades: int = 30
    min_paper_profit_factor: float = 1.0


@dataclass
class BacktestConfig:
    half_spread: float = 0.015
    quote_noise: float = 0.02
    slippage: float = 0.01
    depth: int = 500
    in_sample_fraction: float = 0.7


@dataclass
class ServerConfig:
    host: str = "127.0.0.1"
    port: int = 8787


@dataclass
class Secrets:
    kalshi_key_id: str | None = None
    kalshi_private_key_path: str | None = None
    kalshi_private_key_pem: str | None = None
    live_confirm: str | None = None
    dashboard_token: str | None = None

    def has_kalshi_credentials(self) -> bool:
        return bool(self.kalshi_key_id and (self.kalshi_private_key_path or self.kalshi_private_key_pem))

    def load_private_key_pem(self) -> bytes | None:
        if self.kalshi_private_key_pem:
            return self.kalshi_private_key_pem.replace("\\n", "\n").encode()
        if self.kalshi_private_key_path:
            p = Path(self.kalshi_private_key_path).expanduser()
            return p.read_bytes()
        return None


@dataclass
class Config:
    mode: ModeConfig = field(default_factory=ModeConfig)
    kalshi: KalshiConfig = field(default_factory=KalshiConfig)
    feed: FeedConfig = field(default_factory=FeedConfig)
    strategy: StrategyConfig = field(default_factory=StrategyConfig)
    execution: ExecutionConfig = field(default_factory=ExecutionConfig)
    risk: RiskConfig = field(default_factory=RiskConfig)
    live_gate: LiveGateConfig = field(default_factory=LiveGateConfig)
    backtest: BacktestConfig = field(default_factory=BacktestConfig)
    server: ServerConfig = field(default_factory=ServerConfig)
    secrets: Secrets = field(default_factory=Secrets)
    data_dir: Path = DATA_DIR

    def strategy_fingerprint(self) -> str:
        """Hash of every parameter that changes trading decisions. The live gate requires the
        backtest report to have been produced with the exact same parameters."""
        payload = {
            "strategy": asdict(self.strategy),
            "execution": {k: v for k, v in asdict(self.execution).items()},
            "dollars_per_trade": self.risk.dollars_per_trade,
        }
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:16]

    def public_dict(self) -> dict:
        """Config safe to show in the dashboard (no secrets)."""
        d = {}
        for f in fields(self):
            if f.name in ("secrets", "data_dir"):
                continue
            d[f.name] = asdict(getattr(self, f.name))
        return d


def _load_dotenv(path: Path) -> None:
    """Minimal .env loader (KEY=VALUE lines). Existing env vars win."""
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k, v = k.strip(), v.strip().strip('"').strip("'")
        os.environ.setdefault(k, v)


def _apply(dc, values: dict):
    known = {f.name: f for f in fields(dc)}
    for k, v in values.items():
        if k not in known:
            raise ValueError(f"Unknown config key '{k}' in [{type(dc).__name__}]")
        setattr(dc, k, v)


def load_config(path: str | Path | None = None, env_file: str | Path | None = None) -> Config:
    cfg = Config()
    path = Path(path) if path else ROOT / "config.toml"
    if path.exists():
        with open(path, "rb") as fh:
            raw = tomllib.load(fh)
        for section, values in raw.items():
            if not hasattr(cfg, section):
                raise ValueError(f"Unknown config section [{section}]")
            _apply(getattr(cfg, section), values)

    _load_dotenv(Path(env_file) if env_file else ROOT / ".env")
    cfg.secrets = Secrets(
        kalshi_key_id=os.environ.get("KALSHI_API_KEY_ID") or None,
        kalshi_private_key_path=os.environ.get("KALSHI_PRIVATE_KEY_PATH") or None,
        kalshi_private_key_pem=os.environ.get("KALSHI_PRIVATE_KEY_PEM") or None,
        live_confirm=os.environ.get("KALSHI_LIVE_CONFIRM") or None,
        dashboard_token=os.environ.get("DASHBOARD_TOKEN") or None,
    )
    if os.environ.get("BOT_DATA_DIR"):
        cfg.data_dir = Path(os.environ["BOT_DATA_DIR"])
    cfg.data_dir.mkdir(parents=True, exist_ok=True)
    validate(cfg)
    return cfg


def validate(cfg: Config) -> None:
    if cfg.mode.trading_mode not in ("paper", "live"):
        raise ValueError("mode.trading_mode must be 'paper' or 'live'")
    if cfg.mode.data_source not in ("live", "sim"):
        raise ValueError("mode.data_source must be 'live' or 'sim'")
    if cfg.mode.trading_mode == "live" and cfg.mode.data_source == "sim":
        raise ValueError("live trading cannot use the simulator data source")
    if cfg.kalshi.environment not in KALSHI_URLS:
        raise ValueError("kalshi.environment must be 'prod' or 'demo'")
    if cfg.kalshi.up_side not in ("yes", "no"):
        raise ValueError("kalshi.up_side must be 'yes' or 'no'")
    if cfg.execution.order_style not in ("ioc", "passive"):
        raise ValueError("execution.order_style must be 'ioc' or 'passive'")
    if cfg.strategy.reference_mode not in ("exchange_open", "kalshi_strike"):
        raise ValueError("strategy.reference_mode must be 'exchange_open' or 'kalshi_strike'")
    s = cfg.strategy
    if not (0 < s.min_contract_price < s.max_contract_price < 1):
        raise ValueError("contract price bounds must satisfy 0 < min < max < 1")
    if cfg.risk.dollars_per_trade <= 0 or cfg.risk.max_daily_loss <= 0:
        raise ValueError("risk.dollars_per_trade and risk.max_daily_loss must be positive")
    if cfg.risk.dollars_per_trade > cfg.risk.max_daily_loss:
        raise ValueError("risk.dollars_per_trade cannot exceed risk.max_daily_loss")
    if not 0 < s.probability_shrink <= 1:
        raise ValueError("strategy.probability_shrink must be in (0, 1]")

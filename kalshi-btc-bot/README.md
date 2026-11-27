# Kalshi BTC 15-Minute Momentum Bot

An automated, risk-controlled trading bot for Kalshi's 15-minute Bitcoin UP/DOWN markets (`KXBTC15M`).
It waits out the first 3 minutes of each market, scores BTC's momentum, and buys UP or DOWN **only**
when the signal is strong, the contract is priced below the bot's estimated probability after fees,
and every risk limit allows it. Otherwise it skips.

**Paper trading is the default. Live trading stays off until every live-gate check passes (see below).**

> Not financial advice. Every contract can go to $0. A momentum edge on 15-minute BTC markets is *not*
> established. The backtester measures whether one exists. Don't trade real money unless the real-data
> backtest and your paper record both show an edge.

---

## Workflow (one cycle per market)

| Step | What the bot does |
|---|---|
| 1. Detect | Polls Kalshi for the open `KXBTC15M` market (~15 min long) and records its open/close times and strike |
| 2. Observe | For the first **180 s** it only watches. It streams BTC trades from Coinbase (Kraken as fallback) and updates the momentum score live on the dashboard |
| 3. Analyze | At minute 3 it computes: move vs. open, z-score (move relative to normal noise), regression slope and R², acceleration, path efficiency, sub-window consistency, aggressor buy/sell imbalance, and 60-minute volatility |
| 4. Decide | A composite score gives a direction and a 0–100 confidence. If the components contradict each other (for example, flow opposes price, or the move is reversing), it **skips** |
| 5. Price | Model P(win) = random-walk probability plus optional momentum persistence, shrunk toward 50%. It is compared with the live ask, spread, depth and Kalshi fees, then checked against the edge and EV thresholds |
| 6. Risk | Kill switch, daily loss (counting the worst case of open positions), trades per day, losing streak, open positions, one position per market, balance check (live) |
| 7. Execute | Re-checks the signal and order book on fresh data, then sends a **limit** order (IOC by default, price ≤ ask + slippage cap and ≤ fair value − edge). Only fills Kalshi confirms are recorded |
| 8. Settle | After close it polls the market result and records P&L. Skipped markets get a "shadow" P&L (1 contract at the ask) for analysis |
| 9. Repeat | Moves to the next market automatically |

## Quick start

```bash
cd kalshi-btc-bot
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 1) Offline demo: simulator at 30x speed (no network, no keys)
python -m bot run --sim --speed 30          # open http://127.0.0.1:8787

# 2) Paper trading on real Kalshi + Coinbase data (no keys needed: market data is public)
python -m bot run

# 3) Backtest on real data (writes data/backtest_report.json)
python -m bot backtest --days 30            # Coinbase candles + market-price model
python -m bot backtest --days 14 --kalshi   # + real Kalshi minute-3 quotes and results (needs API key)

python -m bot check-live                    # live-gate status
python -m bot stats                         # paper performance
python -m bot kill                          # kill switch (or: touch data/KILL)
```

Requires Python 3.11+.

## Configuration

* `config.toml` holds every non-secret setting: thresholds, risk limits, fees, gate requirements. Each one is commented.
* `.env` holds secrets (copy `.env.example`). It is git-ignored, and secrets never reach the dashboard.

Key strategy knobs (`[strategy]`): `min_confidence`, `min_abs_z`, `min_edge`, `min_ev_per_dollar`,
`min/max_contract_price`, `max_spread`, `min_seconds_remaining`, `momentum_persistence`, `probability_shrink`.

Key risk knobs (`[risk]`): `dollars_per_trade` (fixed), `max_daily_loss`, `max_trades_per_day`,
`max_consecutive_losses`, `max_open_positions`.

## Risk rules

* **Fixed size.** `dollars_per_trade` comes from config only. No martingale, and no sizing up after losses.
* **Daily loss limit.** A new trade is blocked if realized loss + open-position risk + the new trade's max loss would exceed the limit. Hitting it halts trading until the next trading day and cannot be overridden.
* **Consecutive losses.** Reaching the limit halts trading until you resume it manually (dashboard or `python -m bot resume`). The size does not change on resume.
* **Kill switch.** The dashboard button, `python -m bot kill`, or creating the file `data/KILL` stops new orders within about 1 s and cancels resting orders in live mode. Only a manual clear turns it off.
* **No duplicates.** There is one position per market (a DB unique constraint). The `client_order_id` is deterministic, so Kalshi itself rejects a retried duplicate. After a restart the bot never makes a second decision on a market.

## Enabling live trading (deliberately hard)

All of the following must pass. `python -m bot check-live` shows each check:

1. `config.toml`: `trading_mode = "live"` and `data_source = "live"`
2. `.env`: `KALSHI_LIVE_CONFIRM="I ACCEPT REAL MONEY RISK"`
3. `.env`: `KALSHI_API_KEY_ID` and `KALSHI_PRIVATE_KEY_PATH` set, and the key loads
4. A backtest report from **real data** that is less than 14 days old and was produced with the **current** strategy parameters (fingerprint match), with ≥ 100 trades, profit factor ≥ 1.10 and positive out-of-sample P&L
5. A paper record of ≥ 30 trades with profit factor ≥ 1.0

If live mode is requested and any check fails, the bot runs in **paper** mode and the dashboard shows why.
The dashboard cannot turn on live trading.

## Backtesting: read the calibration table

At minute 3, Kalshi's price already reflects how far BTC is from the strike. Under a pure random walk,
P(UP) = Φ(distance / σ√remaining). The market prices close to that. **The strategy can only win if a minute-3
move continues *more often* than a random walk predicts**, or if the market misprices.

The backtest prints a **momentum calibration** table: for each |z| bucket, the empirical rate at which the
minute-3 direction held to settlement, compared with the random-walk prediction. If "empirical" is not
reliably above "random walk" (by more than its standard error), the momentum edge isn't there, and
`momentum_persistence` should stay at 0.

Other things the backtest does:
* It runs the **same** signal and strategy code as live trading, including fees, slippage and risk limits.
* It splits the data **in-sample and out-of-sample** (70/30, by time). The parameter sweep ranks only on in-sample results, so judge the out-of-sample column. Picking the best of 108 combinations overstates performance.
* It breaks results down by volatility regime, entry price and confidence.
* It has known gaps compared with live trading. 1-minute candles are coarser than ticks and have no buy/sell aggressor data. Without `--kalshi`, both the quotes and the outcomes come from a model and Coinbase, not from Kalshi or BRTI.
* `--synthetic` is a sanity check only. On random-walk data it should show **no** edge, and it does. The live gate rejects synthetic reports.

## Architecture

```
bot/
  config.py        config.toml + .env loading, validation, strategy fingerprint
  kalshi_client.py Kalshi v2 REST: RSA-PSS signing, retries/backoff, rate limiting
  btc_feed.py      Coinbase/Kraken websockets, failover, reconnect, tick buffer, volatility
  market_data.py   current-market discovery
  signals.py       features, momentum score, probability model   (shared with backtest)
  strategy.py      entry checks -> BUY UP / BUY DOWN / SKIP         (shared with backtest)
  fees.py          Kalshi fee formula and trade economics
  risk.py          risk manager and kill switch
  execution.py     PaperExecutor (fills against the live book) / LiveExecutor (confirmed fills)
  engine.py        per-market state machine, settlement, analytics
  live_gate.py     live-trading requirements
  storage.py       SQLite: markets, positions, decision log, risk state
  simulator.py     offline synthetic BTC and Kalshi markets
  server.py        FastAPI dashboard, REST and websocket API (localhost by default)
  backtest/        historical data loaders and the backtest engine
dashboard/         dark single-page dashboard (vanilla JS + canvas, no CDN)
data/              bot.db, bot.log, decisions.jsonl, backtest_report.json (git-ignored)
```

## Operational notes

* **Run continuously.** Use `systemd`, `tmux` or Docker with restart-on-failure. The engine loop survives individual errors. The feed reconnects and fails over between exchanges. Open positions and unsettled markets are recovered on restart.
* **Security.** The dashboard binds to `127.0.0.1`. If you expose it, set `DASHBOARD_TOKEN`; control endpoints refuse non-local requests without it. Keep the private key file at `chmod 600`.
* **Settlement source.** Kalshi settles on CF Benchmarks BRTI, not Coinbase. With the default `reference_mode = "exchange_open"`, the bot measures the move on its own feed from that feed's open price, so most of the exchange-vs-index difference cancels out. The difference still matters for markets that finish very close to the strike.
* **Verify the API against Kalshi's docs before going live.** This code was written against Kalshi Trade API v2: `/markets`, `/markets/{t}/orderbook`, `/portfolio/orders` with `time_in_force`, `/portfolio/fills`. It accepts both cents and `*_dollars` fields. The live order path is covered by mocked tests only. Run paper mode, then `environment = "demo"` with a demo key, before using production.
* **Fees.** The default is Kalshi's published formula, `ceil(0.07 · C · P · (1−P))`. Check the current fee schedule for this series and adjust `[execution]` if it differs.

## Tests

```bash
python -m pytest -q
```
Covers: fee math, order-book parsing and walking, signal scoring and contradictions, entry checks,
risk limits and persistence, kill switch, request signing, client retries, live-executor fill confirmation and
duplicate handling, full engine cycles on the simulator (no trade before minute 3, settlement, no duplicate
positions, restart safety), live gate, and backtest no-lookahead.

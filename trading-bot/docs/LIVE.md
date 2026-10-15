# propbot live layer

`propbot/live/` runs a research strategy against a broker with an independent risk agent in
the middle. It's built for the **Lucid Trading 25K eval with EOD drawdown**:

- profit target: +$1,250
- max loss: $1,000, trailing on end-of-day balances
- daily loss limit: $600
- consistency: 50%
- size limit: 2 minis or 20 micros
- must be flat by 15:55 ET

The core doesn't depend on any trading platform. The platform (most likely NinjaTrader 8 or
Tradovate) plugs in through one small adapter interface.

```
          completed 1-min bars                       fills (synchronous)
 Broker ───────────────────────► LiveEngine ◄──────────────────────────── Broker
   ▲                              │   │                                     ▲
   │                    on_bar    │   │ Signal(side, stop, target)          │
   │                              ▼   ▼                                     │
   │                    ┌──────────────────────┐                            │
   │                    │   STRATEGY AGENT     │  propbot.strategies.*      │
   │                    │   (no broker access) │  same objects as research  │
   │                    └──────────┬───────────┘                            │
   │                               │ submit_entry / submit_exit             │
   │                               ▼                                        │
   │                    ┌──────────────────────┐   flatten / lock / halt    │
   │                    │  RISK GUARDIAN AGENT │───────────────────────────►│
   │   place_bracket    │  vetoes, shrinks,    │   modify_stop (budget stop)│
   └────────────────────│  overrides           │                            │
                        └──────────┬───────────┘                            │
                                   │ reads/writes                           │
                                   ▼                                        │
                        ┌──────────────────────┐                            │
                        │  ACCOUNT-STATE AGENT │  EvalAccount + DayLedger   │
                        │  (JSON, atomic save) │  -> DayResult at EOD       │
                        └──────────────────────┘                            │
                                                                            │
                        EXECUTION / BROKER AGENT: PaperBroker | NT8 | Tradovate
```

| Module | Role |
|---|---|
| `broker.py` | `Broker` protocol, `Bar` / `Fill` / `Position`, `PaperBroker` (bar replay, backtest-identical fills) |
| `guardian.py` | `RiskGuardian`, `GuardianConfig`, `Decision` |
| `state.py` | `AccountState` (persisted `rules.EvalAccount` + halt flag + today's ledger), `DayLedger` |
| `engine.py` | `LiveEngine`: bar loop, session roll, strategy calls, signal routing |
| `events.py` | `EventLog`: JSON-lines decision log (one object per decision, with a reason) |
| `__main__.py` | paper-trading CLI |

## The agents

### Strategy agent

This is any `propbot.strategies` object, the same class and parameters that were researched.
On every completed bar it gets `on_bar(i, session_bars, position)` and can return a
`Signal(side, stop, target, tag)`. It can't reach the broker.

The engine stops calling it when:

- the day is locked
- the guardian is halted
- the bar opens at or after 15:55

The backtester stops calling it in the same cases, so indicators that carry across sessions
(such as `ema_trend` with `carry=True`) end up in the same state as in research.

### Risk guardian agent (`RiskGuardian`)

This is the most important piece. It's the only code path that sends orders. At the start of
each session it calls `rules.room_today(account, safety_buffer)` and derives two numbers.

The daily loss budget:

```
budget = min(room_to_floor - safety_buffer,      # EOD-trailing max loss
             daily_loss_limit - safety_buffer,   # firm DLL ($600)
             bot_daily_stop)                     # the bot's own stop (default $300)
```

The daily profit cap:

```
profit_cap = min(daily_profit_cap, consistency_cap_fraction * max_profit_today_for_consistency)
```

At the start of a fresh account the consistency cap is $625, half of $1,250.

**Entry checks** (`submit_entry`). They run in this order. Every outcome is logged as
`entry_approved`, `entry_reduced` or `entry_rejected`, with a reason and the numbers behind it.

1. Reject if the bot is halted (passed, failed or kill switch), the day is locked, or the kill
   switch file is present.
2. Reject if the fill time (the signal bar's close, which is the next bar's open) is outside
   `[trade_start, last_entry_time)`. The default window is 09:30–15:55.
3. Reject if `max_trades_per_day` has been reached.
4. Reject if a stop is required but missing, or if the stop is on the wrong side of the price.
5. Size: `qty * mini_equivalent` must be `<= max_minis` (also capped by `max_qty`).
6. Reject if the commission alone would push the day past `-budget`.
7. Stop risk: `qty * ((|ref - stop| + risk_slippage_ticks*tick) * point_value + commission)`
   must keep `realised + open - risk` above `-budget`.
8. Reject if realised profit today is already `>= profit_cap`.

For checks 5 and 7, `size_policy="reject"` (the default) vetoes the entry.
`size_policy="reduce"` shrinks `qty` to the largest size that fits, and rejects only if that
is 0.

Approved entries go out as `place_bracket`. If the bot holds an opposite position, it is
flattened first.

**Fill handling** (`on_fill`):

- Right after an entry fills, the guardian moves the resting stop to the price where the
  day's P&L would equal `-budget`, if that is tighter than the strategy's stop. This uses
  `modify_stop`, with the same formula and tick rounding as the backtester's `daily_stop`.
- A stop-out at that level locks the day.
- The day is also locked when realised P&L `<= -budget` or `>= profit_cap`.

**Bar checks** (`on_bar`). These run on every bar, before the strategy:

| Condition | Action |
|---|---|
| halted | flatten anything still open |
| `STOP` file exists | flatten + **halt** |
| bar closes at/after 15:55 ET | flatten (fills at the 15:55 open) |
| realised + open P&L `<= -budget` | flatten + lock day |
| equity `<= floor + floor_buffer` | flatten + lock day |
| target, consistency and min days met counting today | flatten + lock day |
| realised `>= profit_cap` | lock day (no new entries) |

The last row above is how a pass gets banked. At end of day, if the `EvalAccount` reports
PASSED, the guardian halts and logs **`PASSED — stop trading`**. A FAILED account halts too.

`on_clock(now)` repeats the kill-switch and 15:55 checks without waiting for a bar. A live
adapter should call it from a timer so that a stalled data feed can't keep a position open.

### Execution / broker agent (`Broker`)

```python
class Broker(Protocol):
    def connect(self) -> None
    def subscribe_bars(self, symbol: str, callback: Callable[[Bar], None]) -> None   # completed bars
    def subscribe_fills(self, callback: Callable[[Fill], None]) -> None              # executions
    def get_position(self, symbol: str) -> Position                                  # signed qty, avg price
    def get_account_balance(self) -> float
    def place_bracket(self, symbol, side, qty, stop, target) -> str                  # order id
    def modify_stop(self, order_id: str, price: float) -> None
    def flatten(self, symbol: str) -> None                                           # cancel all + close
    def cancel_all(self, symbol: str) -> None
```

`subscribe_fills` was added to the eight methods in the spec. Without fill events the guardian
couldn't arm the budget stop right after an entry or book trades, and every real platform
provides them.

`PaperBroker(bars, contract, slippage_ticks=1)` replays a Bars DataFrame bar by bar:

- Orders sent on bar *i*'s close fill at bar *i+1*'s open, plus slippage against you.
- Bracket legs are live from the fill bar's range onward. If a bar touches both, the stop
  wins.
- A stop fills at the stop price minus slippage, or at the bar open if price gapped through
  it. A target fills exactly at the target.
- Commission is `commission_rt * qty` per round trip.
- Unfilled orders expire at the end of the session. A position still open after the last
  bar closes at that bar's close.

These are exactly the `propbot.backtest` semantics.

### Account-state agent (`AccountState`, `DayLedger`)

`DayLedger` turns fills into realised P&L and `Trade` records. It also tracks the day's worst
intraday P&L, marking every bar's adverse extreme clamped at the resting stop, the same way the
backtester does. At the session roll it produces a `DayResult`, which goes through
`EvalAccount.apply_day`.

`AccountState` saves the following after every fill, lock, halt and end of day. Saves are
atomic (temp file plus rename).

- balance
- EOD high and trailing floor
- best day, days traded and days used
- status and consistency-extension flag
- full history
- today's ledger: realised P&L, worst, trades, entries, open position, lock reason
- the halt flag

What happens on restart:

- Same date: the intraday state, including any lock, is resumed.
- Later date and the last day was never booked: that day is booked first.
- The state was written with different `EvalRules` or a different contract: loading fails.
- Halted by the kill switch: the halt is cleared only when a new process starts after the
  `STOP` file has been removed. A running bot stays halted.
- Halted after PASSED or FAILED: the halt persists.

### Engine (`LiveEngine`)

```python
LiveEngine(strategy, broker, guardian, contract, qty, symbol=None, *,
           session_start="09:30", session_end="16:00", log=None, on_day_end=None)
engine.start()                 # connect, subscribe, reconcile (flattens unknown broker positions)
engine.warmup(history_bars)    # optional, before start(): warm up carry indicators, no orders
engine.on_clock(now)           # timer tick -> guardian time checks
engine.finish()                # book the open session (end of replay / shutdown)
engine.days                    # list[DayResult]
```

For each completed bar the engine does the following, in order:

1. Ignore the bar if it is outside RTH.
2. If the date has changed, book the previous session, call `strategy.reset()` and run
   `guardian.begin_session(date)`.
3. Append the bar to the session frame.
4. Run `guardian.on_bar`.
5. If the guardian allows it, call `strategy.on_bar`.
6. Route the signal. `side=0` goes to `submit_exit`. A signal on the same side as the current
   position is ignored. Anything else goes to `submit_entry`.

The day is booked at 16:00 once flat, or at the next session roll or `finish()` otherwise.
If the strategy raises an exception, the guardian flattens and locks the day.

Every decision is written to the JSON-lines log. Each record has these fields: `wall`, `ts`
(market time), `level`, `agent` (`engine` or `guardian`), `event` and `reason`, plus the
numbers involved.

## Paper trading

```bash
python -m propbot.live --strategy ema_trend --params '{"fast":9}' --qty 2 --synthetic 20
python -m propbot.live --strategy orb --qty 2 --csv data/MNQ_1min.csv --state paper_state.json
```

Useful flags:

- `--daily-stop 300` (or `none`): the bot's daily stop
- `--buffer 50`: the safety buffer
- `--profit-cap X`, `--no-consistency-cap`, `--cap-fraction 0.9`: profit-cap settings
- `--reduce`: shrink oversize entries instead of rejecting them
- `--max-trades N`: maximum entries per day
- `--slippage 1`: slippage in ticks
- `--state FILE`: persist the account between runs (default: a fresh in-memory account)
- `--log FILE`: the decision log (default `logs/paper-<utc>.jsonl`)
- `--kill-switch STOP`: the kill-switch file path
- `--keep-going`: keep replaying after a halt
- `-v`: also echo decisions to stderr

The CLI prints one line per day: date, P&L, trades, balance, floor, room to the floor, best day,
profit still needed, days traded, account status, and any lock or halt. At the end it prints a
summary of the account and the guardian's actions.

To stop everything immediately, create the kill-switch file: `touch STOP`.

### Parity with the backtester

`tests/test_live.py::test_paper_broker_matches_backtest` checks that the live stack reproduces
`run_backtest` on synthetic MNQ sessions. The setup:

- The stack is `PaperBroker` + `LiveEngine` + `RiskGuardian`, with the guardian configured to
  apply only the backtester's `daily_stop` / `daily_profit_cap`.
- Strategies: `ema_trend`, `orb`, `vwap_reversion`.
- Settings: no stop; a $60 daily stop; a $250 daily stop with a $150 profit cap.

Every day's P&L and intraday drawdown match, and so does every trade's time, side, qty, entry,
exit and P&L. The only difference is float rounding, around 1e-12.

The match is exact, not just close, because:

- the guardian's budget stop uses the backtester's `daily_stop` price formula and rounding, and
  is applied through a synchronous fill callback before the fill bar's range is checked;
- the strategy goes quiet at the same moments the backtester stops calling it;
- the ledger books P&L and intraday lows with the same arithmetic.

With the default guardian, results differ from the backtest only where the guardian
deliberately vetoed, shrank or locked. Every such case is in the log.

## Writing a real adapter

An adapter is a class that implements the nine `Broker` methods. Get these right whatever the
platform:

- **Completed bars only.** Emit a 1-minute bar once the minute has closed. `Bar.time` is the
  bar's OPEN time in America/New_York. Use exchange timestamps, not the local clock. Never emit
  a partial bar.
- **Fills before the bar.** Deliver every execution to the fill callbacks when it happens.
  Report the actual fill price and quantity, including partial fills. The ledger supports
  partial closes and scaling in. Deduplicate executions by exchange execution id, because
  reconnects can replay them.
- **Bracket = OCO.** The stop and target must be real resting orders at the broker or
  exchange, not orders simulated in Python, so the position stays protected if this process
  dies. `modify_stop` must change the live stop order.
- **`flatten` must be idempotent.** It cancels working orders and closes the position at
  market, and calling it twice must not open a position in the other direction.
- **Threading.** If the platform calls back on its own threads, queue bars and fills onto one
  thread before calling into the engine. Guardian state isn't thread-safe.
- **Clock.** Call `engine.on_clock(now)` every 1–5 seconds so the kill switch and 15:55 flatten
  still work if the bar feed stalls.
- **Reconnects.** On reconnect, compare the platform's position with the ledger.
  `LiveEngine.start()` flattens any position it doesn't know about.
- **Contract roll.** MNQ is quarterly. Map `"MNQ"` to the front month (for example `MNQZ6`) and
  roll before expiry week.
- **Firm rules on automation.** Confirm with Lucid that automated or API trading is permitted
  on the account, and on which platform connection. Prop firms differ, and breaking their
  terms can void a pass.

### NinjaTrader 8, option A: a NinjaScript bridge strategy (recommended for NT8)

Write a small C# `Strategy` that relays data and orders and makes no decisions. It talks to
Python over a local TCP socket or named pipe, using one JSON message per line.

- **Settings:** `Calculate = Calculate.OnBarClose` on a 1-minute series in Eastern time.
  `IsExitOnSessionCloseStrategy = true` with `ExitOnSessionCloseSeconds` as a second safety
  net. Only act in `State.Realtime`, and send historical bars as warmup.
- **Bars:** in `OnBarUpdate`, send `Time[0]`, which NT stamps with the bar's close time, so
  subtract 1 minute to get the open. Also send `Open[0]`, `High[0]`, `Low[0]`, `Close[0]` and
  `Volume[0]`.
- **Fills:** `OnExecutionUpdate(execution, executionId, price, quantity, marketPosition, orderId, time)`
  maps to `Fill`. Use `execution.Order.Name` or `OrderId` to map back to the bracket id.
- **`place_bracket`:** use the Unmanaged approach (`IsUnmanaged = true`). Call
  `SubmitOrderUnmanaged` once for the market entry. In `OnExecutionUpdate`, after the entry
  fills, submit a `StopMarket` and a `Limit` order sharing an OCO id. The Managed approach,
  `SetStopLoss` / `SetProfitTarget` before `EnterLong` / `EnterShort`, also works but is harder
  to modify reliably.
- **`modify_stop`:** `ChangeOrder(stopOrder, qty, 0, newStopPrice)`.
- **`flatten`:** cancel the working orders with `CancelOrder`, then submit a market order for
  the opposite side, or call `Account.Flatten(new[]{Instrument})`. **`cancel_all`:**
  `CancelOrder` for each working order.
- **`get_position`:** `Position.MarketPosition`, `Position.Quantity` and
  `Position.AveragePrice`, or `Account.Positions` for the account-wide view.
- **`get_account_balance`:** `Account.Get(AccountItem.CashValue, Currency.UsDollar)`.

### NinjaTrader 8, option B: ATI (Automated Trading Interface)

Enable ATI under Tools > Options > Automated trading interface. Python can send orders either
by writing OIF files to `Documents\NinjaTrader 8\incoming` or by calling `NTDirect.dll` through
ctypes. The relevant calls:

- `Command("PLACE", account, instrument, "BUY"/"SELL", qty, "MARKET"/"STOPMARKET"/"LIMIT", limit, stop, "DAY", ocoId, orderId, "", "")`
- `Command("CHANGE", ...)` for `modify_stop`
- `Command("CANCELALLORDERS")` and `Command("CLOSEPOSITION", account, instrument)` for `flatten`
- `MarketPosition(instrument, account)` and `AvgEntryPrice(instrument, account)` for positions
- `CashValue(account)` for the balance
- `Filled(orderId)`, `AvgFillPrice(orderId)` and `OrderStatus(orderId)` for fills, by polling

ATI has no bar stream, so bars must come from somewhere else: the `MarketData`/`Last` calls
aggregated into minutes, or a separate data feed. Fills have to be polled. Option A is
simpler and lower latency.

### Tradovate API

Tradovate uses REST plus WebSocket. Base URLs: `https://demo.tradovateapi.com/v1` and
`https://live.tradovateapi.com/v1`; market data at `wss://md.tradovateapi.com/v1/websocket`.

- **`connect`:**
  - `POST /auth/accesstokenrequest` with name, password, appId, appVersion, cid, sec and
    deviceId. It returns `accessToken` and `mdAccessToken`.
  - Renew with `/auth/renewaccesstoken` before expiry.
  - Open the trading WebSocket and send `user/syncrequest` to receive live entity updates.
  - Answer heartbeats with `[]` about every 2.5 s.
  - Look up the contract with `/contract/find?name=MNQZ6` and get the account id from
    `/account/list`.
- **`subscribe_bars`:** `md/getChart` with `{"symbol": "MNQZ6", "chartDescription":
  {"underlyingType": "MinuteBar", "elementSize": 1, "elementSizeUnit": "UnderlyingUnits"},
  "timeRange": {...}}`. Bars arrive as updates to the forming bar; emit a bar only when the
  next one starts. Timestamps are UTC, so convert to ET.
- **`subscribe_fills`:** `fill` and `executionReport` entity events from the user sync stream.
  `position` events give the position.
- **`place_bracket`:** `POST /order/placeOSO` with a market entry and `bracket1` (Stop) and
  `bracket2` (Limit), which Tradovate links as OCO. Keep the bracket order ids.
- **`modify_stop`:** `POST /order/modifyorder` with `orderId`, `orderQty`, `orderType: "Stop"`
  and `stopPrice`.
- **`flatten`:** `POST /order/liquidateposition` with `accountId`, `contractId` and
  `admin: false`. It cancels the working orders and closes the position.
- **`cancel_all`:** `POST /order/cancelorder` for each working order (`/order/list`, filtered
  by account and contract).
- **`get_position`:** `/position/list`, or the cached sync-stream state (`netPos`, `netPrice`).
- **`get_account_balance`:** `POST /cashBalance/getcashbalancesnapshot` with `{"accountId": ...}`.

Prop accounts on Tradovate may need the firm to enable API access, and Tradovate may require
an API add-on. Check both before building.

Before using any adapter on the eval, run it on a demo or sim account through the full guardian
for several sessions. Compare the platform's fills against the `PaperBroker` replay of the same
bars.

## Caveats

- **The profit cap is checked before entries, not during trades.** A single winning trade can
  still overshoot the consistency-safe cap. In one synthetic run, a day made $696 against a
  $625 cap, which raised the effective target. Use `consistency_cap_fraction < 1`, smaller
  size or tighter targets if that matters.
- **Intraday drawdown comes from 1-minute bar extremes,** not ticks. The firm measures
  tick-level equity, so keep `safety_buffer` above typical slippage on a stop.
- **Live fills will be worse than paper,** which assumes one tick of slippage. Stop-market
  orders in fast markets slip more, and real fills arrive with latency.
- **`max_trades_per_day` counts approved entries,** not fills. An order cancelled before it
  fills still counts.
- **One instrument and one position at a time.** That matches all current strategies.
- **Restarting mid-session** keeps the account and intraday risk state, but not the strategy's
  in-memory indicators. Call `engine.warmup(recent_bars)` before `start()`.

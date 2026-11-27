(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  let S = null;              // latest server state
  let clockOffset = 0;       // server_time - local time
  let lastPrice = null;

  // ---------------------------------------------------------------- formatting
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const usd = (v, d = 2) => v == null || isNaN(v) ? "—" : (v < 0 ? "-$" : "$") + Math.abs(v).toLocaleString(undefined, { minimumFractionDigits: d, maximumFractionDigits: d });
  const sUsd = (v) => v == null ? "—" : (v > 0 ? "+" : "") + usd(v);
  const pct = (v, d = 1) => v == null ? "—" : (v * 100).toFixed(d) + "%";
  const cents = (v) => v == null ? "—" : Math.round(v * 100) + "¢";
  const num = (v, d = 2, sign = false) => v == null || isNaN(v) ? "—" : (sign && v > 0 ? "+" : "") + Number(v).toFixed(d);
  const mmss = (s) => { if (s == null) return "--:--"; s = Math.max(0, Math.floor(s)); return String(Math.floor(s / 60)).padStart(2, "0") + ":" + String(s % 60).padStart(2, "0"); };
  const tm = (ts) => ts ? new Date(ts * 1000).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }) : "—";
  const dt = (ts) => ts ? new Date(ts * 1000).toLocaleString([], { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }) : "—";
  const cls = (v) => v > 0 ? "pos" : v < 0 ? "neg" : "";
  const setText = (id, t, c) => { const el = $(id); if (!el) return; el.textContent = t; if (c !== undefined) el.className = el.className.replace(/\b(pos|neg)\b/g, "").trim() + (c ? " " + c : ""); };
  const setPill = (id, text, kind) => { const el = $(id); el.textContent = text; el.className = "pill" + (kind ? " " + kind : ""); };

  function table(el, cols, rows, empty) {
    if (!rows || !rows.length) { el.innerHTML = `<tr><td class="empty" colspan="${cols.length}">${empty}</td></tr>`; return; }
    el.innerHTML = "<thead><tr>" + cols.map((c) => `<th>${c[0]}</th>`).join("") + "</tr></thead><tbody>" +
      rows.map((r) => "<tr>" + cols.map((c) => { const v = c[1](r); return typeof v === "object" && v ? `<td class="${v.c || ""}">${v.h}</td>` : `<td>${esc(v)}</td>`; }).join("") + "</tr>").join("") + "</tbody>";
  }

  // ---------------------------------------------------------------- chart
  function drawChart() {
    const cv = $("chart"); if (!cv || !S) return;
    const dpr = window.devicePixelRatio || 1, W = cv.clientWidth, H = 300;
    cv.width = W * dpr; cv.height = H * dpr; const g = cv.getContext("2d"); g.scale(dpr, dpr);
    g.clearRect(0, 0, W, H);
    const pts = (S.btc && S.btc.chart) || [];
    if (pts.length < 2) { g.fillStyle = "#4a5468"; g.font = "13px sans-serif"; g.fillText("Waiting for price data…", 16, 30); return; }
    const m = S.market, ref = m && m.reference_price;
    let t0 = pts[0][0], t1 = Math.max(pts[pts.length - 1][0], S.server_time);
    if (m) t1 = Math.max(t1, Math.min(m.close_ts, t1 + 60));
    let lo = Infinity, hi = -Infinity;
    for (const p of pts) { lo = Math.min(lo, p[1]); hi = Math.max(hi, p[1]); }
    if (ref) { lo = Math.min(lo, ref); hi = Math.max(hi, ref); }
    const pad = Math.max((hi - lo) * 0.12, 5); lo -= pad; hi += pad;
    const L = 64, R = 12, T = 10, B = 24;
    const x = (t) => L + (t - t0) / (t1 - t0) * (W - L - R);
    const y = (p) => T + (hi - p) / (hi - lo) * (H - T - B);
    // grid + labels
    g.strokeStyle = "#1c2436"; g.lineWidth = 1; g.fillStyle = "#6b7790"; g.font = "11px " + getComputedStyle(document.body).getPropertyValue("--mono");
    for (let i = 0; i <= 4; i++) { const p = lo + (hi - lo) * i / 4, yy = y(p); g.beginPath(); g.moveTo(L, yy); g.lineTo(W - R, yy); g.stroke(); g.fillText(p.toFixed(0), 6, yy + 4); }
    for (let t = Math.ceil(t0 / 300) * 300; t <= t1; t += 300) { const xx = x(t); g.fillText(new Date(t * 1000).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }), xx - 16, H - 6); }
    // observation window + markers
    if (m) {
      const oa = x(Math.max(m.open_ts, t0)), ob = x(m.open_ts + 180);
      g.fillStyle = "#7c8cff18"; g.fillRect(oa, T, ob - oa, H - T - B);
      const vline = (t, color, label) => { if (t < t0 || t > t1) return; const xx = x(t); g.strokeStyle = color; g.setLineDash([4, 4]); g.beginPath(); g.moveTo(xx, T); g.lineTo(xx, H - B); g.stroke(); g.setLineDash([]); g.fillStyle = color; g.fillText(label, xx + 4, T + 12); };
      vline(m.open_ts, "#7c8cff", "open"); vline(m.open_ts + 180, "#f5b54a", "min 3"); vline(m.close_ts, "#f2546b", "close");
      if (ref) { g.strokeStyle = "#9fb3ff"; g.setLineDash([6, 4]); g.beginPath(); g.moveTo(L, y(ref)); g.lineTo(W - R, y(ref)); g.stroke(); g.setLineDash([]); }
    }
    // price line with area
    const grad = g.createLinearGradient(0, T, 0, H - B); grad.addColorStop(0, "#f7931a33"); grad.addColorStop(1, "#f7931a00");
    g.beginPath(); pts.forEach((p, i) => i ? g.lineTo(x(p[0]), y(p[1])) : g.moveTo(x(p[0]), y(p[1])));
    g.lineTo(x(pts[pts.length - 1][0]), H - B); g.lineTo(x(pts[0][0]), H - B); g.closePath(); g.fillStyle = grad; g.fill();
    g.beginPath(); pts.forEach((p, i) => i ? g.lineTo(x(p[0]), y(p[1])) : g.moveTo(x(p[0]), y(p[1])));
    g.strokeStyle = "#f7931a"; g.lineWidth = 2; g.stroke();
    const last = pts[pts.length - 1]; g.fillStyle = "#f7931a"; g.beginPath(); g.arc(x(last[0]), y(last[1]), 4, 0, Math.PI * 2); g.fill();
  }

  function drawEquity() {
    const cv = $("equity"); if (!cv || !S) return;
    const dpr = window.devicePixelRatio || 1, W = cv.clientWidth, H = 110;
    cv.width = W * dpr; cv.height = H * dpr; const g = cv.getContext("2d"); g.scale(dpr, dpr);
    const pts = (S.stats && S.stats.equity_curve) || [];
    g.fillStyle = "#4a5468"; g.font = "11px sans-serif";
    if (pts.length < 2) { g.fillText("Equity curve appears after 2+ settled trades", 6, 20); return; }
    const vals = [0, ...pts.map((p) => p[1])]; const lo = Math.min(...vals), hi = Math.max(...vals), span = (hi - lo) || 1;
    const x = (i) => 4 + i / (vals.length - 1) * (W - 8), y = (v) => 6 + (hi - v) / span * (H - 12);
    g.strokeStyle = "#2a3450"; g.beginPath(); g.moveTo(0, y(0)); g.lineTo(W, y(0)); g.stroke();
    g.beginPath(); vals.forEach((v, i) => i ? g.lineTo(x(i), y(v)) : g.moveTo(x(i), y(v)));
    g.strokeStyle = vals[vals.length - 1] >= 0 ? "#22c58b" : "#f2546b"; g.lineWidth = 2; g.stroke();
  }

  // ---------------------------------------------------------------- render
  function renderTimers() {
    if (!S) return;
    const now = Date.now() / 1000 + clockOffset, m = S.market;
    if (!m) { setText("cd-close", "--:--"); setText("cd-obs", "--:--"); return; }
    setText("cd-close", mmss(m.close_ts - now));
    const toDec = m.open_ts + 180 - now;
    setText("cd-obs", toDec > 0 ? mmss(toDec) : "DONE");
    $("obs-bar").style.width = Math.min(100, Math.max(0, (now - m.open_ts) / (m.close_ts - m.open_ts) * 100)) + "%";
  }

  function render() {
    const s = S; if (!s) return;
    // top bar
    const live = s.mode === "live";
    const mb = $("mode-badge"); mb.textContent = live ? "LIVE · REAL MONEY" : "PAPER"; mb.className = "badge " + (live ? "badge-live" : "badge-paper");
    $("source-badge").textContent = s.data_source === "sim" ? "SIMULATOR" : "KALSHI + EXCHANGE";
    const p = s.btc.price;
    const el = $("btc-price"); el.textContent = p ? "$" + p.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : "—";
    if (lastPrice && p && p !== lastPrice) { el.classList.remove("tick-up", "tick-down"); el.classList.add(p > lastPrice ? "tick-up" : "tick-down"); }
    lastPrice = p;
    setPill("feed-status", s.btc.stale ? "stale" : (s.btc.source || s.btc.status), s.btc.stale ? "bad" : "ok");
    const kb = $("kill-btn"); kb.textContent = s.risk.kill_engaged ? "KILL ENGAGED" : "KILL SWITCH"; kb.classList.toggle("engaged", s.risk.kill_engaged);

    const ban = $("banner");
    if (s.risk.kill_engaged) { ban.className = "banner bad"; ban.textContent = "Kill switch engaged — no new orders will be placed. Reason: " + (s.risk.kill_reason || "manual"); }
    else if (s.requested_mode === "live" && !live) { ban.className = "banner warn"; ban.textContent = "Live trading was requested but the live gate failed — running in PAPER mode. See Live Trading Gate."; }
    else if (s.risk.halted_reason) { ban.className = "banner warn"; ban.textContent = "Trading halted: " + s.risk.halted_reason; }
    else ban.className = "banner hidden";

    // market
    const m = s.market;
    if (m) {
      $("m-ticker").textContent = m.ticker + (m.notes && m.notes.length ? "  ·  " + m.notes.join("; ") : "");
      const ph = { OBSERVING: "info", DECIDING: "warn", IN_POSITION: "ok", SKIPPED: "warn", MISSED: "bad" }[m.phase] || "";
      setPill("phase", m.phase.replace(/_/g, " "), ph);
      setText("m-ref", m.reference_price ? usd(m.reference_price) : "—");
      setText("m-strike", m.strike ? usd(m.strike) : "—");
      const b = m.book || {}; const up = m.up_side, dn = up === "yes" ? "no" : "yes";
      setText("m-up", `${cents(b[up + "_ask"])} / ${cents(b[up + "_bid"])}`);
      setText("m-down", `${cents(b[dn + "_ask"])} / ${cents(b[dn + "_bid"])}`);
    } else { $("m-ticker").textContent = "waiting for the next BTC 15-minute market…"; setPill("phase", "waiting"); }

    // momentum
    const f = m && m.features, sig = m && m.signal;
    const thr = s.config.strategy.min_confidence;
    $("conf-thr").style.left = thr + "%";
    if (sig) {
      const d = $("mom-dir"); d.textContent = sig.direction === "UP" ? "▲ UP" : sig.direction === "DOWN" ? "▼ DOWN" : "—";
      d.className = "dir " + (sig.direction === "UP" ? "dir-up" : sig.direction === "DOWN" ? "dir-down" : "dir-none");
      setText("mom-conf", sig.confidence.toFixed(0) + " / 100");
      $("conf-bar").style.width = Math.min(100, sig.confidence) + "%";
      setPill("mom-live", m.phase === "OBSERVING" ? "live · observing" : "final at min 3", m.phase === "OBSERVING" ? "info" : "");
      const comps = sig.components || {};
      $("components").innerHTML = Object.entries(comps).map(([k, v]) => {
        const w = Math.min(50, Math.abs(v) * 50), left = v >= 0 ? 50 : 50 - w, col = v >= 0 ? "var(--up)" : "var(--down)";
        return `<div class="comp"><span>${esc(k)}</span><div class="comp-track"><div class="comp-bar" style="left:${left}%;width:${w}%;background:${col}"></div></div><span class="mono">${num(v, 2, true)}</span></div>`;
      }).join("") + (sig.contradictions.length ? `<div class="small neg">⚠ ${sig.contradictions.map(esc).join(" · ")}</div>` : "");
    } else {
      $("mom-dir").textContent = "—"; $("mom-dir").className = "dir dir-none"; setText("mom-conf", "—"); $("conf-bar").style.width = "0"; $("components").innerHTML = "";
      setPill("mom-live", "—");
    }
    setText("f-ret", f ? num(f.ret_pct, 3, true) + "%" : "—", f ? cls(f.ret_pct) : "");
    setText("f-z", f ? num(f.z_score, 2, true) : "—");
    setText("f-slope", f ? num(f.slope_bps_per_min, 2, true) + " bp/m" : "—");
    setText("f-accel", f ? num(f.accel_bps_per_min, 2, true) + " bp/m" : "—");
    setText("f-eff", f ? pct(f.efficiency, 0) : "—");
    setText("f-flow", f && f.flow_imbalance != null ? num(f.flow_imbalance, 2, true) : "—", f ? cls(f.flow_imbalance) : "");
    setText("f-vol", f ? num(f.vol_bps_per_min, 2) + " bp/m" : (s.btc.vol_bps_per_min ? num(s.btc.vol_bps_per_min, 2) + " bp/m" : "—"));
    setText("f-pup", m && m.p_up != null ? pct(m.p_up) : "—");

    // decision
    const d = m && m.decision, dec = $("decision");
    if (d) {
      const fill = m.fill;
      dec.textContent = d.action === "SKIP" ? "SKIP" : d.action + (fill && fill.filled ? " ✓" : "");
      dec.className = "decision " + (d.action === "BUY UP" ? "decision-up" : d.action === "BUY DOWN" ? "decision-down" : "decision-skip");
      const e = d.economics || {};
      const price = fill && fill.filled ? fill.avg_price : d.expected_avg_price;
      const n = fill && fill.filled ? fill.filled : d.contracts;
      setText("d-price", price ? cents(price) + (fill && fill.filled ? " (filled)" : " (est.)") : (d.best_ask ? cents(d.best_ask) + " ask" : "—"));
      setText("d-limit", cents(d.limit_price));
      setText("d-contracts", n || "—");
      setText("d-size", e.cost != null ? usd(fill && fill.filled ? fill.cost : e.cost) : usd(s.risk.limits.dollars_per_trade) + " max");
      setText("d-payout", n ? usd(n) : "—");
      setText("d-profit", e.profit_if_win != null ? sUsd(e.profit_if_win) : "—");
      setText("d-loss", e.loss_if_lose != null ? usd(-e.loss_if_lose) : "—");
      setText("d-fee", d.fee != null && n ? usd(d.fee) : "—");
      setText("d-pwin", d.p_win != null ? pct(d.p_win) : "—");
      setText("d-ev", e.ev != null ? sUsd(e.ev) + ` (${pct(e.ev_per_dollar)})` : "—", cls(e.ev));
      $("checks").innerHTML = Object.entries(d.checks || {}).map(([k, c]) =>
        `<li><span class="${c.ok ? "ok" : "no"}">${c.ok ? "✓" : "✗"}</span><span class="name">${esc(k)}</span><span>${esc(c.detail)}</span></li>`).join("") ||
        (d.reasons || []).map((r) => `<li><span class="no">✗</span><span class="name">reason</span><span>${esc(r)}</span></li>`).join("");
      if (d.reasons && d.reasons.some((r) => /^(risk|revalidate|execution|duplicate|feed|missed)/.test(r)))
        $("checks").innerHTML += d.reasons.filter((r) => /^(risk|revalidate|execution|duplicate|feed|missed)/.test(r)).map((r) => `<li><span class="no">✗</span><span class="name">${esc(r.split(":")[0])}</span><span>${esc(r.split(":").slice(1).join(":"))}</span></li>`).join("");
    } else {
      dec.textContent = m && m.phase === "OBSERVING" ? "OBSERVING…" : "WAITING"; dec.className = "decision decision-wait";
      ["d-price", "d-limit", "d-contracts", "d-payout", "d-profit", "d-loss", "d-fee", "d-pwin", "d-ev"].forEach((i) => setText(i, "—"));
      setText("d-size", usd(s.risk.limits.dollars_per_trade) + " max");
      $("checks").innerHTML = "";
    }

    // stats
    const st = s.stats;
    setPill("perf-mode", s.mode, live ? "bad" : "info");
    setText("s-pnl", sUsd(st.total_pnl), cls(st.total_pnl));
    setText("s-wr", st.win_rate == null ? "—" : pct(st.win_rate) + ` (${st.wins}/${st.trades})`);
    setText("s-trades", st.trades);
    setText("s-today", sUsd(s.risk.realized_today), cls(s.risk.realized_today));
    setText("s-pf", st.profit_factor == null ? "—" : num(st.profit_factor, 2));
    setText("s-dd", usd(st.max_drawdown));
    setText("s-fees", usd(st.fees_paid));
    setText("s-markets", `${st.markets_observed} / ${st.markets_skipped}`);

    // risk
    const r = s.risk, L = r.limits;
    setPill("risk-status", r.can_trade ? "armed" : "blocked", r.can_trade ? "ok" : "bad");
    setText("r-size", usd(L.dollars_per_trade));
    const used = Math.max(0, -r.realized_today);
    setText("r-loss", `${usd(used)} / ${usd(L.max_daily_loss)}`);
    $("loss-bar").style.width = Math.min(100, used / L.max_daily_loss * 100) + "%";
    setText("r-trades", `${r.trades_today} / ${L.max_trades_per_day}`);
    setText("r-consec", `${r.consecutive_losses} / ${L.max_consecutive_losses}`);
    setText("r-exp", usd(r.open_exposure));
    setText("r-kill", r.kill_engaged ? "ENGAGED" : "off", r.kill_engaged ? "neg" : "");
    const blocking = r.blocking.filter((b) => !/max open positions/.test(b) || true);
    $("r-block").textContent = blocking.length ? "Blocking: " + blocking.join(" · ") : "All risk checks clear.";
    $("resume-btn").classList.toggle("hidden", !(r.halted_reason && !r.halted_reason.startsWith("daily")));
    $("unkill-btn").classList.toggle("hidden", !r.kill_engaged);

    // gate
    const gt = s.gate || {};
    setPill("gate-status", gt.allowed ? "passed" : "blocked", gt.allowed ? "ok" : "bad");
    $("gate").innerHTML = (gt.checks || []).map((c) => `<li><span class="${c.ok ? "ok" : "no"}">${c.ok ? "✓" : "✗"}</span><span class="name">${esc(c.name)}</span><span>${esc(c.detail)}</span></li>`).join("");

    // backtest
    const bt = s.backtest;
    if (bt) {
      setPill("bt-src", bt.data_source + (bt.fingerprint_matches ? "" : " · stale params"), bt.fingerprint_matches ? "info" : "warn");
      const a = bt.base.stats, o = bt.base.out_of_sample;
      $("bt-body").innerHTML = `<div class="kv-grid">
        <div><span>Windows</span><b class="mono">${bt.windows}</b></div><div><span>Trades</span><b class="mono">${a.trades}</b></div>
        <div><span>Win rate</span><b class="mono">${pct(a.win_rate)}</b></div><div><span>P&amp;L</span><b class="mono ${cls(a.total_pnl)}">${sUsd(a.total_pnl)}</b></div>
        <div><span>Profit factor</span><b class="mono">${num(a.profit_factor)}</b></div><div><span>Max DD</span><b class="mono">${usd(a.max_drawdown)}</b></div>
        <div><span>OOS trades</span><b class="mono">${o.trades}</b></div><div><span>OOS P&amp;L</span><b class="mono ${cls(o.total_pnl)}">${sUsd(o.total_pnl)}</b></div>
        </div><div class="small muted" style="margin-top:8px">Generated ${dt(bt.generated_at)} · momentum calibration:</div>`;
      table($("calib"), [["|z|", (c) => c.abs_z], ["n", (c) => c.n], ["actual", (c) => pct(c.empirical_continue)], ["random walk", (c) => pct(c.random_walk_pred)], ["model", (c) => pct(c.model_pred)]], bt.calibration, "");
    }

    // positions
    table($("positions"), [
      ["Market", (p) => p.ticker], ["Side", (p) => ({ h: (p.side || "").toUpperCase(), c: "" })], ["Contracts", (p) => p.contracts],
      ["Avg price", (p) => cents(p.avg_price)], ["Cost", (p) => usd(p.cost)], ["Fees", (p) => usd(p.fees)],
      ["Payout if win", (p) => usd(p.potential_payout)], ["Profit if win", (p) => ({ h: sUsd(p.potential_profit), c: "pos" })],
      ["Opened", (p) => tm(p.opened_at)], ["Expires", (p) => tm(p.close_ts)], ["Order", (p) => (p.order_id || "").slice(0, 14)],
    ], s.positions, "No open positions");

    table($("trades"), [
      ["Settled", (t) => dt(t.settled_at)], ["Market", (t) => t.ticker.replace(/^KXBTC15M-/, "")], ["Side", (t) => (t.side || "").toUpperCase()],
      ["Qty", (t) => t.contracts], ["Price", (t) => cents(t.avg_price)], ["Fees", (t) => usd(t.fees)], ["Result", (t) => (t.result || "").toUpperCase()],
      ["", (t) => ({ h: t.won ? "WIN" : "LOSS", c: t.won ? "pos" : "neg" })], ["P&L", (t) => ({ h: sUsd(t.pnl), c: cls(t.pnl) })],
    ], s.trades, "No completed trades yet");

    table($("daily"), [
      ["Date", (d) => d.date], ["Trades", (d) => d.trades], ["Wins", (d) => d.wins], ["Win %", (d) => pct(d.wins / d.trades, 0)],
      ["Fees", (d) => usd(d.fees)], ["P&L", (d) => ({ h: sUsd(d.pnl), c: cls(d.pnl) })],
    ], st.by_day, "No daily history yet");

    table($("markets"), [
      ["Open", (k) => tm(k.open_ts)], ["Market", (k) => (k.ticker || "").replace(/^KXBTC15M-/, "")],
      ["BTC open", (k) => k.btc_open ? usd(k.btc_open, 0) : "—"], ["@3m", (k) => k.btc_at_decision ? usd(k.btc_at_decision, 0) : "—"],
      ["Δ%", (k) => ({ h: k.pct_change == null ? "—" : num(k.pct_change, 3, true), c: cls(k.pct_change) })],
      ["Dir", (k) => k.direction || "—"], ["Conf", (k) => k.confidence == null ? "—" : k.confidence.toFixed(0)],
      ["z", (k) => num(k.z_score, 2, true)], ["Vol", (k) => num(k.volatility, 1)],
      ["Decision", (k) => ({ h: esc(k.decision || "…"), c: /BUY/.test(k.decision || "") ? "pos" : "" })],
      ["Ask", (k) => cents(k.entry_ask)], ["Fill", (k) => cents(k.exec_price)],
      ["Outcome", (k) => k.outcome ? (k.up_won ? "UP" : "DOWN") : "…"],
      ["P&L", (k) => k.pnl != null ? { h: sUsd(k.pnl), c: cls(k.pnl) } : (k.shadow_pnl != null ? { h: "shadow " + num(k.shadow_pnl, 2, true), c: "muted" } : "—")],
      ["Why skipped", (k) => ({ h: esc((k.skip_reasons || "").split(" | ").slice(0, 2).join(" · ")), c: "wrap" })],
    ], s.markets, "No markets recorded yet");

    $("logs").innerHTML = (s.logs || []).map((l) => `<li><span class="muted mono">${tm(l.ts)}</span><span class="lvl lvl-${esc(l.level)}">${esc(l.level)}</span><span class="msg">${l.ticker ? `<span class="muted mono">${esc(l.ticker.replace(/^KXBTC15M-/, ""))}</span> ` : ""}${esc(l.message)}</span></li>`).join("");

    const sr = st.skip_reasons || {}; const max = Math.max(1, ...Object.values(sr));
    $("skip-reasons").innerHTML = Object.keys(sr).length ? Object.entries(sr).slice(0, 12).map(([k, v]) =>
      `<div class="bar-row"><span>${esc(k)}</span><div class="bar-track"><div class="bar-fill" style="width:${v / max * 100}%"></div></div><span class="mono">${v}</span></div>`).join("")
      + `<div class="small muted">Shadow results of skipped signals: ${st.shadow_skipped.n} markets, ${st.shadow_skipped.wins} would have won, ${sUsd(st.shadow_skipped.pnl_per_contract_sum)} per contract total.</div>`
      : `<div class="empty">No skips yet</div>`;

    renderTimers(); drawChart(); drawEquity();
  }

  // ---------------------------------------------------------------- data
  function onState(data) { S = data; clockOffset = S.server_time - Date.now() / 1000; render(); }

  function connect() {
    const proto = location.protocol === "https:" ? "wss" : "ws";
    const ws = new WebSocket(`${proto}://${location.host}/ws`);
    ws.onmessage = (e) => { try { onState(JSON.parse(e.data)); } catch (err) { console.error(err); } };
    ws.onclose = () => { setPill("feed-status", "reconnecting", "warn"); setTimeout(connect, 2000); };
    ws.onerror = () => ws.close();
  }

  async function post(path, confirmMsg) {
    if (confirmMsg && !confirm(confirmMsg)) return;
    const headers = {}; const tok = localStorage.getItem("dashboardToken"); if (tok) headers["X-Dashboard-Token"] = tok;
    let r = await fetch(path, { method: "POST", headers });
    if (r.status === 401) {
      const t = prompt("Dashboard token:"); if (!t) return;
      try { localStorage.setItem("dashboardToken", t); } catch (e) { /* ignore */ }
      r = await fetch(path, { method: "POST", headers: { "X-Dashboard-Token": t } });
    }
    if (!r.ok) alert("Request failed: " + (await r.text()));
  }

  $("kill-btn").onclick = () => { if (S && S.risk.kill_engaged) return; post("/api/kill", "Engage the kill switch? No new orders will be placed until you clear it."); };
  $("unkill-btn").onclick = () => post("/api/kill/clear", "Clear the kill switch and allow trading again?");
  $("resume-btn").onclick = () => post("/api/risk/resume", "Resume trading after the consecutive-loss halt? Position size will NOT change.");
  window.addEventListener("resize", () => { drawChart(); drawEquity(); });
  setInterval(renderTimers, 250);
  connect();
})();

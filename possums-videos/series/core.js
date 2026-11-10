// Shared engine for the daily "worst team in America" series.
// An episode.html loads this file, then defines TEAM (config), drawStadium(t, o), and extra SCENES.
const W = 1080, H = 1920;
const cv = document.getElementById('c');
const ctx = cv.getContext('2d');
let TL = null;
const FONT = 'Inter';

// ---------------------------------------------------------------- helpers
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, k) => a + (b - a) * k;
const seg = (u, a, b) => clamp((u - a) / (b - a));
const eOut = k => 1 - Math.pow(1 - k, 3);
const eIn = k => k * k * k;
const eBack = k => { const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(k - 1, 3) + c1 * Math.pow(k - 1, 2); };
const eInOut = k => k < .5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2;
function rng(seed) { let s = seed >>> 0; return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296); }
const C = { ink: '#1b1b2f', cream: '#fff6e3', red: '#ff4a4a', yellow: '#ffd43b', white: '#ffffff', green: '#1f9d55', sky2: '#d7f1ff', grass: '#4cae4f' };

function rr(x, y, w, h, r) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); }
function txt(s, x, y, size, color = C.white, opts = {}) {
  ctx.save();
  ctx.font = `${opts.weight || 900} ${size}px ${FONT}`;
  ctx.textAlign = opts.align || 'center'; ctx.textBaseline = 'middle';
  if (opts.stroke) { ctx.lineJoin = 'round'; ctx.lineWidth = opts.stroke; ctx.strokeStyle = opts.strokeColor || C.ink; ctx.strokeText(s, x, y); }
  ctx.fillStyle = color; ctx.fillText(s, x, y);
  ctx.restore();
}
function withT(x, y, sc, rot, fn) { ctx.save(); ctx.translate(x, y); ctx.rotate(rot || 0); ctx.scale(sc, sc); fn(); ctx.restore(); }
function shadowOn(b = 18, oy = 10) { ctx.shadowColor = 'rgba(0,0,0,.28)'; ctx.shadowBlur = b; ctx.shadowOffsetY = oy; }
function dim(a) { ctx.fillStyle = `rgba(16,18,40,${a})`; ctx.fillRect(0, 0, W, H); }
function sceneLine(name) { return TL.lines.find(l => l.scene === name); }
function wordP(name, key) { const L = sceneLine(name); key = key.toLowerCase();
  const w = L.words.find(w => w.w.toLowerCase().replace(/[^a-z0-9]/g, '').startsWith(key)); return w ? (w.s - L.start) / (L.end - L.start) : 1; }

// ---------------------------------------------------------------- characters
// feet at (0,0), ~340px tall at scale 1. o.extra(hy, by) draws accessories in player space.
function drawPlayer(x, y, s, o = {}) {
  const jersey = o.jersey || TEAM.c1, trim = o.trim || TEAM.c2, skin = o.skin || '#e0ac69';
  const wide = o.wide || 1, run = o.run || 0, flip = o.flip ? -1 : 1, tall = o.tall || 1;
  ctx.save(); ctx.translate(x, y); ctx.scale(s * flip, s);
  if (o.rot) ctx.rotate(o.rot);
  ctx.fillStyle = 'rgba(0,0,0,.18)'; ctx.beginPath(); ctx.ellipse(0, 4, 70 * wide, 14, 0, 0, 7); ctx.fill();
  const lg = Math.sin(run) * 28, crouch = o.crouch || 0, legH = 88 * tall;
  for (const side of [-1, 1]) {
    ctx.save(); ctx.translate(side * 20 * wide, -2 - legH + crouch * 20); ctx.rotate(side * -lg * .02);
    ctx.fillStyle = o.legColor || '#f5f5f5'; rr(-17, 0, 34, legH - crouch * 18, 14); ctx.fill();
    if (o.socks) { ctx.fillStyle = o.socks; rr(-17, legH * .45, 34, legH * .45 - crouch * 18, 10); ctx.fill(); }
    ctx.fillStyle = o.shoes || C.ink; rr(-20, legH - 18 - crouch * 18, 44, 22, 10); ctx.fill(); ctx.restore();
  }
  const by = -112 - legH + crouch * 40;
  if (o.shorts) { ctx.fillStyle = o.shorts; rr(-58 * wide, by + 90, 116 * wide, 46, 14); ctx.fill(); }
  ctx.fillStyle = jersey; rr(-62 * wide, by, 124 * wide, 120, 30); ctx.fill();
  ctx.fillStyle = trim; ctx.fillRect(-62 * wide, by + 92, 124 * wide, 10);
  if (o.pads !== false) { ctx.fillStyle = jersey; ctx.beginPath(); ctx.ellipse(-62 * wide, by + 18, 30, 24, -.4, 0, 7); ctx.ellipse(62 * wide, by + 18, 30, 24, .4, 0, 7); ctx.fill(); }
  if (o.num !== undefined) { ctx.save(); ctx.scale(flip, 1); txt(String(o.num), 0, by + 54, 56, '#fff', { stroke: 6, strokeColor: trim }); ctx.restore(); }
  ctx.strokeStyle = skin; ctx.lineWidth = 22; ctx.lineCap = 'round';
  const armL = o.armsUp ? -2.4 : (o.armL ?? 0.35 + Math.sin(run) * .5), armR = o.armsUp ? 2.4 : (o.armR ?? -0.35 - Math.sin(run) * .5);
  const hL = [-66 * wide + Math.sin(armL) * -70, by + 30 + Math.cos(armL) * 70], hR = [66 * wide + Math.sin(armR) * -70, by + 30 + Math.cos(armR) * 70];
  ctx.beginPath(); ctx.moveTo(-66 * wide, by + 30); ctx.lineTo(...hL); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(66 * wide, by + 30); ctx.lineTo(...hR); ctx.stroke();
  if (o.gloves) { ctx.fillStyle = o.gloves; for (const h of [hL, hR]) { ctx.beginPath(); ctx.arc(h[0], h[1], 20, 0, 7); ctx.fill(); } }
  const hy = by - 58;
  ctx.fillStyle = skin; ctx.beginPath(); ctx.arc(0, hy, 60, 0, 7); ctx.fill();
  const face = o.face || 'happy', eyeR = face === 'scared' ? 17 : 13;
  ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.arc(-22, hy - 6, eyeR, 0, 7); ctx.arc(22, hy - 6, eyeR, 0, 7); ctx.fill();
  ctx.fillStyle = C.ink;
  if (face === 'sleepy' || face === 'sad') { ctx.fillRect(-34, hy - 6, 24, 5); ctx.fillRect(10, hy - 6, 24, 5); }
  else { const pr = face === 'scared' ? 6 : 7; ctx.beginPath(); ctx.arc(-19, hy - 4, pr, 0, 7); ctx.arc(25, hy - 4, pr, 0, 7); ctx.fill(); }
  ctx.strokeStyle = C.ink; ctx.lineWidth = 6; ctx.beginPath();
  if (face === 'scared') { ctx.fillStyle = '#5a1a1a'; ctx.ellipse(0, hy + 30, 16, 20, 0, 0, 7); ctx.fill(); }
  else if (face === 'sad') { ctx.arc(0, hy + 40, 16, Math.PI * 1.15, Math.PI * 1.85); ctx.stroke(); }
  else if (face === 'sneeze') { ctx.fillStyle = '#5a1a1a'; ctx.ellipse(0, hy + 28, 22, 14, 0, 0, 7); ctx.fill(); }
  else { ctx.arc(0, hy + 14, 22, .2, Math.PI - .2); ctx.stroke(); }
  if (o.mustache) { ctx.fillStyle = o.mustache === true ? '#6b4a2b' : o.mustache; ctx.beginPath(); ctx.ellipse(-14, hy + 16, 18, 8, .2, 0, 7); ctx.ellipse(14, hy + 16, 18, 8, -.2, 0, 7); ctx.fill(); }
  if (o.glasses) { ctx.strokeStyle = C.ink; ctx.lineWidth = 4; ctx.beginPath(); ctx.arc(-22, hy - 6, 17, 0, 7); ctx.moveTo(39, hy - 6); ctx.arc(22, hy - 6, 17, 0, 7); ctx.moveTo(-5, hy - 6); ctx.lineTo(5, hy - 6); ctx.stroke(); }
  if (o.cap) { ctx.fillStyle = o.cap; ctx.beginPath(); ctx.arc(0, hy - 18, 58, Math.PI, 0); ctx.fill(); rr(0, hy - 26, 80, 14, 7); ctx.fill(); }
  else if (o.hair) { ctx.fillStyle = o.hair; ctx.beginPath(); ctx.arc(0, hy - 14, 60, Math.PI * 1.05, Math.PI * 1.95); ctx.fill(); }
  if (o.extra) o.extra(hy, by);
  if (o.sweat) { ctx.fillStyle = '#9fe0ff'; ctx.beginPath(); ctx.arc(54, hy - 30, 9, 0, 7); ctx.fill(); ctx.beginPath(); ctx.arc(-58, hy - 10, 7, 0, 7); ctx.fill(); }
  ctx.restore();
}
function drawCoach(x, y, s, t, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  const bounce = Math.abs(Math.sin(t * 7)) * 14 * (o.bounce ?? 1);
  ctx.translate(0, -bounce);
  ctx.fillStyle = 'rgba(0,0,0,.18)'; ctx.beginPath(); ctx.ellipse(0, bounce + 4, 80, 14, 0, 0, 7); ctx.fill();
  ctx.fillStyle = '#2d3a5a'; rr(-48, -110, 40, 112, 14); ctx.fill(); rr(8, -110, 40, 112, 14); ctx.fill();
  ctx.fillStyle = TEAM.c2; rr(-75, -270, 150, 170, 40); ctx.fill();
  ctx.fillStyle = TEAM.c1; ctx.fillRect(-75, -150, 150, 14);
  txt('COACH', 0, -195, 30, '#fff', { stroke: 5, strokeColor: TEAM.c1 });
  ctx.strokeStyle = '#ffdbac'; ctx.lineWidth = 24; ctx.lineCap = 'round';
  const wave = Math.sin(t * 10) * .35, up = o.armsUp ?? 1;
  ctx.beginPath(); ctx.moveTo(-72, -245); ctx.lineTo(-142, -245 - 80 * up + wave * 40); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(72, -245); ctx.lineTo(142, -245 - 80 * up - wave * 40); ctx.stroke();
  ctx.strokeStyle = '#ddd'; ctx.lineWidth = 4; ctx.beginPath(); ctx.moveTo(-30, -268); ctx.lineTo(0, -238); ctx.lineTo(30, -268); ctx.stroke();
  ctx.fillStyle = '#c0c0c0'; rr(-12, -244, 24, 14, 5); ctx.fill();
  const hy = -330;
  ctx.fillStyle = '#ffdbac'; ctx.beginPath(); ctx.arc(0, hy, 68, 0, 7); ctx.fill();
  ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.arc(-24, hy - 6, 15, 0, 7); ctx.arc(24, hy - 6, 15, 0, 7); ctx.fill();
  ctx.fillStyle = C.ink; ctx.beginPath(); ctx.arc(-20, hy - 4, 7, 0, 7); ctx.arc(28, hy - 4, 7, 0, 7); ctx.fill();
  ctx.fillStyle = '#5a1a1a'; ctx.beginPath(); ctx.arc(0, hy + 20, 26, 0, Math.PI); ctx.fill();
  ctx.fillStyle = '#fff'; ctx.fillRect(-18, hy + 20, 36, 8);
  ctx.fillStyle = '#c96'; ctx.beginPath(); ctx.ellipse(0, hy + 10, 30, 8, 0, Math.PI, 0); ctx.fill();
  ctx.fillStyle = TEAM.c1; ctx.beginPath(); ctx.arc(0, hy - 22, 66, Math.PI, 0); ctx.fill(); rr(-10, hy - 30, 100, 16, 8); ctx.fill();
  ctx.fillStyle = TEAM.c2; ctx.beginPath(); ctx.arc(0, hy - 60, 14, 0, 7); ctx.fill();
  ctx.restore();
}

// ---------------------------------------------------------------- UI pieces
function card(x, y, w, h, k, color = C.cream) {
  const s = eBack(clamp(k)); ctx.save(); ctx.translate(x + w / 2, y + h / 2); ctx.scale(s, s); ctx.translate(-w / 2, -h / 2);
  shadowOn(30, 16); ctx.fillStyle = color; rr(0, 0, w, h, 40); ctx.fill(); ctx.shadowColor = 'transparent';
  ctx.strokeStyle = C.ink; ctx.lineWidth = 8; ctx.stroke();
}
function endCard() { ctx.restore(); }
function bubble(x, y, s, label, k, color = '#fff') {
  if (k <= 0) return; const sc = eBack(clamp(k)) * s;
  withT(x, y, sc, -.06, () => { shadowOn(10, 6); ctx.fillStyle = color; ctx.beginPath(); ctx.ellipse(0, 0, 190, 90, 0, 0, 7); ctx.fill(); ctx.shadowColor = 'transparent';
    ctx.strokeStyle = C.ink; ctx.lineWidth = 7; ctx.stroke(); ctx.beginPath(); ctx.moveTo(-60, 70); ctx.lineTo(-90, 140); ctx.lineTo(-10, 82); ctx.fillStyle = color; ctx.fill();
    txt(label, 0, 0, label.length > 7 ? 48 : 62, C.ink); });
}
function stamp(label, x, y, size, k, color = C.yellow, rot = -.08) {
  if (k <= 0) return; const s = k < 1 ? lerp(2.6, 1, eOut(k)) : 1;
  ctx.save(); ctx.globalAlpha = clamp(k * 3); withT(x, y, s, rot, () => txt(label, 0, 0, size, color, { stroke: size * .16 })); ctx.restore();
}
function callout(label, lx, ly, tx, ty, k, col = C.red) {
  if (k <= 0) return; const e = eBack(clamp(k));
  ctx.strokeStyle = '#fff'; ctx.lineWidth = 8; ctx.setLineDash([16, 12]); ctx.beginPath(); ctx.moveTo(lx, ly); ctx.lineTo(lerp(lx, tx, clamp(k * 1.5)), lerp(ly, ty, clamp(k * 1.5))); ctx.stroke(); ctx.setLineDash([]);
  ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.arc(tx, ty, 14 * clamp(k * 2), 0, 7); ctx.fill();
  withT(lx, ly, e, -.04, () => { ctx.font = `900 46px ${FONT}`; const w = ctx.measureText(label).width + 60; shadowOn(12, 6); ctx.fillStyle = '#fff'; rr(-w / 2, -45, w, 90, 22); ctx.fill(); ctx.shadowColor = 'transparent'; ctx.strokeStyle = C.ink; ctx.lineWidth = 6; ctx.stroke(); txt(label, 0, 2, 46, col); });
}
// home/away: {abbr, score, color}; l1/l2 small text (period, clock); extra right text
function scorebug(home, away, l1, l2, extra) {
  shadowOn(14, 8); ctx.fillStyle = C.ink; rr(90, 210, 900, 120, 26); ctx.fill(); ctx.shadowColor = 'transparent';
  ctx.fillStyle = TEAM.c1; rr(100, 220, 250, 100, 18); ctx.fill();
  ctx.fillStyle = TEAM.opp.c1; rr(470, 220, 250, 100, 18); ctx.fill();
  txt(TEAM.abbr, 175, 270, 44, '#fff'); txt(String(home), 300, 270, 60, C.yellow);
  txt(TEAM.opp.abbr, 545, 270, 44, '#fff'); txt(String(away), 670, 270, 60, C.yellow);
  txt(l1, 790, 248, 32, '#fff', { weight: 800 }); txt(l2, 790, 292, 32, C.yellow, { weight: 800 });
  txt(extra || '', 915, 270, 28, '#fff', { weight: 800 });
}
function confetti(t0, t, n = 90) {
  const r = rng(99); const dt = t - t0; if (dt < 0) return;
  const cols = [TEAM.c1, TEAM.c2, C.yellow, '#fff', C.red];
  for (let i = 0; i < n; i++) { const x0 = r() * W, vy = 380 + r() * 400, sw = r() * 6.28, c = cols[(r() * 5) | 0];
    const y = -40 + dt * vy, x = x0 + Math.sin(dt * 4 + sw) * 50; if (y > H) continue;
    ctx.save(); ctx.translate(x, y); ctx.rotate(dt * 6 + sw); ctx.fillStyle = c; ctx.fillRect(-10, -6, 20, 12); ctx.restore(); }
}
function heart(x, y, s) { ctx.save(); ctx.translate(x, y); ctx.scale(s / 30, s / 30); ctx.fillStyle = C.red; ctx.beginPath(); ctx.moveTo(0, 10); ctx.bezierCurveTo(-30, -14, -14, -36, 0, -18); ctx.bezierCurveTo(14, -36, 30, -14, 0, 10); ctx.fill(); ctx.restore(); }
function thumb() {
  shadowOn(20, 10); ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.arc(0, 0, 230, 0, 7); ctx.fill(); ctx.shadowColor = 'transparent';
  ctx.strokeStyle = C.ink; ctx.lineWidth = 10; ctx.stroke();
  ctx.fillStyle = '#3b82f6'; rr(-130, -20, 70, 150, 14); ctx.fill();
  ctx.beginPath(); ctx.moveTo(-50, -20); ctx.lineTo(-10, -150); ctx.quadraticCurveTo(30, -170, 30, -110); ctx.lineTo(20, -40); ctx.lineTo(120, -40); ctx.quadraticCurveTo(150, -30, 135, 10); ctx.lineTo(110, 120); ctx.quadraticCurveTo(100, 140, 70, 140); ctx.lineTo(-50, 140); ctx.closePath(); ctx.fill();
}

// ---------------------------------------------------------------- HUD (day + fund)
// TEAM.fund = {start, profileScene, spendScene, spendAt (0-1 of line)}
function fundAt(t) {
  const F = TEAM.fund, L = sceneLine(F.profileScene), S = sceneLine(F.spendScene);
  if (!L || t < L.start) return null;
  const tc = L.start + .8 * (L.end - L.start);
  let v = Math.round(F.start * eOut(seg(t, tc - .5, tc + .2)));
  if (S) { const a = S.start + (F.spendAt ?? .3) * (S.end - S.start); if (t > a) v = Math.max(0, F.start - Math.round(F.start * seg(t, a, a + .6))); }
  return v;
}
function hud(t) {
  ctx.save(); shadowOn(10, 6); ctx.fillStyle = TEAM.c2; rr(40, 60, 230, 96, 26); ctx.fill(); ctx.shadowColor = 'transparent';
  ctx.strokeStyle = C.ink; ctx.lineWidth = 6; ctx.stroke(); ctx.restore();
  txt('DAY ' + TEAM.day, 155, 108, 56, '#fff', { stroke: 8 });
  const f = fundAt(t);
  if (f !== null) {
    ctx.save(); shadowOn(10, 6); ctx.fillStyle = '#fff'; rr(610, 60, 430, 96, 26); ctx.fill(); ctx.shadowColor = 'transparent';
    ctx.strokeStyle = C.ink; ctx.lineWidth = 6; ctx.stroke(); ctx.restore();
    txt('TEAM FUND', 760, 108, 34, C.ink, { weight: 800 });
    txt('$' + f, 960, 108, 54, f > 0 ? C.green : C.red);
  }
}

// ---------------------------------------------------------------- captions
function captions(t) {
  const L = TL.lines.find(l => t >= l.start - .05 && t <= l.end + .15); if (!L) return;
  const ws = L.words; let ci = ws.findIndex((w, i) => t >= w.s && (i === ws.length - 1 || t < ws[i + 1].s)); if (ci < 0) ci = 0;
  const CH = 3; const c0 = Math.floor(ci / CH) * CH; const chunk = ws.slice(c0, c0 + CH);
  ctx.save(); ctx.font = `900 84px ${FONT}`;
  const parts = chunk.map(w => w.w.toUpperCase()); const sp = 22;
  const widths = parts.map(p => ctx.measureText(p).width); const total = widths.reduce((a, b) => a + b, 0) + sp * (parts.length - 1);
  const fit = Math.min(1, 960 / total);
  let x = W / 2 - total * fit / 2; const y = 1640;
  parts.forEach((p, i) => { const active = c0 + i === ci; const k = active ? eBack(clamp((t - ws[c0 + i].s) / .12)) : 1;
    withT(x + widths[i] * fit / 2, y, (active ? lerp(.8, 1.08, k) : 1) * fit, 0, () => txt(p, 0, 0, 84, active ? C.yellow : '#fff', { stroke: 16 }));
    x += (widths[i] + sp) * fit; });
  ctx.restore();
}

// ---------------------------------------------------------------- shared scenes
// roster card: d = {name, pos, stat, val, num, small, o (drawPlayer opts), prop(fn)}
function roster(t, u, p, d) {
  drawStadium(t); dim(.4);
  const k = eOut(seg(u, 0, .3)); const x = lerp(W + 600, W / 2, k);
  withT(x, 900, 1, -.04 + (1 - k) * .3, () => {
    shadowOn(30, 16); ctx.fillStyle = C.yellow; rr(-380, -560, 760, 1060, 40); ctx.fill(); ctx.shadowColor = 'transparent';
    ctx.strokeStyle = C.ink; ctx.lineWidth = 10; ctx.stroke();
    ctx.fillStyle = C.sky2; rr(-340, -520, 680, 640, 26); ctx.fill();
    ctx.fillStyle = TEAM.cardGround || C.grass; ctx.fillRect(-340, 0, 680, 120);
    if (d.prop) d.prop(t, p);
    drawPlayer(d.px || 0, 100, d.small ? .9 : 1.25, { num: d.num, ...d.o });
    ctx.fillStyle = C.ink; rr(-340, 140, 680, 120, 20); ctx.fill();
    txt(d.name, 0, 200, 86, '#fff');
    txt(d.pos, 0, 305, 50, TEAM.c1);
    const sk = seg(p, .35, .5);
    ctx.save(); ctx.globalAlpha = sk;
    ctx.fillStyle = '#fff'; rr(-330, 350, 660, 120, 24); ctx.fill(); ctx.strokeStyle = C.ink; ctx.lineWidth = 6; ctx.stroke();
    txt(d.stat, -310, 410, 44, C.ink, { align: 'left', weight: 800 }); txt(d.val, 310, 410, d.val.length > 8 ? 46 : 60, C.red, { align: 'right' });
    ctx.restore();
  });
  txt('NEW SIGNING', W / 2, 270, 70, '#fff', { stroke: 10 });
}
function versus(u, p, opp, top, sub, rec) {
  const k = eOut(seg(u, 0, .4));
  ctx.fillStyle = C.ink; ctx.fillRect(0, 0, W, H);
  ctx.fillStyle = TEAM.c1; ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(lerp(-600, 640, k), 0); ctx.lineTo(lerp(-800, 440, k), H); ctx.lineTo(0, H); ctx.fill();
  ctx.fillStyle = opp.c1; ctx.beginPath(); ctx.moveTo(W, 0); ctx.lineTo(lerp(W + 800, 640, k), 0); ctx.lineTo(lerp(W + 600, 440, k), H); ctx.lineTo(W, H); ctx.fill();
  ctx.strokeStyle = C.yellow; ctx.lineWidth = 16; ctx.beginPath(); ctx.moveTo(640, 0); ctx.lineTo(440, H); ctx.stroke();
  ctx.globalAlpha = k;
  TEAM.logo(300, 620, 170); txt(TEAM.town.toUpperCase(), 300, 860, TEAM.town.length > 10 ? 58 : 70, '#fff', { stroke: 10 }); txt(rec || TEAM.name.toUpperCase(), 300, 945, 70, rec ? C.red : TEAM.c2, { stroke: 10 });
  opp.logo(780, 1050, 170); txt(opp.town.toUpperCase(), 780, 1290, opp.town.length > 10 ? 58 : 70, '#fff', { stroke: 10 }); txt(opp.name.toUpperCase(), 780, 1370, 70, opp.c2, { stroke: 10 });
  ctx.globalAlpha = 1;
  stamp(top, 540, 330, 110, seg(u, .3, .5), '#fff', 0);
  stamp('VS', 540, 1000, 200, seg(u, .4, .65), C.yellow, -.12);
  if (sub) stamp(sub, 540, 1480, Math.min(74, 1120 / sub.length), seg(p, .72, .82), C.red, -.05);
}
const SCENES = {
  intro(t, u, p) {
    drawStadium(t);
    drawCoach(W / 2, 1420, 1.25, t);
    stamp('DAY ' + TEAM.day, W / 2, 560, 230, seg(u, 0, .35), C.yellow, -.1);
    const k = seg(u, .9, 1.3);
    if (k > 0) withT(W / 2, 830, eBack(k), .04, () => { shadowOn(16, 8); ctx.fillStyle = C.red; rr(-430, -60, 860, 120, 20); ctx.fill(); ctx.shadowColor = 'transparent';
      txt('WORST TEAM IN AMERICA', 0, 2, 60, '#fff', { stroke: 8 }); });
  },
  profile(t, u, p) {
    drawStadium(t); dim(.35);
    card(90, 300, 900, 1100, seg(u, 0, .35));
    TEAM.logo(450, 230, 140);
    txt(TEAM.full, 450, 450, TEAM.full.length > 18 ? 62 : 72, C.ink); txt(TEAM.handle, 450, 530, 40, '#666', { weight: 700 });
    [['FANS', '0'], ['WINS', '0'], ['LOSSES', '0']].forEach(([a, b], i) => { const x = 150 + i * 300, kk = seg(p, .25 + i * .1, .4 + i * .1);
      ctx.save(); ctx.globalAlpha = kk; txt(b, x, 680, 110, TEAM.c1); txt(a, x, 770, 38, C.ink, { weight: 800 }); ctx.restore(); });
    const kk = seg(p, .6, .75); ctx.save(); ctx.globalAlpha = kk;
    ctx.fillStyle = '#e8f8ee'; rr(70, 860, 760, 170, 30); ctx.fill(); ctx.strokeStyle = C.green; ctx.lineWidth = 6; ctx.stroke();
    txt('TEAM FUND', 450, 910, 44, C.ink, { weight: 800 }); txt('$' + Math.round(TEAM.fund.start * eOut(seg(p, .7, .85))), 450, 985, 86, C.green);
    ctx.restore(); endCard();
  },
  likes(t, u, p) {
    drawStadium(t); dim(.35);
    const r = rng(5);
    for (let i = 0; i < 14; i++) { const x = 120 + r() * 840, sp = 160 + r() * 140, ph = r(); const y = 1500 - ((u * sp + ph * 900) % 900);
      ctx.save(); ctx.globalAlpha = .85; heart(x, y, 26 + r() * 20); ctx.restore(); }
    const pulse = 1 + Math.sin(t * 12) * .05;
    withT(W / 2, 760, eBack(seg(u, 0, .35)) * pulse, 0, () => thumb());
    const k2 = seg(p, .35, .5);
    if (k2 > 0) withT(W / 2, 1170, eBack(k2), -.05, () => { shadowOn(16, 8); ctx.fillStyle = C.green; rr(-420, -90, 840, 180, 30); ctx.fill(); ctx.shadowColor = 'transparent';
      ctx.strokeStyle = C.ink; ctx.lineWidth = 8; ctx.stroke(); txt('1 LIKE = +$1', 0, 4, 110, '#fff', { stroke: 10 }); });
    const k3 = seg(p, wordP('likes', 'video') - .02, wordP('likes', 'video') + .08);
    if (k3 > 0) withT(W / 2, 1360, eBack(k3), .03, () => { shadowOn(12, 6); ctx.fillStyle = C.ink; rr(-400, -60, 800, 120, 60); ctx.fill(); ctx.shadowColor = 'transparent';
      txt('ON THIS VIDEO', 0, 3, 62, '#fff'); });
  },
  matchcard(t, u, p) { versus(u, p, TEAM.opp, 'GAME ' + TEAM.day, null); },
  nextgame(t, u, p) { versus(u, p, TEAM.next, 'TOMORROW', TEAM.next.brag, TEAM.record); },
  standings(t, u, p) {
    drawStadium(t); dim(.45);
    card(70, 260, 940, 1180, seg(u, 0, .35), '#fff');
    txt('LEAGUE TABLE', 470, 90, 64, C.ink);
    const rows = TEAM.table;
    txt('TEAM', 90, 170, 30, '#888', { align: 'left', weight: 800 }); txt('W-L', 800, 170, 30, '#888', { weight: 800 });
    rows.forEach(([n, wl], i) => { const y = 240 + i * 110; const last = i === rows.length - 1; const kk = seg(p, .1 + i * .04, .2 + i * .04);
      ctx.save(); ctx.globalAlpha = kk;
      ctx.translate(last ? Math.sin(t * 40) * 6 * seg(p, .55, .6) * (1 - seg(p, .8, .9)) : 0, 0);
      if (last) { ctx.fillStyle = '#ffe3e3'; rr(30, y - 46, 880, 92, 18); ctx.fill(); ctx.strokeStyle = C.red; ctx.lineWidth = 6; ctx.stroke(); }
      txt(String(i + 1), 70, y, 42, last ? C.red : C.ink); txt(n, 120, y, 42, last ? C.red : C.ink, { align: 'left', weight: last ? 900 : 700 }); txt(wl, 800, y, 42, last ? C.red : C.ink);
      ctx.restore(); });
    txt(TEAM.finalText, 470, 1110, 46, C.ink);
    endCard();
  },
  cta(t, u, p) {
    drawStadium(t, { excite: .2 }); dim(.45);
    withT(W / 2, 330, eBack(seg(u, 0, .3)), -.04, () => { shadowOn(16, 8); ctx.fillStyle = C.green; rr(-420, -85, 840, 170, 30); ctx.fill(); ctx.shadowColor = 'transparent';
      ctx.strokeStyle = C.ink; ctx.lineWidth = 8; ctx.stroke(); txt('1 LIKE = +$1', 0, -22, 76, '#fff', { stroke: 8 }); txt('ON THIS VIDEO', 0, 50, 40, C.yellow, { stroke: 6 }); });
    const k2 = seg(p, wordP('cta', 'most') - .05, wordP('cta', 'most') + .05);
    if (k2 > 0) withT(W / 2, 930, eBack(k2), 0, () => {
      shadowOn(20, 10); ctx.fillStyle = C.cream; rr(-430, -470, 860, 900, 40); ctx.fill(); ctx.shadowColor = 'transparent'; ctx.strokeStyle = C.ink; ctx.lineWidth = 8; ctx.stroke();
      txt('UPGRADE SHOP', 0, -395, 72, C.ink);
      // TEAM.shop: [name, joke, price, spoken key or null]
      const items = TEAM.shop.map(([n, sub, pr, key]) => [n, sub, pr, key ? wordP('cta', key) : 9]);
      items.forEach(([n, sub, pr, at], i) => { const y = -280 + i * 140; const nextAt = items.slice(i + 1).map(x => x[3]).find(a => a < 9);
        const on = at < 9 && p >= at - .01 && (nextAt === undefined || p < nextAt - .01);
        ctx.fillStyle = on ? C.yellow : '#fff'; rr(-390, y - 58, 780, 116, 24); ctx.fill(); ctx.strokeStyle = C.ink; ctx.lineWidth = 5; ctx.stroke();
        txt(n, -360, y - 14, 50, C.ink, { align: 'left' }); txt(sub, -360, y + 30, 30, '#666', { align: 'left', weight: 600 }); txt(pr, 360, y, 54, C.green, { align: 'right' }); });
    });
    const k3 = seg(p, .88, .98);
    if (k3 > 0) { const yb = Math.sin(t * 8) * 14; withT(W / 2, 1490 + yb, eBack(k3), -.03, () => { txt('MOST-LIKED COMMENT WINS', 0, 0, 64, C.yellow, { stroke: 12 }); txt('COMMENT BELOW', 0, 70, 40, '#fff', { stroke: 8 }); }); }
  },
};

// ---------------------------------------------------------------- frame
window.renderFrame = function (t) {
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.clearRect(0, 0, W, H); ctx.globalAlpha = 1;
  let L = TL.lines[0];
  for (const l of TL.lines) if (t >= l.start - .02) L = l;
  const u = t - L.start, p = clamp(u / (L.end - L.start));
  ctx.save(); SCENES[L.scene](t, u, p); ctx.restore();
  const cut = clamp(1 - u / .12); if (cut > 0 && L !== TL.lines[0]) { ctx.fillStyle = `rgba(255,255,255,${cut * .5})`; ctx.fillRect(0, 0, W, H); }
  if (L.scene !== 'matchcard' && L.scene !== 'nextgame') hud(t);
  captions(t);
  const last = TL.lines[TL.lines.length - 1];
  if (t > last.end + .2) { const k = seg(t, last.end + .2, last.end + .6); withT(W / 2, 1690, eBack(k), 0, () => { ctx.fillStyle = TEAM.c2; rr(-360, -70, 720, 140, 30); ctx.fill(); ctx.strokeStyle = C.ink; ctx.lineWidth = 8; ctx.stroke(); txt('FOLLOW FOR DAY ' + (TEAM.day + 1), 0, 4, 60, '#fff', { stroke: 8 }); }); }
};
window.setTimeline = tl => { TL = tl; };

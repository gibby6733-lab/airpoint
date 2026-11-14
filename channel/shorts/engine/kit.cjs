// Shared shot helpers for scene files.
const C = require('./core.cjs');
const { W, H, g, clamp, ease, lerp, line, rect, circle, ell, vgrad, rgrad, glow, fig, P } = C;
const sh = (at, draw, o = {}) => ({ at, draw, ...o });
const HERO = (vest, extra = {}) => ({ kind: 'hero', headlamp: true, vest, ...extra });
// big centered word (counting beats etc.)
function bigWord(txt, y = 760, size = 260, col = '#ffffff', T = 0, start = 0) {
  const age = T - start; const s = 1 + 0.25 * Math.max(0, 1 - age / 0.15);
  g.save(); g.translate(W / 2, y); g.scale(s, s); C.textBox(txt, 0, 0, size, col, '#000', 26, 'Anton', 'center', 1000); g.restore();
}
// generic dark background with gradient
function darkBG(top = '#0b0f1a', bot = '#020305') { g.fillStyle = vgrad(0, H, [[0, top], [1, bot]]); g.fillRect(-300, -300, W + 600, H + 600); }
// door
function door(x, y, w, h, col = '#4a4038', open = 0, label) {
  rect(x - 8, y - 8, w + 16, h + 8, '#1b1714'); rect(x, y, w, h, '#05070b');
  g.save(); g.translate(x, y); g.scale(1 - open * 0.85, 1); rect(0, 0, w, h, col); g.strokeStyle = 'rgba(0,0,0,0.35)'; g.lineWidth = 6; g.strokeRect(14, 14, w - 28, h * 0.42); g.strokeRect(14, h * 0.5, w - 28, h * 0.45); circle(w - 26, h * 0.52, 9, '#c9b98a'); g.restore();
  if (label) { g.fillStyle = '#e8e2d0'; g.font = '44px "Archivo Black"'; g.textAlign = 'center'; g.fillText(label, x + w / 2, y - 24); g.textAlign = 'left'; }
}
// perspective corridor
function corridor(T, o = {}) {
  const vx = o.vx || W / 2, vy = o.vy || 820, wall = o.wall || '#3c4552', floor = o.floor || '#2a2f36', ceil = o.ceil || '#1d2229', lit = o.lit === undefined ? 1 : o.lit;
  g.fillStyle = ceil; g.beginPath(); g.moveTo(-200, -200); g.lineTo(W + 200, -200); g.lineTo(vx + 90, vy - 120); g.lineTo(vx - 90, vy - 120); g.fill();
  g.fillStyle = wall; g.beginPath(); g.moveTo(-200, -200); g.lineTo(vx - 90, vy - 120); g.lineTo(vx - 90, vy + 120); g.lineTo(-200, H + 200); g.fill();
  g.beginPath(); g.moveTo(W + 200, -200); g.lineTo(vx + 90, vy - 120); g.lineTo(vx + 90, vy + 120); g.lineTo(W + 200, H + 200); g.fill();
  g.fillStyle = floor; g.beginPath(); g.moveTo(-200, H + 200); g.lineTo(vx - 90, vy + 120); g.lineTo(vx + 90, vy + 120); g.lineTo(W + 200, H + 200); g.fill();
  rect(vx - 90, vy - 120, 180, 240, o.end || '#0a0c10');
  if (lit) for (let i = 0; i < 6; i++) { const k = Math.pow(0.62, i); const y = lerp(vy - 120, -60, k); const w = 180 * k + 30; g.fillStyle = `rgba(255,255,235,${0.9 * lit})`; g.fillRect(vx - w / 2, y, w, 16 * k + 4); glow(vx, y + 10, 260 * k + 40, 'rgba(255,255,230,A)', 0.25 * lit); }
  // side doors
  for (let i = 0; i < 4; i++) { const k = Math.pow(0.6, i + 0.6); const x0 = lerp(vx - 90, -200, k), y0 = lerp(vy - 100, -150, k), h = lerp(200, 1700, k) * 0.62; g.fillStyle = 'rgba(0,0,0,0.35)'; g.fillRect(x0 + 20 * k, y0 + h * 0.5, 120 * k, h); g.fillRect(W - x0 - 140 * k, y0 + h * 0.5, 120 * k, h); }
}
function silhouetteCity(y, col = '#0b0d16', seed = 2) { const r = C.rng(seed); g.fillStyle = col; let x = -100; while (x < W + 100) { const w = 60 + r() * 120, h = 120 + r() * 420; g.fillRect(x, y - h, w, h + 600); x += w + 6; } }
function windowsLit(y, seed = 3) { const r = C.rng(seed); for (let i = 0; i < 70; i++) { if (r() < 0.6) continue; g.fillStyle = `rgba(255,214,120,${0.4 + r() * 0.5})`; g.fillRect(r() * W, y - r() * 400, 14, 18); } }
function lightning(x, y0, y1, seed, a = 1) { const r = C.rng(seed); let px = x, py = y0; g.strokeStyle = `rgba(230,240,255,${a})`; g.lineWidth = 9; g.beginPath(); g.moveTo(px, py); while (py < y1) { px += (r() - 0.5) * 140; py += 60 + r() * 80; g.lineTo(px, py); } g.stroke(); glow(x, (y0 + y1) / 2, 700, 'rgba(200,220,255,A)', 0.35 * a); }
function shark(x, y, s, dir = 1) { g.save(); g.translate(x, y); g.scale(s * dir, s); g.fillStyle = '#4a5d6e'; g.beginPath(); g.moveTo(-160, 0); g.quadraticCurveTo(-40, -70, 150, -10); g.lineTo(190, -50); g.lineTo(175, 0); g.lineTo(190, 45); g.lineTo(150, 12); g.quadraticCurveTo(-40, 60, -160, 0); g.fill(); g.beginPath(); g.moveTo(-10, -48); g.lineTo(30, -120); g.lineTo(50, -40); g.fill(); g.fillStyle = '#d7dee5'; g.beginPath(); g.moveTo(-150, 6); g.quadraticCurveTo(-40, 40, 140, 12); g.quadraticCurveTo(-40, 20, -150, 6); g.fill(); circle(-110, -8, 7, '#0c0c0c'); g.restore(); }
function car(x, y, s, col = '#3b5b8a', o = {}) { g.save(); g.translate(x, y); g.scale(s, s); g.fillStyle = col; g.beginPath(); g.roundRect(-200, -90, 400, 90, 26); g.fill(); g.beginPath(); g.roundRect(-120, -170, 230, 90, 30); g.fill(); rect(-100, -158, 90, 66, o.lit ? '#ffe7a6' : '#1b2533'); rect(0, -158, 90, 66, o.lit ? '#ffe7a6' : '#1b2533'); circle(-120, 0, 44, '#111'); circle(120, 0, 44, '#111'); circle(-120, 0, 18, '#777'); circle(120, 0, 18, '#777'); if (o.alarm) { glow(-190, -50, 120, 'rgba(255,170,40,A)', 0.8); glow(190, -50, 120, 'rgba(255,170,40,A)', 0.8); } g.restore(); }
function truck(x, y, s, col = '#9a2f2a') { g.save(); g.translate(x, y); g.scale(s, s); rect(-420, -300, 560, 260, '#d9d4c8'); g.strokeStyle = '#111'; g.lineWidth = 6; g.strokeRect(-420, -300, 560, 260); g.fillStyle = col; g.beginPath(); g.roundRect(150, -260, 200, 220, 24); g.fill(); rect(200, -240, 110, 80, '#1b2533'); rect(130, -60, 240, 30, '#333'); [-340, -220, 210, 300].forEach(wx => { circle(wx, -20, 46, '#111'); circle(wx, -20, 18, '#888'); }); g.restore(); }
function bottle(x, y, s = 1, full = true) { g.save(); g.translate(x, y); g.scale(s, s); g.fillStyle = 'rgba(170,215,255,0.55)'; g.beginPath(); g.roundRect(-26, -120, 52, 120, 10); g.fill(); rect(-12, -150, 24, 32, '#3d7bd9'); if (full) { g.fillStyle = 'rgba(80,160,240,0.6)'; g.fillRect(-22, -95, 44, 90); } g.restore(); }
module.exports = { sh, HERO, bigWord, darkBG, door, corridor, silhouetteCity, windowsLit, lightning, shark, car, truck, bottle };

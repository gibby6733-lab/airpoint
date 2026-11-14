// Last Shift Shorts engine: core drawing kit (1080x1920, 9:16).
const SK = '/root/.claude/skills/directing-stickman-videos';
const { createCanvas, GlobalFonts } = require(SK + '/node_modules/@napi-rs/canvas');
GlobalFonts.registerFromPath(SK + '/assets/fonts/ArchivoBlack.ttf', 'Archivo Black');
GlobalFonts.registerFromPath(SK + '/assets/fonts/Anton.ttf', 'Anton');

const W = 1080, H = 1920;
const canvas = createCanvas(W, H);
const g = canvas.getContext('2d');

const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const ease = x => { x = clamp(x); return x * x * (3 - 2 * x); };
const lerp = (a, b, t) => a + (b - a) * t;
function rng(seed) { let s = seed % 2147483647 || 1; return () => (s = (s * 16807) % 2147483647) / 2147483647; }

// ---------- primitives ----------
function line(pts, col, w) { g.strokeStyle = col; g.lineWidth = w; g.lineCap = 'round'; g.lineJoin = 'round'; g.beginPath(); g.moveTo(pts[0][0], pts[0][1]); for (let i = 1; i < pts.length; i++) g.lineTo(pts[i][0], pts[i][1]); g.stroke(); }
function rect(x, y, w, h, col) { g.fillStyle = col; g.fillRect(x, y, w, h); }
function circle(x, y, r, fill, stroke, sw) { g.beginPath(); g.arc(x, y, r, 0, Math.PI * 2); if (fill) { g.fillStyle = fill; g.fill(); } if (stroke) { g.strokeStyle = stroke; g.lineWidth = sw || 4; g.stroke(); } }
function ell(x, y, rx, ry, fill, rot = 0) { g.beginPath(); g.ellipse(x, y, rx, ry, rot, 0, Math.PI * 2); g.fillStyle = fill; g.fill(); }
function vgrad(y0, y1, stops) { const gr = g.createLinearGradient(0, y0, 0, y1); stops.forEach(([o, c]) => gr.addColorStop(o, c)); return gr; }
function rgrad(x, y, r0, r1, stops) { const gr = g.createRadialGradient(x, y, r0, x, y, r1); stops.forEach(([o, c]) => gr.addColorStop(o, c)); return gr; }
function glow(x, y, r, col, a = 0.5) { g.fillStyle = rgrad(x, y, 0, r, [[0, col.replace('A', a)], [1, col.replace('A', 0)]]); g.fillRect(x - r, y - r, r * 2, r * 2); }
const pol = (x, y, len, ang) => [x + Math.cos(ang) * len, y + Math.sin(ang) * len];

// ---------- skies / environment ----------
const STARS = (() => { const r = rng(5); return Array.from({ length: 220 }, () => [r() * W, r() * H * 0.55, 0.25 + r() * 0.7, r() * 6]); })();
function nightSky(T = 0, top = '#04050d', mid = '#141634', low = '#3a2340', horizon = 1000) {
  g.fillStyle = vgrad(0, horizon, [[0, top], [0.6, mid], [1, low]]); g.fillRect(-300, -300, W + 600, horizon + 300);
  STARS.forEach(([x, y, a, p]) => { if (y < horizon) { g.globalAlpha = a * (0.75 + 0.25 * Math.sin(T * 2 + p)); g.fillStyle = '#fff'; g.fillRect(x, y, 3, 3); } });
  g.globalAlpha = 1;
}
function moon(x, y, r = 70) { glow(x, y, r * 3.2, 'rgba(220,230,255,A)', 0.25); circle(x, y, r, '#e9ecf5'); circle(x + r * 0.35, y - r * 0.2, r * 0.18, '#d3d7e4'); circle(x - r * 0.3, y + r * 0.3, r * 0.12, '#d3d7e4'); }
function hills(y, col, amp = 40, seed = 1) { g.fillStyle = col; g.beginPath(); g.moveTo(-300, y + 200); for (let x = -300; x <= W + 300; x += 30) g.lineTo(x, y - Math.sin(x / 170 + seed) * amp - Math.sin(x / 61 + seed * 3) * amp * 0.3); g.lineTo(W + 300, H + 300); g.lineTo(-300, H + 300); g.fill(); }
function ground(y, c1, c2) { g.fillStyle = vgrad(y, H, [[0, c1], [1, c2]]); g.fillRect(-300, y, W + 600, H - y + 300); }
function room(wall = '#1a2030', floor = '#0e121b', floorY = 1250, wallTop = '#121726') {
  g.fillStyle = vgrad(0, floorY, [[0, wallTop], [1, wall]]); g.fillRect(-300, -300, W + 600, floorY + 300);
  g.fillStyle = vgrad(floorY, H, [[0, floor], [1, '#05070b']]); g.fillRect(-300, floorY, W + 600, H - floorY + 300);
  rect(-300, floorY - 8, W + 600, 10, 'rgba(0,0,0,0.35)');
}
function rain(T, a = 0.35, n = 160) { const r = rng(9); g.strokeStyle = `rgba(190,210,255,${a})`; g.lineWidth = 3; g.beginPath(); for (let i = 0; i < n; i++) { const x = (r() * W * 1.4 + T * 300) % (W * 1.4) - W * 0.2, y = (r() * H + T * 2200 * (0.8 + r() * 0.4)) % H; g.moveTo(x, y); g.lineTo(x - 18, y + 70); } g.stroke(); }
function snow(T, a = 0.8, n = 140) { const r = rng(12); g.fillStyle = `rgba(255,255,255,${a})`; for (let i = 0; i < n; i++) { const sp = 60 + r() * 120, x = (r() * W + Math.sin(T + i) * 40) % W, y = (r() * H + T * sp) % H; g.beginPath(); g.arc(x, y, 3 + r() * 5, 0, 7); g.fill(); } }
function fog(y, a = 0.25) { g.fillStyle = vgrad(y - 200, y + 200, [[0, 'rgba(160,170,190,0)'], [0.5, `rgba(160,170,190,${a})`], [1, 'rgba(160,170,190,0)']]); g.fillRect(-300, y - 200, W + 600, 400); }
function water(y, T, top = '#0d2a3a', bot = '#030b12', shimmer = 'rgba(200,230,255,0.25)') {
  g.fillStyle = vgrad(y, H, [[0, top], [1, bot]]); g.fillRect(-300, y, W + 600, H - y + 300);
  g.strokeStyle = shimmer; g.lineWidth = 4;
  for (let i = 0; i < 18; i++) { const yy = y + 20 + i * i * 4; g.beginPath(); for (let x = -50; x < W + 50; x += 20) g.lineTo(x, yy + Math.sin(x / 40 + T * 2 + i) * (3 + i * 0.6)); g.stroke(); }
}

// ---------- characters ----------
// pose: angles in radians from +x axis (PI/2 = straight down). Each limb [upper, lower].
const P = Math.PI;
const POSES = {
  stand: () => ({ armL: [1.85, 1.75], armR: [1.3, 1.4], legL: [1.75, 1.65], legR: [1.4, 1.5] }),
  scared: () => ({ armL: [2.5, -1.9], armR: [0.65, -1.25], legL: [1.85, 1.6], legR: [1.3, 1.55] }),
  hide: () => ({ armL: [1.0, 2.6], armR: [2.1, 0.5], legL: [2.6, 1.0], legR: [0.55, 2.1], crouch: 1 }),
  point: () => ({ armL: [1.85, 1.75], armR: [-0.25, -0.15], legL: [1.75, 1.65], legR: [1.4, 1.5] }),
  reach: () => ({ armL: [-0.15, -0.05], armR: [0.05, 0.12], legL: [1.75, 1.65], legR: [1.4, 1.5] }),
  zombieL: () => ({ armL: [P + 0.12, P + 0.05], armR: [P - 0.1, P - 0.05], legL: [1.75, 1.65], legR: [1.4, 1.5] }),
  arms_up: () => ({ armL: [-2.5, -2.7], armR: [-0.65, -0.45], legL: [1.75, 1.65], legR: [1.4, 1.5] }),
  hold: () => ({ armL: [2.2, -0.2], armR: [0.9, 3.0], legL: [1.75, 1.65], legR: [1.4, 1.5] }),
  sit: () => ({ armL: [2.0, 0.6], armR: [1.15, 2.5], legL: [0.3, 1.6], legR: [0.15, 1.5], sit: 1 }),
  swim: (T) => ({ armL: [P + Math.sin(T * 6) * 0.9, P + Math.sin(T * 6) * 0.9], armR: [-Math.sin(T * 6) * 0.9, -Math.sin(T * 6) * 0.9], legL: [1.9, 2.0], legR: [1.25, 1.1] }),
  lie: () => ({ armL: [P, P], armR: [0, 0], legL: [0.05, 0.05], legR: [-0.05, -0.05], lie: 1 }),
};
function walkPose(T, speed = 1, zombie = false, dir = 1) {
  const s = Math.sin(T * 5 * speed), c = Math.cos(T * 5 * speed);
  const legs = { legL: [P / 2 + s * 0.42, P / 2 + s * 0.42 + Math.max(0, -c) * 0.5], legR: [P / 2 - s * 0.42, P / 2 - s * 0.42 + Math.max(0, c) * 0.5] };
  if (zombie) { const a = dir > 0 ? 0 : P; return { ...legs, armL: [a + 0.1 * dir + s * 0.05, a + 0.05], armR: [a - 0.05 * dir - s * 0.05, a - 0.1 * dir] }; }
  return { ...legs, armL: [P / 2 - s * 0.5, P / 2 - s * 0.5 - 0.4], armR: [P / 2 + s * 0.5, P / 2 + s * 0.5 - 0.4] };
}
function runPose(T, dir = 1) {
  const s = Math.sin(T * 9);
  const m = a => dir > 0 ? a : P - a;
  return { legL: [m(P / 2 - 0.2 + s * 0.7), m(P / 2 + 0.3 + s * 0.4)], legR: [m(P / 2 - 0.2 - s * 0.7), m(P / 2 + 0.3 - s * 0.4)], armL: [m(P / 2 + s * 0.8), m(P / 2 + s * 0.8 - 1.2)], armR: [m(P / 2 - s * 0.8), m(P / 2 - s * 0.8 - 1.2)] };
}
const LOOK = { HERO: { head: '#ffffff', body: '#111111', glove: '#ffffff' }, ZOMBIE: { head: '#93a08d', body: '#2a2f2a', glove: '#7d8a77' } };

// fig({x,y,s, pose, kind:'hero'|'zombie'|'kid'|'adult', vest, hat, face, look, lean, flip, extra})
function fig(o) {
  const s = o.s || 1, x = o.x, y = o.y, isZ = o.kind === 'zombie';
  const pz = typeof o.pose === 'function' ? o.pose : null;
  const pose = { ...(pz ? pz() : (POSES[o.pose || 'stand'] || POSES.stand)(o.T || 0)), ...(o.poseOv || {}) };
  const look = isZ ? LOOK.ZOMBIE : LOOK.HERO;
  const head = o.headCol || look.head, body = o.bodyCol || look.body, glove = o.gloveCol || look.glove;
  const kid = o.kind === 'kid', sc = kid ? s * 0.68 : s;
  const L = 52 * sc, lw = (o.lw || 11) * sc;
  let hip, sh, hd;
  const lean = (o.lean || 0) * sc;
  if (pose.lie) { hip = [x, y - 20 * sc]; sh = [x - 120 * sc, y - 20 * sc]; hd = [x - 170 * sc, y - 28 * sc]; }
  else {
    const drop = pose.crouch ? 55 : pose.sit ? 48 : 0;
    hip = [x, y - (104 - drop) * sc]; sh = [x + lean, y - (176 - drop) * sc]; hd = [x + lean * 1.25, y - (218 - drop) * sc];
  }
  const limb = (from, a) => { const k = pol(from[0], from[1], L, a[0]); return [from, k, pol(k[0], k[1], L, a[1])]; };
  const legs = [limb(hip, pose.legL), limb(hip, pose.legR)];
  const arms = [limb(sh, pose.armL), limb(sh, pose.armR)];
  const OUT = '#0c0c0c';
  legs.forEach(p => { line(p, OUT, lw + 5 * sc); line(p, body, lw); });
  line([hip, sh], OUT, lw * 1.25 + 5 * sc); line([hip, sh], body, lw * 1.25);
  if (o.vest && !pose.lie) { // work vest
    g.fillStyle = o.vest; g.strokeStyle = OUT; g.lineWidth = 4 * sc;
    g.beginPath(); g.moveTo(sh[0] - 26 * sc, sh[1] - 4 * sc); g.lineTo(sh[0] + 26 * sc, sh[1] - 4 * sc); g.lineTo(hip[0] + 22 * sc, hip[1] + 6 * sc); g.lineTo(hip[0] - 22 * sc, hip[1] + 6 * sc); g.closePath(); g.fill(); g.stroke();
    if (o.stripe) { rect(sh[0] - 22 * sc, lerp(sh[1], hip[1], 0.55), 44 * sc, 7 * sc, o.stripe); }
    circle(sh[0] + 11 * sc, sh[1] + 20 * sc, 7 * sc, '#ff8a1f');
  }
  if (o.dress && !pose.lie) { g.fillStyle = o.dress; g.beginPath(); g.moveTo(sh[0] - 18 * sc, sh[1]); g.lineTo(sh[0] + 18 * sc, sh[1]); g.lineTo(hip[0] + 34 * sc, hip[1] + 26 * sc); g.lineTo(hip[0] - 34 * sc, hip[1] + 26 * sc); g.closePath(); g.fill(); }
  if (o.held) o.held(arms[1][2], sc);
  arms.forEach(p => { line(p, OUT, lw + 5 * sc); line(p, body, lw); });
  arms.forEach(p => circle(p[2][0], p[2][1], 12 * sc, glove, OUT, 4 * sc));
  // head
  const hr = 40 * sc;
  if (o.hair) o.hair(hd[0], hd[1], hr, sc);
  circle(hd[0], hd[1], hr, head, OUT, 5 * sc);
  if (isZ) { circle(hd[0] + 14 * sc, hd[1] + 14 * sc, 6 * sc, 'rgba(90,40,40,0.5)'); }
  if (o.headlamp) {
    rect(hd[0] - hr, hd[1] - 22 * sc, hr * 2, 10 * sc, '#1b1b1b');
    circle(hd[0] + (o.faceDir || 0) * 8 * sc, hd[1] - 20 * sc, 10 * sc, o.lampOn ? '#fff3a8' : '#5a5a5a', OUT, 3 * sc);
    if (o.lampOn) glow(hd[0], hd[1] - 20 * sc, 90 * sc, 'rgba(255,240,170,A)', 0.55);
  }
  if (o.cap) { g.fillStyle = o.cap; g.beginPath(); g.arc(hd[0], hd[1] - 6 * sc, hr + 2 * sc, P, 0); g.fill(); rect(hd[0] + (o.faceDir || 1) * 10 * sc - 4 * sc, hd[1] - 12 * sc, (o.faceDir || 1) * 50 * sc, 9 * sc, o.cap); }
  face(hd[0], hd[1], sc, o);
  if (o.extra) o.extra(hd, sh, hip, arms, sc);
  return { hd, sh, hip, arms, legs };
}
function face(hx, hy, s, o) {
  const f = o.face || (o.kind === 'zombie' ? 'zombie' : 'neutral'), lk = o.look || [0, 0];
  const fx = hx + lk[0] * 7 * s, fy = hy + lk[1] * 6 * s;
  g.fillStyle = '#0c0c0c'; g.strokeStyle = '#0c0c0c'; g.lineCap = 'round';
  if (f === 'none') return;
  if (f === 'zombie') {
    ell(fx - 13 * s, fy - 2 * s, 8 * s, 10 * s, '#0c0c0c'); ell(fx + 13 * s, fy - 2 * s, 8 * s, 10 * s, '#0c0c0c');
    circle(fx - 13 * s, fy - 4 * s, 2.2 * s, o.eyeGlow || '#cfd8c8'); circle(fx + 13 * s, fy - 4 * s, 2.2 * s, o.eyeGlow || '#cfd8c8');
    ell(fx, fy + 20 * s, 9 * s, 5 * s, '#0c0c0c'); return;
  }
  if (f === 'smile_z') { ell(fx - 13 * s, fy - 2 * s, 8 * s, 10 * s, '#0c0c0c'); ell(fx + 13 * s, fy - 2 * s, 8 * s, 10 * s, '#0c0c0c'); g.lineWidth = 4 * s; g.beginPath(); g.arc(fx, fy + 10 * s, 16 * s, 0.2, P - 0.2); g.stroke(); return; }
  const big = f === 'scared' || f === 'shock';
  ell(fx - 13 * s, fy, (big ? 7 : 5.5) * s, (big ? 10 : 8) * s, '#0c0c0c'); ell(fx + 13 * s, fy, (big ? 7 : 5.5) * s, (big ? 10 : 8) * s, '#0c0c0c');
  g.lineWidth = 3.5 * s;
  if (f === 'scared') { g.beginPath(); g.moveTo(fx - 22 * s, fy - 16 * s); g.lineTo(fx - 7 * s, fy - 12 * s); g.moveTo(fx + 22 * s, fy - 16 * s); g.lineTo(fx + 7 * s, fy - 12 * s); g.stroke(); ell(fx, fy + 22 * s, 6 * s, 5 * s, '#0c0c0c'); }
  else if (f === 'shock') { ell(fx, fy + 23 * s, 9 * s, 11 * s, '#0c0c0c'); }
  else if (f === 'determined') { g.beginPath(); g.moveTo(fx - 22 * s, fy - 18 * s); g.lineTo(fx - 6 * s, fy - 10 * s); g.moveTo(fx + 22 * s, fy - 18 * s); g.lineTo(fx + 6 * s, fy - 10 * s); g.stroke(); g.beginPath(); g.moveTo(fx - 8 * s, fy + 21 * s); g.lineTo(fx + 8 * s, fy + 21 * s); g.stroke(); }
  else if (f === 'happy') { g.beginPath(); g.arc(fx, fy + 12 * s, 11 * s, 0.3, P - 0.3); g.stroke(); }
  else if (f === 'sad') { g.beginPath(); g.arc(fx, fy + 28 * s, 10 * s, P + 0.4, -0.4); g.stroke(); }
  else { g.beginPath(); g.moveTo(fx - 7 * s, fy + 21 * s); g.lineTo(fx + 7 * s, fy + 21 * s); g.stroke(); }
}
// crowd of zombies walking toward a vanishing point or across
function crowd(T, opt = {}) {
  const n = opt.n || 24, r = rng(opt.seed || 3), y0 = opt.y0 || 1150, y1 = opt.y1 || 1900, xc = opt.xc || W / 2, spread = opt.spread || 900, sMin = opt.sMin || 0.25, sMax = opt.sMax || 1.3;
  const list = Array.from({ length: n }, (_, i) => ({ k: r(), x: (r() - 0.5) * spread, ph: r() * 9, dx: (r() - 0.5) * 30 })).map(m => ({ ...m, k: (m.k + T * (opt.adv || 0.03)) % 1 })).sort((a, b) => a.k - b.k);
  for (const m of list) {
    const k = m.k, y = lerp(y0, y1, k), s = lerp(sMin, sMax, k);
    const xx = xc + m.x * lerp(0.25, 1, k) + Math.sin(T + m.ph) * m.dx;
    const sh = Math.round(lerp(60, 150, k));
    fig({ x: xx, y, s, kind: 'zombie', pose: () => walkPose(T + m.ph, 0.6, true, opt.dir || -1), headCol: `rgb(${sh + 18},${sh + 30},${sh + 14})`, bodyCol: `rgb(${sh - 35},${sh - 28},${sh - 35})`, gloveCol: `rgb(${sh},${sh + 10},${sh - 4})`, look: [0, 0], lean: -6 });
  }
}

// ---------- effects ----------
function vignette(a = 0.7, r0 = 420) { g.fillStyle = rgrad(W / 2, H / 2, r0, 1250, [[0, 'rgba(0,0,0,0)'], [1, `rgba(0,0,0,${a})`]]); g.fillRect(0, 0, W, H); }
function grain(a = 0.035) { g.fillStyle = `rgba(255,255,255,${a})`; for (let i = 0; i < 500; i++) g.fillRect(Math.random() * W, Math.random() * H, 3, 3); g.fillStyle = `rgba(0,0,0,${a * 1.5})`; for (let i = 0; i < 500; i++) g.fillRect(Math.random() * W, Math.random() * H, 3, 3); }
function flash(a, col = '255,255,255') { if (a > 0) { g.fillStyle = `rgba(${col},${a})`; g.fillRect(0, 0, W, H); } }
function tint(col) { g.fillStyle = col; g.fillRect(0, 0, W, H); }
function flashlight(x, y, ang, len = 900, spread = 0.35, a = 0.35) {
  g.save(); g.globalCompositeOperation = 'lighter';
  const gr = g.createRadialGradient(x, y, 10, x, y, len); gr.addColorStop(0, `rgba(255,245,200,${a})`); gr.addColorStop(1, 'rgba(255,245,200,0)');
  g.fillStyle = gr; g.beginPath(); g.moveTo(x, y); g.arc(x, y, len, ang - spread, ang + spread); g.closePath(); g.fill(); g.restore();
}

// ---------- text ----------
function textBox(txt, x, y, size, fill = '#fff', stroke = '#000', sw = 0, font = 'Archivo Black', align = 'center', maxW = 960) {
  g.font = `${size}px "${font}"`; g.textAlign = align; g.textBaseline = 'middle'; g.lineJoin = 'round';
  // wrap
  const words = txt.split(' '); const lines = []; let cur = '';
  for (const w of words) { const t = cur ? cur + ' ' + w : w; if (g.measureText(t).width > maxW && cur) { lines.push(cur); cur = w; } else cur = t; }
  if (cur) lines.push(cur);
  const lh = size * 1.12; const top = y - (lines.length - 1) * lh / 2;
  lines.forEach((l, i) => { if (sw) { g.strokeStyle = stroke; g.lineWidth = sw; g.strokeText(l, x, top + i * lh); } g.fillStyle = fill; g.fillText(l, x, top + i * lh); });
  g.textAlign = 'left'; g.textBaseline = 'alphabetic';
  return lines.length * lh;
}

module.exports = { W, H, canvas, g, clamp, ease, lerp, rng, line, rect, circle, ell, vgrad, rgrad, glow, pol, nightSky, moon, hills, ground, room, rain, snow, fog, water, P, POSES, walkPose, runPose, fig, face, crowd, vignette, grain, flash, tint, flashlight, textBox };

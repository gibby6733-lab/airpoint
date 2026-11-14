// Last Shift ep01: 30-40s opening test. Free pipeline: code-drawn animation, offline TTS scratch voice, synthesized SFX.
// Usage: node render.cjs <outdir>
const SK = '/root/.claude/skills/directing-stickman-videos';
const { createCanvas, GlobalFonts } = require(SK + '/node_modules/@napi-rs/canvas');
const { execFileSync, spawn } = require('child_process');
const fs = require('fs'), path = require('path');
GlobalFonts.registerFromPath(SK + '/assets/fonts/ArchivoBlack.ttf', 'Archivo Black');

const OUT = path.resolve(process.argv[2] || 'out');
fs.mkdirSync(OUT + '/vo', { recursive: true });
const W = 1280, H = 720, FPS = 24;

// ---------------- script → voice lines → timeline ----------------
const LINES = [
  { id: 'L1', text: 'At two-thirteen in the morning, the bell rings at pump four.', shot: 'A', after: 1.5, sfx: 'ding' },
  { id: 'L2', text: 'That bell means somebody just lifted a nozzle.', shot: 'B' },
  { id: 'L3', text: 'I look up from the register.', shot: 'C' },
  { id: 'L4', text: "There's no car at pump four.", shot: 'D' },
  { id: 'L5', text: "There's a man.", shot: 'D2', after: 0.4 },
  { id: 'L6', text: "He's holding the nozzle against his chest, like he's hugging it,", shot: 'E' },
  { id: 'L7', text: "and he's staring at the store.", shot: 'E2' },
  { id: 'L8', text: 'Not at me. At the glass.', shot: 'F', after: 0.5 },
  { id: 'L9', text: "I don't move.", shot: 'G' },
  { id: 'L10', text: 'My headlamp is off. The store lights are off.', shot: 'G2' },
  { id: 'L11', text: "Out there, under the canopy, it's bright as noon.", shot: 'H', after: 0.4 },
  { id: 'L12', text: 'He leans closer.', shot: 'I' },
  { id: 'L13', text: 'His nose touches the window.', shot: 'I2', after: 0.6, sfx: 'thump' },
  { id: 'L14', text: 'And all he sees...', shot: 'J', after: 0.7 },
  { id: 'L15', text: 'is himself.', shot: 'J', after: 1.2 },
  { id: 'L16', text: 'There are always others.', shot: 'K', after: 1.0 },
];
const dur = f => parseFloat(execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]).toString());
let t = 0.6; const GAP = 0.28;
for (const L of LINES) {
  L.wav = `${OUT}/vo/${L.id}.wav`;
  execFileSync('espeak-ng', ['-v', 'mb-us2', '-s', '128', '-p', '38', '-w', L.wav, L.text]);
  L.start = t; L.dur = dur(L.wav); L.end = L.start + L.dur;
  t = L.end + GAP + (L.after || 0);
}
const TITLE_START = t, TOTAL = t + 3.2;
// shots: each shot starts at its first line's start (shot A starts at 0); ding plays right after L1
const shots = [];
for (const L of LINES) {
  if (!shots.length || shots[shots.length - 1].id !== L.shot) shots.push({ id: L.shot, start: shots.length ? L.start - 0.05 : 0 });
}
// shot B starts at the ding (after L1), not at L2
const dingT = LINES[0].end + 0.15;
shots.find(s => s.id === 'B').start = dingT;
shots.push({ id: 'TITLE', start: TITLE_START });
shots.forEach((s, i) => s.end = i + 1 < shots.length ? shots[i + 1].start : TOTAL);
const thumpT = LINES.find(l => l.id === 'L13').end + 0.05;

// captions: split long lines into ≤6-word chunks timed by word share
const CAPS = [];
for (const L of LINES) {
  const w = L.text.split(' ');
  const n = Math.ceil(w.length / 6), per = Math.ceil(w.length / n);
  for (let i = 0; i < n; i++) {
    const a = i * per, b = Math.min(w.length, a + per);
    CAPS.push({ text: w.slice(a, b).join(' '), start: L.start + L.dur * a / w.length, end: L.start + L.dur * b / w.length + (b === w.length ? 0.15 : 0) });
  }
}
// SRT
const ts = s => { const ms = Math.round(s * 1000); const p = (n, l = 2) => String(n).padStart(l, '0'); return `${p(Math.floor(ms / 3600000))}:${p(Math.floor(ms / 60000) % 60)}:${p(Math.floor(ms / 1000) % 60)},${p(ms % 1000, 3)}`; };
fs.writeFileSync(OUT + '/captions.srt', CAPS.map((c, i) => `${i + 1}\n${ts(c.start)} --> ${ts(c.end)}\n${c.text}\n`).join('\n'));

// ---------------- drawing helpers ----------------
const c = createCanvas(W, H), g = c.getContext('2d');
const ease = x => x < 0 ? 0 : x > 1 ? 1 : x * x * (3 - 2 * x);
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
let seed = 11; const R = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
const STARS = Array.from({ length: 140 }, () => [R() * W, R() * 330, 0.3 + R() * 0.6]);
const WALKERS = Array.from({ length: 55 }, (_, i) => ({ p: R(), lane: R() - 0.5, sp: 0.006 + R() * 0.004, ph: R() * 6 }));

function sky() {
  const s = g.createLinearGradient(0, 0, 0, 440);
  s.addColorStop(0, '#05060f'); s.addColorStop(0.6, '#141634'); s.addColorStop(1, '#3a2340');
  g.fillStyle = s; g.fillRect(-200, -200, W + 400, H + 400);
  g.fillStyle = '#fff'; STARS.forEach(([x, y, a]) => { g.globalAlpha = a; g.fillRect(x, y, 2, 2); }); g.globalAlpha = 1;
  g.fillStyle = '#1b1426'; g.beginPath(); g.moveTo(-200, 420);
  for (let x = -200; x <= W + 200; x += 40) g.lineTo(x, 400 - Math.sin(x / 130) * 18 - Math.sin(x / 47) * 6);
  g.lineTo(W + 200, 440); g.lineTo(-200, 440); g.fill();
  const gr = g.createLinearGradient(0, 410, 0, H);
  gr.addColorStop(0, '#2a1d22'); gr.addColorStop(1, '#120c10');
  g.fillStyle = gr; g.fillRect(-200, 410, W + 400, H);
}
function line(pts, col, w) { g.strokeStyle = col; g.lineWidth = w; g.lineCap = 'round'; g.lineJoin = 'round'; g.beginPath(); g.moveTo(...pts[0]); pts.slice(1).forEach(p => g.lineTo(...p)); g.stroke(); }
const pol = (x, y, len, ang) => [x + Math.cos(ang) * len, y + Math.sin(ang) * len];
// generic stick figure. angles in radians from +x (down = PI/2). feet at (x,y), height ~ 220*s
function figure(o) {
  const s = o.s || 1, x = o.x, y = o.y, lean = o.lean || 0;
  const hip = [x, y - 95 * s], sh = [x + lean * s, y - 160 * s], head = [x + lean * s * 1.2, y - 195 * s];
  const L = 48 * s, lw = (o.lw || 9) * s;
  const limb = (from, a1, a2) => { const k = pol(...from, L, a1); const e = pol(...k, L, a2); return [from, k, e]; };
  const legs = [limb(hip, ...(o.legL || [1.75, 1.65])), limb(hip, ...(o.legR || [1.4, 1.5]))];
  const arms = [limb(sh, ...(o.armL || [2.0, 1.8])), limb(sh, ...(o.armR || [1.2, 1.4]))];
  const out = '#111', col = o.body || '#111';
  legs.forEach(p => line(p, col, lw));
  line([hip, sh], col, lw * 1.15);
  if (o.vest) { // green work vest + orange badge
    g.fillStyle = '#2f5b3a'; g.strokeStyle = out; g.lineWidth = 3 * s;
    g.beginPath(); g.moveTo(sh[0] - 22 * s, sh[1] - 2 * s); g.lineTo(sh[0] + 22 * s, sh[1] - 2 * s); g.lineTo(hip[0] + 18 * s, hip[1] + 4 * s); g.lineTo(hip[0] - 18 * s, hip[1] + 4 * s); g.closePath(); g.fill(); g.stroke();
    g.fillStyle = '#ff8a1f'; g.beginPath(); g.arc(sh[0] + 9 * s, sh[1] + 18 * s, 6 * s, 0, 7); g.fill();
  }
  arms.forEach(p => line(p, col, lw));
  const glove = o.glove || '#fff';
  [...arms.map(a => a[2])].forEach(([gx, gy]) => { g.fillStyle = glove; g.strokeStyle = out; g.lineWidth = 3 * s; g.beginPath(); g.arc(gx, gy, 10 * s, 0, 7); g.fill(); g.stroke(); });
  // head
  g.fillStyle = o.head || '#fff'; g.strokeStyle = out; g.lineWidth = 4 * s;
  g.beginPath(); g.arc(head[0], head[1], 34 * s, 0, 7); g.fill(); g.stroke();
  face(head[0], head[1], s, o);
  return { head, sh, hip, arms };
}
function face(hx, hy, s, o) {
  const f = o.face || 'neutral', look = o.look || [0, 0];
  g.fillStyle = '#111';
  if (o.headlamp) {
    g.fillStyle = '#1d1d1d'; g.fillRect(hx - 34 * s, hy - 22 * s, 68 * s, 8 * s);
    g.fillStyle = o.lampOn ? '#ffe680' : '#555'; g.beginPath(); g.arc(hx, hy - 20 * s, 8 * s, 0, 7); g.fill();
    g.strokeStyle = '#111'; g.lineWidth = 2 * s; g.stroke(); g.fillStyle = '#111';
  }
  if (f === 'zombie') {
    g.beginPath(); g.ellipse(hx - 12 * s + look[0] * 4 * s, hy - 2 * s, 7 * s, 9 * s, 0, 0, 7); g.ellipse(hx + 12 * s + look[0] * 4 * s, hy - 2 * s, 7 * s, 9 * s, 0, 0, 7); g.fill();
    g.beginPath(); g.ellipse(hx + look[0] * 4 * s, hy + 18 * s, 7 * s, 4 * s, 0, 0, 7); g.fill();
    return;
  }
  const ex = look[0] * 5 * s, ey = look[1] * 5 * s;
  const er = f === 'scared' ? 6.5 : 5;
  g.beginPath(); g.ellipse(hx - 11 * s + ex, hy + 2 * s + ey, er * s * 0.8, er * s * 1.2, 0, 0, 7); g.ellipse(hx + 11 * s + ex, hy + 2 * s + ey, er * s * 0.8, er * s * 1.2, 0, 0, 7); g.fill();
  g.lineWidth = 2.5 * s; g.strokeStyle = '#111';
  if (f === 'scared') { g.beginPath(); g.ellipse(hx + ex * 0.5, hy + 20 * s, 5 * s, 4 * s, 0, 0, 7); g.fill(); g.beginPath(); g.moveTo(hx - 18 * s, hy - 12 * s); g.lineTo(hx - 6 * s, hy - 8 * s); g.moveTo(hx + 18 * s, hy - 12 * s); g.lineTo(hx + 6 * s, hy - 8 * s); g.stroke(); }
  else { g.beginPath(); g.moveTo(hx - 6 * s, hy + 19 * s); g.lineTo(hx + 6 * s, hy + 19 * s); g.stroke(); }
}
const ZOMBIE = { head: '#93a08d', body: '#2b302b', glove: '#7f8b79', face: 'zombie' };
function walkerTiny(x, y, s, shade, phase) {
  const sw = Math.sin(phase) * 0.25;
  figure({ x, y, s, ...ZOMBIE, head: `rgb(${shade + 20},${shade + 30},${shade + 18})`, body: `rgb(${shade - 30},${shade - 25},${shade - 30})`, glove: `rgb(${shade},${shade + 8},${shade})`, lean: -8,
    armL: [Math.PI - 0.15, Math.PI - 0.05], armR: [Math.PI - 0.3, Math.PI - 0.1], legL: [1.57 + sw, 1.57 + sw * 0.6], legR: [1.57 - sw, 1.57 - sw * 0.6], lw: 9 });
}
function highway(time, vx = 120, vy = 418, nearX = 210, spread = 1) {
  g.fillStyle = '#1d1a20';
  g.beginPath(); g.moveTo(vx - 6, vy); g.lineTo(vx + 6, vy); g.lineTo(nearX + 350 * spread, H + 40); g.lineTo(nearX - 350 * spread, H + 40); g.fill();
  const lerp = (a, b, t) => a + (b - a) * t;
  g.strokeStyle = '#c9a646';
  for (let k = 0.05; k < 1; k += 0.11) { const k2 = k + 0.05; g.lineWidth = 1 + k * 7; g.beginPath(); g.moveTo(lerp(vx, nearX, k * k), lerp(vy, H, k * k)); g.lineTo(lerp(vx, nearX, k2 * k2), lerp(vy, H, k2 * k2)); g.stroke(); }
  // walkers moving away (west = toward horizon)
  const list = WALKERS.map(w => { let p = (w.p - time * w.sp) % 1; if (p < 0) p += 1; return { ...w, p }; }).sort((a, b) => a.p - b.p);
  for (const w of list) {
    const k = Math.pow(w.p, 1.7) * 0.82;
    const x = lerp(vx, nearX, k) + w.lane * (10 + k * 420) * spread, y = lerp(vy, H + 30, k);
    walkerTiny(x, y, 0.05 + k * 0.62, Math.round(80 + k * 60), time * 4 + w.ph);
  }
}
function canopy(ox, oy, sc, bright = 1) {
  g.save(); g.translate(ox, oy); g.scale(sc, sc);
  const pool = g.createRadialGradient(350, 400, 40, 350, 400, 560);
  pool.addColorStop(0, `rgba(255,244,200,${0.55 * bright})`); pool.addColorStop(1, 'rgba(255,244,200,0)');
  g.fillStyle = pool; g.fillRect(-250, 100, 1200, 500);
  g.fillStyle = '#d8d2c4'; [80, 620].forEach(x => g.fillRect(x - 12, 40, 24, 330));
  g.fillStyle = '#e94b3c'; g.fillRect(0, 0, 720, 34); g.fillStyle = '#f4f1e8'; g.fillRect(0, 34, 720, 14);
  const gl = g.createLinearGradient(0, 48, 0, 150); gl.addColorStop(0, `rgba(255,250,220,${0.9 * bright})`); gl.addColorStop(1, 'rgba(255,250,220,0)');
  g.fillStyle = gl; g.fillRect(0, 48, 720, 102);
  g.restore();
}
function pump(x, y, s, nozzleOut = false, lit = false) {
  g.save(); g.translate(x, y); g.scale(s, s);
  g.fillStyle = '#f2efe6'; g.fillRect(0, 0, 58, 115); g.fillStyle = '#e94b3c'; g.fillRect(0, 0, 58, 22);
  g.fillStyle = lit ? '#7fe3a0' : '#26303b'; g.fillRect(12, 34, 34, 22);
  g.strokeStyle = '#111'; g.lineWidth = 4; g.strokeRect(0, 0, 58, 115);
  g.fillStyle = '#9a9384'; g.fillRect(-10, 115, 78, 12);
  // holster + nozzle
  g.fillStyle = '#333'; g.fillRect(44, 64, 12, 22);
  if (!nozzleOut) { g.fillStyle = '#222'; g.fillRect(48, 60, 16, 30); }
  g.restore();
}
function storeFront(x, y, s, dark = true) {
  g.save(); g.translate(x, y); g.scale(s, s);
  g.fillStyle = '#3b3036'; g.fillRect(0, 0, 450, 240);
  g.fillStyle = dark ? '#05070c' : '#33465a'; g.fillRect(30, 30, 390, 180);
  g.strokeStyle = 'rgba(255,250,230,0.16)'; g.lineWidth = 18; g.beginPath(); g.moveTo(70, 210); g.lineTo(150, 30); g.moveTo(180, 210); g.lineTo(230, 100); g.stroke();
  g.strokeStyle = '#111'; g.lineWidth = 6; g.strokeRect(30, 30, 390, 180); g.beginPath(); g.moveTo(225, 30); g.lineTo(225, 210); g.stroke();
  g.fillStyle = '#e94b3c'; g.fillRect(150, -30, 150, 30); g.fillStyle = '#fff'; g.font = '22px "Archivo Black"'; g.fillText("SUNNY'S", 168, -7);
  g.restore();
}
function vignette(a = 0.75) {
  const v = g.createRadialGradient(W / 2, H / 2, 250, W / 2, H / 2, 820);
  v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, `rgba(0,0,0,${a})`); g.fillStyle = v; g.fillRect(0, 0, W, H);
}
function interiorBG(windowGlow = 1) {
  g.fillStyle = '#070a12'; g.fillRect(0, 0, W, H);
  // big window behind, bright outside
  g.fillStyle = `rgba(255,244,205,${0.85 * windowGlow})`; g.fillRect(140, 70, 1000, 330);
  g.fillStyle = 'rgba(233,75,60,0.9)'; g.fillRect(140, 70, 1000, 26);
  g.fillStyle = '#c9c2b2'; g.fillRect(300, 230, 46, 100); g.fillRect(900, 230, 46, 100);
  g.fillStyle = '#0b0e16'; [140, 640, 1140].forEach(xx => g.fillRect(xx - 10, 60, 20, 350)); g.fillRect(130, 395, 1020, 16); g.fillRect(130, 60, 1020, 14);
  // shelves silhouettes
  g.fillStyle = '#0d111b'; g.fillRect(0, 420, W, 300);
}
function counter() {
  g.fillStyle = '#1a1f2b'; g.fillRect(0, 520, W, 200); g.fillStyle = '#242b3a'; g.fillRect(0, 510, W, 18);
  g.fillStyle = '#2b3242'; g.fillRect(820, 440, 150, 75); g.fillStyle = '#3a8f5a'; g.fillRect(835, 452, 70, 26); // register
  // rules card
  g.fillStyle = '#e9e2cf'; g.fillRect(990, 455, 70, 56); g.fillStyle = '#c33'; g.fillRect(998, 498, 54, 5); g.fillStyle = '#777'; for (let i = 0; i < 5; i++) g.fillRect(998, 464 + i * 6, 50, 2);
}
function grain(time) { g.fillStyle = 'rgba(255,255,255,0.025)'; for (let i = 0; i < 300; i++) g.fillRect(Math.random() * W, Math.random() * H, 2, 2); }

// ---------------- shots ----------------
function cam(z, cx = W / 2, cy = H / 2, dx = 0, dy = 0) { g.translate(cx + dx, cy + dy); g.scale(z, z); g.translate(-cx, -cy); }
const SH = {
  A(t, T) { cam(1 + 0.08 * t, 900, 380); sky(); highway(T); canopy(600, 160, 1, 1); storeFront(830, 300, 1, true); [700, 820, 1060, 1170].forEach((x, i) => pump(x, 410, 0.9, false, false)); },
  B(t, T) { // close-up pump 4, nozzle pulled out by grey hand
    cam(1 + 0.05 * t); g.fillStyle = '#2a1d22'; g.fillRect(0, 0, W, H);
    const gl = g.createLinearGradient(0, 0, 0, H); gl.addColorStop(0, 'rgba(255,248,215,0.55)'); gl.addColorStop(1, 'rgba(255,248,215,0.05)'); g.fillStyle = gl; g.fillRect(0, 0, W, H);
    const out = t > 0.12;
    pump(470, 60, 4.6, out, Math.floor(T * 6) % 2 === 0);
    // the "4" plate
    g.fillStyle = '#111'; g.beginPath(); g.arc(605, 40, 34, 0, 7); g.fill(); g.fillStyle = '#ffd54a'; g.font = '44px "Archivo Black"'; g.fillText('4', 590, 57);
    if (out) { // hose + nozzle leaving to the right, held by grey glove
      const k = ease((t - 0.12) / 0.35), nx = 760 + k * 360, ny = 380 - k * 60;
      line([[740, 420], [800, 560], [nx - 60, ny + 80], [nx - 20, ny + 10]], '#151515', 22);
      g.fillStyle = '#2b2b2b'; g.save(); g.translate(nx - 20, ny); g.rotate(-0.4); g.fillRect(-10, -30, 90, 38); g.restore();
      g.fillStyle = ZOMBIE.glove; g.strokeStyle = '#111'; g.lineWidth = 6; g.beginPath(); g.arc(nx + 30, ny - 16, 40, 0, 7); g.fill(); g.stroke();
      line([[nx + 50, ny - 30], [W + 80, ny - 120]], ZOMBIE.body, 34);
    }
  },
  C(t, T) { cam(1.02 - 0.02 * t); interiorBG(); counter();
    figure({ x: 560, y: 900, s: 2.6, vest: true, headlamp: true, lampOn: false, face: t < 0.35 ? 'neutral' : 'scared', look: [0, t < 0.35 ? 1 : -0.6], armL: [2.0, 1.2], armR: [1.1, 1.9] });
    counter();
    // dim rim light from window
    g.fillStyle = 'rgba(255,240,200,0.06)'; g.fillRect(0, 0, W, H); },
  D(t, T, empty = true) { // POV through window: lane at pump 4
    cam(1 + 0.04 * t, 640, 420); sky(); canopy(-80, 120, 1.6, 1);
    pump(380, 330, 1.6, !empty, false); pump(900, 330, 1.6, false, false);
    if (!empty) { const z = figure({ x: 560, y: 600, s: 1.05, ...ZOMBIE, lean: -6, armL: [2.6, 0.2], armR: [0.6, 2.9], look: [-1, 0] }); line([[470, 420], [540, 480], z.arms[0][2]], '#151515', 9); }
    // window frame + glass tint (we're inside, dark)
    g.setTransform(1, 0, 0, 1, 0, 0);
    g.fillStyle = 'rgba(5,7,12,0.18)'; g.fillRect(0, 0, W, H);
    g.fillStyle = '#05070c'; g.fillRect(0, 0, W, 40); g.fillRect(0, H - 60, W, 60); g.fillRect(0, 0, 50, H); g.fillRect(W - 50, 0, 50, H); g.fillRect(W / 2 - 14, 0, 28, H);
  },
  D2(t, T) { SH.D(t, T, false); },
  E(t, T, turn = 0) { // medium: zombie hugging nozzle at pump, staring at store
    cam(1.05 + 0.06 * t, 640, 330); g.fillStyle = '#2a1d22'; g.fillRect(0, 0, W, H);
    const gl = g.createLinearGradient(0, 0, 0, H); gl.addColorStop(0, 'rgba(255,248,215,0.6)'); gl.addColorStop(1, 'rgba(255,248,215,0.08)'); g.fillStyle = gl; g.fillRect(0, 0, W, H);
    pump(200, 120, 3.6, true, false);
    const sway = Math.sin(T * 1.6) * 3;
    const z = figure({ x: 720 + sway, y: 760, s: 2.3, ...ZOMBIE, lean: -10, armL: [2.2, -0.1], armR: [0.9, 3.0], look: [turn ? 0 : 1, 0] });
    // hose from pump to chest
    line([[400, 360], [520, 560], [640, 520], [700, 480]], '#151515', 16);
    g.fillStyle = '#2b2b2b'; g.save(); g.translate(690, 462); g.rotate(-0.3); g.fillRect(-12, -20, 90, 36); g.restore();
  },
  E2(t, T) { SH.E(t, T, 1); },
  F(t, T) { // zombie face staring at the glass, sheen sweeping
    cam(1 + 0.12 * t, 640, 360); g.fillStyle = '#d9cfb3'; g.fillRect(0, 0, W, H);
    const gl = g.createRadialGradient(640, 200, 50, 640, 300, 800); gl.addColorStop(0, '#f6eed4'); gl.addColorStop(1, '#6b5e55'); g.fillStyle = gl; g.fillRect(0, 0, W, H);
    figure({ x: 640, y: 1350, s: 4.6, ...ZOMBIE, armL: [1.9, 1.7], armR: [1.2, 1.4] });
    // glass plane + sweeping reflection streak
    g.fillStyle = 'rgba(20,30,45,0.12)'; g.fillRect(0, 0, W, H);
    const sx = -400 + t * 1800; g.save(); g.globalAlpha = 0.25; g.fillStyle = '#fff'; g.translate(sx, 0); g.rotate(0.35); g.fillRect(0, -200, 70, 1400); g.fillRect(110, -200, 24, 1400); g.restore();
  },
  G(t, T) { // Sam frozen close-up, sweat drop
    cam(1.0 + 0.04 * t, 640, 300); interiorBG(0.9);
    figure({ x: 640, y: 1150, s: 3.6, vest: true, headlamp: true, lampOn: false, face: 'scared', look: [0, -0.3] });
    const dy = ease(t) * 70; g.fillStyle = '#9fd3ff'; g.beginPath(); g.ellipse(790, 330 + dy, 9, 14, 0, 0, 7); g.fill();
    vignette(0.85);
  },
  G2(t, T) { // headlamp off → light switch off
    g.fillStyle = '#070a12'; g.fillRect(0, 0, W, H);
    if (t < 0.5) { cam(1 + 0.05 * t); figure({ x: 640, y: 1900, s: 7.5, vest: true, headlamp: true, lampOn: false, face: 'scared', look: [0, -1] }); }
    else { cam(1 + 0.05 * t); g.fillStyle = '#1b2230'; g.fillRect(0, 0, W, H); g.fillStyle = '#d9d4c8'; g.fillRect(540, 200, 200, 320); g.strokeStyle = '#111'; g.lineWidth = 8; g.strokeRect(540, 200, 200, 320);
      g.fillStyle = '#8b867c'; g.fillRect(600, 300, 80, 120); g.fillStyle = '#f2efe6'; g.fillRect(608, 365, 64, 50); // switch down = off
      { const k = ease(clamp((t - 0.5) / 0.25)); line([[700, H + 40], [668, 470 - k * 40 + 40]], '#111', 26); g.fillStyle = '#fff'; g.strokeStyle = '#111'; g.lineWidth = 6; g.beginPath(); g.arc(660, 440 - k * 40 + 40, 34, 0, 7); g.fill(); g.stroke(); } }
    vignette(0.8);
  },
  H(t, T) { cam(1.12 - 0.08 * t, 900, 300); sky(); highway(T); canopy(600, 160, 1, 1 + 0.15 * Math.sin(T * 40)); storeFront(830, 300, 1, true); [700, 820, 1060, 1170].forEach(x => pump(x, 410, 0.9));
    g.setTransform(1, 0, 0, 1, 0, 0); const bl = g.createRadialGradient(950, 190, 10, 950, 190, 500); bl.addColorStop(0, 'rgba(255,250,220,0.35)'); bl.addColorStop(1, 'rgba(255,250,220,0)'); g.fillStyle = bl; g.fillRect(0, 0, W, H); },
  I(t, T, pressed = false) { // outside, profile: zombie moving toward window
    cam(1 + 0.05 * t, 800, 360); g.fillStyle = '#2a1d22'; g.fillRect(0, 0, W, H);
    const gl = g.createLinearGradient(0, 0, W, 0); gl.addColorStop(0, 'rgba(255,248,215,0.55)'); gl.addColorStop(1, 'rgba(255,248,215,0.1)'); g.fillStyle = gl; g.fillRect(0, 0, W, H);
    // store wall + window on the right
    g.fillStyle = '#3b3036'; g.fillRect(940, 0, 340, H); g.fillStyle = '#05070c'; g.fillRect(960, 120, 300, 420); g.strokeStyle = 'rgba(255,250,230,0.25)'; g.lineWidth = 14; g.beginPath(); g.moveTo(1000, 540); g.lineTo(1080, 120); g.stroke();
    const k = pressed ? 1 : ease(t);
    const x = 560 + k * 270;
    figure({ x, y: 760, s: 2.2, ...ZOMBIE, lean: 14 + k * 10, armL: [-0.5, -0.2], armR: [-0.3, 0], look: [1, 0] });
    if (pressed) { g.fillStyle = 'rgba(147,160,141,0.35)'; g.beginPath(); g.ellipse(978, 320, 26, 60, 0, 0, 7); g.fill(); }
  },
  I2(t, T) { SH.I(t, T, true); },
  J(t, T) { // split: outside sees reflection | inside Sam hides inches away
    const LINE15 = LINES.find(l => l.id === 'L15'); const shotJ = shots.find(s => s.id === 'J');
    const rev = ease((T - (LINE15.start - 0.2)) / 0.8);
    // left half: outside view of glass — reflection reveal
    g.save(); g.beginPath(); g.rect(0, 0, W / 2 - 4, H); g.clip();
    g.fillStyle = '#c9bfa6'; g.fillRect(0, 0, W / 2, H);
    g.fillStyle = '#0b0f17'; g.fillRect(40, 40, W / 2 - 80, H - 80); // glass (dark)
    // reflection of his face in the glass (mirror)
    g.globalAlpha = 0.15 + rev * 0.65; figure({ x: 300, y: 1100, s: 3.4, ...ZOMBIE }); g.globalAlpha = 1;
    // his actual head from behind (foreground, out of focus)
    g.fillStyle = '#6f7d6c'; g.strokeStyle = '#111'; g.lineWidth = 8; g.beginPath(); g.arc(330, 760, 220, 0, 7); g.fill(); g.stroke();
    g.fillStyle = '#fff'; g.font = '30px "Archivo Black"'; g.fillText('WHAT HE SEES', 60, 92);
    g.restore();
    // right half: inside, Sam crouched right behind the glass
    g.save(); g.beginPath(); g.rect(W / 2 + 4, 0, W / 2, H); g.clip();
    g.fillStyle = '#070a12'; g.fillRect(W / 2, 0, W / 2, H);
    g.fillStyle = 'rgba(255,244,205,0.85)'; g.fillRect(W / 2 + 40, 40, W / 2 - 80, H - 80);
    g.fillStyle = 'rgba(111,125,108,0.95)'; g.beginPath(); g.arc(W / 2 + 330, 330, 95, 0, 7); g.fill(); // zombie face silhouette on glass from inside
    g.fillStyle = '#000'; g.beginPath(); g.ellipse(W / 2 + 300, 320, 14, 20, 0, 0, 7); g.ellipse(W / 2 + 360, 320, 14, 20, 0, 0, 7); g.fill();
    figure({ x: W / 2 + 290, y: 1030, s: 2.4, vest: true, headlamp: true, lampOn: false, face: 'scared', look: [0, -0.6] });
    g.fillStyle = '#fff'; g.font = '30px "Archivo Black"'; g.fillText('INSIDE', W / 2 + 60, 92);
    g.restore();
    g.fillStyle = '#000'; g.fillRect(W / 2 - 4, 0, 8, H);
  },
  K(t, T) { cam(1 + 0.06 * t, 300, 420, -t * 60); sky(); highway(T, 520, 418, 640, 1.6); vignette(0.8); },
  TITLE(t, T) { g.fillStyle = '#05060f'; g.fillRect(0, 0, W, H); const a = ease(t * 3);
    g.globalAlpha = a; g.textAlign = 'center';
    g.font = '120px "Archivo Black"'; g.lineWidth = 14; g.strokeStyle = '#000'; g.strokeText('LAST SHIFT', W / 2, 360); g.fillStyle = '#ffd54a'; g.fillText('LAST SHIFT', W / 2, 360);
    g.font = '40px "Archivo Black"'; g.fillStyle = '#fff'; g.fillText('PART 1 · THE LAST GAS STATION', W / 2, 430);
    g.textAlign = 'left'; g.globalAlpha = 1; },
};

function caption(T) {
  const cap = CAPS.find(c => T >= c.start && T < c.end); if (!cap) return;
  g.setTransform(1, 0, 0, 1, 0, 0); g.textAlign = 'center'; g.font = '40px "Archivo Black"'; g.lineJoin = 'round';
  g.lineWidth = 9; g.strokeStyle = '#000'; g.strokeText(cap.text, W / 2, H - 58); g.fillStyle = '#fff'; g.fillText(cap.text, W / 2, H - 58); g.textAlign = 'left';
}

// ---------------- render video ----------------
const NF = Math.ceil(TOTAL * FPS);
const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', `${W}x${H}`, '-r', String(FPS), '-i', '-', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-preset', 'medium', OUT + '/video_silent.mp4'], { stdio: ['pipe', 'inherit', 'inherit'] });
(async () => {
  for (let f = 0; f < NF; f++) {
    const T = f / FPS; const sh = shots.find(s => T >= s.start && T < s.end) || shots[shots.length - 1];
    const lt = clamp((T - sh.start) / Math.max(0.01, sh.end - sh.start));
    g.setTransform(1, 0, 0, 1, 0, 0); g.globalAlpha = 1; g.textAlign = 'left';
    SH[sh.id](lt, T);
    g.setTransform(1, 0, 0, 1, 0, 0);
    // quick flash on cut-ins for dramatic shots
    const since = T - sh.start; if (since < 0.08 && ['B', 'D2', 'I2'].includes(sh.id)) { g.fillStyle = 'rgba(255,255,255,0.35)'; g.fillRect(0, 0, W, H); }
    grain(T); caption(T);
    const buf = Buffer.from(g.getImageData(0, 0, W, H).data.buffer);
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));

  // ---------------- audio: voice + synthesized SFX/music ----------------
  const args = ['-y', '-loglevel', 'error'];
  LINES.forEach(L => args.push('-i', L.wav));
  const n = LINES.length;
  const D = TOTAL.toFixed(2);
  args.push('-f', 'lavfi', '-i', `sine=f=1318.5:d=1.6`, '-f', 'lavfi', '-i', `sine=f=1760:d=1.6`); // ding partials
  args.push('-f', 'lavfi', '-i', `sine=f=55:d=${D}`, '-f', 'lavfi', '-i', `sine=f=58.3:d=${D}`, '-f', 'lavfi', '-i', `sine=f=110:d=${D}`); // drone
  args.push('-f', 'lavfi', '-i', `anoisesrc=c=brown:a=0.3:d=${D}`); // wind
  args.push('-f', 'lavfi', '-i', `sine=f=120:d=${D}`); // canopy hum
  args.push('-f', 'lavfi', '-i', `sine=f=70:d=0.35`); // thump
  const fc = [];
  LINES.forEach((L, i) => fc.push(`[${i}:a]aresample=48000,volume=1.6,adelay=${Math.round(L.start * 1000)}|${Math.round(L.start * 1000)}[v${i}]`));
  const d = Math.round(dingT * 1000);
  fc.push(`[${n}:a][${n + 1}:a]amix=inputs=2,afade=t=out:st=0.05:d=1.5:curve=exp,volume=0.9,adelay=${d}|${d}[ding]`);
  fc.push(`[${n + 2}:a][${n + 3}:a][${n + 4}:a]amix=inputs=3,volume=0.45,afade=t=in:d=2,afade=t=out:st=${(TOTAL - 2).toFixed(2)}:d=2[drone]`);
  fc.push(`[${n + 5}:a]lowpass=f=380,volume=0.35[wind]`);
  fc.push(`[${n + 6}:a]volume=0.04,tremolo=f=8:d=0.3[hum]`);
  const th = Math.round(thumpT * 1000);
  fc.push(`[${n + 7}:a]afade=t=out:st=0.02:d=0.3,volume=1.4,adelay=${th}|${th}[thump]`);
  fc.push(`${LINES.map((_, i) => `[v${i}]`).join('')}[ding][drone][wind][hum][thump]amix=inputs=${n + 5}:normalize=0,alimiter=limit=0.9[aout]`);
  args.push('-filter_complex', fc.join(';'), '-map', '[aout]', '-t', D, '-ac', '2', '-ar', '48000', OUT + '/audio.wav');
  execFileSync('ffmpeg', args);
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', OUT + '/video_silent.mp4', '-i', OUT + '/audio.wav', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', OUT + '/opening-test.mp4']);
  fs.writeFileSync(OUT + '/timeline.json', JSON.stringify({ TOTAL, shots, lines: LINES.map(({ wav, ...r }) => r) }, null, 1));
  console.log('done', TOTAL.toFixed(1), 's,', NF, 'frames');
})();

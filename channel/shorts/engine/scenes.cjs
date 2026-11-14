// Scene definitions for the 30 Last Shift Shorts.
// Each scene: { hook, fact (sentence index of the fact), bed, sfx:[[name, sentence, offset, vol]], shots:[{at, draw, cam, shake, hit, sfx}] }
const C = require('./core.cjs');
const { W, H, g, clamp, ease, lerp, line, rect, circle, ell, vgrad, rgrad, glow, fig, crowd, P } = C;
const sh = (at, draw, o = {}) => ({ at, draw, ...o });
const HERO = (vest, extra = {}) => ({ kind: 'hero', headlamp: true, vest, ...extra });

// ---------- shared set pieces ----------
function pump(x, y, s = 1, opt = {}) {
  g.save(); g.translate(x, y); g.scale(s, s);
  rect(-14, 300, 148, 26, '#8f887a');
  rect(0, 0, 120, 300, '#f2efe6'); rect(0, 0, 120, 52, '#e94b3c');
  rect(22, 80, 76, 50, opt.lit ? '#7fe3a0' : '#26303b');
  g.strokeStyle = '#111'; g.lineWidth = 7; g.strokeRect(0, 0, 120, 300);
  rect(98, 150, 28, 60, '#333');
  if (!opt.empty) { rect(104, 140, 30, 80, '#1d1d1d'); line([[118, 220], [150, 290], [140, 330]], '#151515', 10); }
  if (opt.num) { circle(60, -34, 34, '#111'); g.fillStyle = '#ffd23f'; g.font = '48px "Archivo Black"'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(opt.num, 60, -32); g.textAlign = 'left'; g.textBaseline = 'alphabetic'; }
  g.restore();
}
function canopyLight(x0, x1, y, T, bright = 1) {
  g.fillStyle = rgrad((x0 + x1) / 2, y + 500, 50, 900, [[0, `rgba(255,244,200,${0.5 * bright})`], [1, 'rgba(255,244,200,0)']]); g.fillRect(-300, y, W + 600, 1400);
  rect(x0 + 60, y + 40, 34, 700, '#d8d2c4'); rect(x1 - 94, y + 40, 34, 700, '#d8d2c4');
  rect(x0, y - 50, x1 - x0, 60, '#e94b3c'); rect(x0, y + 10, x1 - x0, 26, '#f4f1e8');
  g.fillStyle = vgrad(y + 36, y + 260, [[0, `rgba(255,250,220,${0.95 * bright})`], [1, 'rgba(255,250,220,0)']]); g.fillRect(x0, y + 36, x1 - x0, 224);
}
function gasExterior(T, o = {}) {
  C.nightSky(T, '#04050d', '#141634', '#3a2340', 1100); C.moon(220, 300, 60);
  C.hills(1080, '#1b1426', 35, 2); C.ground(1100, '#2a1d22', '#120c10');
  // store
  rect(520, 860, 620, 420, '#3b3036'); rect(560, 920, 520, 300, o.storeLit ? '#ffd98a' : '#05070c');
  g.strokeStyle = 'rgba(255,250,230,0.16)'; g.lineWidth = 26; g.beginPath(); g.moveTo(610, 1220); g.lineTo(720, 920); g.moveTo(780, 1220); g.lineTo(850, 1030); g.stroke();
  g.strokeStyle = '#111'; g.lineWidth = 8; g.strokeRect(560, 920, 520, 300);
  rect(680, 820, 280, 50, '#e94b3c'); g.fillStyle = '#fff'; g.font = '40px "Archivo Black"'; g.fillText("SUNNY'S", 715, 860);
  canopyLight(-60, 900, 620, T, o.bright || 1);
  pump(120, 1000, 0.95, { num: '3' }); pump(470, 1000, 0.95, { num: '4', lit: o.p4lit, empty: o.p4empty });
  if (o.road) { g.fillStyle = '#1d1a20'; g.beginPath(); g.moveTo(-100, 1500); g.lineTo(W + 100, 1420); g.lineTo(W + 100, 1600); g.lineTo(-100, 1700); g.fill(); }
}
function storeInterior(T, o = {}) {
  C.room('#141a28', '#0b0f17', 1300, '#0c111d');
  // big window showing bright canopy
  const lit = o.lamp ? 1 : 0;
  rect(80, 260, 920, 760, '#fff1c8'); g.fillStyle = vgrad(260, 1020, [[0, 'rgba(255,250,225,1)'], [1, 'rgba(230,200,150,1)']]); g.fillRect(80, 260, 920, 760);
  rect(80, 260, 920, 50, '#e94b3c');
  rect(170, 700, 90, 300, '#c9c2b2'); rect(780, 700, 90, 300, '#c9c2b2');
  rect(70, 250, 940, 16, '#090c14'); rect(70, 1012, 940, 20, '#090c14'); rect(530, 250, 20, 780, '#090c14'); rect(70, 250, 16, 780, '#090c14'); rect(994, 250, 16, 780, '#090c14');
  if (o.reflect) { // window as mirror when store is lit
    g.fillStyle = `rgba(20,24,36,${0.75 * lit})`; g.fillRect(86, 266, 908, 746);
  }
  // counter
  rect(-100, 1320, W + 200, 600, '#1a1f2b'); rect(-100, 1300, W + 200, 30, '#252c3c');
  rect(700, 1190, 220, 115, '#2b3242'); rect(722, 1208, 110, 44, '#3a8f5a');
  if (o.lampDesk !== false) { // desk lamp
    line([[200, 1300], [230, 1180], [300, 1130]], '#333', 14); g.fillStyle = '#444'; g.beginPath(); g.moveTo(270, 1100); g.lineTo(350, 1110); g.lineTo(330, 1170); g.closePath(); g.fill();
    if (o.lamp) { g.save(); g.globalCompositeOperation = 'lighter'; g.fillStyle = rgrad(320, 1180, 10, 700, [[0, 'rgba(255,214,140,0.6)'], [1, 'rgba(255,214,140,0)']]); g.fillRect(-400, 500, 1500, 1500); g.restore(); }
  }
}

// ---------- SCENES ----------
const SC = {};

// 1. Pump Four
SC[1] = {
  hook: 'Never look at pump four after 2 AM', fact: 7, bed: 'hum',
  sfx: [['ding', 0, 1.9, 1.2], ['boom', 13, 0.1, 1], ['ding', 14, 3.2, 1.0]],
  shots: [
    sh(0, (lt, T) => gasExterior(T, { p4lit: Math.floor(T * 3) % 2 === 0 }), { cam: [1.0, 1.12], cy: 1100 }),
    sh(1, (lt, T) => { gasExterior(T, { p4empty: true }); }, { cam: [1.6, 1.75], cx: 530, cy: 1150, hit: true, sfx: ['whoosh'] }),
    sh(2, (lt, T) => { // man hugging the nozzle
      C.ground(0, '#3a2f2a', '#1c1512'); g.fillStyle = rgrad(540, 300, 100, 1300, [[0, 'rgba(255,248,215,0.65)'], [1, 'rgba(255,248,215,0)']]); g.fillRect(0, 0, W, H);
      pump(80, 500, 2.2, { num: '4', empty: true });
      line([[380, 950], [470, 1180], [600, 1100], [660, 980]], '#151515', 22);
      const sway = Math.sin(T * 1.5) * 6;
      fig({ x: 690 + sway, y: 1650, s: 2.6, kind: 'zombie', pose: 'hold', look: [1, 0], lean: -8 });
      g.save(); g.translate(660, 1150); g.rotate(-0.3); rect(-14, -30, 120, 48, '#2b2b2b'); g.restore();
    }, { cam: [1.05, 1.15], cy: 1100, sfx: [['creak', 0.4, 0.6]] }),
    sh(3, (lt, T) => { storeInterior(T); fig({ x: 540, y: 1560, s: 2.2, ...HERO('#2f5b3a'), pose: 'stand', face: 'shock', look: [0, -0.4] }); rect(-100, 1320, W + 200, 600, '#1a1f2b'); rect(-100, 1300, W + 200, 30, '#252c3c'); }, { cam: [1.15, 1.2], cy: 1100, hit: true, sfx: ['heartbeat'] }),
    sh(4, (lt, T) => { // light switch off
      C.room('#1b2230', '#0e121b', 1700); rect(390, 600, 300, 480, '#d9d4c8'); g.strokeStyle = '#111'; g.lineWidth = 10; g.strokeRect(390, 600, 300, 480);
      rect(480, 740, 120, 200, '#8b867c'); rect(492, 840 - 90 * (1 - ease(lt * 3)), 96, 86, '#f2efe6');
      const k = ease(clamp(lt * 2.5)); line([[700, H + 50], [620, 1050 - k * 120]], '#111', 30); circle(612, 1030 - k * 120, 40, '#fff', '#111', 7);
    }, { cam: [1.1, 1.0], sfx: [['click', 0.35]] }),
    sh(5, (lt, T) => gasExterior(T, { bright: 1.25 }), { cam: [1.3, 1.1], cy: 900 }),
    sh(6, (lt, T) => { // split: outside vs inside
      C.ground(0, '#3a2f2a', '#1c1512'); g.fillStyle = 'rgba(255,248,215,0.5)'; g.fillRect(0, 0, W, 960);
      rect(60, 640, 960, 300, '#0b0f17'); rect(60, 980, 960, 860, '#ffeec2');
      fig({ x: 300, y: 1700, s: 2.0, ...HERO('#2f5b3a'), pose: 'hide', face: 'scared', look: [1, -1] });
      fig({ x: 760, y: 1240, s: 2.4, kind: 'zombie', pose: 'reach', look: [-1, 0] });
      g.fillStyle = '#000'; g.fillRect(0, 955, W, 30);
    }, { cam: [1.0, 1.05], sfx: ['whoosh'] }),
    sh(8, (lt, T) => { // he sees only himself: mirror
      C.ground(0, '#c9bfa6', '#8b7f6a'); rect(90, 420, 900, 1300, '#0b0f17');
      g.globalAlpha = 0.65; fig({ x: 540, y: 2050, s: 4.2, kind: 'zombie', pose: 'stand', face: 'zombie' }); g.globalAlpha = 1;
      g.strokeStyle = 'rgba(255,255,255,0.12)'; g.lineWidth = 40; g.beginPath(); g.moveTo(200, 1700); g.lineTo(520, 420); g.stroke();
    }, { cam: [1.0, 1.1], cy: 1000 }),
    sh(10, (lt, T) => { // nose to the glass, smiling
      C.ground(0, '#c9bfa6', '#8b7f6a'); rect(0, 300, W, 1500, '#0b0f17');
      const k = ease(lt * 1.5); fig({ x: 540, y: 2100 - k * 60, s: 4.6, kind: 'zombie', pose: 'stand', face: k > 0.6 ? 'smile_z' : 'zombie' });
      if (k > 0.9) { g.fillStyle = 'rgba(255,255,255,0.18)'; g.beginPath(); g.ellipse(540, 1100, 50, 30, 0, 0, 7); g.fill(); }
    }, { cam: [1.0, 1.15], cy: 1050, sfx: [['tap', 1.6]] }),
    sh(11, (lt, T) => { storeInterior(T); fig({ x: 620, y: 1640, s: 2.3, ...HERO('#2f5b3a'), pose: 'hide', face: 'scared', look: [-1, 0] }); fig({ x: 330, y: 1680, s: 2.3, kind: 'kid', pose: () => ({ armL: [1.9, 1.8], armR: [-0.1, 0.0], legL: [1.75, 1.65], legR: [1.4, 1.5] }), dress: '#7aa7d8', face: 'neutral', look: [1, 0], hair: (x, y, r) => { circle(x - r * 0.9, y - r * 0.2, r * 0.35, '#3a2a1a'); circle(x + r * 0.9, y - r * 0.2, r * 0.35, '#3a2a1a'); } }); }, { cam: [1.1, 1.2], cy: 1350 }),
    sh(12, (lt, T) => { storeInterior(T, { lamp: true, reflect: true }); fig({ x: 300, y: 1680, s: 2.3, kind: 'kid', pose: 'point', dress: '#7aa7d8', face: 'happy', hair: (x, y, r) => { circle(x - r * 0.9, y - r * 0.2, r * 0.35, '#3a2a1a'); circle(x + r * 0.9, y - r * 0.2, r * 0.35, '#3a2a1a'); } }); fig({ x: 700, y: 1640, s: 2.3, ...HERO('#2f5b3a'), pose: 'scared', face: 'shock', look: [-1, 0] }); }, { cam: [1.15, 1.05], cy: 1300, hit: true, sfx: [['click', 0.1]] }),
    sh(13, (lt, T) => { // smile stops: now he sees in
      C.ground(0, '#2a2420', '#120e0c'); rect(0, 300, W, 1500, '#ffd98a');
      fig({ x: 540, y: 2080, s: 4.6, kind: 'zombie', pose: 'stand', face: 'zombie', look: [0, 0.3], eyeGlow: '#ff3b3b' });
    }, { cam: [1.0, 1.25], cy: 1000, shake: 8, hit: true }),
    sh(14, (lt, T) => gasExterior(T, { p4lit: true }), { cam: [1.15, 1.0], cy: 1100 }),
  ],
};

Object.assign(SC, require("./scenes_a.cjs"));
try { Object.assign(SC, require("./scenes_b.cjs")); } catch (e) { if (e.code !== "MODULE_NOT_FOUND") throw e; }
try { Object.assign(SC, require("./scenes_c.cjs")); } catch (e) { if (e.code !== "MODULE_NOT_FOUND") throw e; }
module.exports = SC;

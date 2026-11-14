const SK = '/root/.claude/skills/directing-stickman-videos';
const { createCanvas, GlobalFonts } = require(SK + '/node_modules/@napi-rs/canvas');
const fs = require('fs');
GlobalFonts.registerFromPath(SK + '/assets/fonts/ArchivoBlack.ttf', 'Archivo Black');

const W = 1280, H = 720;
const c = createCanvas(W, H);
const g = c.getContext('2d');
const out = process.argv[2];

// --- sky
let sky = g.createLinearGradient(0, 0, 0, 430);
sky.addColorStop(0, '#05060f'); sky.addColorStop(0.6, '#141634'); sky.addColorStop(1, '#3a2340');
g.fillStyle = sky; g.fillRect(0, 0, W, H);
// stars
let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
g.fillStyle = '#ffffff';
for (let i = 0; i < 120; i++) { g.globalAlpha = 0.3 + rnd() * 0.6; g.fillRect(rnd() * W, rnd() * 300, 2, 2); }
g.globalAlpha = 1;
// distant dark hills
g.fillStyle = '#1b1426';
g.beginPath(); g.moveTo(0, 420);
for (let x = 0; x <= W; x += 40) g.lineTo(x, 400 - Math.sin(x / 130) * 18 - Math.sin(x / 47) * 6);
g.lineTo(W, 440); g.lineTo(0, 440); g.fill();
// ground
let gr = g.createLinearGradient(0, 410, 0, H);
gr.addColorStop(0, '#2a1d22'); gr.addColorStop(1, '#120c10');
g.fillStyle = gr; g.fillRect(0, 410, W, H - 410);

// --- highway receding to left-horizon
const vx = 120, vy = 418;
g.fillStyle = '#1d1a20';
g.beginPath(); g.moveTo(vx - 6, vy); g.lineTo(vx + 6, vy); g.lineTo(560, H); g.lineTo(-140, H); g.fill();
g.strokeStyle = '#c9a646'; g.lineWidth = 4;
for (let t = 0.05; t < 1; t += 0.11) {
  const t2 = t + 0.05;
  const lerp = (a, b, t) => a + (b - a) * t;
  g.lineWidth = 1 + t * 7;
  g.beginPath(); g.moveTo(lerp(vx, 210, t * t), lerp(vy, H, t * t)); g.lineTo(lerp(vx, 210, t2 * t2), lerp(vy, H, t2 * t2)); g.stroke();
}

// --- the Walk: grey stick figures along highway
function walker(x, y, s, col, lean = 0) {
  g.save(); g.translate(x, y); g.scale(s, s);
  g.strokeStyle = col; g.fillStyle = col; g.lineWidth = 5; g.lineCap = 'round';
  // legs
  g.beginPath(); g.moveTo(0, -40); g.lineTo(-10, 0); g.moveTo(0, -40); g.lineTo(9, -2); g.stroke();
  // body
  g.beginPath(); g.moveTo(0, -40); g.lineTo(lean, -85); g.stroke();
  // arms reaching forward (zombie)
  g.beginPath(); g.moveTo(lean, -78); g.lineTo(lean - 26, -74); g.moveTo(lean, -74); g.lineTo(lean - 24, -66); g.stroke();
  // head
  g.beginPath(); g.arc(lean - 2, -100, 15, 0, Math.PI * 2); g.fill();
  g.restore();
}
for (let i = 0; i < 70; i++) {
  const t = Math.pow(i / 70, 1.6);
  const x = vx + (360 - vx) * t + (rnd() - 0.5) * (12 + t * 220);
  const y = vy + (H - 40 - vy) * t;
  const s = 0.08 + t * 1.05;
  const shade = Math.round(70 + t * 70);
  walker(x, y, s, `rgb(${shade},${shade + 6},${shade})`, 4);
}

// --- gas station canopy (right)
const cx0 = 600, cx1 = 1280;
// light pool on ground
let pool = g.createRadialGradient(950, 560, 40, 950, 560, 520);
pool.addColorStop(0, 'rgba(255,244,200,0.55)'); pool.addColorStop(1, 'rgba(255,244,200,0)');
g.fillStyle = pool; g.fillRect(400, 300, 880, 420);
// pillars
g.fillStyle = '#d8d2c4';
[[700, 'p'], [1180, 'p']].forEach(([x]) => g.fillRect(x - 12, 200, 24, 330));
// canopy slab
g.fillStyle = '#e94b3c'; g.fillRect(cx0, 160, cx1 - cx0, 34);
g.fillStyle = '#f4f1e8'; g.fillRect(cx0, 194, cx1 - cx0, 14);
// glow under canopy
let glow = g.createLinearGradient(0, 208, 0, 300);
glow.addColorStop(0, 'rgba(255,250,220,0.9)'); glow.addColorStop(1, 'rgba(255,250,220,0)');
g.fillStyle = glow; g.fillRect(cx0, 208, cx1 - cx0, 92);
// pumps
function pump(x) {
  g.fillStyle = '#f2efe6'; g.fillRect(x, 410, 58, 115);
  g.fillStyle = '#e94b3c'; g.fillRect(x, 410, 58, 22);
  g.fillStyle = '#26303b'; g.fillRect(x + 12, 444, 34, 22);
  g.strokeStyle = '#111'; g.lineWidth = 4; g.strokeRect(x, 410, 58, 115);
  g.fillStyle = '#9a9384'; g.fillRect(x - 10, 525, 78, 12);
}
pump(760); pump(1060);

// --- store front with dark window (right lower)
g.fillStyle = '#3b3036'; g.fillRect(830, 300, 450, 240);
g.fillStyle = '#05070c'; g.fillRect(860, 330, 390, 180);
// window reflection streaks
g.strokeStyle = 'rgba(255,250,230,0.18)'; g.lineWidth = 18;
g.beginPath(); g.moveTo(900, 510); g.lineTo(980, 330); g.moveTo(1010, 510); g.lineTo(1060, 400); g.stroke();
g.strokeStyle = '#111'; g.lineWidth = 6; g.strokeRect(860, 330, 390, 180);
g.beginPath(); g.moveTo(1055, 330); g.lineTo(1055, 510); g.stroke();
// two pairs of eyes in the dark window: Sam (headlamp) and Junie
function eyes(x, y, r) { g.fillStyle = '#ffffff'; g.beginPath(); g.ellipse(x - r * 1.4, y, r, r * 1.3, 0, 0, 7); g.ellipse(x + r * 1.4, y, r, r * 1.3, 0, 0, 7); g.fill(); g.fillStyle = '#000'; g.beginPath(); g.arc(x - r * 1.4 - 2, y + 2, r * 0.45, 0, 7); g.arc(x + r * 1.4 - 2, y + 2, r * 0.45, 0, 7); g.fill(); }
// Sam head silhouette + headlamp
g.fillStyle = '#e9e9e9'; g.beginPath(); g.arc(1150, 420, 44, 0, 7); g.fill();
g.strokeStyle = '#111'; g.lineWidth = 5; g.stroke();
g.fillStyle = '#222'; g.fillRect(1108, 388, 84, 12);
g.fillStyle = '#ffd54a'; g.beginPath(); g.arc(1150, 394, 11, 0, 7); g.fill(); g.strokeStyle = '#111'; g.lineWidth = 3; g.stroke();
g.fillStyle = '#111'; g.beginPath(); g.ellipse(1134, 424, 6, 10, 0, 0, 7); g.ellipse(1166, 424, 6, 10, 0, 0, 7); g.fill();
g.beginPath(); g.ellipse(1150, 448, 9, 6, 0, 0, 7); g.fill(); // gasp mouth
// Junie smaller head
g.fillStyle = '#e9e9e9'; g.beginPath(); g.arc(1210, 470, 30, 0, 7); g.fill(); g.strokeStyle = '#111'; g.lineWidth = 4; g.stroke();
g.fillStyle = '#111'; g.beginPath(); g.ellipse(1199, 472, 4.5, 7, 0, 0, 7); g.ellipse(1221, 472, 4.5, 7, 0, 0, 7); g.fill();
// darken the window area over heads a bit (they are inside)
g.fillStyle = 'rgba(5,7,12,0.25)'; g.fillRect(1056, 333, 191, 175);

// --- big foreground zombie: hunched, hands flat on the glass, reflection staring back
// faint reflection of his face in the window (what he sees)
g.save(); g.globalAlpha = 0.35; g.fillStyle = '#b9c4b2';
g.beginPath(); g.arc(968, 392, 48, 0, 7); g.fill();
g.globalAlpha = 0.6; g.fillStyle = '#000';
g.beginPath(); g.ellipse(950, 388, 9, 13, 0.2, 0, 7); g.ellipse(986, 388, 9, 13, -0.2, 0, 7); g.fill();
g.beginPath(); g.ellipse(968, 418, 14, 8, 0, 0, 7); g.fill();
g.restore();
const ZC = '#6f7d6c', ZO = '#141414';
g.lineCap = 'round'; g.lineJoin = 'round';
function limb(pts, w) { g.strokeStyle = ZO; g.lineWidth = w + 7; g.beginPath(); g.moveTo(...pts[0]); pts.slice(1).forEach(p => g.lineTo(...p)); g.stroke(); g.strokeStyle = ZC; g.lineWidth = w; g.beginPath(); g.moveTo(...pts[0]); pts.slice(1).forEach(p => g.lineTo(...p)); g.stroke(); }
// legs (planted on lot)
limb([[930, 560], [905, 625], [890, 690]], 14);
limb([[938, 560], [960, 630], [975, 690]], 14);
// hunched body
limb([[934, 562], [944, 500], [960, 452]], 18);
// arms up to the glass
limb([[958, 470], [905, 470], [880, 420]], 13);
limb([[962, 468], [1010, 452], [1030, 404]], 13);
// palms flat on glass
g.fillStyle = '#8d9a89'; g.strokeStyle = ZO; g.lineWidth = 4;
[[876, 410], [1033, 395]].forEach(([x, y]) => { g.beginPath(); g.ellipse(x, y, 19, 23, 0, 0, 7); g.fill(); g.stroke(); });
// head from behind, tilted, pressed to glass
g.fillStyle = ZC; g.beginPath(); g.ellipse(962, 418, 50, 54, -0.25, 0, 7); g.fill(); g.lineWidth = 6; g.stroke();
// torn collar
g.strokeStyle = '#3a2a2a'; g.lineWidth = 8; g.beginPath(); g.moveTo(935, 475); g.lineTo(952, 465); g.lineTo(972, 474); g.stroke();
// pale glow on the zombie from canopy
g.fillStyle = 'rgba(255,250,220,0.12)'; g.beginPath(); g.ellipse(950, 400, 40, 44, -0.25, 0, 7); g.fill();
// vignette
let v = g.createRadialGradient(W / 2, H / 2, 250, W / 2, H / 2, 820);
v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(0,0,0,0.75)');
g.fillStyle = v; g.fillRect(0, 0, W, H);

// --- text
function txt(s, x, y, size, fill, stroke, sw) {
  g.font = `${size}px "Archivo Black"`; g.textBaseline = 'alphabetic';
  g.lineJoin = 'round'; g.strokeStyle = stroke; g.lineWidth = sw; g.strokeText(s, x, y);
  g.fillStyle = fill; g.fillText(s, x, y);
}
txt('KEEP THE', 44, 128, 92, '#ffffff', '#000000', 16);
txt('LIGHTS ON', 44, 236, 112, '#ffd54a', '#000000', 18);
// red tag
g.save(); g.translate(48, 272); g.rotate(-0.03);
g.fillStyle = '#e02424'; g.fillRect(0, 0, 250, 64);
g.font = '40px "Archivo Black"'; g.fillStyle = '#fff'; g.fillText('NIGHT 30', 18, 47);
g.restore();

fs.writeFileSync(out, c.toBuffer('image/png'));
console.log('wrote', out);

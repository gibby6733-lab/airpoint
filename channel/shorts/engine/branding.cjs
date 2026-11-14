// Your Move Studio channel art: profile picture (800x800) and banner (2560x1440).
// Usage: node branding.cjs <outdir>
const SK = '/root/.claude/skills/directing-stickman-videos';
const { createCanvas, GlobalFonts } = require(SK + '/node_modules/@napi-rs/canvas');
GlobalFonts.registerFromPath(SK + '/assets/fonts/ArchivoBlack.ttf', 'Archivo Black');
GlobalFonts.registerFromPath(SK + '/assets/fonts/Anton.ttf', 'Anton');
const fs = require('fs'), path = require('path');
const OUT = path.resolve(process.argv[2] || 'branding'); fs.mkdirSync(OUT, { recursive: true });
const P = Math.PI;

function head(g, x, y, r, opts = {}) {
  // beam
  if (opts.beam) { const gr = g.createRadialGradient(x, y - r * 0.5, 10, x, y - r * 0.5, opts.beam); gr.addColorStop(0, 'rgba(255,236,150,0.55)'); gr.addColorStop(1, 'rgba(255,236,150,0)'); g.fillStyle = gr; g.beginPath(); g.moveTo(x, y - r * 0.5); g.arc(x, y - r * 0.5, opts.beam, -P / 2 - 0.55 + (opts.tilt || 0), -P / 2 + 0.55 + (opts.tilt || 0)); g.closePath(); g.fill(); }
  g.fillStyle = '#ffffff'; g.strokeStyle = '#0c0c0c'; g.lineWidth = r * 0.12; g.beginPath(); g.arc(x, y, r, 0, 2 * P); g.fill(); g.stroke();
  g.fillStyle = '#1b1b1b'; g.fillRect(x - r, y - r * 0.55, r * 2, r * 0.24);
  g.fillStyle = '#fff3a8'; g.beginPath(); g.arc(x, y - r * 0.43, r * 0.24, 0, 2 * P); g.fill(); g.lineWidth = r * 0.07; g.stroke();
  const gl = g.createRadialGradient(x, y - r * 0.43, 0, x, y - r * 0.43, r * 0.9); gl.addColorStop(0, 'rgba(255,240,170,0.6)'); gl.addColorStop(1, 'rgba(255,240,170,0)'); g.fillStyle = gl; g.fillRect(x - r, y - r * 1.4, r * 2, r * 2);
  // determined eyes + mouth
  g.fillStyle = '#0c0c0c'; [-1, 1].forEach(s => { g.beginPath(); g.ellipse(x + s * r * 0.3, y + r * 0.12, r * 0.12, r * 0.17, 0, 0, 2 * P); g.fill(); });
  g.lineWidth = r * 0.08; g.lineCap = 'round'; g.beginPath(); g.moveTo(x - r * 0.48, y - r * 0.12); g.lineTo(x - r * 0.15, y - r * 0.02); g.moveTo(x + r * 0.48, y - r * 0.12); g.lineTo(x + r * 0.15, y - r * 0.02); g.stroke();
  g.beginPath(); g.moveTo(x - r * 0.14, y + r * 0.5); g.lineTo(x + r * 0.14, y + r * 0.5); g.stroke();
}
function zombieHead(g, x, y, r, a = 1) { g.globalAlpha = a; g.fillStyle = '#93a08d'; g.strokeStyle = '#0c0c0c'; g.lineWidth = r * 0.12; g.beginPath(); g.arc(x, y, r, 0, 2 * P); g.fill(); g.stroke(); g.fillStyle = '#0c0c0c'; [-1, 1].forEach(s => { g.beginPath(); g.ellipse(x + s * r * 0.32, y, r * 0.2, r * 0.25, 0, 0, 2 * P); g.fill(); }); g.fillStyle = '#ff3b3b'; [-1, 1].forEach(s => { g.beginPath(); g.arc(x + s * r * 0.32, y - r * 0.05, r * 0.06, 0, 2 * P); g.fill(); }); g.fillStyle = '#0c0c0c'; g.beginPath(); g.ellipse(x, y + r * 0.5, r * 0.2, r * 0.12, 0, 0, 2 * P); g.fill(); g.globalAlpha = 1; }
function text(g, s, x, y, size, fill, font = 'Archivo Black', stroke = '#000', sw = 0, align = 'center') { g.font = `${size}px "${font}"`; g.textAlign = align; g.textBaseline = 'middle'; g.lineJoin = 'round'; if (sw) { g.strokeStyle = stroke; g.lineWidth = sw; g.strokeText(s, x, y); } g.fillStyle = fill; g.fillText(s, x, y); }

// ---------- profile picture ----------
{
  const S = 800, c = createCanvas(S, S), g = c.getContext('2d');
  const bg = g.createRadialGradient(S / 2, S * 0.45, 50, S / 2, S / 2, S * 0.75); bg.addColorStop(0, '#2a2350'); bg.addColorStop(1, '#07060f'); g.fillStyle = bg; g.fillRect(0, 0, S, S);
  zombieHead(g, 170, 600, 90, 0.55); zombieHead(g, 640, 610, 100, 0.55);
  head(g, S / 2, 360, 190, { beam: 520 });
  // text band (kept inside the circle crop)
  g.fillStyle = '#ffd23f'; g.beginPath(); g.roundRect(150, 590, 500, 120, 22); g.fill();
  text(g, 'YOUR MOVE', S / 2, 652, 78, '#111', 'Anton');
  fs.writeFileSync(path.join(OUT, 'profile-picture-800.png'), c.toBuffer('image/png'));
}

// ---------- banner ----------
{
  const Wd = 2560, Ht = 1440, c = createCanvas(Wd, Ht), g = c.getContext('2d');
  const sky = g.createLinearGradient(0, 0, 0, Ht); sky.addColorStop(0, '#05050d'); sky.addColorStop(0.55, '#171640'); sky.addColorStop(1, '#3a2340'); g.fillStyle = sky; g.fillRect(0, 0, Wd, Ht);
  let s = 7; const R = () => (s = (s * 16807) % 2147483647) / 2147483647;
  g.fillStyle = '#fff'; for (let i = 0; i < 400; i++) { g.globalAlpha = 0.2 + R() * 0.7; g.fillRect(R() * Wd, R() * Ht * 0.6, 3, 3); } g.globalAlpha = 1;
  // ground + crowd silhouettes along the bottom (outside the TV-only band they still look fine)
  g.fillStyle = '#120c10'; g.fillRect(0, 1020, Wd, 420);
  const pts = []; for (let i = 0; i < 46; i++) pts.push([R() * Wd, 1080 + R() * 330, 0.55 + R() * 0.8]); pts.sort((a, b) => a[1] - b[1]);
  for (const [x, y, sc] of pts) { const sh = Math.round(60 + (y - 1080) / 330 * 70); const col = `rgb(${sh},${sh + 12},${sh - 4})`; g.strokeStyle = col; g.lineCap = 'round'; g.lineWidth = 11 * sc;
    g.beginPath(); g.moveTo(x, y - 95 * sc); g.lineTo(x - 22 * sc, y); g.moveTo(x, y - 95 * sc); g.lineTo(x + 20 * sc, y); g.moveTo(x, y - 95 * sc); g.lineTo(x - 4 * sc, y - 170 * sc); g.moveTo(x - 4 * sc, y - 160 * sc); g.lineTo(x - 70 * sc, y - 150 * sc); g.moveTo(x - 4 * sc, y - 150 * sc); g.lineTo(x - 66 * sc, y - 138 * sc); g.stroke();
    g.fillStyle = `rgb(${sh + 25},${sh + 38},${sh + 18})`; g.beginPath(); g.arc(x - 8 * sc, y - 205 * sc, 34 * sc, 0, 2 * P); g.fill(); g.fillStyle = '#0c0c0c'; g.beginPath(); g.arc(x - 22 * sc, y - 208 * sc, 6 * sc, 0, 2 * P); g.arc(x - 2 * sc, y - 208 * sc, 6 * sc, 0, 2 * P); g.fill(); }
  // glowing canopy on the right
  const gl = g.createRadialGradient(2300, 1000, 50, 2050, 900, 700); gl.addColorStop(0, 'rgba(255,244,200,0.5)'); gl.addColorStop(1, 'rgba(255,244,200,0)'); g.fillStyle = gl; g.fillRect(1300, 300, 1260, 1140);
  g.fillStyle = '#e94b3c'; g.fillRect(2020, 760, 600, 46); g.fillStyle = '#f4f1e8'; g.fillRect(2020, 806, 600, 18); g.fillStyle = '#d8d2c4'; g.fillRect(2080, 824, 26, 260); g.fillRect(2440, 824, 26, 260);
  // safe area (1546 x 423 centered) holds the important content
  const cx = Wd / 2, cy = Ht / 2;
  head(g, cx - 560, cy, 150, { beam: 380 });
  text(g, 'YOUR MOVE STUDIO', cx + 120, cy - 60, 150, '#ffffff', 'Anton', '#000', 18);
  text(g, 'SURVIVAL STORIES  ·  REAL FACTS  ·  ONE CHOICE', cx + 120, cy + 70, 46, '#ffd23f', 'Archivo Black', '#000', 10);
  g.fillStyle = '#e02424'; g.beginPath(); g.roundRect(cx - 60, cy + 120, 360, 64, 14); g.fill();
  text(g, 'NEW SHORT DAILY', cx + 120, cy + 153, 34, '#fff', 'Archivo Black');
  fs.writeFileSync(path.join(OUT, 'banner-2560x1440.png'), c.toBuffer('image/png'));
  // preview with safe-area guide (not for upload)
  g.strokeStyle = 'rgba(0,255,120,0.8)'; g.lineWidth = 6; g.setLineDash([20, 14]); g.strokeRect(cx - 773, cy - 211, 1546, 423);
  fs.writeFileSync(path.join(OUT, 'banner-safe-area-preview.png'), c.toBuffer('image/png'));
}
console.log('ok', OUT);

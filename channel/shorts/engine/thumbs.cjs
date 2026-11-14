// Shorts cover thumbnails (1080x1920): strongest twist shot + bold title + "YOUR MOVE?" badge.
// Usage: node thumbs.cjs <outdir> [n ...]
const C = require('./core.cjs');
const { W, H, g, canvas } = C;
const fs = require('fs'), path = require('path');
const SCENES = require('./scenes.cjs');
const SCRIPTS = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'scripts.json'), 'utf8'));
const OUT = path.resolve(process.argv[2] || 'thumbs'); fs.mkdirSync(OUT, { recursive: true });
const list = process.argv.slice(3).map(Number); const ns = list.length ? list : SCRIPTS.map(s => s.n);
const SHORT_TITLE = { 1: 'DON\'T LOOK AT PUMP 4', 2: '13 HOOKS', 3: '10 SECONDS OF DARK', 4: '90 MINUTES OF RED', 5: 'SOMETHING IN THE TANK', 6: 'THEY FOLLOW NOISE', 7: 'LINE 4 IS RINGING', 8: 'SOMETHING IS DIGGING', 9: 'THE WRONG LIGHT', 10: 'THE RAIL WENT DEAD', 11: 'COLD FINGERS', 12: 'PRAY FOR LIGHTNING', 13: 'THE WALL STARTED ROLLING', 14: 'HIDING IN A T-REX', 15: 'THE ICE MELTED', 16: 'SOMEONE FOUND MY KEYS', 17: 'CAN I TAKE YOUR ORDER?', 18: 'THE WIND CHOSE', 19: 'HE PRESSED IT', 20: 'THE DEAD DON\'T GET COLD', 21: 'HE SAVED HIS WATER', 22: 'THERE WERE 13', 23: 'THEIR EYES WERE WRONG', 24: 'THE RUNG SNAPPED', 25: 'FIRE DOORS DON\'T LOCK', 26: 'TOO QUIET', 27: 'IT\'S COMING UP', 28: 'THE TIDE BROUGHT THEM BACK', 29: 'HE BIT ME IN THE CAR', 30: 'THEY WAITED TOO' };
for (const n of ns) {
  const sc = SCENES[n]; const shots = sc.shots;
  // default: last "hit" shot before the final question shot; fall back to the middle
  const PICK = { 12: 5, 15: 3, 22: 11 };
  let idx = PICK[n] !== undefined ? PICK[n] : sc.thumbShot; if (idx === undefined) { for (let i = shots.length - 2; i >= 1; i--) if (shots[i].hit) { idx = i; break; } } if (idx === undefined) idx = Math.floor(shots.length / 2);
  const sh = shots[idx];
  g.setTransform(1, 0, 0, 1, 0, 0); g.globalAlpha = 1; g.fillStyle = '#000'; g.fillRect(0, 0, W, H);
  g.save(); const cam = sh.cam || [1, 1.08]; const z = (cam[0] + cam[1]) / 2; const cx = sh.cx || W / 2, cy = sh.cy || H / 2; g.translate(cx, cy); g.scale(z, z); g.translate(-cx, -cy);
  sh.draw(0.75, 6.0, {}, sh); g.restore(); g.setTransform(1, 0, 0, 1, 0, 0);
  C.vignette(0.75, 380);
  // title block (top third, clear of the Shorts UI)
  g.fillStyle = 'rgba(0,0,0,0.55)'; g.fillRect(0, 180, W, 470);
  C.textBox(SHORT_TITLE[n], W / 2, 410, 120, '#ffffff', '#000', 22, 'Anton', 'center', 980);
  // badge
  g.fillStyle = '#ffd23f'; g.beginPath(); g.roundRect(W / 2 - 260, 1380, 520, 120, 24); g.fill();
  C.textBox('YOUR MOVE?', W / 2, 1442, 86, '#111', '#000', 0, 'Anton');
  fs.writeFileSync(path.join(OUT, `thumb${String(n).padStart(2, '0')}-${SCRIPTS.find(s => s.n === n).slug}.png`), canvas.toBuffer('image/png'));
}
console.log('thumbs', ns.length, OUT);

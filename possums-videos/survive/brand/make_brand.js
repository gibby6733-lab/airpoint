// usage: node survive/brand/make_brand.js <out_dir>  -> profile.png (800x800) + watermark.png (150x150, transparent)
const { chromium } = require('playwright'); const path = require('path');
(async () => {
  const out = path.resolve(process.argv[2] || '.');
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 800, height: 800 } });
  await pg.setContent('<canvas id="c" width="800" height="800"></canvas><style>html,body{margin:0;background:transparent}</style>');
  const draw = async (bg) => pg.evaluate(async (bg) => {
    await document.fonts.load('900 100px Inter');
    const c = document.getElementById('c'), x = c.getContext('2d'), C = 400; x.clearRect(0, 0, 800, 800);
    if (bg) { const g = x.createRadialGradient(C, C, 40, C, C, 560); g.addColorStop(0, '#16304f'); g.addColorStop(1, '#060b16'); x.fillStyle = g; x.fillRect(0, 0, 800, 800);
      x.strokeStyle = 'rgba(160,200,255,.12)'; x.lineWidth = 4; for (let i = 0; i < 6; i++) { x.beginPath(); for (let px = 0; px <= 800; px += 20) x.lineTo(px, 620 + i * 34 + Math.sin(px * .03 + i) * 6); x.stroke(); } }
    const R = bg ? 255 : 320, w = bg ? 92 : 120;
    // life ring: alternating red / white quarters
    x.save(); x.translate(C, C); x.shadowColor = 'rgba(0,0,0,.5)'; x.shadowBlur = bg ? 40 : 0;
    for (let i = 0; i < 8; i++) { x.strokeStyle = i % 2 ? '#f4f1ea' : '#e0392b'; x.lineWidth = w; x.beginPath(); x.arc(0, 0, R, i * Math.PI / 4 + .02, (i + 1) * Math.PI / 4 - .02); x.stroke(); }
    x.shadowColor = 'transparent';
    x.strokeStyle = 'rgba(0,0,0,.25)'; x.lineWidth = 4; [R - w / 2, R + w / 2].forEach(r => { x.beginPath(); x.arc(0, 0, r, 0, 7); x.stroke(); });
    // rope ties
    x.strokeStyle = '#d9b26a'; x.lineWidth = bg ? 12 : 16; for (let i = 0; i < 4; i++) { const a = i * Math.PI / 2 + Math.PI / 4; x.beginPath(); x.moveTo(Math.cos(a) * (R - w / 2 - 6), Math.sin(a) * (R - w / 2 - 6)); x.lineTo(Math.cos(a) * (R + w / 2 + 6), Math.sin(a) * (R + w / 2 + 6)); x.stroke(); }
    // gold question mark
    x.fillStyle = '#ffd24a'; x.font = `900 ${bg ? 300 : 380}px Inter`; x.textAlign = 'center'; x.textBaseline = 'middle';
    x.lineJoin = 'round'; x.lineWidth = bg ? 18 : 26; x.strokeStyle = '#0b1424'; x.strokeText('?', 0, bg ? 14 : 20); x.fillText('?', 0, bg ? 14 : 20);
    x.restore();
  }, bg);
  await draw(true); await pg.screenshot({ path: path.join(out, 'profile.png'), clip: { x: 0, y: 0, width: 800, height: 800 } });
  await draw(false); await pg.screenshot({ path: path.join(out, 'watermark_big.png'), clip: { x: 0, y: 0, width: 800, height: 800 }, omitBackground: true });
  await b.close();
  require('child_process').execFileSync('ffmpeg', ['-loglevel', 'error', '-y', '-i', path.join(out, 'watermark_big.png'), '-vf', 'scale=150:150', path.join(out, 'watermark.png')]);
  require('fs').unlinkSync(path.join(out, 'watermark_big.png'));
})();

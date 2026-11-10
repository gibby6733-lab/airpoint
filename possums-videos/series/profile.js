// usage: node series/profile.js series/<sport>/day01 out.png  -> 1080x1080 profile picture from TEAM.logo
const { chromium } = require('playwright'); const path = require('path');
(async () => {
  const [ep, out] = process.argv.slice(2);
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await pg.goto('file://' + path.resolve(ep, 'episode.html'));
  await pg.evaluate(async () => { await document.fonts.load('900 80px Inter');
    ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.clearRect(0, 0, W, H);
    ctx.fillStyle = TEAM.c2; ctx.fillRect(0, 0, 1080, 1080);
    ctx.save(); ctx.translate(540, 540);
    for (let i = 0; i < 16; i++) { ctx.rotate(Math.PI / 8); ctx.fillStyle = i % 2 ? 'rgba(255,255,255,.08)' : 'rgba(0,0,0,.06)'; ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(-120, -900); ctx.lineTo(120, -900); ctx.fill(); }
    ctx.restore();
    shadowOn(30, 14); ctx.fillStyle = 'rgba(0,0,0,0)'; TEAM.logo(540, 540, 380); ctx.shadowColor = 'transparent';
  });
  await pg.screenshot({ path: out, clip: { x: 0, y: 0, width: 1080, height: 1080 } });
  await b.close();
})();

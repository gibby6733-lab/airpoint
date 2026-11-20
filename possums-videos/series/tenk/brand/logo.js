// usage: node series/tenk/brand/logo.js  -> series/tenk/brand/logo.png (1080x1080 profile picture, circle-safe)
const { chromium } = require('playwright'); const path = require('path'); const fs = require('fs');
(async () => {
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await pg.goto('file://' + path.resolve(__dirname, '../engine.html'));
  const d = await pg.evaluate(async () => { await document.fonts.load('900 100px Inter');
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    const g = ctx.createRadialGradient(540, 470, 60, 540, 540, 760); g.addColorStop(0, '#5fd17a'); g.addColorStop(1, '#13703a'); ctx.fillStyle = g; ctx.fillRect(0, 0, 1080, 1080);
    ctx.save(); ctx.translate(540, 540); for (let i = 0; i < 24; i++) { ctx.rotate(Math.PI / 12); ctx.fillStyle = i % 2 ? 'rgba(255,255,255,.07)' : 'rgba(255,255,255,0)'; ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(-140, -900); ctx.lineTo(140, -900); ctx.fill(); } ctx.restore();
    [[170, 250, -.4], [910, 280, .35], [140, 640, .25], [950, 660, -.3]].forEach(([x, y, r]) => dollar(x, y, .85, r));
    person({ x: 540, y: 1420, s: 1.42, pose: 'cheer', face: 'money', emote: null }, 1.2);
    ctx.save(); ctx.translate(540, 880); ctx.rotate(-.04); box(-340, -88, 680, 176, '#1e2140', '#fff', 40, 10);
    txt('$1', -215, 4, 116, '#8fd18a', { stroke: 14 }); txt('→', -80, 0, 90, '#fff', { stroke: 12 }); txt('$10K', 150, 4, 116, '#ffe14a', { stroke: 14 }); ctx.restore();
    const c2 = document.createElement('canvas'); c2.width = c2.height = 1080; c2.getContext('2d').drawImage(cv, 0, 0); return c2.toDataURL('image/png'); });
  fs.writeFileSync(path.join(__dirname, 'logo.png'), Buffer.from(d.split(',')[1], 'base64')); await b.close(); console.log('wrote logo.png');
})();

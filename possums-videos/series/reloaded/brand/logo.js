// usage: node series/reloaded/brand/logo.js  -> series/reloaded/brand/logo.png (1080x1080 profile picture, circle-safe)
const { chromium } = require('playwright'); const path = require('path'); const fs = require('fs');
(async () => {
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await pg.goto('file://' + path.resolve(__dirname, '../engine.html'));
  const d = await pg.evaluate(async () => { await document.fonts.load('900 100px Inter');
    ctx.setTransform(1, 0, 0, 1, 0, 0); voidBg(1.2, '#0c0820', '#3a1a6a'); gridFloor(760, '#5ff2ff', 1.2, .2); pixels(1.2, 5, 40, -1, 100);
    portal(540, 470, 330, '#5ff2ff', 1.4, 1);
    person({ x: 540, y: 1300, s: 1.25, pose: 'shock', ...J, emote: null }, 1.1);
    ctx.save(); ctx.translate(540, 880); ctx.rotate(-.03); box(-330, -95, 660, 190, '#16061f', '#5ff2ff', 36, 10);
    txt('REALITY', 0, -38, 74, '#fff', { stroke: 10 }); txt('RELOADED', 0, 44, 74, '#ff4fd8', { stroke: 10 }); ctx.restore();
    const c2 = document.createElement('canvas'); c2.width = c2.height = 1080; c2.getContext('2d').drawImage(cv, 0, 0); return c2.toDataURL('image/png'); });
  fs.writeFileSync(path.join(__dirname, 'logo.png'), Buffer.from(d.split(',')[1], 'base64')); await b.close(); console.log('wrote logo.png');
})();

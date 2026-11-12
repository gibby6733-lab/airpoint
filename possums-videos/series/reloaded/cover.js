// usage: node series/reloaded/cover.js <ep_dir> "<top line>" "<bottom line 1>" "<bottom line 2>"  -> <ep_dir>/thumbnail.png (clean frame, no captions)
const { chromium } = require('playwright'); const path = require('path'); const fs = require('fs');
(async () => {
  const [dir, ep, b1, b2] = process.argv.slice(2);
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await pg.goto('file://' + path.resolve(dir, 'episode.html'));
  const d = await pg.evaluate(async ([ep, b1, b2]) => { await document.fonts.load('900 100px Inter'); TL = { lines: [] };
    ctx.setTransform(1, 0, 0, 1, 0, 0); const L = { scene: 'island', boss: [790, .66], blimp: [760, 0, 420], jx: 280, pose: 'shock', emote: '!', words: [], start: 0 };
    SC.island(L, .5, 2.0);
    const box2 = (y0, y1, line, fill) => { ctx.save(); ctx.fillStyle = fill; ctx.strokeStyle = line; ctx.lineWidth = 10; rr(90, y0, 900, y1 - y0, 40); ctx.fill(); ctx.stroke(); ctx.restore(); };
    box2(280, 640, '#5ff2ff', '#16061f'); txt('REALITY', 540, 360, 120, '#fff', { stroke: 16, sc: '#0a0618' }); txt('RELOADED', 540, 490, 120, '#ff4fd8', { stroke: 16, sc: '#0a0618' }); txt(ep, 540, 595, 54, '#5ff2ff', { stroke: 8, sc: '#0a0618' });
    box2(1330, 1600, '#ffe14a', '#16061f'); txt(b1, 540, 1415, 76, '#ffe14a', { stroke: 12, sc: '#0a0618', maxW: 840 }); txt(b2, 540, 1525, 76, '#fff', { stroke: 12, sc: '#0a0618', maxW: 840 });
    return cv.toDataURL('image/png'); }, [ep, b1, b2]);
  fs.writeFileSync(path.join(dir, 'thumbnail.png'), Buffer.from(d.split(',')[1], 'base64')); await b.close(); console.log('wrote', path.join(dir, 'thumbnail.png'));
})();

// usage: node survive/thumbnail.js <topic_dir> "TOPIC" [scene]  -> <topic_dir>/thumbnail.png (1080x1920 Shorts thumbnail)
// Draws the topic's hook scene with the episode engine, then a big "WOULD YOU SURVIVE <TOPIC>?" + "A or B?" badge.
const { chromium } = require('playwright'); const path = require('path'); const fs = require('fs');
(async () => {
  const dir = path.resolve(process.argv[2]), topic = (process.argv[3] || '').toUpperCase(), scene = process.argv[4] || 'impact';
  const tl = JSON.parse(fs.readFileSync(path.join(dir, 'timeline.json')));
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await pg.goto('file://' + path.join(dir, 'episode.html'));
  await pg.evaluate(async ({ tl, topic, scene }) => {
    await document.fonts.load('900 100px Inter'); setTimeline(tl);
    ctx.setTransform(1, 0, 0, 1, 0, 0); const beat = tl.beats.find(x => x.scene === scene) || tl.beats[0];
    (SC[scene] || SC.hook)({ ...beat, clock: null }, .45, 2.0);
    const g = ctx.createLinearGradient(0, 0, 0, 1920); g.addColorStop(0, 'rgba(0,0,0,.75)'); g.addColorStop(.45, 'rgba(0,0,0,.15)'); g.addColorStop(1, 'rgba(0,0,0,.65)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    txt('WOULD YOU', 540, 300, 150, '#fff', { stroke: 24, maxW: 980 });
    txt('SURVIVE', 540, 460, 170, '#ffe14a', { stroke: 26, maxW: 980 });
    // topic on 1-2 lines, as big as fits
    ctx.font = '900 150px Inter'; const words = (topic + '?').split(' '), lines = [''];
    for (const w of words) { const t2 = (lines[lines.length - 1] + ' ' + w).trim(); if (ctx.measureText(t2).width > 960 && lines[lines.length - 1]) lines.push(w); else lines[lines.length - 1] = t2; }
    lines.forEach((l, i) => txt(l, 540, 630 + i * 150, 150, '#fff', { stroke: 24, maxW: 980 }));
    // A or B badge
    withT(540, 1560, 1, -.05, () => { panel(-330, -110, 660, 220, '#c0392b', '#fff'); txt('A or B?', 0, 4, 120, '#fff', { stroke: 12 }); });
  }, { tl, topic, scene });
  await pg.screenshot({ path: path.join(dir, 'thumbnail.png'), clip: { x: 0, y: 0, width: 1080, height: 1920 } }); await b.close();
  console.log('wrote', path.join(dir, 'thumbnail.png'));
})();

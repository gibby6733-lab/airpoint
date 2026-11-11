// usage: node thumbnail.js <episode_dir> <day> -> <episode_dir>/thumbnail.png (1080x1920 cover for TikTok/Reels/Shorts)
const { chromium } = require('playwright'); const path = require('path'); const fs = require('fs');
(async () => {
  const dir = path.resolve(process.argv[2]), day = parseInt(process.argv[3] || '1');
  const tl = JSON.parse(fs.readFileSync(path.join(dir, 'timeline.json')));
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await pg.goto('file://' + path.join(dir, 'episode.html'));
  await pg.evaluate(async ({ tl, day }) => {
    await document.fonts.load('900 100px Inter'); setTimeline(tl);
    ctx.setTransform(1, 0, 0, 1, 0, 0); drawStadium(2.0, { excite: .6 });
    const g = ctx.createLinearGradient(0, 0, 0, 1920); g.addColorStop(0, 'rgba(0,0,0,.7)'); g.addColorStop(.4, 'rgba(0,0,0,.1)'); g.addColorStop(1, 'rgba(0,0,0,.6)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    const big = (s, y, size, color, rot = -.04) => withT(540, y, 1, rot, () => txt(s, 0, 0, size, color, { stroke: size * .17 }));
    if (day === 1) {
      drawCoach(540, 1480, 1.35, 0.1, { bounce: 0 });
      big('DAY 1', 250, 200, '#ffd43b');
      withT(540, 470, 1, .03, () => { ctx.fillStyle = '#ff4a4a'; rr(-470, -80, 940, 160, 26); ctx.fill(); ctx.strokeStyle = '#1b1b2f'; ctx.lineWidth = 10; ctx.stroke(); txt('WORST TEAM', 0, 4, 110, '#fff', { stroke: 12 }); });
      big('IN AMERICA', 640, 110, '#fff');
      withT(540, 1700, 1, -.03, () => { ctx.fillStyle = '#1f9d55'; rr(-360, -70, 720, 140, 30); ctx.fill(); ctx.strokeStyle = '#1b1b2f'; ctx.lineWidth = 8; ctx.stroke(); txt('$0 · 1 HELMET', 0, 4, 76, '#fff', { stroke: 8 }); });
    } else {
      const xs = [190, 420, 660, 900], who = [{ num: 1, skin: '#ffdbac' }, { num: 3, mustache: true, skin: '#f1c27d' }, { num: 12, skin: '#8d5524' }, { wide: 1.6, num: 55, skin: '#c68642', helmetSmall: true, face: 'sad' }];
      xs.forEach((x, i) => drawPlayer(x, 1500, i === 3 ? 1.15 : .95, { helmet: true, ...who[i] }));
      big('DAY 2', 250, 200, '#ffd43b');
      withT(540, 470, 1, .03, () => { ctx.fillStyle = '#1f9d55'; rr(-430, -85, 860, 170, 26); ctx.fill(); ctx.strokeStyle = '#1b1b2f'; ctx.lineWidth = 10; ctx.stroke(); txt('$403', 0, 4, 140, '#fff', { stroke: 14 }); });
      big('BOUGHT HELMETS', 650, 100, '#fff');
      withT(810, 1050, 1, .12, () => txt("LOU'S IS", 0, -55, 64, '#ff4a4a', { stroke: 12 })); withT(810, 1050, 1, .12, () => txt('TOO SMALL', 0, 15, 72, '#ff4a4a', { stroke: 12 }));
      withT(540, 1730, 1, -.03, () => { ctx.fillStyle = '#11a5ad'; rr(-440, -70, 880, 140, 30); ctx.fill(); ctx.strokeStyle = '#1b1b2f'; ctx.lineWidth = 8; ctx.stroke(); txt('+6 JOINED THE TEAM', 0, 4, 70, '#fff', { stroke: 8 }); });
    }
  }, { tl, day });
  await pg.screenshot({ path: path.join(dir, 'thumbnail.png'), clip: { x: 0, y: 0, width: 1080, height: 1920 } }); await b.close();
  console.log('wrote', path.join(dir, 'thumbnail.png'));
})();

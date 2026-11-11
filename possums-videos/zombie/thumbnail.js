// usage: node zombie/thumbnail.js <episode_dir> "BIG TEXT" -> <episode_dir>/thumbnail.png (1280x720)
// Draws one dramatic frame with the episode engine (night station, horde, a scared survivor) plus big title text.
const { chromium } = require('playwright'); const path = require('path'); const fs = require('fs');
(async () => {
  const dir = path.resolve(process.argv[2]); const big = process.argv[3] || 'THEY FOLLOWED US';
  const tl = JSON.parse(fs.readFileSync(path.join(dir, 'timeline.json')));
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  await pg.goto('file://' + path.resolve(__dirname, 'engine.html'));
  await pg.evaluate(async ({ tl, big }) => {
    await document.fonts.load('900 80px Inter'); setTimeline(tl);
    const beat = { loc: 'station_ext', tod: 'night', wx: null, cast: ['tank:.3:scared'], props: ['sign', 'pumps', 'lantern'], fx: [], z: { n: 14, x0: .78, x1: .78, depth: 'mid' }, cam: 1, camx: .5, card: null, hud: null, text: '' };
    ctx.setTransform(1, 0, 0, 1, 0, 0); sceneDraw(beat, .5, 3.3); grade(beat, 3.3);
    ctx.fillStyle = 'rgba(0,0,0,.35)'; ctx.fillRect(0, 0, W, H);
    txt(big, 1180, 230, 120, '#ffe14a', { stroke: 22, strokeColor: '#000' });
    txt('MILE 41', 1180, 380, 90, '#fff', { stroke: 16, strokeColor: '#000', font: SERIF, weight: 700 });
    ctx.fillStyle = '#c0392b'; ctx.fillRect(40, 40, 330, 90); txt('EPISODE ' + tl.episode, 205, 86, 50, '#fff');
  }, { tl, big });
  await pg.screenshot({ path: path.join(dir, 'thumb_full.png') });
  await pg.setViewportSize({ width: 1920, height: 1080 });
  await b.close();
  require('child_process').execFileSync('ffmpeg', ['-loglevel', 'error', '-y', '-i', path.join(dir, 'thumb_full.png'), '-vf', 'scale=1280:720', path.join(dir, 'thumbnail.png')]);
  fs.unlinkSync(path.join(dir, 'thumb_full.png')); console.log('wrote', path.join(dir, 'thumbnail.png'));
})();

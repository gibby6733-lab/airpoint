// usage: node zombie/series/thumb.js <part_dir>   (reads <part_dir>/thumb.json -> writes thumbnail.png, 1080x1920)
// thumb.json: {"t": seconds of the frame to use, "part": "PART 1", "top": [title lines], "hook": [2 short punchy lines]}
// All text stays inside the 3:4 band (y 240-1680) so TikTok / Instagram profile grids don't crop it.
const { chromium } = require('playwright'); const fs = require('fs'), path = require('path');
(async () => {
  const dir = path.resolve(process.argv[2]);
  const tl = JSON.parse(fs.readFileSync(path.join(dir, 'timeline.json'))), spec = JSON.parse(fs.readFileSync(path.join(dir, 'thumb.json')));
  const b = await chromium.launch(), p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  p.on('pageerror', e => { console.error(e); process.exit(1); });
  await p.goto('file://' + path.join(dir, 'episode.html'));
  await p.evaluate(async tl => { setTimeline(tl); await document.fonts.load('900 80px Inter'); }, tl);
  const d = await p.evaluate(s => { renderThumb(s.t, s); return document.getElementById('c').toDataURL('image/png'); }, spec);
  fs.writeFileSync(path.join(dir, 'thumbnail.png'), Buffer.from(d.split(',')[1], 'base64'));
  await b.close(); console.log('wrote', path.join(dir, 'thumbnail.png'));
})();

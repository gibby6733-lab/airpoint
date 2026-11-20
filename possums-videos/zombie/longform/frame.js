// usage: node zombie/longform/frame.js <dir> <t> <out.png>   (clean frame: no captions/HUD, for thumbnails)
const { chromium } = require('playwright'); const fs = require('fs'), path = require('path');
(async () => { const dir = path.resolve(process.argv[2]), t = +process.argv[3]; const tl = JSON.parse(fs.readFileSync(path.join(dir, 'timeline.json')));
  const b = await chromium.launch(), p = await b.newPage({ viewport: { width: 1920, height: 1080 } }); await p.goto('file://' + path.resolve(__dirname, 'engine.html'));
  const d = await p.evaluate(async ([tl, t]) => { setTimeline(tl); await document.fonts.load('900 80px Inter'); window.THUMB = true; renderFrame(t); return document.getElementById('c').toDataURL('image/png'); }, [tl, t]);
  fs.writeFileSync(process.argv[4], Buffer.from(d.split(',')[1], 'base64')); await b.close(); })();

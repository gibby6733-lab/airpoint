// usage: node render.js <episode_dir> [--stills t1,t2,...]
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs'), path = require('path');
(async () => {
  const dir = path.resolve(process.argv[2]);
  const tl = JSON.parse(fs.readFileSync(path.join(dir, 'timeline.json')));
  const stillsArg = process.argv.indexOf('--stills');
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  page.on('pageerror', e => { console.error('PAGE ERROR', e); process.exit(1); });
  await page.goto('file://' + path.join(dir, 'episode.html'));
  if (tl.images) { // pass images as data URLs (file:// images would taint the canvas)
    const data = {}; for (const f of tl.images) { const ext = path.extname(f).slice(1).toLowerCase().replace('jpg', 'jpeg');
      data[f] = `data:image/${ext};base64,` + fs.readFileSync(path.join(dir, 'images', f)).toString('base64'); }
    await page.evaluate(d => { window.IMG_DATA = d; }, data);
  }
  await page.evaluate(async tl => { setTimeline(tl); await document.fonts.load('900 80px Inter'); await document.fonts.load('700 40px Inter'); await document.fonts.load('800 40px Inter'); if (window.whenReady) await window.whenReady(); }, tl);
  const grab = t => page.evaluate(t => { renderFrame(t); return document.getElementById('c').toDataURL('image/jpeg', 0.92); }, t);
  if (stillsArg > 0) {
    const ts = process.argv[stillsArg + 1].split(',').map(Number);
    fs.mkdirSync(path.join(dir, 'stills'), { recursive: true });
    for (const t of ts) { const d = await grab(t); fs.writeFileSync(path.join(dir, 'stills', `t${t}.jpg`), Buffer.from(d.split(',')[1], 'base64')); }
    await browser.close(); return;
  }
  const FPS = 30, n = Math.ceil(tl.duration * FPS);
  const out = path.join(dir, 'episode.mp4');
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-i', path.join(dir, 'audio.wav'), '-vf', 'scale=1080:1920,setsar=1', '-aspect', '9:16', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p',
    '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-shortest', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let i = 0; i < n; i++) {
    const d = await grab(i / FPS);
    if (!ff.stdin.write(Buffer.from(d.split(',')[1], 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 150 === 0) console.log(`frame ${i}/${n}`);
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r));
  await browser.close(); console.log('wrote', out);
})();

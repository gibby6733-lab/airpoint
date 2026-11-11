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
  let server = null;
  if (tl.images) { // serve the story folder over http so images don't taint the canvas
    const http = require('http');
    server = http.createServer((req, res) => { const f = path.join(dir, decodeURIComponent(req.url.split('?')[0]));
      if (!f.startsWith(dir) || !fs.existsSync(f)) { res.writeHead(404); return res.end(); }
      const ext = path.extname(f).toLowerCase(); res.writeHead(200, { 'Content-Type': { '.html': 'text/html', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp' }[ext] || 'application/octet-stream' });
      fs.createReadStream(f).pipe(res); }).listen(0, '127.0.0.1');
    await new Promise(r => server.once('listening', r));
    await page.goto(`http://127.0.0.1:${server.address().port}/episode.html`);
  } else await page.goto('file://' + path.join(dir, 'episode.html'));
  await page.evaluate(async tl => { setTimeline(tl); await document.fonts.load('900 80px Inter'); await document.fonts.load('700 40px Inter'); await document.fonts.load('800 40px Inter'); if (window.whenReady) await window.whenReady(); }, tl);
  const grab = async t => { if (tl.images) await page.evaluate(t => window.prepare && window.prepare(t), t); return page.evaluate(t => { renderFrame(t); return document.getElementById('c').toDataURL('image/jpeg', 0.92); }, t); };
  if (stillsArg > 0) {
    const ts = process.argv[stillsArg + 1].split(',').map(Number);
    fs.mkdirSync(path.join(dir, 'stills'), { recursive: true });
    for (const t of ts) { const d = await grab(t); fs.writeFileSync(path.join(dir, 'stills', `t${t}.jpg`), Buffer.from(d.split(',')[1], 'base64')); }
    await browser.close(); if (server) server.close(); return;
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
  await browser.close(); if (server) server.close(); console.log('wrote', out);
})();

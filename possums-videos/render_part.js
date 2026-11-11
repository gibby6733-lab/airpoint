// usage: node render_part.js <episode_dir> <first_frame> <end_frame> <out.mp4>
// Renders a frame range (video only) so long videos can be rendered by several processes at once (see render_parallel.sh).
const { chromium } = require('playwright'); const { spawn } = require('child_process'); const fs = require('fs'), path = require('path');
(async () => {
  const [dirArg, a, z, out] = process.argv.slice(2); const dir = path.resolve(dirArg); const tl = JSON.parse(fs.readFileSync(path.join(dir, 'timeline.json')));
  const VW = tl.width || 1080, VH = tl.height || 1920, FPS = 30;
  const browser = await chromium.launch(); const page = await browser.newPage({ viewport: { width: VW, height: VH } });
  page.on('pageerror', e => { console.error('PAGE ERROR', e); process.exit(1); });
  await page.goto('file://' + path.join(dir, 'episode.html'));
  await page.evaluate(async tl => { setTimeline(tl); await document.fonts.load('900 80px Inter'); await document.fonts.load('700 40px Inter'); await document.fonts.load('800 40px Inter'); }, tl);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-', '-vf', `scale=${VW}:${VH},setsar=1`,
    '-c:v', 'libx264', '-preset', 'fast', '-crf', '20', '-pix_fmt', 'yuv420p', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let i = +a; i < +z; i++) {
    const d = await page.evaluate(t => { renderFrame(t); return document.getElementById('c').toDataURL('image/jpeg', 0.92); }, i / FPS);
    if (!ff.stdin.write(Buffer.from(d.split(',')[1], 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
    if ((i - a) % 600 === 0) console.log(`${path.basename(out)} ${i - a}/${z - a}`);
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r)); await browser.close(); console.log('done', out);
})();

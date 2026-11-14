// usage: node kids3d/render.js <episode_dir> --stills 1,5.5,12      -> <ep>/stills/t*.jpg
//        node kids3d/render.js <episode_dir> [--workers 4]           -> <ep>/episode.mp4 (1080x1920, fps from timeline)
// Serves kids3d/ over a tiny local HTTP server (ES modules need http), renders with headless Chromium + SwiftShader WebGL.
const { chromium } = require('playwright'); const http = require('http'), fs = require('fs'), path = require('path'); const { spawn, execFileSync } = require('child_process');
const ROOT = __dirname, ep = path.resolve(process.argv[2]), rel = path.relative(ROOT, ep), args = process.argv.slice(3);
const tl = JSON.parse(fs.readFileSync(path.join(ep, 'timeline.json'))); const FPS = tl.fps || 60, CRF = String(tl.crf || 17);
const TYPES = { '.mp3': 'audio/mpeg', '.js': 'text/javascript', '.html': 'text/html', '.ttf': 'font/ttf', '.json': 'application/json', '.png': 'image/png' };
function serve() { return new Promise(res => { const s = http.createServer((q, r) => { const f = path.join(ROOT, decodeURIComponent(q.url.split('?')[0])); if (!f.startsWith(ROOT) || !fs.existsSync(f)) { r.writeHead(404); return r.end(); } r.writeHead(200, { 'Content-Type': TYPES[path.extname(f)] || 'application/octet-stream' }); r.end(fs.readFileSync(f)); }); s.listen(0, () => res(s)); }); }
async function page(port) {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: tl.width || 1080, height: tl.height || 1920 } }); p.on('pageerror', e => { console.error('PAGE ERROR', e.message); process.exit(1); }); p.on('console', m => { if (m.type() === 'error') console.error('console:', m.text()); });
  await p.goto(`http://127.0.0.1:${port}/${rel}/episode.html`); await p.waitForFunction('window.renderFrame && window.ready'); await p.evaluate(async tl => { await window.ready; window.setTimeline(tl); }, tl); return { b, p };
}
const grab = (p, t, q = .92) => p.evaluate(([t, q]) => { renderFrame(t); return document.getElementById('c').toDataURL('image/jpeg', q); }, [t, q]);
(async () => {
  const srv = await serve(), port = srv.address().port;
  if (args[0] === '--stills') { const { b, p } = await page(port); fs.mkdirSync(path.join(ep, 'stills'), { recursive: true });
    for (const t of args[1].split(',').map(Number)) { const d = await grab(p, t); fs.writeFileSync(path.join(ep, 'stills', `t${t}.jpg`), Buffer.from(d.split(',')[1], 'base64')); }
    await b.close(); srv.close(); return; }
  if (args[0] === '--part') { const [a, z, out] = args.slice(1); const { b, p } = await page(port); const t0 = Date.now();
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-', '-c:v', 'libx264', '-preset', 'fast', '-crf', CRF, '-pix_fmt', 'yuv420p', out], { stdio: ['pipe', 'inherit', 'inherit'] });
    for (let i = +a; i < +z; i++) { const d = await grab(p, i / FPS); if (!ff.stdin.write(Buffer.from(d.split(',')[1], 'base64'))) await new Promise(r => ff.stdin.once('drain', r)); if ((i - a) % 300 === 0) console.log(path.basename(out), i - a, '/', z - a, Math.round((Date.now() - t0) / 1000) + 's'); }
    ff.stdin.end(); await new Promise(r => ff.on('close', r)); await b.close(); srv.close(); return; }
  // full render: split into parts rendered by child processes
  srv.close(); const N = +(args[args.indexOf('--workers') + 1] || 4) || 4, total = Math.ceil(tl.duration * FPS), tmp = path.join(ep, '_parts'); fs.rmSync(tmp, { recursive: true, force: true }); fs.mkdirSync(tmp);
  await Promise.all(Array.from({ length: N }, (_, i) => new Promise((res, rej) => { const a = Math.floor(total * i / N), z = Math.floor(total * (i + 1) / N);
    const c = spawn('node', [__filename, ep, '--part', a, z, path.join(tmp, `p${i}.mp4`)], { stdio: 'inherit' }); c.on('close', code => code ? rej(new Error('part ' + i)) : res()); })));
  fs.writeFileSync(path.join(tmp, 'list.txt'), Array.from({ length: N }, (_, i) => `file 'p${i}.mp4'`).join('\n'));
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', path.join(tmp, 'list.txt'), '-i', path.join(ep, 'audio.wav'), '-c:v', 'copy', '-aspect', (tl.width || 1080) > (tl.height || 1920) ? '16:9' : '9:16',
    '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-shortest', '-movflags', '+faststart', path.join(ep, 'episode.mp4')]);
  fs.rmSync(tmp, { recursive: true, force: true }); console.log('wrote', path.join(ep, 'episode.mp4'));
})();

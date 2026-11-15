const { chromium } = require('playwright');
const { spawn } = require('child_process');
(async () => {
  const FPS = 30;
  const b = await chromium.launch();
  const pg = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await pg.goto('file://' + process.cwd() + '/scene.html');
  await pg.evaluate(() => document.fonts.ready);
  const dur = await pg.evaluate(() => window.DURATION);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-i', 'vo1.mp3', '-i', 'music.wav',
    '-filter_complex', '[1:a]volume=1.6,apad[v];[2:a]volume=0.55[m];[v][m]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.95[a]',
    '-map', '0:v', '-map', '[a]', '-t', String(dur), '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
    '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', 'fogville.mp4'], { stdio: ['pipe', 'inherit', 'inherit'] });
  const total = Math.round(dur * FPS);
  for (let f = 0; f < total; f++) {
    const data = await pg.evaluate(t => { window.renderFrame(t); return document.getElementById('c').toDataURL('image/jpeg', 0.95); }, f / FPS);
    const ok = ff.stdin.write(Buffer.from(data.split(',')[1], 'base64'));
    if (!ok) await new Promise(r => ff.stdin.once('drain', r));
    if (f % 150 === 0) console.log('frame', f, '/', total);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await b.close();
})();

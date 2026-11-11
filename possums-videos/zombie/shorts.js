// Cut a vertical 9:16 YouTube Short from a long-form episode.
// usage: node zombie/shorts.js <episode_dir> <name> "<first line starts with>" "<last line starts with>" "HOOK TEXT"
// Re-renders those beats at 2x with the episode engine, crops a 9:16 window that follows the action,
// adds big captions, a series title bar and an end card pointing to the full episode. Writes <episode_dir>/shorts/<name>.mp4
const { chromium } = require('playwright'); const { spawn, execFileSync } = require('child_process');
const fs = require('fs'), path = require('path');
(async () => {
  const [dirArg, name, fromTxt, toTxt, hook] = process.argv.slice(2);
  const dir = path.resolve(dirArg), tl = JSON.parse(fs.readFileSync(path.join(dir, 'timeline.json')));
  const bi = tl.beats.findIndex(b => b.text.startsWith(fromTxt)), ei = tl.beats.findIndex(b => b.text.startsWith(toTxt));
  if (bi < 0 || ei < bi) throw new Error('could not find the start/end lines');
  const T0 = Math.max(0, tl.beats[bi].start - .4), T1 = tl.beats[ei].end + .6, END = 2.5, DUR = T1 - T0 + END;
  fs.mkdirSync(path.join(dir, 'shorts'), { recursive: true });
  const out = path.join(dir, 'shorts', name + '.mp4'), wav = path.join(dir, 'shorts', name + '.wav');
  // audio: the episode mix for that span + silence-padded end card
  execFileSync('ffmpeg', ['-loglevel', 'error', '-y', '-ss', String(T0), '-t', String(T1 - T0), '-i', path.join(dir, 'audio.wav'),
    '-af', `afade=t=in:d=0.3,afade=t=out:st=${(T1 - T0 - .6).toFixed(2)}:d=0.6,apad=pad_dur=${END}`, wav]);
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await pg.goto('file://' + path.resolve(__dirname, 'engine.html'));
  await pg.evaluate(async ({ tl, hook, ep }) => {
    await document.fonts.load('900 80px Inter'); await document.fonts.load('700 46px Inter');
    setTimeline(tl); SHORTS = true; setRenderScale(2);
    const oc = document.createElement('canvas'); oc.width = 1080; oc.height = 1920; window.OC = oc; const o = oc.getContext('2d');
    const t2 = (s, x, y, size, color, stroke) => { o.font = `900 ${size}px Inter`; o.textAlign = 'center'; o.textBaseline = 'middle'; if (stroke) { o.lineJoin = 'round'; o.lineWidth = stroke; o.strokeStyle = '#000'; o.strokeText(s, x, y); } o.fillStyle = color; o.fillText(s, x, y); };
    window.shortFrame = (t, fx, local, dur, endLen) => {
      renderFrame(t);
      const cw = 2160 * 9 / 16, sx = Math.max(0, Math.min(3840 - cw, fx * 3840 - cw / 2));
      o.drawImage(cv, sx, 0, cw, 2160, 0, 0, 1080, 1920);
      o.fillStyle = 'rgba(0,0,0,.55)'; o.fillRect(0, 0, 1080, 150); t2('MILE 41 · EPISODE ' + ep, 540, 78, 50, '#e8c46a');
      if (local < 2.2) { const a = Math.min(1, local * 3, (2.2 - local) * 3); o.globalAlpha = a; t2(hook, 540, 300, 72, '#ffe14a', 14); o.globalAlpha = 1; }
      const B = tl.beats.find(b => b.text && t >= b.start - .05 && t <= b.end + .2);
      if (B && local < dur - endLen) { const ws = B.words; let ci = ws.findIndex((w, i) => t >= w.s && (i === ws.length - 1 || t < ws[i + 1].s)); if (ci < 0) ci = 0;
        const c0 = Math.floor(ci / 3) * 3, chunk = ws.slice(c0, c0 + 3).map(w => w.w.toUpperCase()).join(' ');
        o.font = '900 84px Inter'; const wd = o.measureText(chunk).width, sc = Math.min(1, 980 / wd); o.save(); o.translate(540, 1500); o.scale(sc, sc); t2(chunk, 0, 0, 84, '#fff', 16); o.restore();
        if (B.sp !== 'cole') t2(B.name, 540, 1400, 44, { mags: '#7cd67c', dooley: '#e8c46a', pip: '#f6c84c', tank: '#6fb3ff', radio: '#9effa0' }[B.sp] || '#fff', 10); }
      if (local >= dur - endLen) { const a = Math.min(1, (local - (dur - endLen)) * 3); o.fillStyle = `rgba(7,8,11,${.85 * a})`; o.fillRect(0, 0, 1080, 1920); o.globalAlpha = a;
        o.font = "700 150px 'DejaVu Serif', serif"; o.textAlign = 'center'; o.fillStyle = '#e8e2d0'; o.fillText('MILE 41', 540, 820); o.fillStyle = '#c0392b'; o.fillRect(290, 880, 500, 10);
        t2('Full episode on our channel ▶', 540, 1020, 54, '#ffe14a', 10); t2('Like = 1 supply · Comment = your vote', 540, 1120, 40, '#ddd', 8); o.globalAlpha = 1; }
      return oc.toDataURL('image/jpeg', .92);
    };
  }, { tl, hook: hook || '', ep: tl.episode });
  const FPS = 30, n = Math.ceil(DUR * FPS);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-', '-i', wav,
    '-vf', 'scale=1080:1920,setsar=1', '-aspect', '9:16', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p',
    '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-shortest', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  let fx = null;
  for (let i = 0; i < n; i++) {
    const local = i / FPS, t = Math.min(T0 + local, T1);
    const target = await pg.evaluate(t => focusAt(t), t); fx = fx === null ? target : fx + (target - fx) * .06;   // smooth pan
    const d = await pg.evaluate(a => shortFrame(...a), [t, fx, local, DUR, END]);
    if (!ff.stdin.write(Buffer.from(d.split(',')[1], 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r)); await b.close(); fs.unlinkSync(wav);
  console.log('wrote', out, DUR.toFixed(1) + 's');
})();

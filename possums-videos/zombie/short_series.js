// Render a MILE 41 Shorts-series day (9:16, TikTok / YouTube Shorts) from its timeline.
// usage: node zombie/short_series.js <day_dir>   -> <day_dir>/episode.mp4
// The episode engine draws each frame at 2x; we crop a 9:16 window (beat.focus or the action) and add vertical
// overlays: DAY badge + SUPPLIES, name banners, supplies/vote/shop/join cards, big captions, follow card.
const { chromium } = require('playwright'); const { spawn } = require('child_process');
const fs = require('fs'), path = require('path');
(async () => {
  const dir = path.resolve(process.argv[2]), tl = JSON.parse(fs.readFileSync(path.join(dir, 'timeline.json')));
  const st = fs.existsSync(path.join(dir, 'state.json')) ? JSON.parse(fs.readFileSync(path.join(dir, 'state.json'))) : {};
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await pg.goto('file://' + path.resolve(__dirname, 'engine.html'));
  await pg.evaluate(async ({ tl, st }) => {
    await document.fonts.load('900 80px Inter'); await document.fonts.load('700 46px Inter'); await document.fonts.load("700 80px 'DejaVu Serif'");
    setTimeline(tl); SHORTS = true; setRenderScale(2);
    const oc = document.createElement('canvas'); oc.width = 1080; oc.height = 1920; const o = oc.getContext('2d');
    const T = (s, x, y, size, color, stroke, font) => { o.font = font || `900 ${size}px Inter`; o.textAlign = 'center'; o.textBaseline = 'middle'; if (stroke) { o.lineJoin = 'round'; o.lineWidth = stroke; o.strokeStyle = '#000'; o.strokeText(s, x, y); } o.fillStyle = color; o.fillText(s, x, y); };
    const box = (x, y, w, h, r, fill, line) => { o.save(); o.shadowColor = 'rgba(0,0,0,.6)'; o.shadowBlur = 24; o.fillStyle = fill; o.beginPath(); o.roundRect(x, y, w, h, r); o.fill(); o.shadowColor = 'transparent'; if (line) { o.strokeStyle = line; o.lineWidth = 5; o.stroke(); } o.restore(); };
    const ease = k => 1 - Math.pow(1 - Math.min(1, Math.max(0, k)), 3);
    const day = tl.day || 1, supplies = st.supplies ?? 0, shop = st.shop || [['WALLS', 100], ['GENERATOR', 150], ['WATCHTOWER', 200], ['FOOD RUN', 50]];
    window.vFrame = (t, fx) => {
      renderFrame(t);
      const cw = 2160 * 9 / 16, sx = Math.max(0, Math.min(3840 - cw, fx * 3840 - cw / 2)); o.drawImage(cv, sx, 0, cw, 2160, 0, 0, 1080, 1920);
      let i = 0; for (let j = 0; j < tl.beats.length; j++) if (t >= tl.beats[j].start - .2) i = j; const B = tl.beats[i], k = (t - B.start) / Math.max(.3, B.end - B.start);
      // top HUD
      box(36, 60, 230, 96, 26, '#c0392b', '#000'); T('DAY ' + day, 151, 109, 56, '#fff', 8);
      if (!st.hide_supplies) { box(610, 60, 434, 96, 26, 'rgba(14,16,20,.88)', '#e8c46a'); T('SUPPLIES', 760, 109, 34, '#e8c46a'); T(String(supplies), 960, 109, 56, supplies > 0 ? '#7cd67c' : '#ff6b6b'); }
      // name banner
      if (B.card && B.card.kind === 'name') { const e = ease(k * 3); o.save(); o.translate(0, (1 - e) * 60); o.globalAlpha = e; box(160, 1300, 760, 140, 20, 'rgba(10,12,16,.9)', '#c0392b'); T(B.card.title, 540, 1350, 66, '#e8c46a'); T(B.card.sub, 540, 1408, 36, '#eee', 0, '700 36px Inter'); o.restore(); }
      // hud cards
      if (B.hud) { const e = ease(k * 3); o.save(); o.globalAlpha = e; o.translate(0, (1 - e) * 50);
        if (B.hud === 'supplies') { box(120, 420, 840, 300, 34, 'rgba(14,16,20,.9)', '#e8c46a'); T('1 LIKE', 540, 520, 110, '#fff', 10); T('= 1 SUPPLY', 540, 640, 90, '#7cd67c', 10); }
        if (B.hud === 'vote') { box(100, 420, 880, 320, 34, 'rgba(14,16,20,.9)', '#e8c46a'); T('MOST-LIKED COMMENT', 540, 520, 64, '#fff', 8); T('DECIDES WHAT', 540, 610, 64, '#e8c46a', 8); T('WE BUILD NEXT', 540, 690, 64, '#e8c46a', 8); }
        if (B.hud === 'shop') { box(90, 300, 900, 160 + shop.length * 140, 34, 'rgba(14,16,20,.92)', '#e8c46a'); T('WHAT WE NEED', 540, 380, 64, '#e8c46a');
          const at = shop.map(([nm]) => { const key = nm.split(' ')[0].toLowerCase(); const w = B.words.find(w => w.w.toLowerCase().replace(/[^a-z]/g, '').startsWith(key)); return w ? (w.s - B.start) / (B.end - B.start) : 9; });
          shop.forEach(([n, p], q) => { const y = 480 + q * 140, nx = at.slice(q + 1).find(a => a < 9), on = at[q] < 9 && k >= at[q] - .02 && (nx === undefined || k < nx - .02);
            box(130, y - 54, 820, 108, 22, on ? '#e8c46a' : 'rgba(255,255,255,.08)'); o.textAlign = 'left'; o.textBaseline = 'middle';
            o.font = '900 54px Inter'; o.fillStyle = on ? '#111' : '#fff'; o.fillText(n, 160, y); o.textAlign = 'right'; o.font = '800 44px Inter'; o.fillStyle = on ? '#1b5e20' : '#7cd67c'; o.fillText(p + ' supplies', 920, y); o.textAlign = 'center'; }); }
        if (B.hud === 'wyr') { o.fillStyle = 'rgba(5,6,10,.55)'; o.fillRect(0, 0, 1080, 1920);
          T('WOULD YOU RATHER...', 540, 300, 74, '#ffe14a', 12);
          const wrapT = (str, cx, cy, size, maxW) => { o.font = `900 ${size}px Inter`; const ws = str.split(' '), ls = ['']; for (const w of ws) { const t2 = (ls[ls.length - 1] + ' ' + w).trim(); if (o.measureText(t2).width > maxW && ls[ls.length - 1]) ls.push(w); else ls[ls.length - 1] = t2; }
            ls.forEach((l, q) => T(l, cx, cy - (ls.length - 1) * size * .56 + q * size * 1.12, size, '#fff', 10)); };
          const e1 = ease(k * 4), e2 = ease(k * 4 - .6);
          o.save(); o.globalAlpha = e1; box(90, 400, 900, 300, 34, '#c0392b', '#fff'); wrapT(B.opt1, 540, 550, 62, 800); o.restore();
          o.save(); o.globalAlpha = e2; o.fillStyle = '#111'; o.beginPath(); o.arc(540, 775, 66, 0, 7); o.fill(); o.strokeStyle = '#ffe14a'; o.lineWidth = 6; o.stroke(); T('OR', 540, 777, 52, '#ffe14a');
          box(90, 850, 900, 300, 34, '#1f6f8b', '#fff'); wrapT(B.opt2, 540, 1000, 62, 800); o.restore();
          if (B.countdown) { const left = 3 - Math.floor(k * 3); o.save(); o.translate(540, 1300); o.strokeStyle = 'rgba(255,255,255,.2)'; o.lineWidth = 16; o.beginPath(); o.arc(0, 0, 90, 0, 7); o.stroke();
            o.strokeStyle = '#ffe14a'; o.beginPath(); o.arc(0, 0, 90, -Math.PI / 2, -Math.PI / 2 + (1 - k) * 6.283); o.stroke(); T(String(Math.max(1, left)), 0, 0, 110, '#fff'); o.restore(); }
          if (B.vote) T('VOTE IN THE POLL ▼', 540, 1300, 70, '#7cd67c', 12); }
        if (B.hud === 'join') { box(100, 420, 880, 330, 34, 'rgba(14,16,20,.9)', '#e8c46a'); T('JOIN THE SURVIVORS', 540, 510, 66, '#e8c46a', 8); T('Comment your NAME', 540, 610, 60, '#fff', 8); T('+ your SKILL', 540, 690, 60, '#7cd67c', 8); }
        o.restore(); }
      // captions
      const C = tl.beats.find(x => x.text && t >= x.start - .05 && t <= x.end + .2);
      if (C) { const ws = C.words; let ci = ws.findIndex((w, q) => t >= w.s && (q === ws.length - 1 || t < ws[q + 1].s)); if (ci < 0) ci = 0;
        const c0 = Math.floor(ci / 3) * 3, chunk = ws.slice(c0, c0 + 3); o.font = '900 86px Inter'; const parts = chunk.map(w => w.w.toUpperCase()), sp = 22;
        const ws2 = parts.map(p => o.measureText(p).width), tot = ws2.reduce((a, c) => a + c, 0) + sp * (parts.length - 1), fit = Math.min(1, 980 / tot); let x = 540 - tot * fit / 2;
        parts.forEach((p, q) => { o.save(); o.translate(x + ws2[q] * fit / 2, 1560); o.scale(fit, fit); T(p, 0, 0, 86, c0 + q === ci ? '#ffe14a' : '#fff', 16); o.restore(); x += (ws2[q] + sp) * fit; });
        if (C.sp !== 'cole') T(C.name, 540, 1455, 46, { mags: '#7cd67c', dooley: '#e8c46a', pip: '#f6c84c', tank: '#6fb3ff', radio: '#9effa0' }[C.sp] || '#fff', 10); }
      const last = tl.beats[tl.beats.length - 1];
      if (t > last.end + .2) { const e = ease((t - last.end - .2) / .4); o.save(); o.globalAlpha = e; box(180, 1640, 720, 140, 30, '#c0392b', '#000'); T('FOLLOW FOR DAY ' + (day + 1), 540, 1712, 60, '#fff', 8); o.restore(); }
      return oc.toDataURL('image/jpeg', .92);
    };
  }, { tl, st });
  const FPS = 30, n = Math.ceil(tl.duration * FPS), out = path.join(dir, 'episode.mp4');
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-', '-i', path.join(dir, 'audio.wav'),
    '-vf', 'scale=1080:1920,setsar=1', '-aspect', '9:16', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p',
    '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-shortest', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const stills = process.argv.indexOf('--stills');
  if (stills > 0) { fs.mkdirSync(path.join(dir, 'stills'), { recursive: true }); ff.stdin.end();
    for (const t of process.argv[stills + 1].split(',').map(Number)) { const f = await pg.evaluate(t => focusAt(t), t); const bb = tl.beats.filter(x => t >= x.start - .2).pop();
      const d = await pg.evaluate(a => vFrame(...a), [t, bb && bb.focus != null ? bb.focus : f]); fs.writeFileSync(path.join(dir, 'stills', `v${t}.jpg`), Buffer.from(d.split(',')[1], 'base64')); }
    await b.close(); return; }
  let fx = null;
  for (let i = 0; i < n; i++) {
    const t = i / FPS; const bb = tl.beats.filter(x => t >= x.start - .2).pop();
    const target = bb && bb.focus != null ? bb.focus : await pg.evaluate(t => focusAt(t), t);
    fx = fx === null ? target : fx + (target - fx) * .08;
    const d = await pg.evaluate(a => vFrame(...a), [t, fx]);
    if (!ff.stdin.write(Buffer.from(d.split(',')[1], 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r)); await b.close(); console.log('wrote', out);
})();

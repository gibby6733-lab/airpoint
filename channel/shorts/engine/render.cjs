// Render one Last Shift Short. Usage: node render.cjs <n> <narration.(mp3|wav)> <outdir> [--draft]
const C = require('./core.cjs');
const { W, H, g, canvas, clamp, ease } = C;
const { execFileSync, spawn } = require('child_process');
const fs = require('fs'), path = require('path');
const SCRIPTS = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'scripts.json'), 'utf8'));
const SCENES = require('./scenes.cjs');

const n = parseInt(process.argv[2], 10), AUDIO = process.argv[3], OUT = path.resolve(process.argv[4]);
const DRAFT = process.argv.includes('--draft');
const FPS = DRAFT ? 12 : 30;
fs.mkdirSync(OUT, { recursive: true });
const S = SCRIPTS.find(s => s.n === n);
const scene = SCENES[n];
if (!scene) throw new Error('no scene for ' + n);

// ---------- timing: sentences aligned to pauses in the narration ----------
const probe = f => parseFloat(execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]).toString());
const VO_DUR = probe(AUDIO);
const sentences = S.text.match(/[^.?!]+[.?!]+/g).map(s => s.trim());
const silLog = require('child_process').spawnSync('ffmpeg', ['-hide_banner', '-i', AUDIO, '-af', 'silencedetect=noise=-38dB:d=0.18', '-f', 'null', '-']).stderr.toString();
const gaps = []; let curStart = null;
for (const l of silLog.split('\n')) {
  let m = l.match(/silence_start: ([\d.]+)/); if (m) curStart = parseFloat(m[1]);
  m = l.match(/silence_end: ([\d.]+)/); if (m && curStart !== null) { gaps.push([curStart, parseFloat(m[1])]); curStart = null; }
}
const speechStart = gaps.length && gaps[0][0] < 0.05 ? gaps[0][1] : 0;
const speechEnd = gaps.length && gaps[gaps.length - 1][1] >= VO_DUR - 0.05 ? gaps[gaps.length - 1][0] : VO_DUR;
const inner = gaps.filter(([a, b]) => a > speechStart + 0.1 && b < speechEnd - 0.1).map(([a, b]) => ({ a, b, m: (a + b) / 2, used: false }));
const chars = sentences.map(s => s.length + 6); const totalC = chars.reduce((a, b) => a + b, 0);
const bounds = [speechStart]; let acc = 0;
for (let i = 0; i < sentences.length - 1; i++) {
  acc += chars[i]; const exp = speechStart + (speechEnd - speechStart) * acc / totalC;
  let best = null; for (const gp of inner) if (!gp.used && gp.m > bounds[bounds.length - 1] + 0.25) { if (!best || Math.abs(gp.m - exp) < Math.abs(best.m - exp)) best = gp; }
  if (best && Math.abs(best.m - exp) < 2.2) { best.used = true; bounds.push(best.m); } else bounds.push(exp);
}
bounds.push(speechEnd);
const LEAD = 0.35; // silence before narration starts in the final video
const SENT = sentences.map((t, i) => ({ text: t, start: bounds[i] + LEAD, end: bounds[i + 1] + LEAD }));
// words: distribute within sentence by character weight
const WORDS = [];
SENT.forEach(s => { const ws = s.text.split(/\s+/); const wt = ws.map(w => w.length + 2); const tot = wt.reduce((a, b) => a + b, 0); let t = s.start; const dur = (s.end - s.start) * 0.94; ws.forEach((w, i) => { const d = dur * wt[i] / tot; WORDS.push({ w, start: t, end: t + d, si: SENT.indexOf(s) }); t += d; }); });
const TOTAL = VO_DUR + LEAD + 1.2;

// caption chunks: up to 3 words, break at punctuation
const CHUNKS = []; { let cur = []; WORDS.forEach((w, i) => { cur.push(w); const next = WORDS[i + 1]; if (cur.length >= 3 || /[.,?!]$/.test(w.w) || !next || next.si !== w.si) { CHUNKS.push(cur); cur = []; } }); }

// ---------- shots ----------
const shots = scene.shots.map((sh, i) => ({ ...sh, start: i === 0 ? 0 : SENT[Math.min(sh.at, SENT.length - 1)].start - 0.08 + (sh.off || 0) }));
shots.forEach((s, i) => s.end = i + 1 < shots.length ? shots[i + 1].start : TOTAL);
const factIdx = scene.fact !== undefined ? scene.fact : 1;
const qIdx = SENT.length - 1;
const ctx = { S, SENT, WORDS, TOTAL, scene };

function drawCaption(T) {
  const ch = CHUNKS.find(c => T >= c[0].start - 0.02 && T < c[c.length - 1].end + 0.12); if (!ch) return;
  if (ch[0].si === qIdx) return; // question has its own card
  const age = T - ch[0].start; const pop = 1 + 0.12 * Math.max(0, 1 - age / 0.12);
  g.save(); g.translate(W / 2, 1440); g.scale(pop, pop);
  g.font = '86px "Archivo Black"'; g.textBaseline = 'middle'; g.lineJoin = 'round';
  const words = ch.map(w => w.w.toUpperCase()); const widths = words.map(w => g.measureText(w + ' ').width); let total = widths.reduce((a, b) => a + b, 0) - g.measureText(' ').width;
  let scale = total > 980 ? 980 / total : 1; g.scale(scale, scale);
  let x = -total / 2;
  words.forEach((w, i) => {
    const active = T >= ch[i].start && T < ch[i].end + 0.05;
    g.lineWidth = 18; g.strokeStyle = '#000'; g.strokeText(w, x, 0);
    g.fillStyle = active ? '#ffd23f' : '#ffffff'; g.fillText(w, x, 0); x += widths[i];
  });
  g.restore();
}
function drawHook(T) { // big title at the top for the first seconds
  const a = clamp(1 - (T - 2.6) / 0.3); if (a <= 0) return;
  g.save(); g.globalAlpha = a; const s = 1 + 0.06 * Math.max(0, 1 - T / 0.25);
  g.translate(W / 2, 330); g.scale(s, s);
  C.textBox(scene.hook.toUpperCase(), 0, 0, 92, '#ffffff', '#000', 20, 'Archivo Black', 'center', 940);
  g.restore();
}
function drawFact(T) {
  const st0 = SENT[factIdx]; if (!st0) return; const st = { start: Math.max(st0.start, 2.9), end: Math.max(st0.end, 6.5) }; const a = clamp((T - st.start) / 0.25) * clamp((st.end + 0.6 - T) / 0.3);
  if (a <= 0) return;
  g.save(); g.globalAlpha = a; const y = 250 - (1 - ease(clamp((T - st.start) / 0.3))) * 40;
  g.fillStyle = '#e02424'; const label = 'REAL FACT'; g.font = '50px "Archivo Black"'; const lw = g.measureText(label).width + 60;
  g.beginPath(); g.roundRect(W / 2 - lw / 2, y - 45, lw, 84, 18); g.fill();
  g.fillStyle = '#fff'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(label, W / 2, y); g.textAlign = 'left'; g.textBaseline = 'alphabetic';
  g.fillStyle = 'rgba(0,0,0,0.72)'; g.beginPath(); g.roundRect(50, y + 60, W - 100, 300, 26); g.fill();
  C.textBox(S.fact, W / 2, y + 210, 56, '#fff', '#000', 0, 'Archivo Black', 'center', W - 200);
  g.restore();
}
function drawQuestion(T) {
  const st = SENT[qIdx]; const a = clamp((T - st.start + 0.1) / 0.25); if (a <= 0) return;
  g.save(); g.globalAlpha = a; tintRect();
  const s = 0.9 + 0.1 * ease(clamp((T - st.start) / 0.35));
  g.translate(W / 2, 900); g.scale(s, s);
  const qh = C.textBox(st.text.toUpperCase(), 0, 0, 80, '#ffd23f', '#000', 20, 'Archivo Black', 'center', 900);
  C.textBox('COMMENT BELOW', 0, qh / 2 + 90, 54, '#ffffff', '#000', 14, 'Archivo Black', 'center', 920);
  g.restore();
}
function tintRect() { g.fillStyle = 'rgba(0,0,0,0.45)'; g.fillRect(0, 0, W, H); }

// ---------- render ----------
const NF = Math.ceil(TOTAL * FPS);
const vid = OUT + `/short${String(n).padStart(2, '0')}_video.mp4`;
const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', `${W}x${H}`, '-r', String(FPS), '-i', '-', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', DRAFT ? '28' : '19', '-preset', DRAFT ? 'veryfast' : 'medium', vid], { stdio: ['pipe', 'inherit', 'inherit'] });
(async () => {
  for (let f = 0; f < NF; f++) {
    const T = f / FPS;
    const sh = shots.find(s => T >= s.start && T < s.end) || shots[shots.length - 1];
    const lt = clamp((T - sh.start) / Math.max(0.01, sh.end - sh.start));
    g.setTransform(1, 0, 0, 1, 0, 0); g.globalAlpha = 1; g.globalCompositeOperation = 'source-over';
    g.fillStyle = '#000'; g.fillRect(0, 0, W, H);
    g.save();
    // camera
    const cam = sh.cam || [1, 1.08]; const z = cam[0] + (cam[1] - cam[0]) * ease(lt);
    const cx = sh.cx || W / 2, cy = sh.cy || H / 2;
    let shx = 0, shy = 0; if (sh.shake) { const k = typeof sh.shake === 'number' ? sh.shake : 10; shx = (Math.random() - 0.5) * k; shy = (Math.random() - 0.5) * k; }
    g.translate(cx + shx, cy + shy); g.scale(z, z); g.translate(-cx, -cy);
    sh.draw(lt, T, ctx, sh);
    g.restore(); g.setTransform(1, 0, 0, 1, 0, 0);
    if (sh.post) sh.post(lt, T, ctx);
    const since = T - sh.start; if (since < 0.07 && sh.hit) C.flash(0.35);
    C.vignette(0.55); C.grain(0.03);
    drawHook(T); drawFact(T); drawCaption(T); drawQuestion(T);
    const buf = Buffer.from(g.getImageData(0, 0, W, H).data.buffer);
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r));

  // ---------- audio: narration + bed + sfx ----------
  const SFX = require('./sfx.cjs');
  const events = [];
  shots.forEach(s => (s.sfx || []).forEach(e => { const [name, off = 0, vol = 1] = Array.isArray(e) ? e : [e]; events.push({ name, t: s.start + off, vol }); }));
  (scene.sfx || []).forEach(([name, si, off = 0, vol = 1]) => events.push({ name, t: (si === 'end' ? TOTAL - 1.2 : SENT[si].start) + off, vol }));
  const mixed = OUT + `/short${String(n).padStart(2, '0')}_audio.wav`;
  SFX.mix({ narration: AUDIO, lead: LEAD, total: TOTAL, bed: scene.bed || 'drone', events, out: mixed });
  const final = OUT + `/short${String(n).padStart(2, '0')}-${S.slug}.mp4`;
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', vid, '-i', mixed, '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', final]);
  fs.unlinkSync(vid);
  // SRT captions
  const ts = s => { const ms = Math.round(s * 1000); const p = (x, l = 2) => String(x).padStart(l, '0'); return `${p(Math.floor(ms / 3600000))}:${p(Math.floor(ms / 60000) % 60)}:${p(Math.floor(ms / 1000) % 60)},${p(ms % 1000, 3)}`; };
  fs.writeFileSync(final.replace('.mp4', '.srt'), SENT.map((s, i) => `${i + 1}\n${ts(s.start)} --> ${ts(s.end)}\n${s.text}\n`).join('\n'));
  fs.writeFileSync(OUT + `/short${String(n).padStart(2, '0')}_timing.json`, JSON.stringify({ TOTAL, SENT, shots: shots.map(s => ({ at: s.at, start: s.start, end: s.end })) }, null, 1));
  console.log('rendered', path.basename(final), TOTAL.toFixed(1) + 's');
})();

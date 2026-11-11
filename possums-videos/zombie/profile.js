// usage: node zombie/profile.js out.png  -> 1080x1080 channel profile picture (circle-crop safe)
const { chromium } = require('playwright'); const path = require('path');
(async () => {
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  await pg.goto('file://' + path.resolve(__dirname, 'engine.html'));
  await pg.evaluate(async () => {
    await document.fonts.load('900 80px Inter'); await document.fonts.load("700 80px 'DejaVu Serif'");
    ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.clearRect(0, 0, W, H);
    // night sky with red horizon glow
    const g = ctx.createRadialGradient(540, 760, 60, 540, 600, 760); g.addColorStop(0, '#7a1c16'); g.addColorStop(.45, '#2a0f14'); g.addColorStop(1, '#07080d');
    ctx.fillStyle = g; ctx.fillRect(0, 0, 1080, 1080);
    const r = rng(9); ctx.fillStyle = '#fff'; for (let i = 0; i < 70; i++) { ctx.globalAlpha = .2 + r() * .5; ctx.fillRect(r() * 1080, r() * 420, 3, 3); } ctx.globalAlpha = 1;
    ctx.fillStyle = '#e8e6d8'; ctx.beginPath(); ctx.arc(800, 220, 70, 0, 7); ctx.fill(); ctx.fillStyle = '#12060a'; ctx.beginPath(); ctx.arc(830, 200, 66, 0, 7); ctx.fill();
    // horde silhouettes on the horizon
    ctx.fillStyle = '#0b0507'; ctx.fillRect(0, 820, 1080, 260);
    for (let i = 0; i < 9; i++) { const x = 90 + i * 110 + (i % 2) * 20, s = .55 + (i % 3) * .08; ctx.save(); ctx.translate(x, 830); ctx.scale(s, s); ctx.beginPath(); ctx.arc(0, -150, 34, 0, 7); ctx.fill(); ctx.fillRect(-30, -120, 60, 120); ctx.save(); ctx.rotate(-1.4); ctx.fillRect(40, 10, 90, 18); ctx.restore(); ctx.restore(); }
    // mile marker sign
    ctx.save(); ctx.translate(540, 470); ctx.rotate(-.06);
    ctx.fillStyle = '#5a5a5a'; ctx.fillRect(-16, 120, 32, 460);
    ctx.shadowColor = 'rgba(0,0,0,.7)'; ctx.shadowBlur = 40; ctx.fillStyle = '#1e6b45'; rr(-260, -230, 520, 380, 34); ctx.fill(); ctx.shadowColor = 'transparent';
    ctx.strokeStyle = '#f2efe6'; ctx.lineWidth = 12; rr(-236, -206, 472, 332, 24); ctx.stroke();
    txt('MILE', 0, -120, 92, '#f2efe6');
    txt('41', 0, 20, 210, '#f2efe6', { font: "'DejaVu Serif', serif", weight: 700 });
    // scratches, rust, a bullet hole
    ctx.strokeStyle = 'rgba(10,30,20,.6)'; ctx.lineWidth = 6; ctx.beginPath(); ctx.moveTo(-200, -60); ctx.lineTo(-90, 40); ctx.moveTo(120, -180); ctx.lineTo(220, -110); ctx.moveTo(60, 90); ctx.lineTo(170, 130); ctx.stroke();
    ctx.fillStyle = 'rgba(150,70,30,.75)'; [[-210, 110, 34], [215, -190, 26], [180, 105, 20]].forEach(([x, y, rr2]) => { ctx.beginPath(); ctx.arc(x, y, rr2, 0, 7); ctx.fill(); });
    ctx.fillStyle = '#0b0507'; ctx.beginPath(); ctx.arc(150, -40, 13, 0, 7); ctx.fill();
    ctx.restore();
    // zombie hand reaching up at the sign
    ctx.save(); ctx.translate(250, 1000); ctx.rotate(.18); ctx.fillStyle = '#6f8f5c';
    rr(-44, -330, 88, 340, 30); ctx.fill(); ctx.beginPath(); ctx.ellipse(0, -360, 70, 62, 0, 0, 7); ctx.fill();
    [[-58, -440, -.35], [-22, -470, -.1], [16, -468, .1], [52, -442, .35]].forEach(([x, y, a]) => { ctx.save(); ctx.translate(x, y); ctx.rotate(a); rr(-14, -60, 28, 100, 14); ctx.fill(); ctx.restore(); });
    ctx.save(); ctx.translate(80, -360); ctx.rotate(.9); rr(-14, -50, 28, 80, 14); ctx.fill(); ctx.restore();
    ctx.fillStyle = '#5b4a6a'; ctx.beginPath(); ctx.moveTo(-60, -160); ctx.lineTo(60, -150); ctx.lineTo(64, 20); ctx.lineTo(-64, 20); ctx.closePath(); ctx.fill();
    ctx.restore();
    // subtle vignette
    const v = ctx.createRadialGradient(540, 540, 300, 540, 540, 760); v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(0,0,0,.6)'); ctx.fillStyle = v; ctx.fillRect(0, 0, 1080, 1080);
  });
  await pg.screenshot({ path: process.argv[2], clip: { x: 0, y: 0, width: 1080, height: 1080 } });
  await b.close();
})();

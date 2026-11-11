// usage: node discord_icon.js out.png  -> 1024x1024 server icon for "Your Move Studio" (clean, modern, flat)
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1024, height: 1024 } });
  await pg.setContent('<canvas id="c" width="1024" height="1024"></canvas><style>body{margin:0}</style>');
  await pg.evaluate(async () => {
    await document.fonts.load('800 100px Inter');
    const c = document.getElementById('c'), x = c.getContext('2d'), C = 512;
    // flat near-black background with a very soft centre lift
    x.fillStyle = '#0f1115'; x.fillRect(0, 0, 1024, 1024);
    const bg = x.createRadialGradient(C, C, 0, C, C, 620); bg.addColorStop(0, 'rgba(255,255,255,.05)'); bg.addColorStop(1, 'rgba(255,255,255,0)'); x.fillStyle = bg; x.fillRect(0, 0, 1024, 1024);
    // rounded play triangle (optically centred), coral -> amber gradient
    const r = 80, P = [[-175, -290], [-175, 290], [325, 0]].map(([a, b2]) => [C - 40 + a, C + b2]);
    const grad = x.createLinearGradient(P[0][0], P[0][1], P[2][0], P[1][1]); grad.addColorStop(0, '#ff5a5f'); grad.addColorStop(1, '#ffb547');
    x.beginPath();
    for (let i = 0; i < 3; i++) { const p0 = P[(i + 2) % 3], p1 = P[i], p2 = P[(i + 1) % 3];
      const v1 = [p0[0] - p1[0], p0[1] - p1[1]], v2 = [p2[0] - p1[0], p2[1] - p1[1]], l1 = Math.hypot(...v1), l2 = Math.hypot(...v2);
      const a = [p1[0] + v1[0] / l1 * r, p1[1] + v1[1] / l1 * r], bb = [p1[0] + v2[0] / l2 * r, p1[1] + v2[1] / l2 * r];
      if (i === 0) x.moveTo(...a); else x.lineTo(...a); x.quadraticCurveTo(p1[0], p1[1], ...bb); }
    x.closePath(); x.shadowColor = 'rgba(255,110,80,.35)'; x.shadowBlur = 80; x.fillStyle = grad; x.fill(); x.shadowColor = 'transparent';
    // small monogram inside, set in the dark background colour
    x.fillStyle = '#0f1115'; x.font = '800 172px Inter'; x.textAlign = 'center'; x.textBaseline = 'middle';
    x.save(); x.translate(C - 22, C + 4); x.scale(1, 1); x.fillText('YM', 0, 0); x.restore();
  });
  await pg.screenshot({ path: process.argv[2], clip: { x: 0, y: 0, width: 1024, height: 1024 } }); await b.close();
})();

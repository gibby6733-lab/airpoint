// usage: node survive/brand/make_banner.js out.png  -> 2560x1440 YouTube banner (key content inside the 1546x423 safe area)
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 2560, height: 1440 } });
  await pg.setContent('<canvas id="c" width="2560" height="1440"></canvas><style>html,body{margin:0}</style>');
  await pg.evaluate(async () => {
    await document.fonts.load('900 100px Inter'); await document.fonts.load('700 50px Inter');
    const c = document.getElementById('c'), x = c.getContext('2d'), W = 2560, H = 1440, CX = 1280, CY = 720;
    let s = 7; const r = () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296);
    const sky = x.createLinearGradient(0, 0, 0, 900); sky.addColorStop(0, '#03060f'); sky.addColorStop(1, '#16294a'); x.fillStyle = sky; x.fillRect(0, 0, W, 900);
    x.fillStyle = '#fff'; for (let i = 0; i < 380; i++) { x.globalAlpha = .2 + r() * .6; x.fillRect(r() * W, r() * 820, 3, 3); } x.globalAlpha = 1;
    x.fillStyle = '#e8e6d8'; x.beginPath(); x.arc(2150, 260, 70, 0, 7); x.fill(); x.fillStyle = '#060b18'; x.beginPath(); x.arc(2178, 242, 66, 0, 7); x.fill();
    const sea = x.createLinearGradient(0, 860, 0, H); sea.addColorStop(0, '#0d2340'); sea.addColorStop(1, '#030914'); x.fillStyle = sea; x.fillRect(0, 860, W, H - 860);
    x.strokeStyle = 'rgba(160,200,255,.16)'; x.lineWidth = 4; for (let i = 0; i < 12; i++) { const y = 890 + i * 45 + i * i * 1.5; x.beginPath(); for (let px = 0; px <= W; px += 40) x.lineTo(px, y + Math.sin(px * .012 + i) * 8); x.stroke(); }
    // ship (left) and iceberg (right), outside the safe area
    x.save(); x.translate(250, 900); x.scale(.5, .5); x.fillStyle = '#0b0d12'; x.beginPath(); x.moveTo(-520, -40); x.lineTo(500, -40); x.lineTo(560, -150); x.lineTo(-560, -150); x.closePath(); x.fill();
    x.fillStyle = '#7a1f1f'; x.fillRect(-505, -55, 1000, 15); x.fillStyle = '#e9e6dc'; x.fillRect(-430, -230, 820, 80); x.fillRect(-330, -280, 600, 50);
    for (let i = 0; i < 4; i++) { const fx = -270 + i * 170; x.fillStyle = '#d9a441'; x.fillRect(fx, -430, 70, 150); x.fillStyle = '#111'; x.fillRect(fx, -430, 70, 36); }
    for (let i = 0; i < 30; i++) { x.fillStyle = 'rgba(255,220,140,.9)'; x.fillRect(-480 + i * 32, -120, 10, 8); } x.restore();
    x.save(); x.translate(2400, 900); x.scale(1.15, 1.15); x.fillStyle = '#cfe3f2'; x.beginPath(); x.moveTo(-200, 0); x.lineTo(-120, -220); x.lineTo(-40, -150); x.lineTo(20, -330); x.lineTo(120, -160); x.lineTo(220, 0); x.closePath(); x.fill();
    x.fillStyle = '#9fbcd4'; x.beginPath(); x.moveTo(20, -330); x.lineTo(120, -160); x.lineTo(220, 0); x.lineTo(60, 0); x.closePath(); x.fill(); x.restore();
    // darken centre for legibility
    const v = x.createRadialGradient(CX, CY, 100, CX, CY, 900); v.addColorStop(0, 'rgba(3,6,15,.55)'); v.addColorStop(1, 'rgba(3,6,15,0)'); x.fillStyle = v; x.fillRect(0, 0, W, H);
    // logo (life ring) inside the safe area, left of the title
    const LX = CX - 560, R = 140, w = 52; x.save(); x.translate(LX, CY);
    for (let i = 0; i < 8; i++) { x.strokeStyle = i % 2 ? '#f4f1ea' : '#e0392b'; x.lineWidth = w; x.beginPath(); x.arc(0, 0, R, i * Math.PI / 4 + .02, (i + 1) * Math.PI / 4 - .02); x.stroke(); }
    x.fillStyle = '#ffd24a'; x.font = '900 170px Inter'; x.textAlign = 'center'; x.textBaseline = 'middle'; x.lineJoin = 'round'; x.lineWidth = 12; x.strokeStyle = '#0b1424'; x.strokeText('?', 0, 8); x.fillText('?', 0, 8); x.restore();
    // title + tagline
    x.textAlign = 'left'; x.textBaseline = 'middle'; x.lineJoin = 'round';
    x.font = '900 118px Inter'; x.lineWidth = 16; x.strokeStyle = '#03060f'; x.strokeText('WOULD YOU', CX - 360, CY - 75); x.fillStyle = '#ffffff'; x.fillText('WOULD YOU', CX - 360, CY - 75);
    x.strokeText('SURVIVE?', CX - 360, CY + 45); x.fillStyle = '#ffd24a'; x.fillText('SURVIVE?', CX - 360, CY + 45);
    x.font = '700 44px Inter'; x.fillStyle = '#cfd8e6'; x.fillText('Real disasters · 3 choices · Comment your answers', CX - 356, CY + 150);
  });
  await pg.screenshot({ path: process.argv[2], clip: { x: 0, y: 0, width: 2560, height: 1440 } }); await b.close();
})();

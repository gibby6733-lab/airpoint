// usage: node discord_icon.js out.png  -> 1024x1024 server icon for "Your Move Studios"
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1024, height: 1024 } });
  await pg.setContent('<canvas id="c" width="1024" height="1024"></canvas><style>body{margin:0}</style>');
  await pg.evaluate(async () => {
    await document.fonts.load('900 100px Inter');
    const c = document.getElementById('c'), x = c.getContext('2d'), C = 512;
    // background: deep night gradient + gold rays
    const g = x.createRadialGradient(C, C * .9, 40, C, C, 720); g.addColorStop(0, '#3a1420'); g.addColorStop(.6, '#160c16'); g.addColorStop(1, '#07070b'); x.fillStyle = g; x.fillRect(0, 0, 1024, 1024);
    x.save(); x.translate(C, C); for (let i = 0; i < 18; i++) { x.rotate(Math.PI / 9); x.fillStyle = i % 2 ? 'rgba(232,196,106,.06)' : 'rgba(192,57,43,.05)'; x.beginPath(); x.moveTo(0, 0); x.lineTo(-90, -800); x.lineTo(90, -800); x.fill(); } x.restore();
    // film-strip ring
    x.strokeStyle = '#e8c46a'; x.lineWidth = 26; x.beginPath(); x.arc(C, C, 410, 0, 7); x.stroke();
    x.fillStyle = '#160c16'; for (let i = 0; i < 36; i++) { const a = i / 36 * 6.283; x.save(); x.translate(C + Math.cos(a) * 410, C + Math.sin(a) * 410); x.rotate(a); x.fillRect(-7, -9, 14, 18); x.restore(); }
    // big play button (rounded triangle) with a curved arrow notch = "your move"
    x.save(); x.translate(C + 30, C - 20); x.shadowColor = 'rgba(0,0,0,.6)'; x.shadowBlur = 40;
    x.fillStyle = '#c0392b'; x.beginPath(); x.moveTo(-170, -230); x.quadraticCurveTo(-210, -250, -210, -200); x.lineTo(-210, 200); x.quadraticCurveTo(-210, 250, -170, 230); x.lineTo(210, 30); x.quadraticCurveTo(250, 0, 210, -30); x.closePath(); x.fill();
    x.shadowColor = 'transparent'; x.strokeStyle = '#e8c46a'; x.lineWidth = 14; x.stroke();
    x.restore();
    // "YM" mark inside the play button
    x.fillStyle = '#fff6e3'; x.font = '900 190px Inter'; x.textAlign = 'center'; x.textBaseline = 'middle';
    x.lineJoin = 'round'; x.lineWidth = 18; x.strokeStyle = '#3a0f0b'; x.strokeText('YM', C - 10, C - 20); x.fillText('YM', C - 10, C - 20);
    // small "STUDIOS" plate
    x.fillStyle = '#e8c46a'; x.beginPath(); x.roundRect(C - 190, C + 255, 380, 86, 22); x.fill();
    x.fillStyle = '#160c16'; x.font = '900 58px Inter'; x.fillText('STUDIOS', C, C + 300);
  });
  await pg.screenshot({ path: process.argv[2], clip: { x: 0, y: 0, width: 1024, height: 1024 } }); await b.close();
})();

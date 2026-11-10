// renders profile pictures using the episode's drawing helpers
const { chromium } = require('playwright'); const path = require('path');
(async () => {
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await pg.goto('file://' + path.resolve(process.argv[2] || 'episodes/day01', 'episode.html'));
  await pg.evaluate(async () => { await document.fonts.load('900 80px Inter'); });
  for (const variant of ['icon', 'name']) {
    await pg.evaluate(variant => {
      ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.clearRect(0, 0, W, H);
      // background: teal with orange rays
      ctx.fillStyle = C.teal; ctx.fillRect(0, 0, 1080, 1080);
      ctx.save(); ctx.translate(540, 560);
      for (let i = 0; i < 16; i++) { ctx.rotate(Math.PI / 8); ctx.fillStyle = i % 2 ? 'rgba(255,255,255,.07)' : 'rgba(0,0,0,.05)'; ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(-120, -900); ctx.lineTo(120, -900); ctx.fill(); }
      ctx.restore();
      const cy = variant === 'name' ? 470 : 560, s = variant === 'name' ? 2.9 : 3.5;
      ctx.save(); ctx.translate(540, cy); ctx.scale(s, s);
      // ears
      ctx.fillStyle = '#c9c9d4'; ctx.beginPath(); ctx.arc(-92, -62, 36, 0, 7); ctx.arc(92, -62, 36, 0, 7); ctx.fill();
      ctx.fillStyle = '#ffb3c6'; ctx.beginPath(); ctx.arc(-92, -62, 19, 0, 7); ctx.arc(92, -62, 19, 0, 7); ctx.fill();
      // face (stroke for punch)
      ctx.lineJoin = 'round'; ctx.strokeStyle = C.ink; ctx.lineWidth = 8;
      ctx.fillStyle = '#eeeef4'; ctx.beginPath(); ctx.moveTo(-82, -10); ctx.quadraticCurveTo(0, -70, 82, -10); ctx.quadraticCurveTo(70, 50, 0, 92); ctx.quadraticCurveTo(-70, 50, -82, -10); ctx.closePath(); ctx.fill(); ctx.stroke();
      // eye mask stripes
      ctx.fillStyle = '#b7b7c6'; ctx.beginPath(); ctx.ellipse(-30, -2, 24, 18, -.3, 0, 7); ctx.ellipse(30, -2, 24, 18, .3, 0, 7); ctx.fill();
      ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.arc(-28, -2, 14, 0, 7); ctx.arc(30, -2, 11, 0, 7); ctx.fill();
      ctx.fillStyle = C.ink; ctx.beginPath(); ctx.arc(-24, 0, 7, 0, 7); ctx.arc(33, 0, 6, 0, 7); ctx.fill();
      // nose + grin with one tooth
      ctx.fillStyle = '#ff7aa2'; ctx.beginPath(); ctx.ellipse(0, 34, 13, 10, 0, 0, 7); ctx.fill(); ctx.stroke();
      ctx.strokeStyle = C.ink; ctx.lineWidth = 6; ctx.beginPath(); ctx.moveTo(-24, 54); ctx.quadraticCurveTo(0, 72, 24, 52); ctx.stroke();
      ctx.fillStyle = '#fff'; ctx.fillRect(4, 60, 10, 12); ctx.strokeRect(4, 60, 10, 12);
      // battered helmet
      ctx.fillStyle = C.orange; ctx.strokeStyle = C.ink; ctx.lineWidth = 8;
      ctx.beginPath(); ctx.arc(0, -18, 92, Math.PI * 1.04, Math.PI * 1.96); ctx.closePath(); ctx.fill(); ctx.stroke();
      ctx.fillStyle = '#fff'; ctx.fillRect(-9, -108, 18, 72);
      // crack + duct tape
      ctx.strokeStyle = C.ink; ctx.lineWidth = 4; ctx.beginPath(); ctx.moveTo(-50, -86); ctx.lineTo(-38, -66); ctx.lineTo(-52, -54); ctx.lineTo(-40, -40); ctx.stroke();
      ctx.save(); ctx.translate(46, -70); ctx.rotate(.5); ctx.fillStyle = '#c4c4c4'; ctx.fillRect(-26, -9, 52, 18); ctx.strokeStyle = 'rgba(0,0,0,.25)'; ctx.lineWidth = 2; ctx.strokeRect(-26, -9, 52, 18); ctx.restore();
      ctx.restore();
      if (variant === 'name') {
        ctx.save(); ctx.translate(540, 870); ctx.rotate(-.04);
        ctx.fillStyle = C.ink; ctx.beginPath(); ctx.roundRect(-330, -70, 660, 140, 32); ctx.fill();
        txt('POSSUMS', 0, 4, 104, '#fff', { stroke: 0 }); ctx.restore();
      }
    }, variant);
    await pg.screenshot({ path: `assets/Possums_profile_${variant}.png`, clip: { x: 0, y: 0, width: 1080, height: 1080 } });
  }
  await b.close();
})();

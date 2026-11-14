// Shorts 11-20
const C = require('./core.cjs');
const K = require('./kit.cjs');
const { W, H, g, clamp, ease, lerp, line, rect, circle, ell, vgrad, rgrad, glow, fig, crowd, P } = C;
const { sh, HERO, bigWord, darkBG, door, corridor, silhouetteCity, windowsLit, lightning, car, truck } = K;
const SC = {};

// ---------- 11. Corn maze ----------
function cornWall(x0, x1, yTop, yBot, T, shade = 1) {
  const r = C.rng(Math.round(x0 * 7 + yTop));
  for (let x = x0; x < x1; x += 22) { const h = yBot - yTop + r() * 60, sw = Math.sin(T * 1.3 + x * 0.05) * 6; g.strokeStyle = `rgb(${Math.round(70 * shade)},${Math.round(95 * shade)},${Math.round(40 * shade)})`; g.lineWidth = 12; g.beginPath(); g.moveTo(x, yBot); g.quadraticCurveTo(x + sw, (yTop + yBot) / 2, x + sw * 2, yBot - h); g.stroke();
    g.fillStyle = `rgb(${Math.round(90 * shade)},${Math.round(120 * shade)},${Math.round(45 * shade)})`; for (let k = 0; k < 4; k++) { const yy = yBot - h * (0.2 + k * 0.2); g.beginPath(); g.ellipse(x + sw + (k % 2 ? 30 : -30), yy, 34, 9, (k % 2 ? 0.5 : -0.5), 0, 7); g.fill(); } }
}
function maze(T, o = {}) {
  C.nightSky(T, '#04060c', '#0d1424', '#1c2236', 700); C.moon(820, 220, 55);
  g.fillStyle = '#3a2e1e'; g.beginPath(); g.moveTo(420, 700); g.lineTo(660, 700); g.lineTo(1100, H); g.lineTo(-20, H); g.fill();
  cornWall(-100, 430, 300, 1500, T, 0.75); cornWall(650, 1180, 300, 1500, T, 0.75); cornWall(-100, 400, 600, H + 40, T, 1); cornWall(680, 1180, 600, H + 40, T, 1);
  if (o.dead) cornWall(380, 700, 560, 960, T, 0.6);
}
SC[11] = {
  hook: 'The maze trick that almost got me', fact: 2, bed: 'wind',
  sfx: [['crash', 4, 0, 0.6], ['whoosh', 5, 0, 0.8], ['whoosh', 6, 0, 0.8], ['steps', 9, 0, 1.2], ['boom', 11, 0, 1], ['sting', 12, 0, 1]],
  shots: [
    sh(0, (lt, T) => { maze(T); }, { cam: [1.0, 1.1] }),
    sh(1, (lt, T) => { maze(T); fig({ x: 520, y: 1700, s: 2.3, ...HERO('#c97b2a', { lampOn: true }), pose: () => ({ armL: [P - 0.05, P], armR: [1.3, 1.4], legL: [1.75, 1.65], legR: [1.4, 1.5] }), face: 'determined', look: [-1, 0] }); }),
    sh(2, (lt, T) => { // top-down maze with a path following the left wall
      darkBG('#2a3a18', '#1a2410'); const cells = [[0, 0, 1, 0], [1, 0, 1, 1], [1, 1, 0, 1], [0, 1, 0, 2], [0, 2, 1, 2], [1, 2, 2, 2], [2, 2, 2, 1], [2, 1, 2, 0], [2, 0, 3, 0]];
      const ox = 180, oy = 650, cs = 240; g.strokeStyle = '#7a9a3a'; g.lineWidth = 50; g.lineCap = 'square'; g.strokeRect(ox, oy, cs * 3, cs * 3);
      line([[ox + cs, oy], [ox + cs, oy + cs * 2]], '#7a9a3a', 50); line([[ox + cs * 2, oy + cs], [ox + cs * 2, oy + cs * 3]], '#7a9a3a', 50);
      const k = ease(lt) * (cells.length - 1); g.strokeStyle = '#ffd23f'; g.lineWidth = 16; g.lineCap = 'round'; g.beginPath();
      for (let i = 0; i <= Math.floor(k); i++) { const c = cells[i]; const x = ox + c[0] * cs + cs / 2 - 40, y = oy + c[1] * cs + cs / 2; i ? g.lineTo(x, y) : g.moveTo(x, y); } g.stroke();
      rect(ox + cs * 3 - 25, oy + 20, 50, cs - 40, '#1a2410'); C.textBox('EXIT', ox + cs * 3 + 70, oy + cs / 2, 50, '#fff', '#000', 10);
    }, { cam: [1.0, 1.05] }),
    sh(3, (lt, T) => { maze(T); fig({ x: 540, y: 1720, s: 2.3, ...HERO('#c97b2a'), pose: 'stand', face: 'happy' }); }),
    sh(4, (lt, T) => { maze(T); fig({ x: 470, y: lerp(1750, 1650, lt), s: 2.2, ...HERO('#c97b2a', { lampOn: true }), pose: () => ({ ...C.walkPose(T, 0.7), armL: [P - 0.05, P] }), face: 'scared', look: [-1, 0] }); }, { shake: 2 }),
    sh(5, (lt, T) => { maze(T); bigWord('LEFT', 820, 220, '#ffd23f', T, 0); }, { cam: [1.0, 1.15] }),
    sh(6, (lt, T) => { maze(T); bigWord('LEFT', 820, 220, '#ffd23f', T, 0); }, { cam: [1.15, 1.3] }),
    sh(7, (lt, T) => { maze(T, { dead: true }); bigWord('DEAD END', 820, 180, '#ff4b4b', T, 0); }, { hit: true }),
    sh(9, (lt, T) => { maze(T); fig({ x: 500, y: 1720, s: 2.2, ...HERO('#c97b2a', { lampOn: true }), pose: () => ({ armL: [P - 0.05, P], armR: [1.3, 1.4], legL: [1.75, 1.65], legR: [1.4, 1.5] }), face: 'scared', look: [1, 0] }); for (let i = 0; i < 3; i++) { g.globalAlpha = 0.7; fig({ x: 820 + i * 90 + Math.sin(T * 2 + i) * 20, y: 1500, s: 1.1, kind: 'zombie', pose: () => C.walkPose(T + i, 0.6, true, -1) }); g.globalAlpha = 1; } cornWall(700, 1180, 900, H + 40, T, 1); }),
    sh(10, (lt, T) => { // close-up: glove on corn meets grey hand
      g.fillStyle = '#1a2410'; g.fillRect(0, 0, W, H); cornWall(-100, 1180, 300, H + 40, T, 0.9);
      const k = ease(clamp(lt * 1.5)); line([[-50, 1000], [lerp(250, 470, k), 960]], '#111', 40); circle(lerp(270, 490, k), 960, 60, '#fff', '#000', 8);
      line([[W + 50, 980], [lerp(830, 610, k), 960]], '#2a2f2a', 40); circle(lerp(810, 590, k), 960, 60, '#7d8a77', '#000', 8);
    }, { cam: [1.1, 1.25], cy: 960 }),
    sh(11, (lt, T) => { g.fillStyle = '#1a2410'; g.fillRect(0, 0, W, H); cornWall(-100, 1180, 300, H + 40, T, 0.9); line([[-50, 1000], [490, 960]], '#111', 40); circle(500, 960, 60, '#fff', '#000', 8); line([[W + 50, 980], [600, 960]], '#2a2f2a', 40); circle(580, 960, 60, '#7d8a77', '#000', 8); }, { cam: [1.3, 1.4], cy: 960, hit: true, shake: 6 }),
    sh(12, (lt, T) => { maze(T); fig({ x: 360, y: 1720, s: 2.2, ...HERO('#c97b2a', { lampOn: true }), pose: 'scared', face: 'shock', look: [1, 0] }); fig({ x: 760, y: 1720, s: 2.4, kind: 'zombie', pose: () => ({ armL: [P - 0.1, P], armR: [P + 0.1, P + 0.15], legL: [1.75, 1.65], legR: [1.4, 1.5] }), look: [-1, 0] }); }, { cam: [1.0, 1.08], shake: 3 }),
    sh(14, (lt, T) => maze(T), { cam: [1.1, 1.0] }),
  ],
};

// ---------- 12. Fire lookout ----------
function lookout(T, o = {}) {
  C.nightSky(T, '#03040a', '#0b1024', '#182040', 1200); if (o.strike) lightning(o.sx || 300, -50, 900, o.seed || 4, o.strike);
  C.hills(1200, '#0d1220', 120, 1);
  // cabin interior frame with windows all around
  rect(-100, 1200, W + 200, 800, '#3a2a1c'); for (let i = 0; i < 5; i++) rect(-100 + i * 260, 300, 26, 900, '#2a1d12'); rect(-100, 280, W + 200, 30, '#2a1d12'); rect(-100, 1180, W + 200, 30, '#2a1d12');
  if (o.blue) C.tint(`rgba(120,170,255,${o.blue})`);
}
function stool(x, y, s) { g.save(); g.translate(x, y); g.scale(s, s); rect(-110, -150, 220, 30, '#7a5230'); [-90, 70].forEach(lx => { rect(lx, -120, 20, 110, '#7a5230'); g.fillStyle = 'rgba(160,220,255,0.75)'; g.beginPath(); g.roundRect(lx - 15, -14, 50, 40, 10); g.fill(); }); g.restore(); }
SC[12] = {
  hook: 'Why fire lookouts stand on a glass stool', fact: 2, bed: 'rain',
  sfx: [['thunder', 0, 0.5, 1], ['thunder', 6, 0, 1.4], ['thunder', 9, 0, 1.2], ['steps', 8, 0, 1.2], ['sting', 11, 0, 1]],
  shots: [
    sh(0, (lt, T) => { C.nightSky(T, '#03040a', '#0b1024', '#182040', 1300); lightning(700, -50, 700, 7, lt > 0.5 ? 1 : 0); C.hills(1300, '#0d1220', 200, 1); g.save(); g.translate(540, 1050); rect(-30, 0, 60, 300, '#3a2a1c'); line([[-140, 300], [0, 0], [140, 300]], '#3a2a1c', 16); rect(-130, -160, 260, 160, '#4a3420'); g.fillStyle = '#2a1d12'; g.beginPath(); g.moveTo(-160, -160); g.lineTo(0, -240); g.lineTo(160, -160); g.fill(); rect(-110, -140, 220, 80, '#ffcf7a'); g.restore(); C.rain(T); }, { cam: [1.0, 1.1] }),
    sh(2, (lt, T) => { lookout(T); stool(540, 1600, 2.2); }, { cam: [1.0, 1.08] }),
    sh(3, (lt, T) => { lookout(T); stool(540, 1650, 2.0); fig({ x: 540, y: 1360, s: 1.8, ...HERO('#8a6a2a'), pose: () => ({ armL: [1.6, 1.6], armR: [1.55, 1.55], legL: [1.6, 1.6], legR: [1.55, 1.55] }), face: 'determined' }); }),
    sh(4, (lt, T) => { lookout(T, { strike: Math.floor(T * 3) % 4 === 0 ? 0.6 : 0, sx: 800 }); C.rain(T, 0.4); C.textBox('NIGHT 30', 540, 760, 120, '#fff', '#000', 16, 'Anton'); }),
    sh(5, (lt, T) => { lookout(T); stool(540, 1650, 2.0); fig({ x: 540, y: lerp(1650, 1360, ease(lt * 1.5)), s: 1.8, ...HERO('#8a6a2a'), pose: 'stand', face: 'scared' }); C.rain(T, 0.3); }),
    sh(6, (lt, T) => { lookout(T, { strike: lt < 0.4 ? 1 : 0, sx: 540, blue: lt < 0.4 ? 0.35 : 0.1 }); stool(540, 1650, 2.0); fig({ x: 540, y: 1360, s: 1.8, ...HERO('#8a6a2a'), pose: 'scared', face: 'shock' }); }, { hit: true, shake: 14 }),
    sh(7, (lt, T) => { lookout(T, { strike: 1, sx: 200, seed: 9, blue: 0.3 }); crowd(T, { n: 14, y0: 1220, y1: 1600, sMin: 0.6, sMax: 1.1, spread: 900, adv: 0.0 }); }, { hit: true }),
    sh(8, (lt, T) => { // stairs zigzag with climbers
      C.nightSky(T, '#03040a', '#0b1024', '#182040', H); for (let i = 0; i < 6; i++) { const y = 1900 - i * 260; line([[200, y], [880, y - 130]], '#6a5040', 18); line([[880, y - 130], [200, y - 260]], '#6a5040', 18); }
      for (let i = 0; i < 12; i++) { const k = ((i / 12) + T * 0.04) % 1; const seg = Math.floor(k * 6), f = (k * 6) % 1; const y = 1900 - seg * 260 - f * 130; const x = seg % 2 === 0 ? lerp(200, 880, f) : lerp(880, 200, f); fig({ x, y: y - 10, s: 0.8, kind: 'zombie', pose: () => C.walkPose(T + i, 0.6, true, seg % 2 === 0 ? 1 : -1) }); }
      C.rain(T, 0.3);
    }, { cam: [1.0, 1.08] }),
    sh(9, (lt, T) => { C.nightSky(T, '#03040a', '#0b1024', '#182040', H); lightning(540, -50, 900, 11, lt < 0.35 ? 1 : 0); for (let i = 0; i < 4; i++) { const y = 1900 - i * 300; line([[150, y], [930, y - 150]], '#6a5040', 18); } for (let i = 0; i < 4; i++) { const k = ease(lt); fig({ x: 300 + i * 160 + k * (i - 1.5) * 200, y: 1300 + k * 600 * (i % 2 ? 1 : 0.6), s: 1.0, kind: 'zombie', pose: 'arms_up', eyeGlow: '#bfe1ff' }); } }, { hit: true, shake: 12 }),
    sh(10, (lt, T) => { lookout(T, { blue: 0.08 }); crowd(T, { n: 10, y0: 1220, y1: 1500, sMin: 0.6, sMax: 1.0, spread: 900, adv: 0.04 }); }, { cam: [1.0, 1.1] }),
    sh(11, (lt, T) => { C.nightSky(T, '#03040a', '#0b1024', '#182040', 1300); lightning(lerp(600, 1100, lt), -50, 500, 13, (Math.floor(T * 2) % 3 === 0) ? 0.4 : 0); C.hills(1300, '#0d1220', 200, 1); C.rain(T, 0.25 * (1 - lt)); }, { cam: [1.0, 1.06] }),
    sh(12, (lt, T) => { lookout(T); stool(540, 1650, 2.0); fig({ x: 540, y: 1360, s: 1.8, ...HERO('#8a6a2a'), pose: 'stand', face: 'scared' }); }, { cam: [1.1, 1.0] }),
  ],
};

// ---------- 13. Truck stop ----------
function lot(T, o = {}) {
  C.nightSky(T, '#04050d', '#141634', '#3a2340', 900); C.hills(900, '#1b1426', 30, 3);
  C.ground(900, '#2c2a2e', '#121114');
  rect(380, 820, 320, 160, '#4a3a2e'); rect(400, 850, 280, 70, o.diner === false ? '#111' : '#ffcf7a'); rect(420, 780, 240, 46, '#e02424'); g.fillStyle = '#fff'; g.font = '36px "Archivo Black"'; g.fillText('DINER', 485, 816);
  const n = 8; for (let i = 0; i < n; i++) { const a = i / n * 2 * P + (o.roll || 0) * (i % 2 ? 0.12 : -0.12); const x = 540 + Math.cos(a) * 470, y = 1250 + Math.sin(a) * 300, s = lerp(0.42, 0.78, (Math.sin(a) + 1) / 2); truck(x, y, s * (Math.cos(a) > 0 ? -1 : 1) * 1, ['#9a2f2a', '#2a5a9a', '#3a7a3a', '#c97b2a'][i % 4]); }
}
SC[13] = {
  hook: 'We hid inside a wall of trucks', fact: 0, bed: 'wind',
  sfx: [['hiss', 0, 2.5, 1], ['hiss', 8, 0.5, 1.4], ['hiss', 9, 0, 1.4], ['hiss', 10, 0, 1.4], ['creak', 12, 0, 1.4], ['boom', 12, 0.6, 1]],
  shots: [
    sh(0, (lt, T) => { C.ground(0, '#2c2a2e', '#121114'); truck(700, 1350, 1.2, '#9a2f2a'); for (let i = 0; i < 3; i++) { g.globalAlpha = 0.4 * (1 - ((T * 0.8 + i * 0.33) % 1)); circle(280, 1250 - ((T * 0.8 + i * 0.33) % 1) * 300, 40 + ((T * 0.8 + i * 0.33) % 1) * 80, '#ccc'); } g.globalAlpha = 1; }, { cam: [1.0, 1.1] }),
    sh(1, (lt, T) => { C.ground(0, '#2c2a2e', '#121114'); truck(700, 1350, 1.2, '#9a2f2a'); C.textBox('NO AIR = NO ROLL', 540, 800, 100, '#ffd23f', '#000', 16, 'Anton'); }, { cam: [1.1, 1.15] }),
    sh(2, (lt, T) => { C.room('#4a3a2e', '#1e1712', 1300); rect(-100, 1300, W + 200, 700, '#7a3a2a'); rect(-100, 1280, W + 200, 30, '#c9b98a'); fig({ x: 540, y: 1600, s: 2.3, ...HERO('#c0392b'), pose: 'stand', face: 'neutral' }); rect(-100, 1330, W + 200, 600, '#7a3a2a'); }),
    sh(3, (lt, T) => { lot(T); C.textBox('40 TRUCKS', 540, 650, 120, '#fff', '#000', 16, 'Anton'); }, { cam: [1.0, 1.08] }),
    sh(6, (lt, T) => { lot(T); crowd(T, { n: 8, y0: 1650, y1: 1950, sMin: 0.8, sMax: 1.4, spread: 1000, adv: 0.0 }); }, { cam: [1.0, 1.05] }),
    sh(7, (lt, T) => { lot(T); fig({ x: 540, y: 1300, s: 0.9, ...HERO('#c0392b'), pose: 'stand', face: 'happy' }); fig({ x: 620, y: 1300, s: 0.9, kind: 'adult', pose: 'sit', face: 'neutral' }); }, { cam: [1.2, 1.3], cy: 1200 }),
    sh(8, (lt, T) => { C.room('#4a3a2e', '#1e1712', 1300); fig({ x: 540, y: 1700, s: 2.3, ...HERO('#c0392b'), pose: 'lie', face: 'shock', look: [1, -1] }); C.textBox('DAY 8', 540, 700, 120, '#fff', '#000', 16, 'Anton'); }, { hit: true }),
    sh(9, (lt, T) => { lot(T); glow(980, 1250, 220, 'rgba(255,255,255,A)', 0.4 * (1 - lt)); }, { cam: [1.4, 1.5], cx: 900, cy: 1250 }),
    sh(10, (lt, T) => { lot(T); glow(130, 1250, 220, 'rgba(255,255,255,A)', 0.4 * (1 - lt)); }, { cam: [1.4, 1.5], cx: 200, cy: 1250 }),
    sh(11, (lt, T) => { lot(T); fig({ x: lerp(250, 850, lt), y: 1600, s: 1.2, kind: 'zombie', pose: () => C.walkPose(T, 0.5, true, 1), extra: (hd, s2, hip, arms) => { line([arms[1][2], [arms[1][2][0] + 30, arms[1][2][1] + 60]], '#e8e8e8', 8); } }); }, { cam: [1.0, 1.08] }),
    sh(12, (lt, T) => { lot(T, { roll: ease(lt) * 2 }); crowd(T, { n: 16, y0: 1500, y1: 1950, sMin: 0.8, sMax: 1.5, spread: 1000, adv: 0.05 }); }, { shake: 7, hit: true }),
    sh(13, (lt, T) => lot(T), { cam: [1.1, 1.0] }),
  ],
};

// ---------- 14. Museum T-rex ----------
function hall(T, o = {}) {
  C.room('#2a2620', '#15120e', 1450, '#1e1b16'); for (let i = 0; i < 4; i++) { rect(60 + i * 270, 120, 90, 1330, '#3a342c'); } glow(540, 300, 900, 'rgba(120,150,255,A)', 0.12);
  if (o.rex !== false) trex(540, 1450, 1);
}
function trex(x, y, s) {
  g.save(); g.translate(x, y); g.scale(s, s); g.strokeStyle = '#e8dcc0'; g.lineCap = 'round';
  g.lineWidth = 22; g.beginPath(); g.moveTo(-480, -760); g.quadraticCurveTo(-150, -930, 150, -820); g.quadraticCurveTo(320, -760, 380, -900); g.stroke(); // spine/tail->neck
  for (let i = 0; i < 9; i++) { const xx = -120 + i * 35; g.lineWidth = 12; g.beginPath(); g.moveTo(xx, -850 + Math.abs(i - 4) * 6); g.quadraticCurveTo(xx - 20, -700, xx + 10, -600); g.stroke(); } // ribs
  g.lineWidth = 20; [[60, -820, 40, -400, 100, 0], [-60, -820, -100, -400, -40, 0]].forEach(([a, b, c, d, e, f]) => { g.beginPath(); g.moveTo(a, b); g.lineTo(c, d); g.lineTo(e, f); g.stroke(); });
  g.fillStyle = '#e8dcc0'; g.beginPath(); g.moveTo(330, -920); g.lineTo(560, -900); g.lineTo(580, -840); g.lineTo(380, -810); g.closePath(); g.fill(); circle(420, -890, 16, '#2a2620');
  for (let i = 0; i < 5; i++) { line([[400 + i * 30, -850], [405 + i * 30, -830]], '#2a2620', 6); }
  rect(-200, -10, 400, 30, '#3a342c');
  g.restore();
}
SC[14] = {
  hook: 'I hid inside the T-rex skeleton', fact: 0, bed: 'drone',
  sfx: [['steps', 5, 0, 1.1], ['sting', 7, 0, 0.8], ['boom', 12, 0, 1], ['boom', 13, 0, 0.8]],
  shots: [
    sh(0, (lt, T) => hall(T), { cam: [1.0, 1.1], cy: 900 }),
    sh(1, (lt, T) => { hall(T); C.textBox('CAST', 540, 520, 200, '#ffd23f', '#000', 22, 'Anton'); }, { cam: [1.1, 1.15], cy: 900, hit: true }),
    sh(3, (lt, T) => { hall(T); fig({ x: lerp(300, 500, lt), y: lerp(1450, 880, ease(lt)), s: 1.2, ...HERO('#2a3a5a', { cap: '#1a2a4a' }), pose: () => C.runPose(T, 1), face: 'scared' }); }, { cam: [1.0, 1.05] }),
    sh(4, (lt, T) => { hall(T); fig({ x: 440, y: 760, s: 0.9, ...HERO('#2a3a5a', { cap: '#1a2a4a' }), pose: 'hide', face: 'scared' }); trex(540, 1450, 1); }, { cam: [1.6, 1.7], cx: 470, cy: 700 }),
    sh(5, (lt, T) => { hall(T); crowd(T, { n: 12, y0: 1300, y1: 1900, sMin: 0.9, sMax: 1.4, spread: 1100, adv: 0.02 }); fig({ x: 440, y: 760, s: 0.9, ...HERO('#2a3a5a', { cap: '#1a2a4a' }), pose: 'hide', face: 'scared' }); trex(540, 1450, 1); }, { cam: [1.0, 1.06] }),
    sh(7, (lt, T) => { hall(T); fig({ x: lerp(100, 520, lt), y: 1700, s: 1.6, kind: 'kid', pose: () => C.walkPose(T), face: 'happy', look: [0, -1], dress: '#e67e22' }); }),
    sh(9, (lt, T) => { hall(T); fig({ x: 520, y: 1700, s: 1.6, kind: 'kid', pose: 'point', face: 'happy', look: [0, -1], dress: '#e67e22', poseOv: { armR: [-1.2, -1.3] } }); }, { cam: [1.0, 1.05] }),
    sh(10, (lt, T) => { hall(T); fig({ x: 520, y: 1700, s: 1.6, kind: 'kid', pose: 'arms_up', face: 'shock', look: [0, -1], dress: '#e67e22' }); C.textBox('MOM!', 540, 1000, 160, '#fff', '#000', 18, 'Anton'); }, { hit: true }),
    sh(11, (lt, T) => { hall(T, { rex: false }); trex(540, 1450, 1); fig({ x: 440, y: 760, s: 0.9, ...HERO('#2a3a5a', { cap: '#1a2a4a' }), pose: 'hide', face: 'shock' }); }, { cam: [2.0, 2.2], cx: 450, cy: 680 }),
    sh(12, (lt, T) => { hall(T); crowd(T, { n: 14, y0: 1300, y1: 1900, sMin: 0.9, sMax: 1.4, spread: 1100, adv: 0.0 }); }, { hit: true, shake: 5 }),
    sh(13, (lt, T) => { darkBG('#1e1b16', '#000'); fig({ x: 540, y: 2050, s: 4.4, kind: 'zombie', pose: 'stand', look: [0, -1], eyeGlow: '#ff3b3b' }); }, { cam: [1.0, 1.15], cy: 900 }),
    sh(14, (lt, T) => hall(T), { cam: [1.1, 1.0], cy: 900 }),
  ],
};

// ---------- 15. Ice rink ----------
function rink(T, o = {}) {
  darkBG('#141a24', '#06080c'); for (let i = 0; i < 5; i++) glow(140 + i * 200, 120, 220, 'rgba(220,235,255,A)', o.dark ? 0.03 : 0.25);
  for (let r = 0; r < 6; r++) rect(-100, 260 + r * 70, W + 200, 50, ['#2a3a5a', '#3a2a4a'][r % 2]);
  const melt = o.melt || 0;
  g.fillStyle = melt > 0.7 ? '#3a5a70' : (melt > 0.3 ? '#b8cde0' : '#e8f2fa'); g.beginPath(); g.roundRect(-60, 760, W + 120, 1300, 120); g.fill();
  if (melt > 0.6) { g.strokeStyle = 'rgba(200,230,255,0.35)'; g.lineWidth = 4; for (let i = 0; i < 10; i++) { g.beginPath(); for (let x = 0; x < W; x += 20) g.lineTo(x, 900 + i * 100 + Math.sin(x / 50 + T * 2 + i) * 6); g.stroke(); } }
  rect(-60, 720, W + 120, 50, '#f2efe6'); rect(-60, 750, W + 120, 16, '#c33');
  line([[-60, 1300], [W + 60, 1300]], 'rgba(200,30,30,0.6)', 14); circle(540, 1300, 120, null, 'rgba(30,60,200,0.6)', 10);
  if (o.box) { rect(700, 560, 360, 200, 'rgba(180,220,255,0.25)'); rect(700, 560, 360, 14, '#ddd'); }
}
SC[15] = {
  hook: 'The ice was only an inch thick', fact: 0, bed: 'hum',
  sfx: [['click', 6, 0, 1.2], ['boom', 6, 0.1, 0.8], ['splash', 9, 0, 1], ['steps', 10, 0, 1.2], ['sting', 10, 0.5, 1]],
  shots: [
    sh(0, (lt, T) => { // cross-section
      darkBG('#141a24', '#06080c'); rect(0, 700, W, 120, '#e8f2fa'); rect(0, 820, W, 300, '#6a6f78'); for (let i = 0; i < 8; i++) circle(80 + i * 130, 900, 34, '#2a7ad0', '#000', 5);
      g.strokeStyle = '#ffd23f'; g.lineWidth = 8; line([[980, 700], [980, 820]], '#ffd23f', 8); C.textBox('1 INCH', 820, 620, 100, '#ffd23f', '#000', 14, 'Anton');
    }, { cam: [1.0, 1.08] }),
    sh(1, (lt, T) => { darkBG('#141a24', '#06080c'); rect(0, 700, W, 120, '#e8f2fa'); rect(0, 820, W, 300, '#6a6f78'); for (let i = 0; i < 8; i++) { circle(80 + i * 130, 900, 34, '#2a7ad0', '#000', 5); circle(80 + i * 130 + Math.sin(T * 3 + i) * 10, 900, 10, '#bfe7ff'); } }, { cam: [1.2, 1.3], cy: 860 }),
    sh(2, (lt, T) => { rink(T); g.save(); g.translate(lerp(200, 800, lt), 1350); rect(-200, -160, 400, 160, '#2a6ad0'); rect(-150, -280, 200, 130, '#1d4a9a'); circle(-130, 10, 40, '#111'); circle(130, 10, 40, '#111'); g.restore(); fig({ x: lerp(160, 760, lt), y: 1250, s: 1.0, ...HERO('#2a6ad0'), pose: 'sit', face: 'neutral' }); }),
    sh(3, (lt, T) => { rink(T); for (let i = 0; i < 6; i++) { const a = T * 2 + i; fig({ x: 150 + i * 160 + Math.sin(a) * 40, y: 1400 + (i % 2) * 220, s: 1.1, kind: 'zombie', pose: () => ({ armL: [P + Math.sin(a * 2) * 0.8, P - 0.6], armR: [-Math.sin(a * 2) * 0.8, 0.6], legL: [1.0 + Math.sin(a) * 0.4, 1.3], legR: [2.1 - Math.sin(a) * 0.4, 1.8] }) }); } }, { shake: 2 }),
    sh(5, (lt, T) => { rink(T, { box: true }); fig({ x: 880, y: 760, s: 1.0, ...HERO('#2a6ad0'), pose: 'sit', face: 'happy' }); for (let i = 0; i < 4; i++) fig({ x: 200 + i * 160, y: 1450 + (i % 2) * 150, s: 1.1, kind: 'zombie', pose: 'zombieL' }); }),
    sh(6, (lt, T) => { rink(T, { dark: lt > 0.3 }); if (lt > 0.3) C.tint('rgba(0,0,0,0.7)'); }, { hit: true }),
    sh(7, (lt, T) => { darkBG('#141a24', '#06080c'); rect(0, 700, W, 120, '#e8f2fa'); rect(0, 820, W, 300, '#6a6f78'); for (let i = 0; i < 8; i++) circle(80 + i * 130, 900, 34, '#5a5f68', '#000', 5); C.textBox('NO POWER', 540, 520, 120, '#ff4b4b', '#000', 16, 'Anton'); }),
    sh(8, (lt, T) => { rink(T, { melt: 0.4, dark: true }); C.textBox('MORNING', 540, 520, 110, '#fff', '#000', 16, 'Anton'); }),
    sh(9, (lt, T) => { rink(T, { melt: 0.9, dark: true }); C.textBox('NOON', 540, 520, 110, '#fff', '#000', 16, 'Anton'); }),
    sh(10, (lt, T) => { rink(T, { melt: 0.9, dark: true, box: true }); for (let i = 0; i < 5; i++) fig({ x: lerp(200 + i * 150, 820, ease(lt) * 0.7), y: lerp(1500, 1000, ease(lt)) + (i % 2) * 120, s: 1.2, kind: 'zombie', pose: () => C.walkPose(T + i, 0.6, true, 1) }); }, { cam: [1.0, 1.1], shake: 3 }),
    sh(11, (lt, T) => rink(T, { box: true }), { cam: [1.1, 1.0] }),
  ],
};

// ---------- 16. Parking garage ----------
function garage(T, o = {}) {
  g.fillStyle = '#4a4d52'; g.fillRect(-300, -300, W + 600, H + 600);
  for (let f = 0; f < 6; f++) { const y = 150 + f * 300; rect(-100, y, W + 200, 40, '#6a6d72'); C.textBox(String(6 - f), 80, y + 150, 80, o.floor === 6 - f ? '#ffd23f' : '#c9c9c9', '#000', 10, 'Anton'); for (let i = 0; i < 4; i++) { car(260 + i * 220, y + 270, 0.42, ['#9a2f2a', '#2a5a9a', '#3a7a3a', '#c97b2a', '#666'][(i + f) % 5], { alarm: o.alarm === 6 - f && i === 1 && Math.floor(T * 4) % 2 === 0 }); } rect(-100, y + 280, W + 200, 20, '#2c2f33'); }
}
SC[16] = {
  hook: 'I had 400 car keys and a plan', fact: 0, bed: 'hum',
  sfx: [['carAlarm', 1, 0, 1.2], ['carAlarm', 5, 0, 1.3], ['steps', 6, 0, 1.2], ['steps', 8, 0, 1.2], ['carAlarm', 12, 0.3, 1.0], ['boom', 14, 0, 1]],
  shots: [
    sh(0, (lt, T) => { darkBG('#2a2d33', '#0c0d10'); g.save(); g.translate(540, 900); g.rotate(-0.2); g.fillStyle = '#222'; g.beginPath(); g.roundRect(-120, -220, 240, 380, 60); g.fill(); [-90, 10, 110].forEach((y, i) => circle(0, y, 50, i === 2 ? '#e02424' : '#555', '#000', 6)); g.restore(); C.textBox('PANIC', 540, 1250, 110, '#e02424', '#000', 14, 'Anton'); }, { cam: [1.0, 1.1] }),
    sh(1, (lt, T) => { darkBG('#2a2d33', '#0c0d10'); car(540, 1300, 1.6, '#2a5a9a', { alarm: Math.floor(T * 4) % 2 === 0 }); }, { shake: 6 }),
    sh(2, (lt, T) => { garage(T); fig({ x: 540, y: 1500, s: 1.4, ...HERO('#e6c32a', { stripe: '#e8e8e8' }), pose: 'hold', face: 'happy', held: ([x, y], sc) => { rect(x - 60 * sc, y - 40 * sc, 120 * sc, 70 * sc, '#8a5a30'); } }); }, { cam: [1.0, 1.05] }),
    sh(4, (lt, T) => garage(T, { floor: 6 }), { cam: [1.6, 1.7], cy: 300, cx: 540 }),
    sh(5, (lt, T) => garage(T, { floor: 6, alarm: 6 }), { cam: [1.7, 1.75], cy: 400, shake: 6, hit: true }),
    sh(6, (lt, T) => { garage(T, { alarm: 6 }); for (let f = 1; f < 5; f++) for (let i = 0; i < 3; i++) fig({ x: (200 + i * 300 + T * 60 * (f % 2 ? 1 : -1) + 2000) % 1100, y: 150 + f * 300 + 270, s: 0.55, kind: 'zombie', pose: () => C.walkPose(T + i, 0.6, true, f % 2 ? 1 : -1) }); }),
    sh(7, (lt, T) => garage(T, { floor: 1 }), { cam: [1.6, 1.7], cy: 1650 }),
    sh(8, (lt, T) => { garage(T, { floor: 1 }); fig({ x: lerp(200, 1000, lt), y: 1720, s: 0.9, ...HERO('#e6c32a', { stripe: '#e8e8e8' }), pose: () => C.runPose(T, 1), face: 'scared' }); }, { cam: [1.6, 1.6], cy: 1600 }),
    sh(9, (lt, T) => { C.nightSky(T); C.ground(1300, '#2c2a2e', '#121114'); fig({ x: 540, y: 1750, s: 2.3, ...HERO('#e6c32a', { stripe: '#e8e8e8' }), pose: 'arms_up', face: 'happy' }); }),
    sh(11, (lt, T) => garage(T), { cam: [1.6, 1.7], cy: 400 }),
    sh(12, (lt, T) => garage(T, { alarm: 2, floor: 2 }), { cam: [1.7, 1.8], cy: 1350, shake: 5, hit: true }),
    sh(14, (lt, T) => { garage(T); fig({ x: 540, y: 1320, s: 1.0, kind: 'zombie', pose: 'hold', held: ([x, y], sc) => { rect(x - 60 * sc, y - 40 * sc, 120 * sc, 70 * sc, '#8a5a30'); }, eyeGlow: '#ff3b3b' }); }, { cam: [1.5, 1.8], cy: 1150 }),
    sh(15, (lt, T) => garage(T), { cam: [1.1, 1.0] }),
  ],
};

// ---------- 17. Grease fire ----------
function kitchen(T, o = {}) {
  C.room('#b8b2a4', '#4a4540', 1350, '#cfc9bb'); for (let i = 0; i < 12; i++) for (let j = 0; j < 8; j++) rect(i * 95, 200 + j * 95, 90, 90, (i + j) % 2 ? '#c9c3b5' : '#d6d0c2');
  rect(80, 900, 520, 440, '#8a8f96'); rect(120, 940, 200, 140, '#2a2a2a'); rect(360, 940, 200, 140, '#2a2a2a');
  if (o.fire) { for (let i = 0; i < 2; i++) { const x = 220 + i * 240; for (let k = 0; k < 6; k++) { const h = 120 + Math.sin(T * 12 + k + i) * 40; g.fillStyle = k % 2 ? '#ffb02e' : '#ff5a1f'; g.beginPath(); g.ellipse(x + (k - 2.5) * 22, 930 - h / 2, 22, h / 2, 0, 0, 7); g.fill(); } glow(x, 850, 300, 'rgba(255,140,40,A)', 0.4); } }
  rect(760, 700, 260, 420, '#2a3a4a'); rect(780, 720, 220, 300, o.night ? '#0b1020' : '#ffd98a'); // drive-thru window
  g.fillStyle = '#333'; g.beginPath(); g.roundRect(840, 1080, 100, 80, 12); g.fill(); for (let i = 0; i < 4; i++) line([[855, 1100 + i * 15], [925, 1100 + i * 15]], '#777', 4);
}
SC[17] = {
  hook: 'Never put water on a grease fire', fact: 0, bed: 'hum',
  sfx: [['boom', 1, 0, 1.2], ['splash', 6, 0.6, 1], ['boom', 7, 0, 1.4], ['hiss', 8, 0, 1.2], ['static', 10, 0, 1.4], ['sting', 11, 0, 1]],
  shots: [
    sh(0, (lt, T) => { kitchen(T, { fire: true }); }, { cam: [1.0, 1.1], cx: 340, cy: 950 }),
    sh(1, (lt, T) => { kitchen(T, { fire: true }); glow(340, 800, 900, 'rgba(255,120,30,A)', 0.8); C.textBox('BOOM', 540, 600, 200, '#ff5a1f', '#000', 22, 'Anton'); }, { hit: true, shake: 14 }),
    sh(2, (lt, T) => { kitchen(T, { fire: lt < 0.5 }); rect(100, lerp(500, 880, ease(clamp(lt * 2))), 240, 40, '#666'); C.textBox('LID. HEAT OFF.', 540, 1150, 100, '#ffd23f', '#000', 14, 'Anton'); }, { cam: [1.1, 1.15], cx: 340, cy: 950 }),
    sh(3, (lt, T) => { kitchen(T); fig({ x: 700, y: 1700, s: 2.3, ...HERO('#e02424', { cap: '#e02424' }), pose: 'hold', face: 'happy' }); }),
    sh(4, (lt, T) => { kitchen(T, { fire: true }); crowd(T, { n: 5, y0: 1500, y1: 1800, xc: 900, spread: 300, sMin: 1.2, sMax: 1.5, adv: 0 }); }, { cam: [1.0, 1.05] }),
    sh(5, (lt, T) => { kitchen(T, { fire: true }); fig({ x: 600, y: 1750, s: 2.0, ...HERO('#e02424', { cap: '#e02424' }), pose: 'hide', face: 'scared' }); fig({ x: 860, y: 1750, s: 2.0, kind: 'adult', pose: 'hide', face: 'scared', cap: '#e02424', dress: '#e02424' }); }),
    sh(6, (lt, T) => { kitchen(T, { fire: true }); fig({ x: 700, y: 1750, s: 2.2, kind: 'adult', pose: () => ({ armL: [1.8, 1.7], armR: [lerp(1.0, -0.6, ease(lt)), lerp(1.2, -0.5, ease(lt))], legL: [1.75, 1.65], legR: [1.4, 1.5] }), face: 'scared', cap: '#e02424', dress: '#e02424' }); }),
    sh(7, (lt, T) => { kitchen(T, { fire: true }); g.fillStyle = `rgba(255,${Math.round(150 - lt * 100)},40,${0.9 - lt * 0.4})`; g.beginPath(); g.ellipse(340, lerp(900, 400, ease(lt)), lerp(100, 600, ease(lt)), lerp(100, 500, ease(lt)), 0, 0, 7); g.fill(); }, { hit: true, shake: 18 }),
    sh(8, (lt, T) => { kitchen(T); C.rain(T, 0.6, 220); C.tint('rgba(40,60,90,0.35)'); }),
    sh(9, (lt, T) => { kitchen(T, { night: true }); C.rain(T, 0.4, 160); C.tint('rgba(0,0,0,0.6)'); }),
    sh(10, (lt, T) => { kitchen(T, { night: true }); C.tint('rgba(0,0,0,0.5)'); glow(890, 1120, 200, 'rgba(255,60,60,A)', 0.5 * (Math.floor(T * 8) % 2)); }, { cam: [1.5, 1.8], cx: 890, cy: 1120 }),
    sh(11, (lt, T) => { C.nightSky(T); C.ground(1300, '#2c2a2e', '#121114'); g.fillStyle = '#333'; g.beginPath(); g.roundRect(160, 900, 300, 440, 20); g.fill(); rect(200, 950, 220, 160, '#1a2a3a'); fig({ x: 740, y: 1750, s: 2.6, kind: 'zombie', pose: 'stand', face: 'smile_z', eyeGlow: '#ff3b3b', cap: '#e02424', look: [-1, 0] }); }, { hit: true, cam: [1.0, 1.15] }),
    sh(13, (lt, T) => { kitchen(T, { night: true }); C.tint('rgba(0,0,0,0.5)'); fig({ x: 600, y: 1750, s: 2.0, ...HERO('#e02424', { cap: '#e02424' }), pose: 'hide', face: 'shock', look: [1, 0] }); }),
    sh(14, (lt, T) => kitchen(T, { fire: true }), { cam: [1.1, 1.0] }),
  ],
};

// ---------- 18. Crane ----------
function craneView(T, o = {}) {
  C.nightSky(T, '#04050d', '#0d1230', '#2a2050', 1500); silhouetteCity(1700, '#0b0d16', 2); windowsLit(1650, 3);
  const ang = o.ang || 0; g.save(); g.translate(540, 1950); line([[0, 0], [0, -1300]], '#d9a22a', 40); for (let i = 0; i < 12; i++) line([[-20, -i * 110], [20, -i * 110 - 110]], '#b07f15', 8);
  g.translate(0, -1300); g.scale(Math.cos(ang), 1); rect(-300, -40, 1000, 40, '#d9a22a'); for (let i = 0; i < 12; i++) line([[-300 + i * 85, -40], [-260 + i * 85, 0]], '#b07f15', 6); rect(-300, -20, 120, 120, '#666'); g.restore();
  g.save(); g.translate(540, 650); rect(-70, -90, 140, 100, '#d9a22a'); rect(-50, -75, 100, 60, '#ffe7a6'); g.restore();
}
SC[18] = {
  hook: 'Cranes spin in the wind. I was inside one.', fact: 0, bed: 'wind',
  sfx: [['creak', 5, 0, 1.4], ['creak', 7, 0, 1.2], ['steps', 8, 0, 1], ['boom', 10, 0.5, 1]],
  shots: [
    sh(0, (lt, T) => craneView(T, { ang: Math.sin(T * 0.6) * 0.6 }), { cam: [1.0, 1.08] }),
    sh(1, (lt, T) => { craneView(T, { ang: 0 }); C.textBox('LOCKED = DANGER', 540, 1100, 100, '#ff4b4b', '#000', 14, 'Anton'); }, { shake: 3 }),
    sh(2, (lt, T) => { C.nightSky(T, '#04050d', '#0d1230', '#2a2050', 1500); rect(140, 500, 800, 900, '#d9a22a'); rect(180, 540, 720, 520, '#0b1530'); silhouetteCity(1060, '#070912', 5); fig({ x: 540, y: 1650, s: 2.3, ...HERO('#e67e22', { cap: '#f2c200' }), pose: 'sit', face: 'neutral' }); }),
    sh(3, (lt, T) => { craneView(T); C.textBox('200 FT', 540, 1050, 120, '#ffd23f', '#000', 14, 'Anton'); }, { cam: [1.0, 1.1] }),
    sh(4, (lt, T) => { C.nightSky(T, '#04050d', '#0d1230', '#2a2050', 1500); rect(140, 500, 800, 900, '#d9a22a'); rect(180, 540, 720, 520, '#0b1530'); silhouetteCity(1060, '#070912', 5); fig({ x: 540, y: 1650, s: 2.3, ...HERO('#e67e22', { cap: '#f2c200' }), pose: 'sit', face: 'happy' }); }),
    sh(5, (lt, T) => craneView(T, { ang: lt * 1.2 }), { cam: [1.0, 1.05] }),
    sh(7, (lt, T) => { // top-down city with rotating arm
      g.fillStyle = '#10121a'; g.fillRect(0, 0, W, H); const r = C.rng(4); for (let i = 0; i < 8; i++) for (let j = 0; j < 14; j++) { g.fillStyle = r() < 0.5 ? '#1c2030' : '#252a3a'; g.fillRect(i * 140 + 10, j * 140 + 10, 110, 110); }
      for (let i = 0; i < 40; i++) circle((r() * W), (r() * H), 6, '#93a08d');
      g.save(); g.translate(540, 960); g.rotate(T * 0.3); rect(-120, -20, 900, 40, '#d9a22a'); g.restore(); circle(540, 960, 40, '#d9a22a');
    }, { cam: [1.0, 1.1] }),
    sh(8, (lt, T) => { C.ground(0, '#2c2a2e', '#121114'); g.save(); g.translate(0, -400 + lt * 600); rect(-200, 500, 1500, 60, 'rgba(217,162,42,0.25)'); g.restore(); crowd(T, { n: 16, y0: 900, y1: 1950, sMin: 0.6, sMax: 2.0, spread: 1000, adv: 0.0 }); }, { cam: [1.0, 1.1] }),
    sh(9, (lt, T) => { darkBG('#1a1c24', '#000'); fig({ x: 540, y: 2050, s: 4.4, kind: 'zombie', pose: 'stand', look: [0, -1] }); }, { cam: [1.0, 1.12], cy: 900 }),
    sh(10, (lt, T) => { C.nightSky(T, '#04050d', '#0d1230', '#2a2050', 1500); silhouetteCity(1750, '#0b0d16', 2); rect(620, 1050, 380, 700, '#cfd8da'); rect(760, 1100, 100, 100, '#e02424'); rect(785, 1080, 50, 140, '#fff'); rect(740, 1125, 140, 50, '#fff'); for (let i = 0; i < 4; i++) rect(660 + i * 85, 1300, 50, 60, '#ffe7a6'); g.save(); g.translate(0, 0); rect(-100, 760, 900, 40, '#d9a22a'); g.restore(); crowd(T, { n: 20, y0: 1700, y1: 1950, sMin: 0.4, sMax: 0.9, xc: 700, spread: 900, adv: 0.03, dir: 1 }); }, { hit: true, cam: [1.0, 1.08] }),
    sh(11, (lt, T) => craneView(T, { ang: 1.2 + Math.sin(T) * 0.1 }), { cam: [1.1, 1.0] }),
  ],
};

// ---------- 19. Mall escalator ----------
function mall(T, o = {}) {
  C.room('#2a2a36', '#15151c', 1650, '#1e1e28');
  rect(-100, 500, W + 200, 40, '#4a4a5a'); // upper floor
  rect(60, 560, 360, 260, o.toy ? '#ff7ab8' : '#3a2a40'); C.textBox('TOYS', 240, 690, 70, '#fff', '#000', 10, 'Anton');
  // escalator diagonal
  g.fillStyle = '#5a5f6a'; g.beginPath(); g.moveTo(300, 1650); g.lineTo(520, 1650); g.lineTo(960, 540); g.lineTo(760, 540); g.fill();
  const dir = o.stopped ? 0 : -1; for (let i = 0; i < 16; i++) { const k = ((i / 16) + (dir * T * 0.25) % 1 + 1) % 1; const x = lerp(410, 860, k), y = lerp(1650, 540, k); line([[x - 100, y], [x + 100, y]], '#2a2d33', 8); }
  line([[300, 1650], [760, 540]], '#222', 16); line([[520, 1650], [960, 540]], '#222', 16);
  circle(560, 1610, 26, '#e02424', '#000', 5); circle(990, 520, 26, '#e02424', '#000', 5);
}
SC[19] = {
  hook: 'The kid pressed the escalator button', fact: 0, bed: 'hum',
  sfx: [['whoosh', 3, 0, 0.8], ['whoosh', 4, 0, 0.8], ['click', 12, 0.4, 1.4], ['boom', 12, 0.6, 1], ['steps', 12, 1.2, 1.4]],
  shots: [
    sh(0, (lt, T) => { mall(T); }, { cam: [1.6, 1.8], cx: 560, cy: 1550 }),
    sh(1, (lt, T) => { mall(T); fig({ x: 900, y: 500, s: 1.1, ...HERO('#2a2a6a', { cap: '#1a1a4a' }), pose: 'stand', face: 'neutral' }); }, { cam: [1.0, 1.05] }),
    sh(2, (lt, T) => { mall(T); const k = (T * 0.6) % 1; fig({ x: lerp(450, 560, k), y: lerp(1550, 1300, k) + (k > 0.8 ? (k - 0.8) * 1000 : 0), s: 1.1, kind: 'zombie', pose: () => C.walkPose(T, 0.6, true, 1) }); }),
    sh(3, (lt, T) => { mall(T); const k = Math.abs(Math.sin(T * 2.2)); fig({ x: lerp(440, 520, k), y: lerp(1600, 1400, k), s: 1.2, kind: 'zombie', pose: 'zombieL', lean: -10 }); fig({ x: lerp(400, 480, 1 - k), y: lerp(1650, 1450, 1 - k), s: 1.2, kind: 'zombie', pose: 'zombieL' }); }, { cam: [1.2, 1.25], cx: 500, cy: 1400 }),
    sh(5, (lt, T) => { mall(T); fig({ x: 900, y: 500, s: 1.1, ...HERO('#2a2a6a', { cap: '#1a1a4a' }), pose: 'sit', face: 'happy' }); crowd(T, { n: 8, y0: 1550, y1: 1900, sMin: 1.0, sMax: 1.4, xc: 300, spread: 500, adv: 0 }); }),
    sh(6, (lt, T) => { mall(T); C.textBox('3 DAYS', 540, 1200, 140, '#fff', '#000', 16, 'Anton'); }),
    sh(7, (lt, T) => { mall(T, { toy: true }); fig({ x: lerp(200, 330, lt), y: 820, s: 0.9, kind: 'kid', pose: () => C.runPose(T, 1), face: 'scared', dress: '#3a9a5a' }); }, { cam: [1.5, 1.6], cx: 300, cy: 760 }),
    sh(9, (lt, T) => { mall(T); fig({ x: lerp(330, 430, lt), y: 1660, s: 1.1, kind: 'kid', pose: () => C.runPose(T, 1), face: 'scared', dress: '#3a9a5a' }); fig({ x: 900, y: 500, s: 1.1, ...HERO('#2a2a6a', { cap: '#1a1a4a' }), pose: 'arms_up', face: 'shock' }); }),
    sh(10, (lt, T) => { mall(T); const k = Math.abs(Math.sin(T * 2.5)); fig({ x: lerp(440, 500, k), y: lerp(1640, 1500, k), s: 1.1, kind: 'kid', pose: () => C.walkPose(T, 1.2), face: 'sad', dress: '#3a9a5a' }); }, { cam: [1.3, 1.35], cx: 480, cy: 1450 }),
    sh(12, (lt, T) => { mall(T, { stopped: lt > 0.3 }); const k = ease(clamp(lt * 3)); fig({ x: 560, y: 1700, s: 1.6, kind: 'kid', pose: () => ({ armL: [1.9, 1.8], armR: [lerp(1.2, -0.6, k), lerp(1.3, -0.4, k)], legL: [1.75, 1.65], legR: [1.4, 1.5] }), face: 'neutral', dress: '#3a9a5a' }); }, { cam: [1.7, 1.8], cx: 560, cy: 1550, hit: true }),
    sh(13, (lt, T) => { mall(T, { stopped: true }); for (let i = 0; i < 6; i++) { const k = clamp(((T * 0.15) + i * 0.12) % 1); fig({ x: lerp(410, 860, k), y: lerp(1650, 540, k), s: 1.0, kind: 'zombie', pose: () => C.walkPose(T + i, 0.6, true, 1) }); } }, { cam: [1.1, 1.0] }),
  ],
};

// ---------- 20. Ferry ----------
function ferry(T, o = {}) {
  C.nightSky(T, '#03040a', '#0b1028', '#16203a', 1000); silhouetteCity(1000, '#0b0d18', 7); windowsLit(980, 9);
  C.water(1000, T, '#0b1c33', '#02060c');
  if (o.boat !== false) { const bob = Math.sin(T * 1.2) * 8; g.save(); g.translate(o.bx || 540, 1250 + bob); g.scale(o.bs || 1, o.bs || 1); g.fillStyle = '#e8e2d0'; g.beginPath(); g.moveTo(-420, -80); g.lineTo(420, -80); g.lineTo(360, 60); g.lineTo(-360, 60); g.fill(); rect(-300, -220, 600, 140, '#d0c8b4'); for (let i = 0; i < 7; i++) rect(-270 + i * 80, -190, 50, 50, o.lit === false ? '#222' : '#ffcf7a'); rect(-420, -100, 840, 20, '#c33'); g.restore(); }
  if (o.buoy) { const bob = Math.sin(T * 2) * 10; g.save(); g.translate(o.buoy[0], o.buoy[1] + bob); rect(-40, -90, 80, 90, '#e02424'); rect(-40, -60, 80, 20, '#fff'); glow(0, -110, 80, 'rgba(255,240,180,A)', Math.floor(T * 2) % 2 ? 0.8 : 0.1); circle(0, -110, 12, '#fff3a8'); g.restore(); }
}
SC[20] = {
  hook: 'The 1-10-1 rule saved my life. Almost.', fact: 0, bed: 'wind',
  sfx: [['thump', 5, 0, 1.4], ['creak', 6, 0, 1.2], ['splash', 7, 0.2, 1.4], ['heartbeat', 8, 0, 1.2], ['splash', 15, 0, 1], ['sting', 16, 0, 1]],
  shots: [
    sh(0, (lt, T) => { darkBG('#0b1c33', '#02060c'); C.textBox('1', 260, 900, 300, '#7fd0ff', '#000', 22, 'Anton'); C.textBox('10', 540, 900, 300, '#ffd23f', '#000', 22, 'Anton'); C.textBox('1', 820, 900, 300, '#ff4b4b', '#000', 22, 'Anton'); }, { cam: [1.0, 1.08] }),
    sh(1, (lt, T) => { darkBG('#0b1c33', '#02060c'); C.textBox('1 MIN', 540, 760, 200, '#7fd0ff', '#000', 22, 'Anton'); C.textBox('BREATHE', 540, 1000, 110, '#fff', '#000', 14, 'Anton'); }, { hit: true }),
    sh(2, (lt, T) => { darkBG('#0b1c33', '#02060c'); C.textBox('10 MIN', 540, 760, 200, '#ffd23f', '#000', 22, 'Anton'); C.textBox('MOVE', 540, 1000, 110, '#fff', '#000', 14, 'Anton'); }, { hit: true }),
    sh(3, (lt, T) => { darkBG('#0b1c33', '#02060c'); C.textBox('1 HOUR', 540, 760, 200, '#ff4b4b', '#000', 22, 'Anton'); C.textBox('BEFORE YOU PASS OUT', 540, 1000, 80, '#fff', '#000', 12, 'Anton'); }, { hit: true }),
    sh(4, (lt, T) => { ferry(T); fig({ x: 540, y: 1110, s: 0.7, ...HERO('#e67e22', { stripe: '#e8e8e8' }), pose: 'stand', face: 'neutral' }); }, { cam: [1.0, 1.08] }),
    sh(5, (lt, T) => { ferry(T); }, { shake: 14, hit: true }),
    sh(6, (lt, T) => { ferry(T); fig({ x: 280, y: 1110, s: 0.7, kind: 'zombie', pose: 'zombieL' }); fig({ x: 540, y: 1110, s: 0.7, ...HERO('#e67e22', { stripe: '#e8e8e8' }), pose: 'scared', face: 'shock', look: [-1, 0] }); }, { cam: [1.4, 1.5], cy: 1100 }),
    sh(7, (lt, T) => { ferry(T); const k = ease(lt); fig({ x: lerp(700, 900, k), y: lerp(1110, 1500, k), s: 0.7, ...HERO('#e67e22', { stripe: '#e8e8e8' }), pose: 'arms_up', face: 'scared' }); }, { cam: [1.2, 1.3], cy: 1200 }),
    sh(8, (lt, T) => { C.water(0, T, '#0d2a3a', '#030b12'); fig({ x: 540, y: 1300, s: 2.4, ...HERO('#e67e22', { stripe: '#e8e8e8' }), pose: 'swim', T, face: 'scared' }); C.water(1150, T, 'rgba(13,42,58,0.9)', 'rgba(3,11,18,1)'); C.textBox('1:00', 540, 650, 160, '#7fd0ff', '#000', 18, 'Anton'); }, { cam: [1.0, 1.05] }),
    sh(10, (lt, T) => { ferry(T, { bx: 200, bs: 0.6, buoy: [800, 1250] }); fig({ x: lerp(300, 760, lt), y: 1300, s: 0.6, ...HERO('#e67e22', { stripe: '#e8e8e8' }), pose: 'swim', T: T, face: 'determined' }); C.textBox('10:00', 540, 650, 160, '#ffd23f', '#000', 18, 'Anton'); }),
    sh(12, (lt, T) => { ferry(T, { bx: 200, bs: 0.6, buoy: [700, 1250] }); fig({ x: 760, y: 1240, s: 0.6, ...HERO('#e67e22', { stripe: '#e8e8e8' }), pose: 'stand', face: 'happy' }); }, { cam: [1.3, 1.4], cx: 700, cy: 1150 }),
    sh(14, (lt, T) => ferry(T, { lit: false }), { cam: [1.3, 1.4], cy: 1150 }),
    sh(15, (lt, T) => { ferry(T, { bx: 200, bs: 0.6, buoy: [760, 1250] }); for (let i = 0; i < 10; i++) { const x = 250 + i * 50, y = 1350 + Math.sin(i) * 60; circle(x + T * 20, y, 18, '#93a08d', '#000', 3); } }, { hit: true }),
    sh(16, (lt, T) => { C.water(0, T, '#0d2a3a', '#030b12'); for (let i = 0; i < 5; i++) fig({ x: 140 + i * 200, y: 1500 + (i % 2) * 120, s: 1.4, kind: 'zombie', pose: 'swim', T: T + i }); C.water(1350, T, 'rgba(13,42,58,0.85)', 'rgba(3,11,18,1)'); }, { cam: [1.0, 1.1] }),
    sh(17, (lt, T) => ferry(T, { bx: 200, bs: 0.6, buoy: [760, 1250] }), { cam: [1.1, 1.0] }),
  ],
};

module.exports = SC;

// Shorts 2-10
const C = require('./core.cjs');
const K = require('./kit.cjs');
const { W, H, g, clamp, ease, lerp, line, rect, circle, ell, vgrad, rgrad, glow, fig, crowd, P } = C;
const { sh, HERO, bigWord, darkBG, door, corridor } = K;
const SC = {};

// ---------- 2. Meat locker ----------
function locker(T, o = {}) {
  const lit = o.lit || 0.6;
  g.fillStyle = vgrad(0, H, [[0, '#1d2d3a'], [1, '#0a1218']]); g.fillRect(-300, -300, W + 600, H + 600);
  for (let i = 0; i < 9; i++) rect(i * 130 - 40, 0, 6, 1300, 'rgba(255,255,255,0.05)');
  rect(-300, 360, W + 600, 18, '#8a9aa8'); // rail
  const n = o.hooks || 12;
  for (let i = 0; i < n; i++) {
    const x = 70 + i * (940 / (n - 1)), sw = (o.swing === i) ? Math.sin(T * 2.4) * 0.25 : Math.sin(T * 0.6 + i) * 0.02;
    g.save(); g.translate(x, 370); g.rotate(sw);
    line([[0, 0], [0, 70]], '#aab4bd', 6); g.strokeStyle = '#aab4bd'; g.lineWidth = 6; g.beginPath(); g.arc(-10, 80, 14, -1, 2.5); g.stroke();
    if (o.swing === i) { g.restore(); continue; }
    g.fillStyle = '#9c4a4a'; g.beginPath(); g.ellipse(0, 210, 34, 120, 0, 0, 7); g.fill(); g.fillStyle = '#e8d6c8'; g.beginPath(); g.ellipse(0, 200, 14, 80, 0, 0, 7); g.fill();
    g.restore();
  }
  g.fillStyle = vgrad(1300, H, [[0, '#2b3a44'], [1, '#0d1418']]); g.fillRect(-300, 1300, W + 600, 700);
  for (let i = 0; i < 30; i++) circle((i * 97) % W, 1500 + (i * 53) % 300, 4, 'rgba(255,255,255,0.15)');
  g.fillStyle = `rgba(150,200,255,${0.08 * lit})`; g.fillRect(0, 0, W, H);
}
SC[2] = {
  hook: 'The butcher had one rule', fact: 3, bed: 'hum',
  sfx: [['creak', 12, 0.2, 1.2], ['sting', 11, 0, 1]],
  shots: [
    sh(0, (lt, T) => { // butcher shop counter, butcher pointing
      C.room('#3a2e2a', '#1a1412', 1300, '#2a201d'); rect(-100, 1220, W + 200, 700, '#5a4a40'); rect(-100, 1200, W + 200, 30, '#c9c2b2');
      door(640, 520, 300, 700, '#9aa6ae', 0); g.fillStyle = '#c33'; g.fillRect(680, 600, 220, 60); g.fillStyle = '#fff'; g.font = '34px "Archivo Black"'; g.fillText('LOCKER', 712, 642);
      fig({ x: 330, y: 1500, s: 2.2, kind: 'adult', pose: 'point', face: 'determined', look: [1, 0], dress: '#f2efe6', headCol: '#fff', hair: (x, y, r) => { rect(x - r, y - r - 8, r * 2, 22, '#555'); } });
    }, { cam: [1.0, 1.08] }),
    sh(1, (lt, T) => { C.room('#3a2e2a', '#1a1412', 1300, '#2a201d'); door(240, 300, 600, 1300, '#9aa6ae', 0); g.fillStyle = '#c33'; g.fillRect(340, 520, 400, 110); g.fillStyle = '#fff'; g.font = '64px "Archivo Black"'; g.fillText('LOCKER', 395, 598); line([[780, 900], [780, 1100]], '#c9b98a', 30); }, { cam: [1.05, 1.2], hit: true, sfx: ['boom'] }),
    sh(2, (lt, T) => { C.room('#151a22', '#0b0e13', 1300); rect(200, 400, 680, 520, '#05070a'); C.textBox('NIGHT 3', W / 2, 660, 120, '#ff4b4b', '#000', 18, 'Anton'); fig({ x: 360, y: 1650, s: 2.0, ...HERO('#f2efe6'), pose: 'sit', face: 'sad' }); fig({ x: 720, y: 1650, s: 2.0, kind: 'adult', pose: 'sit', face: 'sad', dress: '#6b8e5a' }); }, { cam: [1.0, 1.06] }),
    sh(3, (lt, T) => { locker(T, { lit: 1 }); fig({ x: 540, y: 1700, s: 2.2, ...HERO('#f2efe6', { lampOn: true }), pose: 'stand', face: 'neutral' }); }, { cam: [1.1, 1.0] }),
    sh(4, (lt, T) => { darkBG('#14202a', '#05080b'); // clock running fast
      circle(540, 860, 300, '#e8e2d0', '#111', 16); for (let i = 0; i < 12; i++) { const a = i / 12 * 2 * P; line([[540 + Math.cos(a) * 250, 860 + Math.sin(a) * 250], [540 + Math.cos(a) * 280, 860 + Math.sin(a) * 280]], '#111', 10); }
      const a = T * 6; line([[540, 860], [540 + Math.cos(a) * 220, 860 + Math.sin(a) * 220]], '#c33', 12); line([[540, 860], [540 + Math.cos(a / 12) * 150, 860 + Math.sin(a / 12) * 150]], '#111', 16); circle(540, 860, 20, '#111');
    }, { cam: [1.0, 1.1], sfx: [['tick', 0.0], ['tick', 0.3], ['tick', 0.6], ['tick', 0.9]] }),
    sh(5, (lt, T) => { C.room('#3a2e2a', '#1a1412', 1300, '#2a201d'); const op = ease(clamp(lt * 3)) * (1 - ease(clamp((lt - 0.7) * 4))); door(240, 300, 600, 1300, '#9aa6ae', op); fig({ x: 540, y: 1700, s: 2.2, ...HERO('#f2efe6', { lampOn: true }), pose: 'reach', face: 'scared' }); bigWord(String(Math.max(1, 5 - Math.floor(lt * 5))), 400, 200, '#ffd23f', T, 0); }, { cam: [1.0, 1.05], sfx: ['creak'] }),
    sh(8, (lt, T) => { locker(T); C.textBox('NIGHT 4', W / 2, 1600, 110, '#ffffff', '#000', 16, 'Anton'); }, { cam: [1.0, 1.08] }),
    sh(9, (lt, T) => { locker(T); bigWord('12', 820, 330, '#ffffff', T, 0); }, { hit: true }),
    sh(10, (lt, T) => { locker(T, { hooks: 13 }); bigWord('13', 820, 330, '#ff4b4b', T, 0); }, { hit: true, sfx: ['boom'] }),
    sh(11, (lt, T) => { // hanging figure in apron, swinging
      locker(T, { hooks: 1, swing: 0 }); g.save(); g.translate(540, 300); g.rotate(Math.sin(T * 2.2) * 0.12);
      fig({ x: 0, y: 1380, s: 2.6, kind: 'zombie', pose: () => ({ armL: [1.75, 1.7], armR: [1.4, 1.45], legL: [1.6, 1.6], legR: [1.55, 1.55] }), dress: '#f2efe6', face: 'zombie' });
      line([[0, -200], [0, 820]], '#aab4bd', 8); g.restore();
    }, { cam: [1.0, 1.15], cy: 900, hit: true }),
    sh(13, (lt, T) => { C.room('#3a2e2a', '#1a1412', 1300, '#2a201d'); door(240, 300, 600, 1300, '#9aa6ae', 0); g.fillStyle = '#c33'; g.fillRect(340, 520, 400, 110); g.fillStyle = '#fff'; g.font = '64px "Archivo Black"'; g.fillText('LOCKER', 395, 598); }, { cam: [1.15, 1.0] }),
  ],
};

// ---------- 3. Hospital: ten seconds ----------
function gurney(x, y, s, o = {}) { g.save(); g.translate(x, y); g.scale(s, s); rect(-200, -120, 400, 30, '#cfd6dc'); if (o.sheet) { g.fillStyle = '#e8eef2'; g.beginPath(); g.roundRect(-190, -160, 380, 50, 18); g.fill(); } line([[-170, -90], [-170, 0]], '#888', 10); line([[170, -90], [170, 0]], '#888', 10); circle(-170, 10, 18, '#222'); circle(170, 10, 18, '#222'); g.restore(); }
SC[3] = {
  hook: 'A hospital has 10 seconds', fact: 0, bed: 'hum',
  sfx: [['electric', 0, 0, 0.8], ['click', 2, 0.6, 1.2], ['creak', 5, 0, 1], ['creak', 8, 0, 1], ['heartbeat', 13, 0, 1.3], ['electric', 17, 0, 1], ['boom', 21, 0, 1]],
  shots: [
    sh(0, (lt, T) => { corridor(T, { wall: '#9fb3b8', floor: '#6f7f84', ceil: '#cfd8da' }); fig({ x: 540, y: 1750, s: 2.3, ...HERO('#5a8fb0'), pose: 'stand', face: 'neutral' }); }, { cam: [1.0, 1.1] }),
    sh(2, (lt, T) => { corridor(T, { wall: '#9fb3b8', floor: '#6f7f84', ceil: '#cfd8da', lit: lt < 0.25 ? 1 : 0 }); if (lt >= 0.25) C.tint('rgba(0,0,0,0.88)'); }, { hit: true }),
    sh(3, (lt, T) => { darkBG('#06080c', '#000'); bigWord('1', 800, 420, '#ffffff', T, 0); }),
    sh(4, (lt, T) => { darkBG('#06080c', '#000'); bigWord('2', 800, 420, '#ffffff', T, 0); }),
    sh(5, (lt, T) => { corridor(T, { wall: '#1a2226', floor: '#111', ceil: '#0b0f12', lit: 0 }); gurney(540 + 0, lerp(980, 1150, lt), lerp(0.5, 0.8, lt), { sheet: true }); C.flashlight(540, 1900, -P / 2, 1500, 0.3, 0.25); }, { cam: [1.0, 1.05] }),
    sh(6, (lt, T) => { darkBG('#06080c', '#000'); bigWord('3', 800, 420, '#ffffff', T, 0); }),
    sh(7, (lt, T) => { darkBG('#06080c', '#000'); bigWord('4', 800, 420, '#ffffff', T, 0); }),
    sh(8, (lt, T) => { corridor(T, { wall: '#1a2226', floor: '#111', ceil: '#0b0f12', lit: 0 }); gurney(540, lerp(1150, 1350, lt), lerp(0.8, 1.3, lt), { sheet: true }); C.flashlight(540, 1900, -P / 2, 1500, 0.3, 0.25); }, { shake: 4 }),
    sh(10, (lt, T) => { darkBG('#06080c', '#000'); bigWord(['5', '6', '7'][Math.min(2, Math.floor(lt * 3))], 800, 420, '#ffd23f', T, Math.floor(lt * 3) / 3); }),
    sh(13, (lt, T) => { darkBG('#0b0f14', '#000'); fig({ x: 540, y: 2000, s: 4.2, ...HERO('#5a8fb0'), pose: 'stand', face: 'scared', look: [0.6, 0] }); C.tint('rgba(0,0,10,0.45)'); }, { cam: [1.0, 1.12], cy: 900 }),
    sh(15, (lt, T) => { darkBG('#06080c', '#000'); bigWord(lt < 0.5 ? '8' : '9', 800, 420, '#ff4b4b', T, lt < 0.5 ? 0 : 0.5); }, { shake: 6 }),
    sh(17, (lt, T) => { corridor(T, { wall: '#9fb3b8', floor: '#6f7f84', ceil: '#cfd8da' }); gurney(540, 1500, 1.8, { sheet: false }); g.fillStyle = '#e8eef2'; g.beginPath(); g.roundRect(340, 1230, 160, 40, 10); g.fill(); }, { hit: true, cam: [1.0, 1.1] }),
    sh(21, (lt, T) => { // open body bag in room 12
      C.room('#9fb3b8', '#6f7f84', 1350, '#cfd8da'); door(110, 420, 260, 600, '#e8eef2', 0.7, '12');
      rect(430, 1150, 560, 60, '#cfd6dc'); g.fillStyle = '#1d2228'; g.beginPath(); g.roundRect(440, 1080, 540, 90, 30); g.fill(); line([[460, 1090], [600, 1060]], '#c9b98a', 6);
      C.tint('rgba(10,0,0,0.25)');
    }, { cam: [1.0, 1.15], cy: 1100, shake: 3 }),
    sh(22, (lt, T) => corridor(T, { wall: '#9fb3b8', floor: '#6f7f84', ceil: '#cfd8da', lit: (Math.floor(T * 8) % 5 === 0) ? 0.2 : 1 })),
  ],
};

// ---------- 4. Movie theater exit signs ----------
function theater(T, o = {}) {
  darkBG('#0c0607', '#020000');
  const red = o.red || 0; const fl = o.flicker ? (Math.random() < 0.3 ? 0.2 : 1) : 1;
  rect(140, 160, 800, 440, o.screen || '#1a1414');
  for (let r = 0; r < 7; r++) { const y = 760 + r * 160, s = 0.5 + r * 0.12; for (let i = -6; i <= 6; i++) { const x = 540 + i * 150 * s; g.fillStyle = '#3a1416'; g.beginPath(); g.roundRect(x - 60 * s, y, 120 * s, 120 * s, 18 * s); g.fill(); } }
  if (red) { [[60, 700], [W - 200, 700]].forEach(([x, y]) => { rect(x, y, 140, 70, `rgba(255,40,40,${fl})`); g.fillStyle = `rgba(255,255,255,${fl})`; g.font = '44px "Archivo Black"'; g.fillText('EXIT', x + 16, y + 52); glow(x + 70, y + 35, 500, 'rgba(255,30,30,A)', 0.35 * red * fl); }); g.fillStyle = `rgba(120,0,0,${0.25 * red * fl})`; g.fillRect(0, 0, W, H); }
}
function theaterCrowd(T, turn = 0) { for (let r = 0; r < 6; r++) { const y = 900 + r * 170, s = 0.55 + r * 0.14; for (let i = -4; i <= 4; i++) { if ((i + r) % 2) continue; fig({ x: 540 + i * 160 * s, y: y + 120 * s, s: s * 0.9, kind: 'zombie', pose: 'sit', face: turn ? 'zombie' : 'none', look: [0, 0], eyeGlow: turn ? '#ff3b3b' : undefined }); } } }
SC[4] = {
  hook: 'Exit signs last 90 minutes. Then what?', fact: 5, bed: 'drone',
  sfx: [['click', 3, 0, 1.2], ['steps', 7, 0, 1], ['static', 10, 0, 1], ['boom', 11, 0, 1]],
  shots: [
    sh(0, (lt, T) => { theater(T, { screen: '#f2e6c8' }); C.textBox('THE END', 540, 380, 110, '#111', '#000', 0, 'Anton'); }, { cam: [1.0, 1.08] }),
    sh(1, (lt, T) => { theater(T, { screen: '#f2e6c8' }); C.textBox('12:05', 540, 380, 150, '#c33', '#000', 0, 'Anton'); }, { hit: true, sfx: ['sting'] }),
    sh(2, (lt, T) => { darkBG('#14100c', '#050302'); rect(160, 520, 760, 360, '#2a2622'); rect(260, 600, 260, 200, '#0b0b0b'); circle(390, 700, 80, '#444', '#111', 8); circle(700, 700, 120, '#555', '#111', 10); glow(820, 700, 400, 'rgba(255,240,200,A)', 0.4); fig({ x: 540, y: 1700, s: 2.3, ...HERO('#3a3a7a'), pose: 'stand', face: 'scared' }); }, { cam: [1.0, 1.08] }),
    sh(3, (lt, T) => { theater(T, { red: lt > 0.3 ? 1 : 0 }); if (lt < 0.3) C.tint('rgba(0,0,0,0.9)'); }, { hit: true }),
    sh(5, (lt, T) => { darkBG('#0c0607', '#020000'); rect(290, 700, 500, 240, '#ff2a2a'); g.fillStyle = '#fff'; g.font = '150px "Archivo Black"'; g.fillText('EXIT', 335, 885); glow(540, 820, 700, 'rgba(255,30,30,A)', 0.5); rect(500, 960, 80, 60, '#2c2c2c'); C.textBox('90 MIN', 540, 1160, 110, '#ffd23f', '#000', 16, 'Anton'); }, { cam: [1.0, 1.1] }),
    sh(6, (lt, T) => theater(T, { red: 1 }), { cam: [1.0, 1.06] }),
    sh(7, (lt, T) => { theater(T, { red: 1 }); crowd(T, { n: 10, y0: 900, y1: 1500, xc: 950, spread: 300, sMin: 0.6, sMax: 1.2, dir: -1, adv: 0.05 }); }, { cam: [1.0, 1.05] }),
    sh(8, (lt, T) => { theater(T, { red: 1 }); theaterCrowd(T, 0); }, { cam: [1.0, 1.08] }),
    sh(10, (lt, T) => { theater(T, { red: 1, flicker: true }); theaterCrowd(T, 0); bigWord('89:00', 420, 170, '#ff4b4b', T, 0); }),
    sh(11, (lt, T) => { theater(T, { red: 0.8 }); theaterCrowd(T, 1); }, { hit: true, cam: [1.0, 1.2], shake: 6 }),
    sh(12, (lt, T) => { theater(T, { screen: '#f2e6c8' }); }, { cam: [1.1, 1.0] }),
  ],
};

// ---------- 5. Aquarium shark tunnel ----------
function tunnel(T, o = {}) {
  g.fillStyle = vgrad(0, H, [[0, '#0d5e7a'], [0.6, '#06324a'], [1, '#03141e']]); g.fillRect(-300, -300, W + 600, H + 600);
  for (let i = 0; i < 12; i++) { g.fillStyle = 'rgba(180,240,255,0.06)'; g.beginPath(); g.moveTo(i * 120 + Math.sin(T + i) * 40, -100); g.lineTo(i * 120 + 80, 1400); g.lineTo(i * 120 - 40, 1400); g.fill(); }
  K.shark(lerp(-300, 1400, (T * 0.07) % 1), 500, 1.3, 1); K.shark(lerp(1400, -300, (T * 0.05 + 0.4) % 1), 900, 0.9, -1);
  if (o.zombie) { const x = lerp(1000, 300, o.zk || 0); fig({ x, y: 400, s: 1.6, kind: 'zombie', pose: () => C.walkPose(T, 0.4, true, -1), look: [0, 1] }); }
  // tunnel arch
  g.strokeStyle = '#9fb6c0'; g.lineWidth = 26; g.beginPath(); g.arc(540, 1500, 700, P, 0); g.stroke();
  for (let i = 1; i < 6; i++) { g.strokeStyle = 'rgba(160,190,200,0.5)'; g.lineWidth = 10; g.beginPath(); g.arc(540, 1500, 700 - i * 8, P + i * 0.5, P + i * 0.5 + 0.02); g.stroke(); }
  g.fillStyle = vgrad(1500, H, [[0, '#2b3a40'], [1, '#0b1215']]); g.fillRect(-300, 1500, W + 600, 600);
}
SC[5] = {
  hook: 'I hid in the shark tunnel', fact: 3, bed: 'underwater',
  sfx: [['tap', 6, 0, 1.3], ['tap', 6, 0.4, 1.3], ['tap', 8, 0, 1.3], ['boom', 9, 0, 0.8], ['sting', 10, 0, 1]],
  shots: [
    sh(0, (lt, T) => tunnel(T), { cam: [1.0, 1.1] }),
    sh(1, (lt, T) => { tunnel(T); fig({ x: lerp(100, 540, lt), y: 1750, s: 1.9, ...HERO('#2a7a8a', { lampOn: true }), pose: () => C.runPose(T, 1), face: 'scared' }); }, { cam: [1.0, 1.05], sfx: ['whoosh'] }),
    sh(2, (lt, T) => { tunnel(T); rect(160, 700, 760, 500, 'rgba(200,240,255,0.15)'); g.strokeStyle = '#fff'; g.lineWidth = 6; g.strokeRect(160, 700, 760, 500); C.textBox('ACRYLIC', 540, 950, 130, '#ffffff', '#000', 16, 'Anton'); }, { hit: true }),
    sh(4, (lt, T) => { tunnel(T); fig({ x: 540, y: 1750, s: 2.0, ...HERO('#2a7a8a'), pose: 'stand', face: 'determined' }); }),
    sh(5, (lt, T) => { tunnel(T); fig({ x: 540, y: 1720, s: 2.0, ...HERO('#2a7a8a'), pose: 'lie', face: 'neutral' }); C.tint('rgba(0,10,30,0.3)'); }, { cam: [1.0, 1.08] }),
    sh(6, (lt, T) => { tunnel(T); fig({ x: 540, y: 1720, s: 2.0, ...HERO('#2a7a8a'), pose: 'lie', face: 'shock', look: [0, -1] }); }, { hit: true }),
    sh(8, (lt, T) => { tunnel(T, { zombie: true, zk: lt }); }, { cam: [1.15, 1.25], cy: 600 }),
    sh(9, (lt, T) => { // gray hands on acrylic, seen from below
      g.fillStyle = vgrad(0, H, [[0, '#0d5e7a'], [1, '#03141e']]); g.fillRect(0, 0, W, H);
      fig({ x: 540, y: 1250, s: 4.0, kind: 'zombie', pose: 'arms_up', look: [0, 1] });
      g.fillStyle = 'rgba(200,240,255,0.12)'; g.fillRect(0, 0, W, H);
    }, { cam: [1.0, 1.15], shake: 3 }),
    sh(11, (lt, T) => tunnel(T, { zombie: true, zk: 0.5 + lt * 0.5 })),
    sh(12, (lt, T) => tunnel(T), { cam: [1.1, 1.0] }),
  ],
};

// ---------- 6. Bowling ----------
function lanes(T, o = {}) {
  darkBG('#140c1e', '#050208');
  const vy = 620; for (let i = -2; i <= 2; i++) { g.fillStyle = i === (o.hl || 99) ? '#d9a35a' : '#b98546'; g.beginPath(); g.moveTo(540 + i * 70 - 30, vy); g.lineTo(540 + i * 70 + 30, vy); g.lineTo(540 + i * 520 + 220, H); g.lineTo(540 + i * 520 - 220, H); g.fill(); g.fillStyle = '#2a1a10'; g.beginPath(); g.moveTo(540 + i * 70 + 30, vy); g.lineTo(540 + i * 70 + 36, vy); g.lineTo(540 + i * 520 + 260, H); g.lineTo(540 + i * 520 + 220, H); g.fill(); }
  rect(0, 440, W, 180, o.dark ? '#08060a' : '#2a1d3a'); if (!o.dark) for (let i = 0; i < 5; i++) { rect(120 + i * 180, 470, 120, 40, '#ff4bd8'); glow(180 + i * 180, 490, 200, 'rgba(255,80,220,A)', 0.25); }
  if (!o.dark) for (let i = -2; i <= 2; i++) for (let p = 0; p < 4; p++) for (let q = 0; q <= p; q++) { circle(540 + i * 70 + (q - p / 2) * 10, 600 - p * 6, 4, '#fff'); }
}
function pinsExplode(lt, x, y, s = 1) { for (let i = 0; i < 10; i++) { const a = -P / 2 + (i - 4.5) * 0.25, d = ease(lt) * 400 * s; g.save(); g.translate(x + Math.cos(a) * d, y + Math.sin(a) * d * 0.6 + ease(lt) * ease(lt) * 300 * s); g.rotate(lt * (i - 4) * 3); g.fillStyle = '#fff'; g.beginPath(); g.ellipse(0, 0, 18 * s, 50 * s, 0, 0, 7); g.fill(); rect(-18 * s, -20 * s, 36 * s, 8 * s, '#c33'); g.restore(); } }
SC[6] = {
  hook: 'The dead follow noise. So I bowled.', fact: 0, bed: 'drone',
  sfx: [['crash', 6, 0, 1.4], ['crash', 9, 0, 1.4], ['crash', 11, 0, 1.4], ['thump', 12, 0.3, 1.2], ['boom', 13, 0, 1], ['click', 14, 0, 1], ['heartbeat', 16, 0, 1.4]],
  shots: [
    sh(0, (lt, T) => { darkBG('#1e1428', '#06030a'); g.save(); g.translate(540, 900); g.rotate(Math.sin(T) * 0.1); g.fillStyle = '#fff'; g.beginPath(); g.ellipse(0, 0, 150, 420, 0, 0, 7); g.fill(); rect(-150, -160, 300, 40, '#c33'); rect(-150, -100, 300, 20, '#c33'); g.restore(); C.textBox('3.5 LB', 540, 1450, 140, '#ffd23f', '#000', 18, 'Anton'); }, { cam: [1.0, 1.1] }),
    sh(1, (lt, T) => { lanes(T); pinsExplode(lt, 540, 700, 1.4); }, { sfx: ['crash'], hit: true }),
    sh(2, (lt, T) => { darkBG('#1a1220', '#050208'); rect(0, 900, W, 300, '#333'); for (let i = 0; i < 8; i++) rect(80 + i * 120, 820, 40, 80, '#fff'); fig({ x: 540, y: 1750, s: 2.2, ...HERO('#7a3a9a'), pose: 'hold', face: 'neutral' }); }, { cam: [1.0, 1.05] }),
    sh(3, (lt, T) => { lanes(T); crowd(T, { n: 16, y0: 700, y1: 1800, sMin: 0.3, sMax: 1.3, adv: 0.04, dir: 1 }); }, { cam: [1.0, 1.08] }),
    sh(4, (lt, T) => { lanes(T); fig({ x: 540, y: 1800, s: 2.4, ...HERO('#7a3a9a'), pose: 'point', face: 'determined', look: [1, 0] }); }),
    sh(5, (lt, T) => { lanes(T, { hl: -2 }); circle(lerp(140, 400, ease(lt)), lerp(1700, 700, ease(lt)), lerp(80, 14, ease(lt)), '#1d3b8a', '#000', 4); bigWord('LANE 1', 300, 140, '#fff', T, 0); }),
    sh(6, (lt, T) => { lanes(T, { hl: -2 }); pinsExplode(lt, 400, 680, 1); bigWord('STRIKE!', 300, 170, '#ffd23f', T, 0); }, { shake: 8 }),
    sh(7, (lt, T) => { lanes(T); crowd(T, { n: 12, y0: 700, y1: 1500, xc: 300, spread: 400, sMin: 0.3, sMax: 1.0, adv: 0.02, dir: -1 }); fig({ x: lerp(900, 700, lt), y: 1800, s: 1.8, ...HERO('#7a3a9a'), pose: 'hide', face: 'scared' }); }),
    sh(8, (lt, T) => { lanes(T, { hl: -1 }); pinsExplode(clamp(lt * 2 - 0.4), 470, 680, 1); bigWord('LANE 2', 300, 140, '#fff', T, 0); }, { shake: 4 }),
    sh(10, (lt, T) => { lanes(T, { hl: 0 }); pinsExplode(clamp(lt * 2 - 0.4), 540, 680, 1); bigWord('LANE 3', 300, 140, '#fff', T, 0); }, { shake: 6 }),
    sh(12, (lt, T) => { C.room('#2a1d3a', '#100a16', 1400); door(300, 400, 480, 1000, '#5a4a6a', 0); rect(330, 900, 420, 40, '#c9b98a'); fig({ x: 540, y: 1750, s: 2.2, ...HERO('#7a3a9a'), pose: 'reach', face: 'scared', look: [0, -0.5] }); }, { cam: [1.0, 1.1] }),
    sh(13, (lt, T) => { C.room('#2a1d3a', '#100a16', 1400); door(300, 400, 480, 1000, '#5a4a6a', 0); bigWord('LOCKED', 800, 200, '#ff4b4b', T, 0); }, { hit: true, shake: 8 }),
    sh(14, (lt, T) => { lanes(T, { dark: true }); C.tint('rgba(0,0,0,0.6)'); }),
    sh(16, (lt, T) => { darkBG('#06030a', '#000'); fig({ x: 540, y: 2050, s: 4.2, ...HERO('#7a3a9a'), pose: 'stand', face: 'scared', look: [0, 0] }); C.tint('rgba(0,0,0,0.35)'); }, { cam: [1.0, 1.15], cy: 900 }),
    sh(17, (lt, T) => { lanes(T); }, { cam: [1.1, 1.0] }),
  ],
};

// ---------- 7. Radio station ----------
function studio(T, o = {}) {
  C.room('#2a2230', '#140f18', 1250, '#1d1724');
  for (let i = 0; i < 8; i++) for (let j = 0; j < 5; j++) rect(60 + i * 125, 150 + j * 125, 110, 110, '#3a3044');
  rect(640, 200, 360, 120, o.onair === false ? '#3a1010' : '#e02424'); g.fillStyle = '#fff'; g.font = '64px "Archivo Black"'; g.fillText('ON AIR', 665, 285); if (o.onair !== false) glow(820, 260, 400, 'rgba(255,40,40,A)', 0.3);
  rect(-100, 1250, W + 200, 700, '#3b2f28'); rect(-100, 1230, W + 200, 30, '#5a4a40');
  // phone with lines
  rect(700, 1100, 300, 140, '#222'); for (let i = 0; i < 4; i++) { const on = o.lines ? (Math.floor(T * 4 + i) % 2 === 0 || o.lines === 'all') : (o.line === i + 1 && Math.floor(T * 6) % 2 === 0); circle(740 + i * 66, 1150, 22, on ? '#ff4b4b' : '#552222'); }
  // mic
  line([[300, 1240], [300, 1000], [420, 900]], '#555', 16); g.fillStyle = '#2a2a2a'; g.beginPath(); g.roundRect(400, 780, 90, 160, 40); g.fill();
}
SC[7] = {
  hook: 'I kept broadcasting after dark', fact: 1, bed: 'drone',
  sfx: [['static', 0, 0, 0.8], ['phone', 6, 0, 0.9], ['phone', 8, 0, 1.1], ['boom', 13, 0, 1], ['static', 15, 0, 1]],
  shots: [
    sh(0, (lt, T) => { C.nightSky(T); C.hills(1300, '#120e1a', 60); const k = (T * 0.6) % 1; for (let i = 0; i < 4; i++) { g.strokeStyle = `rgba(255,214,120,${0.6 - i * 0.12})`; g.lineWidth = 8; g.beginPath(); g.arc(540, 1100, 120 + ((k + i * 0.25) % 1) * 700, P * 1.1, P * 1.9); g.stroke(); } line([[540, 1300], [540, 900]], '#888', 14); circle(540, 890, 18, '#ff4b4b'); }, { cam: [1.0, 1.08] }),
    sh(1, (lt, T) => { C.nightSky(T, '#04050d', '#0b1030', '#1b1440', 1500); g.strokeStyle = 'rgba(255,214,120,0.8)'; g.lineWidth = 10; g.beginPath(); g.moveTo(100, 1500); g.quadraticCurveTo(540, 200, 980, 1500); g.stroke(); circle(100, 1500, 20, '#ff4b4b'); circle(lerp(100, 980, ease(lt)), 0, 0); const k = ease(lt); const x = lerp(100, 980, k), y = (1 - k) * (1 - k) * 1500 + 2 * (1 - k) * k * 200 + k * k * 1500; circle(x, y, 26, '#ffd23f'); C.hills(1500, '#120e1a', 40); }, { cam: [1.0, 1.05] }),
    sh(2, (lt, T) => { studio(T); fig({ x: 470, y: 1650, s: 2.3, ...HERO('#3a5a8a'), pose: 'sit', face: 'determined', look: [0, 0] }); }, { cam: [1.0, 1.06] }),
    sh(3, (lt, T) => { studio(T); fig({ x: 470, y: 1650, s: 2.3, ...HERO('#3a5a8a'), pose: 'point', face: 'determined' }); }, { cam: [1.15, 1.2], cx: 480, cy: 1000 }),
    sh(6, (lt, T) => { studio(T, { lines: 'all' }); fig({ x: 470, y: 1650, s: 2.3, ...HERO('#3a5a8a'), pose: 'sit', face: 'happy' }); }, { cam: [1.05, 1.15], cx: 820, cy: 1150 }),
    sh(8, (lt, T) => { studio(T, { line: 4 }); bigWord('LINE 4', 600, 160, '#ff4b4b', T, 0); }, { cam: [1.3, 1.4], cx: 840, cy: 1150 }),
    sh(9, (lt, T) => { studio(T); fig({ x: 470, y: 1650, s: 2.3, ...HERO('#3a5a8a'), pose: 'sit', face: 'neutral', extra: (hd, s2, h2, arms, sc) => { line([[hd[0] - 40 * sc, hd[1]], [hd[0] - 70 * sc, hd[1] + 60 * sc]], '#222', 14 * sc); } }); }, { cam: [1.2, 1.3], cx: 470, cy: 1100 }),
    sh(12, (lt, T) => { studio(T); fig({ x: 470, y: 1650, s: 2.3, ...HERO('#3a5a8a'), pose: 'sit', face: 'scared' }); }, { cam: [1.25, 1.35], cx: 470, cy: 1100 }),
    sh(13, (lt, T) => { // outside the studio door
      C.room('#2a2230', '#140f18', 1350); door(320, 420, 440, 930, '#4a3a2a', 0); rect(400, 520, 280, 120, '#e02424'); g.fillStyle = '#fff'; g.font = '50px "Archivo Black"'; g.fillText('ON AIR', 420, 600);
      crowd(T, { n: 12, y0: 1300, y1: 1950, sMin: 1.0, sMax: 2.0, spread: 900, adv: 0.0 });
    }, { hit: true, cam: [1.0, 1.12], shake: 6 }),
    sh(14, (lt, T) => { studio(T, { onair: false }); C.tint('rgba(0,0,0,0.4)'); }),
    sh(15, (lt, T) => { C.nightSky(T); C.hills(1300, '#120e1a', 60); crowd(T, { n: 26, y0: 1300, y1: 1950, adv: 0.05 }); line([[540, 1300], [540, 900]], '#888', 14); circle(540, 890, 18, '#ff4b4b'); }, { cam: [1.0, 1.1] }),
    sh(16, (lt, T) => studio(T), { cam: [1.1, 1.0] }),
  ],
};

// ---------- 8. Ski lodge snow cave ----------
function slope(T, o = {}) {
  C.nightSky(T, '#060914', '#121a33', '#2b3554', 900); C.moon(800, 260, 70);
  g.fillStyle = '#d9e2ef'; g.beginPath(); g.moveTo(-300, 1000); g.lineTo(400, 500); g.lineTo(1400, 1100); g.lineTo(1400, H + 300); g.lineTo(-300, H + 300); g.fill();
  g.fillStyle = '#b7c3d6'; g.beginPath(); g.moveTo(400, 500); g.lineTo(700, 820); g.lineTo(560, 760); g.fill();
  if (o.lodge) { rect(620, 900, 380, 260, '#4a3020'); g.fillStyle = '#6b4a30'; g.beginPath(); g.moveTo(590, 910); g.lineTo(810, 760); g.lineTo(1030, 910); g.fill(); rect(680, 980, 90, 90, '#ffcf7a'); rect(860, 980, 90, 90, '#ffcf7a'); }
  if (o.lift) { line([[-50, 600], [1100, 1200]], '#333', 6); for (let i = 0; i < 4; i++) { const x = ((i * 300 + T * 30) % 1200) - 50; line([[x, 600 + x * 0.52], [x, 660 + x * 0.52]], '#333', 5); rect(x - 30, 660 + x * 0.52, 60, 14, '#333'); } }
  C.snow(T, 0.7);
}
function snowCave(T, o = {}) {
  g.fillStyle = vgrad(0, H, [[0, '#e4ebf5'], [1, '#aebbd0']]); g.fillRect(-300, -300, W + 600, H + 600);
  g.fillStyle = '#4a5a76'; g.beginPath(); g.ellipse(540, 1250, 470, 330, 0, P, 0); g.lineTo(1010, 1300); g.lineTo(70, 1300); g.fill();
  g.fillStyle = '#2c3850'; g.beginPath(); g.ellipse(540, 1250, 430, 290, 0, P, 0); g.fill();
  rect(-300, 1300, W + 600, 700, '#c9d3e2');
  fig({ x: 540, y: 1310, s: 1.8, ...HERO('#c0392b', { lampOn: o.lamp }), pose: 'hide', face: o.face || 'neutral', look: o.look || [0, 0] });
  if (o.pole) { const k = o.pole; line([[620, lerp(500, 1010, k)], [620, 300]], '#222', 14); circle(620, lerp(500, 1010, k) - 10, 22, null, '#222', 6); }
  if (o.dig) { for (let i = 0; i < 8; i++) { const a = T * 3 + i; circle(540 + Math.sin(a) * 120, 920 - Math.abs(Math.cos(a * 1.3)) * 80, 16, '#fff'); } }
}
SC[8] = {
  hook: 'I dug a snow cave to hide', fact: 2, bed: 'wind',
  sfx: [['thump', 0, 0.3, 1.2], ['whoosh', 5, 0, 1.2], ['crash', 9, 0, 1], ['boom', 11, 0, 1]],
  shots: [
    sh(0, (lt, T) => { slope(T, { lodge: true }); crowd(T, { n: 10, y0: 1150, y1: 1300, xc: 800, spread: 300, sMin: 0.3, sMax: 0.6, adv: 0.0 }); }, { cam: [1.0, 1.1], cy: 1000 }),
    sh(1, (lt, T) => { slope(T); for (let i = 0; i < 10; i++) circle(540 + Math.sin(T * 9 + i) * 140, 1500 - Math.abs(Math.sin(T * 7 + i)) * 200, 20, '#fff'); fig({ x: 540, y: 1700, s: 2.0, ...HERO('#c0392b'), pose: 'reach', face: 'determined' }); }, { shake: 4 }),
    sh(2, (lt, T) => { snowCave(T); g.fillStyle = 'rgba(255,255,255,0.5)'; for (let i = 0; i < 40; i++) circle(120 + (i * 137) % 840, 300 + (i * 89) % 500, 8, null, '#7a8aa8', 3); C.textBox('INSIDE: ABOUT 0°C', 540, 1150, 70, '#7fd0ff', '#000', 12, 'Anton'); C.textBox('OUTSIDE: -20°C', 540, 820, 70, '#2a6ad0', '#000', 12, 'Anton'); }, { cam: [1.0, 1.06] }),
    sh(3, (lt, T) => { slope(T, { lift: true }); fig({ x: 540, y: 1650, s: 1.8, ...HERO('#c0392b'), pose: 'hide', face: 'determined' }); }),
    sh(4, (lt, T) => { snowCave(T); C.textBox('NIGHT 1', 540, 700, 120, '#fff', '#000', 16, 'Anton'); }),
    sh(5, (lt, T) => { slope(T); fig({ x: lerp(300, 700, lt), y: lerp(900, 1300, lt), s: 1.0, kind: 'zombie', pose: 'stand', look: [1, 0], extra: (hd, s2, hip, arms, sc) => { line([[hip[0] - 60, hip[1] + 120], [hip[0] + 80, hip[1] + 140]], '#c33', 10); } }); C.textBox('NIGHT 2', 540, 600, 120, '#fff', '#000', 16, 'Anton'); }),
    sh(8, (lt, T) => { snowCave(T, { face: 'scared', look: [0, -1] }); fig({ x: 560, y: 640, s: 1.0, kind: 'zombie', pose: 'stand', look: [0, 1] }); }, { cam: [1.0, 1.1] }),
    sh(9, (lt, T) => snowCave(T, { pole: ease(clamp(lt * 4)), face: 'shock', look: [0.5, -1] }), { hit: true, shake: 6, cam: [1.3, 1.4], cy: 1100 }),
    sh(10, (lt, T) => snowCave(T, { pole: 1 - ease(clamp(lt * 3)), face: 'scared', look: [0, -1] }), { cam: [1.3, 1.25], cy: 1100 }),
    sh(11, (lt, T) => snowCave(T, { dig: true, face: 'scared', look: [0, -1] }), { shake: 5, cam: [1.1, 1.2], cy: 1050 }),
    sh(12, (lt, T) => slope(T, { lodge: true, lift: true }), { cam: [1.1, 1.0], cy: 1000 }),
  ],
};

// ---------- 9. Lighthouse ----------
function bay(T, o = {}) {
  C.nightSky(T, '#03040b', '#0b1028', '#16203a', 1050); C.moon(860, 240, 50);
  C.water(1050, T, '#0b1c33', '#02060c');
  const lh = (x, y, s, on, mine) => { g.save(); g.translate(x, y); g.scale(s, s); g.fillStyle = '#e8e2d0'; g.beginPath(); g.moveTo(-60, 0); g.lineTo(60, 0); g.lineTo(38, -420); g.lineTo(-38, -420); g.fill(); rect(-55, -320, 110, 40, '#c33'); rect(-55, -160, 110, 40, '#c33'); rect(-50, -470, 100, 50, on ? '#fff7c0' : '#333'); g.fillStyle = '#222'; g.beginPath(); g.moveTo(-58, -470); g.lineTo(0, -530); g.lineTo(58, -470); g.fill(); rect(-120, 0, 240, 40, '#2a2a2a'); g.restore(); if (on) glow(x, y - 445 * s, 220 * s, 'rgba(255,250,200,A)', 0.8); };
  const on1 = o.mine ? (T % 3 < 0.5) : false, on2 = o.other ? ((T + 1.2) % 3 < 0.5) : false;
  lh(220, 1150, 1.4, on1, true); lh(860, 1040, 0.55, on2, false);
  if (on1) { g.save(); g.globalCompositeOperation = 'lighter'; g.fillStyle = 'rgba(255,250,200,0.25)'; g.beginPath(); g.moveTo(220, 527); g.lineTo(1300, 300); g.lineTo(1300, 760); g.fill(); g.restore(); }
  if (on2) { g.save(); g.globalCompositeOperation = 'lighter'; g.fillStyle = 'rgba(255,250,200,0.2)'; g.beginPath(); g.moveTo(860, 795); g.lineTo(-200, 600); g.lineTo(-200, 950); g.fill(); g.restore(); }
  if (o.boat !== undefined) { const x = lerp(500, 820, o.boat), y = lerp(1450, 1150, o.boat), s = lerp(1, 0.5, o.boat); g.save(); g.translate(x, y); g.scale(s, s); g.fillStyle = '#5a3a20'; g.beginPath(); g.moveTo(-90, 0); g.lineTo(90, 0); g.lineTo(60, 40); g.lineTo(-60, 40); g.fill(); line([[0, 0], [0, -200]], '#333', 6); g.fillStyle = '#eee'; g.beginPath(); g.moveTo(6, -190); g.lineTo(80, -10); g.lineTo(6, -10); g.fill(); g.restore(); }
}
SC[9] = {
  hook: 'Someone copied my lighthouse signal', fact: 0, bed: 'wind',
  sfx: [['bell', 1, 0, 0.8], ['sting', 4, 0, 1], ['boom', 8, 0, 1]],
  shots: [
    sh(0, (lt, T) => bay(T, { mine: true }), { cam: [1.0, 1.08] }),
    sh(1, (lt, T) => { bay(T, { mine: true }); bigWord('EVERY 10 SEC', 1500, 120, '#fff', T, 0); }, { cam: [1.3, 1.35], cx: 220, cy: 800 }),
    sh(2, (lt, T) => { bay(T, { mine: true, boat: 0.1 }); }, { cam: [1.0, 1.05] }),
    sh(3, (lt, T) => { C.nightSky(T); rect(0, 1100, W, 900, '#1a1a1a'); fig({ x: 540, y: 1750, s: 2.4, ...HERO('#2a4a7a'), pose: 'point', face: 'shock', look: [1, -0.5] }); C.textBox('NIGHT 20', 540, 600, 120, '#fff', '#000', 16, 'Anton'); }),
    sh(4, (lt, T) => bay(T, { mine: false, other: true }), { cam: [1.6, 1.8], cx: 860, cy: 820, hit: true }),
    sh(7, (lt, T) => bay(T, { mine: true, other: true }), { cam: [1.0, 1.05] }),
    sh(8, (lt, T) => { bay(T, { other: true }); fig({ x: 860, y: 1050, s: 0.4, kind: 'zombie', pose: 'stand' }); }, { cam: [2.2, 2.6], cx: 860, cy: 900, shake: 2 }),
    sh(10, (lt, T) => bay(T, { mine: true, other: true, boat: lt }), { cam: [1.0, 1.08] }),
    sh(11, (lt, T) => bay(T, { mine: true, other: true }), { cam: [1.08, 1.0] }),
  ],
};

// ---------- 10. Subway third rail ----------
function subway(T, o = {}) {
  darkBG('#121418', '#040506');
  const vx = 540, vy = 760; g.fillStyle = '#2a2d33'; g.beginPath(); g.arc(vx, vy, 160, P, 0); g.lineTo(vx + 160, vy + 140); g.lineTo(vx - 160, vy + 140); g.fill(); g.fillStyle = '#000'; g.beginPath(); g.arc(vx, vy, 130, P, 0); g.lineTo(vx + 130, vy + 140); g.lineTo(vx - 130, vy + 140); g.fill();
  g.fillStyle = '#3b3f46'; g.beginPath(); g.moveTo(vx - 160, vy + 140); g.lineTo(vx + 160, vy + 140); g.lineTo(W + 400, H); g.lineTo(-400, H); g.fill();
  for (let k = 0.05; k < 1; k += 0.08) { const y = lerp(vy + 140, H, k * k); const w = lerp(140, 1600, k * k); rect(vx - w / 2, y, w, 6 + k * 20, '#4a3a2a'); }
  [[-60, -380], [60, 380]].forEach(([a, b]) => line([[vx + a, vy + 140], [vx + b, H]], '#8a8f96', 12));
  line([[vx + 100, vy + 140], [vx + 700, H]], o.power === false ? '#555' : '#d9b03a', 20); // third rail
  // platform on left
  g.fillStyle = '#6a6f78'; g.beginPath(); g.moveTo(-300, 900); g.lineTo(vx - 170, vy + 120); g.lineTo(vx - 170, vy + 150); g.lineTo(-300, 1700); g.fill(); rect(-300, 880, 600, 20, '#ffd23f');
  for (let i = 0; i < 4; i++) { const k = Math.pow(0.6, i); glow(vx, lerp(vy - 100, 80, k), 200 * k + 40, 'rgba(255,240,200,A)', o.power === false ? 0 : 0.3); }
}
function sparks(x, y, T, n = 18) { for (let i = 0; i < n; i++) { const a = -P / 2 + (Math.random() - 0.5) * 2.4, d = Math.random() * 160; line([[x, y], [x + Math.cos(a) * d, y + Math.sin(a) * d]], Math.random() < 0.5 ? '#fff6a0' : '#7fd8ff', 4); } glow(x, y, 260, 'rgba(160,220,255,A)', 0.6); }
SC[10] = {
  hook: "The dead don't know about the third rail", fact: 1, bed: 'hum',
  sfx: [['zap', 6, 0, 1.4], ['zap', 7, 0, 1.4], ['zap', 8, 0, 1.4], ['click', 10, 0, 1], ['steps', 13, 0, 1.4], ['boom', 15, 0, 1]],
  shots: [
    sh(0, (lt, T) => { subway(T); }, { cam: [1.0, 1.1] }),
    sh(1, (lt, T) => { subway(T); bigWord('600 V', 1250, 220, '#ffd23f', T, 0); }, { cam: [1.25, 1.35], cx: 860, cy: 1350, hit: true, sfx: ['zap'] }),
    sh(2, (lt, T) => { subway(T); fig({ x: 300, y: 1300, s: 1.6, ...HERO('#e67e22', { stripe: '#e8e8e8' }), pose: 'stand', face: 'neutral' }); }),
    sh(4, (lt, T) => { subway(T); crowd(T, { n: 10, y0: 860, y1: 1400, xc: 600, spread: 300, sMin: 0.25, sMax: 0.9, dir: 1, adv: 0.03 }); }),
    sh(5, (lt, T) => { subway(T); fig({ x: 860, y: 1350, s: 1.4, kind: 'zombie', pose: () => C.walkPose(T, 0.5, true, 1) }); if (lt > 0.7) sparks(880, 1350, T); }, { cam: [1.1, 1.2], cx: 820, cy: 1250 }),
    sh(6, (lt, T) => { subway(T); fig({ x: 860, y: 1350, s: 1.4, kind: 'zombie', pose: 'arms_up', eyeGlow: '#7fd8ff' }); sparks(880, 1350, T, 30); }, { hit: true, shake: 12, cam: [1.2, 1.25], cx: 820, cy: 1250 }),
    sh(7, (lt, T) => { subway(T); sparks(760, 1150, T); sparks(980, 1500, T); }, { shake: 10 }),
    sh(9, (lt, T) => { subway(T); for (let i = 0; i < 3; i++) fig({ x: 760 + i * 30, y: 1050 + i * 40, s: 0.8, kind: 'zombie', pose: 'lie' }); }),
    sh(10, (lt, T) => { subway(T, { power: lt < 0.3 }); if (lt >= 0.3) C.tint('rgba(0,0,0,0.75)'); }, { hit: true }),
    sh(13, (lt, T) => { subway(T, { power: false }); C.tint('rgba(0,0,0,0.6)'); C.flashlight(300, 1300, -0.6, 1300, 0.25, 0.3); crowd(T, { n: 18, y0: 860, y1: 1500, xc: 700, spread: 400, sMin: 0.25, sMax: 1.0, dir: 1, adv: 0.04 }); }, { shake: 3 }),
    sh(15, (lt, T) => { subway(T, { power: false }); C.tint('rgba(0,0,0,0.4)'); crowd(T, { n: 24, y0: 1000, y1: 1950, xc: 760, spread: 600, sMin: 0.5, sMax: 1.8, dir: 1, adv: 0.06 }); }, { hit: true, cam: [1.0, 1.15] }),
    sh(16, (lt, T) => subway(T), { cam: [1.1, 1.0] }),
  ],
};

module.exports = SC;

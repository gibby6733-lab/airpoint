// Shorts 21-30
const C = require('./core.cjs');
const K = require('./kit.cjs');
const { W, H, g, clamp, ease, lerp, line, rect, circle, ell, vgrad, rgrad, glow, fig, crowd, P } = C;
const { sh, HERO, bigWord, darkBG, door, corridor, silhouetteCity, windowsLit, lightning, car, truck, bottle } = K;
const SC = {};

// ---------- 21. Desert motel ----------
function desert(T, o = {}) {
  if (o.day) { g.fillStyle = vgrad(0, 1100, [[0, '#f2a64a'], [1, '#ffd98a']]); g.fillRect(-300, -300, W + 600, 1400); circle(820, 320, 110, '#fff3c8'); glow(820, 320, 400, 'rgba(255,240,200,A)', 0.5); }
  else { C.nightSky(T, '#05040c', '#1b1430', '#4a2a3a', 1100); C.moon(820, 300, 60); }
  C.hills(1080, o.day ? '#c97b4a' : '#3a2230', 40, 5);
  C.ground(1100, o.day ? '#e0b070' : '#4a3226', o.day ? '#b07a40' : '#1e140f');
  // motel
  rect(60, 800, 960, 420, o.day ? '#e8d4b0' : '#5a4636'); for (let i = 0; i < 5; i++) { door(110 + i * 185, 900, 110, 240, o.day ? '#3a7a8a' : '#2a4a54', 0); g.fillStyle = '#fff'; g.font = '34px "Archivo Black"'; g.fillText(String(5 + i), 150 + i * 185, 880); rect(230 + i * 185 - 60, 940, 50, 60, o.day ? '#9ad0e0' : (i === 4 && o.lit9 ? '#ffd98a' : '#1b2533')); }
  rect(40, 760, 1000, 50, '#a0522d'); line([[960, 1220], [960, 520]], '#555', 14); rect(840, 400, 240, 130, '#e02424'); g.fillStyle = '#fff'; g.font = '50px "Archivo Black"'; g.fillText('MOTEL', 870, 485);
}
SC[21] = {
  hook: 'Drink it or save it?', fact: 0, bed: 'wind',
  sfx: [['sting', 2, 0, 0.8], ['click', 6, 0, 1], ['creak', 8, 0, 1.2], ['boom', 10, 0, 1]],
  shots: [
    sh(0, (lt, T) => { desert(T, { day: true }); }, { cam: [1.0, 1.08] }),
    sh(1, (lt, T) => { desert(T, { day: true }); fig({ x: 540, y: 1700, s: 2.3, ...HERO('#c0392b', { cap: '#d9c08a', headlamp: false }), pose: () => ({ armL: [1.85, 1.75], armR: [-1.2, -2.6], legL: [1.75, 1.65], legR: [1.4, 1.5] }), face: 'happy', look: [0.5, -0.5] }); bottle(640, 1140, 1.2, true); }, { cam: [1.1, 1.15], cy: 1300 }),
    sh(2, (lt, T) => { desert(T, { day: true }); C.tint('rgba(120,60,0,0.25)'); bottle(540, 1500, 2.2, true); C.textBox('STILL FULL', 540, 1050, 110, '#ff4b4b', '#000', 14, 'Anton'); }, { hit: true }),
    sh(3, (lt, T) => { desert(T); fig({ x: 540, y: 1650, s: 1.8, ...HERO('#c0392b', { cap: '#d9c08a' }), pose: 'stand', face: 'neutral' }); }, { cam: [1.0, 1.06] }),
    sh(4, (lt, T) => { darkBG('#3a2a20', '#1a120c'); rect(-100, 1200, W + 200, 800, '#5a3a20'); for (let i = 0; i < 12; i++) bottle(150 + (i % 6) * 156, 1180 + Math.floor(i / 6) * 160, 1.0, true); C.textBox('12 BOTTLES  ·  6 GUESTS', 540, 700, 80, '#fff', '#000', 12, 'Anton'); }),
    sh(5, (lt, T) => { C.room('#5a4636', '#2a1e16', 1350); fig({ x: 380, y: 1700, s: 2.2, kind: 'adult', pose: 'point', face: 'determined', dress: '#3a5a8a', hair: (x, y, r) => { g.fillStyle = '#ddd'; g.beginPath(); g.arc(x, y - 6, r + 4, P, 0); g.fill(); } }); fig({ x: 760, y: 1700, s: 2.2, ...HERO('#c0392b', { cap: '#d9c08a' }), pose: 'stand', face: 'neutral', look: [-1, 0] }); }),
    sh(6, (lt, T) => { C.room('#5a4636', '#2a1e16', 1350); fig({ x: 540, y: 1700, s: 2.4, ...HERO('#c0392b', { cap: '#d9c08a' }), pose: () => ({ armL: [1.85, 1.75], armR: [-1.0, -2.5], legL: [1.75, 1.65], legR: [1.4, 1.5] }), face: 'happy' }); bottle(640, 1080, 1.1, false); }),
    sh(7, (lt, T) => { C.room('#5a4636', '#2a1e16', 1350); fig({ x: 540, y: 1700, s: 2.4, kind: 'adult', pose: 'hold', face: 'determined', dress: '#3a5a8a', held: ([x, y], sc) => bottle(x, y + 40 * sc, sc, true), hair: (x, y, r) => { g.fillStyle = '#ddd'; g.beginPath(); g.arc(x, y - 6, r + 4, P, 0); g.fill(); } }); }),
    sh(8, (lt, T) => desert(T, { lit9: false }), { cam: [1.5, 1.6], cx: 900, cy: 1000 }),
    sh(9, (lt, T) => { // through the window: standing still
      darkBG('#2a2018', '#0a0805'); rect(140, 400, 800, 1000, '#0b0f17'); g.globalAlpha = 0.9; fig({ x: 540, y: 1700, s: 3.0, kind: 'zombie', pose: 'hold', face: 'zombie', dress: '#3a5a8a', held: ([x, y], sc) => bottle(x, y + 40 * sc, sc, true), hair: (x, y, r) => { g.fillStyle = '#ddd'; g.beginPath(); g.arc(x, y - 6, r + 4, P, 0); g.fill(); } }); g.globalAlpha = 1;
      rect(130, 390, 820, 24, '#4a3a2a'); rect(130, 1390, 820, 24, '#4a3a2a'); rect(130, 390, 24, 1020, '#4a3a2a'); rect(926, 390, 24, 1020, '#4a3a2a'); rect(530, 390, 20, 1020, '#4a3a2a');
    }, { cam: [1.0, 1.12], shake: 2 }),
    sh(10, (lt, T) => { darkBG('#2a2018', '#0a0805'); bottle(540, 1400, 3.2, true); }, { hit: true, cam: [1.0, 1.1] }),
    sh(11, (lt, T) => desert(T, { day: true }), { cam: [1.1, 1.0] }),
  ],
};

// ---------- 22. Cave ----------
function cave(T, o = {}) {
  darkBG('#141210', '#050403');
  g.fillStyle = '#2a2420'; for (let i = 0; i < 9; i++) { g.beginPath(); g.moveTo(i * 140 - 40, 0); g.lineTo(i * 140 + 30, 180 + (i % 3) * 90); g.lineTo(i * 140 + 90, 0); g.fill(); }
  for (let i = 0; i < 7; i++) { g.beginPath(); g.moveTo(i * 170, H); g.lineTo(i * 170 + 70, H - 160 - (i % 2) * 80); g.lineTo(i * 170 + 140, H); g.fill(); }
  if (o.group) for (let i = 0; i < 6; i++) fig({ x: 140 + i * 160, y: 1500 + (i % 2) * 80, s: 1.1, kind: 'adult', pose: 'stand', face: o.scared ? 'scared' : 'neutral', look: [i < 3 ? 1 : -1, 0], dress: ['#7a5a3a', '#3a5a7a', '#6a3a5a', '#3a6a4a', '#8a6a2a', '#5a5a5a'][i] });
}
SC[22] = {
  hook: 'In the dark, I counted twelve people', fact: 1, bed: 'drone',
  sfx: [['click', 4, 0, 1.4], ['tap', 6, 0, 0.8], ['tap', 6, 0.5, 0.6], ['heartbeat', 7, 0, 1.4], ['sting', 13, 0.8, 1.2]],
  shots: [
    sh(0, (lt, T) => { cave(T); C.flashlight(540, 1900, -P / 2 - 0.2, 1400, 0.3, 0.3); }, { cam: [1.0, 1.08] }),
    sh(1, (lt, T) => { darkBG('#000', '#000'); fig({ x: 540, y: 2050, s: 4.2, ...HERO('#6a4a2a'), pose: 'stand', face: 'scared', look: [Math.sin(T * 2), 0] }); C.tint('rgba(0,0,0,0.85)'); }),
    sh(2, (lt, T) => { cave(T, { group: true }); C.flashlight(540, 1900, -P / 2, 1400, 0.45, 0.35); fig({ x: 540, y: 1800, s: 1.6, ...HERO('#6a4a2a', { lampOn: true }), pose: 'point', face: 'happy' }); }, { cam: [1.0, 1.06] }),
    sh(3, (lt, T) => { cave(T, { group: true }); C.tint('rgba(0,0,0,0.5)'); glow(540, 1600, 300, 'rgba(255,240,180,A)', 0.4); C.textBox('ONE FLASHLIGHT', 540, 700, 100, '#fff', '#000', 14, 'Anton'); }),
    sh(4, (lt, T) => { cave(T, { group: true }); C.tint(lt < 0.4 ? 'rgba(0,0,0,0.5)' : 'rgba(0,0,0,0.97)'); if (lt < 0.4) glow(540, 1600, 300, 'rgba(255,240,180,A)', Math.random() * 0.5); }, { hit: true }),
    sh(6, (lt, T) => { darkBG('#000', '#000'); for (let i = 0; i < 3; i++) { const k = ((T * 0.7) + i * 0.33) % 1; circle(300 + i * 240, lerp(600, 1400, k), 12, `rgba(150,180,220,${1 - k})`); } }),
    sh(7, (lt, T) => { darkBG('#000', '#000'); const b = Math.max(0, Math.sin(T * 7)); circle(540, 900, 120 + b * 30, `rgba(160,20,20,${0.4 + b * 0.4})`); }),
    sh(8, (lt, T) => { darkBG('#000', '#000'); for (let i = 0; i < 12; i++) { const a = 0.15 + 0.1 * Math.sin(T * 2 + i); circle(120 + (i % 6) * 168, 800 + Math.floor(i / 6) * 260, 50, `rgba(230,230,230,${a})`); } }),
    sh(10, (lt, T) => { darkBG('#000', '#000'); bigWord('10', 860, 380, '#fff', T, 0); }),
    sh(11, (lt, T) => { darkBG('#000', '#000'); bigWord('11', 860, 380, '#fff', T, 0); }),
    sh(12, (lt, T) => { darkBG('#000', '#000'); bigWord('12', 860, 380, '#fff', T, 0); }),
    sh(13, (lt, T) => { darkBG('#000', '#000'); if (lt > 0.55) { bigWord('13', 860, 380, '#ff3b3b', T, 0); } if (lt > 0.75) { circle(470, 1500, 10, '#cfd8c8'); circle(560, 1500, 10, '#cfd8c8'); } }, { shake: 0 }),
    sh(14, (lt, T) => { cave(T); C.flashlight(540, 1900, -P / 2 - 0.2, 1400, 0.3, 0.3); }, { cam: [1.1, 1.0] }),
  ],
};

// ---------- 23. Snowplow ----------
function snowRoad(T, o = {}) {
  C.nightSky(T, '#05070e', '#121a2c', '#2a3346', 1000); C.hills(1000, '#cfd8e6', 40, 8); C.ground(1000, '#dfe7f2', '#aeb9cc');
  g.fillStyle = '#9aa4b4'; g.beginPath(); g.moveTo(480, 1000); g.lineTo(600, 1000); g.lineTo(1300, H); g.lineTo(-200, H); g.fill();
  C.snow(T, 0.8, 160);
}
function minivan(x, y, s, o = {}) { g.save(); g.translate(x, y); g.scale(s, s); g.fillStyle = '#6a2a3a'; g.beginPath(); g.roundRect(-260, -230, 520, 230, 40); g.fill(); for (let i = 0; i < 3; i++) rect(-220 + i * 150, -200, 130, 90, o.fog ? 'rgba(220,230,240,0.85)' : '#1b2533'); circle(-160, 0, 50, '#111'); circle(160, 0, 50, '#111'); if (o.buried) { g.fillStyle = '#eef3fa'; g.beginPath(); g.ellipse(0, 0, 340, 90, 0, P, 0); g.fill(); g.beginPath(); g.ellipse(-80, -230, 220, 50, 0, P, 0); g.fill(); } else rect(250, -30, 30, 20, '#333'); g.restore(); }
SC[23] = {
  hook: 'I dug out their tailpipe. Big mistake.', fact: 0, bed: 'wind',
  sfx: [['electric', 7, 0, 0.6], ['tap', 11, 0.8, 1.4], ['tap', 11, 1.1, 1.4], ['tap', 11, 1.4, 1.4], ['sting', 14, 0, 1], ['boom', 15, 0, 1]],
  shots: [
    sh(0, (lt, T) => { snowRoad(T); minivan(540, 1500, 1.4, { buried: true }); }, { cam: [1.0, 1.08] }),
    sh(1, (lt, T) => { snowRoad(T); minivan(540, 1500, 1.4, { buried: true }); for (let i = 0; i < 5; i++) { const k = ((T * 0.4) + i * 0.2) % 1; g.globalAlpha = 0.5 * (1 - k); circle(lerp(800, 600, k), lerp(1480, 1300, k), 40 + k * 80, '#9a9a9a'); } g.globalAlpha = 1; C.textBox('CO', 540, 1000, 160, '#ff4b4b', '#000', 18, 'Anton'); }),
    sh(2, (lt, T) => { darkBG('#1b2230', '#0b0e14'); C.textBox('NO SMELL', 540, 820, 140, '#fff', '#000', 16, 'Anton'); }, { hit: true }),
    sh(3, (lt, T) => { darkBG('#1b2230', '#0b0e14'); C.textBox('NO COLOR', 540, 820, 140, '#fff', '#000', 16, 'Anton'); }, { hit: true }),
    sh(4, (lt, T) => { darkBG('#1b2230', '#0b0e14'); fig({ x: 540, y: 2000, s: 4.0, kind: 'adult', pose: 'stand', face: 'neutral', look: [0, 0.5 + lt * 0.5] }); C.tint(`rgba(0,0,0,${lt * 0.6})`); }),
    sh(5, (lt, T) => { snowRoad(T); g.save(); g.translate(540, 1500); rect(-260, -320, 300, 260, '#e6a12a'); rect(-200, -290, 180, 120, '#1b2533'); rect(40, -200, 300, 160, '#e6a12a'); g.fillStyle = '#c33'; g.beginPath(); g.moveTo(-420, -40); g.lineTo(-260, -200); g.lineTo(-260, 0); g.fill(); circle(-150, 0, 60, '#111'); circle(220, 0, 60, '#111'); glow(-60, -340, 80, 'rgba(255,170,40,A)', Math.floor(T * 4) % 2); g.restore(); }, { cam: [1.0, 1.08] }),
    sh(6, (lt, T) => { snowRoad(T); minivan(540, 1450, 1.3, { buried: true }); }, { cam: [1.0, 1.06] }),
    sh(8, (lt, T) => { snowRoad(T); minivan(540, 1450, 1.6, { fog: true }); }, { cam: [1.1, 1.2], cy: 1250 }),
    sh(9, (lt, T) => { darkBG('#2a2228', '#0b0a0c'); rect(100, 500, 880, 700, 'rgba(220,230,240,0.35)'); for (let i = 0; i < 3; i++) fig({ x: 280 + i * 260, y: 1400, s: [1.6, 1.6, 1.0][i], kind: i === 2 ? 'kid' : 'adult', pose: 'sit', face: 'none', dress: ['#3a5a8a', '#8a3a5a', '#3a8a5a'][i] }); }),
    sh(11, (lt, T) => { snowRoad(T); minivan(540, 1450, 1.3, {}); fig({ x: 900, y: 1500, s: 1.4, ...HERO('#e6a12a', { stripe: '#e8e8e8', lampOn: true }), pose: () => ({ ...POSES_dig(T) }), face: 'determined' }); }),
    sh(12, (lt, T) => { darkBG('#2a2228', '#0b0a0c'); rect(100, 500, 880, 700, 'rgba(220,230,240,0.25)'); for (let i = 0; i < 3; i++) fig({ x: 280 + i * 260, y: 1400, s: [1.6, 1.6, 1.0][i], kind: i === 2 ? 'kid' : 'adult', pose: 'sit', face: 'happy', dress: ['#3a5a8a', '#8a3a5a', '#3a8a5a'][i] }); }),
    sh(14, (lt, T) => { darkBG('#2a2228', '#0b0a0c'); rect(100, 500, 880, 700, 'rgba(220,230,240,0.15)'); for (let i = 0; i < 3; i++) fig({ x: 280 + i * 260, y: 1400, s: [1.6, 1.6, 1.0][i], kind: 'zombie', pose: 'sit', face: 'zombie', look: [0, 0], dress: ['#3a5a8a', '#8a3a5a', '#3a8a5a'][i] }); }, { cam: [1.0, 1.1] }),
    sh(15, (lt, T) => { darkBG('#2a2228', '#0b0a0c'); fig({ x: 540, y: 2100, s: 4.6, kind: 'zombie', pose: 'stand', face: 'zombie', eyeGlow: '#ff3b3b', dress: '#3a5a8a' }); g.fillStyle = 'rgba(220,230,240,0.18)'; g.fillRect(0, 0, W, H); }, { hit: true, cam: [1.0, 1.2], cy: 900 }),
    sh(17, (lt, T) => { snowRoad(T); minivan(540, 1500, 1.4, { buried: true }); }, { cam: [1.1, 1.0] }),
  ],
};
function POSES_dig(T) { const s = Math.sin(T * 6); return { armL: [2.2 + s * 0.4, 2.6], armR: [1.4 + s * 0.4, 2.0], legL: [1.9, 1.6], legR: [1.3, 1.5] }; }

// ---------- 24. Grain silo ----------
function silo(T, o = {}) {
  darkBG('#2a2018', '#0e0a06'); g.fillStyle = '#3a3026'; g.fillRect(140, 0, 800, H);
  for (let i = 0; i < 14; i++) line([[140, i * 140], [940, i * 140]], 'rgba(0,0,0,0.25)', 6);
  const lvl = o.lvl || 1450; g.fillStyle = '#d9a64a'; g.beginPath(); g.moveTo(140, lvl); g.quadraticCurveTo(540, lvl + (o.cone || 0), 940, lvl); g.lineTo(940, H); g.lineTo(140, H); g.fill();
  for (let i = 0; i < 80; i++) circle(160 + (i * 97) % 760, lvl + 30 + (i * 53) % 400, 4, '#b8862a');
  // ladder on right wall
  line([[860, 100], [860, H]], '#8a8f96', 10); line([[920, 100], [920, H]], '#8a8f96', 10); for (let i = 0; i < 18; i++) { if (o.broken === i) continue; line([[860, 120 + i * 100], [920, 120 + i * 100]], '#8a8f96', 8); }
  glow(540, 0, 600, 'rgba(255,230,180,A)', 0.2);
}
SC[24] = {
  hook: 'Grain moves like quicksand', fact: 0, bed: 'hum',
  sfx: [['steps', 3, 0, 1.2], ['creak', 6, 0, 1.4], ['hiss', 7, 0, 1.4], ['crash', 9, 0, 1], ['boom', 10, 0, 1]],
  shots: [
    sh(0, (lt, T) => { silo(T, { cone: 200 * lt }); }, { cam: [1.0, 1.1] }),
    sh(1, (lt, T) => { silo(T, { lvl: 1250 }); fig({ x: 450, y: lerp(1250, 1420, ease(lt)), s: 1.6, ...HERO('#4a7a3a'), pose: 'scared', face: 'shock' }); silo2Cover(1250 + 40); C.textBox('SECONDS', 540, 750, 140, '#ffd23f', '#000', 16, 'Anton'); }, { cam: [1.0, 1.05] }),
    sh(2, (lt, T) => { C.nightSky(T); C.ground(1400, '#3a3020', '#151008'); for (let i = 0; i < 3; i++) { rect(120 + i * 300, 600, 220, 800, '#9aa0a8'); g.fillStyle = '#7a8088'; g.beginPath(); g.moveTo(120 + i * 300, 600); g.lineTo(230 + i * 300, 480); g.lineTo(340 + i * 300, 600); g.fill(); } }, { cam: [1.0, 1.08] }),
    sh(3, (lt, T) => { silo(T); crowd(T, { n: 6, y0: 1450, y1: 1700, sMin: 1.0, sMax: 1.4, spread: 600, adv: 0.0 }); fig({ x: 890, y: 1300, s: 1.1, ...HERO('#4a7a3a', { lampOn: true }), pose: 'arms_up', face: 'scared' }); }),
    sh(4, (lt, T) => { silo(T); fig({ x: 890, y: lerp(1300, 700, lt), s: 1.1, ...HERO('#4a7a3a', { lampOn: true }), pose: () => ({ armL: [-2.0 + Math.sin(T * 6) * 0.3, -1.6], armR: [-1.1 - Math.sin(T * 6) * 0.3, -1.4], legL: [1.9, 1.4], legR: [1.3, 1.7] }), face: 'scared' }); }),
    sh(5, (lt, T) => { silo(T); fig({ x: 890, y: 700, s: 1.1, ...HERO('#4a7a3a', { lampOn: true }), pose: 'arms_up', face: 'scared', look: [0, 1] }); fig({ x: 890, y: lerp(1500, 1250, lt), s: 1.1, kind: 'zombie', pose: 'arms_up', look: [0, -1] }); }),
    sh(6, (lt, T) => { silo(T); fig({ x: 890, y: 700, s: 1.1, ...HERO('#4a7a3a', { lampOn: true }), pose: () => ({ armL: [-2.0, -1.6], armR: [0.4, 0.2], legL: [1.9, 1.4], legR: [1.3, 1.7] }), face: 'determined' }); }, { cam: [1.3, 1.4], cx: 860, cy: 700 }),
    sh(7, (lt, T) => { silo(T, { cone: 400 * lt, lvl: 1450 }); for (let i = 0; i < 5; i++) fig({ x: 300 + i * 110, y: 1450 + 400 * lt * (1 - Math.abs(i - 2) / 3) + 120, s: 1.1, kind: 'zombie', pose: 'arms_up' }); silo2Cover(1450 + 20); }, { shake: 4 }),
    sh(9, (lt, T) => { silo(T, { broken: 6 }); fig({ x: 890, y: lerp(700, 900, ease(lt)), s: 1.1, ...HERO('#4a7a3a', { lampOn: true }), pose: 'scared', face: 'shock' }); }, { hit: true, shake: 10 }),
    sh(10, (lt, T) => { silo(T, { cone: 400, lvl: 1450 }); fig({ x: lerp(800, 600, lt), y: lerp(1100, 1700, ease(lt)), s: 1.1, ...HERO('#4a7a3a', { lampOn: true }), pose: 'arms_up', face: 'shock' }); silo2Cover(1600); }, { shake: 6 }),
    sh(11, (lt, T) => silo(T), { cam: [1.1, 1.0] }),
  ],
};
function silo2Cover(y) { g.fillStyle = '#d9a64a'; g.fillRect(140, y, 800, H - y); }

// ---------- 25. School fire doors ----------
function schoolHall(T, o = {}) {
  corridor(T, { wall: '#c9b98a', floor: '#7a6a5a', ceil: '#e8e2d0', lit: o.lit === undefined ? 0.8 : o.lit, end: '#2a2a2a' });
  for (let i = 0; i < 6; i++) { const k = Math.pow(0.7, i); const x = lerp(470, -100, k), y = lerp(700, 0, k), h = lerp(260, 1900, k); for (let j = 0; j < 2; j++) rect(x + j * 60 * k, y + h * 0.35, 50 * k, h * 0.5, '#3a6a9a'); }
  const shut = o.shut || 0; if (shut > 0) { rect(540 - 420, 260, 420 * shut, 1500, '#9a2f2a'); rect(540 + 420 - 420 * shut, 260, 420 * shut, 1500, '#9a2f2a'); if (shut > 0.98) { rect(520, 260, 40, 1500, '#5a1a1a'); rect(220, 700, 160, 220, '#cfe0ea'); rect(700, 700, 160, 220, '#cfe0ea'); line([[180, 1050], [420, 1050]], '#c9c9c9', 22); line([[660, 1050], [900, 1050]], '#c9c9c9', 22); } }
}
SC[25] = {
  hook: 'I pulled the fire alarm to trap them', fact: 0, bed: 'hum',
  sfx: [['alarm', 3, 0, 1.4], ['thump', 4, 0, 1.4], ['thump', 4, 0.4, 1.2], ['creak', 11, 0, 1.4], ['boom', 11, 0.6, 1]],
  shots: [
    sh(0, (lt, T) => schoolHall(T, { shut: ease(clamp(lt * 1.5)) }), { cam: [1.0, 1.08] }),
    sh(1, (lt, T) => { C.room('#c9b98a', '#7a6a5a', 1500, '#e8e2d0'); rect(380, 500, 320, 200, '#555'); rect(420, 540, 240, 120, '#333'); glow(540, 600, 200, 'rgba(255,60,60,A)', lt > 0.5 ? 0 : 0.6); rect(540 - 60, 700, 120, 900, '#9a2f2a'); C.textBox('MAGNET', 540, 820, 100, '#fff', '#000', 14, 'Anton'); }, { cam: [1.1, 1.15] }),
    sh(2, (lt, T) => { schoolHall(T); fig({ x: 540, y: 1750, s: 2.3, ...HERO('#3a6a9a', { cap: '#2a4a6a' }), pose: 'hold', face: 'neutral', held: ([x, y], sc) => { line([[x, y], [x + 20 * sc, y + 160 * sc]], '#8a5a30', 10 * sc); rect(x - 10 * sc, y + 150 * sc, 70 * sc, 30 * sc, '#ddd'); } }); }),
    sh(3, (lt, T) => { C.room('#c9b98a', '#7a6a5a', 1500, '#e8e2d0'); rect(390, 600, 300, 380, '#e02424'); C.textBox('FIRE', 540, 700, 80, '#fff', '#000', 0, 'Anton'); rect(460, 780, 160, 120, '#fff'); const k = ease(clamp(lt * 3)); rect(480, 800 + k * 60, 120, 40, '#c33'); glow(540, 400, 500, 'rgba(255,40,40,A)', Math.floor(T * 4) % 2 ? 0.5 : 0); }, { hit: true, cam: [1.05, 1.15] }),
    sh(4, (lt, T) => schoolHall(T, { shut: 1 }), { shake: 8, hit: true }),
    sh(5, (lt, T) => { C.room('#8a7a5a', '#4a3a2a', 1450); for (let i = 0; i < 4; i++) rect(i * 300, 300, 10, 1150, '#555'); crowd(T, { n: 14, y0: 1300, y1: 1900, sMin: 0.9, sMax: 1.4, spread: 1100, adv: 0.0 }); C.textBox('GYM', 540, 500, 160, '#fff', '#000', 16, 'Anton'); }),
    sh(6, (lt, T) => { schoolHall(T, { shut: 1 }); fig({ x: 540, y: 1750, s: 2.3, ...HERO('#3a6a9a', { cap: '#2a4a6a' }), pose: 'sit', face: 'happy' }); }),
    sh(7, (lt, T) => { schoolHall(T, { shut: 1 }); C.textBox('NO LOCK', 540, 600, 160, '#ffd23f', '#000', 18, 'Anton'); }, { cam: [1.1, 1.2], cy: 1050 }),
    sh(9, (lt, T) => { schoolHall(T, { shut: 1 }); C.textBox('EXIT', 540, 600, 200, '#2ad04a', '#000', 18, 'Anton'); }, { cam: [1.2, 1.25], cy: 1050 }),
    sh(10, (lt, T) => { C.room('#8a7a5a', '#4a3a2a', 1450); rect(200, 260, 680, 1300, '#9a2f2a'); line([[260, 1050], [820, 1050]], '#c9c9c9', 26); fig({ x: 540, y: 1900, s: 2.8, kind: 'zombie', pose: 'zombieL', face: 'none' }); }),
    sh(11, (lt, T) => { schoolHall(T, { shut: 1 - ease(clamp(lt * 2)) * 0.6 }); crowd(T, { n: 10, y0: 900, y1: 1700, sMin: 0.5, sMax: 1.3, spread: 500, adv: 0.05, dir: 1 }); }, { hit: true, shake: 6 }),
    sh(12, (lt, T) => schoolHall(T, { shut: 0 }), { cam: [1.1, 1.0] }),
  ],
};

// ---------- 26. Pool ----------
function pool(T, o = {}) {
  C.room('#2a3a4a', '#1a2430', 900, '#1d2a38'); for (let i = 0; i < 8; i++) rect(i * 140, 120, 120, 600, o.dark ? '#0b1018' : '#3a5a7a');
  g.fillStyle = o.dark ? '#06202e' : '#1f8fb0'; g.fillRect(-100, 950, W + 200, 1000); rect(-100, 900, W + 200, 60, '#d9d4c8');
  g.strokeStyle = o.dark ? 'rgba(120,180,220,0.15)' : 'rgba(255,255,255,0.35)'; g.lineWidth = 5; for (let i = 0; i < 12; i++) { g.beginPath(); for (let x = -50; x < W + 50; x += 20) g.lineTo(x, 1000 + i * 80 + Math.sin(x / 40 + T * 2 + i + (o.move ? T * 6 : 0)) * (o.move ? 18 : 6)); g.stroke(); }
  if (o.floaters) for (let i = 0; i < 10; i++) { const x = 120 + (i % 5) * 200 + Math.sin(T * 0.5 + i) * 10, y = 1150 + Math.floor(i / 5) * 300 + Math.cos(T * 0.6 + i) * 8; circle(x, y, 40, '#93a08d', '#000', 4); }
}
SC[26] = {
  hook: "Drowning doesn't look like drowning", fact: 0, bed: 'underwater',
  sfx: [['click', 7, 0, 1.4], ['splash', 15, 0.3, 1.5], ['sting', 16, 0, 1.2], ['boom', 16, 0.5, 1]],
  shots: [
    sh(0, (lt, T) => { pool(T); circle(540, 1200, 50, '#fff', '#000', 5); line([[540, 1250], [540, 1330]], '#111', 12); }, { cam: [1.0, 1.08] }),
    sh(1, (lt, T) => { pool(T); C.textBox('NO SPLASHING', 540, 650, 120, '#fff', '#000', 16, 'Anton'); }, { hit: true }),
    sh(2, (lt, T) => { pool(T); C.textBox('NO YELLING', 540, 650, 120, '#fff', '#000', 16, 'Anton'); }, { hit: true }),
    sh(3, (lt, T) => { pool(T); circle(540, 1080, 50, '#fff', '#000', 5); }, { cam: [1.3, 1.4], cy: 1080 }),
    sh(5, (lt, T) => { pool(T); fig({ x: 540, y: 880, s: 2.0, ...HERO('#e02424', { headlamp: false }), pose: 'stand', face: 'neutral', extra: (hd, s2, h2, arms, sc) => { line([[hd[0] - 30 * sc, hd[1] + 50 * sc], [hd[0] + 30 * sc, hd[1] + 70 * sc]], '#e02424', 10 * sc); } }); }),
    sh(6, (lt, T) => { C.room('#2a3a4a', '#1a2430', 1500); door(300, 400, 480, 1100, '#5a6a7a', 0); line([[340, 900], [740, 900]], '#999', 30); line([[340, 950], [740, 950]], '#999', 30); }, { shake: 3 }),
    sh(7, (lt, T) => { pool(T, { dark: lt > 0.3, floaters: true }); if (lt > 0.3) C.tint('rgba(0,0,0,0.6)'); }, { hit: true }),
    sh(8, (lt, T) => { pool(T, { dark: true, floaters: true }); C.tint('rgba(0,0,0,0.65)'); C.flashlight(540, 700, P / 2 + Math.sin(T) * 0.5, 1200, 0.18, 0.5); }),
    sh(9, (lt, T) => { pool(T, { dark: true, floaters: true }); C.tint('rgba(0,0,0,0.5)'); bigWord('10', 700, 300, '#fff', T, 0); }),
    sh(10, (lt, T) => { pool(T, { dark: true, floaters: true }); C.tint('rgba(0,0,0,0.5)'); }, { cam: [1.2, 1.3], cy: 1250 }),
    sh(12, (lt, T) => { pool(T, { dark: true, floaters: true }); C.tint('rgba(0,0,0,0.55)'); C.textBox('TOO QUIET', 540, 700, 140, '#ff4b4b', '#000', 16, 'Anton'); }),
    sh(14, (lt, T) => { darkBG('#06202e', '#020a10'); fig({ x: 540, y: 2050, s: 4.2, ...HERO('#e02424', { headlamp: false }), pose: 'stand', face: 'determined' }); }, { cam: [1.0, 1.1], cy: 900 }),
    sh(15, (lt, T) => { pool(T, { dark: true, floaters: true }); C.tint('rgba(0,0,0,0.4)'); fig({ x: 540, y: lerp(880, 1400, ease(lt)), s: 2.0, ...HERO('#e02424', { headlamp: false }), pose: 'arms_up', face: 'determined' }); }),
    sh(16, (lt, T) => { pool(T, { dark: true, floaters: true, move: true }); C.tint('rgba(0,0,0,0.35)'); fig({ x: 540, y: 1300, s: 1.6, ...HERO('#e02424', { headlamp: false }), pose: 'swim', T, face: 'shock' }); for (let i = 0; i < 6; i++) { const a = i / 6 * 2 * P + T * 0.5; const r = lerp(500, 220, ease(lt)); circle(540 + Math.cos(a) * r, 1250 + Math.sin(a) * r * 0.5, 44, '#93a08d', '#000', 4); } }, { hit: true, shake: 5 }),
    sh(17, (lt, T) => pool(T), { cam: [1.1, 1.0] }),
  ],
};

// ---------- 27. Elevator shaft ----------
function shaft(T, o = {}) {
  darkBG('#1a1c22', '#08090c'); rect(140, 0, 800, H, '#22252c'); line([[220, 0], [220, H]], '#6a6f78', 16); line([[860, 0], [860, H]], '#6a6f78', 16);
  for (let i = 0; i < 6; i++) { const y = ((i * 380 + (o.scroll || 0)) % 2280) - 200; rect(140, y, 800, 20, '#3a3e46'); }
  const cy = o.carY || 1200; const nC = o.cables === undefined ? 4 : o.cables;
  for (let i = 0; i < 4; i++) { const x = 440 + i * 70; if (i < nC) line([[x, -50], [x, cy - 250]], '#aab0b8', 8); else { line([[x, cy - 250], [x + 20, cy - 450]], '#aab0b8', 8); } }
  rect(240, cy - 250, 600, 520, '#5a5f68'); rect(240, cy - 260, 600, 24, '#7a7f88'); if (o.brakes) { rect(200, cy - 220, 40, 80, '#e02424'); rect(840, cy - 220, 40, 80, '#e02424'); }
  return cy;
}
SC[27] = {
  hook: 'Elevators almost never fall. Almost.', fact: 1, bed: 'hum',
  sfx: [['electric', 6, 0, 1], ['creak', 7, 0, 1.2], ['bell', 8, 0.5, 0.7], ['steps', 9, 0, 1.4], ['zap', 11, 0, 1.4], ['zap', 12, 0, 1.4], ['thump', 13, 0, 1.6], ['creak', 14, 0, 1.4], ['boom', 15, 0, 1]],
  shots: [
    sh(0, (lt, T) => shaft(T), { cam: [1.0, 1.08] }),
    sh(1, (lt, T) => { shaft(T); C.textBox('4 CABLES', 540, 900, 130, '#ffd23f', '#000', 16, 'Anton'); }, { cam: [1.1, 1.2], cy: 800 }),
    sh(2, (lt, T) => { shaft(T, { brakes: true }); C.textBox('SAFETY BRAKES', 540, 1150, 110, '#ff4b4b', '#000', 14, 'Anton'); }, { cam: [1.0, 1.05] }),
    sh(3, (lt, T) => { C.room('#3a3e46', '#1a1c22', 1450); fig({ x: 540, y: 1750, s: 2.3, ...HERO('#e6a12a', { stripe: '#e8e8e8' }), pose: 'hold', face: 'neutral', held: ([x, y], sc) => { line([[x, y], [x + 60 * sc, y - 60 * sc]], '#888', 12 * sc); } }); }),
    sh(4, (lt, T) => { const cy = shaft(T, { carY: 1500 }); fig({ x: 540, y: cy - 260, s: 1.3, ...HERO('#e6a12a', { stripe: '#e8e8e8', lampOn: true }), pose: 'sit', face: 'neutral' }); }, { cam: [1.0, 1.06] }),
    sh(5, (lt, T) => { const cy = shaft(T, { carY: 1500 }); fig({ x: 540, y: cy - 260, s: 1.3, ...HERO('#e6a12a', { stripe: '#e8e8e8', lampOn: true }), pose: 'sit', face: 'happy' }); }, { cam: [1.3, 1.35], cy: 1150 }),
    sh(6, (lt, T) => { const cy = shaft(T, { carY: 1500, scroll: T * 600 }); fig({ x: 540, y: cy - 260, s: 1.3, ...HERO('#e6a12a', { stripe: '#e8e8e8', lampOn: true }), pose: 'scared', face: 'shock' }); }, { shake: 4, hit: true }),
    sh(8, (lt, T) => { C.room('#8a7a6a', '#3a3028', 1500); rect(300, 500, 480, 1000, '#7a7f88'); line([[540, 500], [540, 1500]], '#333', 8); circle(860, 1000, 30, '#ffd23f', '#000', 5); fig({ x: 860, y: 1700, s: 1.6, kind: 'zombie', pose: 'point', poseOv: { armR: [-0.5, -0.9] } }); }),
    sh(9, (lt, T) => { C.room('#8a7a6a', '#3a3028', 1500); const op = ease(lt); rect(300, 500, 480, 1000, '#0b0b0b'); rect(300, 500, 240 * (1 - op), 1000, '#7a7f88'); rect(540 + 240 * op, 500, 240 * (1 - op), 1000, '#7a7f88'); crowd(T, { n: 14, y0: 1300, y1: 1950, sMin: 1.0, sMax: 2.0, spread: 1000, adv: 0.08, dir: -1 }); }),
    sh(11, (lt, T) => { shaft(T, { cables: 3, carY: 1500 }); }, { hit: true, shake: 10 }),
    sh(12, (lt, T) => { shaft(T, { cables: 2, carY: 1500 }); }, { hit: true, shake: 12 }),
    sh(13, (lt, T) => { shaft(T, { cables: 2, carY: 1500, brakes: true }); }, { shake: 6 }),
    sh(14, (lt, T) => { const cy = shaft(T, { cables: 2, carY: lerp(1700, 1000, ease(lt)), brakes: false }); fig({ x: 540, y: 300, s: 1.3, ...HERO('#e6a12a', { stripe: '#e8e8e8', lampOn: true }), pose: 'hide', face: 'shock', look: [0, 1] }); rect(140, 310, 800, 20, '#3a3e46'); }, { shake: 3 }),
    sh(15, (lt, T) => { const cy = shaft(T, { cables: 2, carY: lerp(1000, 700, lt) }); fig({ x: 540, y: 300, s: 1.3, ...HERO('#e6a12a', { stripe: '#e8e8e8', lampOn: true }), pose: 'hide', face: 'scared', look: [0, 1] }); rect(140, 310, 800, 20, '#3a3e46'); }, { hit: true, shake: 6, cam: [1.1, 1.3], cy: 500 }),
    sh(16, (lt, T) => shaft(T), { cam: [1.1, 1.0] }),
  ],
};

// ---------- 28. Beach rip current ----------
function beach(T, o = {}) {
  C.nightSky(T, '#03040b', '#0b1028', '#1c2a4a', 700); C.moon(820, 260, 60);
  C.water(700, T, '#0e2a48', '#071a2e'); // sea top part
  // shore curve (sand bottom)
  g.fillStyle = '#c9b48a'; g.beginPath(); g.moveTo(-100, 1450); for (let x = -100; x <= W + 100; x += 30) g.lineTo(x, 1450 + Math.sin(x / 150 + T * 0.8) * 20); g.lineTo(W + 100, H + 100); g.lineTo(-100, H + 100); g.fill();
  g.strokeStyle = 'rgba(255,255,255,0.6)'; g.lineWidth = 8; g.beginPath(); for (let x = -100; x <= W + 100; x += 30) g.lineTo(x, 1440 + Math.sin(x / 150 + T * 0.8) * 20); g.stroke();
  if (o.rip) { g.fillStyle = 'rgba(40,60,80,0.45)'; g.beginPath(); g.moveTo(440, 1450); g.lineTo(640, 1450); g.lineTo(600, 750); g.lineTo(480, 750); g.fill(); for (let i = 0; i < 4; i++) { const y = 1400 - ((T * 300 + i * 160) % 640); line([[540, y], [540, y - 70]], '#ff4b4b', 10); line([[510, y - 40], [540, y - 70], [570, y - 40]], '#ff4b4b', 10); } }
  if (o.side) { for (let i = 0; i < 3; i++) { const x = 600 + ((T * 200 + i * 120) % 360); line([[x, 1000], [x + 70, 1000]], '#2ad04a', 10); line([[x + 40, 970], [x + 70, 1000], [x + 40, 1030]], '#2ad04a', 10); } }
}
SC[28] = {
  hook: 'How to escape a rip current (and them)', fact: 0, bed: 'wind',
  sfx: [['splash', 3, 0, 1.4], ['whoosh', 4, 0, 1.2], ['splash', 7, 0, 1], ['sting', 13, 0.5, 0.8], ['boom', 14, 0, 1]],
  shots: [
    sh(0, (lt, T) => { beach(T, { rip: true }); C.textBox('DON\'T', 540, 1150, 120, '#ff4b4b', '#000', 14, 'Anton'); }, { cam: [1.0, 1.06] }),
    sh(1, (lt, T) => { beach(T, { rip: true, side: true }); C.textBox('SWIM SIDEWAYS', 540, 1150, 110, '#2ad04a', '#000', 14, 'Anton'); }),
    sh(2, (lt, T) => { beach(T); crowd(T, { n: 12, y0: 1500, y1: 1950, sMin: 0.8, sMax: 1.4, xc: 300, spread: 600, adv: 0.0 }); fig({ x: lerp(700, 800, lt), y: 1600, s: 1.4, ...HERO('#e02424', { headlamp: false, lampOn: false }), pose: () => C.runPose(T, -1), face: 'scared' }); }),
    sh(3, (lt, T) => { beach(T); fig({ x: 540, y: lerp(1600, 1450, lt), s: 1.4, ...HERO('#e02424', { headlamp: false }), pose: () => C.runPose(T, -1), face: 'scared' }); }),
    sh(4, (lt, T) => { beach(T, { rip: true }); fig({ x: 540, y: lerp(1350, 900, ease(lt)), s: 0.9, ...HERO('#e02424', { headlamp: false }), pose: 'swim', T, face: 'scared' }); }, { shake: 3 }),
    sh(6, (lt, T) => { beach(T, { rip: true }); fig({ x: 540, y: 850, s: 0.8, ...HERO('#e02424', { headlamp: false }), pose: 'swim', T, face: 'determined' }); }, { cam: [1.3, 1.35], cy: 900 }),
    sh(7, (lt, T) => { beach(T, { rip: true }); for (let i = 0; i < 8; i++) { const k = clamp(lt * 1.2 - i * 0.05); circle(470 + (i % 3) * 70, lerp(1400, 760, k), 26, '#93a08d', '#000', 3); } }),
    sh(9, (lt, T) => { beach(T, { rip: true, side: true }); fig({ x: lerp(540, 860, lt), y: 900, s: 0.8, ...HERO('#e02424', { headlamp: false }), pose: 'swim', T, face: 'determined' }); }),
    sh(11, (lt, T) => { beach(T); fig({ x: 860, y: lerp(900, 1480, ease(lt)), s: 1.0, ...HERO('#e02424', { headlamp: false }), pose: 'swim', T, face: 'happy' }); }),
    sh(12, (lt, T) => { beach(T); fig({ x: 760, y: 1650, s: 1.6, ...HERO('#e02424', { headlamp: false }), pose: 'stand', face: 'happy' }); }, { cam: [1.0, 1.06] }),
    sh(13, (lt, T) => { beach(T); fig({ x: 760, y: 1650, s: 1.6, ...HERO('#e02424', { headlamp: false }), pose: 'stand', face: 'scared', look: [-1, 0] }); }, { cam: [1.0, 1.1], cx: 300 }),
    sh(14, (lt, T) => { beach(T); for (let i = 0; i < 12; i++) fig({ x: 100 + i * 80, y: lerp(1350, 1550, ease(lt)) + (i % 3) * 40, s: 0.8, kind: 'zombie', pose: () => C.walkPose(T + i, 0.5, true, 1) }); }, { hit: true, shake: 4 }),
    sh(15, (lt, T) => beach(T, { rip: true }), { cam: [1.1, 1.0] }),
  ],
};

// ---------- 29. Car in the lake ----------
function lake(T, o = {}) {
  C.nightSky(T, '#03040b', '#0b1028', '#16203a', 800); C.hills(800, '#0d1220', 40, 4);
  C.water(820, T, '#0b2233', '#02080d');
  if (o.car !== undefined) { const sink = o.car; g.save(); g.translate(540, lerp(1000, 1500, sink)); g.rotate(-0.15 + sink * 0.1); car(0, 0, 1.4, '#3b5b8a', { lit: true }); g.restore(); g.fillStyle = 'rgba(11,34,51,0.75)'; g.fillRect(0, 1060, W, H); }
}
SC[29] = {
  hook: 'Seatbelt, window, out', fact: 0, bed: 'underwater',
  sfx: [['splash', 6, 1.2, 1.4], ['thump', 7, 0.4, 1.4], ['thump', 7, 0.8, 1.4], ['crash', 10, 0, 1.4], ['sting', 15, 0.5, 1], ['boom', 16, 0, 1]],
  shots: [
    sh(0, (lt, T) => { lake(T, { car: ease(lt) * 0.3 }); C.textBox('~ 1 MINUTE', 540, 830, 140, '#ffd23f', '#000', 16, 'Anton'); }, { cam: [1.0, 1.08] }),
    sh(1, (lt, T) => { darkBG('#0b2233', '#02080d'); C.textBox('1. SEATBELT', 540, 900, 130, '#fff', '#000', 16, 'Anton'); }, { hit: true }),
    sh(2, (lt, T) => { darkBG('#0b2233', '#02080d'); C.textBox('2. WINDOW', 540, 900, 130, '#fff', '#000', 16, 'Anton'); }, { hit: true }),
    sh(3, (lt, T) => { darkBG('#0b2233', '#02080d'); C.textBox('3. OUT', 540, 900, 130, '#fff', '#000', 16, 'Anton'); }, { hit: true }),
    sh(4, (lt, T) => { darkBG('#0b2233', '#02080d'); C.textBox('KIDS FIRST', 540, 900, 130, '#ffd23f', '#000', 16, 'Anton'); }, { hit: true }),
    sh(5, (lt, T) => { lake(T, { car: 0.6 + lt * 0.3 }); }, { cam: [1.0, 1.06] }),
    sh(6, (lt, T) => { C.nightSky(T, '#03040b', '#0b1028', '#16203a', 800); C.water(820, T, '#0b2233', '#02080d'); C.ground(1300, '#3a3026', '#151008'); g.save(); g.translate(lerp(300, 620, ease(lt)), lerp(1300, 1050, ease(lt))); g.rotate(lt * 0.3); car(0, 0, 0.9, '#3b5b8a', { lit: true }); g.restore(); truck(-40, 1500, -0.6, '#e6a12a'); }),
    sh(7, (lt, T) => { C.water(0, T, '#0d2a3a', '#030b12'); rect(140, 600, 800, 600, '#3b5b8a'); rect(200, 660, 680, 380, '#2a4058'); fig({ x: 360, y: 1300, s: 1.4, kind: 'adult', pose: 'scared', face: 'scared', dress: '#8a3a5a' }); fig({ x: 720, y: 1300, s: 1.2, kind: 'kid', pose: 'scared', face: 'scared', dress: '#3a8a5a' }); circle(980, 900, 60, '#fff', '#000', 8); line([[1100, 950], [990, 910]], '#111', 30); }, { shake: 5 }),
    sh(10, (lt, T) => { C.water(0, T, '#0d2a3a', '#030b12'); rect(140, 600, 800, 600, '#3b5b8a'); for (let i = 0; i < 14; i++) { const a = i / 14 * 2 * P; line([[540, 850], [540 + Math.cos(a) * 340 * ease(lt * 3), 850 + Math.sin(a) * 240 * ease(lt * 3)]], 'rgba(220,240,255,0.8)', 6); } }, { hit: true, shake: 10 }),
    sh(11, (lt, T) => { lake(T); fig({ x: lerp(540, 300, lt), y: lerp(1200, 1000, lt), s: 0.9, kind: 'kid', pose: 'swim', T, face: 'scared', dress: '#3a8a5a' }); fig({ x: lerp(600, 380, lt), y: lerp(1250, 1050, lt), s: 1.1, ...HERO('#e6a12a', { stripe: '#e8e8e8', headlamp: true }), pose: 'swim', T, face: 'determined' }); }),
    sh(12, (lt, T) => { lake(T); fig({ x: lerp(600, 400, lt), y: lerp(1250, 1080, lt), s: 1.1, kind: 'adult', pose: 'swim', T, face: 'scared', dress: '#8a3a5a' }); }),
    sh(13, (lt, T) => { C.nightSky(T, '#03040b', '#0b1028', '#16203a', 800); C.water(820, T, '#0b2233', '#02080d'); C.ground(1300, '#3a3026', '#151008'); fig({ x: 420, y: 1700, s: 2.0, kind: 'adult', pose: 'hold', face: 'happy', dress: '#8a3a5a' }); fig({ x: 470, y: 1700, s: 2.0, kind: 'kid', pose: 'stand', face: 'happy', dress: '#3a8a5a' }); fig({ x: 820, y: 1720, s: 2.0, ...HERO('#e6a12a', { stripe: '#e8e8e8' }), pose: 'stand', face: 'happy' }); }),
    sh(14, (lt, T) => { C.nightSky(T, '#03040b', '#0b1028', '#16203a', 800); C.ground(1300, '#3a3026', '#151008'); fig({ x: 540, y: 2050, s: 4.2, kind: 'adult', pose: 'stand', face: 'sad', dress: '#8a3a5a', look: [0, 0] }); }, { cam: [1.0, 1.1], cy: 900 }),
    sh(16, (lt, T) => { C.nightSky(T, '#03040b', '#0b1028', '#16203a', 800); C.ground(1300, '#3a3026', '#151008'); fig({ x: 540, y: 2050, s: 4.2, kind: 'adult', pose: 'hold', face: 'sad', dress: '#8a3a5a', extra: (hd, s2, hip, arms, sc) => { circle(arms[1][2][0], arms[1][2][1] - 40 * sc, 22 * sc, '#8a2a2a'); } }); C.tint('rgba(60,0,0,0.25)'); }, { hit: true, cam: [1.0, 1.15], cy: 900 }),
    sh(17, (lt, T) => lake(T, { car: 0.8 }), { cam: [1.1, 1.0] }),
  ],
};

// ---------- 30. Golf course ----------
function course(T, o = {}) {
  C.nightSky(T, '#03040a', '#0b1024', o.storm ? '#2a2a3a' : '#182040', 1000); if (o.strike) lightning(o.sx || 540, -50, 1050, o.seed || 3, o.strike);
  C.hills(1000, '#0d1a12', 50, 6); C.ground(1000, '#1f4a2a', '#0b1e10');
  g.fillStyle = '#2f6a3a'; g.beginPath(); g.ellipse(540, 1250, 420, 110, 0, 0, 7); g.fill(); line([[700, 1250], [700, 900]], '#ddd', 8); g.fillStyle = '#e02424'; g.beginPath(); g.moveTo(704, 900); g.lineTo(800, 930); g.lineTo(704, 960); g.fill(); circle(700, 1250, 14, '#000');
  if (o.shed) { rect(40, 1150, 260, 320, '#6a4a2a'); g.fillStyle = '#4a3220'; g.beginPath(); g.moveTo(20, 1160); g.lineTo(170, 1060); g.lineTo(320, 1160); g.fill(); rect(130, 1270, 90, 200, o.doorOpen ? '#ffcf7a' : '#3a2410'); }
  if (o.storm) C.rain(T, 0.35);
}
SC[30] = {
  hook: 'They learned to wait 30 minutes too', fact: 0, bed: 'rain',
  sfx: [['thunder', 0, 0.3, 1.2], ['thunder', 4, 0.3, 1.4], ['thunder', 5, 0, 1.2], ['thunder', 7, 0, 0.5], ['tick', 8, 0, 1], ['tick', 8, 0.5, 1], ['creak', 9, 0, 1.2], ['boom', 10, 0.3, 1]],
  shots: [
    sh(0, (lt, T) => { course(T, { storm: true, strike: lt > 0.4 && lt < 0.6 ? 1 : 0, sx: 900 }); C.textBox('10 MILES', 540, 860, 130, '#fff', '#000', 16, 'Anton'); }, { cam: [1.0, 1.08] }),
    sh(1, (lt, T) => { course(T); C.textBox('WAIT 30 MIN', 540, 760, 130, '#ffd23f', '#000', 16, 'Anton'); }),
    sh(2, (lt, T) => { course(T, { shed: true }); fig({ x: 540, y: 1600, s: 1.8, ...HERO('#3a7a3a', { cap: '#2a5a2a' }), pose: 'hold', face: 'neutral', held: ([x, y], sc) => { line([[x, y - 120 * sc], [x, y + 140 * sc]], '#8a5a30', 10 * sc); line([[x - 40 * sc, y + 140 * sc], [x + 40 * sc, y + 140 * sc]], '#888', 10 * sc); } }); }),
    sh(3, (lt, T) => { course(T, { storm: true }); crowd(T, { n: 10, y0: 1050, y1: 1500, sMin: 0.4, sMax: 0.9, spread: 900, adv: 0.0 }); }),
    sh(4, (lt, T) => { course(T, { storm: true, strike: lt < 0.4 ? 1 : 0, sx: 420, seed: 8 }); for (let i = 0; i < 5; i++) fig({ x: 180 + i * 180, y: 1300, s: 0.8, kind: 'zombie', pose: i === 1 && lt < 0.4 ? 'arms_up' : 'stand', eyeGlow: i === 1 && lt < 0.4 ? '#bfe1ff' : undefined }); }, { hit: true, shake: 10 }),
    sh(5, (lt, T) => { course(T, { storm: true, strike: Math.floor(T * 3) % 3 === 0 ? 1 : 0, sx: 700, seed: Math.floor(T * 3) }); }, { shake: 6 }),
    sh(6, (lt, T) => { darkBG('#2a1d12', '#0e0a06'); for (let i = 0; i < 6; i++) rect(i * 200, 300, 20, 1400, '#3a2818'); fig({ x: 540, y: 1700, s: 2.3, ...HERO('#3a7a3a', { cap: '#2a5a2a', lampOn: true }), pose: 'sit', face: 'neutral' }); C.rain(T, 0.15); }),
    sh(7, (lt, T) => course(T, { storm: true, shed: true }), { cam: [1.0, 1.06] }),
    sh(8, (lt, T) => { darkBG('#0b1024', '#03040a'); circle(540, 860, 300, '#e8e2d0', '#111', 16); const a = -P / 2 + ease(lt) * 2 * P * 0.5; g.fillStyle = 'rgba(255,210,63,0.6)'; g.beginPath(); g.moveTo(540, 860); g.arc(540, 860, 280, -P / 2, a); g.fill(); C.textBox('30:00', 540, 1300, 130, '#ffd23f', '#000', 16, 'Anton'); }),
    sh(9, (lt, T) => { course(T, { shed: true, doorOpen: true }); fig({ x: lerp(175, 260, lt), y: 1480, s: 1.0, ...HERO('#3a7a3a', { cap: '#2a5a2a', lampOn: true }), pose: () => C.walkPose(T), face: 'neutral' }); }, { cam: [1.3, 1.4], cx: 260, cy: 1250 }),
    sh(10, (lt, T) => { course(T); for (let i = 0; i < 8; i++) fig({ x: 220 + i * 90, y: 1260, s: 0.75, kind: 'zombie', pose: 'stand', look: [-1, 0] }); }, { hit: true, cam: [1.0, 1.15], cy: 1150 }),
    sh(11, (lt, T) => { darkBG('#0b1024', '#03040a'); for (let i = 0; i < 3; i++) fig({ x: 220 + i * 320, y: 2100, s: 2.6, kind: 'zombie', pose: 'stand', look: [0, 0], eyeGlow: '#ff3b3b' }); }, { cam: [1.0, 1.1], cy: 1000 }),
    sh(12, (lt, T) => { darkBG('#0b1024', '#03040a'); circle(540, 860, 300, '#e8e2d0', '#111', 16); g.fillStyle = 'rgba(255,60,60,0.6)'; g.beginPath(); g.moveTo(540, 860); g.arc(540, 860, 280, -P / 2, P * 1.5); g.fill(); }, { shake: 3 }),
    sh(13, (lt, T) => course(T, { storm: true, shed: true }), { cam: [1.1, 1.0] }),
  ],
};

module.exports = SC;

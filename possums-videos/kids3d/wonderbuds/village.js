// WonderBuds Village — permanent home location (reuse in every episode; never rebuild per episode).
// Map (world units, characters ≈2.5 tall, camera usually south looking north):
//   Village Square + fountain (0,0) · WonderBuds gate arch (0,15) · signpost (4.2,3.4)
//   Pudding's Snack Shack bakery (18,-7) · Ollie's Treehouse Library (0,-24) · Clover's Flower Garden + bunny burrow (-18,-5)
//   Ziggy's Playground (17,13) · Rosie's house (-9,-13) · Rainbow River + bridge (z≈-40) · Candy Mountain far north-west
import { THREE, mat, mesh, group, SPH, CAP, tube, canvasTex, rng, tree, bush, flowers, grass, cloud, skyDome, bakeEnv, lerp, clamp } from '../lib.js';

export const SPOTS = { square: [0, 0], gate: [0, 15], sign: [4.2, 3.4], bakery: [18, -7], treehouse: [0, -24], garden: [-18, -5], playground: [17, 13], rosieHouse: [-9, -13], bridge: [-6, -40] };
const CBS = ['#ff6b6b', '#ffd43b', '#4dabf7', '#69db7c', '#da77f2', '#ff9f43'];

function label(text, w, h, bg, fg, size) { return canvasTex(w, h, (c) => { c.fillStyle = bg; c.beginPath(); c.roundRect(4, 4, w - 8, h - 8, h * .25); c.fill(); c.lineWidth = 8; c.strokeStyle = '#ffffff'; c.stroke(); c.font = `700 ${size}px Fredoka`; const mw = c.measureText(text).width, k = Math.min(1, (w - 40) / mw); c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillStyle = fg; c.save(); c.translate(w / 2, h / 2 + 4); c.scale(k, k); c.fillText(text, 0, 0); c.restore(); }); }
function sign(parent, text, x, y, z, w = 4, h = 1, bg = '#8a5a33', fg = '#fff8e8', ry = 0) { const g = group(parent, x, y, z); g.rotation.y = ry; mesh(new THREE.BoxGeometry(w + .2, h + .2, .15), mat('#6b4423'), 0, 0, -.06, g);
  mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshStandardMaterial({ map: label(text, 512, Math.round(512 * h / w), bg, fg, Math.round(300 * h / w)), roughness: .7 }), 0, 0, .03, g, { cast: false }); return g; }
function cobbles() { return canvasTex(1024, 1024, (c, w, h) => { c.fillStyle = '#c9b89a'; c.fillRect(0, 0, w, h); const r = rng(5); for (let y = 0; y < h; y += 46) for (let x = (y / 46 % 2) * 30; x < w; x += 62) { const s = 20 + r() * 6; c.fillStyle = ['#e2d4b8', '#d8c7a6', '#ebdfc6', '#cdbb98'][Math.floor(r() * 4)]; c.beginPath(); c.ellipse(x + r() * 6, y + r() * 6, s * 1.25, s * .85, r() * .4, 0, 7); c.fill(); } }); }

function cottage(parent, x, z, o = {}) {
  const g = group(parent, x, 0, z); g.rotation.y = o.ry || 0; const W = o.w || 5, D = o.d || 4, Hh = o.h || 3.4, wall = mat(o.wall || '#fff1d6', { rough: .85 }), trim = mat('#ffffff', { rough: .6 });
  mesh(new THREE.BoxGeometry(W, Hh, D), wall, 0, Hh / 2, 0, g); mesh(new THREE.BoxGeometry(W + .2, .3, D + .2), trim, 0, .15, 0, g);
  const s = new THREE.Shape(); s.moveTo(-W / 2 - .5, 0); s.lineTo(0, o.roofH || 2.3); s.lineTo(W / 2 + .5, 0); s.lineTo(-W / 2 - .5, 0);
  mesh(new THREE.ExtrudeGeometry(s, { depth: D + .7, bevelEnabled: true, bevelThickness: .12, bevelSize: .12, bevelSegments: 3 }), mat(o.roof || '#ff6b6b', { rough: .55 }), 0, Hh, -D / 2 - .35, g);
  mesh(new THREE.BoxGeometry(1.2, 2.1, .12), mat(o.door || '#4dabf7', { kind: 'gloss' }), 0, 1.05, D / 2 + .02, g); mesh(SPH(.07), mat('#ffd43b', { kind: 'gloss' }), .4, 1.05, D / 2 + .12, g);
  for (const sd of [-1, 1]) { const wx = sd * (W / 2 - 1); mesh(new THREE.PlaneGeometry(1, .9), mat('#fff1c2', { emissive: '#ffcf70', ei: .45 }), wx, Hh * .58, D / 2 + .01, g, { cast: false });
    for (const [w, h, xx, yy] of [[1.15, .09, 0, .48], [1.15, .09, 0, -.48], [.09, 1, .55, 0], [.09, 1, -.55, 0], [1, .05, 0, 0]]) mesh(new THREE.BoxGeometry(w, h, .08), trim, wx + xx, Hh * .58 + yy, D / 2 + .04, g);
    mesh(new THREE.BoxGeometry(1.2, .24, .3), mat('#8a5a33'), wx, Hh * .58 - .62, D / 2 + .15, g); for (let k = 0; k < 4; k++) mesh(SPH(.1, 10, 8), mat(CBS[(k + (x | 0)) % 6]), wx - .4 + k * .27, Hh * .58 - .45, D / 2 + .2, g); }
  if (o.chimney !== false) { mesh(new THREE.BoxGeometry(.6, 1.4, .6), mat('#c0574e'), W * .25, Hh + 1.6, -.3, g); }
  return g;
}

export function buildVillage(scene, r) {
  const V = { anim: [] };
  scene.add(skyDome('#5ec2ff', '#e4f7ff', '#fff6d0')); scene.environment = bakeEnv(r, '#86d4ff', '#d8f0c8', '#fff3c0'); scene.environmentIntensity = 1.0;
  scene.fog = new THREE.Fog('#dff3ff', 70, 230);
  const hemi = new THREE.HemisphereLight('#ffffff', '#7cc35a', 1.2); scene.add(hemi);
  const sun = new THREE.DirectionalLight('#fff3dc', 3.0); sun.castShadow = true; sun.shadow.mapSize.set(4096, 4096); sun.shadow.bias = -.0003; sun.shadow.normalBias = .03; sun.shadow.radius = 4;
  Object.assign(sun.shadow.camera, { left: -45, right: 45, top: 45, bottom: -45, near: 1, far: 160 }); sun.position.set(25, 45, 30); scene.add(sun, sun.target); V.sun = sun;
  // ground
  const gg = new THREE.PlaneGeometry(320, 320, 160, 160); gg.rotateX(-Math.PI / 2); { const p = gg.attributes.position, col = [], R = rng(3), a = new THREE.Color('#72c64c'), b = new THREE.Color('#98d862'), cc = new THREE.Color('#5fb240');
    for (let i = 0; i < p.count; i++) { const x = p.getX(i), z = p.getZ(i), d = Math.hypot(x, z * .9), n = .5 + .25 * Math.sin(x * .17 + z * .11) + .25 * Math.sin(x * .05 - z * .23); const k = a.clone().lerp(b, n).lerp(cc, R() * .2); col.push(k.r, k.g, k.b);
      if (d > 48) p.setY(i, (d - 48) * .12 * (1 + .5 * Math.sin(x * .04) * Math.cos(z * .05)) + Math.sin(x * .09) * 1.5); }
    gg.setAttribute('color', new THREE.Float32BufferAttribute(col, 3)); gg.computeVertexNormals(); }
  mesh(gg, new THREE.MeshStandardMaterial({ vertexColors: true, roughness: .95 }), 0, 0, 0, scene, { cast: false });
  // Village Square: cobbles, fountain, lampposts, bunting, benches, flower pots
  const ct = cobbles(); ct.wrapS = ct.wrapT = THREE.RepeatWrapping; ct.repeat.set(3, 3);
  mesh(new THREE.CircleGeometry(10, 64), new THREE.MeshStandardMaterial({ map: ct, roughness: .9 }), 0, .02, 0, scene, { r: [-Math.PI / 2, 0, 0], cast: false });
  mesh(new THREE.TorusGeometry(10, .18, 8, 96), mat('#b8a47e'), 0, .05, 0, scene, { r: [Math.PI / 2, 0, 0] });
  const F = group(scene, 0, 0, 0); const stone = mat('#e9e2d4', { rough: .6 }), stone2 = mat('#cfc6b3', { rough: .7 }), water = mat('#69c3ff', { kind: 'water' });
  mesh(new THREE.CylinderGeometry(2.6, 2.8, .7, 48), stone, 0, .35, 0, F); mesh(new THREE.TorusGeometry(2.6, .2, 12, 48), stone2, 0, .72, 0, F, { r: [Math.PI / 2, 0, 0] });
  mesh(new THREE.CircleGeometry(2.45, 48), water, 0, .62, 0, F, { r: [-Math.PI / 2, 0, 0], cast: false }); mesh(new THREE.CylinderGeometry(.35, .5, 2.2, 24), stone, 0, 1.5, 0, F);
  mesh(new THREE.CylinderGeometry(1.2, .4, .45, 32), stone, 0, 2.6, 0, F); mesh(new THREE.CircleGeometry(1.08, 32), water, 0, 2.82, 0, F, { r: [-Math.PI / 2, 0, 0], cast: false }); mesh(SPH(.32), mat('#ffd43b', { kind: 'gloss' }), 0, 3.15, 0, F);
  const SPN = 140, spray = new THREE.InstancedMesh(SPH(.06, 8, 6), mat('#bfe8ff', { kind: 'water', opacity: .85 }), SPN); spray.frustumCulled = false; scene.add(spray); V.spray = spray;
  const lamp = (x, z) => { const g = group(scene, x, 0, z); mesh(new THREE.CylinderGeometry(.1, .14, 5.6, 10), mat('#3d4a5c', { kind: 'gloss' }), 0, 2.8, 0, g); mesh(SPH(.3, 16, 12), mat('#fff4c2', { emissive: '#ffe08a', ei: .7 }), 0, 5.75, 0, g, { cast: false }); mesh(new THREE.ConeGeometry(.38, .3, 12), mat('#3d4a5c', { kind: 'gloss' }), 0, 6.1, 0, g); return [x, 5.6, z]; };
  const lamps = [[-7, -7], [7, -7], [9.2, 3], [-9.2, 3]].map(([x, z]) => lamp(x, z));
  V.flags = [];
  for (let i = 0; i < 4; i++) { const a = lamps[i], b = lamps[(i + 1) % 4], pts = []; for (let k = 0; k <= 16; k++) { const u = k / 16; pts.push([lerp(a[0], b[0], u), lerp(a[1], b[1], u) - Math.sin(u * Math.PI) * .8, lerp(a[2], b[2], u)]); }
    tube(pts, .02, scene, mat('#ffffff'));
    for (let k = 1; k < 16; k++) { const p = pts[k], fg = new THREE.ConeGeometry(.22, .5, 3); const f = mesh(fg, mat(CBS[k % 6], { side: THREE.DoubleSide }), p[0], p[1] - .28, p[2], scene, { r: [Math.PI, 0, 0], cast: false }); V.flags.push(f); } }
  for (const [x, z, ry] of [[-6.6, -4.6, .9], [6.6, -4.6, -.9]]) { const g = group(scene, x, 0, z); g.rotation.y = ry; mesh(new THREE.BoxGeometry(2.2, .14, .6), mat('#c98a4a'), 0, .62, 0, g); mesh(new THREE.BoxGeometry(2.2, .5, .1), mat('#c98a4a'), 0, 1.0, -.28, g); for (const sd of [-1, 1]) mesh(new THREE.BoxGeometry(.1, .6, .5), mat('#3d4a5c'), sd * .95, .3, 0, g); }
  for (const [x, z] of [[-3.6, -3.2], [3.6, -3.2], [-6.5, 1], [6.5, 1]]) { mesh(new THREE.CylinderGeometry(.45, .35, .6, 16), mat('#e07a4a'), x, .3, z, scene); for (let k = 0; k < 5; k++) mesh(SPH(.16, 10, 8), mat(CBS[k]), x + Math.cos(k * 1.3) * .22, .72, z + Math.sin(k * 1.3) * .22, scene); mesh(SPH(.3, 12, 8), mat('#4caf50'), x, .6, z, scene, { s: [1, .5, 1] }); }
  // signpost to every location
  const sp = group(scene, ...[SPOTS.sign[0], 0, SPOTS.sign[1]]); mesh(new THREE.CylinderGeometry(.12, .15, 4.4, 10), mat('#8a5a33'), 0, 2.2, 0, sp); mesh(SPH(.22), mat('#ffd43b', { kind: 'gloss' }), 0, 4.5, 0, sp);
  [['SNACK SHACK', '#ff8fb1', -.3], ['TREEHOUSE', '#4dabf7', 2.2], ['GARDEN', '#69db7c', 2.9], ['PLAYGROUND', '#ffb02e', -.9], ['RAINBOW RIVER', '#9775fa', 1.6]].forEach(([t, c, ry], i) => sign(sp, t, 0, 3.9 - i * .62, 0, 2.6, .5, c, '#ffffff', ry));
  // gate arch at the village entrance
  const gate = group(scene, SPOTS.gate[0], 0, SPOTS.gate[1]); for (const sd of [-1, 1]) { mesh(new THREE.CylinderGeometry(.35, .4, 5.5, 16), mat('#c98a4a'), sd * 4, 2.75, 0, gate); mesh(SPH(.5), mat('#ffd43b', { kind: 'gloss' }), sd * 4, 5.7, 0, gate); for (let k = 0; k < 7; k++) mesh(SPH(.28, 10, 8), mat(['#4caf50', '#5cbf55'][k % 2]), sd * 4 + Math.sin(k) * .3, .8 + k * .65, .35, gate); }
  mesh(new THREE.TorusGeometry(4, .25, 12, 48, Math.PI), mat('#c98a4a'), 0, 5.2, 0, gate); sign(gate, 'WONDERBUDS VILLAGE', 0, 6.4, .2, 6.5, 1.3, '#ff6b6b', '#ffffff');
  // Pudding's Snack Shack
  const bk = cottage(scene, SPOTS.bakery[0], SPOTS.bakery[1], { wall: '#ffd6e5', roof: '#ff8fb1', door: '#ffffff', w: 7, d: 5, h: 3.6, chimney: false });
  sign(bk, "PUDDING'S SNACK SHACK", 0, 4.25, 2.62, 6, .9, '#b9a3e3', '#ffffff');
  const aw = group(bk, 0, 2.95, 2.6); for (let i = 0; i < 9; i++) { const s = mesh(new THREE.BoxGeometry(.78, .08, 1.3), mat(i % 2 ? '#ffffff' : '#ff6b6b'), -3.1 + i * .78, 0, .55, aw, { r: [.45, 0, 0] }); } for (let i = 0; i < 9; i++) mesh(SPH(.39, 12, 8, 0, Math.PI * 2, Math.PI / 2, Math.PI / 2), mat(i % 2 ? '#ffffff' : '#ff6b6b'), -3.1 + i * .78, -.3, 1.15, aw);
  const cake = group(bk, 0, 5.4, 0); mesh(new THREE.CylinderGeometry(1.4, 1.0, 1.4, 24), mat('#ff8fb1', { rough: .5 }), 0, 0, 0, cake); for (let k = 0; k < 3; k++) mesh(new THREE.TorusGeometry(1.35 - k * .35, .32, 12, 32), mat('#fff4fa', { rough: .4 }), 0, .85 + k * .38, 0, cake, { r: [Math.PI / 2, 0, 0] }); mesh(SPH(.32), mat('#e03131', { kind: 'gloss' }), 0, 2.0, 0, cake);
  for (let k = 0; k < 14; k++) mesh(CAP(.03, .12, 4), mat(CBS[k % 6]), Math.cos(k) * .9, 1.1 + (k % 3) * .3, Math.sin(k) * .9, cake, { r: [k, k * 2, 0], cast: false });
  V.bigCake = cake;
  const ctr = group(scene, SPOTS.bakery[0] - 2.6, 0, SPOTS.bakery[1] + 4.6); mesh(new THREE.BoxGeometry(2.6, 1.1, 1.0), mat('#ffffff', { rough: .6 }), 0, .55, 0, ctr); mesh(new THREE.BoxGeometry(2.8, .12, 1.2), mat('#ff8fb1'), 0, 1.15, 0, ctr);
  for (let k = 0; k < 4; k++) { const c = group(ctr, -.9 + k * .6, 1.2, 0); mesh(new THREE.CylinderGeometry(.18, .13, .22, 12), mat(CBS[k]), 0, .11, 0, c); mesh(SPH(.2, 12, 8), mat('#fff4fa'), 0, .28, 0, c, { s: [1, .8, 1] }); mesh(SPH(.06), mat('#e03131'), 0, .42, 0, c); }
  // Ollie's Treehouse Library
  const th = group(scene, SPOTS.treehouse[0], 0, SPOTS.treehouse[1]); mesh(new THREE.CylinderGeometry(1.4, 2.0, 12, 16), mat('#8a5a33', { rough: .95 }), 0, 6, -1.5, th);
  for (const [x, y, z, s] of [[0, 13, -1.5, 5.5], [-4, 11.5, -1, 3.8], [4, 11.8, -1, 3.8], [-2, 14.5, -2, 3.6], [2.5, 14.2, -2.5, 3.4]]) mesh(SPH(s, 24, 16), mat(['#4caf50', '#5cbf55', '#43a047'][Math.round(x + y) % 3 | 0] || '#4caf50', { rough: .85 }), x, y, z, th);
  mesh(new THREE.CylinderGeometry(4.2, 4.2, .35, 32), mat('#c98a4a'), 0, 5, 0, th); const hut = group(th, 0, 5.2, -.8); mesh(new THREE.BoxGeometry(4.6, 3.2, 3.2), mat('#8fd3ff', { rough: .7 }), 0, 1.6, 0, hut);
  const rf = new THREE.Shape(); rf.moveTo(-2.9, 0); rf.lineTo(0, 1.9); rf.lineTo(2.9, 0); rf.lineTo(-2.9, 0); mesh(new THREE.ExtrudeGeometry(rf, { depth: 3.8, bevelEnabled: false }), mat('#3b5bdb', { rough: .5 }), 0, 3.2, -1.9, hut);
  mesh(new THREE.CircleGeometry(.75, 32), mat('#fff1c2', { emissive: '#ffcf70', ei: .5 }), 0, 1.9, 1.62, hut, { cast: false }); mesh(new THREE.TorusGeometry(.78, .1, 10, 32), mat('#ffffff'), 0, 1.9, 1.63, hut);
  sign(hut, 'LIBRARY', 0, 3.0, 1.66, 2.4, .55, '#ffd43b', '#3b5bdb');
  for (let i = 0; i < 17; i++) { const a = -Math.PI * .1 + i / 16 * Math.PI * 1.2; mesh(new THREE.CylinderGeometry(.05, .05, .9, 6), mat('#ffffff'), Math.cos(a) * 4.0, 5.6, Math.sin(a) * 4.0 * .55 + 1.2, th); }
  { const pts = []; for (let i = 0; i <= 20; i++) { const a = -Math.PI * .1 + i / 20 * Math.PI * 1.2; pts.push([Math.cos(a) * 4.0, 6.05, Math.sin(a) * 4.0 * .55 + 1.2]); } tube(pts, .07, th, mat('#ffffff')); }
  for (const sd of [-1, 1]) mesh(new THREE.CylinderGeometry(.06, .06, 5.2, 6), mat('#8a5a33'), 2.6 + sd * .35, 2.6, 2.6, th); for (let k = 0; k < 9; k++) mesh(new THREE.CylinderGeometry(.04, .04, .7, 6), mat('#8a5a33'), 2.6, .4 + k * .55, 2.6, th, { r: [0, 0, Math.PI / 2] });
  const tel = group(th, -1.6, 5.2, 1.6); for (let k = 0; k < 3; k++) mesh(new THREE.CylinderGeometry(.03, .03, 1.2, 6), mat('#33415c'), Math.cos(k * 2.1) * .25, .55, Math.sin(k * 2.1) * .25, tel, { r: [Math.sin(k * 2.1) * .3, 0, -Math.cos(k * 2.1) * .3] });
  mesh(new THREE.CylinderGeometry(.13, .2, 1.3, 16), mat('#ffd43b', { kind: 'gloss' }), 0, 1.25, 0, tel, { r: [0, 0, 1.0] }); V.telescope = tel;
  for (let k = 0; k < 5; k++) mesh(new THREE.BoxGeometry(.6, .12, .45), mat(CBS[k]), 2.7, 5.3 + k * .13, .4, th, { r: [0, k * .3, 0] });
  // Clover's Flower Garden + bunny burrow cottage
  const gd = group(scene, SPOTS.garden[0], 0, SPOTS.garden[1]);
  for (let i = 0; i < 22; i++) { const a = i / 22 * Math.PI * 2; if (Math.abs(a - Math.PI * .1) < .25) continue; const x = Math.cos(a) * 7, z = Math.sin(a) * 5.5; mesh(new THREE.BoxGeometry(.2, 1.0, .12), mat('#ffffff'), x, .5, z, gd, { r: [0, -a + Math.PI / 2, 0] }); mesh(new THREE.ConeGeometry(.14, .22, 4), mat('#ffffff'), x, 1.1, z, gd); }
  V.bigFlowers = []; [[-3, -2.2, '#ff8ab8', 2.6], [3.2, -2.5, '#ffd43b', 3.0], [-4.6, 1.4, '#da77f2', 2.2], [4.4, 1.2, '#74c0fc', 2.3], [0, -3.4, '#ff922b', 3.3], [-1.8, 2.8, '#ffffff', 1.6], [2.2, 3.0, '#ff6b6b', 1.7]].forEach(([x, z, c, h], i) => {
    const f = group(gd, x, 0, z); mesh(new THREE.CylinderGeometry(.08, .1, h, 8), mat('#3e8e3a'), 0, h / 2, 0, f); mesh(SPH(.35, 12, 8), mat('#4caf50'), .3, h * .4, 0, f, { s: [1.4, .25, .8], r: [0, 0, .5] });
    const head = group(f, 0, h, 0); head.rotation.x = .35; for (let k = 0; k < 7; k++) { const a = k / 7 * Math.PI * 2; mesh(SPH(.36, 14, 10), mat(c, { rough: .6 }), Math.cos(a) * .42, Math.sin(a) * .42, 0, head, { s: [1, 1, .3] }); } mesh(SPH(.3, 14, 10), mat('#ffb02e'), 0, 0, .08, head, { s: [1, 1, .5] }); V.bigFlowers.push(head); });
  for (let row = 0; row < 3; row++) for (let k = 0; k < 6; k++) { const x = -2.6 + k * 1.05, z = 4.2 + row * .0 - .1; if (row) continue; mesh(new THREE.ConeGeometry(.12, .5, 8), mat('#ff922b'), x, .1, z, gd, { r: [Math.PI, 0, 0] }); for (let l = 0; l < 3; l++) mesh(new THREE.ConeGeometry(.05, .35, 4), mat('#4caf50'), x + (l - 1) * .06, .45, z, gd); }
  const burrow = group(gd, 0, 0, -6.5); mesh(SPH(3.2, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2), mat('#7cc95a', { rough: .9 }), 0, 0, 0, burrow, { s: [1.3, 1, 1] }); mesh(new THREE.CircleGeometry(1.0, 32), mat('#8fdcc2', { kind: 'gloss' }), 0, 1.0, 3.1, burrow, { cast: false }); mesh(new THREE.TorusGeometry(1.0, .12, 10, 32), mat('#ffffff'), 0, 1.0, 3.12, burrow); mesh(new THREE.BoxGeometry(2.2, .1, .8), mat('#d9cbb2'), 0, .05, 3.6, burrow);
  for (let k = 0; k < 8; k++) mesh(SPH(.18, 10, 8), mat(CBS[k % 6]), -2.5 + k * .7, 2.6 + Math.sin(k) * .3, Math.cos(k) * .9, burrow, { cast: false });
  // watering can
  { const wc = group(gd, 4.8, 0, -1); mesh(new THREE.CylinderGeometry(.35, .4, .6, 16), mat('#4dabf7', { kind: 'gloss' }), 0, .3, 0, wc); mesh(new THREE.CylinderGeometry(.04, .06, .7, 8), mat('#4dabf7', { kind: 'gloss' }), .45, .55, 0, wc, { r: [0, 0, -.8] }); }
  // Ziggy's Playground
  const pg = group(scene, SPOTS.playground[0], 0, SPOTS.playground[1]); const sand = mesh(new THREE.CircleGeometry(7, 48), mat('#f2dfae', { rough: 1 }), 0, .03, 0, pg, { r: [-Math.PI / 2, 0, 0], cast: false }); sand.scale.set(1, 1, 1);
  const bigTree = tree(pg, -3.5, -3, 1.5, false); V.ropeAnchor = new THREE.Vector3(SPOTS.playground[0] - 1.2, 7.2, SPOTS.playground[1] - 2.2);
  mesh(CAP(.35, 4.5, 8), mat('#8a5a33'), -1.5, 7.2, -2.6, pg, { r: [0, 0, Math.PI / 2 - .15] });
  const sl = group(pg, 3, 0, -1); for (const sd of [-1, 1]) mesh(new THREE.CylinderGeometry(.08, .08, 3.2, 8), mat('#ff6b6b', { kind: 'gloss' }), sd * .6, 1.6, -1.6, sl); for (let k = 0; k < 6; k++) mesh(new THREE.CylinderGeometry(.05, .05, 1.2, 6), mat('#ffd43b'), 0, .4 + k * .5, -1.6, sl, { r: [0, 0, Math.PI / 2] });
  mesh(new THREE.BoxGeometry(1.4, .12, 1.4), mat('#4dabf7'), 0, 3.2, -1.2, sl); mesh(new THREE.BoxGeometry(1.2, .1, 4.2), mat('#ffd43b', { kind: 'gloss' }), 0, 1.65, .8, sl, { r: [.72, 0, 0] });
  for (const sd of [-1, 1]) mesh(new THREE.BoxGeometry(.1, .35, 4.2), mat('#ffb02e', { kind: 'gloss' }), sd * .62, 1.8, .8, sl, { r: [.72, 0, 0] });
  const sw = group(pg, 6.0, 0, 4.0); for (const sd of [-1, 1]) { mesh(new THREE.CylinderGeometry(.09, .09, 3.6, 8), mat('#69db7c', { kind: 'gloss' }), sd * 1.6, 1.7, -.6, sw, { r: [-.25, 0, 0] }); mesh(new THREE.CylinderGeometry(.09, .09, 3.6, 8), mat('#69db7c', { kind: 'gloss' }), sd * 1.6, 1.7, .6, sw, { r: [.25, 0, 0] }); }
  mesh(new THREE.CylinderGeometry(.09, .09, 3.4, 8), mat('#69db7c', { kind: 'gloss' }), 0, 3.45, 0, sw, { r: [0, 0, Math.PI / 2] }); V.swing = group(sw, .6, 3.45, 0); for (const sd of [-1, 1]) mesh(new THREE.CylinderGeometry(.015, .015, 2.4, 4), mat('#555'), sd * .35, -1.2, 0, V.swing); mesh(new THREE.BoxGeometry(.9, .08, .4), mat('#ff6b6b'), 0, -2.4, 0, V.swing);
  mesh(SPH(.6, 16, 12), mat('#ff6b6b', { kind: 'gloss' }), -4.6, .6, .2, pg); mesh(SPH(.4, 16, 12), mat('#4dabf7', { kind: 'gloss' }), 1.4, .4, -4.6, pg);
  // Rosie's house + extra cottages
  const rh = cottage(scene, SPOTS.rosieHouse[0], SPOTS.rosieHouse[1], { wall: '#ffe3cc', roof: '#c8562a', door: '#20b2aa', ry: .35 }); const fp = group(rh, 2.8, 0, 2.2); mesh(new THREE.CylinderGeometry(.06, .06, 4.5, 8), mat('#ffffff'), 0, 2.25, 0, fp); V.flag = mesh(new THREE.PlaneGeometry(1.4, .9, 8, 4), mat('#20b2aa', { side: THREE.DoubleSide }), .72, 4.0, 0, fp, { cast: false });
  cottage(scene, 9, -15, { wall: '#e3f6ff', roof: '#4dabf7', door: '#ff922b', ry: -.3 }); cottage(scene, -20, 9, { wall: '#fff6c9', roof: '#69db7c', door: '#da77f2', ry: 1.2, w: 4.5 }); cottage(scene, 27, 3, { wall: '#efe3ff', roof: '#9775fa', door: '#ffd43b', ry: -1.3, w: 4.5 });
  // paths from the square to each place
  const R0 = rng(9); for (const [x, z] of Object.values({ b: SPOTS.bakery, t: SPOTS.treehouse, g: SPOTS.garden, p: SPOTS.playground, gt: SPOTS.gate, r: SPOTS.rosieHouse })) { const d = Math.hypot(x, z); for (let s = 10.6; s < d - 3; s += 1.15) { const u = s / d; mesh(SPH(.45, 14, 8), mat('#e2d4b8', { rough: .9 }), x * u + (R0() - .5) * .5, .02, z * u + (R0() - .5) * .5, scene, { s: [1, .12, .8], cast: false }); } }
  // Rainbow River + bridge, trees, bushes, flowers, grass, mountains, clouds
  const riv = new THREE.PlaneGeometry(220, 7, 100, 1); riv.rotateX(-Math.PI / 2); { const p = riv.attributes.position; for (let i = 0; i < p.count; i++) p.setZ(i, p.getZ(i) + Math.sin(p.getX(i) * .05) * 4); }
  mesh(riv, mat('#5fc0ff', { kind: 'water' }), 0, .05, -41, scene, { cast: false });
  const br = group(scene, SPOTS.bridge[0], 0, SPOTS.bridge[1]); for (let i = 0; i < 7; i++) mesh(new THREE.TorusGeometry(4.6 - i * .02, .16, 8, 32, Math.PI), mat(['#ff6b6b', '#ff9f43', '#ffd43b', '#69db7c', '#4dabf7', '#748ffc', '#b57cff'][i]), (i - 3) * .3, 0, 0, br, { r: [0, Math.PI / 2, 0] });
  mesh(new THREE.BoxGeometry(2.4, .15, 9.5), mat('#c98a4a'), 0, 1.2, 0, br, { s: [1, 1, 1] }).visible = false;
  const treeSpots = []; const RT = rng(42); for (let i = 0; i < 44; i++) { const a = RT() * Math.PI * 2, d = 30 + RT() * 22; const x = Math.cos(a) * d, z = Math.sin(a) * d * .9; if ((z < -36 && z > -46) || (z > 18 && Math.abs(x) < 16)) continue; const ts = .9 + RT() * .5; treeSpots.push([x, z, ts]); tree(scene, x, z, ts, RT() > .5); }
  for (const [x, z] of [[-11, -2], [11, -1], [-12.5, 8.6], [12.5, 8.6], [-5, -16], [5, -18], [22, -12], [-24, -12], [24, 18], [-14, 18]]) tree(scene, x, z, .75, true);
  [[-13, -9], [13, -11], [-25, 2], [25, -5], [-9, 12], [10, 9], [21, 7], [-12, 15]].forEach(([x, z], i) => bush(scene, x, z, 1, ['#4caf50', '#43a047', '#5cbf55'][i % 3], CBS[i % 6]));
  const avoid = (x, z) => Math.hypot(x, z) < 10.6 || Math.hypot(x - SPOTS.garden[0], (z - SPOTS.garden[1]) * 1.25) < 7.2 || Math.hypot(x - SPOTS.playground[0], z - SPOTS.playground[1]) < 7.2 || Math.hypot(x - SPOTS.bakery[0], z - SPOTS.bakery[1]) < 6 || Math.hypot(x - SPOTS.treehouse[0], z - SPOTS.treehouse[1]) < 6 || (z < -37 && z > -45);
  flowers(scene, 420, [-34, 34, -36, 28, avoid], 13); grass(scene, 14000, [-36, 36, -38, 30, avoid], 7);
  for (const [x, z, s, c] of [[-80, -150, 50, '#9bd47a'], [40, -170, 60, '#8ccb6a'], [130, -140, 55, '#a2da82'], [-150, -90, 45, '#94d374']]) mesh(SPH(1, 32, 16), mat(c, { rough: 1 }), x, -s * .45, z, scene, { s: [s * 1.5, s, s], cast: false });
  const cm = group(scene, -70, 0, -135); mesh(new THREE.ConeGeometry(38, 62, 48), mat('#ffb3d1', { rough: .6 }), 0, 28, 0, cm, { cast: false }); for (let k = 0; k < 5; k++) mesh(new THREE.TorusGeometry(31 - k * 6, 1.5, 8, 48), mat('#ffffff'), 0, 6 + k * 11, 0, cm, { r: [Math.PI / 2, 0, 0], cast: false }); mesh(SPH(5), mat('#ff6b6b', { kind: 'gloss' }), 0, 60, 0, cm, { cast: false });
  V.clouds = [[-40, 34, -90, 3], [10, 40, -110, 3.5], [55, 36, -95, 3], [90, 42, -120, 3.5], [-90, 38, -100, 3]].map(([x, y, z, s]) => cloud(scene, x, y, z, s));
  const sunM = mesh(SPH(7, 32, 16), new THREE.MeshBasicMaterial({ color: '#fff3b0', fog: false }), 70, 75, -170, scene, { cast: false });
  // butterflies
  V.flies = [0, 1, 2, 3].map(i => { const g = group(scene); const c = ['#ffb02e', '#da77f2', '#4dabf7', '#ff6b6b'][i]; const wl = mesh(SPH(.22, 12, 8), mat(c, { side: THREE.DoubleSide }), -.2, 0, 0, g, { s: [1, .12, .8], cast: false }), wr = mesh(SPH(.22, 12, 8), mat(c, { side: THREE.DoubleSide }), .2, 0, 0, g, { s: [1, .12, .8], cast: false }); mesh(CAP(.03, .25, 4), mat('#2b1d1d'), 0, 0, 0, g, { r: [Math.PI / 2, 0, 0], cast: false }); g.userData = { wl, wr }; return g; });
  // ---------------- collision footprints for QC: c = circle {x,z,r}, b = box {x,z,w,d,ry}; y0..h = vertical extent
  const O = V.obstacles = []; const ob = (o) => O.push({ y0: 0, h: 9, ...o });
  ob({ t: 'c', n: 'fountain', x: 0, z: 0, r: 2.75, h: .74 }); ob({ t: 'c', n: 'fountain column', x: 0, z: 0, r: .6, h: 3.5 });
  lamps.forEach(([x, , z], i) => ob({ t: 'c', n: 'lamp ' + i, x, z, r: .22 }));
  [[-6.6, -4.6, .9], [6.6, -4.6, -.9]].forEach(([x, z, ry], i) => ob({ t: 'b', n: 'bench ' + i, x, z, w: 2.3, d: .75, ry, h: 1.15 }));
  [[-3.6, -3.2], [3.6, -3.2], [-6.5, 1], [6.5, 1]].forEach(([x, z], i) => ob({ t: 'c', n: 'flower pot ' + i, x, z, r: .5, h: .95 }));
  ob({ t: 'c', n: 'signpost', x: SPOTS.sign[0], z: SPOTS.sign[1], r: .22 }); for (const sd of [-1, 1]) ob({ t: 'c', n: 'gate post', x: sd * 4, z: SPOTS.gate[1], r: .5 });
  ob({ t: 'b', n: 'snack shack', x: SPOTS.bakery[0], z: SPOTS.bakery[1], w: 7.3, d: 5.3, ry: 0 }); ob({ t: 'b', n: 'snack counter', x: SPOTS.bakery[0] - 2.6, z: SPOTS.bakery[1] + 4.6, w: 2.8, d: 1.2, ry: 0, h: 1.25 });
  ob({ t: 'c', n: 'treehouse trunk', x: SPOTS.treehouse[0], z: SPOTS.treehouse[1] - 1.5, r: 2.0, h: 5 }); ob({ t: 'c', n: 'treehouse ladder', x: 2.6, z: SPOTS.treehouse[1] + 2.6, r: .4, h: 5.2 });
  ob({ t: 'c', n: 'telescope', x: -1.6, z: SPOTS.treehouse[1] + 1.6, r: .4, y0: 5.2, h: 6.9 }); ob({ t: 'c', n: 'book stack', x: 2.7, z: SPOTS.treehouse[1] + .4, r: .45, y0: 5.2, h: 6.0 }); ob({ t: 'b', n: 'treehouse hut', x: 0, z: SPOTS.treehouse[1] - .8, w: 4.7, d: 3.3, ry: 0, y0: 5.2, h: 9 });
  [[-3, -2.2], [3.2, -2.5], [-4.6, 1.4], [4.4, 1.2], [0, -3.4], [-1.8, 2.8], [2.2, 3.0]].forEach(([x, z], i) => ob({ t: 'c', n: 'garden flower ' + i, x: SPOTS.garden[0] + x, z: SPOTS.garden[1] + z, r: .3 }));
  ob({ t: 'c', n: 'bunny burrow', x: SPOTS.garden[0], z: SPOTS.garden[1] - 6.5, r: 4.0, h: 3.2 }); ob({ t: 'c', n: 'watering can', x: SPOTS.garden[0] + 4.8, z: SPOTS.garden[1] - 1, r: .45, h: .8 });
  const pgx = SPOTS.playground[0], pgz = SPOTS.playground[1];
  ob({ t: 'c', n: 'playground tree', x: pgx - 3.5, z: pgz - 3, r: .9 }); ob({ t: 'b', n: 'slide', x: pgx + 3, z: pgz - .9, w: 1.5, d: 4.4, ry: 0, h: 3.4 });
  for (const sx of [-1.6, 1.6]) for (const sz of [-.95, .95]) ob({ t: 'c', n: 'swing post', x: pgx + 6 + sx, z: pgz + 4 + sz, r: .25 });
  ob({ t: 'c', n: 'red ball', x: pgx - 4.6, z: pgz + .2, r: .6, h: 1.2 }); ob({ t: 'c', n: 'blue ball', x: pgx + 1.4, z: pgz - 4.6, r: .4, h: .8 });
  [[SPOTS.rosieHouse, .35, 5, 4], [[9, -15], -.3, 5, 4], [[-20, 9], 1.2, 4.5, 4], [[27, 3], -1.3, 4.5, 4]].forEach(([p, ry, w, d], i) => ob({ t: 'b', n: 'house ' + i, x: p[0], z: p[1], w: w + .3, d: d + .3, ry }));
  [[-11, -2], [11, -1], [-12.5, 8.6], [12.5, 8.6], [-5, -16], [5, -18], [22, -12], [-24, -12], [24, 18], [-14, 18]].forEach(([x, z], i) => ob({ t: 'c', n: 'tree ' + i, x, z, r: .45 }));
  treeSpots.forEach(([x, z, sc], i) => ob({ t: 'c', n: 'forest tree ' + i, x, z, r: .55 * sc })); ob({ t: 'c', n: 'playground tree trunk', x: pgx - 3.5, z: pgz - 3, r: .85 });
  [[-13, -9], [13, -11], [-25, 2], [25, -5], [-9, 12], [10, 9], [21, 7], [-12, 15]].forEach(([x, z], i) => ob({ t: 'c', n: 'bush ' + i, x, z, r: 1.1, h: 1.3 }));
  // per-frame ambient animation
  const M4 = new THREE.Matrix4(), V3 = new THREE.Vector3(), Q = new THREE.Quaternion(), S3 = new THREE.Vector3();
  V.update = (t) => {
    for (let i = 0; i < SPN; i++) { const ph = (t * .9 + i / SPN) % 1, a = i * 2.399, v = .9 + (i % 5) * .08; const x = Math.cos(a) * v * ph * 1.2, z = Math.sin(a) * v * ph * 1.2, y = 3.3 + 2.4 * ph - 4.9 * ph * ph * 1.0;
      M4.compose(V3.set(x, Math.max(.7, y), z), Q, S3.setScalar(y < .75 ? 0 : 1)); spray.setMatrixAt(i, M4); } spray.instanceMatrix.needsUpdate = true;
    V.flags.forEach((f, i) => { f.rotation.z = Math.sin(t * 3 + i) * .18; });
    if (V.flag) { const p = V.flag.geometry.attributes.position; for (let i = 0; i < p.count; i++) { const x = p.getX(i); p.setZ(i, Math.sin(t * 5 + x * 3) * .12 * (x + .7)); } p.needsUpdate = true; }
    V.clouds.forEach((c, i) => c.position.x += 0); V.clouds.forEach((c, i) => { c.position.x = [-40, 10, 55, 90, -90][i] + t * .6; });
    V.bigFlowers.forEach((h, i) => { h.rotation.z = Math.sin(t * 1.3 + i) * .08; });
    if (V.swing) V.swing.rotation.x = Math.sin(t * 2.2) * .35;
    V.flies.forEach((f, i) => { const c = [SPOTS.garden, SPOTS.square, SPOTS.playground, SPOTS.garden][i], a = t * .6 + i * 1.7; f.position.set(c[0] + Math.cos(a) * (3 + i), 3.6 + Math.sin(a * 2) * .5, c[1] + Math.sin(a) * 2.2 - 2.5); f.rotation.set(.9, -a, .2); const fl = Math.sin(t * 26 + i) * .9; f.userData.wl.rotation.z = fl; f.userData.wr.rotation.z = -fl; });
  };
  return V;
}

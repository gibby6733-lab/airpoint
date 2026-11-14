// kids3d — a small three.js toolkit for soft "toy 3D" kids cartoons (9:16, deterministic: everything is a function of time t).
import * as THREE from './vendor/three.module.js';
export { THREE };
export const W = 1080, H = 1920;
export const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x)), lerp = (a, b, k) => a + (b - a) * k, seg = (u, a, b) => clamp((u - a) / (b - a));
export const eOut = k => 1 - Math.pow(1 - k, 3), eIn = k => k * k * k, eInOut = k => k < .5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2;
export const eBack = k => { const c1 = 1.9, c3 = c1 + 1; return 1 + c3 * Math.pow(k - 1, 3) + c1 * Math.pow(k - 1, 2); };
export const eElastic = k => k === 0 || k === 1 ? k : Math.pow(2, -10 * k) * Math.sin((k * 10 - .75) * (2 * Math.PI) / 3) + 1;
export function rng(seed) { let s = seed >>> 0; return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296); }

// ------------------------------------------------------------------ renderer / scene
export function setup() {
  const r = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true, powerPreference: 'high-performance' });
  r.setPixelRatio(1); r.setSize(W, H); r.shadowMap.enabled = true; r.shadowMap.type = THREE.PCFSoftShadowMap;
  r.toneMapping = THREE.ACESFilmicToneMapping; r.toneMappingExposure = 1.05; r.outputColorSpace = THREE.SRGBColorSpace;
  const scene = new THREE.Scene(); const cam = new THREE.PerspectiveCamera(40, W / H, .1, 400);
  const out = document.createElement('canvas'); out.width = W; out.height = H; out.id = 'c'; document.body.appendChild(out);
  return { r, scene, cam, out, octx: out.getContext('2d') };
}
// gradient sky dome; also used to bake a soft environment map (reflections + ambient)
export function skyDome(top, bottom, sun) {
  const g = new THREE.SphereGeometry(200, 32, 16), col = [], ct = new THREE.Color(top), cb = new THREE.Color(bottom), cs = new THREE.Color(sun || bottom);
  const p = g.attributes.position; for (let i = 0; i < p.count; i++) { const y = p.getY(i) / 200, k = clamp(y * 1.4 + .15); const c = cb.clone().lerp(ct, k); if (sun && y > .1) c.lerp(cs, Math.pow(clamp(1 - Math.hypot(p.getX(i) / 200 - .3, y - .5) * 2.2), 3) * .8); col.push(c.r, c.g, c.b); }
  g.setAttribute('color', new THREE.Float32BufferAttribute(col, 3));
  return new THREE.Mesh(g, new THREE.MeshBasicMaterial({ vertexColors: true, side: THREE.BackSide, fog: false, depthWrite: false }));
}
export function bakeEnv(r, top, bottom, sun) { const s = new THREE.Scene(); s.add(skyDome(top, bottom, sun)); const pm = new THREE.PMREMGenerator(r); const t = pm.fromScene(s, .02).texture; pm.dispose(); return t; }

// ------------------------------------------------------------------ materials
const MC = {};
export function mat(color, o = {}) {
  const key = color + JSON.stringify(o); if (MC[key]) return MC[key];
  const kind = o.kind || 'std'; let m;
  if (kind === 'fur') m = new THREE.MeshPhysicalMaterial({ color, roughness: .85, sheen: 1, sheenRoughness: .5, sheenColor: new THREE.Color(color).lerp(new THREE.Color('#ffffff'), .45) });
  else if (kind === 'gloss') m = new THREE.MeshPhysicalMaterial({ color, roughness: .32, clearcoat: 1, clearcoatRoughness: .15 });
  else if (kind === 'eye') m = new THREE.MeshPhysicalMaterial({ color, roughness: .08, clearcoat: 1, clearcoatRoughness: .02 });
  else if (kind === 'basic') m = new THREE.MeshBasicMaterial({ color, transparent: !!o.transparent, opacity: o.opacity ?? 1, depthWrite: o.depthWrite ?? true, fog: o.fog ?? true });
  else if (kind === 'water') m = new THREE.MeshPhysicalMaterial({ color, roughness: .04, metalness: .15, clearcoat: 1, clearcoatRoughness: .02, transparent: true, opacity: o.opacity ?? .92, envMapIntensity: 1.6 });
  else m = new THREE.MeshStandardMaterial({ color, roughness: o.rough ?? .7, metalness: o.metal ?? 0, emissive: o.emissive || '#000000', emissiveIntensity: o.ei ?? 1, transparent: !!o.transparent, opacity: o.opacity ?? 1, side: o.side ?? THREE.FrontSide, flatShading: !!o.flat });
  return (MC[key] = m);
}
export function mesh(geo, m, x = 0, y = 0, z = 0, parent, o = {}) {
  const me = new THREE.Mesh(geo, m); me.position.set(x, y, z); me.castShadow = o.cast ?? true; me.receiveShadow = o.recv ?? true;
  if (o.s) Array.isArray(o.s) ? me.scale.set(...o.s) : me.scale.setScalar(o.s); if (o.r) me.rotation.set(...o.r); if (parent) parent.add(me); return me;
}
export function group(parent, x = 0, y = 0, z = 0) { const g = new THREE.Group(); g.position.set(x, y, z); if (parent) parent.add(g); return g; }
export const SPH = (r = 1, w = 32, h = 24, ...rest) => new THREE.SphereGeometry(r, w, h, ...rest);
export const CAP = (r, l, s = 10) => new THREE.CapsuleGeometry(r, l, 8, s * 2);
export function tube(points, r, parent, m, closed = false) { const c = new THREE.CatmullRomCurve3(points.map(p => new THREE.Vector3(...p))); return mesh(new THREE.TubeGeometry(c, 24, r, 8, closed), m, 0, 0, 0, parent, { cast: false }); }
export function canvasTex(w, h, draw) { const c = document.createElement('canvas'); c.width = w; c.height = h; draw(c.getContext('2d'), w, h); const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4; return t; }

// ------------------------------------------------------------------ face kit (cute big eyes, blink, brows, talking mouth)
export function eyes(parent, o) {
  const E = { L: null, R: null, lids: [], brows: [], irises: [], pupils: [] }, sep = o.sep, y = o.y, z = o.z, r = o.r;
  for (const sd of [-1, 1]) {
    const g = group(parent, sd * sep, y, z); g.rotation.y = sd * (o.yaw ?? .18);
    mesh(SPH(r, 32, 24), mat('#ffffff', { kind: 'eye' }), 0, 0, 0, g, { s: [1, 1.12, .7], cast: false });
    const ir = mesh(SPH(r * .68, 32, 24), mat(o.iris || '#4a2c17', { kind: 'eye' }), 0, -r * .05, r * .38, g, { s: [1, 1.1, .55], cast: false });
    const pu = mesh(SPH(r * .4, 24, 16), mat('#0d0d14', { kind: 'eye' }), 0, -r * .05, r * .6, g, { s: [1, 1.1, .4], cast: false });
    mesh(SPH(r * .2, 16, 12), mat('#ffffff', { kind: 'basic' }), r * .2 * -sd + r * .05, r * .22, r * .72, g, { cast: false });
    mesh(SPH(r * .09, 12, 8), mat('#ffffff', { kind: 'basic' }), -r * .18 * -sd, -r * .25, r * .74, g, { cast: false });
    const lid = null;
    const brow = mesh(CAP(r * .14, r * .8, 6), mat(o.brow || '#3b2414'), 0, r * 1.45, r * .35, g, { r: [0, 0, Math.PI / 2], cast: false });
    E[sd < 0 ? 'L' : 'R'] = g; E.lids.push(lid); E.brows.push(brow); E.irises.push(ir); E.pupils.push(pu);
  }
  return E;
}
// blink: 0 open .. 1 closed; look: [-1..1, -1..1]; brow: -1 worried .. 1 surprised; wide: eye scale
export function faceEyes(E, { blink = 0, look = [0, 0], brow = 0, wide = 1, r }) {
  for (const [i, g] of [E.L, E.R].entries()) { g.scale.set(wide, wide * (1 - blink * .9), wide); E.irises[i].position.x = look[0] * r * .22; E.irises[i].position.y = -r * .05 + look[1] * r * .2; E.pupils[i].position.x = look[0] * r * .26; E.pupils[i].position.y = -r * .05 + look[1] * r * .22;
    const sd = i ? 1 : -1; E.brows[i].position.y = r * (1.45 + brow * .25); E.brows[i].rotation.z = Math.PI / 2 + sd * brow * -.35; }
}
export function mouth(parent, o) {
  const g = group(parent, 0, o.y, o.z); g.rotation.x = o.tilt ?? .15;
  const smile = tube([[-o.w, .06, 0], [-o.w * .5, -.05, .02], [0, -.08, .03], [o.w * .5, -.05, .02], [o.w, .06, 0]], o.th || .035, g, mat('#2a1418'));
  const open = mesh(SPH(o.w * .62, 24, 16), mat('#5a1420', { rough: .5 }), 0, -.05, 0, g, { s: [1, .01, .45], cast: false });
  const tongue = mesh(SPH(o.w * .4, 16, 12), mat('#ff7a8a'), 0, -.1, .03, g, { s: [1, .01, .4], cast: false });
  return { g, smile, open, tongue, w: o.w };
}
export function faceMouth(M, open = 0, smile = 1) { M.open.scale.y = .01 + open * .75; M.tongue.scale.y = .01 + open * .45; M.tongue.position.y = -.06 - open * .08; M.smile.visible = open < .25; M.smile.scale.y = smile; }

// ------------------------------------------------------------------ characters
export function otter(o = {}) {
  const F = o.fur || '#a86d3c', CR = '#f6dcb6', root = group(null), body = group(root), R = { root, body };
  const fur = mat(F, { kind: 'fur' }), cream = mat(CR, { kind: 'fur' }), coatM = mat(o.coat || '#ffcf2e', { kind: 'gloss' }), bootM = mat(o.boots || '#ff4a4a', { kind: 'gloss' });
  // torso + belly
  mesh(SPH(.8), fur, 0, 1.15, 0, body, { s: [1, 1.12, .9] }); R.belly = mesh(SPH(.62), cream, 0, 1.1, .32, body, { s: [1, 1.15, .75] });
  // tail
  R.tail = group(body, 0, .55, -.6); mesh(CAP(.22, .9, 10), fur, 0, -.1, -.45, R.tail, { r: [1.2, 0, 0], s: [1.3, 1, .7] });
  // legs + feet / boots
  R.legs = []; R.boots = [];
  for (const sd of [-1, 1]) { const l = group(body, sd * .36, .5, 0); mesh(CAP(.2, .3, 10), fur, 0, -.2, 0, l); mesh(SPH(.22), cream, 0, -.43, .1, l, { s: [1, .6, 1.3] }); R.legs.push(l);
    const b = group(l, 0, -.32, .04); mesh(new THREE.CylinderGeometry(.25, .27, .42, 24), bootM, 0, .02, 0, b); mesh(SPH(.27), bootM, 0, -.14, .14, b, { s: [1, .62, 1.3] }); mesh(new THREE.CylinderGeometry(.3, .3, .07, 24), mat('#3a2a2a'), 0, -.24, .08, b, { s: [1, 1, 1.35] }); mesh(new THREE.TorusGeometry(.25, .04, 8, 24), mat('#ffffff', { kind: 'gloss' }), 0, .23, 0, b, { r: [Math.PI / 2, 0, 0] }); R.boots.push(b); }
  // raincoat (A-line lathe), hood, buttons, pockets, collar
  R.coat = group(body, 0, 0, 0);
  const prof = []; for (let i = 0; i <= 12; i++) { const k = i / 12; prof.push(new THREE.Vector2(.82 + .1 * Math.pow(1 - k, 1.6) + .015 * Math.sin(k * 9), .45 + k * 1.15)); } prof.push(new THREE.Vector2(.55, 1.68));
  mesh(new THREE.LatheGeometry(prof, 48), coatM, 0, 0, 0, R.coat, { s: [1, 1, .9] });
  mesh(new THREE.TorusGeometry(.5, .1, 12, 32), coatM, 0, 1.67, 0, R.coat, { r: [Math.PI / 2, 0, 0], s: [1.05, .9, 1] });
  mesh(SPH(.78, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2), coatM, 0, 1.62, -.45, R.coat, { s: [1, .75, .8], r: [-1.2, 0, 0] });
  for (let i = 0; i < 3; i++) mesh(SPH(.075, 16, 12), mat('#ffffff', { kind: 'gloss' }), 0, 1.45 - i * .3, .82 - i * .03, R.coat, { s: [1, 1, .6] });
  for (const sd of [-1, 1]) { mesh(new THREE.BoxGeometry(.38, .26, .06), coatM, sd * .5, .78, .86, R.coat, { r: [0, sd * .35, 0] }); mesh(new THREE.BoxGeometry(.4, .09, .08), mat('#f2b800', { kind: 'gloss' }), sd * .5, .9, .88, R.coat, { r: [0, sd * .35, 0] }); }
  // arms (pivot at shoulder) with sleeves
  R.arms = []; R.sleeves = [];
  for (const sd of [-1, 1]) { const a = group(body, sd * .78, 1.55, 0); mesh(CAP(.17, .55, 10), fur, 0, -.4, 0, a); mesh(SPH(.2), cream, 0, -.78, .02, a, { s: [1, .9, 1] });
    const sl = mesh(CAP(.21, .42, 10), coatM, 0, -.33, 0, a); R.sleeves.push(sl); R.arms.push(a); }
  // head
  R.head = group(body, 0, 2.3, .05); const hd = R.head;
  mesh(SPH(.78), fur, 0, 0, 0, hd, { s: [1.08, .95, .95] });
  for (const sd of [-1, 1]) { mesh(SPH(.36), cream, sd * .24, -.22, .55, hd, { s: [1, .82, .8] }); const ear = mesh(SPH(.18), fur, sd * .62, .48, -.05, hd, { s: [1, 1, .6] }); mesh(SPH(.1), mat('#ff9db4'), sd * .62, .49, .03, hd, { s: [1, 1, .4] });
    mesh(new THREE.CircleGeometry(.13, 24), mat('#ff8fa8', { kind: 'basic', transparent: true, opacity: .55 }), sd * .5, -.17, .62, hd, { r: [0, sd * .55, 0], cast: false });
    for (let k = 0; k < 3; k++) tube([[sd * .38, -.16 + k * .06, .7], [sd * .62, -.12 + k * .1, .72], [sd * .85, -.06 + k * .15, .66]], .008, hd, mat('#3b2414')); }
  mesh(SPH(.15), mat('#2a1a1e', { kind: 'gloss' }), 0, -.08, .83, hd, { s: [1.25, .85, .8] }); mesh(SPH(.04), mat('#ffffff', { kind: 'basic' }), -.05, -.03, .93, hd, { cast: false });
  R.eyes = eyes(hd, { sep: .27, y: .14, z: .58, r: .17, lid: F }); R.eyeR = .17;
  R.mouth = mouth(hd, { y: -.36, z: .68, w: .16 });
  R.wet = 0; return R;
}
export function frog(o = {}) {
  const G = o.color || '#5fc96b', root = group(null), body = group(root), R = { root, body }, gm = mat(G, { rough: .45 }), belly = mat('#d8f5b0', { rough: .5 });
  mesh(SPH(.62), gm, 0, .62, 0, body, { s: [1.15, .95, 1] }); mesh(SPH(.48), belly, 0, .56, .28, body, { s: [1.05, .9, .7] });
  R.legs = []; for (const sd of [-1, 1]) { const l = group(body, sd * .55, .25, -.05); mesh(SPH(.3), gm, 0, .05, 0, l, { s: [1, .7, 1.3] }); mesh(SPH(.2), gm, sd * .05, -.15, .32, l, { s: [1.3, .35, 1.2] }); R.legs.push(l); }
  R.arms = []; for (const sd of [-1, 1]) { const a = group(body, sd * .5, .7, .25); mesh(CAP(.1, .3, 8), gm, 0, -.2, .05, a); mesh(SPH(.13), gm, 0, -.4, .1, a, { s: [1.3, .4, 1.2] }); R.arms.push(a); }
  R.head = group(body, 0, 1.0, .05);
  mesh(SPH(.55), gm, 0, 0, 0, R.head, { s: [1.25, .78, 1] });
  for (const sd of [-1, 1]) { mesh(SPH(.25), gm, sd * .32, .32, .1, R.head); mesh(new THREE.CircleGeometry(.1, 24), mat('#ff8fa8', { kind: 'basic', transparent: true, opacity: .55 }), sd * .45, -.08, .5, R.head, { r: [0, sd * .5, 0], cast: false }); }
  R.eyes = eyes(R.head, { sep: .32, y: .36, z: .2, r: .17, lid: G, iris: '#2b5d2e', brow: '#2e6b33' }); R.eyeR = .17;
  R.mouth = mouth(R.head, { y: -.12, z: .52, w: .3, th: .03 });
  R.hat = group(R.head, 0, .5, -.05); mesh(new THREE.ConeGeometry(.3, .32, 24), mat('#4dabf7', { kind: 'gloss' }), 0, .12, 0, R.hat); mesh(new THREE.CylinderGeometry(.42, .42, .04, 32), mat('#4dabf7', { kind: 'gloss' }), 0, -.02, 0, R.hat); R.hat.rotation.z = .25;
  return R;
}
export function duck(o = {}) {
  const Y = '#ffd84a', root = group(null), body = group(root), R = { root, body }, ym = mat(Y, { kind: 'fur' }), om = mat('#ff9a2e', { kind: 'gloss' });
  mesh(SPH(.6), ym, 0, .75, 0, body, { s: [1, .95, 1.2] }); mesh(CAP(.12, .2, 6), ym, 0, .9, -.75, body, { r: [-.9, 0, 0] });
  R.wings = []; for (const sd of [-1, 1]) { const w = group(body, sd * .55, .9, 0); mesh(SPH(.32), ym, 0, -.1, -.05, w, { s: [.35, .8, 1.1] }); R.wings.push(w); }
  R.legs = []; for (const sd of [-1, 1]) { const l = group(body, sd * .25, .22, .05); mesh(CAP(.05, .18, 6), om, 0, 0, 0, l); mesh(SPH(.16), om, 0, -.15, .12, l, { s: [1, .25, 1.4] }); R.legs.push(l); }
  R.head = group(body, 0, 1.55, .2); mesh(SPH(.45), ym, 0, 0, 0, R.head, { s: [1, 1, .95] });
  mesh(SPH(.08, 12, 8), ym, 0, .45, 0, R.head, { s: [1, 2, 1] });
  R.beakTop = mesh(SPH(.2), om, 0, -.08, .4, R.head, { s: [1.2, .45, 1.1] }); R.beakBot = mesh(SPH(.17), om, 0, -.16, .38, R.head, { s: [1.1, .35, 1] });
  for (const sd of [-1, 1]) mesh(new THREE.CircleGeometry(.08, 24), mat('#ff8fa8', { kind: 'basic', transparent: true, opacity: .6 }), sd * .28, -.08, .35, R.head, { r: [0, sd * .6, 0], cast: false });
  R.eyes = eyes(R.head, { sep: .18, y: .1, z: .35, r: .12, lid: Y, iris: '#3a2410', brow: '#c98a00' }); R.eyeR = .12;
  // pink polka-dot umbrella
  R.umb = group(body, -.55, 1.0, .1); mesh(new THREE.CylinderGeometry(.025, .025, 1.6, 8), mat('#8a5a33'), 0, .8, 0, R.umb);
  const tex = canvasTex(512, 256, (c, w, h) => { c.fillStyle = '#ff7eb6'; c.fillRect(0, 0, w, h); c.fillStyle = '#ffffff'; const r = rng(3); for (let i = 0; i < 40; i++) { c.beginPath(); c.arc(r() * w, r() * h, 12, 0, 7); c.fill(); } });
  mesh(new THREE.ConeGeometry(.75, .42, 8, 1, true), new THREE.MeshStandardMaterial({ map: tex, side: THREE.DoubleSide, roughness: .5 }), 0, 1.65, 0, R.umb);
  mesh(SPH(.05), mat('#8a5a33'), 0, 1.88, 0, R.umb); R.umb.rotation.z = .3;
  return R;
}
// generic pose driver. s: {t, talk 0..1, blink, jump: {u (0..1 air), crouch, land}, wave, arms, look, brow, wide, spin, walk}
export function pose(R, s) {
  const t = s.t, br = Math.sin(t * 2.2 + (s.ph || 0));
  R.body.position.y = (s.hop || 0); R.body.scale.set(1 + (s.squash || 0) * .5, 1 - (s.squash || 0), 1 + (s.squash || 0) * .5);
  R.body.rotation.y = s.spin || 0; R.body.rotation.z = (s.lean || 0) + (s.shake ? Math.sin(t * 40) * .18 * s.shake : 0);
  if (R.head) { R.head.rotation.z = Math.sin(t * 1.3 + (s.ph || 0)) * .05 + (s.tilt || 0) + (s.shake ? Math.sin(t * 40 + 1) * .25 * s.shake : 0); R.head.rotation.x = br * .02 + (s.nod || 0); R.head.rotation.y = s.headYaw || 0; }
  if (R.eyes) faceEyes(R.eyes, { blink: s.blink ?? blinkAt(t, s.ph || 0), look: s.look || [0, 0], brow: s.brow || 0, wide: s.wide || 1, r: R.eyeR });
  if (R.mouth) faceMouth(R.mouth, s.talk || 0, 1);
  if (R.beakBot) { R.beakBot.position.y = -.16 - (s.talk || 0) * .12; R.beakBot.rotation.x = (s.talk || 0) * .4; }
  const sw = s.walk ? Math.sin(t * 12) : 0;
  if (R.arms) R.arms.forEach((a, i) => { const sd = i ? 1 : -1; let z = sd * (.25 + br * .03), x = 0;
    if (s.arms === 'up') z = sd * 2.6; if (s.arms === 'cheer') z = sd * (2.3 + Math.sin(t * 9 + i) * .25); if (s.arms === 'clap') { z = sd * .9; x = -1.2 + Math.abs(Math.sin(t * 8)) * .3 * (1 - i * 2) * 0; }
    if (s.wave && i === 1) { z = 2.4 + Math.sin(t * 10) * .35; } if (s.walk) x = sd * sw * .5;
    a.rotation.set(x, 0, z); });
  if (R.wings) R.wings.forEach((w, i) => { const sd = i ? 1 : -1; w.rotation.z = sd * ((s.flap ? (.6 + Math.sin(t * 22) * .5) : .1) + (s.arms === 'up' || s.arms === 'cheer' ? 1.2 : 0)); });
  if (R.legs) R.legs.forEach((l, i) => { const sd = i ? 1 : -1; l.rotation.x = s.walk ? sd * sw * .6 : (s.tuck ? -.5 : 0); });
  if (R.tail) R.tail.rotation.y = Math.sin(t * 3) * .3;
}
export function blinkAt(t, ph = 0) { const c = (t + ph * 1.7) % 3.4; return c < .12 ? Math.sin(c / .12 * Math.PI) : 0; }

// ------------------------------------------------------------------ world props
export function tree(parent, x, z, s = 1, fruit = true) {
  const g = group(parent, x, 0, z); g.scale.setScalar(s); const r = rng(Math.floor(x * 7 + z * 13 + 99));
  mesh(new THREE.CylinderGeometry(.35, .55, 3.2, 12), mat('#8a5a33', { rough: .9 }), 0, 1.6, 0, g);
  for (let i = 0; i < 6; i++) { const a = i / 6 * Math.PI * 2; mesh(SPH(1.3 + r() * .5, 20, 14), mat(['#4caf50', '#5cbf55', '#43a047'][i % 3], { rough: .8 }), Math.cos(a) * 1.1, 3.8 + r() * .9, Math.sin(a) * 1.1, g); }
  mesh(SPH(1.6, 20, 14), mat('#58b84f', { rough: .8 }), 0, 4.9, 0, g);
  if (fruit) for (let i = 0; i < 7; i++) { const a = r() * 6.28, rr = 1.9 + r() * .3; mesh(SPH(.2, 12, 8), mat('#ff4a4a', { kind: 'gloss' }), Math.cos(a) * rr, 3.4 + r() * 1.8, Math.sin(a) * rr, g); }
  return g;
}
export function bush(parent, x, z, s = 1, col = '#4caf50', flowers = '#ff8ab8') { const g = group(parent, x, 0, z); g.scale.setScalar(s); const r = rng(Math.floor(x * 11 + z * 5 + 7));
  for (let i = 0; i < 5; i++) mesh(SPH(.7 + r() * .3, 16, 12), mat(col, { rough: .85 }), (r() - .5) * 1.4, .55 + r() * .3, (r() - .5) * .8, g);
  for (let i = 0; i < 6; i++) mesh(SPH(.12, 10, 8), mat(flowers), (r() - .5) * 1.5, .8 + r() * .5, .45 + r() * .2, g, { cast: false }); return g; }
export function flowers(parent, n, area, seed = 5) { // instanced stems + petals + centers
  const r = rng(seed), stem = new THREE.InstancedMesh(new THREE.CylinderGeometry(.025, .03, .5, 5), mat('#3e8e3a'), n), pet = new THREE.InstancedMesh(SPH(.09, 10, 8), mat('#ffffff'), n * 5), cen = new THREE.InstancedMesh(SPH(.07, 10, 8), mat('#ffd43b'), n);
  const cols = ['#ff8ab8', '#ffffff', '#ffb02e', '#da77f2', '#ff5a5a', '#74c0fc'].map(c => new THREE.Color(c)); const m = new THREE.Matrix4(), q = new THREE.Quaternion(), sc = new THREE.Vector3();
  const pos = [];
  for (let i = 0; i < n; i++) { let x, z; do { x = area[0] + r() * (area[1] - area[0]); z = area[2] + r() * (area[3] - area[2]); } while (area[4] && area[4](x, z)); const h = .35 + r() * .25; pos.push([x, z]);
    m.compose(new THREE.Vector3(x, h / 2, z), q, sc.set(1, h / .5, 1)); stem.setMatrixAt(i, m); m.compose(new THREE.Vector3(x, h, z + .03), q, sc.set(1, 1, .6)); cen.setMatrixAt(i, m); const c = cols[Math.floor(r() * cols.length)];
    for (let k = 0; k < 5; k++) { const a = k / 5 * Math.PI * 2; m.compose(new THREE.Vector3(x + Math.cos(a) * .11, h + Math.sin(a) * .11, z), q, sc.set(1, 1, .45)); pet.setMatrixAt(i * 5 + k, m); pet.setColorAt(i * 5 + k, c); } }
  for (const im of [stem, pet, cen]) { im.castShadow = true; im.receiveShadow = true; parent.add(im); } return pos;
}
export function grass(parent, n, area, seed = 9) {
  const r = rng(seed), g = new THREE.ConeGeometry(.035, .32, 4); g.translate(0, .16, 0); const im = new THREE.InstancedMesh(g, mat('#5aa83f', { rough: .9 }), n), m = new THREE.Matrix4(), q = new THREE.Quaternion(), e = new THREE.Euler();
  const cols = ['#5aa83f', '#6bbd4c', '#4e9a37', '#7cc95a'].map(c => new THREE.Color(c));
  for (let i = 0; i < n; i++) { let x, z; do { x = area[0] + r() * (area[1] - area[0]); z = area[2] + r() * (area[3] - area[2]); } while (area[4] && area[4](x, z)); e.set((r() - .5) * .5, r() * 6, (r() - .5) * .5); q.setFromEuler(e);
    m.compose(new THREE.Vector3(x, 0, z), q, new THREE.Vector3(1, .7 + r() * .8, 1)); im.setMatrixAt(i, m); im.setColorAt(i, cols[i % 4]); }
  im.receiveShadow = true; parent.add(im); return im;
}
export function cloud(parent, x, y, z, s = 1) { const g = group(parent, x, y, z); g.scale.setScalar(s); const m = mat('#ffffff', { rough: 1 });
  for (const [dx, dy, r] of [[0, 0, 2.2], [2.2, -.3, 1.7], [-2.2, -.4, 1.6], [1, .9, 1.6], [-1, .8, 1.4], [3.6, -.6, 1.1], [-3.5, -.7, 1.0]]) mesh(SPH(r, 20, 14), m, dx, dy, 0, g, { cast: false, recv: false }); g.userData.m = m; return g; }
export function fence(parent, x0, x1, z) { const g = group(parent); const wm = mat('#fff8ef', { rough: .7 });
  for (let x = x0; x <= x1; x += 1.1) { mesh(new THREE.BoxGeometry(.22, 1.4, .12), wm, x, .7, z, g); mesh(new THREE.ConeGeometry(.16, .25, 4), wm, x, 1.52, z, g, { r: [0, Math.PI / 4, 0] }); }
  for (const y of [.45, 1.0]) mesh(new THREE.BoxGeometry(x1 - x0, .12, .08), wm, (x0 + x1) / 2, y, z - .1, g); return g; }
export function house(parent, x, z) {
  const g = group(parent, x, 0, z), wall = mat('#ffe6c4', { rough: .8 }), trim = mat('#ffffff', { rough: .6 });
  mesh(new THREE.BoxGeometry(6, 4, 4.5), wall, 0, 2, 0, g); mesh(new THREE.BoxGeometry(6.2, .3, 4.7), trim, 0, .15, 0, g);
  const roof = new THREE.Shape(); roof.moveTo(-3.6, 0); roof.lineTo(0, 2.6); roof.lineTo(3.6, 0); roof.lineTo(-3.6, 0);
  const rg = new THREE.ExtrudeGeometry(roof, { depth: 5.2, bevelEnabled: true, bevelThickness: .12, bevelSize: .12, bevelSegments: 3 }); mesh(rg, mat('#ff6b6b', { rough: .55 }), 0, 4, -2.6, g);
  mesh(new THREE.BoxGeometry(.8, 1.8, .8), mat('#c0574e'), 1.8, 5.6, -.5, g); mesh(new THREE.BoxGeometry(1, .25, 1), trim, 1.8, 6.55, -.5, g);
  // door (pivot on the left edge)
  const dp = group(g, -.65, 0, 2.27); const door = mesh(new THREE.BoxGeometry(1.3, 2.4, .12), mat('#4dabf7', { kind: 'gloss' }), .65, 1.2, 0, dp); mesh(SPH(.08), mat('#ffd43b', { kind: 'gloss' }), 1.1, 1.2, .1, dp);
  mesh(new THREE.CircleGeometry(.25, 24), mat('#fff3b0', { emissive: '#ffd77a', ei: .6 }), .65, 2.05, .07, dp);
  mesh(new THREE.BoxGeometry(1.7, .15, .3), trim, 0, 2.55, 2.32, g); mesh(new THREE.BoxGeometry(1.8, .12, 1.0), mat('#c99a6b'), 0, .06, 2.8, g);
  // glowing windows with flower boxes
  const wins = [];
  for (const sd of [-1, 1]) { const wg = group(g, sd * 1.9, 2.3, 2.27); mesh(new THREE.PlaneGeometry(1.2, 1.1), mat('#fff1c2', { emissive: '#ffc96b', ei: .55 }), 0, 0, .02, wg, { cast: false });
    for (const [w, h, xx, yy] of [[1.35, .1, 0, .58], [1.35, .1, 0, -.58], [.1, 1.25, .62, 0], [.1, 1.25, -.62, 0], [1.2, .06, 0, 0], [.06, 1.1, 0, 0]]) mesh(new THREE.BoxGeometry(w, h, .1), trim, xx, yy, .05, wg);
    mesh(new THREE.BoxGeometry(1.45, .3, .35), mat('#8a5a33'), 0, -.78, .15, wg); for (let k = 0; k < 5; k++) mesh(SPH(.12, 10, 8), mat(['#ff8ab8', '#ffd43b', '#da77f2'][k % 3]), -.5 + k * .25, -.55, .2, wg); wins.push(wg); }
  return { g, door: dp, wins };
}
export function signpost(parent, x, z, num, col) {
  const g = group(parent, x, 0, z); mesh(new THREE.CylinderGeometry(.07, .09, 1.6, 8), mat('#8a5a33'), 0, .8, 0, g);
  const tex = canvasTex(256, 256, (c, w, h) => { c.fillStyle = col; c.beginPath(); c.arc(128, 128, 120, 0, 7); c.fill(); c.lineWidth = 14; c.strokeStyle = '#ffffff'; c.stroke(); c.font = `700 150px Fredoka`; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillStyle = '#ffffff'; c.strokeStyle = 'rgba(0,0,0,.25)'; c.lineWidth = 10; c.strokeText(num, 128, 138); c.fillText(num, 128, 138); });
  const plate = mesh(new THREE.CylinderGeometry(.48, .48, .08, 32), mat('#ffffff'), 0, 1.75, 0, g, { r: [Math.PI / 2, 0, 0] });
  mesh(new THREE.CircleGeometry(.46, 32), new THREE.MeshStandardMaterial({ map: tex, roughness: .6 }), 0, 1.75, .045, g, { cast: false }); return g;
}
export function puddleGeo(r, seed) { const s = new THREE.Shape(), rr = rng(seed); const k = [rr(), rr(), rr()];
  for (let i = 0; i <= 64; i++) { const a = i / 64 * Math.PI * 2, rad = r * (1 + .08 * Math.sin(a * 3 + k[0] * 6) + .05 * Math.sin(a * 5 + k[1] * 6) + .04 * Math.sin(a * 2 + k[2] * 6)); const x = Math.cos(a) * rad, y = Math.sin(a) * rad * .72; i ? s.lineTo(x, y) : s.moveTo(x, y); }
  const g = new THREE.ShapeGeometry(s, 64); g.rotateX(-Math.PI / 2); return g; }
export function starTex() { return canvasTex(128, 128, (c) => { const g = c.createRadialGradient(64, 64, 0, 64, 64, 64); g.addColorStop(0, 'rgba(255,255,255,1)'); g.addColorStop(.25, 'rgba(255,250,200,.9)'); g.addColorStop(1, 'rgba(255,250,200,0)'); c.fillStyle = g; c.fillRect(0, 0, 128, 128); c.fillStyle = '#fff';
  c.beginPath(); for (let i = 0; i < 8; i++) { const a = i / 8 * Math.PI * 2, r = i % 2 ? 14 : 62; c.lineTo(64 + Math.cos(a) * r, 64 + Math.sin(a) * r); } c.closePath(); c.fill(); }); }

// ------------------------------------------------------------------ timeline helpers
export function wordT(L, key) { if (typeof key === 'number') return L.start + key * (L.end - L.start); const k = key.toLowerCase(); const w = L.words.find(w => w.w.toLowerCase().replace(/[^a-z0-9]/g, '').startsWith(k)); return w ? w.s : L.start; }
export function sfxT(L, name, n = 0) { const s = (L.sfx_times || []).filter(s => s[0] === name); return s[n] ? s[n][1] : null; }
export function envAt(TL, sp, t) { const e = TL.env[sp]; if (!e) return 0; const f = t * 60, i = Math.floor(f); return clamp(((e[i] || 0) * (1 - (f - i)) + (e[i + 1] || 0) * (f - i)) / 100 * 1.6); }

// ------------------------------------------------------------------ 2D overlay (captions, badges, titles) drawn on the output canvas
export function txt(c, s, x, y, size, fill, o = {}) { c.save(); c.font = `${o.weight || 700} ${size}px Fredoka`; c.textAlign = o.align || 'center'; c.textBaseline = 'middle';
  if (o.maxW) { const w = c.measureText(s).width; if (w > o.maxW) { c.translate(x, y); c.scale(o.maxW / w, o.maxW / w); x = 0; y = 0; } }
  if (o.stroke) { c.lineJoin = 'round'; c.lineWidth = o.stroke; c.strokeStyle = o.sc || '#2b1d4a'; c.strokeText(s, x, y); } c.fillStyle = fill; c.fillText(s, x, y); c.restore(); }
export function captions(c, TL, t, colors) {
  const L = TL.lines.find(l => t >= l.start - .05 && t <= l.end + .25); if (!L || L.nocap) return;
  const ws = L.words; let ci = ws.findIndex((w, i) => t >= w.s && (i === ws.length - 1 || t < ws[i + 1].s)); if (ci < 0) ci = 0;
  const per = 4, c0 = Math.floor(ci / per) * per, ch = ws.slice(c0, c0 + per); c.save(); c.font = '700 84px Fredoka';
  const ps = ch.map(w => w.w.replace(/[.,!?]+$/, '').toUpperCase() + (/[!?]$/.test(w.w) ? w.w.slice(-1) : '')), sp = 24, wd = ps.map(p => c.measureText(p).width), tot = wd.reduce((a, b) => a + b, 0) + sp * (ps.length - 1), f = Math.min(1, 860 / tot);
  let x = W / 2 - tot * f / 2; const y = 1440;
  ps.forEach((p, q) => { const act = c0 + q === ci, k = act ? eBack(clamp((t - ws[c0 + q].s) / .14)) : 1, col = act ? colors[(c0 + q) % colors.length] : '#ffffff';
    c.save(); c.translate(x + wd[q] * f / 2, y - (act ? 10 * k : 0)); c.scale(f * (act ? lerp(.85, 1.12, k) : 1), f * (act ? lerp(.85, 1.12, k) : 1)); txt(c, p, 0, 6, 84, 'rgba(0,0,0,.25)', { stroke: 18, sc: 'rgba(0,0,0,.25)' }); txt(c, p, 0, 0, 84, col, { stroke: 16 }); c.restore(); x += (wd[q] + sp) * f; });
  c.restore();
}
export function vignette(c, a = .28) { const g = c.createRadialGradient(W / 2, H / 2, 500, W / 2, H / 2, 1250); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, `rgba(20,10,40,${a})`); c.fillStyle = g; c.fillRect(0, 0, W, H); }

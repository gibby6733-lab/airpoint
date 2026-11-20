// WonderBuds — the five permanent 3D characters. Build once, reuse in every episode (never redesign).
// Every builder returns a rig: {root, body, head, arms[], legs[], eyes, eyeR, mouth, ...extras}. Animate with act(rig, state).
import { THREE, mat, mesh, group, SPH, CAP, tube, eyes, mouth, pose, blinkAt, canvasTex, clamp, lerp } from '../lib.js';

const pinkBlush = () => mat('#ff8fa8', { kind: 'basic', transparent: true, opacity: .5 });
function blush(head, x, y, z, r, yaw) { for (const sd of [-1, 1]) mesh(new THREE.CircleGeometry(r, 24), pinkBlush(), sd * x, y, z, head, { r: [0, sd * yaw, 0], cast: false }); }
function sneaker(parent, col, sole = '#ffffff') { const b = group(parent); mesh(SPH(.26), mat(col, { kind: 'gloss' }), 0, 0, .08, b, { s: [1, .7, 1.35] }); mesh(new THREE.CylinderGeometry(.27, .29, .08, 24), mat(sole), 0, -.15, .08, b, { s: [1, 1, 1.4] }); mesh(SPH(.08), mat(sole), 0, .1, .3, b); return b; }

// ------------------------------------------------------------------ ROSIE — red panda, the leader
export function rosie() {
  const F = '#c8562a', D = '#5a2a1e', Wm = '#fff3e0', root = group(null), body = group(root), R = { root, body, id: 'rosie' };
  const fur = mat(F, { kind: 'fur' }), dark = mat(D, { kind: 'fur' }), white = mat(Wm, { kind: 'fur' }), scarf = mat('#20b2aa', { rough: .6 }), pack = mat('#ffc93c', { kind: 'gloss' });
  mesh(SPH(.72), fur, 0, 1.2, 0, body, { s: [1, 1.1, .9] }); mesh(SPH(.55), dark, 0, 1.08, .3, body, { s: [1, 1.1, .7] });
  R.legs = []; for (const sd of [-1, 1]) { const l = group(body, sd * .34, .55, 0); mesh(CAP(.19, .32, 10), dark, 0, -.22, 0, l); mesh(SPH(.22), dark, 0, -.46, .1, l, { s: [1, .6, 1.3] }); R.legs.push(l); }
  R.arms = []; for (const sd of [-1, 1]) { const a = group(body, sd * .66, 1.55, 0); mesh(CAP(.15, .55, 10), dark, 0, -.38, 0, a); mesh(SPH(.18), dark, 0, -.74, .02, a); R.arms.push(a); }
  // ringed bushy tail
  R.tail = group(body, 0, .75, -.55); for (let i = 0; i < 7; i++) { const k = i / 6; mesh(SPH(.3 - k * .04, 20, 14), mat(i % 2 ? '#7a3418' : F, { kind: 'fur' }), 0, .1 + k * 1.1 + Math.sin(k * 3) * .1, -.25 - Math.sin(k * 2.2) * .55, R.tail, { s: [1, .9, 1] }); }
  // scarf + backpack
  mesh(new THREE.TorusGeometry(.48, .14, 14, 32), scarf, 0, 1.78, .02, body, { r: [Math.PI / 2, 0, 0], s: [1, .9, 1] }); R.scarfTail = group(body, .25, 1.72, .38); mesh(CAP(.11, .45, 8), scarf, 0, -.3, 0, R.scarfTail, { s: [1.4, 1, .6] });
  const bp = group(body, 0, 1.3, -.75); mesh(new THREE.BoxGeometry(.85, .9, .38), pack, 0, 0, 0, bp); mesh(new THREE.BoxGeometry(.88, .3, .42), mat('#f2a900', { kind: 'gloss' }), 0, .32, .02, bp); mesh(new THREE.BoxGeometry(.45, .3, .1), mat('#f2a900', { kind: 'gloss' }), 0, -.15, -.22, bp);
  for (const sd of [-1, 1]) tube([[sd * .35, 1.75, -.45], [sd * .55, 1.5, .1], [sd * .45, .95, .45]], .045, body, mat('#8a5a33'));
  // head
  R.head = group(body, 0, 2.35, .05); const h = R.head;
  mesh(SPH(.8), fur, 0, 0, 0, h, { s: [1.12, .95, .95] });
  for (const sd of [-1, 1]) { mesh(SPH(.3), white, sd * .4, -.2, .52, h, { s: [1.1, .8, .7] }); mesh(SPH(.11), white, sd * .3, .42, .66, h, { s: [1.3, .6, .5] });
    const ear = group(h, sd * .6, .6, -.05); ear.rotation.z = sd * -.35; mesh(SPH(.3, 20, 12), white, 0, 0, 0, ear, { s: [1, 1.1, .45] }); mesh(SPH(.24, 20, 12), fur, 0, -.02, .05, ear, { s: [1, 1.05, .45] }); mesh(SPH(.16), dark, 0, -.05, .1, ear, { s: [1, 1, .3] }); }
  mesh(SPH(.32), white, 0, -.28, .62, h, { s: [1.2, .75, .75] }); mesh(SPH(.12), mat('#1e1416', { kind: 'gloss' }), 0, -.16, .87, h, { s: [1.3, .85, .8] });
  R.eyes = eyes(h, { sep: .3, y: .08, z: .6, r: .2, iris: '#4a2b16', brow: D }); R.eyeR = .2; R.mouth = mouth(h, { y: -.42, z: .76, w: .14 }); blush(h, .52, -.18, .64, .12, .55);
  return R;
}
// ------------------------------------------------------------------ PUDDING — hippo, the funny one
export function pudding() {
  const P = '#b9a3e3', root = group(null), body = group(root), R = { root, body, id: 'pudding' }, fur = mat(P, { rough: .55 }), belly = mat('#e3d7f7', { rough: .6 }), snout = mat('#d4c2f2', { rough: .55 });
  mesh(SPH(.95), fur, 0, 1.05, 0, body, { s: [1.05, 1, .95] }); mesh(SPH(.75), belly, 0, .98, .32, body, { s: [1, 1, .75] });
  R.legs = []; for (const sd of [-1, 1]) { const l = group(body, sd * .45, .35, .05); mesh(new THREE.CylinderGeometry(.24, .26, .4, 20), fur, 0, -.12, 0, l); mesh(SPH(.26), fur, 0, -.3, .04, l, { s: [1, .45, 1.1] }); for (let k = -1; k <= 1; k++) mesh(SPH(.05), mat('#f4ecff'), k * .1, -.3, .27, l, { cast: false }); R.legs.push(l); }
  R.arms = []; for (const sd of [-1, 1]) { const a = group(body, sd * .9, 1.35, 0); mesh(CAP(.17, .4, 10), fur, 0, -.3, 0, a); mesh(SPH(.2), fur, 0, -.58, .02, a); R.arms.push(a); }
  R.tail = group(body, 0, .7, -.85); mesh(CAP(.06, .15, 6), fur, 0, 0, 0, R.tail, { r: [-.8, 0, 0] }); mesh(SPH(.09), fur, 0, .05, -.12, R.tail, { s: [1.2, 1, .5] });
  R.head = group(body, 0, 2.1, .1); const h = R.head;
  mesh(SPH(.7), fur, 0, .1, -.05, h, { s: [1.1, .95, .95] }); mesh(SPH(.55), snout, 0, -.22, .45, h, { s: [1.25, .78, .85] });
  for (const sd of [-1, 1]) { mesh(SPH(.07), mat('#7a5aa8'), sd * .2, -.05, .9, h, { s: [1, .7, .5], cast: false }); const ear = mesh(SPH(.14), fur, sd * .5, .62, -.05, h, { s: [1, .8, .7] }); mesh(SPH(.08), mat('#ff9db4'), sd * .5, .63, .03, h, { s: [1, .8, .4] });
    mesh(new THREE.BoxGeometry(.11, .12, .05), mat('#ffffff', { kind: 'gloss' }), sd * .1, -.43, .9, h, { r: [-.2, 0, 0] }); }
  R.eyes = eyes(h, { sep: .28, y: .3, z: .5, r: .16, iris: '#5b3a8c', brow: '#6a4c9c' }); R.eyeR = .16; R.mouth = mouth(h, { y: -.37, z: .9, w: .3, th: .04 }); blush(h, .58, -.12, .55, .13, .7);
  // rainbow propeller beanie
  R.hat = group(h, 0, .68, -.02); const segCols = ['#ff6b6b', '#ffd43b', '#4dabf7', '#69db7c'];
  segCols.forEach((c, i) => mesh(SPH(.5, 24, 12, i * Math.PI / 2, Math.PI / 2, 0, Math.PI / 2), mat(c, { kind: 'gloss' }), 0, 0, 0, R.hat, { s: [1.05, .7, 1.05] }));
  mesh(new THREE.TorusGeometry(.5, .05, 8, 32), mat('#ffffff', { kind: 'gloss' }), 0, .01, 0, R.hat, { r: [Math.PI / 2, 0, 0], s: [1.05, 1.05, 1] }); mesh(new THREE.CylinderGeometry(.03, .03, .2, 8), mat('#555'), 0, .42, 0, R.hat);
  R.prop = group(R.hat, 0, .53, 0); for (let i = 0; i < 2; i++) mesh(SPH(.22, 16, 8), mat(i ? '#ff6b6b' : '#4dabf7', { kind: 'gloss' }), 0, 0, 0, R.prop, { s: [1.2, .06, .3], r: [0, i * Math.PI, 0] }).position.x = (i ? -1 : 1) * .24; mesh(SPH(.05), mat('#ffd43b'), 0, .02, 0, R.prop);
  return R;
}
// ------------------------------------------------------------------ OLLIE — owl, the smart one
export function ollie() {
  const B = '#5aa9e6', root = group(null), body = group(root), R = { root, body, id: 'ollie' }, feath = mat(B, { kind: 'fur' }), face = mat('#d6ecfb', { kind: 'fur' }), cream = mat('#f4ead2', { kind: 'fur' }), orange = mat('#ffa94d', { kind: 'gloss' });
  mesh(SPH(.82), feath, 0, 1.05, 0, body, { s: [1, 1.12, .92] }); mesh(SPH(.6), cream, 0, .98, .34, body, { s: [1, 1.15, .7] });
  for (let r = 0; r < 3; r++) for (let c = -1; c <= 1; c++) tube([[c * .2 - .07, 1.25 - r * .22, .78], [c * .2, 1.2 - r * .22, .8], [c * .2 + .07, 1.25 - r * .22, .78]], .015, body, mat('#c9b48a'));
  R.legs = []; for (const sd of [-1, 1]) { const l = group(body, sd * .3, .25, .15); for (let k = -1; k <= 1; k++) mesh(CAP(.045, .14, 6), orange, k * .08, -.15, .1, l, { r: [1.3, k * .3, 0] }); R.legs.push(l); }
  R.arms = []; for (const sd of [-1, 1]) { const a = group(body, sd * .78, 1.5, -.05); mesh(SPH(.38), feath, 0, -.35, 0, a, { s: [.38, 1, .75] }); for (let k = 0; k < 3; k++) mesh(SPH(.12), mat('#3f86c2', { kind: 'fur' }), 0, -.66 - k * .02, .1 - k * .12, a, { s: [.4, 1, .5] }); R.arms.push(a); }
  R.head = group(body, 0, 2.1, .05); const h = R.head;
  mesh(SPH(.78), feath, 0, 0, 0, h, { s: [1.12, .95, .95] });
  for (const sd of [-1, 1]) { mesh(SPH(.36), face, sd * .27, .02, .5, h, { s: [1, 1, .55] }); const tuft = group(h, sd * .55, .6, 0); tuft.rotation.z = sd * -.5; mesh(new THREE.ConeGeometry(.16, .42, 16), feath, 0, .15, 0, tuft); }
  mesh(new THREE.ConeGeometry(.1, .26, 16), orange, 0, -.17, .82, h, { r: [Math.PI / 2 + .5, 0, 0] });
  R.eyes = eyes(h, { sep: .27, y: .05, z: .7, r: .17, iris: '#2b6cb0', brow: '#2f5f8f', yaw: .22 }); R.eyeR = .17; R.mouth = mouth(h, { y: -.38, z: .74, w: .1 });
  // glasses + bowtie
  const gl = mat('#33415c', { kind: 'gloss' }); for (const sd of [-1, 1]) { mesh(new THREE.TorusGeometry(.25, .035, 10, 32), gl, sd * .28, .05, .86, h, { r: [0, sd * .2, 0] }); mesh(new THREE.CircleGeometry(.24, 32), new THREE.MeshPhysicalMaterial({ color: '#e8f6ff', transparent: true, opacity: .18, roughness: 0, clearcoat: 1 }), sd * .28, .05, .855, h, { r: [0, sd * .2, 0], cast: false }); }
  mesh(CAP(.025, .1, 4), gl, 0, .07, .9, h, { r: [0, 0, Math.PI / 2] });
  const bt = group(body, 0, 1.4, .74); bt.scale.setScalar(.9); for (const sd of [-1, 1]) mesh(new THREE.ConeGeometry(.15, .26, 4), mat('#ff6b6b', { kind: 'gloss' }), sd * .13, 0, 0, bt, { r: [0, 0, sd * -Math.PI / 2] }); mesh(SPH(.07), mat('#e03131', { kind: 'gloss' }), 0, 0, .03, bt);
  blush(h, .52, -.25, .6, .1, .6); return R;
}
// ------------------------------------------------------------------ CLOVER — bunny, the shy one
export function clover() {
  const C = '#f6e7dc', root = group(null), body = group(root), R = { root, body, id: 'clover' }, fur = mat(C, { kind: 'fur' }), pink = mat('#ffb3c7', { kind: 'fur' }), hood = mat('#8fdcc2', { rough: .75 });
  mesh(SPH(.68), fur, 0, 1.1, 0, body, { s: [1, 1.1, .9] });
  // mint hoodie (lathe) with pocket + drawstrings
  const prof = []; for (let i = 0; i <= 10; i++) { const k = i / 10; prof.push(new THREE.Vector2(.74 + .06 * Math.sin(k * Math.PI) - k * .12, .62 + k * 1.0)); } prof.push(new THREE.Vector2(.45, 1.66));
  mesh(new THREE.LatheGeometry(prof, 40), hood, 0, 0, 0, body, { s: [1, 1, .9] }); mesh(new THREE.TorusGeometry(.46, .1, 12, 28), hood, 0, 1.66, 0, body, { r: [Math.PI / 2, 0, 0] });
  mesh(new THREE.BoxGeometry(.7, .32, .08), mat('#7ccdb2', { rough: .75 }), 0, .92, .68, body, { r: [-.15, 0, 0] }); for (const sd of [-1, 1]) mesh(CAP(.02, .25, 4), mat('#ffffff'), sd * .12, 1.45, .67, body);
  mesh(SPH(.62, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2), hood, 0, 1.62, -.4, body, { s: [1, .7, .8], r: [-1.25, 0, 0] });
  R.legs = []; for (const sd of [-1, 1]) { const l = group(body, sd * .3, .55, 0); mesh(CAP(.17, .3, 10), fur, 0, -.2, 0, l); mesh(SPH(.22), fur, 0, -.42, .16, l, { s: [.9, .55, 1.6] }); R.legs.push(l); }
  R.arms = []; for (const sd of [-1, 1]) { const a = group(body, sd * .64, 1.5, 0); mesh(CAP(.16, .45, 10), hood, 0, -.32, 0, a); mesh(SPH(.16), fur, 0, -.66, .02, a); R.arms.push(a); }
  R.tail = group(body, 0, .75, -.62); for (let i = 0; i < 6; i++) { const a = i / 6 * 6.28; mesh(SPH(.16, 14, 10), fur, Math.cos(a) * .1, Math.sin(a) * .1, 0, R.tail); } mesh(SPH(.2), fur, 0, 0, -.05, R.tail);
  R.head = group(body, 0, 2.25, .05); const h = R.head;
  mesh(SPH(.74), fur, 0, 0, 0, h, { s: [1.08, .97, .95] }); for (const sd of [-1, 1]) mesh(SPH(.26), mat('#fffaf5', { kind: 'fur' }), sd * .18, -.25, .5, h, { s: [1, .8, .8] });
  mesh(SPH(.1), mat('#ff7a9a', { kind: 'gloss' }), 0, -.1, .74, h, { s: [1.3, .9, .8] }); for (const sd of [-1, 1]) mesh(new THREE.BoxGeometry(.08, .1, .04), mat('#ffffff', { kind: 'gloss' }), sd * .045, -.43, .67, h);
  R.ears = []; for (const sd of [-1, 1]) { const e = group(h, sd * .34, .55, -.1); mesh(CAP(.2, 1.0, 12), fur, 0, .62, 0, e, { s: [1, 1, .55] }); mesh(CAP(.12, .85, 10), pink, 0, .62, .08, e, { s: [1, 1, .3] }); R.ears.push(e); }
  const fl = group(R.ears[1], .12, .35, .1); for (let k = 0; k < 6; k++) { const a = k / 6 * 6.28; mesh(SPH(.07, 10, 8), mat('#ffffff'), Math.cos(a) * .09, Math.sin(a) * .09, 0, fl, { s: [1, 1, .4] }); } mesh(SPH(.06), mat('#ffd43b'), 0, 0, .02, fl);
  R.eyes = eyes(h, { sep: .27, y: .1, z: .56, r: .16, iris: '#5c8a3a', brow: '#c9a48a' }); R.eyeR = .16; R.mouth = mouth(h, { y: -.36, z: .68, w: .1 }); blush(h, .45, -.15, .6, .12, .55);
  return R;
}
// ------------------------------------------------------------------ ZIGGY — monkey, the energetic one
export function ziggy() {
  const Bn = '#8a5a3c', Pc = '#f2c9a0', root = group(null), body = group(root), R = { root, body, id: 'ziggy' }, fur = mat(Bn, { kind: 'fur' }), peach = mat(Pc, { kind: 'fur' });
  mesh(SPH(.66), fur, 0, 1.25, 0, body, { s: [1, 1.15, .9] }); mesh(SPH(.5), peach, 0, 1.2, .26, body, { s: [1, 1.2, .7] });
  R.legs = []; for (const sd of [-1, 1]) { const l = group(body, sd * .3, .7, 0); mesh(CAP(.14, .42, 10), fur, 0, -.3, 0, l); const s = sneaker(l, '#ff4a4a'); s.position.set(0, -.62, .05); R.legs.push(l); }
  R.arms = []; for (const sd of [-1, 1]) { const a = group(body, sd * .62, 1.65, 0); mesh(CAP(.13, .75, 10), fur, 0, -.48, 0, a); mesh(SPH(.18), peach, 0, -.92, .02, a); R.arms.push(a); }
  R.tail = group(body, 0, .8, -.5); const pts = []; for (let i = 0; i <= 24; i++) { const k = i / 24; pts.push([0, k * 1.5 + (k > .7 ? Math.sin((k - .7) * 14) * .3 : 0), -.2 - k * .5 - (k > .7 ? (1 - Math.cos((k - .7) * 14)) * .3 : 0)]); } tube(pts, .07, R.tail, fur);
  R.head = group(body, 0, 2.4, .05); const h = R.head;
  mesh(SPH(.72), fur, 0, 0, 0, h, { s: [1.05, .97, .95] }); mesh(SPH(.5), peach, 0, -.08, .38, h, { s: [1.25, 1, .7] }); mesh(SPH(.32), peach, 0, -.32, .55, h, { s: [1.3, .75, .8] });
  for (const sd of [-1, 1]) { mesh(SPH(.25), fur, sd * .78, .05, -.05, h, { s: [.5, 1, 1] }); mesh(SPH(.17), peach, sd * .82, .05, -.02, h, { s: [.4, 1, 1] }); }
  mesh(SPH(.06), mat('#3a2418'), -.07, -.2, .82, h, { cast: false }); mesh(SPH(.06), mat('#3a2418'), .07, -.2, .82, h, { cast: false });
  R.eyes = eyes(h, { sep: .25, y: .14, z: .58, r: .16, iris: '#5a3216', brow: '#4a2c1a' }); R.eyeR = .16; R.mouth = mouth(h, { y: -.42, z: .76, w: .2 });
  // lightning headband
  mesh(new THREE.TorusGeometry(.72, .07, 10, 40), mat('#ffd43b', { kind: 'gloss' }), 0, .3, 0, h, { r: [Math.PI / 2 - .15, 0, 0], s: [1.05, .98, 1] });
  const bolt = new THREE.Shape(); [[.08, .2], [-.08, 0], [0, 0], [-.08, -.2], [.1, .03], [.02, .03]].forEach(([x, y], i) => i ? bolt.lineTo(x, y) : bolt.moveTo(x, y)); bolt.closePath();
  mesh(new THREE.ExtrudeGeometry(bolt, { depth: .05, bevelEnabled: true, bevelThickness: .015, bevelSize: .015, bevelSegments: 2 }), mat('#ff922b', { kind: 'gloss' }), 0, .42, .72, h, { s: 1.4 });
  blush(h, .48, -.15, .6, .1, .55); return R;
}
export const BUILD = { rosie, pudding, ollie, clover, ziggy };

// ------------------------------------------------------------------ acting: expressions + character-specific secondary motion
// st: {t, talk, viseme:{open,wide}, expr: 'happy'|'laugh'|'surprised'|'nervous'|'thinking'|'sad'|'determined', arms, wave, walk, hop, squash, spin, look, ...}
export const EXPR = {
  happy: { brow: .2, smile: 1 }, laugh: { brow: .4, blink: .55, open: .55 }, surprised: { brow: 1, wide: 1.18, open: .5 }, nervous: { brow: -.9, look: [-.5, -.2], open: .1 },
  thinking: { brow: .6, look: [.6, .7] }, sad: { brow: -1, look: [0, -.5] }, determined: { brow: -.4, smile: 1 } };
export function act(R, st) {
  const ex = EXPR[st.expr || 'happy'] || EXPR.happy, t = st.t;
  const talk = st.talk || 0, open = Math.max(talk, ex.open || 0);
  pose(R, { ...st, brow: st.brow ?? ex.brow, wide: st.wide ?? ex.wide ?? 1, look: st.look || ex.look || [0, 0], talk: open, blink: ex.blink !== undefined ? Math.max(ex.blink, blinkAt(t, st.ph || 0)) : st.blink });
  if (R.mouth && st.viseme) R.mouth.open.scale.x = lerp(.8, 1.3, st.viseme.wide || 0);
  if (R.prop) R.prop.rotation.y = t * (st.excited ? 22 : 3);
  if (R.ears) { R.ears[0].rotation.z = .12 + Math.sin(t * 2 + 1) * .04 + (st.expr === 'nervous' ? .35 : 0); R.ears[1].rotation.z = -1.0 + Math.sin(t * 2.3) * .06 + (st.expr === 'surprised' ? .7 : 0); R.ears[1].rotation.x = .3; }
  if (R.tail && R.id === 'rosie') { R.tail.rotation.y = Math.sin(t * 2.4) * .35; R.tail.rotation.x = -.1 + Math.sin(t * 1.7) * .08; }
  if (R.tail && R.id === 'ziggy') R.tail.rotation.y = Math.sin(t * 3.5) * .4;
  if (R.tail && R.id === 'clover') R.tail.scale.setScalar(1 + Math.sin(t * 6) * .04);
  if (R.scarfTail) R.scarfTail.rotation.z = Math.sin(t * 3) * .15 + (st.walk ? Math.sin(t * 12) * .2 : 0);
  if (st.chinTap && R.arms) { R.arms[1].rotation.set(-1.9, 0, -.6 + Math.sin(t * 8) * .05); }
}

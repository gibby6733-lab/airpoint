"""Rebuild engine.html = tenk helpers + chef/scenes.js + tenk frame code (new HUD). usage: python3 build_engine.py [episode_dir...]"""
import sys, os
here = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(here, '../tenk/engine.html')).read().split('\n')
si = next(i for i, l in enumerate(src) if l.startswith('// ================================================================ scenes'))
hi = next(i for i, l in enumerate(src) if 'HUD, captions, frame' in l)
h, t = '\n'.join(src[:si]), '\n'.join(src[hi:])
h = h.replace('// "30 Days: $1 to $10,000" — flat 2D cartoon, 9:16. Benny turns $1 into $10K; viewers vote each day.', '// "13 Days to Thanksgiving" — flat 2D cartoon, 9:16. Marcus faked being a chef online; viewers pick what he learns each day.')
a = "  if (p.kind === 'mom') { box(-95, -470, 190, 280, '#9b6ad1', K, 60, 7);"
h = h.replace(a, "  if (p.kind === 'chef') { for (const sd of [-1, 1]) for (let q = 0; q < 3; q++) circ(sd * 30, -420 + q * 60, 9, '#c8c8d0', K, 3); ctx.strokeStyle = '#ddd'; ctx.lineWidth = 6; ctx.beginPath(); ctx.moveTo(-60, -470); ctx.lineTo(0, -400); ctx.lineTo(60, -470); ctx.stroke(); }\n  if (p.stain) { ctx.fillStyle = 'rgba(120,70,20,.45)'; for (const [sx, sy, sr] of [[-40, -300, 22], [30, -250, 14], [50, -380, 10]]) { ctx.beginPath(); ctx.arc(sx, sy, sr, 0, 7); ctx.fill(); } }\n" + a)
b = "  if (p.visor)"
h = h.replace(b, "  if (p.hat) { box(-105, hy - 150, 210, 50, '#fff', K, 10, 6); for (const [cx, cy, r] of [[-60, -200, 60], [0, -230, 70], [60, -200, 60]]) circ(cx, hy + cy, r, '#fff', K, 6); ctx.fillStyle = '#fff'; ctx.fillRect(-100, hy - 200, 200, 60); }\n" + b)
i0 = t.index('function moneyAt'); i1 = t.index('function captions')
hud = r"""function hud(t, L) { if (!['intro', 'fridge', 'chef'].includes(L.scene) && !(L.scene === 'getting' && L.text.startsWith('For'))) return;
  ctx.save(); ctx.translate(87, 266); ctx.scale(.84, .84);
  box(30, 40, 250, 110, '#e04a3a', K, 26, 7); shine(34, 44, 242, 102, 22); txt((TL.daysLeft || 13) + ' DAYS', 155, 96, 50, '#fff', { stroke: 6, maxW: 220 });
  box(300, 40, 440, 110, '#1e2140', K, 26, 7); shine(304, 44, 432, 102, 22); txt('CHEF METER', 520, 74, 28, '#fff', { weight: 800 }); box(330, 98, 380, 34, '#2a2f55', '#fff', 17, 4); const m = L.meter ?? 3; ctx.fillStyle = m > 50 ? '#8fd18a' : '#e04a3a'; rr(334, 102, Math.max(26, 372 * m / 100), 26, 13); ctx.fill(); txt(m + '%', 520, 116, 26, '#fff', { stroke: 5 });
  box(760, 40, 290, 110, '#fff', K, 26, 7); ctx.fillStyle = '#e8e8f0'; rr(770, 50, 270, 40, 20); ctx.fill(); txt('GUESTS', 905, 76, 30, K, { weight: 800 }); txt('22', 905, 118, 46, '#e04a3a', { weight: 900 }); ctx.restore(); }
"""
t = t[:i0] + hud + t[i1:]
for o, n in [("['note', 'math', 'vote', 'counter'].includes(L.scene)", "['vote', 'end', 'cal', 'crash'].includes(L.scene)"),
             ("dollar(lerp(W + 700, -700, e), 960, 9.5, Math.PI / 2 + .08)", "pan(lerp(W + 900, -900, e), 960, 5, -.3)"),
             ("['vote', 'counter', 'math'].includes(LL.scene)", "['vote', 'end', 'crash'].includes(LL.scene)"),
             ("const SH = { stamp: 20, boing: 10, crowd: 5, slide: 9, honk: 7, cash: 5, whistle: 4, spend: 12 };", "const SH = { stamp: 20, boing: 10, slide: 9, horn: 8, spend: 14, scream: 10 };")]:
    assert o in t, o; t = t.replace(o, n)
t = t.replace('function captions(t) {', 'function captions(t) { if (window.NOCAP) return;')
out = h + '\n' + open(os.path.join(here, 'scenes.js')).read() + '\n' + t
open(os.path.join(here, 'engine.html'), 'w').write(out)
for d in sys.argv[1:]: open(os.path.join(d, 'episode.html'), 'w').write(out)
print('ok')

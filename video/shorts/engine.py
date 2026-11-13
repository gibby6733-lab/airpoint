"""Render a vertical Short (1080x1920) from scripts.VIDEOS: python3 engine.py <slug> [preview]"""
import json, math, random, re, subprocess, sys
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFont
from scripts import VIDEOS

W, H, FPS = 1080, 1920, 30
GAP = 0.16
F = "/usr/share/fonts/opentype/inter/"
fnt = lambda n, s: ImageFont.truetype(F + n, s)
F_CAP = fnt("Inter-ExtraBold.otf", 86)
F_CARD = fnt("InterDisplay-Bold.otf", 112)
F_STAT = fnt("InterDisplay-Bold.otf", 230)
F_SUB = fnt("Inter-Bold.otf", 44)
F_TAG = fnt("Inter-Bold.otf", 30)
F_TH = fnt("Inter-Black.otf", 150) if __import__("os").path.exists(F + "Inter-Black.otf") else fnt("Inter-ExtraBold.otf", 150)

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1 - (1 - x) ** 3
def back(x):
    x = clamp(x); c = 1.7
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def C(c, a=1.0): return (int(c[0]), int(c[1]), int(c[2]), int(255 * clamp(a)))
def mix(a, b, k): return tuple(a[i] + (b[i] - a[i]) * k for i in range(3))

THEMES = {
    "titanic":    dict(sky=((4, 8, 20), (18, 34, 58)), part="snow", root=55.0),
    "hindenburg": dict(sky=((14, 8, 10), (60, 30, 22)), part="ember", root=49.0),
    "chernobyl":  dict(sky=((6, 10, 8), (26, 40, 30)), part="dust", root=46.2),
    "challenger": dict(sky=((70, 120, 170), (190, 215, 235)), part="none", root=58.3),
    "tacoma":     dict(sky=((40, 52, 66), (110, 125, 138)), part="rain", root=51.9),
    "molasses":   dict(sky=((30, 34, 44), (90, 96, 108)), part="snow", root=49.0),
    "pompeii":    dict(sky=((30, 14, 10), (120, 60, 34)), part="ash", root=43.6),
}

# ---------------- hero illustrations (vector, drawn per frame) ----------------
class Cam:
    def __init__(s, cx, cy, sc): s.cx, s.cy, s.sc = cx, cy, sc
    def p(s, x, y): return (s.cx + x * s.sc, s.cy + y * s.sc)
    def P(s, pts): return [s.p(x, y) for x, y in pts]
    def r(s, x0, y0, x1, y1): a, b = s.p(x0, y0), s.p(x1, y1); return [a[0], a[1], b[0], b[1]]
    def w(s, v): return max(1, int(v * s.sc))

def flames(d, c, x0, x1, y0, y1, t, n, seed, a=1.0):
    rnd = random.Random(seed)
    for i in range(n):
        x = rnd.uniform(x0, x1); y = rnd.uniform(y0, y1); r = rnd.uniform(18, 60)
        f = 0.5 + 0.5 * math.sin(t * rnd.uniform(6, 14) + i)
        rr = r * (0.7 + 0.5 * f)
        col = mix((255, 90, 20), (255, 230, 120), f)
        d.ellipse(c.r(x - rr, y - rr * 1.4 - 20 * f, x + rr, y + rr * 0.6), fill=C(col, 0.75 * a))

def hero_titanic(d, c, t, st, p):
    sea_y = 170
    sx = -420 + 25 * math.sin(t * 0.2)
    sink = 0 if st < 2 else 90
    tilt = 0 if st < 1 else 22
    s = 0.95
    def S(px, py): return (sx + px * s, sea_y + sink + py * s + tilt * (px / 690.0))
    hull = [S(*q) for q in [(0, -70), (640, -70), (690, -95), (650, 0), (40, 0)]]
    d.polygon(c.P(hull), fill=C((8, 10, 16)))
    d.polygon(c.P([S(*q) for q in [(90, -70), (90, -108), (560, -108), (560, -70)]]), fill=C((8, 10, 16)))
    for fx in (175, 270, 365, 460):
        d.polygon(c.P([S(fx, -108), S(fx + 6, -215), S(fx + 52, -215), S(fx + 46, -108)]), fill=C((20, 18, 18)))
        d.polygon(c.P([S(fx + 5, -198), S(fx + 6, -215), S(fx + 52, -215), S(fx + 51, -198)]), fill=C((180, 90, 30) if st < 2 else (60, 40, 30)))
    if st < 2:
        for row, yy in enumerate((-88, -52, -28)):
            for i in range(24 - row * 2):
                if (i * 7 + row * 3) % 5:
                    x, y = S(110 + i * 21 + row * 18, yy)
                    d.ellipse(c.r(x - 2.6, y - 2.6, x + 2.6, y + 2.6), fill=C((255, 214, 140)))
    # iceberg
    bx = 420
    pts = [(-170, 0), (-120, -100), (-70, -120), (-30, -250), (20, -200), (60, -300), (110, -170), (150, -130), (190, 0)]
    d.polygon(c.P([(bx + x, sea_y + y) for x, y in pts]), fill=C((215, 235, 250)))
    d.polygon(c.P([(bx + x, sea_y + y) for x, y in [(20, -200), (60, -300), (110, -170), (150, -130), (190, 0), (40, 0)]]), fill=C((150, 190, 222)))
    d.rectangle(c.r(-2000, sea_y, 2000, 1400), fill=C((8, 26, 46)))
    d.polygon(c.P([(bx + x, sea_y + y) for x, y in [(-180, 0), (200, 0), (280, 160), (140, 330), (-110, 300), (-240, 140)]]), fill=C((40, 90, 130, ), 0.5))
    for i in range(7):
        yy = sea_y + 18 + i * 30
        d.line(c.P([(-2000, yy), (2000, yy)]), fill=C((40, 80, 115), 0.35), width=2)

def hero_hindenburg(d, c, t, st, p):
    gy = 330
    d.rectangle(c.r(-2000, gy, 2000, 1400), fill=C((22, 16, 14)))
    # mooring mast
    for x in (560, 610):
        d.line(c.P([(x, gy), (585, -60)]), fill=C((30, 24, 22)), width=c.w(8))
    for k in range(8):
        y = gy - k * 48
        d.line(c.P([(560 + k * 3, y), (610 - k * 3, y)]), fill=C((30, 24, 22)), width=c.w(4))
    drop = 0 if st < 2 else 120 * ease(p)
    cx, cy = -60 + 20 * math.sin(t * 0.3), -60 + drop
    hull_col = (190, 190, 196) if st < 2 else (70, 50, 44)
    d.ellipse(c.r(cx - 520, cy - 110, cx + 520, cy + 110), fill=C(hull_col))
    d.ellipse(c.r(cx - 520, cy - 10, cx + 520, cy + 110), fill=C(mix(hull_col, (0, 0, 0), 0.25)))
    for i in range(1, 16):
        x = cx - 520 + i * 65
        d.line(c.P([(x, cy - 100 + abs(i - 8) ** 2 * 0.8), (x, cy + 100 - abs(i - 8) ** 2 * 0.8)]), fill=C(mix(hull_col, (0, 0, 0), 0.15)), width=c.w(2))
    for sgn in (-1, 1):
        d.polygon(c.P([(cx - 380, cy + sgn * 40), (cx - 520, cy + sgn * 200), (cx - 560, cy + sgn * 190), (cx - 470, cy + sgn * 20)]), fill=C(mix(hull_col, (0, 0, 0), 0.3)))
    d.rounded_rectangle(c.r(cx + 150, cy + 95, cx + 290, cy + 140), 10, fill=C((60, 60, 66)))
    if st >= 1:
        k = 1.0 if st >= 2 else ease(p * 1.5)
        flames(d, c, cx - 520, cx - 520 + 1040 * (0.25 + 0.75 * k) * (1 if st >= 2 else 0.35), cy - 140, cy + 100, t, 70 if st >= 2 else 30, 3)

def hero_chernobyl(d, c, t, st, p):
    gy = 280
    d.rectangle(c.r(-2000, gy, 2000, 1400), fill=C((18, 22, 18)))
    d.rectangle(c.r(-460, -40, 360, gy), fill=C((70, 74, 70)))
    d.rectangle(c.r(-300, -190, 200, -40), fill=C((86, 90, 86)))
    for i in range(10):
        x = -430 + i * 78
        for y in (40, 140):
            col = (40, 46, 44)
            if st >= 1 and (i + int(t * 3)) % 3 == 0: col = (230, 70, 50)
            d.rectangle(c.r(x, y, x + 46, y + 50), fill=C(col))
    # vent stack
    sx = 250
    d.polygon(c.P([(sx - 50, -40), (sx - 30, -560), (sx + 30, -560), (sx + 50, -40)]), fill=C((200, 200, 196)))
    for k in range(7):
        y0 = -560 + k * 74
        if k % 2 == 0:
            d.polygon(c.P([(sx - 30 - k * 2.7, y0), (sx + 30 + k * 2.7, y0), (sx + 32 + k * 2.7, y0 + 37), (sx - 32 - k * 2.7, y0 + 37)]), fill=C((200, 60, 50)))
    for k in range(5):
        y = -500 + k * 110
        d.line(c.P([(sx - 120, y), (sx + 120, y)]), fill=C((60, 60, 60)), width=c.w(4))
    if st >= 2:
        glow = 0.6 + 0.4 * math.sin(t * 8)
        for r, a in ((380, 0.12), (260, 0.2), (150, 0.35)):
            d.ellipse(c.r(-50 - r, -190 - r, -50 + r, -190 + r), fill=C((150, 200, 255), a * glow))
        d.polygon(c.P([(-140, -190), (-110, -900), (10, -900), (40, -190)]), fill=C((170, 210, 255), 0.35 * glow))
        rnd = random.Random(5)
        for i in range(26):
            ang = rnd.uniform(-2.6, -0.5); sp = rnd.uniform(200, 600) * (0.5 + 0.5 * ease(p * 2))
            x, y = -50 + math.cos(ang) * sp, -190 + math.sin(ang) * sp + 300 * (p ** 2)
            d.rectangle(c.r(x - 12, y - 8, x + 12, y + 8), fill=C((40, 40, 40)))
        flames(d, c, -300, 200, -230, -150, t, 25, 9)

def hero_challenger(d, c, t, st, p):
    gy = 380
    if st == 0:
        d.rectangle(c.r(-2000, gy, 2000, 1400), fill=C((60, 70, 60)))
        for k in range(14):
            y = gy - k * 60
            d.line(c.P([(-330, y), (-250, y - 60)]), fill=C((120, 60, 40)), width=c.w(5))
        d.line(c.P([(-330, gy), (-330, gy - 840)]), fill=C((120, 60, 40)), width=c.w(10))
        d.line(c.P([(-250, gy), (-250, gy - 840)]), fill=C((120, 60, 40)), width=c.w(10))
        lift = 0
    else:
        lift = -120 * ease(p)
    if st <= 1:
        oy = lift + (0 if st == 0 else -60 * math.sin(t))
        if st == 1:
            for i in range(14):
                yy = gy - 40 + oy + i * 70
                rr = 60 + i * 26
                d.ellipse(c.r(-rr - 60, yy - rr * 0.6, rr - 60, yy + rr * 0.6), fill=C((250, 250, 250), 0.85))
            d.polygon(c.P([(-150, gy - 40 + oy), (-60, gy + 200 + oy), (30, gy - 40 + oy)]), fill=C((255, 200, 90)))
        d.rounded_rectangle(c.r(-60, -480 + oy, 60, gy - 40 + oy), 40, fill=C((205, 110, 50)))
        for bx in (-130, 70):
            d.rectangle(c.r(bx, -380 + oy, bx + 60, gy - 20 + oy), fill=C((240, 240, 236)))
            d.polygon(c.P([(bx, -380 + oy), (bx + 30, -470 + oy), (bx + 60, -380 + oy)]), fill=C((240, 240, 236)))
        d.polygon(c.P([(0, -300 + oy), (40, -340 + oy), (110, -300 + oy), (120, 300 + oy), (220, 320 + oy), (220, 360 + oy), (0, 360 + oy)]), fill=C((250, 250, 250)))
        d.polygon(c.P([(170, 300 + oy), (230, 150 + oy), (240, 300 + oy)]), fill=C((40, 40, 44)))
    else:
        # breakup: smoke cloud + diverging booster trails
        k = ease(p * 1.3)
        cx, cy = 0, -100
        rnd = random.Random(2)
        for i in range(40):
            ang = rnd.uniform(0, 6.28); rr = rnd.uniform(0, 220) * (0.4 + 0.6 * k)
            x, y = cx + math.cos(ang) * rr, cy + math.sin(ang) * rr * 0.7
            r = rnd.uniform(50, 110)
            d.ellipse(c.r(x - r, y - r, x + r, y + r), fill=C((245, 245, 245), 0.9))
        for i in range(4):
            x, y = cx + rnd.uniform(-80, 80), cy + rnd.uniform(-60, 60)
            d.ellipse(c.r(x - 60, y - 60, x + 60, y + 60), fill=C((255, 150, 60), 0.8))
        for sgn in (-1, 1):
            pts = []
            for j in range(30):
                q = j / 29 * k
                pts.append((cx + sgn * (q * 520 + 40 * math.sin(q * 6)), cy - q * 560 + q * q * 200))
            for j in range(len(pts) - 1):
                w = 30 + j * 2
                d.line(c.P([pts[j], pts[j + 1]]), fill=C((250, 250, 250), 0.95), width=c.w(w))
            d.ellipse(c.r(pts[-1][0] - 22, pts[-1][1] - 22, pts[-1][0] + 22, pts[-1][1] + 22), fill=C((255, 220, 120)))
        d.line(c.P([(0, 40), (0, 900)]), fill=C((250, 250, 250), 0.6), width=c.w(40))

def hero_tacoma(d, c, t, st, p):
    wy = 300
    d.rectangle(c.r(-2000, wy, 2000, 1400), fill=C((30, 52, 66)))
    for i in range(6):
        d.line(c.P([(-2000, wy + 20 + i * 34), (2000, wy + 20 + i * 34)]), fill=C((70, 100, 120), 0.4), width=2)
    d.polygon(c.P([(-2000, wy), (-760, wy), (-640, wy - 120), (-2000, wy - 160)]), fill=C((40, 56, 46)))
    d.polygon(c.P([(2000, wy), (760, wy), (640, wy - 110), (2000, wy - 150)]), fill=C((40, 56, 46)))
    T, top, deck = 380, -420, 60
    amp = [6, 26, 60, 60][st]
    tw = [0, 0, 1, 1][st]
    gap = st == 3
    def dy(x): return amp * (1 - tw) * math.sin(x / 120 - t * 3.2) + 0
    def twist(x): return tw * 60 * math.sin(math.pi * (x + T) / (2 * T)) * math.sin(t * 4.5) if abs(x) < T else 0
    def cab(x):
        if abs(x) <= T: return top + (deck - 30 - top) * (1 - (x / T) ** 2)
        return top + (abs(x) - T) / (760 - T) * (deck - top) * 0.9
    xs = list(range(-760, 761, 20))
    for sgn, col in ((1, (150, 160, 170)), (-1, (190, 200, 210))):
        pts = [(x, cab(x) + (dy(x) * 0.3 if abs(x) < T else 0)) for x in xs]
        d.line(c.P(pts), fill=C(col), width=c.w(5))
    for x in xs[::2]:
        if gap and abs(x) < 300: continue
        d.line(c.P([(x, cab(x)), (x, deck + dy(x) - twist(x))]), fill=C((150, 160, 170), 0.8), width=c.w(2))
    for seg in ([x for x in xs if x <= -300], [x for x in xs if x >= 300]) if gap else (xs,):
        up = [(x, deck + dy(x) - twist(x)) for x in seg]
        lo = [(x, deck + 22 + dy(x) + twist(x)) for x in seg]
        d.polygon(c.P(up + lo[::-1]), fill=C((95, 100, 104)))
    if gap:
        for i, x0 in enumerate(range(-280, 280, 90)):
            f = clamp(p * 1.6 - i * 0.05)
            yy = deck + 260 * f * f
            d.polygon(c.P([(x0, yy), (x0 + 80, yy + 30 * f), (x0 + 80, yy + 50 + 30 * f), (x0, yy + 20)]), fill=C((95, 100, 104), 1 - f * 0.6))
            if f > 0.8:
                d.ellipse(c.r(x0 - 40, wy - 30, x0 + 120, wy + 20), fill=C((220, 235, 245), (1 - f) * 3))
    for sgn in (-1, 1):
        x = sgn * T
        d.rectangle(c.r(x - 22, top - 20, x + 22, wy), fill=C((70, 76, 82)))
        d.rectangle(c.r(x - 30, top + 120, x + 30, top + 140), fill=C((70, 76, 82)))

def hero_molasses(d, c, t, st, p):
    gy = 330
    d.rectangle(c.r(-2000, gy, 2000, 1400), fill=C((40, 40, 44)))
    for x0, w, h in ((-760, 200, 380), (-540, 150, 300), (380, 180, 420), (580, 220, 330)):
        d.rectangle(c.r(x0, gy - h, x0 + w, gy), fill=C((60, 52, 50)))
        for yy in range(gy - h + 30, gy - 30, 60):
            for xx in range(x0 + 20, x0 + w - 30, 50):
                d.rectangle(c.r(xx, yy, xx + 24, yy + 30), fill=C((90, 80, 60)))
    d.rectangle(c.r(-900, 130, 900, 160), fill=C((30, 30, 30)))
    for x in range(-860, 900, 160):
        d.rectangle(c.r(x, 160, x + 16, gy), fill=C((30, 30, 30)))
    if st == 0:
        d.rectangle(c.r(-230, -280, 230, gy), fill=C((110, 66, 40)))
        d.ellipse(c.r(-230, -320, 230, -240), fill=C((140, 86, 52)))
        for k in range(6):
            d.line(c.P([(-230, -220 + k * 90), (230, -220 + k * 90)]), fill=C((80, 48, 30)), width=c.w(4))
        for k in range(8):
            x = -200 + k * 55
            d.line(c.P([(x, -240), (x + 4, -240 + 120 + (k * 37) % 200)]), fill=C((70, 36, 18), 0.8), width=c.w(5))
    else:
        k = ease(p * 1.4) if st == 1 else 1.0
        for sgn in (-1, 1):
            d.polygon(c.P([(sgn * 30, gy), (sgn * 230 + sgn * 160 * k, -100 + 300 * k), (sgn * 240 + sgn * 200 * k, -60 + 330 * k), (sgn * 60, gy)]), fill=C((110, 66, 40)))
        lvl = gy - 260 * k if st == 1 else gy - 130
        pts = [(x, lvl + 30 * math.sin(x / 70 + t * 2) * (1.2 - k * 0.7)) for x in range(-1000, 1001, 40)]
        d.polygon(c.P(pts + [(1000, gy + 400), (-1000, gy + 400)]), fill=C((58, 28, 12)))
        d.line(c.P(pts), fill=C((120, 64, 30)), width=c.w(8))

def hero_pompeii(d, c, t, st, p):
    gy = 330
    if st >= 1:
        k = 1.0 if st >= 2 else ease(p * 1.2)
        for i in range(30):
            q = i / 29
            y = -260 - q * 900 * k
            r = 60 + q * 180 + (q > 0.8) * (q - 0.8) * 1400
            x = 120 + 30 * math.sin(i + t)
            d.ellipse(c.r(x - r, y - r * 0.6, x + r, y + r * 0.6), fill=C(mix((70, 60, 56), (40, 34, 32), q), 0.95))
        flames(d, c, 60, 180, -300, -250, t, 8, 4)
    d.polygon(c.P([(-500, gy), (0, -230), (60, -260), (190, -260), (250, -220), (800, gy)]), fill=C((54, 38, 32)))
    d.polygon(c.P([(120, -260), (250, -220), (800, gy), (400, gy)]), fill=C((40, 28, 24)))
    d.rectangle(c.r(-2000, gy, 2000, 1400), fill=C((60, 46, 36)))
    for i, x in enumerate(range(-700, -100, 110)):
        h = 260 - (i % 3) * 50
        d.rectangle(c.r(x, gy - h, x + 40, gy), fill=C((200, 180, 150)))
        d.rectangle(c.r(x - 12, gy - h - 22, x + 52, gy - h), fill=C((200, 180, 150)))
    d.rectangle(c.r(-720, gy - 290, -60, gy - 262), fill=C((190, 170, 140)))
    if st >= 2:
        k = ease(p * 1.1) if st == 2 else 1.0
        front = 250 - 1100 * k
        rnd = random.Random(8)
        for i in range(60):
            x = rnd.uniform(front, 700); y = gy - rnd.uniform(0, 300) * (1 - (x - front) / 1400) - 60
            r = rnd.uniform(70, 140)
            d.ellipse(c.r(x - r, y - r, x + r, y + r), fill=C((120, 100, 86), 0.92))
    if st >= 3:
        d.rectangle(c.r(-2000, gy - 60, 2000, 1400), fill=C((110, 98, 88)))

HEROES = dict(titanic=hero_titanic, hindenburg=hero_hindenburg, chernobyl=hero_chernobyl,
              challenger=hero_challenger, tacoma=hero_tacoma, molasses=hero_molasses, pompeii=hero_pompeii)

YOFF = dict(challenger=170, chernobyl=60)
_g = np.zeros((H, W), np.float32)
_y = np.arange(H, dtype=np.float32)[:, None]
_g += np.clip(1 - _y / 380, 0, 1) * 160
_g += np.clip((_y - 1100) / 820, 0, 1) ** 1.2 * 170
VIG = Image.fromarray(_g.astype(np.uint8), "L")
CAMS = [(0.78, 0, 0), (1.05, 160, 60), (1.05, -180, 40), (1.3, 40, 120), (0.95, -60, -40)]

# ---------------- captions ----------------
def syl(w):
    w = w.lower()
    if re.search(r"\d", w): return 2.5 * len(re.sub(r"\D", "", w)) ** 0.7 + 1
    n = len(re.findall(r"[aeiouy]+", w))
    return max(1, n) + (0.6 if w[-1:] in ",.?!" else 0)

def chunks(cap):
    words = cap.split()
    out, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) == 3 or w[-1] in ",.?!" or sum(len(x) for x in cur) > 14:
            out.append(cur); cur = []
    if cur: out.append(cur)
    return out

def draw_caption(d, words, act, accent):
    sp = F_CAP.getlength(" ")
    lines, line = [], []
    for i, w in enumerate(words):
        test = line + [(i, w)]
        if sum(F_CAP.getlength(x) for _, x in test) + sp * (len(test) - 1) > 900 and line:
            lines.append(line); line = [(i, w)]
        else: line = test
    lines.append(line)
    y = 1330 - (len(lines) - 1) * 52
    for ln in lines:
        tw = sum(F_CAP.getlength(x) for _, x in ln) + sp * (len(ln) - 1)
        x = W / 2 - tw / 2
        for i, w in ln:
            col = (255, 222, 40) if i == act else (255, 255, 255)
            d.text((x, y), w, font=F_CAP, fill=col + (255,), stroke_width=9, stroke_fill=(0, 0, 0, 255), anchor="lm")
            x += F_CAP.getlength(w) + sp
        y += 104

# ---------------- particles ----------------
def particles(d, kind, t):
    if kind == "none": return
    rnd = random.Random(11)
    for i in range(90):
        x0, y0, sp, r = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(0.5, 1.5), rnd.uniform(1.5, 4.5)
        if kind == "snow":
            x = (x0 + 30 * math.sin(t + i) - 20 * t * sp) % W; y = (y0 + 70 * t * sp) % H; col, a = (235, 240, 255), 0.6
        elif kind == "ember":
            x = (x0 + 25 * math.sin(t * 2 + i)) % W; y = (y0 - 120 * t * sp) % H; col, a = (255, 160, 60), 0.8 * (0.5 + 0.5 * math.sin(t * 5 + i))
        elif kind == "dust":
            x = (x0 + 15 * t * sp) % W; y = (y0 + 10 * math.sin(t + i)) % H; col, a = (200, 230, 180), 0.35
        elif kind == "ash":
            x = (x0 - 40 * t * sp) % W; y = (y0 + 90 * t * sp) % H; col, a = (150, 140, 130), 0.7
        elif kind == "rain":
            x = (x0 - 300 * t * sp) % W; y = (y0 + 40 * t * sp) % H
            d.line([(x, y), (x + 60, y - 8)], fill=C((210, 220, 230), 0.35), width=2); continue
        d.ellipse([x - r, y - r, x + r, y + r], fill=C(col, a))

# ---------------- main render ----------------
def build_timeline(v):
    meta = json.load(open(f"build/{v['slug']}/narr.json"))
    t, tl = 0.0, []
    for b, du in zip(v["beats"], meta["durs"]):
        tl.append((t, du)); t += du + GAP
    return tl, t + 0.25 - GAP, meta

def word_times(cap, t0, du):
    ch = chunks(cap)
    flat = [w for c in ch for w in c]
    ws = [syl(w) for w in flat]; tot = sum(ws)
    times, acc = [], t0
    for w in ws:
        times.append(acc); acc += du * w / tot
    return ch, times

def make_bg(theme):
    a, b = THEMES[theme]["sky"]
    g = np.linspace(0, 1, H)[:, None]
    arr = (np.array(a)[None, None, :] * (1 - g[..., None]) + np.array(b)[None, None, :] * g[..., None])
    arr = np.repeat(arr, W, axis=1).astype(np.uint8)
    return Image.fromarray(arr, "RGB")

def draw_card(d, text, k, accent, y=430):
    lines = text.split("\n")
    sc = 0.6 + 0.4 * back(k)
    size = 112
    while max(F_CARD.font_variant(size=size).getlength(l) for l in lines) > 940: size -= 6
    f = F_CARD.font_variant(size=int(size * sc))
    yy = y - (len(lines) - 1) * size * 0.55
    for i, l in enumerate(lines):
        col = accent if i == len(lines) - 1 and len(lines) > 1 else (255, 255, 255)
        d.text((W / 2, yy), l, font=f, fill=col + (int(255 * clamp(k * 3)),), anchor="mm", stroke_width=6, stroke_fill=(0, 0, 0, int(200 * clamp(k * 3))))
        yy += size * 1.08

def render_frame(v, bg, beats, tl, total, T, theme):
    img = bg.copy(); d = ImageDraw.Draw(img, "RGBA")
    bi = max(i for i, (t0, _) in enumerate(tl) if t0 <= T or i == 0)
    b = beats[bi]; t0, du = tl[bi]; lt = T - t0
    nd = tl[bi + 1][0] if bi + 1 < len(tl) else total
    p = clamp(lt / max(0.1, nd - t0))
    cam = CAMS[b.get("cam", (bi * 3 + 1) % len(CAMS))]
    punch = 1 + 0.08 * (1 - ease(lt / 0.35))
    sc = cam[0] * (1 + 0.05 * p) * punch
    shake = 0
    if b.get("hit") and lt < 0.5: shake = 18 * (1 - lt / 0.5)
    sx = random.uniform(-shake, shake); sy = random.uniform(-shake, shake)
    HEROES[theme](d, Cam(W / 2 + cam[1] + sx, 900 + YOFF.get(theme, 0) + cam[2] + sy, sc), T, b.get("st", 0), p)
    particles(d, THEMES[theme]["part"], T)
    # vignette bands for legibility
    img.paste((0, 0, 0), (0, 0, W, H), VIG)
    if "stat" in b:
        d.rectangle([0, 0, W, H], fill=(0, 0, 0, 120))
        k = ease(lt / 0.4)
        stat = b["stat"]
        m = re.match(r"^([~]?)([\d,\.]+)(.*)$", stat)
        if m and lt < 0.9:
            num = m.group(2); val = float(num.replace(",", "")); dec = len(num.split(".")[1]) if "." in num else 0
            cur = val * ease(lt / 0.9)
            s = f"{cur:,.{dec}f}" if "," in num else f"{cur:.{dec}f}"
            stat = m.group(1) + s + m.group(3)
        f = F_STAT
        while f.getlength(stat) > 980: f = f.font_variant(size=f.size - 10)
        d.text((W / 2, 700), stat, font=f, fill=v["accent"] + (255,), anchor="mm", stroke_width=8, stroke_fill=(0, 0, 0, 255))
        d.text((W / 2, 870), b["sub"], font=F_SUB, fill=(255, 255, 255, int(255 * k)), anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0, 255))
    elif "k" in b:
        k = 1.0 if bi == 0 else ease(lt / 0.3)
        draw_card(d, b["k"], k, v["accent"])
    if b.get("hit") and lt < 0.25:
        d.rectangle([0, 0, W, H], fill=(255, 255, 255, int(200 * (1 - lt / 0.25))))
    ch, times = word_times(b["cap"], t0, du)
    flat_i = max([i for i, tt in enumerate(times) if tt <= T] or [0])
    acc = 0
    for c in ch:
        if acc <= flat_i < acc + len(c):
            draw_caption(d, c, flat_i - acc, v["accent"]); break
        acc += len(c)
    else:
        if T > t0 + du: draw_caption(d, ch[-1], len(ch[-1]) - 1, v["accent"])
    d.rectangle([0, 0, W, 10], fill=(255, 255, 255, 50))
    d.rectangle([0, 0, W * T / total, 10], fill=v["accent"] + (255,))
    return img

def render_audio(v, tl, total, meta, out):
    sr = meta["sr"]; n = int(total * sr) + sr
    mixb = np.zeros(n)
    rnd = np.random.default_rng(3)
    root = THEMES[v["theme"]]["root"]
    tt = np.arange(n) / sr
    bed = 0.05 * np.sin(2 * np.pi * root * tt) + 0.03 * np.sin(2 * np.pi * root * 1.5 * tt) + 0.02 * np.sin(2 * np.pi * root * 2 * tt) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.2 * tt))
    noise = np.cumsum(rnd.normal(0, 1, n)); noise -= np.convolve(noise, np.ones(4000) / 4000, "same"); noise /= np.max(np.abs(noise)) + 1e-9
    mixb += bed + 0.05 * noise
    for i, (b, (t0, du)) in enumerate(zip(v["beats"], tl)):
        a, _ = sf.read(f"build/{v['slug']}/{i:02d}.wav")
        s = int(t0 * sr); mixb[s:s + len(a)] += a * 0.95
        # whoosh
        L = int(0.35 * sr); w = rnd.normal(0, 1, L); w = np.convolve(w, np.ones(30) / 30, "same")
        env = np.sin(np.linspace(0, np.pi, L)) ** 2
        st = max(0, s - int(0.12 * sr)); mixb[st:st + L] += 0.10 * w[:len(mixb[st:st + L])] * env[:len(mixb[st:st + L])]
        if b.get("hit"):
            L = int(1.2 * sr); x = np.arange(L) / sr
            boom = np.sin(2 * np.pi * (70 * x - 20 * x * x)) * np.exp(-x * 3.5) * 0.5
            mixb[s:s + L] += boom[:len(mixb[s:s + L])]
    mixb = mixb[:int(total * sr)]
    fade = int(0.08 * sr); mixb[:fade] *= np.linspace(0, 1, fade)
    mixb /= max(1.0, np.max(np.abs(mixb)) / 0.95)
    sf.write(out, mixb, sr)

def main():
    slug = sys.argv[1]; prev = len(sys.argv) > 2
    v = next(x for x in VIDEOS if x["slug"] == slug)
    theme = v["theme"]; beats = v["beats"]
    tl, total, meta = build_timeline(v)
    bg = make_bg(theme)
    random.seed(1)
    if prev:
        for i, (t0, du) in enumerate(tl):
            render_frame(v, bg, beats, tl, total, t0 + du * 0.6, theme).save(f"build/{slug}/prev{i:02d}.png")
        return
    wav = f"build/{slug}/mix.wav"; render_audio(v, tl, total, meta, wav)
    out = f"out/{slug}.mp4"
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "19",
                           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for f in range(int(total * FPS)):
        ff.stdin.write(render_frame(v, bg, beats, tl, total, f / FPS, theme).tobytes())
    ff.stdin.close(); ff.wait()
    print(slug, round(total, 1), "s")

if __name__ == "__main__":
    main()

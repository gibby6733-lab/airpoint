import math, random, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
OUT = sys.argv[1]
PREVIEW = len(sys.argv) > 2  # write stills instead of video

F = "/usr/share/fonts/opentype/inter/"
def font(name, size): return ImageFont.truetype(F + name, size)
F_KICK = font("Inter-SemiBold.otf", 34)
F_HEAD = font("InterDisplay-Bold.otf", 84)
F_BODY = font("Inter-Medium.otf", 42)
F_STAT = font("InterDisplay-Bold.otf", 170)
F_SMALL = font("Inter-SemiBold.otf", 28)
F_TINY = font("Inter-Medium.otf", 24)
F_CARD = font("Inter-Bold.otf", 30)

WHITE = (240, 244, 250)
MUTED = (160, 176, 200)
AMBER = (245, 176, 65)
RED = (232, 72, 72)
ICE = (205, 228, 245)
SEA = (14, 40, 66)
SHIP = (10, 14, 22)
MX = 90

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1 - (1 - x) ** 3
def ramp(t, a, b): return ease((t - a) / (b - a)) if b > a else float(t >= a)
def rgba(c, a): return (c[0], c[1], c[2], int(255 * clamp(a)))

# ---------- background ----------
random.seed(7)
bg = Image.new("RGB", (W, H))
bd = ImageDraw.Draw(bg)
for y in range(H):
    k = y / H
    bd.line([(0, y), (W, y)], fill=(int(6 + 8 * k), int(10 + 16 * k), int(22 + 26 * k)))
STARS = [(random.uniform(0, W), random.uniform(0, H * 0.55), random.uniform(0.8, 2.4), random.uniform(0, 6.28)) for _ in range(170)]

def wrap(text, fnt, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if fnt.getlength(test) <= maxw: cur = test
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

# ---------- art helpers ----------
def ship(d, x, y, s, a, col=SHIP, lights=True):
    """Generic four-funnel liner silhouette, bow to the right. (x,y) = waterline at stern."""
    P = lambda pts: [(x + px * s, y + py * s) for px, py in pts]
    d.polygon(P([(0, -70), (640, -70), (690, -95), (650, 0), (40, 0)]), fill=rgba(col, a))
    d.polygon(P([(90, -70), (90, -105), (560, -105), (560, -70)]), fill=rgba(col, a))
    d.polygon(P([(130, -105), (130, -125), (520, -125), (520, -105)]), fill=rgba(col, a))
    for fx in (175, 270, 365, 460):
        d.polygon(P([(fx, -125), (fx + 6, -215), (fx + 52, -215), (fx + 46, -125)]), fill=rgba((26, 22, 20), a))
        d.polygon(P([(fx + 5, -200), (fx + 6, -215), (fx + 52, -215), (fx + 51, -200)]), fill=rgba((40, 30, 24), a))
    d.line(P([(60, -70), (40, -280)]), fill=rgba(col, a), width=max(1, int(4 * s)))
    d.line(P([(600, -70), (620, -290)]), fill=rgba(col, a), width=max(1, int(4 * s)))
    d.line(P([(40, -280), (620, -290)]), fill=rgba((60, 70, 90), a * 0.6), width=1)
    if lights:
        for row, yy in enumerate((-85, -55, -30)):
            for i in range(22 - row * 2):
                px = 110 + i * 22 + row * 20
                if (i * 7 + row * 3) % 5:
                    r = 2.2 * s
                    cx, cy = x + px * s, y + yy * s
                    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=rgba((255, 214, 140), a * 0.9))

def iceberg(d, x, y, s, a, col=ICE):
    pts = [(-160, 0), (-120, -90), (-80, -110), (-40, -210), (10, -180), (40, -260), (90, -150), (130, -120), (170, 0)]
    d.polygon([(x + px * s, y + py * s) for px, py in pts], fill=rgba(col, a))
    shade = [(10, -180), (40, -260), (90, -150), (130, -120), (170, 0), (40, 0)]
    d.polygon([(x + px * s, y + py * s) for px, py in shade], fill=rgba((150, 185, 215), a))
    under = [(-170, 0), (180, 0), (240, 120), (120, 260), (-90, 240), (-210, 110)]
    d.polygon([(x + px * s, y + py * s) for px, py in under], fill=rgba((40, 90, 130), a * 0.55))

def sea(d, top, a, bottom=1010, calm=True, t=0):
    d.rectangle([0, top, W, bottom], fill=rgba(SEA, a))
    for i in range(6):
        yy = top + 20 + i * 28
        if yy > bottom: break
        off = (t * 20 + i * 90) % 200
        d.line([(-200 + off, yy), (W, yy)], fill=rgba((40, 80, 115), a * (0.25 if calm else 0.6)), width=2)

def ctext(d, x, y, s, fnt, col, a, anchor="mm"):
    d.text((x, y), s, font=fnt, fill=rgba(col, a), anchor=anchor)

# ---------- scene art ----------
def art_intro(img, d, t, dur, a):
    sea(d, 820, a, t=t)
    iceberg(d, 860, 820, 1.0, a)
    sx = -700 + 820 * ease(t / dur)
    ship(d, sx, 820, 0.85, a)

def art_speed(img, d, t, dur, a):
    cx, cy, R = W / 2, 720, 330
    d.arc([cx - R, cy - R, cx + R, cy + R], 150, 390, fill=rgba((40, 60, 90), a), width=26)
    frac = 0.88 * ramp(t, 0.3, 2.4)
    d.arc([cx - R, cy - R, cx + R, cy + R], 150, 150 + 240 * frac, fill=rgba(AMBER, a), width=26)
    for i in range(13):
        ang = math.radians(150 + 240 * i / 12)
        r1, r2 = R - 40, R - (70 if i % 3 == 0 else 55)
        d.line([(cx + r1 * math.cos(ang), cy + r1 * math.sin(ang)), (cx + r2 * math.cos(ang), cy + r2 * math.sin(ang))], fill=rgba(MUTED, a), width=4)
    ang = math.radians(150 + 240 * frac)
    d.line([(cx, cy), (cx + (R - 90) * math.cos(ang), cy + (R - 90) * math.sin(ang))], fill=rgba(WHITE, a), width=8)
    d.ellipse([cx - 18, cy - 18, cx + 18, cy + 18], fill=rgba(WHITE, a))
    v = 22.5 * ramp(t, 0.3, 2.4)
    ctext(d, cx, cy + 150, f"{v:.1f}", F_STAT, WHITE, a)
    ctext(d, cx, cy + 260, "KNOTS  ·  NEAR TOP SPEED", F_SMALL, MUTED, a)

WARN = [("CARONIA", "9:00 AM", 0), ("BALTIC", "1:42 PM", 0), ("AMERIKA", "1:45 PM", 0),
        ("CALIFORNIAN", "7:30 PM", 0), ("MESABA", "9:40 PM", 1), ("CALIFORNIAN", "10:55 PM", 2)]
def art_warnings(img, d, t, dur, a):
    cw, ch, gx, gy = 410, 170, 40, 36
    x0, y0 = (W - 2 * cw - gx) / 2, 360
    for i, (name, tm, flag) in enumerate(WARN):
        k = ramp(t, 0.2 + i * 0.35, 0.6 + i * 0.35) * a
        if k <= 0: continue
        x = x0 + (i % 2) * (cw + gx); y = y0 + (i // 2) * (ch + gy) + 30 * (1 - k)
        d.rounded_rectangle([x, y, x + cw, y + ch], 16, fill=rgba((232, 222, 196), k))
        d.text((x + 28, y + 26), "ICE WARNING", font=F_TINY, fill=rgba((120, 100, 70), k))
        d.text((x + 28, y + 62), name, font=F_CARD, fill=rgba((30, 30, 36), k))
        d.text((x + 28, y + 108), tm, font=F_TINY, fill=rgba((90, 80, 70), k))
        if flag:
            s = ramp(t, 3.0 + (flag - 1) * 0.6, 3.4 + (flag - 1) * 0.6) * a
            if s > 0:
                lab = "NEVER REACHED BRIDGE" if flag == 1 else "“SHUT UP, I AM BUSY”"
                d.rounded_rectangle([x + 14, y + ch - 52, x + cw - 14, y + ch - 12], 8, fill=rgba(RED, s))
                d.text((x + cw / 2, y + ch - 32), lab, font=F_TINY, fill=rgba(WHITE, s), anchor="mm")

def art_binoculars(img, d, t, dur, a):
    cx, cy = W / 2, 640
    k = ramp(t, 0.1, 0.9) * a
    for dx in (-150, 150):
        d.rounded_rectangle([cx + dx - 95, cy - 210, cx + dx + 95, cy + 40], 30, fill=rgba((44, 52, 70), k))
        d.ellipse([cx + dx - 120, cy - 10, cx + dx + 120, cy + 230], fill=rgba((44, 52, 70), k))
        d.ellipse([cx + dx - 85, cy + 25, cx + dx + 85, cy + 195], fill=rgba((12, 18, 30), k))
    d.rectangle([cx - 60, cy - 120, cx + 60, cy - 40], fill=rgba((44, 52, 70), k))
    s = ramp(t, 1.2, 1.8) * a
    if s > 0:
        L = 380 * s
        d.line([(cx - L, cy + 260), (cx + L * 0.9, cy - 290 + 550 * (1 - s))], fill=rgba(RED, s), width=26)
    # key drifting away
    kk = ramp(t, 2.0, 2.6) * a
    if kk > 0:
        kx, ky = cx - 330 - 60 * ramp(t, 2.0, 6.0), 320 - 20 * ramp(t, 2.0, 6.0)
        d.ellipse([kx - 34, ky - 34, kx + 34, ky + 34], outline=rgba(AMBER, kk), width=12)
        d.line([(kx + 30, ky), (kx + 150, ky)], fill=rgba(AMBER, kk), width=12)
        d.line([(kx + 120, ky), (kx + 120, ky + 34)], fill=rgba(AMBER, kk), width=10)
        d.line([(kx + 145, ky), (kx + 145, ky + 26)], fill=rgba(AMBER, kk), width=10)
        d.text((kx + 50, ky + 60), "locker key", font=F_TINY, fill=rgba(MUTED, kk), anchor="mm")

def art_late(img, d, t, dur, a):
    sea(d, 860, a, t=0)
    grow = ramp(t, 0.2, dur - 0.5)
    iceberg(d, W / 2, 860, 0.3 + 0.95 * grow, a * (0.25 + 0.75 * grow), col=(150, 175, 200))
    secs = max(0, 37 - int(37 * clamp((t - 0.6) / (dur - 1.6))))
    ctext(d, W / 2, 360, f"0:{secs:02d}", F_STAT, RED if secs < 10 else WHITE, a)
    ctext(d, W / 2, 455, "FROM SIGHTING TO IMPACT", F_SMALL, MUTED, a)

def art_rivets(img, d, t, dur, a):
    top, bot = 380, 900
    d.rectangle([0, top, W, bot], fill=rgba((34, 38, 46), a))
    pop = ramp(t, 1.8, 3.2)
    for i, px in enumerate(range(-40, W + 200, 260)):
        gap = 0
        if i in (2, 3): gap = 26 * pop
        d.rectangle([px + gap, top + 10, px + 250, bot - 10], fill=rgba((48, 54, 64), a))
        for ry in range(top + 50, bot - 20, 70):
            for rx in (px + 22, px + 228):
                rr = 9
                if i in (2, 3) and rx == px + 228 or i in (3, 4) and rx == px + 22:
                    off = 300 * pop * (1 + (ry % 3) * 0.3)
                    rx2, ry2 = rx + off * 0.4, ry - off * 0.5 + 400 * pop * pop
                    d.ellipse([rx2 - rr, ry2 - rr, rx2 + rr, ry2 + rr], fill=rgba((150, 140, 125), a * (1 - pop * 0.7)))
                else:
                    d.ellipse([rx - rr, ry - rr, rx + rr, ry + rr], fill=rgba((110, 105, 98), a))
    if pop > 0.2:
        for j in range(12):
            yy = top + 30 + j * 42
            gx = -40 + 2 * 260 + 248 + 13 * pop
            jet = 60 + 40 * math.sin(t * 9 + j)
            d.line([(gx, yy), (gx - jet * pop, yy + 10)], fill=rgba((110, 190, 235), a * pop), width=8)
    ctext(d, W / 2, 330, "HULL PLATES  ·  STARBOARD BOW", F_SMALL, MUTED, a)

def art_bulkheads(img, d, t, dur, a):
    x0, x1, top, bot = 70, W - 70, 470, 820
    edeck = top + 70
    n = 16
    cw = (x1 - x0) / n
    d.rectangle([x0, top, x1, bot], outline=rgba(MUTED, a), width=4)
    # flooding: bow is on the right. first 5 fill, then spill sequentially
    for i in range(n):
        c = n - 1 - i  # index from bow
        if c < 5: lvl = ramp(t, 0.4 + c * 0.15, 1.8 + c * 0.15)
        else: lvl = ramp(t, 2.2 + (c - 5) * 0.55, 2.9 + (c - 5) * 0.55)
        if lvl > 0:
            cx0 = x0 + i * cw
            yy = bot - (bot - edeck) * lvl
            d.rectangle([cx0 + 3, yy, cx0 + cw - 3, bot - 3], fill=rgba((40, 130, 200), a * 0.85))
            if c >= 4 and lvl >= 1:
                # overflow trickle to the next compartment (sternward = left)
                nxt = ramp(t, 2.2 + (c - 4) * 0.55, 2.9 + (c - 4) * 0.55)
                if nxt < 1:
                    d.line([(cx0 + 2, edeck - 6), (cx0 - 10, edeck + 40)], fill=rgba((90, 180, 240), a), width=8)
    for i in range(1, n):
        x = x0 + i * cw
        d.line([(x, edeck), (x, bot)], fill=rgba(WHITE, a * 0.8), width=4)
    for x in range(x0, x1, 28):
        d.line([(x, edeck), (x + 14, edeck)], fill=rgba(AMBER, a), width=3)
    d.text((x0 + 10, edeck - 40), "E DECK — BULKHEADS STOP HERE", font=F_TINY, fill=rgba(AMBER, a))
    ctext(d, x1 - 2 * cw, bot + 40, "BOW →", F_SMALL, MUTED, a)
    ctext(d, x0 + 70, bot + 40, "← STERN", F_SMALL, MUTED, a)
    b = ramp(t, 1.6, 2.0) * a
    d.line([(x1 - 4 * cw, bot + 80), (x1, bot + 80)], fill=rgba(WHITE, b), width=3)
    ctext(d, x1 - 2 * cw, bot + 115, "4 flooded = survivable", F_TINY, WHITE, b)
    b2 = ramp(t, 1.9, 2.3) * a
    d.line([(x1 - 5 * cw, bot + 160), (x1, bot + 160)], fill=rgba(RED, b2), width=3)
    ctext(d, x1 - 2.5 * cw, bot + 195, "5+ opened = fatal", F_TINY, RED, b2)

def art_lifeboats(img, d, t, dur, a):
    cols, sp = 54, 15.4
    total, seats = 2224, 1178
    gx0 = (W - cols * sp) / 2 + sp / 2
    gy0 = 340
    shown = int(total * ramp(t, 0.2, 2.0))
    hl = int(seats * ramp(t, 2.2, 3.6))
    for i in range(shown):
        r, c = divmod(i, cols)
        x, y = gx0 + c * sp, gy0 + r * sp
        col = AMBER if i < hl else (70, 82, 104)
        d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=rgba(col, a))
    k = ramp(t, 3.6, 4.2) * a
    ly = gy0 + (total // cols + 1) * sp + 30
    d.ellipse([MX + 40, ly - 9, MX + 58, ly + 9], fill=rgba(AMBER, k))
    d.text((MX + 72, ly), "1,178 lifeboat seats", font=F_SMALL, fill=rgba(WHITE, k), anchor="lm")
    d.ellipse([W / 2 + 60, ly - 9, W / 2 + 78, ly + 9], fill=rgba((70, 82, 104), k))
    d.text((W / 2 + 92, ly), "1,046 with no seat", font=F_SMALL, fill=rgba(WHITE, k), anchor="lm")

def art_californian(img, d, t, dur, a):
    hz = 820
    sea(d, hz, a)
    ship(d, 80, hz, 0.42, a)
    ship(d, 700, hz, 0.32, a, col=(18, 22, 32), lights=False)
    d.text((700 + 0.32 * 330, hz - 120), "Z z", font=F_HEAD, fill=rgba(MUTED, a * ramp(t, 2.5, 3.2)), anchor="mm")
    d.text((700 + 0.32 * 330, hz + 50), "CALIFORNIAN", font=F_TINY, fill=rgba(MUTED, a), anchor="mm")
    d.text((80 + 0.42 * 330, hz + 50), "TITANIC", font=F_TINY, fill=rgba(MUTED, a), anchor="mm")
    for j in range(4):
        st = 0.6 + j * 1.5
        p = (t - st) / 1.2
        if 0 < p < 1.6:
            rx = 250 + j * 12
            ry = hz - 180 - 420 * ease(min(p, 1))
            if p < 1:
                d.ellipse([rx - 5, ry - 5, rx + 5, ry + 5], fill=rgba(WHITE, a))
            else:
                q = p - 1
                for k in range(14):
                    ang = k * 6.28 / 14
                    rr = 80 * q / 0.6
                    sx, sy = rx + rr * math.cos(ang), ry + rr * math.sin(ang) + 40 * q
                    d.ellipse([sx - 4, sy - 4, sx + 4, sy + 4], fill=rgba(WHITE, a * (1 - q / 0.6)))

def art_toll(img, d, t, dur, a):
    hz = 860
    layer = Image.new("RGBA", (900, 700), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ship(ld, 120, 420, 1.0, 1.0, lights=t < 2.5)
    p = ramp(t, 0.3, dur - 0.8)
    rot = layer.rotate(-(10 + 25 * p), resample=Image.BICUBIC, center=(450, 420))
    if a < 1:
        al = rot.getchannel("A").point(lambda v: int(v * a)); rot.putalpha(al)
    img.paste(rot, (int(W / 2 - 450), int(hz - 420 + 200 * p)), rot)
    d.rectangle([0, hz, W, 1010], fill=rgba(SEA, 1.0 * a))
    sea(d, hz, a)
    n = int(1500 * ramp(t, 0.6, 3.0))
    ctext(d, W / 2, 470, f"{n:,}+", F_STAT, WHITE, a)
    ctext(d, W / 2, 570, "PEOPLE DIED", F_SMALL, MUTED, a)

CHAIN = ["Speed", "Ignored warnings", "No binoculars", "Seen too late", "Weak rivets", "Short bulkheads", "Too few lifeboats"]
def art_outro(img, d, t, dur, a):
    for i, s in enumerate(CHAIN):
        k = ramp(t, 0.2 + i * 0.25, 0.6 + i * 0.25) * a
        y = 330 + i * 92
        d.ellipse([MX + 40, y - 30, MX + 100, y + 30], outline=rgba(AMBER, k), width=6)
        d.text((MX + 70, y), str(i + 1), font=F_SMALL, fill=rgba(AMBER, k), anchor="mm")
        if i < len(CHAIN) - 1:
            d.line([(MX + 70, y + 32), (MX + 70, y + 60)], fill=rgba(AMBER, k * 0.6), width=4)
        d.text((MX + 140, y), s, font=F_BODY, fill=rgba(WHITE, k), anchor="lm")

# ---------- script ----------
S = [
    dict(dur=6.5, n=0, art=art_intro, kick="APRIL 14, 1912  ·  NORTH ATLANTIC",
         head="Everyone blames the iceberg.",
         body="But the iceberg was only the last link in a chain of seven failures."),
    dict(dur=8, n=1, art=art_speed, kick="FAILURE 1  ·  SPEED",
         head="Full speed into an ice field",
         body="Titanic ran at about 22 knots, at night, through waters she'd been warned were full of ice. Standard practice: keep speed and trust the lookouts."),
    dict(dur=9, n=2, art=art_warnings, kick="FAILURE 2  ·  WARNINGS",
         head="Six ice warnings in one day",
         body="The radio operators were swamped with passengers' private messages. A warning of ice dead ahead never reached the bridge."),
    dict(dur=8, n=3, art=art_binoculars, kick="FAILURE 3  ·  NO BINOCULARS",
         head="The key was left behind",
         body="An officer was moved off the crew just before sailing and kept the key to the binocular locker. The lookouts scanned the dark by eye."),
    dict(dur=8.5, n=4, art=art_late, kick="FAILURE 4  ·  SEEN TOO LATE",
         head="Spotted 37 seconds out",
         body="No moon, a sea flat as glass, no waves breaking at the iceberg's base. At 11:40 pm the bell rang. The ship turned enough to scrape, not miss."),
    dict(dur=8.5, n=5, art=art_rivets, kick="FAILURE 5  ·  WEAK RIVETS",
         head="No giant gash. Just popped seams.",
         body="In the curved bow, workers hand-hammered iron rivets, some full of slag. Under strain their heads snapped and plates sprang apart: about 12 sq ft of openings."),
    dict(dur=9.5, n=6, art=art_bulkheads, kick="FAILURE 6  ·  SHORT BULKHEADS",
         head="Watertight, but not to the top",
         body="She could float with four compartments flooded. The iceberg opened five. As the bow sank, water spilled over each wall, like an ice-cube tray."),
    dict(dur=9, n=7, art=art_lifeboats, kick="FAILURE 7  ·  LIFEBOATS",
         head="Seats for barely half",
         body="20 boats for 2,224 people, and that was legal. The first boat lowered carried about 28 people. It had room for 65."),
    dict(dur=8.5, n=7, art=art_californian, kick="AND ONE MORE",
         head="Help was in sight",
         body="The Californian sat stopped, maybe 10 to 20 miles away. Her crew saw rockets. Her radio operator had gone to bed."),
    dict(dur=8, n=7, art=art_toll, kick="2:20 AM  ·  APRIL 15, 1912",
         head="Gone in 2 hours 40 minutes",
         body="Rescue ship Carpathia, 58 miles away, arrived after dawn. Only about 710 people survived."),
    dict(dur=10, n=7, art=art_outro, kick="WHY IT REALLY SANK",
         head="Not one mistake. A chain.",
         body="It changed the sea for good: lifeboats for all, 24-hour radio watch, and an Ice Patrol that still tracks icebergs today."),
]

import soundfile as _sf, os as _os
_ND = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "narr")
LEAD, TAIL = 0.5, 1.1
for _i, _sc in enumerate(S):
    _sc["dur"] = round((LEAD + _sf.info(f"{_ND}/{_i:02d}.wav").duration + TAIL) * 30) / 30

def draw_frame(sc, t, img):
    d = ImageDraw.Draw(img, "RGBA")
    dur = sc["dur"]
    a = clamp(t / 0.35) * clamp((dur - t) / 0.35)
    # stars (twinkle)
    for (x, y, r, ph) in STARS:
        tw = 0.35 + 0.65 * (0.5 + 0.5 * math.sin(ph + (gt[0]) * 1.7))
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, int(110 * tw)))
    sc["art"](img, d, t, dur, a)
    # failure chain progress (stays visible across scenes, no fade)
    n = sc["n"]
    if n:
        sp = 74
        x0 = W / 2 - 3 * sp
        for i in range(7):
            x = x0 + i * sp
            on = i < n
            if i < 6: d.line([(x + 16, 170), (x + sp - 16, 170)], fill=(70, 82, 104, 255), width=3)
            if on:
                d.ellipse([x - 13, 157, x + 13, 183], fill=AMBER + (255,))
            else:
                d.ellipse([x - 13, 157, x + 13, 183], outline=(70, 82, 104, 255), width=3)
        d.text((W / 2, 225), f"{n} OF 7 FAILURES", font=F_TINY, fill=MUTED + (255,), anchor="mm")
    # text block
    y = 1150
    k = ramp(t, 0.15, 0.6) * a
    d.text((MX, y), sc["kick"], font=F_KICK, fill=rgba(AMBER, k))
    y += 70
    k = ramp(t, 0.35, 0.95) * a
    for line in wrap(sc["head"], F_HEAD, W - 2 * MX):
        d.text((MX, y + 24 * (1 - k)), line, font=F_HEAD, fill=rgba(WHITE, k))
        y += 98
    y += 26
    k = ramp(t, 0.8, 1.4) * a
    for line in wrap(sc["body"], F_BODY, W - 2 * MX):
        d.text((MX, y + 16 * (1 - k)), line, font=F_BODY, fill=rgba(MUTED, k))
        y += 60
    d.text((W / 2, 1830), "WHY THE TITANIC REALLY SANK", font=F_TINY, fill=(90, 104, 128, 255), anchor="mm")

gt = [0.0]
def render():
    total = sum(s["dur"] for s in S)
    if PREVIEW:
        for i, sc in enumerate(S):
            gt[0] = 0
            img = bg.copy(); draw_frame(sc, sc["dur"] * 0.6, img)
            img.save(f"{OUT}/scene{i:02d}.png")
        return
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                           "-crf", "20", "-pix_fmt", "yuv420p", OUT], stdin=subprocess.PIPE)
    for sc in S:
        for f in range(int(sc["dur"] * FPS)):
            t = f / FPS
            gt[0] += 1 / FPS
            img = bg.copy()
            draw_frame(sc, t, img)
            ff.stdin.write(img.tobytes())
    ff.stdin.close(); ff.wait()
    print("duration", total)

render()

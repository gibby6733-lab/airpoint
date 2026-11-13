"""YouTube banner 2560x1440. Text and logo stay inside the 1546x423 safe area (visible on every device)."""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
W, H = 2560, 1440
SX0, SY0, SX1, SY1 = (W - 1546) // 2, (H - 423) // 2, (W + 1546) // 2, (H + 423) // 2
YEL, RED, ICE, ICE2 = (255, 214, 40), (226, 38, 38), (226, 240, 252), (150, 192, 228)
F = "/usr/share/fonts/opentype/inter/"

y = np.arange(H, dtype=np.float32)[:, None]
k = np.clip(y / (H * 0.62), 0, 1)
sky = np.array((6, 10, 24)) * (1 - k[..., None]) + np.array((28, 48, 84)) * k[..., None]
img = Image.fromarray(np.repeat(sky, W, 1).astype(np.uint8), "RGB")
d = ImageDraw.Draw(img, "RGBA")
rnd = random.Random(4)
for _ in range(260):
    x, yy, r = rnd.uniform(0, W), rnd.uniform(0, H * 0.6), rnd.uniform(1, 3.2)
    d.ellipse([x - r, yy - r, x + r, yy + r], fill=(255, 255, 255, rnd.randint(60, 200)))
WL = SY0 + 160
d.rectangle([0, WL, W, H], fill=(10, 30, 56))
for i in range(12):
    yy = WL + 22 + i * 46
    d.line([(0, yy), (W, yy)], fill=(26, 58, 92, 160), width=3)

# edge silhouettes (only fully visible on desktop/TV): liner left, airship + volcano right
def ship(x, y, s):
    P = lambda pts: [(x + a * s, y + b * s) for a, b in pts]
    d.polygon(P([(0, -70), (640, -70), (690, -95), (650, 0), (40, 0)]), fill=(4, 6, 12))
    d.polygon(P([(90, -70), (90, -108), (560, -108), (560, -70)]), fill=(4, 6, 12))
    for fx in (175, 270, 365, 460):
        d.polygon(P([(fx, -108), (fx + 6, -215), (fx + 52, -215), (fx + 46, -108)]), fill=(14, 12, 12))
    for i in range(24):
        if i % 4:
            cx, cy = x + (110 + i * 21) * s, y - 50 * s
            d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(255, 214, 140, 220))
ship(60, WL, 0.75)
d.polygon([(2050, WL), (2290, WL - 300), (2340, WL - 310), (2560, WL - 120), (2560, WL)], fill=(16, 18, 26))
for i in range(10):
    q = i / 9; r = 30 + q * 90
    d.ellipse([2310 - r + 20 * math.sin(i), WL - 330 - q * 260 - r * 0.6, 2310 + r, WL - 330 - q * 260 + r * 0.6], fill=(40, 40, 48, 200))
ax, ay = 2140, 230
d.ellipse([ax - 260, ay - 50, ax + 260, ay + 50], fill=(150, 152, 160, 200))
d.polygon([(ax - 200, ay - 20), (ax - 280, ay - 90), (ax - 300, ay - 80), (ax - 250, ay)], fill=(110, 112, 120, 200))

# logo (iceberg + magnifier), left side of the safe area
cx, wl, Ls = SX0 + 175, WL, 0.22
_tip = [(cx - 190, wl), (cx - 120, wl - 120), (cx - 50, wl - 150), (cx + 5, wl - 290), (cx + 60, wl - 210), (cx + 115, wl - 170), (cx + 200, wl)]
T = lambda pts: [(cx + (x - cx) * Ls / 0.48 * 0.48 * 2.1 if False else cx + (x - cx) * Ls * 2.1, wl + (y - wl) * Ls * 2.1) for x, y in pts]
tip = T(_tip)
d.polygon(tip, fill=ICE)
d.polygon(T([(cx + 5, wl - 290), (cx + 60, wl - 210), (cx + 115, wl - 170), (cx + 200, wl), (cx + 30, wl)]), fill=ICE2)
_under = [(cx - 210, wl), (cx + 220, wl), (cx + 340, wl + 190), (cx + 260, wl + 460), (cx + 30, wl + 540), (cx - 230, wl + 470), (cx - 360, wl + 210)]
under = T(_under)
d.polygon(under, fill=(30, 74, 118))
lx, ly, lr = cx + 50 * Ls * 2.1, wl + 210 * Ls * 2.1, 165 * Ls * 2.1
d.ellipse([lx - lr, ly - lr, lx + lr, ly + lr], fill=(120, 190, 240))
d.ellipse([lx - lr, ly - lr, lx + lr, ly + lr], outline=YEL, width=int(44 * Ls * 2.1))
a = math.radians(45)
x0, y0 = lx + (lr + 8) * math.cos(a), ly + (lr + 15) * math.sin(a)
x1, y1 = lx + (lr + 210 * Ls * 2.1) * math.cos(a), ly + (lr + 210 * Ls * 2.1) * math.sin(a)
d.line([(x0, y0), (x1, y1)], fill=YEL, width=int(68 * Ls * 2.1))

# wordmark centered in the safe area (to the right of the logo)
tx = SX0 + 400
f_tag = ImageFont.truetype(F + "Inter-Bold.otf", 34)
f_big = ImageFont.truetype(F + "Inter-ExtraBold.otf", 116)
f_sub = ImageFont.truetype(F + "Inter-SemiBold.otf", 40)
tag = "HISTORY'S BIGGEST DISASTERS"
tw = f_tag.getlength(tag)
d.rounded_rectangle([tx, SY0 + 40, tx + tw + 56, SY0 + 104], 32, fill=RED)
d.text((tx + 28, SY0 + 72), tag, font=f_tag, fill=(255, 255, 255), anchor="lm")
d.text((tx - 6, SY0 + 190), "THE REAL", font=f_big, fill=(255, 255, 255), anchor="lm", stroke_width=4, stroke_fill=(0, 0, 0))
w1 = f_big.getlength("THE REAL ")
d.text((tx - 6 + w1, SY0 + 190), "REASON", font=f_big, fill=YEL, anchor="lm", stroke_width=4, stroke_fill=(0, 0, 0))
d.text((tx, SY0 + 300), "Why it really happened, in 60 seconds.", font=f_sub, fill=(205, 218, 236), anchor="lm")
d.text((tx, SY0 + 356), "New Short every day", font=f_sub, fill=YEL, anchor="lm")
img.save("banner_youtube_2560x1440.png", optimize=True)

# preview with device crop guides
p = img.copy(); pd = ImageDraw.Draw(p)
pd.rectangle([SX0, SY0, SX1, SY1], outline=(0, 255, 120), width=6)
pd.rectangle([(W - 2560) // 2, (H - 423) // 2, W, (H + 423) // 2], outline=(255, 80, 200), width=4)
p.resize((1280, 720)).save("banner_preview_safe_area.png")
print("text right edge", max(tx + f_big.getlength("THE REAL REASON"), tx + f_sub.getlength("Why it really happened, in 60 seconds.")), "safe right", SX1)

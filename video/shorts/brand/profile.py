"""Profile pictures for The Real Reason (800x800, circle-safe). Drawn at 4x then downsampled."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S = 3200; OUT = 800
NAVY_A, NAVY_B = (8, 14, 30), (26, 44, 78)
YEL, RED, ICE, ICE2, DEEP = (255, 214, 40), (226, 38, 38), (226, 240, 252), (150, 192, 228), (40, 96, 150)

def bg():
    y, x = np.mgrid[0:S, 0:S].astype(np.float32)
    r = np.sqrt((x - S * 0.5) ** 2 + (y - S * 0.42) ** 2) / (S * 0.75)
    k = np.clip(r, 0, 1)[..., None]
    arr = np.array(NAVY_B) * (1 - k) + np.array(NAVY_A) * k
    return Image.fromarray(arr.astype(np.uint8), "RGB")

def save(img, name):
    img = img.resize((OUT, OUT), Image.LANCZOS); img.save(name, optimize=True)
    # circle preview
    m = Image.new("L", (OUT, OUT), 0); ImageDraw.Draw(m).ellipse([0, 0, OUT, OUT], fill=255)
    p = Image.new("RGB", (OUT, OUT), (255, 255, 255)); p.paste(img, (0, 0), m); return p

# A: iceberg under a magnifying glass ("the real reason is below the surface")
def option_a():
    img = bg(); d = ImageDraw.Draw(img)
    wl = S * 0.47
    d.rectangle([0, wl, S, S], fill=(10, 34, 62))
    for i in range(6):
        y = wl + 90 + i * 150
        d.line([(0, y), (S, y)], fill=(22, 56, 92), width=14)
    cx = S * 0.47
    tip = [(cx - 430, wl), (cx - 280, wl - 260), (cx - 120, wl - 330), (cx + 10, wl - 640), (cx + 130, wl - 470), (cx + 260, wl - 380), (cx + 450, wl)]
    d.polygon(tip, fill=ICE)
    d.polygon([(cx + 10, wl - 640), (cx + 130, wl - 470), (cx + 260, wl - 380), (cx + 450, wl), (cx + 60, wl)], fill=ICE2)
    under = [(cx - 470, wl), (cx + 490, wl), (cx + 780, wl + 420), (cx + 600, wl + 1050), (cx + 60, wl + 1250), (cx - 520, wl + 1080), (cx - 820, wl + 480)]
    d.polygon(under, fill=(30, 74, 118))
    # lens reveals the hidden part brightly
    lx, ly, lr = cx + 120, wl + 560, 560
    lens = Image.new("L", (S, S), 0); ImageDraw.Draw(lens).ellipse([lx - lr, ly - lr, lx + lr, ly + lr], fill=255)
    bright = Image.new("RGB", (S, S), (16, 52, 90)); bd = ImageDraw.Draw(bright)
    bd.polygon(under, fill=(120, 190, 240)); bd.polygon(tip, fill=ICE)
    bd.polygon([(cx - 470, wl), (cx + 60, wl), (cx - 200, wl + 1150), (cx - 520, wl + 1080), (cx - 820, wl + 480)], fill=(160, 214, 250))
    img.paste(bright, (0, 0), lens)
    d = ImageDraw.Draw(img)
    d.ellipse([lx - lr, ly - lr, lx + lr, ly + lr], outline=YEL, width=150)
    a = math.radians(45); r0 = lr + 60
    x0, y0 = lx + r0 * math.cos(a), ly + r0 * math.sin(a)
    x1, y1 = lx + (lr + 720) * math.cos(a), ly + (lr + 720) * math.sin(a)
    d.line([(x0, y0), (x1, y1)], fill=YEL, width=230)
    d.ellipse([x1 - 115, y1 - 115, x1 + 115, y1 + 115], fill=YEL)
    d.arc([lx - lr + 170, ly - lr + 170, lx + lr - 170, ly + lr - 170], 200, 250, fill=(255, 255, 255), width=60)
    return img

# B: bold monogram with red "reason" bar
def option_b():
    img = bg(); d = ImageDraw.Draw(img)
    f = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf", 1500)
    d.text((S / 2 + 20, S * 0.47), "RR", font=f, fill=(255, 255, 255), anchor="mm")
    d.text((S / 2 + 20, S * 0.47), "R", font=f, fill=YEL, anchor="rm")
    d.rounded_rectangle([S * 0.24, S * 0.70, S * 0.76, S * 0.76], 60, fill=RED)
    return img

# C: warning triangle with a question mark
def option_c():
    img = bg(); d = ImageDraw.Draw(img)
    cx, cy, R = S / 2, S * 0.54, 1250
    pts = [(cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a))) for a in (-90, 30, 150)]
    d.polygon(pts, fill=YEL)
    inner = [(cx + (R - 260) * math.cos(math.radians(a)), cy + 40 + (R - 260) * math.sin(math.radians(a))) for a in (-90, 30, 150)]
    d.polygon(inner, fill=(14, 22, 40))
    f = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf", 1150)
    d.text((cx, cy + 180), "?", font=f, fill=YEL, anchor="mm")
    return img

prev = Image.new("RGB", (OUT * 3 + 80, OUT + 40), (255, 255, 255))
for i, (fn, name) in enumerate([(option_a, "profile_A_iceberg.png"), (option_b, "profile_B_monogram.png"), (option_c, "profile_C_warning.png")]):
    prev.paste(save(fn(), name), (20 + i * (OUT + 20), 20))
prev.save("profile_preview_circles.png")

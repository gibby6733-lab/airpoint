"""Thumbnails / covers, 1080x1920: python3 thumbs.py"""
from PIL import Image, ImageDraw
import engine as E
from scripts import VIDEOS
CLIMAX = dict(titanic=1, hindenburg=2, chernobyl=2, challenger=2, tacoma=2, molasses=1, pompeii=1)
for v in VIDEOS:
    th = v["theme"]; img = E.make_bg(th); d = ImageDraw.Draw(img, "RGBA")
    E.HEROES[th](d, E.Cam(540, 1230 + E.YOFF.get(th, 0) * 0.6, 1.12), 2.0, CLIMAX[th], 0.7)
    E.particles(d, E.THEMES[th]["part"], 1.0)
    img.paste((0, 0, 0), (0, 0, E.W, E.H), E.VIG)
    import numpy as np
    m = np.clip(1 - np.arange(E.H)[:, None] / 1250.0, 0, 1) ** 0.8 * 120
    img.paste((0, 0, 0), (0, 0, E.W, E.H), Image.fromarray(np.repeat(m, E.W, 1).astype("uint8"), "L"))
    tag = "THE REAL REASON"
    tw = E.F_TAG.getlength(tag)
    d.rounded_rectangle([540 - tw / 2 - 28, 360, 540 + tw / 2 + 28, 424], 32, fill=(220, 30, 30, 255))
    d.text((540, 392), tag, font=E.F_TAG, fill=(255, 255, 255), anchor="mm")
    y = 560
    for i, line in enumerate(v["thumb"]):
        f = E.F_TH
        while f.getlength(line) > 990: f = f.font_variant(size=f.size - 6)
        col = (255, 222, 40) if i == v["thumb_hi"] else (255, 255, 255)
        d.text((540, y), line, font=f, fill=col, anchor="mm", stroke_width=12, stroke_fill=(0, 0, 0))
        y += 162
    img.save(f"out/{v['slug']}_thumbnail.png", optimize=True)
    print(v["slug"])

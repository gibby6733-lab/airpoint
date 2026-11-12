"""Daily video stats tracker for a series' #video-stats Discord channel.

The data lives IN the channel (routines run in fresh clones and can't keep files): every logged entry is a bot message
ending in a hidden-ish data line `-# data: {...}`. The chart and summary are rebuilt from those lines every time.

usage:
  python3 stats.py log  <key> --day N --platform tiktok views=4736 likes=516 comments=225 shares=7 [saves=.. followers=..]
  python3 stats.py post <key>            # rebuild chart image + summary, replace the previous chart message
  python3 stats.py show <key>            # print the table (no posting)
key = channels.json key of the stats channel (possums_stats).
Logging the same day + platform again overwrites the older numbers (the newest message wins).
"""
import io, json, os, re, sys, uuid, urllib.request
from PIL import Image, ImageDraw, ImageFont

here = os.path.dirname(os.path.abspath(__file__))
API = "https://discord.com/api/v10"
HDR = {"Authorization": "Bot proxy-injected", "User-Agent": "DiscordBot (daily-video-poster, 1.0)"}
F = "/usr/share/fonts/opentype/inter/Inter-{}.otf"
def font(w, s): return ImageFont.truetype(F.format(w), s)
FIELDS = ["views", "likes", "comments", "shares", "saves", "followers"]
NAMES = {"possums_stats": "MUDVILLE POSSUMS"}

def call(method, path, body=None, raw=None, ctype="application/json"):
    req = urllib.request.Request(API + path, method=method, headers={**HDR, **({"Content-Type": ctype} if (body is not None or raw) else {})},
                                 data=raw if raw is not None else (json.dumps(body).encode() if body is not None else None))
    with urllib.request.urlopen(req, timeout=60) as r:
        t = r.read(); return json.loads(t) if t else {}

def history(ch):
    out, before = [], None
    for _ in range(10):
        page = call("GET", f"/channels/{ch}/messages?limit=100" + (f"&before={before}" if before else ""))
        out += page
        if len(page) < 100: break
        before = page[-1]["id"]
    return sorted(out, key=lambda m: int(m["id"]))

def data(msgs):
    rows = {}
    for m in msgs:
        if not m["author"].get("bot"): continue
        mt = re.search(r"-# data: (\{.*\})", m.get("content", ""))
        if mt:
            d = json.loads(mt.group(1)); rows[(d["day"], d["platform"])] = d
    return rows

def fmt(n): return "–" if n is None else (f"{n / 1e6:.1f}M" if n >= 1e6 else f"{n / 1e3:.1f}K" if n >= 1e4 else f"{n:,}")

def log(key, day, platform, vals):
    ch = json.load(open(os.path.join(here, "channels.json")))[key]
    d = {"day": day, "platform": platform, **vals}
    parts = [f"{k} **{fmt(vals[k])}**" for k in FIELDS if k in vals]
    emoji = {"tiktok": "🎵", "instagram": "📸", "youtube": "▶️"}.get(platform, "📊")
    txt = f"✅ Logged **Day {day}** {emoji} {platform.title()}: " + " • ".join(parts) + f"\n-# data: {json.dumps(d)}"
    print("logged", call("POST", f"/channels/{ch}/messages", {"content": txt})["id"])

def chart(name, rows):
    days = sorted({d for d, _ in rows}); plats = sorted({p for _, p in rows}, key=lambda p: ["tiktok", "instagram", "youtube"].index(p) if p in ["tiktok", "instagram", "youtube"] else 9)
    COL = {"tiktok": (37, 244, 238), "instagram": (225, 48, 108), "youtube": (255, 60, 60)}
    W, H = 1600, 1000; im = Image.new("RGB", (W, H), (14, 16, 24)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((40, 30, W - 40, 150), 30, fill=(24, 28, 40), outline=(232, 180, 60), width=5)
    d.text((80, 52), name, font=font("Black", 56), fill=(255, 255, 255)); d.text((80, 112), "DAILY VIDEO STATS", font=font("Bold", 28), fill=(232, 180, 60))
    lx = W - 80
    for p in reversed(plats):
        w = d.textlength(p.upper(), font=font("Bold", 30)); lx -= w; d.text((lx, 75), p.upper(), font=font("Bold", 30), fill=COL.get(p, (200, 200, 200))); lx -= 46
        d.rounded_rectangle((lx, 80, lx + 30, 104), 6, fill=COL.get(p, (200, 200, 200))); lx -= 40
    panels = [("VIEWS", "views"), ("LIKES  (= $ for the team)", "likes")]
    for pi, (title, f) in enumerate(panels):
        x0, y0, x1, y1 = 110, 210 + pi * 390, W - 70, 520 + pi * 390
        d.text((x0 - 60, y0 - 44), title, font=font("Black", 32), fill=(220, 224, 236))
        vals = [rows[(dd, p)].get(f) for dd in days for p in plats if (dd, p) in rows and rows[(dd, p)].get(f) is not None]
        top = max(vals) if vals else 1; top = top * 1.15 or 1
        d.line([(x0, y1), (x1, y1)], fill=(70, 74, 90), width=3)
        for q in range(1, 4):
            yy = y1 - (y1 - y0) * q / 3; d.line([(x0, yy), (x1, yy)], fill=(34, 38, 52), width=2); d.text((x0 - 95, yy - 14), fmt(int(top * q / 3)), font=font("Bold", 22), fill=(120, 126, 146))
        n = max(1, len(days)); gw = (x1 - x0) / n; bw = min(90, (gw - 30) / max(1, len(plats)))
        for i, dd in enumerate(days):
            cx = x0 + gw * i + gw / 2; d.text((cx - d.textlength(f"DAY {dd}", font=font("Bold", 24)) / 2, y1 + 10), f"DAY {dd}", font=font("Bold", 24), fill=(170, 176, 196))
            for j, p in enumerate(plats):
                v = rows.get((dd, p), {}).get(f)
                if v is None: continue
                bx = cx - bw * len(plats) / 2 + j * bw; h = (y1 - y0) * v / top
                d.rounded_rectangle((bx + 4, y1 - h, bx + bw - 4, y1), 8, fill=COL.get(p, (200, 200, 200)))
                lab = fmt(v); tw = d.textlength(lab, font=font("Bold", 22)); d.text((bx + bw / 2 - tw / 2, y1 - h - 30), lab, font=font("Bold", 22), fill=(255, 255, 255))
    return im

def summary(name, rows):
    days = sorted({d for d, _ in rows})
    if not days: return f"📊 **{name.title()} stats**: nothing logged yet."
    def tot(dd, f): return sum((rows.get((dd, p), {}).get(f) or 0) for p in ["tiktok", "instagram", "youtube"])
    last = days[-1]; prev = days[-2] if len(days) > 1 else None
    lines = [f"📊 **{name.title()} — stats after Day {last}**"]
    for f, e in [("views", "👀"), ("likes", "❤️"), ("comments", "💬"), ("shares", "🔁"), ("followers", "👥")]:
        v = tot(last, f)
        if not v: continue
        ch = ""
        if prev and tot(prev, f):
            pc = (v - tot(prev, f)) / tot(prev, f) * 100; ch = f" ({'⬆️' if pc >= 0 else '⬇️'} {abs(pc):.0f}% vs Day {prev})"
        lines.append(f"{e} {f.title()}: **{fmt(v)}**{ch}")
    best = max(days, key=lambda dd: tot(dd, "views") or tot(dd, "likes"))
    lines.append(f"🏆 Best day so far: **Day {best}** • 💵 Total likes (all days): **{fmt(sum(tot(dd, 'likes') for dd in days))}**")
    return "\n".join(lines)

def post(key):
    ch = json.load(open(os.path.join(here, "channels.json")))[key]; msgs = history(ch); rows = data(msgs); name = NAMES.get(key, key.upper())
    im = chart(name, rows); buf = io.BytesIO(); im.save(buf, "PNG"); b = uuid.uuid4().hex
    for m in msgs:  # keep only the newest chart in the channel
        if m["author"].get("bot") and any(a.get("filename") == "stats.png" for a in m.get("attachments", [])): call("DELETE", f"/channels/{ch}/messages/{m['id']}")
    body = b"".join([f"--{b}\r\nContent-Disposition: form-data; name=\"payload_json\"\r\nContent-Type: application/json\r\n\r\n".encode(),
        json.dumps({"content": summary(name, rows), "attachments": [{"id": 0, "filename": "stats.png"}]}).encode(), b"\r\n",
        f"--{b}\r\nContent-Disposition: form-data; name=\"files[0]\"; filename=\"stats.png\"\r\nContent-Type: image/png\r\n\r\n".encode(), buf.getvalue(), f"\r\n--{b}--\r\n".encode()])
    print("chart", call("POST", f"/channels/{ch}/messages", raw=body, ctype=f"multipart/form-data; boundary={b}")["id"])

if __name__ == "__main__":
    cmd, key = sys.argv[1], sys.argv[2]
    if cmd == "log":
        a = sys.argv[3:]; day = int(a[a.index("--day") + 1]); plat = a[a.index("--platform") + 1].lower()
        vals = {k: int(float(v.replace(",", ""))) for k, v in (x.split("=", 1) for x in a if "=" in x) if k in FIELDS}
        log(key, day, plat, vals)
    elif cmd == "post": post(key)
    elif cmd == "show":
        ch = json.load(open(os.path.join(here, "channels.json")))[key]
        for (dd, p), v in sorted(data(history(ch)).items()): print(dd, p, v)

"""Master posting schedule for the #schedule channel: one month calendar showing which videos go out each day,
with finished days crossed off, plus a short text list (today + the next days, past days struck through).

usage: python3 schedule_post.py [--dry-run]      (the daily 6 AM routine runs it)
Each run deletes the bot's previous schedule messages in the channel and posts a fresh image + list.
What goes out on which day comes from schedule.json:
  - "history": what was actually posted on past dates (edit it if a day changes)
  - "series":  the daily plan from "from" onwards (Day number counts up from "first_day"; "last_day" stops it)
A day counts as over (crossed off) once it is before today in New York time.
"""
import calendar, datetime, io, json, os, sys, uuid, urllib.request
from zoneinfo import ZoneInfo
from PIL import Image, ImageDraw, ImageFont

here = os.path.dirname(os.path.abspath(__file__))
TZ = ZoneInfo("America/New_York")
API = "https://discord.com/api/v10"
HDR = {"Authorization": "Bot proxy-injected", "User-Agent": "DiscordBot (daily-video-poster, 1.0)"}
F = "/usr/share/fonts/opentype/inter/Inter-{}.otf"
def font(w, s): return ImageFont.truetype(F.format(w), s)
def D(s): return datetime.date.fromisoformat(s)

def call(method, path, body=None, raw=None, ctype="application/json"):
    req = urllib.request.Request(API + path, method=method, headers={**HDR, **({"Content-Type": ctype} if (body is not None or raw) else {})},
                                 data=raw if raw is not None else (json.dumps(body).encode() if body is not None else None))
    with urllib.request.urlopen(req, timeout=60) as r:
        t = r.read(); return json.loads(t) if t else {}

def plan():
    cfg = json.load(open(os.path.join(here, "schedule.json")))
    S = {s["key"]: s for s in cfg["series"]}
    def videos(day):
        h = cfg["history"].get(day.isoformat())
        if h is not None: return [(S[k], label) for k, label in h]
        out = []
        for s in cfg["series"]:
            if day < D(s["from"]): continue
            n = s.get("first_day", 1) + (day - D(s["from"])).days
            if s.get("last_day") and n > s["last_day"]: continue
            out.append((s, s["label"].format(n=n)))
        return out
    return cfg, videos

def draw(today, videos, cfg):
    y0, m0 = today.year, today.month; cal = calendar.Calendar(firstweekday=6).monthdatescalendar(y0, m0)
    W, CW, CH, TOP = 1600, 214, 230, 330; H = TOP + len(cal) * CH + 210
    im = Image.new("RGB", (W, H), (14, 16, 24)); d = ImageDraw.Draw(im)
    for y in range(H): k = y / H; d.line([(0, y), (W, y)], fill=(int(14 + 12 * k), int(16 + 10 * k), int(24 + 20 * k)))
    d.rounded_rectangle((40, 36, W - 40, 236), 36, fill=(24, 28, 40), outline=(255, 214, 80), width=5)
    d.text((80, 62), "POSTING SCHEDULE", font=font("Black", 64), fill=(255, 255, 255)); d.text((80, 144), "WHAT GOES OUT EACH DAY", font=font("Bold", 38), fill=(255, 214, 80))
    mo = today.strftime("%B %Y").upper(); d.text((W - 80 - d.textlength(mo, font=font("Black", 64)), 62), mo, font=font("Black", 64), fill=(255, 255, 255))
    x0 = (W - 7 * CW) // 2
    for i, wd in enumerate(["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]):
        tw = d.textlength(wd, font=font("Bold", 30)); d.text((x0 + i * CW + CW / 2 - tw / 2, 268), wd, font=font("Bold", 30), fill=(150, 156, 176))
    for r, week in enumerate(cal):
        for c, day in enumerate(week):
            x, y = x0 + c * CW, TOP + r * CH; box = (x + 6, y + 6, x + CW - 6, y + CH - 6)
            if day.month != m0: d.rounded_rectangle(box, 22, fill=(20, 22, 32)); continue
            past, now = day < today, day == today
            if past and day < D(min(cfg['history'] or [today.isoformat()])): d.rounded_rectangle(box, 22, fill=(22, 24, 34)); d.text((x + 22, y + 16), str(day.day), font=font('Black', 40), fill=(70, 74, 88)); continue
            d.rounded_rectangle(box, 22, fill=(30, 34, 48) if not past else (24, 26, 34), outline=(255, 214, 80) if now else None, width=6 if now else 0)
            d.text((x + 22, y + 16), str(day.day), font=font("Black", 40), fill=(110, 114, 128) if past else (255, 255, 255))
            if now: d.text((x + CW - 22 - d.textlength("TODAY", font=font("Black", 24)), y + 26), "TODAY", font=font("Black", 24), fill=(255, 214, 80))
            for j, (s, label) in enumerate(videos(day)[:4]):
                py = y + 72 + j * 38; col = tuple(s["color"]) if not past else tuple(int(v * .45) + 30 for v in s["color"])
                d.rounded_rectangle((x + 16, py, x + CW - 16, py + 32), 10, fill=col)
                f = font("Bold", 21); t = label
                while d.textlength(t, font=f) > CW - 52 and len(t) > 3: t = t[:-2] + "…"
                d.text((x + 26, py + 4), t, font=f, fill=(20, 20, 26))
            if past:  # crossed off
                d.line([(x + 18, y + 18), (x + CW - 18, y + CH - 18)], fill=(229, 72, 72), width=9); d.line([(x + CW - 18, y + 18), (x + 18, y + CH - 18)], fill=(229, 72, 72), width=9)
    ly = TOP + len(cal) * CH + 50; lx = 80
    for s in cfg["series"]:
        d.rounded_rectangle((lx, ly, lx + 40, ly + 40), 10, fill=tuple(s["color"])); d.text((lx + 54, ly + 2), s["name"], font=font("Bold", 32), fill=(230, 232, 240)); lx += 110 + d.textlength(s["name"], font=font("Bold", 32))
    d.line([(80, ly + 100), (130, ly + 150)], fill=(229, 72, 72), width=7); d.line([(130, ly + 100), (80, ly + 150)], fill=(229, 72, 72), width=7)
    d.text((150, ly + 105), "= day is over      Gold border = today      Posting time: " + cfg.get("post_time", "11:45 AM") + " ET", font=font("Bold", 32), fill=(170, 176, 196))
    return im

def text_list(today, videos, cfg):
    lines = [f"🗓️ **Posting schedule** (updates every morning; days get crossed off once they're over)"]
    for k in range(-2, 7):
        day = today + datetime.timedelta(days=k); vids = videos(day)
        what = " • ".join(f"{s['emoji']} {label}" for s, label in vids) or "nothing planned"
        name = day.strftime("%a %b ") + str(day.day)
        if k < 0: lines.append(f"~~{name}: {what}~~ ✅")
        elif k == 0: lines.append(f"👉 **TODAY {name}: {what}** ⏰ {cfg.get('post_time', '11:45 AM')}")
        else: lines.append(f"{name}: {what}")
    return "\n".join(lines)

def main():
    cfg, videos = plan(); today = datetime.datetime.now(TZ).date()
    im = draw(today, videos, cfg); txt = text_list(today, videos, cfg)
    if "--dry-run" in sys.argv:
        im.save(os.path.join(here, "schedule_preview.png")); print(txt); return
    ch = json.load(open(os.path.join(here, "channels.json")))["schedule"]
    for m in call("GET", f"/channels/{ch}/messages?limit=50"):
        if m["author"].get("bot"): call("DELETE", f"/channels/{ch}/messages/{m['id']}")
    buf = io.BytesIO(); im.save(buf, "PNG"); b = uuid.uuid4().hex
    body = b"".join([f"--{b}\r\nContent-Disposition: form-data; name=\"payload_json\"\r\nContent-Type: application/json\r\n\r\n".encode(),
        json.dumps({"content": txt, "attachments": [{"id": 0, "filename": "schedule.png"}]}).encode(), b"\r\n",
        f"--{b}\r\nContent-Disposition: form-data; name=\"files[0]\"; filename=\"schedule.png\"\r\nContent-Type: image/png\r\n\r\n".encode(), buf.getvalue(), f"\r\n--{b}--\r\n".encode()])
    print("schedule", call("POST", f"/channels/{ch}/messages", raw=body, ctype=f"multipart/form-data; boundary={b}")["id"])

if __name__ == "__main__": main()

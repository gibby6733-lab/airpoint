"""Posting calendar for a series' #posting-calendar channel.

usage: python3 calendar_post.py <football|apocalypse> [--image-only] [--dry-run]

Every run (the daily 6 AM routine runs it):
  1. posts today's checklist message ("Post the video at 11:45 AM") with a ✅ reaction pre-added, so checking a
     day off is one tap on ✅ (count goes to 2 = done). Past days can be checked off on their own message.
  2. re-draws the month calendar image (done days = green check, today highlighted, posted time on every day)
     and replaces the previous calendar image in the channel.
"""
import datetime, io, json, os, re, sys, uuid, urllib.request, urllib.error
from zoneinfo import ZoneInfo
from PIL import Image, ImageDraw, ImageFont

here = os.path.dirname(os.path.abspath(__file__))
SERIES = {
    "football": {"name": "MUDVILLE POSSUMS", "what": "the Mudville Possums video", "accent": (232, 180, 60), "accent2": (46, 125, 50), "emoji": "🏈"},
    "baseball": {"name": "CRABAPPLE RACCOONS", "what": "the Crabapple Raccoons video", "accent": (232, 120, 50), "accent2": (46, 125, 50), "emoji": "⚾"},
    "tenk": {"name": "$1 TO $10,000", "what": "today's $1 to $10K video", "accent": (143, 209, 138), "accent2": (46, 125, 50), "emoji": "💵"},
    "yourmove": {"name": "YOUR MOVE STUDIO", "what": "a new 10-min Your Move video with Claude", "accent": (255, 225, 74), "accent2": (46, 125, 50), "emoji": "🎬",
                 "time": "MAKE", "pill": "MAKE A NEW VIDEO EVERY DAY", "verb": "Make", "label": "NEW VIDEO"},
    "apocalypse": {"name": "ZOMBIE APOCALYPSE", "what": "today's zombie part", "accent": (220, 70, 60), "accent2": (124, 214, 124), "emoji": "🧟"},
}
POST_TIME, START = "11:45 AM", datetime.date(2026, 11, 11)   # tracking starts the day the calendar was made
TZ = ZoneInfo("America/New_York")
API = "https://discord.com/api/v10"
HDR = {"Authorization": "Bot proxy-injected", "User-Agent": "DiscordBot (daily-video-poster, 1.0)"}
F = "/usr/share/fonts/opentype/inter/Inter-{}.otf"
def font(w, s): return ImageFont.truetype(F.format(w), s)

def call(method, path, body=None, raw=None, ctype="application/json"):
    req = urllib.request.Request(API + path, method=method, headers={**HDR, **({"Content-Type": ctype} if (body is not None or raw) else {})},
                                 data=raw if raw is not None else (json.dumps(body).encode() if body is not None else None))
    with urllib.request.urlopen(req, timeout=60) as r:
        t = r.read(); return json.loads(t) if t else {}

def messages(ch):
    out, before = [], None
    for _ in range(4):
        page = call("GET", f"/channels/{ch}/messages?limit=100" + (f"&before={before}" if before else ""))
        out += page
        if len(page) < 100: break
        before = page[-1]["id"]
    return out

DAY_RE = re.compile(r"\((\d{4})-(\d{2})-(\d{2})\)")
def done_days(msgs):
    done = set()
    for m in msgs:
        mt = DAY_RE.search(m.get("content", ""))
        if not mt or not m["author"].get("bot"): continue
        for r in m.get("reactions", []):
            if r["emoji"].get("name") == "✅" and r["count"] - (1 if r.get("me") else 0) >= 1:
                done.add(datetime.date(*map(int, mt.groups())))
    return done

def rr(d, box, r, **kw): d.rounded_rectangle(box, r, **kw)
def check(d, cx, cy, s, col, w):
    d.line([(cx - s, cy), (cx - s * .3, cy + s * .7), (cx + s, cy - s * .8)], fill=col, width=w, joint="curve")

def draw(key, today, done):
    S = SERIES[key]; A, A2 = S["accent"], S["accent2"]
    first0 = today.replace(day=1); nd0 = ((first0.replace(month=first0.month % 12 + 1, year=first0.year + (first0.month == 12))) - first0).days
    rows = ((first0.weekday() + 1) % 7 + nd0 + 6) // 7
    W, H = 1600, 280 + 54 + rows * 200 + 200; im = Image.new("RGB", (W, H), (14, 16, 24)); d = ImageDraw.Draw(im)
    for y in range(H):  # soft vertical gradient
        k = y / H; d.line([(0, y), (W, y)], fill=(int(14 + 14 * k), int(16 + 10 * k), int(24 + 22 * k)))
    # header
    rr(d, (40, 36, W - 40, 236), 36, fill=(24, 28, 40), outline=A, width=5)
    d.text((80, 62), S["name"], font=font("Black", 64), fill=(255, 255, 255))
    d.text((80, 142), "POSTING CALENDAR", font=font("Bold", 40), fill=A)
    month = today.strftime("%B %Y").upper()
    mw = d.textlength(month, font=font("Black", 64)); d.text((W - 80 - mw, 62), month, font=font("Black", 64), fill=(255, 255, 255))
    # post-time pill with a little clock
    pill = S.get("pill", f"POST EVERY DAY  {POST_TIME} ET"); pw = d.textlength(pill, font=font("Bold", 36))
    rr(d, (W - 160 - pw, 138, W - 70, 200), 30, fill=A)
    cx, cy = W - 130 - pw, 169; d.ellipse((cx - 20, cy - 20, cx + 20, cy + 20), outline=(20, 20, 26), width=5); d.line([(cx, cy), (cx, cy - 12)], fill=(20, 20, 26), width=4); d.line([(cx, cy), (cx + 10, cy + 4)], fill=(20, 20, 26), width=4)
    d.text((W - 95 - pw, 146), pill, font=font("Bold", 36), fill=(20, 20, 26))
    # weekday row
    gx, gy, cw, ch, gap = 40, 280, (W - 80 - 6 * 14) / 7, 186, 14
    for i, wd in enumerate(["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]):
        x = gx + i * (cw + gap); tw = d.textlength(wd, font=font("Bold", 30)); d.text((x + cw / 2 - tw / 2, gy), wd, font=font("Bold", 30), fill=(150, 156, 176))
    first = today.replace(day=1); lead = (first.weekday() + 1) % 7
    ndays = ((first.replace(month=first.month % 12 + 1, year=first.year + (first.month == 12))) - first).days
    tracked = posted = 0
    for n in range(1, ndays + 1):
        day = first.replace(day=n); idx = lead + n - 1; col, row = idx % 7, idx // 7
        x0, y0 = gx + col * (cw + gap), gy + 54 + row * (ch + gap); x1, y1 = x0 + cw, y0 + ch
        active = day >= START; is_done = day in done; past = day < today
        if active and day <= today: tracked += 1
        if is_done: posted += 1
        if not active: fill, ol, numc = (22, 24, 32), None, (70, 74, 90)
        elif is_done: fill, ol, numc = A2, None, (255, 255, 255)
        elif day == today: fill, ol, numc = (34, 38, 54), A, (255, 255, 255)
        elif past: fill, ol, numc = (30, 30, 40), (120, 60, 60), (170, 120, 120)
        else: fill, ol, numc = (30, 34, 48), (52, 58, 78), (220, 224, 236)
        rr(d, (x0, y0, x1, y1), 26, fill=fill, outline=ol, width=6 if day == today else 3)
        d.text((x0 + 20, y0 + 14), str(n), font=font("Black", 46), fill=numc)
        if is_done:
            check(d, x1 - 62, y0 + 82, 36, (255, 255, 255), 14); d.text((x0 + 20, y1 - 46), "POSTED", font=font("Black", 26), fill=(255, 255, 255))
        elif active:
            d.text((x0 + 20, y1 - 82), "TODAY" if False else ("" if S.get("time") else "VIDEO"), font=font("Bold", 24), fill=(150, 156, 176) if day != today else A)
            d.text((x0 + 20, y1 - 52), S.get("label", POST_TIME), font=font("Black", 30), fill=(230, 232, 240) if not past else (170, 120, 120))
            if day == today:
                tw = d.textlength("TODAY", font=font("Black", 24)); rr(d, (x1 - tw - 44, y0 + 18, x1 - 16, y0 + 58), 18, fill=A); d.text((x1 - tw - 30, y0 + 22), "TODAY", font=font("Black", 24), fill=(20, 20, 26))
            elif past:
                d.text((x1 - 64, y0 + 14), "–", font=font("Black", 46), fill=(170, 120, 120))
    # progress bar + streak
    by = H - 160; rr(d, (40, by, W - 40, by + 110), 30, fill=(24, 28, 40), outline=(52, 58, 78), width=3)
    pct = posted / tracked if tracked else 0; rr(d, (70, by + 64, W - 70, by + 88), 12, fill=(44, 48, 64))
    if pct > 0: rr(d, (70, by + 64, 70 + (W - 140) * pct, by + 88), 12, fill=A2)
    streak, k = 0, today
    while k in done: streak += 1; k -= datetime.timedelta(days=1)
    if streak == 0:
        k = today - datetime.timedelta(days=1)
        while k in done: streak += 1; k -= datetime.timedelta(days=1)
    d.text((70, by + 14), f"{posted} / {tracked} DAYS POSTED", font=font("Black", 38), fill=(255, 255, 255))
    st = f"STREAK: {streak} DAY{'S' if streak != 1 else ''}"; sw = d.textlength(st, font=font("Black", 38)); d.text((W - 70 - sw, by + 14), st, font=font("Black", 38), fill=A)
    return im

def post_image(ch, im, text):
    buf = io.BytesIO(); im.save(buf, "PNG"); b = uuid.uuid4().hex
    body = b"".join([f"--{b}\r\nContent-Disposition: form-data; name=\"payload_json\"\r\nContent-Type: application/json\r\n\r\n".encode(),
        json.dumps({"content": text, "attachments": [{"id": 0, "filename": "calendar.png"}]}).encode(), b"\r\n",
        f"--{b}\r\nContent-Disposition: form-data; name=\"files[0]\"; filename=\"calendar.png\"\r\nContent-Type: image/png\r\n\r\n".encode(), buf.getvalue(), f"\r\n--{b}--\r\n".encode()])
    return call("POST", f"/channels/{ch}/messages", raw=body, ctype=f"multipart/form-data; boundary={b}")

if __name__ == "__main__":
    key = sys.argv[1]; S = SERIES[key]; dry = "--dry-run" in sys.argv
    ch = json.load(open(os.path.join(here, "channels.json")))[f"{key}_calendar"]
    today = datetime.datetime.now(TZ).date()
    msgs = [] if dry else messages(ch)
    if not dry and "--image-only" not in sys.argv:
        tag = f"({today.isoformat()})"
        if not any(tag in m.get("content", "") and m["author"].get("bot") for m in msgs):
            line2 = (f"{S['emoji']} {S['verb']} {S['what']} 🎥" if S.get("verb") else f"{S['emoji']} Post {S['what']} at **{POST_TIME}** ⏰")
            txt = f"📅 **{today.strftime('%A, %B')} {today.day}** {tag}\n{line2}\nTap ✅ when it's done 👇"
            m = call("POST", f"/channels/{ch}/messages", {"content": txt})
            call("PUT", f"/channels/{ch}/messages/{m['id']}/reactions/%E2%9C%85/@me")
            print("today's checklist:", m["id"]); msgs = messages(ch)
    done = done_days(msgs)
    im = draw(key, today, done)
    if dry:
        im.save(os.path.join(here, f"calendar_{key}.png")); print("wrote preview", f"calendar_{key}.png", "done:", sorted(done)); sys.exit(0)
    for m in msgs:  # replace the old calendar image so only the latest one is in the channel
        if m["author"].get("bot") and any(a.get("filename") == "calendar.png" for a in m.get("attachments", [])):
            call("DELETE", f"/channels/{ch}/messages/{m['id']}")
    m = post_image(ch, im, f"🗓️ **{S['name'].title()} — {today.strftime('%B')} posting calendar** (updates every morning) ✅ = posted")
    print("calendar image:", m["id"], "| done:", sorted(str(x) for x in done))

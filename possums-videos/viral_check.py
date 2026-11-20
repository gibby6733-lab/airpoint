"""Our own "viral check": scores a rendered short on the things that drive TikTok / Reels performance.

usage: python3 viral_check.py <episode_dir> [--png out.png] [--json]
Reads <dir>/episode.mp4 + <dir>/timeline.json (Possums / $1 to $10K / REALITY RELOADED "lines" or zombie "beats").
It is a checklist score, not a real prediction. Parts:
  hook, first frame, pacing, motion, drop-off risk (second by second), captions & talk speed, payoffs, open loops,
  length (+ TikTok's 1-minute pay rule), audio, ending (CTA + loop back), safe zones (TikTok / Instagram buttons + bars).
Compare it against the real numbers in #video-stats over time and tune the weights below.
"""
import json, os, re, subprocess, sys
import numpy as np

STAKES = re.compile(r"\d|dollar|\$|dead|kick|out|last|never|first|only|zero|million|thousand|hundred|day|minute|second|tomorrow|worst|broke|why|how|what if|\?", re.I)
CTA = re.compile(r"comment|vote|like|follow|poll|tomorrow|part \w+|which|would you|day \w+ starts|your choice|next|episode \w+ drops", re.I)
LOOPS = re.compile(r"\?|\b(but|then|until|wait|suddenly|what|why|who|how|if|unless|except|only|turns out|nobody|somebody|something|secret|mystery)\b", re.I)
# UI zones on a 1080x1920 frame: TikTok/Instagram caption + username (bottom), like/comment/share column (right),
# top bar ("Following | For You", Instagram back/camera, Story progress bar)
ZONES = {"bottom bar": (0, 1600, 1080, 1920), "right buttons": (960, 760, 1080, 1600), "top bar": (0, 0, 1080, 170)}

def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=width,height,r_frame_rate", "-of", "json", path], capture_output=True, text=True).stdout
    j = json.loads(out); v = next(s for s in j["streams"] if "width" in s)
    n, d = v["r_frame_rate"].split("/"); return float(j["format"]["duration"]), int(v["width"]), int(v["height"]), float(n) / float(d or 1)

def frames(path, fps=6, w=90, h=160, fmt="gray"):
    ch = 1 if fmt == "gray" else 3
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-vf", f"fps={fps},scale={w}:{h},format={fmt}", "-f", "rawvideo", "-"], capture_output=True).stdout
    a = np.frombuffer(raw, np.uint8).reshape(-1, h, w, ch).astype(np.float32); return a[..., 0] if ch == 1 else a

def frame_at(path, t, w=270, h=480):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", str(max(0, t)), "-i", path, "-frames:v", "1", "-vf", f"scale={w}:{h},format=rgb24", "-f", "rawvideo", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(h, w, 3).astype(np.float32) if raw else None

def loudness(path):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", err); return float(m[-1]) if m else None

def silences(path):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", "silencedetect=n=-40dB:d=1.2", "-f", "null", "-"], capture_output=True, text=True).stderr
    return [float(x) for x in re.findall(r"silence_duration: ([\d.]+)", err)]

def band(x, lo, hi, soft):  # 100 inside [lo, hi], falls off linearly over `soft` outside
    if lo <= x <= hi: return 100.0
    d = lo - x if x < lo else x - hi; return max(0.0, 100 - 100 * d / soft)

def text_mask(img):
    """Caption/stamp-like pixels: bright white or yellow text with a dark outline right next to it."""
    r, g, b = img[..., 0], img[..., 1], img[..., 2]; lum = .299 * r + .587 * g + .114 * b
    bright = ((r > 225) & (g > 225) & (b > 225)) | ((r > 225) & (g > 190) & (b < 130))
    dark = lum < 55; near = np.zeros_like(dark)
    for dy in (-2, 0, 2):
        for dx in (-2, 0, 2):
            near |= np.roll(np.roll(dark, dy, 0), dx, 1)
    return bright & near

def texty(mz):
    """True when a zone holds lettering: several rows with many on/off flips (letters), not one long outline or sill."""
    if mz.sum() < 25: return False
    flips = (np.diff(mz.astype(np.int8), axis=1) == 1).sum(axis=1)   # starts of bright runs per row
    return int((flips >= 4).sum()) >= 3

def fmt_t(s): return f"{int(s // 60)}:{int(s % 60):02d}"

def check(d):
    vid = os.path.join(d, "episode.mp4"); tl = json.load(open(os.path.join(d, "timeline.json")))
    lines = [l for l in (tl.get("beats") or tl.get("lines")) if l.get("text")]
    allb = tl.get("beats") or tl.get("lines")
    dur, W, H, fps = probe(vid); is_long = W > H
    fps_s = 6; F = frames(vid, fps_s); diff = np.abs(np.diff(F, axis=0)).mean(axis=(1, 2)) if len(F) > 1 else np.zeros(1)
    thr = max(18.0, 3 * float(np.median(diff))); cut_times, last = [], -99
    for i, x in enumerate(diff):   # a cut = a sudden big change, at most one per 1.2 s (falling confetti/money is not a cut)
        if x > thr and (i - last) / fps_s >= 1.2: cut_times.append((i + 1) / fps_s); last = i
    cuts = len(cut_times); motion = float(np.median(diff)); still = float((diff < .6).mean())
    first3 = diff[: 6 * 3].mean() if len(diff) else 0
    words = [w for l in lines for w in l.get("words", [])]
    first_word = min((w["s"] for w in words), default=dur)
    spoken = sum(max(0, l["end"] - l["start"]) for l in lines); wps = len(words) / max(1, spoken)
    hook = lines[0]["text"] if lines else ""; hook2 = " ".join(l["text"] for l in lines[:2])
    ending = " ".join(l["text"] for l in lines[-3:])
    lufs = loudness(vid); sil = silences(vid)
    # sound-effect / reveal moments (lines carry absolute sfx_times; zombie beats carry fractions of the beat)
    sfx_t = []
    for b in allb:
        if b.get("sfx_times"): sfx_t += [s for _, s in b["sfx_times"]]
        elif b.get("sfx") and "start" in b: sfx_t += [b["start"] + (f if isinstance(f, (int, float)) else 0) * (b["end"] - b["start"]) for _, f in b["sfx"]]
    events = sorted(set(round(x, 2) for x in sfx_t + cut_times))
    S, tips = {}, []

    # 1. HOOK (first 3 s): speech starts fast, stakes/numbers/question in the first line, motion right away, cold open
    S["Hook (first 3 s)"] = band(first_word, 0, .6, 1.5) * .35 + (100 if STAKES.search(hook) else 40 if STAKES.search(hook2) else 0) * .35 + min(100, first3 * 6) * .2 + (100 if any(l.get("cold") or l.get("rewind") for l in lines) or len(hook.split()) <= 12 else 60) * .1
    if S["Hook (first 3 s)"] < 75: tips.append(f"Hook: first words at {first_word:.1f}s — start talking by 0.5 s and put a number/stake in line 1 (\"{hook[:60]}\")")

    # 2. FIRST FRAME (the scroll-stopper): text on screen, bright, contrasty, colorful, already moving
    f0 = frame_at(vid, .35); ff = {}
    if f0 is not None:
        lum = .299 * f0[..., 0] + .587 * f0[..., 1] + .114 * f0[..., 2]; mx, mn = f0.max(axis=2), f0.min(axis=2)
        ff = {"text_px": int(text_mask(f0).sum()), "brightness": float(lum.mean()), "contrast": float(lum.std()), "saturation": float(((mx - mn) / (mx + 1)).mean())}
        mov = float(diff[:4].mean()) if len(diff) else 0
        S["First frame"] = (100 if ff["text_px"] > 120 else 50 if ff["text_px"] > 30 else 10) * .35 + band(ff["brightness"], 70, 200, 60) * .2 + band(ff["contrast"], 45, 120, 35) * .2 + band(ff["saturation"], .25, 1, .2) * .1 + min(100, mov * 8) * .15
        if ff["text_px"] <= 120: tips.append("First frame: no big words on screen at 0:00 — open on a caption/stamp so people stop scrolling")
        if ff["brightness"] < 70: tips.append(f"First frame is dark (brightness {ff['brightness']:.0f}) — brighter openings stop more thumbs")
        if ff["contrast"] < 45: tips.append("First frame is flat (low contrast) — add a bright subject on a dark background or vice versa")
    else: S["First frame"] = 50

    # 3. PACING + MOTION
    cpm = cuts / dur * 60; S["Pacing (cuts)"] = band(cpm, 12, 40, 20) if not is_long else band(cpm, 6, 20, 12)
    if S["Pacing (cuts)"] < 75: tips.append(f"Pacing: {cpm:.0f} cuts/min — aim for a new shot or big zoom every 2-4 s")
    S["Motion"] = min(100, motion * 18) * .6 + (1 - min(1, still * 3)) * 100 * .4
    if S["Motion"] < 75: tips.append(f"Motion: {still * 100:.0f}% of the video is nearly still — add camera moves or moving props")

    # 4. DROP-OFF RISK: second by second (no speech + little motion + no new shot + no SFX = people swipe)
    secs = int(dur); risk = np.zeros(secs)
    for s in range(secs):
        talking = any(l["start"] - .3 <= s + .5 <= l["end"] + .3 for l in lines)
        mv = diff[s * fps_s:(s + 1) * fps_s].mean() if s * fps_s < len(diff) else 0
        newshot = any(s - 2.5 <= c <= s + 1 for c in cut_times); ev = any(s - 2.5 <= e <= s + 1 for e in sfx_t)
        risk[s] = (0 if talking else .4) + (.3 if mv < 1.0 else .12 if mv < 2.5 else 0) + (0 if newshot else .2) + (0 if ev else .1)
    dead, run = [], None
    for s in range(1, max(1, secs - 2)):   # skip the first second and the outro
        if risk[s] >= .6: run = run if run is not None else s
        else:
            if run is not None and s - run >= 2: dead.append((run, s))
            run = None
    if run is not None and secs - 2 - run >= 2: dead.append((run, secs - 2))
    S["Drop-off risk"] = max(0, 100 - 22 * len(dead) - 5 * sum(b - a for a, b in dead))
    for a, b in dead[:4]: tips.append(f"Drop-off risk {fmt_t(a)}–{fmt_t(b)}: little talking/motion/new shots — add a cut, a sound effect or a line there")

    # 5. CAPTIONS + talk speed
    S["Captions & talk speed"] = band(spoken / dur, .75, 1, .4) * .5 + band(wps, 2.2, 4.3, 1.2) * .5
    if S["Captions & talk speed"] < 75: tips.append(f"Talk speed {wps:.1f} words/s, captions on {spoken / dur * 100:.0f}% of the time — aim 2.2-4.3 w/s and 75%+")

    # 6. PAYOFFS: a cut, stamp sound or reveal at least every 5-8 s
    pts = [0.0] + [e for e in events if 0 < e < dur] + [dur]; gaps = np.diff(pts) if len(pts) > 1 else np.array([dur])
    longest = float(gaps.max()); gi = int(gaps.argmax())
    S["Payoffs (every 5-8 s)"] = float((gaps <= 8).mean() * 100) * .7 + band(longest, 0, 8, 10) * .3
    if longest > 8: tips.append(f"Payoffs: nothing new happens for {longest:.0f}s around {fmt_t(pts[gi])}–{fmt_t(pts[gi + 1])} — drop a stamp, SFX or reveal in there")

    # 7. OPEN LOOPS: questions / "but" / "until" / mysteries keep people watching
    alltext = " ".join(l["text"] for l in lines); loops = len(LOOPS.findall(alltext)); lpm = loops / max(1, dur / 60)
    S["Open loops"] = band(lpm, 6, 60, 6)
    if S["Open loops"] < 75: tips.append(f"Open loops: only {loops} questions/twists words — add a 'but…', 'until…' or a question that gets answered later")

    # 8. LENGTH (+ TikTok Creator Rewards only pays on videos OVER 1 minute)
    S["Length"] = band(dur, 61, 95, 25) if not is_long else band(dur, 480, 720, 300)
    if not is_long and dur <= 60: tips.append(f"Length {dur:.0f}s: under 1 minute, so TikTok Creator Rewards won't pay for it (fine for Stories/Highlights)")
    elif S["Length"] < 75: tips.append(f"Length {dur:.0f}s is outside the sweet spot")

    # 9. AUDIO
    S["Audio"] = (band(lufs or -30, -16, -12, 6)) * .6 + (100 if not sil else max(0, 100 - 40 * len(sil))) * .4
    if S["Audio"] < 75: tips.append(f"Audio: {lufs} LUFS, {len(sil)} silent gaps — aim -14 LUFS, no gaps over 1 s")

    # 10. ENDING: CTA + tease + does the last shot loop back to the first one (rewatches)
    cta = 100 if len(CTA.findall(ending)) >= 2 else 60 if CTA.search(ending) else 15
    fa, fb = frame_at(vid, .4, 90, 160), frame_at(vid, max(0, dur - 1.6), 90, 160)
    loopsim = float(np.corrcoef(fa.ravel(), fb.ravel())[0, 1]) if fa is not None and fb is not None else 0
    S["Ending (CTA / loop)"] = cta * .8 + (100 if loopsim > .55 else 40) * .2
    if cta < 75: tips.append("Ending: ask for a comment/vote AND tease tomorrow in the last lines")

    # 11. SAFE ZONES: words under TikTok/Instagram buttons, captions or top bars
    C = frames(vid, 1, 270, 480, "rgb24"); hits = {z: [] for z in ZONES}
    for si, img in enumerate(C):
        m = text_mask(img)
        for z, (x0, y0, x1, y1) in ZONES.items():
            if texty(m[y0 // 4:y1 // 4, x0 // 4:x1 // 4]): hits[z].append(si)
    bad = {z: v for z, v in hits.items() if len(v) / max(1, len(C)) > .08}
    S["Safe zones"] = max(0, 100 - sum(min(60, 100 * len(v) / max(1, len(C))) for v in bad.values()))
    for z, v in bad.items(): tips.append(f"Safe zones: words sit under the {z} in {len(v) * 100 // max(1, len(C))}% of the video (e.g. {fmt_t(v[0])}) — move them inside")

    weights = {"Hook (first 3 s)": .17, "First frame": .08, "Pacing (cuts)": .09, "Motion": .07, "Drop-off risk": .12, "Captions & talk speed": .07,
               "Payoffs (every 5-8 s)": .08, "Open loops": .05, "Length": .05, "Audio": .06, "Ending (CTA / loop)": .09, "Safe zones": .07}
    total = sum(S[k] * w for k, w in weights.items())
    return {"dir": d, "score": round(total), "parts": {k: round(v) for k, v in S.items()}, "tips": tips, "risk": [round(float(x), 2) for x in risk], "dead": dead,
            "facts": {"duration": round(dur, 1), "cuts_per_min": round(cpm, 1), "first_word_s": round(first_word, 2), "words_per_s": round(wps, 2), "lufs": lufs,
                      "still_pct": round(still * 100), "longest_no_payoff_s": round(longest, 1), "open_loops": loops, "loop_back": round(loopsim, 2), **{k: round(v, 2) for k, v in ff.items()}}}

def png(r, out):
    from PIL import Image, ImageDraw, ImageFont
    F = lambda w, s: ImageFont.truetype(f"/usr/share/fonts/opentype/inter/Inter-{w}.otf", s)
    W, H = 1200, 1240; im = Image.new("RGB", (W, H), (14, 16, 24)); d = ImageDraw.Draw(im)
    sc = r["score"]; col = (46, 204, 113) if sc >= 80 else (241, 196, 15) if sc >= 65 else (231, 76, 60)
    d.text((50, 40), "VIRAL CHECK", font=F("Black", 54), fill=(255, 255, 255)); d.text((50, 105), os.path.basename(os.path.normpath(r["dir"])).upper(), font=F("Bold", 28), fill=(150, 156, 176))
    d.ellipse((930, 30, 1150, 250), outline=col, width=18); t = str(sc); tw = d.textlength(t, font=F("Black", 96)); d.text((1040 - tw / 2, 82), t, font=F("Black", 96), fill=col); d.text((1005, 190), "/ 100", font=F("Bold", 26), fill=(150, 156, 176))
    y = 280
    for k, v in r["parts"].items():
        c = (46, 204, 113) if v >= 80 else (241, 196, 15) if v >= 65 else (231, 76, 60)
        d.text((50, y), k, font=F("Bold", 30), fill=(230, 232, 240)); d.rounded_rectangle((500, y + 6, 1050, y + 34), 14, fill=(36, 40, 56)); d.rounded_rectangle((500, y + 6, 500 + 550 * v / 100, y + 34), 14, fill=c)
        d.text((1070, y), str(v), font=F("Black", 30), fill=c); y += 56
    # drop-off risk timeline: green = safe, red = likely swipe
    y += 20; d.text((50, y), "DROP-OFF RISK, SECOND BY SECOND", font=F("Black", 28), fill=(230, 232, 240)); y += 50
    rk = r["risk"]; n = max(1, len(rk)); bw = 1100 / n
    for i, v in enumerate(rk):
        c = (46, 204, 113) if v < .35 else (241, 196, 15) if v < .6 else (231, 76, 60); h = 20 + 80 * v
        d.rectangle((50 + i * bw, y + 100 - h, 50 + (i + 1) * bw - 2, y + 100), fill=c)
    for i in range(0, n, 10): d.text((50 + i * bw, y + 108), f"{i // 60}:{i % 60:02d}", font=F("Bold", 20), fill=(150, 156, 176))
    d.text((50, H - 50), "Checklist score, not a view prediction.", font=F("Bold", 22), fill=(120, 126, 146))
    im.save(out)

if __name__ == "__main__":
    r = check(sys.argv[1])
    if "--png" in sys.argv: png(r, sys.argv[sys.argv.index("--png") + 1])
    if "--json" in sys.argv: print(json.dumps(r)); sys.exit()
    print(f"🔥 VIRAL CHECK: {r['score']}/100  ({r['dir']})")
    for k, v in r["parts"].items(): print(f"  {'✅' if v >= 80 else '🟡' if v >= 65 else '❌'} {k}: {v}")
    for t in r["tips"]: print("  → " + t)

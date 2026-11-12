"""Our own "viral check": scores a rendered short on the things that drive TikTok / Reels performance.

usage: python3 viral_check.py <episode_dir> [--png out.png] [--json]
Reads <dir>/episode.mp4 + <dir>/timeline.json (Possums / $1 to $10K "lines" or zombie "beats").
It is a checklist score, not a real prediction: it measures hook speed, pacing, motion, captions, length, audio, ending.
Compare it against the real numbers in #video-stats over time and tune the weights below.
"""
import json, os, re, subprocess, sys
import numpy as np

STAKES = re.compile(r"\d|dollar|\$|dead|kick|out|last|never|first|only|zero|million|thousand|hundred|day|minute|second|tomorrow|worst|broke|why|how|what if|\?", re.I)
CTA = re.compile(r"comment|vote|like|follow|poll|tomorrow|part \w+|which|would you|day \w+ starts|your choice|next", re.I)

def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=width,height,r_frame_rate", "-of", "json", path], capture_output=True, text=True).stdout
    j = json.loads(out); v = next(s for s in j["streams"] if "width" in s)
    n, d = v["r_frame_rate"].split("/"); return float(j["format"]["duration"]), int(v["width"]), int(v["height"]), float(n) / float(d or 1)

def frames(path, fps=6, w=90, h=160):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-vf", f"fps={fps},scale={w}:{h},format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(np.float32)

def loudness(path):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", err); return float(m[-1]) if m else None

def silences(path):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", "silencedetect=n=-40dB:d=1.2", "-f", "null", "-"], capture_output=True, text=True).stderr
    return [float(x) for x in re.findall(r"silence_duration: ([\d.]+)", err)]

def band(x, lo, hi, soft):  # 100 inside [lo, hi], falls off linearly over `soft` outside
    if lo <= x <= hi: return 100.0
    d = lo - x if x < lo else x - hi; return max(0.0, 100 - 100 * d / soft)

def check(d):
    vid = os.path.join(d, "episode.mp4"); tl = json.load(open(os.path.join(d, "timeline.json")))
    lines = [l for l in (tl.get("beats") or tl.get("lines")) if l.get("text")]
    dur, W, H, fps = probe(vid)
    fps_s = 6; F = frames(vid, fps_s); diff = np.abs(np.diff(F, axis=0)).mean(axis=(1, 2)) if len(F) > 1 else np.zeros(1)
    thr = max(18.0, 3 * float(np.median(diff))); cuts, last = 0, -99
    for i, x in enumerate(diff):   # a cut = a sudden big change, at most one per 1.2 s (falling confetti/money is not a cut)
        if x > thr and (i - last) / fps_s >= 1.2: cuts += 1; last = i
    motion = float(np.median(diff)); still = float((diff < .6).mean())
    first3 = diff[: 6 * 3].mean() if len(diff) else 0
    words = [w for l in lines for w in l.get("words", [])]
    first_word = min((w["s"] for w in words), default=dur)
    spoken = sum(max(0, l["end"] - l["start"]) for l in lines); wps = len(words) / max(1, spoken)
    hook = lines[0]["text"] if lines else ""; hook2 = " ".join(l["text"] for l in lines[:2])
    ending = " ".join(l["text"] for l in lines[-3:])
    lufs = loudness(vid); sil = silences(vid)
    is_long = W > H
    S = {}
    # 1. HOOK (first 3 s): speech starts fast, stakes/numbers/question in the first line, motion right away, cold open
    hook_pts = band(first_word, 0, .6, 1.5) * .35 + (100 if STAKES.search(hook) else 40 if STAKES.search(hook2) else 0) * .35 + min(100, first3 * 6) * .2 + (100 if any(l.get("cold") or l.get("rewind") for l in lines) or len(hook.split()) <= 12 else 60) * .1
    S["Hook (first 3 s)"] = hook_pts
    # 2. PACE: visual cuts every 2-4 s on shorts
    cpm = cuts / dur * 60; S["Pacing (cuts)"] = band(cpm, 12, 40, 20) if not is_long else band(cpm, 6, 20, 12)
    # 3. MOTION: something always moving, few frozen moments
    S["Motion"] = min(100, motion * 18) * .6 + (1 - min(1, still * 3)) * 100 * .4
    # 4. CAPTIONS + talk speed: words on screen most of the time, 2.3-3.4 words/s
    S["Captions & talk speed"] = band(spoken / dur, .75, 1, .4) * .5 + band(wps, 2.2, 4.3, 1.2) * .5
    # 5. LENGTH: shorts sweet spot
    S["Length"] = band(dur, 21, 95, 40) if not is_long else band(dur, 480, 720, 300)
    # 6. AUDIO: about -14 LUFS, no dead air
    S["Audio"] = (band(lufs or -30, -16, -12, 6)) * .6 + (100 if not sil else max(0, 100 - 40 * len(sil))) * .4
    # 7. ENDING: asks for comments / votes / follow, sets up tomorrow (loop + comments = reach)
    S["Ending (CTA / loop)"] = 100 if len(CTA.findall(ending)) >= 2 else 60 if CTA.search(ending) else 15
    weights = {"Hook (first 3 s)": .28, "Pacing (cuts)": .14, "Motion": .12, "Captions & talk speed": .12, "Length": .08, "Audio": .08, "Ending (CTA / loop)": .18}
    total = sum(S[k] * w for k, w in weights.items())
    tips = []
    if S["Hook (first 3 s)"] < 75: tips.append(f"Hook: first words at {first_word:.1f}s — start talking by 0.5 s and put a number/stake in line 1 (\"{hook[:60]}\")")
    if S["Pacing (cuts)"] < 75: tips.append(f"Pacing: {cpm:.0f} cuts/min — aim for a new shot or big zoom every 2-4 s")
    if S["Motion"] < 75: tips.append(f"Motion: {still * 100:.0f}% of the video is nearly still — add camera moves or moving props")
    if S["Captions & talk speed"] < 75: tips.append(f"Talk speed {wps:.1f} words/s, captions on {spoken / dur * 100:.0f}% of the time — aim 2.2-4.3 w/s and 75%+")
    if S["Length"] < 75: tips.append(f"Length {dur:.0f}s is outside the sweet spot")
    if S["Audio"] < 75: tips.append(f"Audio: {lufs} LUFS, {len(sil)} silent gaps — aim -14 LUFS, no gaps over 1 s")
    if S["Ending (CTA / loop)"] < 75: tips.append("Ending: ask for a comment/vote AND tease tomorrow in the last lines")
    return {"dir": d, "score": round(total), "parts": {k: round(v) for k, v in S.items()}, "tips": tips,
            "facts": {"duration": round(dur, 1), "cuts_per_min": round(cpm, 1), "first_word_s": round(first_word, 2), "words_per_s": round(wps, 2), "lufs": lufs, "still_pct": round(still * 100)}}

def png(r, out):
    from PIL import Image, ImageDraw, ImageFont
    F = lambda w, s: ImageFont.truetype(f"/usr/share/fonts/opentype/inter/Inter-{w}.otf", s)
    W, H = 1200, 900; im = Image.new("RGB", (W, H), (14, 16, 24)); d = ImageDraw.Draw(im)
    sc = r["score"]; col = (46, 204, 113) if sc >= 80 else (241, 196, 15) if sc >= 65 else (231, 76, 60)
    d.text((50, 40), "VIRAL CHECK", font=F("Black", 54), fill=(255, 255, 255)); d.text((50, 105), os.path.basename(os.path.normpath(r["dir"])).upper(), font=F("Bold", 28), fill=(150, 156, 176))
    d.ellipse((930, 30, 1150, 250), outline=col, width=18); t = str(sc); tw = d.textlength(t, font=F("Black", 96)); d.text((1040 - tw / 2, 82), t, font=F("Black", 96), fill=col); d.text((1005, 190), "/ 100", font=F("Bold", 26), fill=(150, 156, 176))
    y = 290
    for k, v in r["parts"].items():
        c = (46, 204, 113) if v >= 80 else (241, 196, 15) if v >= 65 else (231, 76, 60)
        d.text((50, y), k, font=F("Bold", 32), fill=(230, 232, 240)); d.rounded_rectangle((470, y + 6, 1050, y + 36), 15, fill=(36, 40, 56)); d.rounded_rectangle((470, y + 6, 470 + 580 * v / 100, y + 36), 15, fill=c)
        d.text((1070, y), str(v), font=F("Black", 32), fill=c); y += 62
    d.text((50, y + 20), "This is a checklist score, not a view prediction.", font=F("Bold", 24), fill=(120, 126, 146))
    im.save(out)

if __name__ == "__main__":
    r = check(sys.argv[1])
    if "--png" in sys.argv: png(r, sys.argv[sys.argv.index("--png") + 1])
    if "--json" in sys.argv: print(json.dumps(r)); sys.exit()
    print(f"🔥 VIRAL CHECK: {r['score']}/100  ({r['dir']})")
    for k, v in r["parts"].items(): print(f"  {'✅' if v >= 80 else '🟡' if v >= 65 else '❌'} {k}: {v}")
    for t in r["tips"]: print("  → " + t)

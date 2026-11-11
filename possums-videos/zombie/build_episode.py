"""MILE 41 long-form episode: script.json -> voices, music, ambience, SFX, timeline.json (1920x1080).

usage: python3 zombie/build_episode.py <episode_dir> <tts_dir>
"""
import hashlib, json, os, re, sys
import numpy as np
import soundfile as sf

SR = 24000
d, tts_dir = sys.argv[1], sys.argv[2]
S = json.load(open(os.path.join(d, "script.json")))
VOICES = {"cole": ("am_onyx", .86), "mags": ("af_bella", 1.0), "dooley": ("bm_lewis", .92), "pip": ("af_sky", 1.06),
          "tank": ("am_fenrir", 1.0), "radio": ("am_echo", .95), "narr": ("am_michael", 1.06)}
NAMES = {"narr": "NARRATOR", "cole": "COLE", "mags": "MAGS", "dooley": "DOOLEY", "pip": "PIP", "tank": "TANK", "radio": "RADIO"}
class _Lazy:
    k = None
    def create(self, *a, **kw):
        if self.k is None:
            from kokoro_onnx import Kokoro
            self.k = Kokoro(os.path.join(tts_dir, "kokoro.onnx"), os.path.join(tts_dir, "voices.bin"))
        return self.k.create(*a, **kw)
kok = _Lazy()

rng = np.random.default_rng(41)
def tt(x): return np.arange(int(x * SR)) / SR
def noise(x): return rng.uniform(-1, 1, int(x * SR)).astype(np.float32)
def nn(n): return rng.uniform(-1, 1, n).astype(np.float32)
def lp(x, k): return np.convolve(x, np.ones(k) / k, mode="same").astype(np.float32)
def env(n, a=.005, r=.1):
    e = np.ones(n, np.float32); na, nr = max(1, int(a * SR)), max(1, int(r * SR)); e[:na] = np.linspace(0, 1, na); e[-nr:] *= np.linspace(1, 0, nr); return e
def saw(f, x): return (2 * ((tt(x) * f) % 1) - 1).astype(np.float32)
def sweep(f0, f1, x):
    f = np.linspace(f0, f1, int(x * SR)); return np.sin(2 * np.pi * np.cumsum(f) / SR).astype(np.float32)
def add(buf, at, sig):
    i = int(at * SR)
    if i >= len(buf) or i + len(sig) <= 0: return
    j = min(len(buf), i + len(sig)); buf[max(0, i):j] += sig[max(0, -i): j - i]
def radio_fx(a):  # band-limited, slightly crushed, with static
    hp = a - lp(a, 40); bp = lp(hp, 3); bp = np.tanh(bp * 3) * .5
    return (bp + lp(rng.uniform(-1, 1, len(a)).astype(np.float32), 2) * .05).astype(np.float32)

# ---- resolve shots (fields carry over) + voice each line
KEYS = ["loc", "tod", "wx", "cast", "z", "props", "fx", "card", "cam", "camx", "hud", "act", "intensity", "focus"]
state = {"loc": "black", "tod": "night", "wx": None, "cast": [], "z": None, "props": [], "fx": [], "card": None, "cam": 1.0, "camx": .5, "hud": None, "act": "", "intensity": .3, "focus": None}
beats, clips, t = [], [], S.get("lead", 1.0)
prev_sp = None
for raw in S["beats"]:
    for k in KEYS:
        if k in raw: state[k] = raw[k]
    shot = {k: state[k] for k in KEYS}
    shot.update({k: v for k, v in raw.items() if k not in KEYS and k not in ("sp", "text", "hold", "sfx")})  # per-beat extras (e.g. scene, choice)
    if raw.get("hold"):
        dur = raw["hold"]; st = t + .2
        beats.append({**shot, "sp": "", "text": "", "start": round(st, 3), "end": round(st + dur, 3), "words": [], "sfx": raw.get("sfx", [])})
        t = st + dur + .2; prev_sp = None; continue
    voice, speed = VOICES[raw["sp"]]
    if S.get("vertical") and raw["sp"] == "cole": speed = .9
    key = hashlib.md5(f"{voice}|{speed}|{raw['text']}".encode()).hexdigest()[:16]; cp = os.path.join(d, "_tts", key + ".wav")
    if os.path.exists(cp):
        a, _ = sf.read(cp, dtype="float32")
    else:  # cache each line so edits only re-voice what changed
        a, sr = kok.create(raw["text"], voice=voice, speed=speed, lang="en-us")
        a = np.asarray(a, np.float32); nz = np.where(np.abs(a) > .01)[0]; a = a[max(0, nz[0] - 600): nz[-1] + 1500]
        os.makedirs(os.path.dirname(cp), exist_ok=True); sf.write(cp, a, SR)
    if raw["sp"] == "radio": a = radio_fx(a)
    gap = (.3 if raw["sp"] == prev_sp else .45) if S.get("vertical") else (.42 if raw["sp"] == prev_sp else .75)  # Shorts: snappier
    st = t + gap; dur = len(a) / SR
    ws = raw["text"].split(); wt = [len(re.sub(r"\W", "", w)) + 2 + (3 if re.search(r"[.,!?]$", w) else 0) for w in ws]; tot = sum(wt); acc = 0; words = []
    for w, k in zip(ws, wt): words.append({"w": w, "s": round(st + dur * acc / tot, 3)}); acc += k
    beats.append({**shot, "sp": raw["sp"], "name": NAMES[raw["sp"]], "text": raw["text"], "start": round(st, 3), "end": round(st + dur, 3), "words": words, "sfx": raw.get("sfx", [])})
    clips.append((st, a)); t = st + dur; prev_sp = raw["sp"]
total = t + 2.0
N = int(total * SR)

voice = np.zeros(N, np.float32)
for st, a in clips: add(voice, st, a)

# ---- intensity curve (per beat, smoothed)
inten = np.zeros(N, np.float32)
for b in beats: inten[int(b["start"] * SR): int(b["end"] * SR) + int(.6 * SR)] = b["intensity"]
k = int(2.5 * SR); inten = np.convolve(inten, np.ones(k) / k, mode="same")

# ---- original tense score: drone + pulse whose speed/volume follow intensity + high tension tone
music = np.zeros(N, np.float32)
dr = sum(lp(saw(f, total), 80) for f in (36.71, 36.9, 55.0)) * .1
music += dr[:N] * (.6 + .5 * inten)
step = 60 / 92 / 2; x = 0.0; n = 0
notes = [73.42, 73.42, 77.78, 73.42, 87.31, 77.78, 73.42, 69.3]
while x < total - 1:
    i = int(x * SR); lvl = float(inten[min(i, N - 1)])
    play = (lvl > .75) or (lvl > .4 and n % 2 == 0) or (lvl > .15 and n % 4 == 0)
    if play:
        f = notes[n % 8] * (2 if lvl > .75 and (n // 16) % 2 else 1)
        add(music, x, lp(saw(f, step * .85), 14) * env(int(step * .85 * SR), r=.06) * (.06 + .1 * lvl))
    n += 1; x += step
hi = (np.sin(2 * np.pi * 587.3 * tt(total)) + np.sin(2 * np.pi * 622.3 * tt(total))).astype(np.float32) * .012
music += hi[:N] * np.clip((inten - .55) * 2.5, 0, 1)
music[-int(3 * SR):] *= np.linspace(1, 0, int(3 * SR))

# ---- ambience per location / time / weather
amb = np.zeros(N, np.float32)
base_wind = lp(noise(total), 120)[:N]
for b in beats:
    a0, a1 = int((b["start"] - .5) * SR), int((b["end"] + .6) * SR); a0 = max(0, a0); a1 = min(N, a1)
    seg = np.zeros(a1 - a0, np.float32)
    n_ = a1 - a0
    if b["loc"] in ("station_int", "pharmacy"): seg += lp(nn(n_), 300) * .6
    else: seg += base_wind[a0:a1] * 2.5
    if b["tod"] == "night" and b["loc"] not in ("station_int", "pharmacy", "black"):
        tt_ = np.arange(a1 - a0) / SR; seg += (np.sin(2 * np.pi * 4300 * tt_) * (np.sin(2 * np.pi * 18 * tt_) > .6) * (np.sin(2 * np.pi * .7 * tt_) > 0)).astype(np.float32) * .02
    if b["wx"] == "rain": r_ = nn(n_); seg += (r_ - lp(r_, 6)) * .18
    amb[a0:a1] = seg

# ---- SFX
def sfx(name):
    if name == "groan":
        x = tt(1.6); f = 95 + 15 * np.sin(2 * np.pi * 1.3 * x); s = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * .5 + lp(noise(1.6), 8) * .6
        return (lp(s.astype(np.float32), 30) * np.sin(np.linspace(0, np.pi, len(x))) * .6).astype(np.float32)
    if name == "thunder":
        x = noise(3.0); return (lp(x, 60) * 3 * np.exp(-tt(3.0) * 1.2) + lp(x, 6) * np.exp(-tt(3.0) * 8) * .6).astype(np.float32) * .8
    if name == "sting":
        x = tt(2.5); s = sum(np.sin(2 * np.pi * f * x) for f in (110, 116.5, 164.8, 233)) * np.exp(-x * 1.4); return (s * .18 + lp(noise(2.5), 4) * np.exp(-x * 6) * .3).astype(np.float32)
    if name == "whoosh":
        x = lp(noise(.8), 10); return (x * np.sin(np.linspace(0, np.pi, len(x))) * .8).astype(np.float32)
    if name == "reveal":
        return (sweep(300, 900, .5) * env(int(.5 * SR), r=.3) * .15).astype(np.float32)
    if name == "bark":
        out = np.zeros(int(.6 * SR), np.float32)
        for o in (0, .22): add(out, o, (lp(noise(.12), 3) * .6 + sweep(700, 420, .12) * .5) * env(int(.12 * SR), r=.05))
        return out * .7
    if name == "cough":
        out = np.zeros(int(1.0 * SR), np.float32)
        for o in (0, .28, .5): add(out, o, lp(noise(.18), 5) * np.exp(-tt(.18) * 14) * .9)
        return out
    if name == "engine":
        x = tt(3.0); f = 40 + 25 * np.clip(x / 1.5, 0, 1); s = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * .3 + lp(noise(3.0), 30)
        return (lp(s.astype(np.float32), 12) * env(len(x), a=.3, r=.8) * .5).astype(np.float32)
    if name == "sputter":
        out = np.zeros(int(2.0 * SR), np.float32)
        for o in np.arange(0, 1.6, .18): add(out, o + rng.uniform(0, .05), lp(noise(.09), 10) * np.exp(-tt(.09) * 30) * 1.2)
        add(out, 1.6, sweep(80, 30, .4) * env(int(.4 * SR), r=.3) * .5); return out
    if name == "steps":
        out = np.zeros(int(2.5 * SR), np.float32)
        for o in np.arange(0, 2.4, .19): add(out, o, lp(noise(.06), 8) * np.exp(-tt(.06) * 60) * .7)
        return out
    if name == "scream":
        x = tt(1.2); f = 1100 + 250 * np.sin(2 * np.pi * 7 * x) + 200 * x
        return (lp(np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)).astype(np.float32), 5) * env(len(x), r=.3) * .12).astype(np.float32)
    if name == "rattle":
        out = np.zeros(int(1.5 * SR), np.float32)
        for o in np.arange(0, 1.4, .05): add(out, o, noise(.03) * np.exp(-tt(.03) * 80) * .35)
        return out
    if name == "crash":
        return (noise(.9) * np.exp(-tt(.9) * 6) * .6 + sweep(150, 40, .9) * np.exp(-tt(.9) * 5) * .6).astype(np.float32)
    if name == "bang":
        return (sweep(120, 45, .35) * np.exp(-tt(.35) * 9) * .9 + lp(noise(.35), 10) * np.exp(-tt(.35) * 16) * .5).astype(np.float32)
    if name == "scrape":
        x = tt(1.4); return (lp(noise(1.4), 3) * (.5 + .5 * np.sin(2 * np.pi * 9 * x)) * env(len(x), r=.3) * .35).astype(np.float32)
    if name == "static":
        return (noise(2.5) - lp(noise(2.5), 4)) * .35 * env(int(2.5 * SR), a=.05, r=.4)
    if name == "tick":
        return (np.sin(2 * np.pi * 1800 * tt(.05)) * np.exp(-tt(.05) * 90) * .5).astype(np.float32)
    if name == "ding":
        return ((np.sin(2 * np.pi * 1318 * tt(.9)) + .5 * np.sin(2 * np.pi * 2637 * tt(.9))) * np.exp(-tt(.9) * 5) * .35).astype(np.float32)
    raise KeyError(name)
fx = np.zeros(N, np.float32)
for b in beats:
    for name, at in b["sfx"]:
        if isinstance(at, str):
            key = at[1:].lower(); w = next((w for w in b["words"] if re.sub(r"\W", "", w["w"].lower()).startswith(key)), None)
            tm = w["s"] if w else b["start"]
        else:
            tm = b["start"] + at * max(.5, b["end"] - b["start"])
        add(fx, tm, sfx(name))

def _db(x):
    x = x[np.abs(x) > 1e-4]; return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)
VO, MU, FX, AM = 1.3, .10, .14, .07
mx = S.get("mix", {}); MU, FX, AM = mx.get("music", MU), mx.get("sfx", FX), mx.get("ambience", AM)  # per-video override
v_env = np.convolve(np.abs(voice), np.ones(2400) / 2400, mode="same")
duck = np.convolve(np.clip(1 - (v_env > .004) * .5, .5, 1), np.ones(4800) / 4800, mode="same")
mix = voice * VO + music * MU * duck + fx * FX + amb * AM * duck
mix = np.tanh(mix * 1.05) * .9
sf.write(os.path.join(d, "audio.wav"), mix, SR)
vdb = _db(voice * VO)
print(f"duration {total:.1f}s ({total / 60:.1f} min) | music {_db(music * MU) - vdb:+.1f} dB, sfx {_db(fx * FX) - vdb:+.1f} dB, ambience {_db(amb * AM) - vdb:+.1f} dB vs voice")

# ---- YouTube chapters
chap, seen = [], set()
for b in beats:
    if b["act"] and b["act"] not in seen:
        seen.add(b["act"]); s0 = 0 if not chap else b["start"]; chap.append(f"{int(s0 // 60)}:{int(s0 % 60):02d} {b['act']}")
open(os.path.join(d, "chapters.txt"), "w").write("\n".join(chap) + "\n")
json.dump({"width": S.get("width", 1920), "height": S.get("height", 1080), "vertical": bool(S.get("vertical")), "day": S.get("day"), "lesson": S.get("lesson"), "duration": round(total, 3), "series": S["series"], "episode": S["episode"], "title": S["title"],
           "beats": beats, "lines": [{"start": b["start"], "end": b["end"], "words": b["words"]} for b in beats if b["text"]]},
          open(os.path.join(d, "timeline.json"), "w"), indent=0)

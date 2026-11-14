"""Voice + original kids music + sound effects for a kids3d episode, and timeline.json for the 3D engine.

usage: python3 kids3d/build_audio.py <episode_dir> <tts_dir>
script.json: {"bpm": 104, "key": "C", "speakers": {"narr": {"voice", "speed"}, "pip": {"voice", "speed", "pitch"}},
              "lines": [{"sp": "narr", "text": "...", "sfx": [["splash", "@splash"], ["pop", 0.2]], "pause": 0.3, ...any scene keys}]}
"@word" = at that word (first match from the start), number = fraction of the line.
"""
import json, os, re, sys
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

SR = 24000; FPS = 60
ep, tts = sys.argv[1], sys.argv[2]
S = json.load(open(os.path.join(ep, "script.json")))
kok = Kokoro(os.path.join(tts, "kokoro.onnx"), os.path.join(tts, "voices.bin"))
rng = np.random.default_rng(7)

# ------------------------------------------------------------------ voice
def tts_line(text, spk):
    a, sr = kok.create(text, voice=spk["voice"], speed=spk.get("speed", 1.0), lang="en-us"); a = np.asarray(a, np.float32)
    p = spk.get("pitch", 1.0)
    if p != 1.0:  # simple resample pitch-up (also a bit faster): a younger, cartoon voice
        n = int(len(a) / p); a = np.interp(np.arange(n) * p, np.arange(len(a)), a).astype(np.float32)
    nz = np.where(np.abs(a) > 0.01)[0]; a = a[max(0, nz[0] - 500): nz[-1] + 1500]
    return a / (np.abs(a).max() + 1e-6) * 0.9

LEAD, GAP = 0.6, 0.28
lines, clips, t = [], [], LEAD
for ln in S["lines"]:
    spk = S["speakers"][ln.get("sp", "narr")]
    a = tts_line(ln["text"], spk); dur = len(a) / SR
    words = ln["text"].split(); wts = []
    for w in words:
        wt = len(re.sub(r"[^A-Za-z0-9]", "", w)) + 2.0
        if re.search(r"[.,!?…]$", w): wt += 3.0
        wts.append(wt)
    tot = sum(wts); acc = 0; ws = []
    for w, wt in zip(words, wts):
        s = t + dur * acc / tot; acc += wt; ws.append({"w": w, "s": round(s, 3), "e": round(t + dur * acc / tot, 3)})
    L = {k: v for k, v in ln.items() if k not in ("sfx",)}; L.update(start=round(t, 3), end=round(t + dur, 3), words=ws, sp=ln.get("sp", "narr"))
    L["_sfx"] = ln.get("sfx", [])
    lines.append(L); clips.append((t, a, L["sp"])); t += dur + GAP + ln.get("pause", 0)
DUR = t + 1.6
N = int(DUR * SR) + SR
voice = np.zeros(N, np.float32); env = {k: np.zeros(int(DUR * FPS) + 2, np.float32) for k in S["speakers"]}
for st, a, sp in clips:
    i = int(st * SR); voice[i:i + len(a)] += a
    hop = SR // FPS
    for f in range(len(a) // hop):
        seg = a[f * hop:(f + 1) * hop]; fi = int(st * FPS) + f
        if fi < len(env[sp]): env[sp][fi] = max(env[sp][fi], float(np.sqrt((seg ** 2).mean())) * 4)

# ------------------------------------------------------------------ instruments
def tt(d): return np.arange(int(d * SR)) / SR
def mtof(m): return 440 * 2 ** ((m - 69) / 12)
def marimba(m, d=0.5, v=1.0):
    x = tt(d); f = mtof(m)
    return v * (np.sin(2 * np.pi * f * x) + .35 * np.sin(2 * np.pi * f * 4 * x) * np.exp(-x * 30) + .15 * np.sin(2 * np.pi * f * 10 * x) * np.exp(-x * 60)) * np.exp(-x * 7)
def glock(m, d=0.9, v=1.0):
    x = tt(d); f = mtof(m)
    return v * (np.sin(2 * np.pi * f * x) + .4 * np.sin(2 * np.pi * f * 2.76 * x) * np.exp(-x * 6) + .2 * np.sin(2 * np.pi * f * 5.4 * x) * np.exp(-x * 12)) * np.exp(-x * 4)
def ukulele(m, d=0.45, v=1.0):  # plucked string (Karplus-Strong)
    f = mtof(m); n = int(d * SR); p = max(2, int(SR / f)); buf = rng.uniform(-1, 1, p).astype(np.float32); out = np.zeros(n, np.float32)
    for i in range(n): out[i] = buf[i % p]; buf[i % p] = 0.5 * (buf[i % p] + buf[(i + 1) % p]) * 0.996
    return v * out
def bass(m, d=0.4, v=1.0):
    x = tt(d); f = mtof(m); return v * (np.sin(2 * np.pi * f * x) + .3 * np.sin(4 * np.pi * f * x)) * np.minimum(1, x * 80) * np.exp(-x * 4)
def kick(v=1.0):
    x = tt(.25); return v * np.sin(2 * np.pi * (50 + 90 * np.exp(-x * 30)) * x) * np.exp(-x * 14)
def noise(d): return rng.uniform(-1, 1, int(d * SR)).astype(np.float32)
def hp(x, k=0.9):
    y = np.zeros_like(x);
    for i in range(1, len(x)): y[i] = k * (y[i - 1] + x[i] - x[i - 1])
    return y
def lp(x, k=12):
    return np.convolve(x, np.ones(k) / k, mode="same")
def clap(v=1.0):
    x = tt(.18); n = noise(.18); return v * hp(n, .7) * (np.exp(-x * 30) + .5 * np.exp(-np.maximum(0, x - .012) * 30) * (x > .012))
def shaker(v=1.0):
    x = tt(.07); return v * hp(noise(.07), .5) * np.exp(-x * 60) * .5

def put(buf, at, a, g=1.0):
    i = int(at * SR)
    if i < 0 or i >= len(buf): return
    j = min(len(buf), i + len(a)); buf[i:j] += a[:j - i] * g

# ------------------------------------------------------------------ the song (original): I-V-vi-IV in C, bouncy marimba hook
bpm = S.get("bpm", 104); beat = 60 / bpm; bar = 4 * beat
music = np.zeros(N, np.float32)
chords = [(48, [60, 64, 67]), (43, [59, 62, 67]), (45, [57, 60, 64]), (41, [57, 60, 65])]
hook = [[72, None, 76, 79, None, 76, 72, None], [74, None, 71, 74, None, 79, None, 74], [72, None, 76, 72, None, 69, None, 72], [69, 72, None, 77, 76, None, 74, None]]
hook2 = [[79, 79, 76, None, 72, 74, 76, None], [79, None, 74, None, 71, 74, 79, None], [76, 76, 72, None, 69, 72, 76, None], [77, None, 76, 74, 72, None, 74, None]]
start = 0.0; nb = int(DUR / bar) + 1
for b in range(nb):
    t0 = start + b * bar; root, tri = chords[b % 4]; part = (b // 8) % 2
    for k in range(4):  # bass + drums
        put(music, t0 + k * beat, bass(root if k % 2 == 0 else root + 7, beat * .9), .55)
        put(music, t0 + k * beat, kick(), .5 if k % 2 == 0 else .25)
        if k % 2 == 1: put(music, t0 + k * beat, clap(), .22)
        for h in range(2): put(music, t0 + k * beat + h * beat / 2, shaker(), .3)
    for k in range(4):  # ukulele strum on the beat
        for j, m in enumerate(tri): put(music, t0 + k * beat + j * 0.012 + (beat / 2 if k % 2 else 0) * 0, ukulele(m, beat * .9), .16)
    mel = (hook2 if part else hook)[b % 4]
    for k, m in enumerate(mel):
        if m: put(music, t0 + k * beat / 2, marimba(m, beat * 1.2), .3)
    if b % 4 == 3: put(music, t0 + 3.5 * beat, glock(84, .8), .12)

# ------------------------------------------------------------------ sound effects
def sweep(f0, f1, d, wave="sine"):
    x = tt(d); f = f0 * (f1 / f0) ** (x / d); ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) if wave == "sine" else 2 * ((ph / (2 * np.pi)) % 1) - 1
def sfx(name):
    if name in ("splash", "bigsplash"):
        d = .9 if name == "splash" else 1.6; x = tt(d); n = lp(noise(d), 6) * np.exp(-x * (5 if name == "splash" else 2.6))
        out = n * .9
        for k in range(8 if name == "splash" else 16):  # bubbly droplets
            at = rng.uniform(.05, d * .7); b = sweep(rng.uniform(600, 1400), rng.uniform(1600, 3000), .06) * np.exp(-tt(.06) * 40)
            put(out, at, b, .35)
        return out
    if name == "pop": x = tt(.12); return sweep(500, 1400, .12) * np.exp(-x * 30)
    if name == "boing": x = tt(.5); return sweep(180, 520, .5) * (1 + .5 * np.sin(2 * np.pi * 14 * x)) * np.exp(-x * 5) * .7
    if name == "ding": return glock(88, 1.2) * .7
    if name == "sparkle":
        out = np.zeros(int(1.0 * SR), np.float32)
        for k, m in enumerate([84, 88, 91, 96]): put(out, k * .07, glock(m, .7), .5)
        return out
    if name == "whoosh": x = tt(.5); return lp(noise(.5), 3) * np.sin(np.pi * x / .5) ** 2 * .6
    if name == "quack":
        out = np.zeros(int(.5 * SR), np.float32)
        for k in range(2):
            x = tt(.16); w = sweep(520, 420, .16, "saw") * np.exp(-x * 6) * (1 + .6 * np.sin(2 * np.pi * 30 * x)); put(out, k * .2, lp(w, 4), .5)
        return out
    if name == "ribbit":
        out = np.zeros(int(.5 * SR), np.float32)
        for k in range(2):
            x = tt(.12); w = sweep(170, 130, .12, "saw") * (np.sin(2 * np.pi * 45 * x) > 0) * np.exp(-x * 8); put(out, k * .17, lp(w, 5), .6)
        return out
    if name == "giggle":
        out = np.zeros(int(.8 * SR), np.float32)
        for k in range(5): x = tt(.09); put(out, k * .13, sweep(900 - k * 40, 1100 - k * 40, .09) * np.exp(-x * 20), .3)
        return out
    if name == "cheer":
        x = tt(2.0); return lp(noise(2.0), 4) * (np.minimum(1, x * 6) * np.exp(-x * 1.4)) * .5
    if name == "shake":
        x = tt(.7); return lp(noise(.7), 3) * (0.5 + 0.5 * np.sin(2 * np.pi * 14 * x)) * np.exp(-x * 3) * .6
    raise SystemExit("unknown sfx " + name)

fx = np.zeros(N, np.float32)
def word_time(L, key):
    if isinstance(key, (int, float)): return L["start"] + key * (L["end"] - L["start"])
    k = key[1:].lower()
    for w in L["words"]:
        if re.sub(r"[^a-z0-9]", "", w["w"].lower()).startswith(k): return w["s"]
    return L["start"]
for L in lines:
    L["sfx_times"] = []
    for name, key in L.pop("_sfx"):
        at = word_time(L, key); put(fx, at, sfx(name), 1.0); L["sfx_times"].append([name, round(at, 3)])
# rain ambience during the rainy part
rain_end = next((L["start"] for L in lines if L.get("rain_stops")), DUR)
x = np.arange(N) / SR; rain = lp(rng.uniform(-1, 1, N).astype(np.float32), 9) * .12
rain *= np.clip((x - 1.0) / 2, 0, 1) * np.clip((rain_end + 1.5 - x) / 2.5, 0, 1)

# ducking: music dips under the voice
v_env = np.convolve(np.abs(voice), np.ones(2400) / 2400, mode="same"); duck = 1 - 0.45 * np.clip(v_env * 10, 0, 1)
mix = voice * 1.0 + music * 0.5 * duck + fx * 0.5 + rain
fade = np.clip((DUR - x) / 1.2, 0, 1); mix *= fade
mix = mix[:int(DUR * SR)]; mix = mix / (np.abs(mix).max() + 1e-6) * 0.89
sf.write(os.path.join(ep, "audio.wav"), mix, SR)
tl = {"duration": round(DUR, 3), "fps": S.get("fps", 60), "crf": S.get("crf", 17), "bpm": bpm, "lines": lines,
      "env": {k: [int(min(100, v * 100)) for v in e] for k, e in env.items()}}
json.dump(tl, open(os.path.join(ep, "timeline.json"), "w"))
print("duration %.2f s, %d lines" % (DUR, len(lines)))

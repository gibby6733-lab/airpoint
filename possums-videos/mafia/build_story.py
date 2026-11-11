"""Mafia story: narration + images -> beat timeline, voice, tense music, SFX.

usage: python3 mafia/build_story.py <story_dir> <tts_dir>

<story_dir> contains:
  images/            the user's images, used in filename order (01.jpg, 02.png, ...)
  narration.txt      narration text  (voiced with TTS)        -- and/or --
  narration.<audio>  the user's own recording (.mp3/.m4a/.wav/.ogg/.aac); split into beats on pauses
  script.txt         optional script with time marks, one line each: "0:05 text", "[0:05] text", "0:05 - 0:09 text";
                     "(image 3)" in a line picks the image. With a recording, cuts/captions land exactly on the marks;
                     with TTS, a mark is the earliest a line may start.
  config.json        optional: {"voice": "am_onyx", "speed": 0.95, "title": "..."}
Writes audio.wav + timeline.json (beats, shots, transitions, sfx) for story.html.
"""
import glob, json, os, re, subprocess, sys
import numpy as np
import soundfile as sf

SR = 24000
d, tts_dir = sys.argv[1], sys.argv[2]
cfg = {"voice": "am_onyx", "speed": 0.95, "title": ""}
if os.path.exists(os.path.join(d, "config.json")):
    cfg.update(json.load(open(os.path.join(d, "config.json"))))
images = sorted(f for f in os.listdir(os.path.join(d, "images")) if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")))
assert images, "no images in images/"
text = open(os.path.join(d, "narration.txt")).read().strip() if os.path.exists(os.path.join(d, "narration.txt")) else ""
rec = [f for f in glob.glob(os.path.join(d, "narration.*")) if not f.endswith(".txt")]

LEAD, GAP, TAIL = 1.2, 0.45, 2.5

TM = re.compile(r"^\s*[\[(]?(\d{1,2}):(\d{2})(?:[.,](\d+))?[\])]?(?:\s*[-–—]+\s*[\[(]?\d{1,2}:\d{2}(?:[.,]\d+)?[\])]?)?\s*[:\-–—|.]?\s*(.*)$")
IMGTAG = re.compile(r"[\[(]\s*(?:img|image|pic|photo|picture)\s*#?\s*(\d+)\s*[\])]", re.I)
def parse_script(path):
    """Lines with time marks -> [{"t": secs, "text": str, "img": int|None}]; untimed lines join the previous beat."""
    out = []
    for raw in open(path, encoding="utf-8", errors="ignore").read().splitlines():
        if not raw.strip(): continue
        m = TM.match(raw)
        if m:
            secs = int(m.group(1)) * 60 + int(m.group(2)) + (float("0." + m.group(3)) if m.group(3) else 0)
            body = m.group(4).strip()
            im = IMGTAG.search(body); body = IMGTAG.sub("", body).strip(" -–—:|")
            out.append({"t": secs, "text": body, "img": int(im.group(1)) if im else None})
        elif out:
            im = IMGTAG.search(raw)
            if im and out[-1]["img"] is None: out[-1]["img"] = int(im.group(1))
            out[-1]["text"] = (out[-1]["text"] + " " + IMGTAG.sub("", raw).strip()).strip()
    return [b for b in out if b["text"] or b["img"]]
script = parse_script(os.path.join(d, "script.txt")) if os.path.exists(os.path.join(d, "script.txt")) else []

def split_beats(t):
    parts = re.split(r"(?<=[.!?…])\s+|\n+", t)
    beats, buf = [], ""
    for p in (x.strip() for x in parts if x.strip()):
        buf = (buf + " " + p).strip()
        if len(buf.split()) >= 4:  # merge tiny fragments ("Silence.") into the next beat
            beats.append(buf); buf = ""
    if buf:
        if beats: beats[-1] += " " + buf
        else: beats.append(buf)
    return beats

def word_times(beat_text, start, dur):
    words = beat_text.split(); w = [len(re.sub(r"\W", "", x)) + 2 + (3 if re.search(r"[.,!?…]$", x) else 0) for x in words]
    tot, acc, out = sum(w), 0, []
    for x, k in zip(words, w):
        out.append({"w": x, "s": round(start + dur * acc / tot, 3)}); acc += k
    return out

beats, clips = [], []
t = LEAD
if script and rec:
    tmp = os.path.join(d, "_rec.wav")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", rec[0], "-ac", "1", "-ar", str(SR), tmp], check=True)
    a, _ = sf.read(tmp, dtype="float32"); os.remove(tmp); a = a / (np.max(np.abs(a)) + 1e-6) * 0.9
    clips.append((LEAD, a)); rec_end = LEAD + len(a) / SR
    for k, b in enumerate(script):
        st = LEAD + b["t"]; en = LEAD + script[k + 1]["t"] - .1 if k + 1 < len(script) else rec_end
        beats.append({"text": b["text"], "img": b["img"], "start": round(st, 3), "end": round(en, 3), "words": word_times(b["text"], st, max(.5, en - st))})
    t = rec_end + GAP
elif script:
    from kokoro_onnx import Kokoro
    kok = Kokoro(os.path.join(tts_dir, "kokoro.onnx"), os.path.join(tts_dir, "voices.bin"))
    for b in script:
        a, sr = kok.create(b["text"], voice=cfg["voice"], speed=cfg["speed"], lang="en-us")
        a = np.asarray(a, dtype=np.float32); nz = np.where(np.abs(a) > 0.01)[0]; a = a[max(0, nz[0] - 600): nz[-1] + 1500]
        st = max(t, LEAD + b["t"]); dur = len(a) / SR
        beats.append({"text": b["text"], "img": b["img"], "start": round(st, 3), "end": round(st + dur, 3), "words": word_times(b["text"], st, dur)})
        clips.append((st, a)); t = st + dur + GAP
elif rec:  # user's own voice: split on pauses
    src = rec[0]
    tmp = os.path.join(d, "_rec.wav")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", src, "-ac", "1", "-ar", str(SR), tmp], check=True)
    a, _ = sf.read(tmp, dtype="float32"); os.remove(tmp)
    a = a / (np.max(np.abs(a)) + 1e-6) * 0.9
    env = np.convolve(np.abs(a), np.ones(1200) / 1200, mode="same")
    loud = env > max(0.02, np.percentile(env, 60) * 0.25)
    segs, i, n = [], 0, len(a)
    while i < n:
        if loud[i]:
            j = i
            while j < n and (loud[j] or (j + int(.35 * SR) < n and loud[j:j + int(.35 * SR)].any())):
                j += 1
            segs.append((i, j)); i = j
        else:
            i += 1
    segs = [(s, e) for s, e in segs if e - s > .3 * SR]
    texts = split_beats(text) if text else []
    for k, (s, e) in enumerate(segs):
        seg = a[max(0, s - 600): e + 1200]; dur = len(seg) / SR
        bt = texts[k] if k < len(texts) else ""
        beats.append({"text": bt, "start": round(t, 3), "end": round(t + dur, 3), "words": word_times(bt, t, dur) if bt else []})
        clips.append((t, seg)); t += dur + GAP
else:
    from kokoro_onnx import Kokoro
    kok = Kokoro(os.path.join(tts_dir, "kokoro.onnx"), os.path.join(tts_dir, "voices.bin"))
    for bt in split_beats(text):
        a, sr = kok.create(bt, voice=cfg["voice"], speed=cfg["speed"], lang="en-us")
        a = np.asarray(a, dtype=np.float32); nz = np.where(np.abs(a) > 0.01)[0]; a = a[max(0, nz[0] - 600): nz[-1] + 1500]
        dur = len(a) / SR
        beats.append({"text": bt, "start": round(t, 3), "end": round(t + dur, 3), "words": word_times(bt, t, dur)})
        clips.append((t, a)); t += dur + GAP
total = t - GAP + TAIL
N = int(total * SR)

# ---- shots: spread images across beats in order
n, m = len(images), len(beats)
shots = []
if any(b.get("img") for b in beats):   # script says which image goes with which line
    cur = None
    for k, b in enumerate(beats):
        idx = min(n, max(1, b["img"])) - 1 if b.get("img") else (cur if cur is not None else 0)
        if idx != cur:
            shots.append({"img": images[idx], "beats": [k, k], "start": 0.0 if not shots else round((beats[k - 1]["end"] + b["start"]) / 2, 3)})
            cur = idx
        else:
            shots[-1]["beats"][1] = k
elif n <= m:
    for j in range(n):
        b0, b1 = (j * m) // n, ((j + 1) * m) // n
        shots.append({"img": images[j], "beats": [b0, b1 - 1]})
    for j, sh in enumerate(shots):
        sh["start"] = 0.0 if j == 0 else round((beats[sh["beats"][0] - 1]["end"] + beats[sh["beats"][0]]["start"]) / 2, 3)
else:
    for j in range(n):
        shots.append({"img": images[j], "start": round(total * j / n, 3) if j else 0.0})
for j, s in enumerate(shots):
    s["end"] = shots[j + 1]["start"] if j + 1 < len(shots) else round(total, 3)
TRANS = ["tear_h", "cutout", "tear_v", "tear_diag", "cutout"]
transitions = [{"t": s["start"], "kind": TRANS[(j - 1) % len(TRANS)], "dur": 0.7} for j, s in enumerate(shots) if j > 0]

# ---- synth helpers
rng = np.random.default_rng(13)
def tt(x): return np.arange(int(x * SR)) / SR
def noise(x): return rng.uniform(-1, 1, int(x * SR)).astype(np.float32)
def lp(x, k): return np.convolve(x, np.ones(k) / k, mode="same").astype(np.float32)
def env(n, a=.005, r=.1):
    e = np.ones(n, np.float32); na, nr = max(1, int(a * SR)), max(1, int(r * SR)); e[:na] = np.linspace(0, 1, na); e[-nr:] *= np.linspace(1, 0, nr); return e
def saw(f, x):
    ph = (tt(x) * f) % 1; return (2 * ph - 1).astype(np.float32)
def add(buf, at, sig):
    i = int(at * SR)
    if i >= len(buf) or i + len(sig) <= 0: return
    j = min(len(buf), i + len(sig)); buf[max(0, i):j] += sig[max(0, -i): j - i]

# ---- tense music (original): low D drone, pulsing ostinato with a b2 rub, distant hits, risers into cuts
music = np.zeros(N, np.float32)
dr = sum(lp(saw(f, total), 60) for f in (36.71, 36.95, 73.42)) * 0.12            # D1/D2 drone, detuned
dr *= (0.75 + 0.25 * np.sin(2 * np.pi * 0.07 * tt(total)))[: len(dr)]
music[: len(dr)] += dr[:N]
bpm = 96; step = 60 / bpm / 2
notes = [146.83, 146.83, 155.56, 146.83, 146.83, 174.61, 155.56, 146.83]          # D3 D3 Eb3 D3 D3 F3 Eb3 D3
k = 0; x = LEAD * .5
while x < total - 1.5:
    f = notes[k % 8] * (0.5 if (k // 32) % 2 == 0 else 1)
    s = lp(saw(f, step * .8), 12) * env(int(step * .8 * SR), r=.08) * (0.10 + 0.04 * ((k % 4) == 0))
    add(music, x, s); k += 1; x += step
for b in range(0, int(total / (step * 16))):                                         # distant timpani-ish hit
    at = LEAD * .5 + b * step * 16
    add(music, at, (np.sin(2 * np.pi * np.cumsum(np.linspace(90, 45, int(.9 * SR))) / SR) * np.exp(-tt(.9) * 4)).astype(np.float32) * .35)
for tr in transitions:                                                               # riser into each cut
    r = lp(noise(1.2), 20) * np.linspace(0, 1, int(1.2 * SR)) ** 2 * .18
    add(music, tr["t"] - 1.2, r.astype(np.float32))
v_env = np.zeros(N, np.float32)
for st, a in clips: add(v_env, st, np.abs(a))
v_env = np.convolve(v_env, np.ones(2400) / 2400, mode="same")
duck = np.convolve(np.clip(1 - (v_env > .004) * .55, .45, 1), np.ones(4800) / 4800, mode="same")
music *= duck; music[-int(2 * SR):] *= np.linspace(1, 0, int(2 * SR))

# ---- sfx
def sfx(name):
    if name == "rip":
        x = noise(.45); crackle = (rng.random(len(x)) > .985).astype(np.float32) * rng.uniform(-1, 1, len(x))
        return (lp(x, 3) * .5 + crackle * .9) * np.linspace(1, .2, len(x)) * env(len(x), r=.08) * .5
    if name == "impact":
        return ((np.sin(2 * np.pi * np.cumsum(np.linspace(120, 30, int(1.2 * SR))) / SR) * np.exp(-tt(1.2) * 3)) + lp(noise(1.2), 40) * np.exp(-tt(1.2) * 6) * .6).astype(np.float32) * .8
    if name == "gunshot":
        x = noise(1.0); return ((x * np.exp(-tt(1.0) * 22) * 1.2) + lp(noise(1.0), 30) * np.exp(-tt(1.0) * 3.5) * .5 + np.sin(2 * np.pi * 55 * tt(1.0)) * np.exp(-tt(1.0) * 8) * .6).astype(np.float32) * .8
    if name == "heartbeat":
        one = (np.sin(2 * np.pi * 48 * tt(.18)) * np.exp(-tt(.18) * 18)).astype(np.float32)
        out = np.zeros(int(2.4 * SR), np.float32)
        for b in range(3):
            for off in (0, .22): add(out, b * .8 + off, one * (1 if off == 0 else .7))
        return out * .9
    if name == "door":
        return (lp(noise(.5), 6) * np.exp(-tt(.5) * 10) * .6 + np.sin(2 * np.pi * 80 * tt(.5)) * np.exp(-tt(.5) * 12) * .5).astype(np.float32)
    raise KeyError(name)
CUES = [("gunshot", r"\b(shot|shoot|shots|gun|guns|fired|fire|bang|trigger|bullet)"),
        ("heartbeat", r"\b(heart|quiet|silence|silent|waited|wait|breath|nervous|afraid|scared)"),
        ("door", r"\b(door|knock|knocked|walked in|entered)"),
        ("impact", r"\b(boss|don|family|betray|betrayed|dead|death|kill|killed|blood|never|rat|truth|deal)")]
fx = np.zeros(N, np.float32); fx_log = []
for tr in transitions:
    add(fx, tr["t"] - .15, sfx("rip")); fx_log.append(["rip", tr["t"]])
for b in beats:
    for name, pat in CUES:
        mm = re.search(pat, b["text"], re.I)
        if mm:
            w = next((w for w in b["words"] if re.sub(r"\W", "", w["w"].lower()).startswith(mm.group(1).split()[0].lower()[:4])), None)
            at = w["s"] if w else b["start"]
            add(fx, at, sfx(name)); fx_log.append([name, round(at, 3)]); break

voice = np.zeros(N, np.float32)
for st, a in clips: add(voice, st, a)
def _db(x):
    x = x[np.abs(x) > 1e-4]; return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)
MUS, FX = 0.10, 0.10
mix = np.tanh((voice * 1.3 + music * MUS + fx * FX) * 1.05) * .9
sf.write(os.path.join(d, "audio.wav"), mix, SR)
json.dump({"duration": round(total, 3), "title": cfg.get("title", ""), "images": images, "beats": beats, "shots": shots,
           "transitions": transitions, "sfx": fx_log, "lines": [{"scene": "story", "start": b["start"], "end": b["end"], "words": b["words"]} for b in beats]},
          open(os.path.join(d, "timeline.json"), "w"), indent=1)
print(f"beats {m}  images {n}  duration {total:.1f}s  | music {_db(music * MUS) - _db(voice * 1.3):+.1f} dB, sfx {_db(fx * FX) - _db(voice * 1.3):+.1f} dB vs voice")

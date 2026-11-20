"""WonderBuds show intro (plays before every episode): theme music + character lines + SFX -> audio.wav, timeline.json
usage: python3 build.py <tts_dir>"""
import json, os, sys, numpy as np, soundfile as sf
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", ".."))
from voice import render
from sound import *
B = json.load(open(os.path.join(HERE, "..", "bible.json"))); TTS = sys.argv[1]; FPS = 30
BPM = 120; beat = 60 / BPM; bar = 4 * beat
SEGS = [("title", 0, 3), ("rosie", 3, 4), ("pudding", 7, 4), ("ollie", 11, 4), ("clover", 15, 4), ("ziggy", 19, 4), ("finale", 23, 4)]  # (name, start bar, bars)
DUR = (27 * bar) + 1.5
LINES = [  # (speaker, segment, seconds after segment start, text, mood)
 ("all", "title", 2.2, "Hey hey! It's the WonderBuds!", "excited"),
 ("rosie", "rosie", 1.6, "I'm Rosie! I lead the way… so follow ME!", "excited"),
 ("pudding", "pudding", 1.5, "I'm Pudding! I bring the giggles… and the SNACKS! Hee hee!", "giggly"),
 ("ollie", "ollie", 1.5, "Hmm… I'm Ollie. Got a puzzle? I'll solve it!", "calm"),
 ("clover", "clover", 1.6, "Um… I'm Clover. And I can hear EVERYTHING!", "nervous"),
 ("ziggy", "ziggy", 1.3, "I'm Ziggy! Ready? Ready! READY! Zoom zoom!", "excited"),
 ("all", "finale", 1.0, "Together, we're the WonderBuds!", "excited"),
 ("all", "finale", 4.6, "Let's go, WonderBuds!", "shout")]
CAST = ["rosie", "pudding", "ollie", "clover", "ziggy"]
N = int(DUR * SR); voice = np.zeros(N, np.float32); music = np.zeros(N, np.float32); fx = np.zeros(N, np.float32)
segT = {n: (s * bar, (s + l) * bar) for n, s, l in SEGS}
vis = {c: {"o": np.zeros(int(DUR * FPS) + 2, np.float32), "w": np.zeros(int(DUR * FPS) + 2, np.float32)} for c in CAST}
tl_lines = []
for i, (sp, seg, off, text, mood) in enumerate(LINES):
    t0 = segT[seg][0] + off; who = CAST if sp == "all" else [sp]; clips = []
    for k, c in enumerate(who):
        y = render(text, B["characters"][c]["voice"], TTS, mood, seed=i * 7 + k); clips.append(y)
        o, w = visemes(y, FPS); f0 = int(t0 * FPS) + (k * 1 if sp == "all" else 0); n = min(len(o), len(vis[c]["o"]) - f0)
        vis[c]["o"][f0:f0 + n] = np.maximum(vis[c]["o"][f0:f0 + n], o[:n]); vis[c]["w"][f0:f0 + n] = w[:n]
    L = max(len(y) for y in clips)
    for k, y in enumerate(clips): place(voice, t0 + (k * .012 if sp == "all" else 0), y, (1.0 if sp != "all" else .5))
    d = L / SR; words = text.split(); wts = [len(w.strip(".,!?…")) + 2 for w in words]; acc = 0; ws = []
    for w, wt in zip(words, wts): ws.append({"w": w, "s": round(t0 + d * acc / sum(wts), 3)}); acc += wt
    tl_lines.append({"sp": sp, "seg": seg, "text": text, "start": round(t0, 3), "end": round(t0 + d, 3), "words": ws, "mood": mood})

# ------------------------------------------------------------------ theme song (original): C - Am - F - G, 120 BPM
CH = [(48, [60, 64, 67]), (45, [57, 60, 64]), (41, [57, 60, 65]), (43, [55, 59, 62])]
HOOK = [[72, None, 72, 74, 76, None, 72, None], [76, None, 76, 77, 79, None, 76, None], [77, None, 77, 76, 74, None, 72, None], [74, None, 76, 74, 71, None, 67, None]]
FANFARE = [[67, None, 72, None, 76, None, 79, None], [79, None, 76, None, 72, None, None, None], [77, None, 81, None, 79, None, 77, None], [74, 76, 77, None, 79, None, None, None]]
nb = int(DUR / bar)
def seg_at(b):
    for n, s, l in SEGS:
        if s <= b < s + l: return n, b - s
    return "end", 0
for b in range(nb):
    t0 = b * bar; root, tri = CH[b % 4]; seg, bi = seg_at(b); soft = seg == "clover"
    for k in range(4):  # groove
        place(music, t0 + k * beat, kick(), .55 if k % 2 == 0 else .35); place(music, t0 + k * beat, bass(root if k % 2 == 0 else root + 7, beat * .9), .5)
        if k % 2: place(music, t0 + k * beat, snare() if not soft else clap(), .3 if not soft else .15)
        for h in range(2): place(music, t0 + k * beat + h * beat / 2, hat() if not soft else shaker(), .5)
        for j, m in enumerate(tri): place(music, t0 + k * beat + j * .01, pluck(m, beat * .8, .55), .13)
    mel = HOOK[b % 4]
    if seg in ("title", "finale"):
        for k, m in enumerate(mel):
            if m: place(music, t0 + k * beat / 2, marimba(m, beat * 1.2), .32); place(music, t0 + k * beat / 2, glock(m + 12, .6), .07 if seg == "finale" else 0)
        if seg == "finale": place(music, t0, brass(tri[0] + 12, bar * .9), .08)
    elif seg == "rosie":
        for k, m in enumerate(FANFARE[bi]):
            if m: place(music, t0 + k * beat / 2, brass(m, beat * .9), .16)
    elif seg == "pudding":
        for k in range(4): place(music, t0 + k * beat, tuba(root - 12 + (7 if k % 2 else 0), beat * .7), .4)
        for k, m in enumerate(mel):
            if m and k % 2 == 0: place(music, t0 + k * beat / 2, marimba(m - 12, beat), .22)
    elif seg == "ollie":
        arp = (tri + [t + 12 for t in tri])
        for k in range(8): place(music, t0 + k * beat / 2, pluck(arp[k % 6] + 12, beat * .6, .3), .2)
    elif seg == "clover":
        for k in range(4): place(music, t0 + k * beat, musicbox(tri[k % 3] + 24, 1.4), .2)
        place(music, t0 + 3.5 * beat, musicbox(tri[2] + 24 + 5, 1.2), .12)
    elif seg == "ziggy":
        scale = [0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17, 19, 21, 23, 24, 26]
        for k in range(16): place(music, t0 + k * beat / 4, xylo(tri[0] + 12 + scale[(k + bi * 3) % 16], .25), .2)
# end hit
place(music, nb * bar - .02, marimba(72, 1.5) + marimba(76, 1.5) + marimba(79, 1.5), .35); place(music, nb * bar, glock(96, 1.5), .15)

# ------------------------------------------------------------------ SFX cues (per segment)
for n, s, l in SEGS[1:]:
    t0 = s * bar; place(fx, t0 - .35, sfx("whoosh"), .7); place(fx, t0 - .2, sfx("slide_up" if n != "finale" else "zoom"), .5)
place(fx, .1, sfx("slide_up"), .6); place(fx, 1.0, sfx("sparkle"), .6); place(fx, 1.9, sfx("pop"), .7)
st = lambda n: segT[n][0]
place(fx, st("rosie") + .9, sfx("ding"), .4); place(fx, st("rosie") + 5.2, sfx("boing"), .5)
place(fx, st("pudding") + 1.0, sfx("chomp"), .7); place(fx, st("pudding") + 5.0, sfx("propeller"), .7); place(fx, st("pudding") + 6.3, sfx("boing"), .6)
place(fx, st("ollie") + 4.2, sfx("bulb"), .8); place(fx, st("ollie") + 6.0, sfx("pop"), .5)
place(fx, st("clover") + 4.3, sfx("flutter"), .7); place(fx, st("clover") + 5.4, sfx("giggle"), .6)
place(fx, st("ziggy") + .2, sfx("creak"), .7); place(fx, st("ziggy") + 4.6, sfx("zoom"), .7); place(fx, st("ziggy") + 6.4, sfx("boing"), .5)
place(fx, st("finale") + 4.4, sfx("confetti"), .8); place(fx, st("finale") + 5.0, sfx("cheer"), .7)

v_env = np.convolve(np.abs(voice), np.ones(2400) / 2400, mode="same"); duck = 1 - .5 * np.clip(v_env * 10, 0, 1)
mix = voice * 1.05 + music * .55 * duck + fx * .55
x = np.arange(N) / SR; mix *= np.clip((DUR - x) / .6, 0, 1); mix = mix / (np.abs(mix).max() + 1e-6) * .89
sf.write(os.path.join(HERE, "audio.wav"), mix.astype(np.float32), SR)
json.dump({"width": 1920, "height": 1080, "fps": 60, "vis_fps": FPS, "crf": 18, "duration": round(DUR, 3), "bpm": BPM, "bar": bar,
           "segs": [{"name": n, "start": s * bar, "end": (s + l) * bar} for n, s, l in SEGS], "lines": tl_lines,
           "vis": {c: {"o": [round(float(v), 2) for v in d["o"]], "w": [round(float(v), 2) for v in d["w"]]} for c, d in vis.items()}},
          open(os.path.join(HERE, "timeline.json"), "w"))
print("intro %.1f s" % DUR)

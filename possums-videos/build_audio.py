"""Builds voiceover + music + SFX for an episode and writes timeline.json.

usage: python3 build_audio.py <episode_dir> <tts_dir>
"""
import json, os, re, sys
import numpy as np
import soundfile as sf

SR = 24000
ep_dir, tts_dir = sys.argv[1], sys.argv[2]
script = json.load(open(os.path.join(ep_dir, "script.json")))

# ---------------------------------------------------------------- voice
from kokoro_onnx import Kokoro
kok = Kokoro(os.path.join(tts_dir, "kokoro.onnx"), os.path.join(tts_dir, "voices.bin"))

LEAD, GAP, TAIL = 0.35, 0.22, 1.5
lines, clips, t = [], [], LEAD
for ln in script["lines"]:
    audio, sr = kok.create(ln["text"], voice=script["voice"], speed=script["speed"], lang="en-us")
    assert sr == SR
    audio = np.asarray(audio, dtype=np.float32)
    # trim silence
    nz = np.where(np.abs(audio) > 0.01)[0]
    audio = audio[max(0, nz[0] - 600): nz[-1] + 1200]
    dur = len(audio) / SR
    # approximate word timings, weighted by letters (+ pause weight on punctuation)
    words = ln["text"].split()
    weights = []
    for w in words:
        wt = len(re.sub(r"[^A-Za-z0-9]", "", w)) + 2.0
        if re.search(r"[.,!?]$", w):
            wt += 3.0
        weights.append(wt)
    tot = sum(weights)
    wt_times, acc = [], 0.0
    for w, wt in zip(words, weights):
        wt_times.append({"w": w, "s": round(t + dur * acc / tot, 3)})
        acc += wt
    lines.append({**ln, "start": round(t, 3), "end": round(t + dur, 3), "words": wt_times})
    clips.append((t, audio))
    t += dur + GAP
total = t - GAP + TAIL
N = int(total * SR)
voice = np.zeros(N, np.float32)
for st, a in clips:
    i = int(st * SR)
    voice[i:i + len(a)] += a

# ---------------------------------------------------------------- synth helpers
def tt(d):
    return np.arange(int(d * SR)) / SR

def env(n, a=0.005, r=0.08):
    e = np.ones(n, np.float32)
    na, nr = max(1, int(a * SR)), max(1, int(r * SR))
    e[:na] = np.linspace(0, 1, na)
    e[-nr:] *= np.linspace(1, 0, nr)
    return e

def sq(f, d, duty=0.5):
    x = tt(d)
    return np.where((x * f) % 1 < duty, 1.0, -1.0).astype(np.float32)

def sine(f, d):
    return np.sin(2 * np.pi * f * tt(d)).astype(np.float32)

def sweep(f0, f1, d, kind="sine"):
    x = tt(d)
    f = np.linspace(f0, f1, len(x))
    ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) if kind == "sine" else np.sign(np.sin(ph))).astype(np.float32)

rng = np.random.default_rng(7)
def noise(d):
    return rng.uniform(-1, 1, int(d * SR)).astype(np.float32)

def lowpass(x, k=8):
    return np.convolve(x, np.ones(k) / k, mode="same").astype(np.float32)

def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)

# ---------------------------------------------------------------- music (original chiptune loop)
BPM = 128
beat = 60 / BPM
step = beat / 2  # eighth notes
prog = [(60, [0, 4, 7]), (55, [0, 4, 7]), (57, [0, 3, 7]), (53, [0, 4, 7])]  # C G Am F
lead_pat = [12, None, 16, 19, 16, None, 14, 12, 12, None, 19, None, 16, 14, 12, None]
music = np.zeros(N, np.float32)
bar_len = 8 * step
nbars = int(total / bar_len) + 1
for b in range(nbars):
    root, chord = prog[b % 4]
    b0 = b * bar_len
    for s in range(8):
        st = b0 + s * step
        i = int(st * SR)
        # bass: root/octave bounce
        bn = root - 24 + (12 if s % 2 else 0)
        n = sq(mtof(bn), step * 0.9, 0.5) * env(int(step * 0.9 * SR), r=0.03) * 0.22
        # arp
        an = root + chord[s % 3] + 12
        a = sq(mtof(an), step * 0.5, 0.25) * env(int(step * 0.5 * SR), r=0.04) * 0.08
        # drums
        d = np.zeros(1, np.float32)
        if s % 4 == 0:
            d = sweep(150, 45, 0.16) * env(int(0.16 * SR), r=0.12) * 0.55
        elif s % 4 == 2:
            d = lowpass(noise(0.12), 3) * env(int(0.12 * SR), r=0.1) * 0.25
        hat = noise(0.03) * env(int(0.03 * SR), r=0.025) * 0.06
        for sig in (n, a, d, hat):
            if i < N:
                j = min(N, i + len(sig)); music[i:j] += sig[: j - i]
    # lead melody every other pair of bars
    if (b // 2) % 2 == 1:
        for s in range(8):
            m = lead_pat[(b % 2) * 8 + s]
            if m is None:
                continue
            st = b0 + s * step
            i = int(st * SR)
            sig = sq(mtof(root + m), step * 0.85, 0.125) * env(int(step * 0.85 * SR), r=0.05) * 0.06
            if i < N:
                j = min(N, i + len(sig)); music[i:j] += sig[: j - i]

# duck under voice
v_env = np.convolve(np.abs(voice), np.ones(2400) / 2400, mode="same")
duck = np.clip(1.0 - (v_env > 0.004) * 0.6, 0.4, 1.0)
duck = np.convolve(duck, np.ones(4800) / 4800, mode="same")
music *= duck
fade = int(1.5 * SR)
music[-fade:] *= np.linspace(1, 0, fade)
music[: int(0.2 * SR)] *= np.linspace(0, 1, int(0.2 * SR))

# ---------------------------------------------------------------- sfx
def sfx(name):
    if name == "whoosh":
        x = lowpass(noise(0.45), 6); return x * np.sin(np.linspace(0, np.pi, len(x))) * 0.5
    if name == "stamp":
        return sweep(120, 40, 0.25) * env(int(0.25 * SR), r=0.2) * 0.9
    if name == "pop":
        return sweep(400, 1200, 0.07) * env(int(0.07 * SR), r=0.05) * 0.5
    if name == "swipe":
        x = lowpass(noise(0.25), 3); return x * np.linspace(0.1, 1, len(x)) * env(len(x), r=0.08) * 0.35
    if name == "cash":
        a = sine(2093, 0.5) * np.exp(-tt(0.5) * 7) + sine(2637, 0.5) * np.exp(-tt(0.5) * 7)
        click = noise(0.04) * 0.6
        out = np.zeros(int(0.6 * SR), np.float32); out[:len(click)] += click
        out[int(0.08 * SR):int(0.08 * SR) + len(a)] += a * 0.5
        return out * 0.6
    if name == "ding":
        return (sine(1568, 0.8) + 0.5 * sine(3136, 0.8)) * np.exp(-tt(0.8) * 5) * 0.4
    if name == "spend":
        return np.concatenate([sq(mtof(m), 0.08, 0.5) * env(int(0.08 * SR), r=0.02) for m in (76, 72, 67, 60)]) * 0.18
    if name == "boing":
        x = tt(0.35); f = 300 + 120 * np.sin(2 * np.pi * 14 * x) * np.exp(-x * 6)
        return np.sin(2 * np.pi * np.cumsum(f) / SR).astype(np.float32) * env(len(x), r=0.1) * 0.4
    if name == "honk":
        return (sq(370, 0.45, 0.5) + sq(466, 0.45, 0.5)) * env(int(0.45 * SR), r=0.05) * 0.12
    if name == "crowd":
        x = lowpass(noise(2.2), 14) * 2.5
        return x * np.sin(np.linspace(0, np.pi, len(x))) ** 0.6 * 0.5
    if name == "whistle":
        x = tt(0.6); f = 2800 + 140 * np.sign(np.sin(2 * np.pi * 30 * x))
        return np.sin(2 * np.pi * np.cumsum(f) / SR).astype(np.float32) * env(len(x), r=0.05) * 0.18
    if name == "scream":
        x = tt(0.9); f = 900 + 250 * np.sin(2 * np.pi * 9 * x) + 300 * x
        s = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)).astype(np.float32)
        return lowpass(s, 5) * env(len(x), r=0.2) * 0.12
    if name == "slide":
        return sweep(1400, 300, 0.7) * env(int(0.7 * SR), r=0.1) * 0.3
    if name == "horn":
        return (sq(233, 1.0, 0.5) + sq(294, 1.0, 0.5) + sq(349, 1.0, 0.5)) * env(int(1.0 * SR), r=0.15) * 0.08
    if name == "squawk":
        x = tt(0.35); f = 1100 + 500 * np.sin(2 * np.pi * 18 * x)
        return lowpass(np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)).astype(np.float32), 4) * env(len(x), r=0.1) * 0.18
    if name == "bonk":
        return (sweep(700, 180, 0.22) + sine(180, 0.22) * 0.5) * env(int(0.22 * SR), r=0.18) * 0.6
    if name == "kick":
        return sweep(200, 60, 0.12) * env(int(0.12 * SR), r=0.1) * 0.7 + 0
    if name == "glass":
        x = noise(0.7) * np.exp(-tt(0.7) * 6)
        tinks = sum(sine(f, 0.7) * np.exp(-tt(0.7) * d) for f, d in ((3500, 9), (4700, 12), (5900, 7)))
        return (x * 0.4 + tinks * 0.15).astype(np.float32)
    if name == "sad":
        return np.concatenate([sq(mtof(m), d, 0.5) * env(int(d * SR), r=0.05) for m, d in ((67, 0.3), (66, 0.3), (65, 0.3), (64, 0.9))]) * 0.12
    if name == "boo":
        x = tt(1.6); base = sum(np.sign(np.sin(2 * np.pi * f * x + ph)) for f, ph in ((110, 0), (123, 1), (98, 2), (131, 3)))
        wob = 1 + 0.08 * np.sin(2 * np.pi * 3 * x)
        return lowpass((base * wob).astype(np.float32), 30) * np.sin(np.linspace(0, np.pi, len(x))) * 0.12 + lowpass(noise(1.6), 20) * 0.6 * np.sin(np.linspace(0, np.pi, len(x)))
    raise KeyError(name)

def word_time(ln, frac):
    """frac is a 0-1 fraction of the line, or "@word" to anchor on a spoken word."""
    if isinstance(frac, str):
        key = frac[1:].lower()
        for w in ln["words"]:
            if re.sub(r"[^a-z0-9]", "", w["w"].lower()).startswith(key):
                return w["s"]
        raise KeyError(f"word {key!r} not in line {ln['text']!r}")
    return ln["start"] + frac * (ln["end"] - ln["start"])

fx = np.zeros(N, np.float32)
for ln in lines:
    for name, frac in ln.get("sfx", []):
        st = word_time(ln, frac)
        s = sfx(name).astype(np.float32)
        i = int(st * SR); j = min(N, i + len(s))
        fx[i:j] += s[: j - i]
    ln["sfx_times"] = [[n, round(word_time(ln, f), 3)] for n, f in ln.get("sfx", [])]

mix = voice * 1.3 + music * 0.035 + fx * 0.09
mix = np.tanh(mix * 1.1) * 0.9
def _db(x):
    x = x[np.abs(x) > 1e-4]
    return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)
vdb = _db(voice * 1.3)
print("LEVELS vs voice: music %+.1f dB, sfx %+.1f dB" % (_db(music * 0.035) - vdb, _db(fx * 0.09) - vdb))
sf.write(os.path.join(ep_dir, "audio.wav"), mix, SR)
json.dump({"duration": round(total, 3), "lines": lines}, open(os.path.join(ep_dir, "timeline.json"), "w"), indent=1)
print("duration", round(total, 2), "s")

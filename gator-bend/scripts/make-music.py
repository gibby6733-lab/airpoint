"""Synthesized score + foley for an episode (no samples, no downloads).

Plucked strings use the Karplus-Strong algorithm. Writes one track, public/sfx/music.wav:
  - opening strum sting, a light strummed bed that ducks under dialogue, a title sting
  - footsteps on walk-in steps, clacks when the gator chomps its pool noodle

usage: make-music.py <timeline.json> <out.wav>
"""
import json
import sys
import wave

import numpy as np

SR = 44100
rng = np.random.default_rng(7)
tl = json.load(open(sys.argv[1]))
fps = tl["fps"]
total = tl["durationInFrames"] / fps
out = np.zeros(int(SR * (total + 1.5)))


def midi(n: float) -> float:
    return 440.0 * 2 ** ((n - 69) / 12)


def pluck(freq: float, dur: float, decay: float = 0.996, bright: float = 0.5) -> np.ndarray:
    n = max(2, int(SR / freq))
    sig = np.zeros(int(SR * dur) + n + 1)
    sig[:n] = rng.uniform(-1, 1, n)
    # soften the attack a bit (less "8-bit")
    sig[1:n] = bright * sig[1:n] + (1 - bright) * sig[: n - 1]
    i = n
    while i < len(sig):
        j = min(len(sig), i + n)
        prev = sig[i - n : j - n]
        prev2 = sig[i - n - 1 : j - n - 1] if i - n - 1 >= 0 else np.concatenate([[0.0], sig[i - n : j - n - 1]])
        sig[i:j] = decay * 0.5 * (prev + prev2)
        i = j
    return sig[: int(SR * dur)]


def add(sig: np.ndarray, t: float, gain: float = 1.0) -> None:
    a = int(t * SR)
    if a >= len(out):
        return
    b = min(len(out), a + len(sig))
    out[a:b] += sig[: b - a] * gain


# ukulele-ish voicings (high re-entrant G)
CHORDS = {
    "C": [67, 60, 64, 72],
    "G": [67, 62, 67, 71],
    "Am": [69, 60, 64, 69],
    "F": [69, 60, 65, 69],
    "D": [69, 62, 66, 69],
}


def strum(chord: str, t: float, gain: float, down: bool = True, ring: float = 1.2) -> None:
    notes = CHORDS[chord] if down else CHORDS[chord][::-1]
    for k, n in enumerate(notes):
        add(pluck(midi(n), ring), t + k * 0.012, gain * (0.9 if k else 1.0))


# --- dialogue ducking envelope ---------------------------------------------------
lines = [(b["start"] / fps, b["end"] / fps) for b in tl["beats"] if b["type"] == "line"]
title = next((b for b in tl["beats"] if b["type"] == "title"), None)
title_t = title["start"] / fps if title else total


def duck(t: float) -> float:
    return 0.33 if any(s - 0.1 <= t <= e + 0.1 for s, e in lines) else 0.75


# --- opening sting ---------------------------------------------------------------
for k, (c, dt) in enumerate([("C", 0.0), ("C", 0.16), ("G", 0.32), ("C", 0.56)]):
    strum(c, dt, 0.22, down=k % 2 == 0, ring=1.4)

# --- bed: island strum, C G Am F, 104 bpm ----------------------------------------
beat = 60 / 104
pattern = [(0, True, 1.0), (1, True, 0.7), (1.5, False, 0.5), (2.5, False, 0.5), (3, True, 0.7), (3.5, False, 0.5)]
prog = ["C", "G", "Am", "F"]
bar = 0
t0 = 4 * beat * 0.5
while t0 + bar * 4 * beat < title_t - 0.2:
    chord = prog[bar % 4]
    for pos, down, acc in pattern:
        t = t0 + (bar * 4 + pos) * beat
        if t < title_t - 0.2:
            strum(chord, t, 0.085 * acc * duck(t), down=down, ring=0.6)
    bar += 1

# --- title sting: big strum + resolve ----------------------------------------------
if title:
    for k, (c, dt) in enumerate([("G", 0.0), ("G", 0.12), ("C", 0.3)]):
        strum(c, title_t + dt, 0.3 if k == 2 else 0.2, down=True, ring=1.6 if k == 2 else 0.5)

# --- foley -------------------------------------------------------------------------
def thump() -> np.ndarray:
    t = np.arange(int(SR * 0.09)) / SR
    return (np.sin(2 * np.pi * 85 * t) * np.exp(-t * 45) + 0.3 * rng.uniform(-1, 1, len(t)) * np.exp(-t * 120)) * 0.5


def clack() -> np.ndarray:
    t = np.arange(int(SR * 0.05)) / SR
    noise = rng.uniform(-1, 1, len(t))
    tone = np.sin(2 * np.pi * 1300 * t) * 0.5
    return (noise * 0.6 + tone) * np.exp(-t * 90) * 0.35


for b in tl["beats"]:
    if b.get("action") == "walk-in":
        for f in range(b["start"], b["end"], 6):
            add(thump(), f / fps + 3 / fps, 0.9)

burp = next((b for b in tl["beats"] if b.get("action") == "gator-burp"), None)
for f in range(12, int(title_t * fps), 24):  # jaw snaps shut on these frames (see gatorState)
    if burp and burp["start"] - 6 <= f <= burp["end"]:
        continue
    add(clack(), f / fps, 0.5)

def write(buf: np.ndarray, path: str, level: float) -> None:
    peak = np.max(np.abs(buf)) or 1
    pcm = (np.clip(buf / peak * level, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


write(out[: int(SR * total)], sys.argv[2], 0.5)

# --- opening-titles jingle (INTRO_SECONDS long, cue points match src/Intro.tsx) ------
INTRO_SECONDS = 7.5
CARD_TIMES = [0.25, 1.5, 2.75, 4.0]
LOGO_T = 5.25
out = np.zeros(int(SR * (INTRO_SECONDS + 1)))
beat = 60 / 124
prog = ["C", "F", "G", "C", "F", "G", "Am", "G"]
t, k = 0.0, 0
while t < LOGO_T - 0.1:
    chord = prog[(k // 2) % len(prog)]
    strum(chord, t, 0.12 if k % 2 == 0 else 0.07, down=k % 2 == 0, ring=0.45)
    t += beat / 2
    k += 1
for n, ct in zip([72, 76, 79, 84], CARD_TIMES):  # rising pluck as each card slaps down
    add(pluck(midi(n), 0.9, decay=0.997, bright=0.8), ct, 0.35)
    add(pluck(midi(n + 12), 0.5, decay=0.995, bright=0.8), ct + 0.08, 0.15)
for i, n in enumerate([60, 64, 67, 72, 76, 79, 84]):  # logo: big strum + run up
    add(pluck(midi(n), 2.2, decay=0.998), LOGO_T + i * 0.025, 0.3)
for i, n in enumerate([79, 81, 83, 84]):
    add(pluck(midi(n), 0.6, decay=0.996, bright=0.8), LOGO_T + 0.6 + i * 0.09, 0.22)
write(out[: int(SR * INTRO_SECONDS)], sys.argv[2].replace("music.wav", "intro.wav"), 0.55)

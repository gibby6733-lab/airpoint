"""Lip-sync + caption timing for one recorded line (free, offline).

1. Whisper (faster-whisper base.en) finds when each word was actually spoken.
2. Script words are matched to the heard words, so captions land on the real timing.
3. Each spoken word is split into phonemes (espeak-ng) spread across the word,
   and every phoneme becomes a mouth shape (viseme). Quiet frames close the mouth.

usage: align.py <audio> <spoken text> <caption text> <fps>
prints JSON: {"words": [{word,start,end}], "mouth": [shape per frame], "heard": "..."}
"""
import json
import os
import re
import subprocess
import sys
from difflib import SequenceMatcher
from pathlib import Path

import numpy as np

os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
from faster_whisper import WhisperModel  # noqa: E402

audio_path, spoken, caption, fps = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
models = Path(__file__).resolve().parent.parent / "models" / "whisper"

raw = subprocess.run(
    ["ffmpeg", "-loglevel", "error", "-i", audio_path, "-f", "f32le", "-ac", "1", "-ar", "16000", "-"],
    capture_output=True,
    check=True,
).stdout
audio = np.frombuffer(raw, np.float32)
duration = len(audio) / 16000
frames = int(np.ceil(duration * fps))

model = WhisperModel("base.en", device="cpu", compute_type="int8", download_root=str(models))
segments, _ = model.transcribe(audio, word_timestamps=True)  # no prompt: hear what was really said
heard = [(w.word.strip(), float(w.start), float(w.end)) for s in segments for w in s.words]


def norm(w: str) -> str:
    return re.sub(r"[^a-z0-9]", "", w.lower())


def align(tokens: list[str]) -> list[tuple[str, float, float]]:
    """Give every token a start/end taken from the matching heard word, interpolating gaps."""
    a = [norm(t) for t in tokens]
    b = [norm(h[0]) for h in heard]
    times: list[tuple[float, float] | None] = [None] * len(tokens)
    for blk in SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for k in range(blk.size):
            h = heard[blk.b + k]
            times[blk.a + k] = (h[1], h[2])
    # fill unmatched runs by spreading them across the gap between known neighbours
    i = 0
    while i < len(tokens):
        if times[i] is not None:
            i += 1
            continue
        j = i
        while j < len(tokens) and times[j] is None:
            j += 1
        t0 = times[i - 1][1] if i > 0 else (heard[0][1] if heard else 0.0)
        t1 = times[j][0] if j < len(tokens) else (heard[-1][2] if heard else duration)
        if t1 <= t0:
            t1 = t0 + 0.15 * (j - i)
        step = (t1 - t0) / (j - i)
        for k in range(i, j):
            times[k] = (t0 + step * (k - i), t0 + step * (k - i + 1))
        i = j
    return [(tokens[k], times[k][0], times[k][1]) for k in range(len(tokens))]


spoken_words = align(spoken.split())
caption_words = align(caption.split())

# loudness per video frame; used to stretch the last word and to close the mouth on silence
per = 16000 // fps
rms = np.array([np.sqrt(np.mean(audio[f * per : (f + 1) * per] ** 2) + 1e-12) for f in range(frames)])
voiced = np.nonzero(rms > 0.06 * rms.max())[0]
if len(voiced):
    # recognizers tend to end the final word early; run it to the end of the actual sound
    sound_end = (voiced[-1] + 1) / fps
    for lst in (spoken_words, caption_words):
        w, s0, e0 = lst[-1]
        if e0 < sound_end:
            lst[-1] = (w, s0, sound_end)

# --- visemes ---------------------------------------------------------------
VISEME = [
    (("m", "b", "p"), "closed"),
    (("f", "v"), "F"),
    (("oʊ", "aʊ", "ɔ", "o", "u", "ʊ", "w", "ɒ", "ɹ", "r", "ɔɪ"), "O"),
    (("aɪ", "a", "æ", "ɑ", "ʌ", "ɐ"), "wide"),
    (("eɪ", "i", "s", "z", "θ", "ð", "ʃ", "ʒ", "tʃ", "dʒ"), "E"),
]
VOWELS = set("aeiouæɑɐɒɔəɛɜɪʊʌ")


def phonemes(word: str) -> list[str]:
    ipa = subprocess.run(
        ["espeak-ng", "-q", "--ipa", "-v", "en-us", word], capture_output=True, text=True
    ).stdout
    ipa = re.sub(r"[ˈˌːˑ\s\-_]", "", ipa)
    out, i = [], 0
    two = {"aɪ", "aʊ", "eɪ", "oʊ", "ɔɪ", "tʃ", "dʒ"}
    while i < len(ipa):
        if ipa[i : i + 2] in two:
            out.append(ipa[i : i + 2])
            i += 2
        else:
            out.append(ipa[i])
            i += 1
    return [p for p in out if p.strip()]


def viseme(p: str) -> str:
    for keys, shape in VISEME:
        if p in keys:
            return shape
    return "open"  # soft vowels and n/l/k/g/h/t/d: relaxed open mouth


mouth = ["closed"] * frames
for word, t0, t1 in spoken_words:
    ph = phonemes(re.sub(r"[^A-Za-z']", " ", word).strip() or word)
    if not ph:
        continue
    weights = [2.0 if any(c in VOWELS for c in p) else 1.0 for p in ph]
    total = sum(weights)
    t = t0
    for p, w in zip(ph, weights):
        d = (t1 - t0) * w / total
        for f in range(int(t * fps), min(frames, int(np.ceil((t + d) * fps)))):
            mouth[f] = viseme(p)
        t += d

# close the mouth on real silence (pauses, breaths) but not on soft consonants like f/s
quiet = rms < 0.035 * rms.max()
mouth = ["closed" if quiet[f] and m not in ("F", "E") else m for f, m in enumerate(mouth)]
# on twos: hold every mouth for two frames
mouth = [mouth[f - (f % 2)] for f in range(frames)]

print(
    json.dumps(
        {
            "words": [{"word": w, "start": s, "end": e} for w, s, e in caption_words],
            "mouth": mouth,
            "heard": " ".join(h[0] for h in heard),
        }
    )
)

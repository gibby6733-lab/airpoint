"""Shared character-voice renderer for kids3d / WonderBuds.

Kokoro TTS reads each sentence, then the WORLD vocoder re-synthesises it:
  pitch    - multiplies pitch (younger = higher) WITHOUT the sped-up "chipmunk" effect
  formant  - shifts vocal-tract resonances up (a smaller, child-sized voice)
  expr     - exaggerates intonation around the speaker's average pitch (livelier)
  breath   - adds breathiness (soft voices)
Natural delivery on top of that:
  * sentence-by-sentence rendering with small speed variation and real pauses ("…" = thinking pause)
  * EMPHASIS: a word in CAPS (or *word*) is said higher and louder
  * mood per line: excited, whisper, giggly, nervous, sad, shout, calm (or the profile default)
Profiles live in wonderbuds/bible.json -> characters.<id>.voice and never change between episodes.
"""
import re, numpy as np, pyworld as pw
SR = 24000
_kok = None
MOODS = {  # pitch x, intonation x, speed x, breath +, gain x
    None: (1, 1, 1, 0, 1), "calm": (.97, .85, .95, 0, .9), "excited": (1.09, 1.25, 1.07, 0, 1.1), "shout": (1.13, 1.2, 1.04, 0, 1.2),
    "whisper": (1.0, .7, .92, .45, .55), "giggly": (1.1, 1.35, 1.05, .1, 1.0), "nervous": (1.04, .8, .9, .12, .85), "sad": (.92, .7, .86, .08, .8)}

def kokoro(tts_dir):
    global _kok
    if _kok is None:
        import os
        from kokoro_onnx import Kokoro
        _kok = Kokoro(os.path.join(tts_dir, "kokoro.onnx"), os.path.join(tts_dir, "voices.bin"))
    return _kok

def warp_envelope(sp, alpha):
    n = sp.shape[1]; src = np.arange(n) / alpha; out = np.empty_like(sp)
    for i in range(sp.shape[0]): out[i] = np.interp(src, np.arange(n), sp[i], right=sp[i, -1])
    return out

def _sentence(text, prof, tts_dir, mood, seed):
    mp, me, ms, mb, mg = MOODS.get(mood, MOODS[None]); rng = np.random.default_rng(seed)
    words = text.split(); emph = [bool(re.sub(r"[^A-Za-z]", "", w)) and (re.sub(r"[^A-Za-z]", "", w).isupper() and len(re.sub(r"[^A-Za-z]", "", w)) > 1 or w.startswith("*")) for w in words]
    spoken = " ".join(w.strip("*").capitalize() if e and w.strip("*").isupper() else w.strip("*") for w, e in zip(words, emph))
    speed = prof.get("speed", 1.0) * ms * (1 + rng.uniform(-.05, .05))
    a, sr = kokoro(tts_dir).create(spoken, voice=prof["voice"], speed=speed, lang="en-us"); x = np.asarray(a, np.float64)
    nz = np.where(np.abs(x) > .01)[0]
    if len(nz): x = x[max(0, nz[0] - 300): nz[-1] + 600]
    f0, t = pw.harvest(x, SR, f0_floor=60, f0_ceil=600, frame_period=5.0); sp = pw.cheaptrick(x, f0, t, SR); ap = pw.d4c(x, f0, t, SR)
    v = f0 > 0; f0n = f0.copy(); gain = np.ones(len(f0))
    if v.any():
        lf = np.log(f0[v]); m = np.median(lf); lf = m + (lf - m) * prof.get("expr", 1.0) * me; f0n[v] = np.exp(lf) * prof.get("pitch", 1.0) * mp
    # emphasis: map each word to its share of the sentence by letter count
    if any(emph):
        wts = np.array([len(w) + 1 for w in words], float); edges = np.concatenate([[0], np.cumsum(wts)]) / wts.sum() * len(f0)
        for i, e in enumerate(emph):
            if not e: continue
            a0, a1 = int(edges[i]), int(edges[i + 1]); win = np.zeros(len(f0)); win[a0:a1] = 1; win = np.convolve(win, np.hanning(15) / np.hanning(15).sum(), "same")
            f0n = np.where(f0n > 0, f0n * (1 + .14 * win), 0); gain *= 1 + .35 * win
    sp = warp_envelope(sp, prof.get("formant", 1.0)) * (gain[:, None] ** 2)
    b = prof.get("breath", 0) + mb
    if b: ap = np.clip(ap + b, 0, 1)
    y = pw.synthesize(f0n, sp, ap, SR, frame_period=5.0).astype(np.float32) * mg
    return y

def render(text, prof, tts_dir, mood=None, seed=0):
    """Returns a float32 mono clip (SR 24 kHz). Text may contain '…' pauses, CAPS emphasis and a trailing '—' (cut off)."""
    cut = text.rstrip().endswith(("—", "-")); text = text.rstrip().rstrip("—-").strip()
    parts = [p for p in re.split(r"(?<=[.!?…])\s+", text) if p.strip()]
    out = []
    for i, p in enumerate(parts):
        thinking = p.endswith("…") or p.endswith("...")
        y = _sentence(p.replace("…", ",").replace("...", ","), prof, tts_dir, mood, seed * 31 + i); out.append(y)
        if i < len(parts) - 1: out.append(np.zeros(int(SR * (.5 if thinking else .16 + .08 * (i % 2))), np.float32))
    y = np.concatenate(out)
    if cut:  # cut off mid-word: quick fade so the next speaker can jump in
        y = y[:int(len(y) * .92)]; f = int(SR * .05); y[-f:] *= np.linspace(1, 0, f)
    return (y / (np.abs(y).max() + 1e-6) * 0.9 * min(1.0, MOODS.get(mood, MOODS[None])[4])).astype(np.float32)

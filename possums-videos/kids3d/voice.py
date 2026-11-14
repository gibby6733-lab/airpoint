"""Shared character-voice renderer for kids3d / WonderBuds.

Kokoro TTS reads the line at natural speed, then the WORLD vocoder re-synthesises it:
  pitch    - multiplies the voice's pitch (younger = higher) WITHOUT the sped-up "chipmunk" effect
  formant  - shifts the vocal-tract resonances up (a smaller, child-sized voice) while keeping it natural
  expr     - exaggerates the intonation around the speaker's average pitch (livelier, more cartoon-expressive)
  breath   - adds a little breathiness (soft voices)
Profiles live in wonderbuds/bible.json -> characters.<id>.voice and never change between episodes.
"""
import numpy as np, pyworld as pw
SR = 24000
_kok = None
def kokoro(tts_dir):
    global _kok
    if _kok is None:
        import os
        from kokoro_onnx import Kokoro
        _kok = Kokoro(os.path.join(tts_dir, "kokoro.onnx"), os.path.join(tts_dir, "voices.bin"))
    return _kok

def warp_envelope(sp, alpha):
    """Scale formant frequencies by alpha (>1 = smaller, younger vocal tract)."""
    n = sp.shape[1]; src = np.arange(n) / alpha; out = np.empty_like(sp)
    for i in range(sp.shape[0]): out[i] = np.interp(src, np.arange(n), sp[i], right=sp[i, -1])
    return out

def render(text, prof, tts_dir):
    a, sr = kokoro(tts_dir).create(text, voice=prof["voice"], speed=prof.get("speed", 1.0), lang="en-us")
    x = np.asarray(a, np.float64); assert sr == SR
    f0, t = pw.harvest(x, SR, f0_floor=60, f0_ceil=600, frame_period=5.0)
    sp = pw.cheaptrick(x, f0, t, SR); ap = pw.d4c(x, f0, t, SR)
    v = f0 > 0
    if v.any():
        lf = np.log(f0[v]); m = np.median(lf)
        lf = m + (lf - m) * prof.get("expr", 1.0)              # livelier intonation
        f0n = f0.copy(); f0n[v] = np.exp(lf) * prof.get("pitch", 1.0)
    else: f0n = f0
    sp = warp_envelope(sp, prof.get("formant", 1.0))
    if prof.get("breath"): ap = np.clip(ap + prof["breath"], 0, 1)
    y = pw.synthesize(f0n, sp, ap, SR, frame_period=5.0).astype(np.float32)
    nz = np.where(np.abs(y) > 0.01)[0]
    if len(nz): y = y[max(0, nz[0] - 400): nz[-1] + 1200]
    return y / (np.abs(y).max() + 1e-6) * 0.9

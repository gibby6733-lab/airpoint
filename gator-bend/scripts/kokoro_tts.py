"""Free neural voices (Kokoro-82M, Apache-2.0) for the voice stage.

usage: kokoro_tts.py "<text>" <voice> <speed> <out.wav>
voice can be one voice ("am_puck") or a blend ("am_puck:0.7,af_sky:0.3").
"""
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

root = Path(__file__).resolve().parent.parent / "models"
text, voice, speed, out = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]

voices_npz = root / "voices.npz"
if not voices_npz.exists():
    packs = {p.stem: np.fromfile(p, dtype=np.float32).reshape(-1, 1, 256) for p in (root / "voices").glob("*.bin")}
    np.savez(voices_npz, **packs)

tts = Kokoro(str(root / "kokoro.onnx"), str(voices_npz))
style = voice
if ":" in voice or "," in voice:
    parts = [v.split(":") for v in voice.split(",")]
    style = sum(tts.get_voice_style(name) * float(w) for name, w in parts)
samples, rate = tts.create(text, voice=style, speed=speed, lang="en-us")
sf.write(out, samples, rate)

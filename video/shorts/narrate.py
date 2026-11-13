"""Generate per-beat narration with Kokoro; tune speed so each Short lands at ~68s."""
import json, os, sys, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
from scripts import VIDEOS
KD = sys.argv[1]; VOICE = "bm_george"; GAP = 0.16; TARGET = 68.0
k = Kokoro(f"{KD}/kokoro-v1.0.onnx", f"{KD}/voices-v1.0.bin")
def trim(a, sr, thr=0.012):
    idx = np.where(np.abs(a) > thr)[0]
    if not len(idx): return a
    return a[max(0, idx[0] - int(0.03 * sr)): idx[-1] + int(0.08 * sr)]
def gen(v, speed):
    clips = []
    for b in v["beats"]:
        a, sr = k.create(b.get("say", b["cap"]), voice=VOICE, speed=speed, lang="en-gb")
        clips.append(trim(a, sr))
    return clips, sr
only = sys.argv[2:] 
for v in VIDEOS:
    if only and v["slug"] not in only: continue
    speed = 1.05
    for _ in range(3):
        clips, sr = gen(v, speed)
        total = sum(len(c) for c in clips) / sr + GAP * len(clips) + 0.3
        if 62 <= total <= 73: break
        speed = max(0.88, min(1.25, speed * total / TARGET))
    os.makedirs(f"build/{v['slug']}", exist_ok=True)
    meta = []
    for i, c in enumerate(clips):
        sf.write(f"build/{v['slug']}/{i:02d}.wav", c, sr); meta.append(len(c) / sr)
    json.dump(dict(speed=speed, sr=sr, durs=meta), open(f"build/{v['slug']}/narr.json", "w"))
    print(v["slug"], "speed", round(speed, 3), "total", round(total, 1), flush=True)

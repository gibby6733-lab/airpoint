"""Voice samples for the WonderBuds cast (permanent profiles in bible.json, rendered with ../voice.py).
usage: python3 voices.py <tts_dir> <out.wav>
Script lines: (speaker, text, mood). A line ending in '—' is interrupted: the next speaker starts slightly early."""
import json, os, sys, numpy as np, soundfile as sf
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from voice import render, SR
B = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "bible.json")))
def say(who, text, mood=None, seed=0): return render(text, B["characters"][who]["voice"], sys.argv[1], mood, seed)
lines = [
 ("rosie", "Hi! I'm Rosie the red panda… and I LOVE adventures. Let's go, WonderBuds!", "excited"),
 ("pudding", "And I'm Pudding! Hee hee hee. Ooh, is it snack time yet?", "giggly"),
 ("ollie", "Hello. I'm Ollie. Hmm… let me think. Yes. I'm the one who solves the puzzles.", None),
 ("clover", "Um… h-hi. I'm Clover. I can hear really, really well.", "nervous"),
 ("ziggy", "I'm Ziggy! Ready? Ready! READY! Zoom zoom!", "excited"),
 ("rosie", "Okay, everybody! Today we're going to find the—", None),
 ("ziggy", "Treasure? Is it treasure? I bet it's TREASURE!", "excited"),
 ("pudding", "Ooh, I hope it's cookie treasure.", "giggly"),
 ("ollie", "Statistically, it is probably not cookies, Pudding.", "calm"),
 ("clover", "Shh! Wait… did you guys hear that?", "whisper"),
 ("rosie", "WHOA. Okay. WonderBuds… let's go find out!", "excited")]
if __name__ == "__main__":
    out = np.zeros(0, np.float32)
    for i, (who, text, mood) in enumerate(lines):
        y = say(who, text, mood, i); overlap = int(SR * .12) if i and lines[i - 1][1].rstrip().endswith("—") else 0
        if overlap: start = len(out) - overlap; buf = np.zeros(start + len(y), np.float32); buf[:len(out)] = out; buf[start:start + len(y)] += y; out = buf
        else: out = np.concatenate([out, np.zeros(int(SR * (.35 + .1 * (i % 3))), np.float32) if i else np.zeros(0, np.float32), y])
    sf.write(sys.argv[2], out, SR); print("ok", round(len(out) / SR, 1), "s")

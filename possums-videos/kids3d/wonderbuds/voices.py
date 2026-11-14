"""Voice samples for the WonderBuds cast, using the permanent voice profiles in bible.json.
usage: python3 voices.py <tts_dir> <out.wav>"""
import json, os, sys, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
SR = 24000; here = os.path.dirname(os.path.abspath(__file__)); B = json.load(open(os.path.join(here, "bible.json")))
kok = Kokoro(os.path.join(sys.argv[1], "kokoro.onnx"), os.path.join(sys.argv[1], "voices.bin"))
def say(who, text):
    v = B["characters"][who]["voice"] if who in B["characters"] else B["narrator"]; p = v.get("pitch", 1.0)
    a, _ = kok.create(text, voice=v["voice"], speed=v["speed"] / p ** .5, lang="en-us"); a = np.asarray(a, np.float32)
    if p != 1: n = int(len(a) / p); a = np.interp(np.arange(n) * p, np.arange(len(a)), a).astype(np.float32)
    nz = np.where(np.abs(a) > .01)[0]; a = a[max(0, nz[0] - 400): nz[-1] + 1200]; return a / (np.abs(a).max() + 1e-6) * .9
lines = [("rosie", "Hi! I'm Rosie the red panda. Let's go, WonderBuds!"), ("pudding", "And I'm Pudding! Hee hee! Is it snack time yet?"),
         ("ollie", "Hello. I'm Ollie. Hmm, let me think. Yes, I love puzzles!"), ("clover", "H-hi. I'm Clover. I can hear really, really well."),
         ("ziggy", "I'm Ziggy! Ready? Ready! READY! Zoom zoom!"),
         ("rosie", "WonderBuds, are we ready for an adventure?"), ("ziggy", "Ready ready ready!"), ("pudding", "Can we bring snacks?"), ("ollie", "I've packed a map, a compass, and three sandwiches."), ("clover", "We can do it together!")]
out = []
for who, text in lines: out += [say(who, text), np.zeros(int(SR * .45), np.float32)]
sf.write(sys.argv[2], np.concatenate(out), SR); print("ok")

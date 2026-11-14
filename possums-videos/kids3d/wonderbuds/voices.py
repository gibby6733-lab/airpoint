"""Voice samples for the WonderBuds cast (permanent profiles in bible.json, rendered with ../voice.py).
usage: python3 voices.py <tts_dir> <out.wav>"""
import json, os, sys, numpy as np, soundfile as sf
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from voice import render, SR
B = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "bible.json")))
def say(who, text): return render(text, B["characters"][who]["voice"], sys.argv[1])
lines = [("rosie", "Hi! I'm Rosie the red panda. Let's go, WonderBuds!"), ("pudding", "And I'm Pudding! Hee hee! Is it snack time yet?"),
         ("ollie", "Hello. I'm Ollie. Hmm, let me think. Yes, I love puzzles!"), ("clover", "H-hi. I'm Clover. I can hear really, really well."),
         ("ziggy", "I'm Ziggy! Ready? Ready! READY! Zoom zoom!"),
         ("rosie", "WonderBuds, are we ready for an adventure?"), ("ziggy", "Ready, ready, ready!"), ("pudding", "Can we bring snacks?"), ("ollie", "I've packed a map, a compass, and three sandwiches."), ("clover", "We can do it together!")]
if __name__ == "__main__":
    out = []
    for who, text in lines: out += [say(who, text), np.zeros(int(SR * .45), np.float32)]
    sf.write(sys.argv[2], np.concatenate(out), SR); print("ok")

# Free local voiceover with Kokoro (open-source). Generates each line, then lays them out with pauses.
import json, sys, numpy as np, soundfile as sf, os
from kokoro_onnx import Kokoro
MODEL = os.environ.get('KOKORO_DIR', '/home/user/tts')
VOICE = sys.argv[1] if len(sys.argv) > 1 else 'am_michael'
SPEED = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
k = Kokoro(f'{MODEL}/kokoro.onnx', f'{MODEL}/voices.bin')
# (text as spoken, pause AFTER the line in seconds)
LINES = [
 ("What if you could see inside your brain's control room?", .55),
 ("Turns out... it's run by four guys.", .3),
 ("And none of them are qualified.", .5),
 ("This is Gary.", .3),
 ("Gary is in charge of focus.", .45),
 ("Gary has been on his phone... since twenty nineteen.", .5),
 ("This is Panic Pete.", .3),
 ("His only job is pressing the big red button.", .4),
 ("He presses it when the teacher says, we need to talk.", .4),
 ("He presses it when someone says your name in another room.", .45),
 ("He presses it for fun.", .55),
 ("Over here is the Snack Department.", .35),
 ("Budget?", .25),
 ("Unlimited.", .3),
 ("Today, they've approved three dinners.", .45),
 ("It is eleven A M.", .6),
 ("And this...", .3),
 ("is the Cringe Archive.", .4),
 ("Every embarrassing thing you've ever done.", .3),
 ("Saved.", .25),
 ("Backed up.", .3),
 ("In 4 K.", .6),
 ("Now it's 3 A M.", .4),
 ("Your body is asleep.", .35),
 ("Everyone in the control room is asleep.", .45),
 ("Except... one guy.", .4),
 ("He's been waiting all day.", .5),
 ("Twenty fourteen.", .4),
 ("You waved back at someone...", .25),
 ("who was waving at the person behind you.", 1.0),
 ("And that's why you can't sleep.", 0),
]
SR = 24000; LEAD = .4
out = [np.zeros(int(LEAD * SR))]; t = LEAD; timing = []
for text, pause in LINES:
    a, sr = k.create(text, voice=VOICE, speed=SPEED, lang='en-us')
    assert sr == SR
    # trim leading/trailing silence
    idx = np.where(np.abs(a) > 0.01)[0]; a = a[max(0, idx[0] - 240): idx[-1] + 1200]
    d = len(a) / SR; timing.append([round(t, 3), round(t + d, 3)])
    out += [a, np.zeros(int(pause * SR))]; t += d + pause
vo = np.concatenate(out)
sf.write('tts/voice.wav', vo, SR)
json.dump(timing, open('timing.json', 'w')); open('timing.js','w').write('window.TIMING='+json.dumps(timing)+';')
print(VOICE, SPEED, 'voice length', round(len(vo) / SR, 2), 's; last line ends', timing[-1][1])

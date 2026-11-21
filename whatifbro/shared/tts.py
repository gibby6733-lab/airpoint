# Free local voiceover with Kokoro. Usage: python3 tts.py <episode_dir>
# Reads script.json -> writes tts/voice.wav, timing.json, timing.js (window.TIMING + window.SCRIPT)
import json, sys, os, hashlib, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
ep = sys.argv[1]; S = json.load(open(f'{ep}/script.json'))
MODEL = os.environ.get('KOKORO_DIR', '/home/user/tts')
k = Kokoro(f'{MODEL}/kokoro.onnx', f'{MODEL}/voices.bin')
SR = 24000; LEAD = S.get('lead', .4)
os.makedirs(f'{ep}/tts/cache', exist_ok=True)
out = [np.zeros(int(LEAD * SR))]; t = LEAD; timing = []
for l in S['lines']:
    voice = l.get('voice', S.get('voice', 'am_michael')); speed = l.get('speed', S.get('speed', 1.1))
    key = hashlib.md5(f"{l['t']}|{voice}|{speed}".encode()).hexdigest()[:12]; cp = f'{ep}/tts/cache/{key}.npy'
    if os.path.exists(cp): a = np.load(cp)
    else:
        a, sr = k.create(l['t'], voice=voice, speed=speed, lang='en-us'); assert sr == SR
        idx = np.where(np.abs(a) > 0.01)[0]; a = a[max(0, idx[0] - 240): idx[-1] + 1200]
        a = a / (np.max(np.abs(a)) + 1e-9) * 0.9 * l.get('gain', 1.0); np.save(cp, a)
    d = len(a) / SR; timing.append([round(t, 3), round(t + d, 3)])
    pause = l.get('pause', .35)
    out += [a, np.zeros(int(pause * SR))]; t += d + pause
sf.write(f'{ep}/tts/voice.wav', np.concatenate(out), SR)
json.dump(timing, open(f'{ep}/timing.json', 'w'))
open(f'{ep}/timing.js', 'w').write('window.TIMING=' + json.dumps(timing) + ';\nwindow.SCRIPT=' + json.dumps(S) + ';\n')
print(ep, 'voice', round(t, 2), 's  (+end card ~', round(t + 3.0, 1), 's total)')

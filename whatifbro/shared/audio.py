# Usage: python3 audio.py <episode_dir>
# Builds audio/mix.wav from tts/voice.wav + original music bed + synthesized SFX listed in script.json
import numpy as np, subprocess, json, sys, wave, os
ep = sys.argv[1]
S = json.load(open(f'{ep}/script.json')); M = json.load(open(f'{ep}/meta.json'))
SR = 44100; TOTAL = M['TOTAL']; C = M['cues']; ENDS = M['ends']; END = M['END_CARD']
N = int(TOTAL * SR) + SR
rng = np.random.default_rng(S.get('music', {}).get('seed', 7))

def decode(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 's16le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768
def tt(d): return np.arange(int(d * SR)) / SR
def env(n, a=0.005, r=None):
    e = np.ones(n); ai = max(1, int(a * SR)); e[:ai] = np.linspace(0, 1, ai)
    if r: ri = min(n, int(r * SR)); e[-ri:] *= np.linspace(1, 0, ri)
    return e
def lp(x, a):
    y = np.zeros_like(x); s = 0.0; a = np.broadcast_to(a, x.shape)
    for i in range(len(x)): s += a[i] * (x[i] - s); y[i] = s
    return y
def lpf(x, a):  # fast fixed-coefficient one-pole via scipy-free cumulative trick (approx with repeated moving average)
    k = max(1, int(1 / max(a, 1e-4))); c = np.cumsum(np.concatenate([np.zeros(k), x]))
    y = (c[k:] - c[:-k]) / k; return np.roll(y, -k // 2)
def sweep(f0, f1, d, shape='sine'):
    t = tt(d); f = np.geomspace(f0, f1, len(t)); ph = 2 * np.pi * np.cumsum(f) / SR
    if shape == 'sine': return np.sin(ph)
    if shape == 'square': return np.sign(np.sin(ph)) * .6
    return 2 * ((ph / (2 * np.pi)) % 1) - 1
def noise(d): return rng.standard_normal(int(d * SR))

# ---------------- SFX library ----------------
def whoosh(d=0.45):
    n = int(d * SR); x = rng.standard_normal(n)
    a = np.concatenate([np.linspace(0.02, 0.35, n // 2), np.linspace(0.35, 0.02, n - n // 2)])
    y = lp(x, a) - lp(lp(x, a), 0.02); return y * np.sin(np.linspace(0, np.pi, n)) ** 2 * 0.9
def pop(d=None):
    t = tt(0.09); return np.sin(2 * np.pi * np.cumsum(np.geomspace(500, 1400, len(t))) / SR) * np.exp(-t * 40) * 0.6
def thud(d=0.3, f0=140):
    t = tt(d); y = sweep(f0, 45, d) * np.exp(-t * 14) + rng.standard_normal(len(t)) * np.exp(-t * 90) * 0.5
    return np.tanh(y * 2.2) * 0.8
def boom(d=1.6):
    t = tt(d); y = sweep(95, 38, d) * np.exp(-t * 2.6) + 0.5 * sweep(190, 76, d) * np.exp(-t * 4)
    y += lpf(rng.standard_normal(len(t)), 0.05) * np.exp(-t * 8) * 1.5; return np.tanh(y * 3) * 0.9
def ding(d=1.0):
    t = tt(d); return (np.sin(2*np.pi*1568*t) + 0.5*np.sin(2*np.pi*2352*t) + 0.25*np.sin(2*np.pi*3136*t)) * np.exp(-t * 4.5) * 0.35
def siren(d=1.4):
    t = tt(d); f = np.where((t * 5).astype(int) % 2 == 0, 960, 720).astype(float); f = lpf(f, 0.004)
    return np.tanh(np.sin(2 * np.pi * np.cumsum(f) / SR) * 3) * 0.32 * env(len(t), 0.01, 0.2)
def scratch(d=0.42):
    t = tt(d); f = 220 + 700 * np.abs(np.sin(t * np.pi / d * 2.2)) ** 1.5
    ph = 2 * np.pi * np.cumsum(f) / SR; y = (2 * ((ph / (2 * np.pi)) % 1) - 1) * 0.35 + lpf(rng.standard_normal(len(t)), 0.3) * 0.5
    return lpf(y, 0.35) * env(len(t), 0.003, 0.05) * 0.9
def click(d=0.05):
    t = tt(0.05); return (rng.standard_normal(len(t)) * np.exp(-t * 300) + np.sin(2*np.pi*2400*t) * np.exp(-t * 200)) * 0.5
def sparkle(d=1.0):
    y = np.zeros(int(d * SR) + SR)
    for k in range(7):
        s = int(rng.uniform(0, max(.01, d - 0.25)) * SR); t = tt(0.25); f = rng.choice([2093, 2637, 3136, 3520, 4186])
        y[s:s + len(t)] += np.sin(2 * np.pi * f * t) * np.exp(-t * 18) * 0.18
    return y
def drone(d=6):
    t = tt(d); y = 0.25*np.sin(2*np.pi*55*t) + 0.22*np.sin(2*np.pi*58.3*t) + 0.12*np.sin(2*np.pi*82.4*t + np.sin(t*0.7)*2)
    y += lpf(rng.standard_normal(len(t)), 0.01) * 0.6; return y * env(len(t), 1.0, 1.2) * 0.55
def crickets(d=5):
    t = tt(d); am = (np.sin(2*np.pi*28*t) > 0.2) * ((t * 1.6) % 1 < 0.35)
    return np.sin(2*np.pi*4600*t) * lpf(am.astype(float), 0.01) * 0.045
def ticks(d=5):
    y = np.zeros(int(d * SR) + SR); t = tt(0.02)
    for k in range(int(d)): s = int(k * SR); y[s:s+len(t)] += rng.standard_normal(len(t)) * np.exp(-t * 400) * 0.22
    return y
def stab(d=1.4):
    t = tt(d); y = sum(np.sin(2*np.pi*f*t) for f in [233, 247, 349, 370]) * 0.12 + 0.4*np.sign(np.sin(2*np.pi*58*t))*np.exp(-t*5)
    return np.tanh(y * 2) * np.exp(-t * 2.2) * 0.8
def levelup(d=0.7):
    out = []
    for f in [523, 659, 784, 1047, 1319]:
        t = tt(0.09); out.append(np.sign(np.sin(2*np.pi*f*t)) * 0.18 * np.exp(-t*8))
    return np.concatenate(out)
def hit8(d=0.25):
    t = tt(d); y = np.sign(np.sin(2*np.pi*np.cumsum(np.geomspace(300, 60, len(t)))/SR)) * 0.4 * np.exp(-t*12)
    return y + rng.standard_normal(len(t)) * np.exp(-t*30) * 0.4
def boing(d=0.6):
    t = tt(d); f = 180 + 120*np.sin(2*np.pi*9*t)*np.exp(-t*5) + 80*t
    return np.sin(2*np.pi*np.cumsum(f)/SR) * np.exp(-t*4) * 0.6
def tada(d=1.2):
    t = tt(d); y = np.zeros(len(t))
    for f in [523, 659, 784, 1047]:
        ph = 2*np.pi*f*t; y += (2*((ph/(2*np.pi)) % 1)-1) * 0.08
    y = lpf(y, 0.2) * env(len(t), 0.01) * np.exp(-t*1.6); s2 = int(.12*SR)
    return np.concatenate([y[:s2]*.8, np.zeros(int(.05*SR)), y])[:len(t)] * 1.6
def fail(d=1.6):  # sad descending "wah wah"
    out = []
    for f, dd in [(392, .35), (370, .35), (349, .35), (330, .9)]:
        t = tt(dd); vib = 1 + 0.02*np.sin(2*np.pi*6*t)*(t > .3)
        ph = 2*np.pi*np.cumsum(f*vib*np.linspace(1, .97, len(t)))/SR
        y = lpf(2*((ph/(2*np.pi)) % 1)-1, 0.15) * 0.4 * env(len(t), .02, .08); out.append(y)
    return np.concatenate(out)
def notif(d=0.5):
    t = tt(0.16); a = np.sin(2*np.pi*1319*t)*np.exp(-t*14); b = np.sin(2*np.pi*1760*t)*np.exp(-t*10)
    return np.concatenate([a, b]) * 0.35
def zap(d=0.45):
    t = tt(d); y = sweep(200, 2400, d, 'square') * 0.25 * np.exp(-t*3) + lpf(rng.standard_normal(len(t)), .3) * np.exp(-t*10) * .3
    return y * env(len(t), .002, .05)
def cheer(d=2.5):
    t = tt(d); y = lpf(rng.standard_normal(len(t)), 0.08) * 0.9 * env(len(t), 0.2, 0.9)
    for k in range(18):
        s = int(rng.uniform(0, d*.8)*SR); tw = tt(.25); f = rng.uniform(500, 1100)
        y[s:s+len(tw)] += np.sin(2*np.pi*np.cumsum(np.linspace(f, f*1.3, len(tw)))/SR) * np.sin(np.linspace(0, np.pi, len(tw))) * .06
    return y
def gasp(d=1.0):
    t = tt(d); return lpf(rng.standard_normal(len(t)), 0.12) * np.sin(np.linspace(0, np.pi, len(t)))**.5 * np.exp(-t*1.5) * 0.9
def bark(d=0.5):
    out = []
    for i in range(2):
        t = tt(.14); f = np.geomspace(520, 300, len(t)); ph = 2*np.pi*np.cumsum(f)/SR
        y = np.tanh((np.sin(ph) + .5*np.sin(2*ph) + .4*rng.standard_normal(len(t))) * 2) * np.sin(np.linspace(0, np.pi, len(t))) * .5
        out += [y, np.zeros(int(.08*SR))]
    return np.concatenate(out)
def meow(d=0.8):
    t = tt(.7); f = 520 + 380*np.sin(np.pi*t/.7)**2 + 15*np.sin(2*np.pi*7*t)
    ph = 2*np.pi*np.cumsum(f)/SR; y = (np.sin(ph) + .4*np.sin(2*ph) + .2*np.sin(3*ph)) * np.sin(np.linspace(0, np.pi, len(t))) * .35
    return y
def glass(d=1.0):
    t = tt(d); y = rng.standard_normal(len(t)) * np.exp(-t*9) * 0.5
    for f in [3100, 4300, 5200, 6100]: y += np.sin(2*np.pi*f*t) * np.exp(-t*(5+rng.uniform(0, 4))) * .08
    return y
def bell(d=2.0):  # school bell ring
    t = tt(d); return np.sign(np.sin(2*np.pi*880*t)) * (np.sin(2*np.pi*22*t) > 0) * 0.12 * env(len(t), .01, .3)
def heartbeat(d=2.0):
    y = np.zeros(int(d*SR) + SR)
    for k in np.arange(0, d-.3, .8):
        for o, g_ in [(0, 1), (.18, .7)]:
            t = tt(.15); s = int((k+o)*SR); y[s:s+len(t)] += np.sin(2*np.pi*55*t)*np.exp(-t*25)*g_*.9
    return y
def typing(d=1.5):
    y = np.zeros(int(d*SR) + SR); t = tt(.03)
    for k in np.arange(0, d-.05, .09 + 0):
        s = int((k + rng.uniform(0, .04))*SR); y[s:s+len(t)] += rng.standard_normal(len(t))*np.exp(-t*250)*.25
    return y
def slide(d=0.6):  # slide whistle up
    t = tt(d); return np.sin(2*np.pi*np.cumsum(np.geomspace(300, 1400, len(t)))/SR) * 0.3 * env(len(t), .02, .1)
def slidedown(d=0.6):
    t = tt(d); return np.sin(2*np.pi*np.cumsum(np.geomspace(1400, 250, len(t)))/SR) * 0.3 * env(len(t), .02, .1)
def power(d=0.8):  # power-up hum rising
    t = tt(d); return (sweep(80, 400, d, 'saw') * 0.2 + sweep(160, 800, d) * .2) * env(len(t), .05, .1)
def powerdown(d=0.9):
    t = tt(d); return (sweep(400, 50, d, 'saw') * 0.22) * env(len(t), .01, .2)
def door_(d=0.6):
    t = tt(d); return (lpf(rng.standard_normal(len(t)), .05) * .5 * np.exp(-t*6) + sweep(200, 120, d)*.2*np.exp(-t*5))
SFX = {k: v for k, v in globals().items() if callable(v) and k in ('whoosh pop thud boom ding siren scratch click sparkle drone crickets ticks stab levelup hit8 boing tada fail notif zap cheer gasp bark meow glass bell heartbeat typing slide slidedown power powerdown door_'.split())}

# ---------------- music ----------------
mus_cfg = S.get('music', {})
BPM = mus_cfg.get('bpm', 116); BEAT = 60 / BPM
PROGS = {'happy': [[48, 60, 64, 67], [45, 57, 60, 64], [41, 57, 60, 65], [43, 55, 59, 62]],
         'sneaky': [[45, 57, 60, 64], [41, 57, 60, 65], [40, 56, 59, 64], [45, 57, 60, 64]],
         'heroic': [[48, 60, 64, 67], [43, 55, 59, 62], [45, 57, 60, 64], [41, 57, 60, 65]],
         'chill': [[41, 57, 60, 64], [43, 55, 59, 62], [40, 55, 59, 64], [45, 57, 60, 64]]}
prog = PROGS[mus_cfg.get('prog', 'happy')]
NOTE = lambda n: 440 * 2 ** ((n - 69) / 12)
def pluck(f, d=0.32, v=1.0, wave='sine'):
    t = tt(d); y = np.zeros(len(t))
    if wave == 'square': y = np.sign(np.sin(2*np.pi*f*t)) * .5 * np.exp(-t*10)
    else:
        for h, a in [(1, 1), (2, .5), (3, .25), (4, .12)]: y += a * np.sin(2*np.pi*f*h*t) * np.exp(-t * (9 + h * 5))
    return y * env(len(t), 0.003) * v
def bassn(f, d=0.28): t = tt(d); return (np.sin(2*np.pi*f*t) + .3*np.sin(2*np.pi*2*f*t)) * np.exp(-t * 7) * env(len(t), .004)
def hat(): t = tt(0.04); return lpf(rng.standard_normal(len(t)), 0.9) * np.exp(-t * 120) * 0.18
def kick(): t = tt(.18); return np.sin(2*np.pi*np.cumsum(np.geomspace(140, 45, len(t)))/SR) * np.exp(-t*18) * .7
mrng = np.random.default_rng(mus_cfg.get('seed', 3))
mel = []
for bar in range(4):
    tones = prog[bar][1:] + [prog[bar][1] + 12]
    for step in range(8): mel.append(None if mrng.random() < .3 else int(mrng.choice(tones)) + 12)
def music(d):
    y = np.zeros(int(d * SR) + SR); nb = int(d / BEAT); wave = mus_cfg.get('wave', 'sine')
    for b in range(nb):
        bar = (b // 4) % 4; ch = prog[bar]; s = int(b * BEAT * SR)
        bs = bassn(NOTE(ch[0] - 12 if b % 2 == 0 else ch[0])); y[s:s+len(bs)] += bs * 0.55
        if mus_cfg.get('kick') and b % 2 == 0: k_ = kick(); y[s:s+len(k_)] += k_ * .5
        if b % 2 == 1:
            for n in ch[1:]: pl = pluck(NOTE(n), .25, .22); y[s:s+len(pl)] += pl
        hs = int((b + .5) * BEAT * SR); h = hat(); y[hs:hs+len(h)] += h
        if b >= 4:
            for half in range(2):
                m = mel[((b * 2 + half)) % len(mel)]
                if m: ms = int((b + half*.5) * BEAT * SR); pl = pluck(NOTE(m), .3, .28, wave); y[ms:ms+len(pl)] += pl
    return y[:int(d * SR)]

def at(ref, off=0.0):
    if ref == 'end': return END + off
    if isinstance(ref, str) and ref.startswith('e'): return ENDS[int(ref[1:])] + off
    return C[int(ref)] + off

mix = np.zeros(N)
def put(x, t0, g=1.0):
    s = int(t0 * SR); e = min(N, s + len(x))
    if 0 <= s < N: mix[s:e] += x[:e - s] * g

voice = np.zeros(N); vo = decode(f'{ep}/tts/voice.wav'); voice[:min(N, len(vo))] = vo[:N]
# music with mute ranges
mus = music(TOTAL + 1)[:N]; mus = np.pad(mus, (0, max(0, N - len(mus))))
gain = np.ones(N)
for a, b in mus_cfg.get('mute', []):
    ta, tb = at(a), at(b); ia, ib = int(ta * SR), int(tb * SR); fd = int(.25 * SR)
    gain[ia:ib] = 0; gain[max(0, ia - fd):ia] = np.minimum(gain[max(0, ia - fd):ia], np.linspace(1, 0, ia - max(0, ia - fd)))
    gain[ib:ib + fd] = np.minimum(gain[ib:ib + fd], np.linspace(0, 1, len(gain[ib:ib + fd])))
venv = lpf(np.abs(voice), 0.0008); venv = venv / (venv.max() + 1e-9)
duck = 1 - 0.55 * np.clip(venv * 4, 0, 1)
mix += mus * gain * duck * mus_cfg.get('vol', 0.40)
for item in S.get('sfx', []):
    name, ref, off = item[0], item[1], item[2]; g_ = item[3] if len(item) > 3 else 1.0; dur = item[4] if len(item) > 4 else None
    fn = SFX[name]; x = fn(dur) if dur is not None else fn()
    put(x, at(ref, off), g_)
put(pop(), END, .7); put(pop(), END + .5, .6); put(pop(), END + .85, .6)
mix += voice
mix = np.tanh(mix * 1.15) / np.tanh(1.15); mix = mix / np.max(np.abs(mix)) * 0.93
mix = mix[:int(TOTAL * SR)]
os.makedirs(f'{ep}/audio', exist_ok=True)
with wave.open(f'{ep}/audio/mix.wav', 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
print(os.path.basename(ep), 'mix', round(len(mix) / SR, 2), 's')

import numpy as np, subprocess, json, sys, wave

SR = 44100
meta = json.load(open('meta.json'))
TOTAL = meta['TOTAL']; C = meta['cues']; END = meta['END_CARD']; SPL = meta['SPLICE_T']
N = int(TOTAL * SR) + SR
rng = np.random.default_rng(7)

def decode(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 's16le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768

def tt(d): return np.arange(int(d * SR)) / SR
def env(n, a=0.005, r=None):
    e = np.ones(n); ai = max(1, int(a * SR)); e[:ai] = np.linspace(0, 1, ai)
    if r: ri = min(n, int(r * SR)); e[-ri:] *= np.linspace(1, 0, ri)
    return e
def lp(x, a):  # one-pole lowpass, a may be array
    y = np.zeros_like(x); s = 0.0; a = np.broadcast_to(a, x.shape)
    for i in range(len(x)): s += a[i] * (x[i] - s); y[i] = s
    return y
def sweep(f0, f1, d, shape='sine'):
    t = tt(d); f = np.geomspace(f0, f1, len(t)); ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) if shape == 'sine' else 2 * ((ph / (2 * np.pi)) % 1) - 1

def whoosh(d=0.45):
    n = int(d * SR); x = rng.standard_normal(n)
    a = np.concatenate([np.linspace(0.02, 0.35, n // 2), np.linspace(0.35, 0.02, n - n // 2)])
    y = lp(x, a) - lp(lp(x, a), 0.02)
    return y * np.sin(np.linspace(0, np.pi, n)) ** 2 * 0.9
def pop():
    t = tt(0.09); return np.sin(2 * np.pi * np.cumsum(np.geomspace(500, 1400, len(t))) / SR) * np.exp(-t * 40) * 0.6
def thud(f0=140, d=0.3, v=1.0):
    t = tt(d); y = sweep(f0, 45, d) * np.exp(-t * 14)
    y += rng.standard_normal(len(t)) * np.exp(-t * 90) * 0.5
    return np.tanh(y * 2.2) * 0.8 * v
def boom():
    d = 1.6; t = tt(d); y = sweep(95, 38, d) * np.exp(-t * 2.6)
    y += 0.5 * sweep(190, 76, d) * np.exp(-t * 4)
    y += lp(rng.standard_normal(len(t)), 0.05) * np.exp(-t * 8) * 1.5
    return np.tanh(y * 3) * 0.9
def ding():
    t = tt(1.0); return (np.sin(2*np.pi*1568*t) + 0.5*np.sin(2*np.pi*2352*t) + 0.25*np.sin(2*np.pi*3136*t)) * np.exp(-t * 4.5) * 0.35
def siren(d=1.4):
    t = tt(d); f = np.where((t * 5).astype(int) % 2 == 0, 960, 720).astype(float)
    f = lp(f, 0.004); ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.tanh(np.sin(ph) * 3) * 0.32; return y * env(len(t), 0.01, 0.2)
def scratch():
    d = 0.42; t = tt(d); f = 220 + 700 * np.abs(np.sin(t * np.pi / d * 2.2)) ** 1.5
    ph = 2 * np.pi * np.cumsum(f) / SR; y = (2 * ((ph / (2 * np.pi)) % 1) - 1) * 0.35
    y += lp(rng.standard_normal(len(t)), 0.3) * 0.5
    return lp(y, 0.35) * env(len(t), 0.003, 0.05) * 0.9
def click():
    t = tt(0.05); return (rng.standard_normal(len(t)) * np.exp(-t * 300) + np.sin(2*np.pi*2400*t) * np.exp(-t * 200)) * 0.5
def sparkle(d=1.0):
    y = np.zeros(int(d * SR))
    for k in range(7):
        s = int(rng.uniform(0, d - 0.25) * SR); t = tt(0.25); f = rng.choice([2093, 2637, 3136, 3520, 4186])
        y[s:s + len(t)] += np.sin(2 * np.pi * f * t) * np.exp(-t * 18) * 0.18
    return y
def drone(d):
    t = tt(d); y = 0.25 * np.sin(2*np.pi*55*t) + 0.22 * np.sin(2*np.pi*58.3*t) + 0.12*np.sin(2*np.pi*82.4*t + np.sin(t*0.7)*2)
    y += lp(rng.standard_normal(len(t)), 0.01) * 1.2 * (0.6 + 0.4 * np.sin(t * 0.9))
    return y * env(len(t), 1.0, 1.2) * 0.55
def crickets(d):
    t = tt(d); car = np.sin(2 * np.pi * 4600 * t)
    am = (np.sin(2 * np.pi * 28 * t) > 0.2) * ((t * 1.6) % 1 < 0.35)
    return car * lp(am.astype(float), 0.01) * 0.045
def tick_clock(d):
    y = np.zeros(int(d * SR)); t = tt(0.02)
    for k in range(int(d)): s = int(k * SR); y[s:s+len(t)] += rng.standard_normal(len(t)) * np.exp(-t * 400) * (0.25 if k % 2 else 0.18)
    return y
def projector(d):
    t = tt(d); x = lp(rng.standard_normal(len(t)), 0.08)
    clicks = (np.sin(2 * np.pi * 24 * t) > 0.92).astype(float)
    return (x * 0.18 + lp(clicks, 0.3) * 0.25) * env(len(t), 0.15, 0.3)
def stab():  # dissonant hit for the wake-up
    t = tt(1.4); y = sum(np.sin(2*np.pi*f*t) for f in [233, 247, 349, 370]) * 0.12
    y += 0.4 * np.sign(np.sin(2*np.pi*58*t)) * np.exp(-t*5)
    return np.tanh(y * 2) * np.exp(-t * 2.2) * 0.8

# ------------- music: bouncy pizzicato, 116 bpm -------------
BPM = 116; BEAT = 60 / BPM
def pluck(f, d=0.32, v=1.0):
    t = tt(d); y = np.zeros(len(t))
    for h, a in [(1, 1), (2, .5), (3, .25), (4, .12)]: y += a * np.sin(2*np.pi*f*h*t) * np.exp(-t * (9 + h * 5))
    return y * env(len(t), 0.003) * v
def bass(f, d=0.28):
    t = tt(d); return (np.sin(2*np.pi*f*t) + .3*np.sin(2*np.pi*2*f*t)) * np.exp(-t * 7) * env(len(t), .004)
def hat():
    t = tt(0.04); return lp(rng.standard_normal(len(t)), 0.9) * np.exp(-t * 120) * 0.18
NOTE = lambda n: 440 * 2 ** ((n - 69) / 12)
prog = [[48, 60, 64, 67], [45, 57, 60, 64], [41, 57, 60, 65], [43, 55, 59, 62]]  # C Am F G
mel = [72, None, 76, 74, 72, None, 69, None, 72, 74, None, 76, 77, 76, 74, None,
       69, None, 72, 72, 74, None, 72, 69, 71, None, 74, 72, 71, None, 67, None]
def music(d):
    y = np.zeros(int(d * SR) + SR)
    nbeats = int(d / BEAT)
    for b in range(nbeats):
        bar = (b // 4) % 4; ch = prog[bar]; s = int(b * BEAT * SR)
        bs = bass(NOTE(ch[0] - 12 if b % 2 == 0 else ch[0])); y[s:s+len(bs)] += bs * 0.55
        for k, n in enumerate(ch[1:]):
            if b % 2 == 1: pl = pluck(NOTE(n), .25, .22); y[s:s+len(pl)] += pl
        hs = int((b + .5) * BEAT * SR); h = hat(); y[hs:hs+len(h)] += h
        for half in range(2):
            m = mel[(b * 2 + half) % len(mel)]
            if m and (b // 16) % 2 == 1 or (m and b >= 4):
                ms = int((b + half * .5) * BEAT * SR); pl = pluck(NOTE(m), .3, .3); y[ms:ms+len(pl)] += pl
    return y[:int(d * SR)]

mix = np.zeros(N)
def put(x, at, g=1.0):
    s = int(at * SR); e = min(N, s + len(x))
    if s < N: mix[s:e] += x[:e - s] * g

# voice with splice
vo = decode('audio/vo.mp3')
sp = int(56.38 * SR)
vo = np.concatenate([vo[:sp], np.zeros(int(0.8 * SR)), vo[sp:]])
voice = np.zeros(N); s = int(0.4 * SR); voice[s:s+len(vo)] = vo[:N - s]

# music sections
m1 = music(43.4)
fade = np.ones(len(m1)); fade[int(34.2*SR):int(34.7*SR)] = np.linspace(1, 0.0, int(34.7*SR)-int(34.2*SR)); fade[int(34.7*SR):] = 0
mus = np.zeros(N); mus[:len(m1)] += m1 * fade
m2 = music(TOTAL - END + 0.5); e2 = env(len(m2), 0.05, 0.8)
put_at = int(END * SR); mus[put_at:put_at+len(m2)] += (m2 * e2)[:N - put_at]
# duck music under voice (sidechain-ish)
venv = lp(np.abs(voice), 0.0008); venv = venv / (venv.max() + 1e-9)
duck = 1 - 0.55 * np.clip(venv * 4, 0, 1)
mix += mus * duck * 0.42

# ------------- SFX timeline -------------
put(whoosh(.7), C[1] - .65, .9); put(pop(), C[1] - .05, .7)
for i in range(4): put(pop(), C[1] + .35 + i * .25, .55)
put(pop(), C[1] + 1.3, .6)
put(thud(160), C[2] + .1, 1.0)
put(whoosh(), C[3] - .2, .8); put(pop(), C[3] + .1, .6)
put(ding(), C[5] + 1.05, .9)
put(whoosh(), C[6] - .25, .8)
put(pop(), C[7] + .6, .5)
put(pop(), C[8] + .05, .5); put(pop(), C[9] + .05, .5); put(pop(), C[10] + .05, .5)
for sl in [C[8] + 1.25, C[9] + 1.35]:
    put(thud(110, .35), sl, 1.0); put(siren(), sl + .02, 1.0)
put(thud(220, .2, .5), C[10] + .45, .8); put(siren(.35), C[10] + .47, .5)
put(whoosh(), C[11] - .3, .8)
put(pop(), C[12], .6); put(sparkle(.8), C[13], 1.0); put(ding(), C[13], .5)
for h in [C[14] + .1, C[14] + .6, C[14] + 1.1]: put(thud(200, .22), h, .9)
put(scratch(), C[15] - .1, 1.0)
put(whoosh(.8), C[16] - .25, .7)
put(drone(8.8), C[16] - .1, 1.0)
put(click(), C[17], .8); put(click(), C[17] + .12, .5); put(click(), C[17] + .25, .6)
for i in range(3): put(whoosh(.3), C[18] + i * .55, .5)
put(thud(180, .25), C[19], .9); put(pop(), C[20], .6); put(sparkle(1.0), C[21], 1.2); put(ding(), C[21], .6)
put(click(), C[22], 1.0); put(crickets(9.0), C[22] + .2, 1.0); put(tick_clock(8.5), C[22] + .3, .8)
put(boom(), C[25] + .55, .35)
put(click(), C[26] - .05, .9)
put(projector(5.9), C[27] - .05, 1.0); put(click(), C[27] - .05, .9)
put(scratch(), C[29] + .55, .7); put(boom(), C[29] + 1.15, .9)
put(stab(), SPL + .62, 1.0); put(boom(), SPL + .62, .7)
put(pop(), END, .7); put(pop(), END + .6, .6); put(pop(), END + 1.0, .6)

mix += voice * 1.0
# master: soft limiter + normalise
mix = np.tanh(mix * 1.15) / np.tanh(1.15)
mix = mix / np.max(np.abs(mix)) * 0.93
mix = mix[:int(TOTAL * SR)]
with wave.open('audio/mix.wav', 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print('mix', len(mix) / SR, 's')

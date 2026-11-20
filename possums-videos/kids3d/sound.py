"""kids3d sound kit: original synthesized instruments, cartoon SFX, mixing helpers (numpy only, 24 kHz mono)."""
import numpy as np
SR = 24000
_rng = np.random.default_rng(11)
def tt(d): return np.arange(int(d * SR)) / SR
def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def noise(d): return _rng.uniform(-1, 1, int(d * SR)).astype(np.float32)
def lp(x, k=8): return np.convolve(x, np.ones(k) / k, mode="same")
def hp(x): return np.concatenate([[0], np.diff(x)]) * 4
def adsr(n, a=.005, d=.08, s=.6, r=.08, dur=None):
    a, d, r = int(a * SR), int(d * SR), int(r * SR); s_len = max(0, n - a - d - r)
    return np.concatenate([np.linspace(0, 1, a, False), np.linspace(1, s, d, False), np.full(s_len, s), np.linspace(s, 0, n - a - d - s_len)])[:n]
def sweep(f0, f1, d, wave="sine"):
    x = tt(d); f = f0 * (f1 / f0) ** (x / max(d, 1e-6)); ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) if wave == "sine" else (2 * ((ph / (2 * np.pi)) % 1) - 1) if wave == "saw" else np.sign(np.sin(ph))

# ------------------------------------------------------------------ instruments (m = MIDI note, d = seconds)
def marimba(m, d=.5): x = tt(d); f = mtof(m); return (np.sin(2*np.pi*f*x) + .35*np.sin(2*np.pi*f*4*x)*np.exp(-x*30) + .12*np.sin(2*np.pi*f*10*x)*np.exp(-x*60)) * np.exp(-x*7)
def xylo(m, d=.3): x = tt(d); f = mtof(m); return (np.sin(2*np.pi*f*x) + .5*np.sin(2*np.pi*f*3*x)*np.exp(-x*25)) * np.exp(-x*14)
def glock(m, d=.9): x = tt(d); f = mtof(m); return (np.sin(2*np.pi*f*x) + .4*np.sin(2*np.pi*f*2.76*x)*np.exp(-x*6) + .2*np.sin(2*np.pi*f*5.4*x)*np.exp(-x*12)) * np.exp(-x*4)
def musicbox(m, d=1.2): x = tt(d); f = mtof(m); return (np.sin(2*np.pi*f*x) + .3*np.sin(2*np.pi*f*3.01*x)*np.exp(-x*8) + .15*np.sin(2*np.pi*f*6.2*x)*np.exp(-x*15)) * np.exp(-x*3) * np.minimum(1, x*400)
def pluck(m, d=.5, bright=.5):  # ukulele / pizzicato: additive decaying harmonics
    x = tt(d); f = mtof(m); y = sum((bright ** (k - 1)) / k * np.sin(2*np.pi*f*k*x) * np.exp(-x*(4 + 3*k)) for k in range(1, 8)); return y * np.minimum(1, x * 600)
def bass(m, d=.4): x = tt(d); f = mtof(m); return (np.sin(2*np.pi*f*x) + .3*np.sin(4*np.pi*f*x)) * np.minimum(1, x*80) * np.exp(-x*3.5)
def tuba(m, d=.35): x = tt(d); f = mtof(m) * (1 + .01*np.sin(2*np.pi*5*x)); ph = 2*np.pi*np.cumsum(f)/SR; y = np.sin(ph) + .5*np.sin(2*ph) + .25*np.sin(3*ph); return lp(y, 6) * adsr(len(x), .02, .08, .7, .1)
def brass(m, d=.4): x = tt(d); f = mtof(m) * (1 + .006*np.sin(2*np.pi*5.5*x)); ph = 2*np.pi*np.cumsum(f)/SR; y = sum(np.sin(k*ph)/k**.9 for k in range(1, 9)); return lp(y, 3) * adsr(len(x), .03, .1, .75, .08)
def whistle(f0, f1, d=.5): x = tt(d); return sweep(f0, f1, d) * np.sin(np.pi * x / d) ** .5
def kick(): x = tt(.25); return np.sin(2*np.pi*(48 + 90*np.exp(-x*30))*x) * np.exp(-x*14)
def snare(): x = tt(.2); return (lp(noise(.2), 2) * .7 + .4*np.sin(2*np.pi*190*x)) * np.exp(-x*22)
def clap(): x = tt(.18); n = hp(noise(.18)); return n * (np.exp(-x*30) + .5*np.exp(-np.maximum(0, x-.012)*30)*(x > .012)) * .5
def hat(): x = tt(.05); return hp(noise(.05)) * np.exp(-x*90) * .35
def shaker(): x = tt(.07); return hp(noise(.07)) * np.exp(-x*60) * .25

# ------------------------------------------------------------------ cartoon SFX
def sfx(name):
    if name == "pop": x = tt(.12); return sweep(500, 1500, .12) * np.exp(-x*30)
    if name == "boing": x = tt(.5); return sweep(180, 520, .5) * (1 + .5*np.sin(2*np.pi*14*x)) * np.exp(-x*5) * .7
    if name == "ding": return glock(88, 1.2) * .7
    if name == "sparkle":
        out = np.zeros(int(1.0 * SR), np.float32)
        for k, m in enumerate([84, 88, 91, 96]): place(out, k * .07, glock(m, .7) * .5)
        return out
    if name == "whoosh": x = tt(.5); return lp(noise(.5), 3) * np.sin(np.pi * x / .5) ** 2 * .7
    if name == "swish": x = tt(.3); return lp(noise(.3), 2) * np.sin(np.pi * x / .3) ** 3 * .6
    if name == "slide_up": return whistle(400, 1400, .45) * .5
    if name == "slide_down": return whistle(1400, 400, .45) * .5
    if name == "giggle":
        out = np.zeros(int(.8 * SR), np.float32)
        for k in range(5): x = tt(.09); place(out, k * .13, sweep(900 - k*40, 1100 - k*40, .09) * np.exp(-x*20) * .3)
        return out
    if name == "cheer": x = tt(2.0); return lp(noise(2.0), 4) * (np.minimum(1, x*6) * np.exp(-x*1.4)) * .5
    if name == "chomp": x = tt(.18); return lp(noise(.18), 3) * np.exp(-x*25) * .8
    if name == "propeller": x = tt(1.2); return (sweep(60, 180, 1.2, "saw") * .3 + lp(noise(1.2), 5) * .2) * (0.6 + .4*np.sign(np.sin(2*np.pi*28*x))) * np.sin(np.pi*x/1.2)
    if name == "bulb": return glock(96, .6) * .5 + glock(100, .6) * .3
    if name == "flutter": x = tt(.6); return lp(noise(.6), 2) * (np.sin(2*np.pi*22*x) > 0) * np.sin(np.pi*x/.6) * .3
    if name == "creak": x = tt(.5); return sweep(300, 220, .5, "saw") * (np.sin(2*np.pi*35*x) > .3) * np.exp(-x*3) * .25
    if name == "zoom": x = tt(.6); return (sweep(300, 1800, .6, "saw") * .2 + lp(noise(.6), 2) * .3) * np.sin(np.pi*x/.6)
    if name == "splash":
        x = tt(.9); out = lp(noise(.9), 6) * np.exp(-x*5) * .9
        for _ in range(8): place(out, _rng.uniform(.05, .6), sweep(_rng.uniform(600, 1400), _rng.uniform(1600, 3000), .06) * np.exp(-tt(.06)*40) * .35)
        return out
    if name == "confetti":
        out = np.zeros(int(1.4 * SR), np.float32); place(out, 0, sweep(200, 60, .25) * np.exp(-tt(.25)*10) * .8)
        for k in range(14): place(out, .05 + k * .07, glock(84 + (k * 5) % 14, .4) * .15)
        return out
    raise KeyError(name)

def place(buf, at, a, g=1.0):
    i = int(at * SR)
    if i >= len(buf) or i + len(a) <= 0: return
    a = a[max(0, -i):]; i = max(0, i); j = min(len(buf), i + len(a)); buf[i:j] += (a[:j - i] * g).astype(np.float32)

def visemes(clip, fps):
    """Per-frame mouth data from a voice clip: open (loudness) and wide (bright 'ee' sounds vs round 'oo')."""
    hop = SR // fps; n = len(clip) // hop; o, w = np.zeros(n, np.float32), np.zeros(n, np.float32)
    for f in range(n):
        s = clip[f * hop:(f + 1) * hop]; e = np.sqrt((s ** 2).mean()); o[f] = min(1, e * 4.5)
        if e > .01:
            sp = np.abs(np.fft.rfft(s * np.hanning(len(s)))); fr = np.fft.rfftfreq(len(s), 1 / SR); w[f] = min(1, max(0, ((sp * fr).sum() / (sp.sum() + 1e-9) - 900) / 1800))
    o = np.convolve(o, [.25, .5, .25], "same"); return o, w

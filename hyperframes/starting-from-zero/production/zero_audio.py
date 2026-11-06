# Score + sound design for "Stop starting from zero". Synthesized; every cue is read from timing.json.
import json, math, subprocess, sys
import numpy as np, soundfile as sf
from scipy.signal import fftconvolve, butter, sosfilt

T = json.load(open(sys.argv[1])); VODIR = sys.argv[2]; OUT = sys.argv[3]
SR = 48000; END = T["end"]; N = int(END * SR); rng = np.random.default_rng(21)
S, B, VO = T["scenes"], T["beats"], T["vo"]
mtof = lambda m: 440.0 * 2 ** ((m - 69) / 12)
lp = lambda x, f, o=2: sosfilt(butter(o, f, "low", fs=SR, output="sos"), x)
hp = lambda x, f, o=2: sosfilt(butter(o, f, "high", fs=SR, output="sos"), x)
bp = lambda x, lo, hi, o=2: sosfilt(butter(o, [lo, hi], "band", fs=SR, output="sos"), x)
t_all = np.arange(N) / SR
def place(buf, x, t, g=1.0, pan=0.0):
    i = int(t * SR); j = min(N, i + len(x))
    if i < 0 or j <= i: return
    l, r = math.cos((pan + 1) * math.pi / 4) * 1.414, math.sin((pan + 1) * math.pi / 4) * 1.414
    buf[i:j, 0] += x[: j - i] * g * l; buf[i:j, 1] += x[: j - i] * g * r

def piano(f, dur=2.5, vel=0.6):
    n = int(dur * SR); t = np.arange(n) / SR
    y = sum(a * np.sin(2 * np.pi * f * k * t) * np.exp(-t * (1.2 + 1.6 * k)) for k, a in [(1, 1.0), (2, 0.35), (3, 0.12), (4, 0.05)])
    y = lp(y, 2600) * np.minimum(1, t / 0.006) * vel
    return y * np.minimum(1, (dur - t) / 0.2)
def saw(f, n):
    t = np.arange(n) / SR
    return sum(np.sin(2 * np.pi * f * k * t + k) / k for k in range(1, int(4000 / f) + 1))

# D major: Dmaj9, A/C#, Bm7, Gmaj7
CH = [[50, 57, 61, 64, 66], [49, 57, 61, 64, 69], [47, 54, 57, 62, 66], [43, 50, 54, 59, 62]]
BPM = 90; BEAT = 60 / BPM; BAR = 4 * BEAT
music = np.zeros((N, 2)); pad = np.zeros((N, 2)); pulse = np.zeros((N, 2)); bass = np.zeros(N)

# A · problem: sparse felt piano (cream scenes), stops dead at the silence beat
SIL = B["s2"]["silence"]; NAVY = S["s3"]
for k, t0 in enumerate(np.arange(0.2, SIL, BEAT * 2)):
    ch = CH[(k // 2) % 4]
    place(music, piano(mtof(ch[1 + k % 3] + 12), 2.4, 0.5), t0, 0.06, -0.3 + 0.6 * (k % 2))
    if k % 2 == 0: place(music, piano(mtof(ch[0]), 3.0, 0.5), t0, 0.05)
music[int(SIL * SR):int(NAVY * SR)] = 0
a_, b_ = int((SIL - 0.03) * SR), int(SIL * SR); music[a_:b_] *= np.linspace(1, 0, b_ - a_)[:, None]

# B · navy: pad swell + soft eighth pulse + bass; rises slightly into the final card
FIN = S["fin"]
for b, t0 in enumerate(np.arange(NAVY, END + BAR, BAR)):
    ci = b % 4; n = int((BAR + 1.0) * SR); env = np.minimum(1, np.arange(n) / (0.8 * SR)) * np.minimum(1, (n - np.arange(n)) / (1.0 * SR))
    for k, m in enumerate(CH[ci][1:]):
        for det, pn in [(-6, -0.6), (6, 0.6)]:
            place(pad, lp(saw(mtof(m) * 2 ** (det / 1200), n), 1200) * env * 0.03, t0, 1.0, pn)
    nb = int(BAR * SR); tb = np.arange(nb) / SR; f = mtof(CH[ci][0] - 12)
    yb = (np.sin(2 * np.pi * f * tb) + 0.2 * np.sin(4 * np.pi * f * tb)) * np.minimum(1, tb / 0.02) * np.exp(-tb * 0.6) * 0.16
    i = int(t0 * SR); j = min(N, i + nb)
    if i < N: bass[i:j] += yb[: j - i]
    if t0 >= S["s4"] - 0.01:                   # pulse enters once the user is in control
        for e in range(8):
            te = t0 + e * BEAT / 2; m = CH[ci][1 + e % 4] + 12; np_ = int(0.4 * SR); tt = np.arange(np_) / SR
            y = np.sin(2 * np.pi * mtof(m) * tt) * np.exp(-tt * 9) * np.minimum(1, tt / 0.003)
            place(pulse, y * 0.03 * (1.25 if te >= FIN - 0.5 else 1.0), te, 1.0, -0.4 if e % 2 else 0.4)
swell = np.clip((t_all - NAVY) / 2.5, 0, 1) * (1 + 0.35 * np.clip((t_all - (FIN - 1.0)) / 2.0, 0, 1))
pad *= swell[:, None]; bass *= swell
music += pad + pulse + lp(bass, 300)[:, None]
music *= np.clip((END - t_all) / 1.2, 0, 1)[:, None]

# reverb
irn = int(2.4 * SR); irt = np.arange(irn) / SR
ir = np.stack([rng.standard_normal(irn), rng.standard_normal(irn)], 1) * np.exp(-irt * 2.8)[:, None]
ir = lp(ir.T, 5000).T; ir /= np.sqrt((ir ** 2).sum())
music = music + np.stack([fftconvolve(music[:, c], ir[:, c])[:N] for c in range(2)], 1) * 0.4
music[int(SIL * SR):int(NAVY * SR)] *= 0.0           # the silence stays silent (reverb tail too)

# ---- sound design ----
fx = np.zeros((N, 2))
def click(g=0.12):
    n = int(0.03 * SR); tt = np.arange(n) / SR
    return (np.sin(2 * np.pi * 2400 * tt) * 0.5 + bp(rng.standard_normal(n), 2000, 6000) * 0.5) * np.exp(-tt * 260) * g
def tap(): n = int(0.06 * SR); tt = np.arange(n) / SR; return np.sin(2 * np.pi * 1500 * tt) * np.exp(-tt * 90) * 0.12
def shimmer(dur=1.4):
    n = int(dur * SR); tt = np.arange(n) / SR
    y = sum(np.sin(2 * np.pi * f * tt) * np.exp(-tt * d) for f, d in [(1174.7, 2.5), (1480.0, 3), (1760.0, 3.5), (2349.3, 4.5)])
    return y * np.minimum(1, tt / 0.02) * 0.03
def rise(dur=0.6):
    n = int(dur * SR); tt = np.arange(n) / SR
    return bp(rng.standard_normal(n), 800, 5000) * (tt / dur) ** 2 * 0.06
def whoosh(dur=0.7):
    n = int(dur * SR); tt = np.arange(n) / SR
    return bp(rng.standard_normal(n), 400, 3000) * np.sin(np.pi * tt / dur) ** 2 * 0.07
def pen(dur):
    n = int(dur * SR); y = np.zeros(n)
    for p in rng.integers(0, n - 200, int(dur * 300)): L = rng.integers(40, 160); y[p:p + L] += rng.standard_normal(L) * np.exp(-np.arange(L) / (L / 3))
    return bp(y, 2500, 8000) * 0.05
def keys(t0, nk):
    for k in range(nk): place(fx, click(0.07), t0 + k * 1.0 / nk + rng.uniform(-0.02, 0.02), 1.0, rng.uniform(-0.3, 0.3))
place(fx, pen(1.3), 0.35, 1.0, -0.1)                     # pen on paper
keys(B["s1"]["type"] + 0.1, 12)                           # same name, typed again
place(fx, whoosh(0.4) * 0.6, B["s1"]["doc"] - 0.05)       # reaching for the document
place(fx, pen(0.5) * 0.7, B["s1"]["form4"])
for t in [B["s2"]["l1"], B["s2"]["l2"], B["s2"]["l3"], B["s2"]["l4"]]: place(fx, click(0.14), t)
span = SIL - B["s2"]["rep"]
for k in range(8): place(fx, click(0.12), B["s2"]["rep"] + k * span / 8)
fx[int(SIL * SR):int(NAVY * SR)] = 0
place(fx, shimmer(2.2) * 0.6, NAVY + 0.1)                 # purple light appears
place(fx, tap(), B["s4"]["toggle"])
place(fx, tap(), B["s4"]["press"])
place(fx, rise(B["s4"]["release"] - B["s4"]["press"]), B["s4"]["press"])   # the hold
place(fx, shimmer(), B["s4"]["release"])                  # approval: data may now move
place(fx, shimmer(1.0) * 0.6, B["s5"]["packet"] + 0.1)
place(fx, tap(), B["s5"]["tap"])
place(fx, tap(), B["s6"]["approve"])
place(fx, whoosh(1.0), B["s6"]["tunnel"])
place(fx, tap(), B["s7"]["tap"])
place(fx, shimmer(1.6) * 0.7, B["s8"]["connect"])
n = int(1.6 * SR); tt = np.arange(n) / SR                 # final soft purple pulse
place(fx, np.sin(2 * np.pi * 73.4 * tt) * np.sin(np.pi * tt / 1.6) ** 2 * 0.18 + shimmer(1.6)[:n] * 0.8, END - 1.5)

# ---- narration ----
vo = np.zeros((N, 2))
for name, t in VO.items():
    x, sr = sf.read(f"{VODIR}/{name}.wav", dtype="float32")
    x = np.interp(np.arange(int(len(x) * SR / sr)) * sr / SR, np.arange(len(x)), x); place(vo, x, t)
vo = hp(vo.T, 80).T
env = lp(np.abs(vo).mean(1), 4); env /= env.max() + 1e-9
gate = lp(np.convolve((env > 0.04).astype(float), np.ones(int(0.25 * SR)) / int(0.25 * SR), "same"), 3)
music *= (1 - 0.5 * np.clip(gate, 0, 1))[:, None]

def lufs(x):
    sf.write("/tmp/_x.wav", x.astype(np.float32), SR)
    o = subprocess.run(["ffmpeg", "-hide_banner", "-i", "/tmp/_x.wav", "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    return float(o.split("I:")[-1].split("LUFS")[0])
vo *= 10 ** ((-16 - lufs(vo)) / 20); music *= 10 ** ((-25 - lufs(music)) / 20)
mix = vo + music + fx
sf.write("/tmp/_mix.wav", mix.astype(np.float32), SR)
m = subprocess.run(["ffmpeg", "-hide_banner", "-i", "/tmp/_mix.wav", "-af", "loudnorm=I=-14:TP=-1.5:LRA=9:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
j = json.loads(m[m.rindex("{"):])
ln = (f"loudnorm=I=-14:TP=-1.5:LRA=9:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}"
      f":measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "/tmp/_mix.wav", "-af", f"{ln},alimiter=limit=0.84:level=false,aresample=48000",
                "-ar", "48000", "-c:a", "pcm_s16le", OUT], check=True)
print("wrote", OUT, "silence", round(SIL, 2), "-", round(NAVY, 2))

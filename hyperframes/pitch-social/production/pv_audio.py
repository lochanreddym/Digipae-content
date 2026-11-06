# Score + sound design + VO mix for the DigiPae social pitch. Synthesized; every cue reads timing.json.
import json, math, subprocess, sys
import numpy as np, soundfile as sf
from scipy.signal import fftconvolve, butter, sosfilt
T = json.load(open(sys.argv[1])); VODIR = sys.argv[2]; OUT = sys.argv[3]
SR = 48000; END = T["end"]; N = int(END * SR); rng = np.random.default_rng(7)
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
def saw(f, n):
    t = np.arange(n) / SR
    return sum(np.sin(2 * np.pi * f * k * t + k) / k for k in range(1, int(4000 / f) + 1))
# A minor -> F -> C -> G (problem), lifts at the DigiPae reveal
CH = [[45, 52, 57, 60, 64], [41, 53, 57, 60, 65], [48, 52, 55, 60, 67], [43, 50, 55, 59, 62]]
BPM = 96; BEAT = 60 / BPM; BAR = 4 * BEAT
pad = np.zeros((N, 2)); pulse = np.zeros((N, 2)); bass = np.zeros(N); kick = np.zeros(N)
LIFT = B["a4"]["dp"]
for b, t0 in enumerate(np.arange(0, END + BAR, BAR)):
    ci = b % 4; n = int((BAR + 1.0) * SR); env = np.minimum(1, np.arange(n) / (0.6 * SR)) * np.minimum(1, (n - np.arange(n)) / (1.0 * SR))
    for m in CH[ci][1:]:
        for det, pn in [(-7, -0.6), (7, 0.6)]:
            place(pad, lp(saw(mtof(m) * 2 ** (det / 1200), n), 1100) * env * 0.028, t0, 1.0, pn)
    nb = int(BAR * SR); tb = np.arange(nb) / SR; f = mtof(CH[ci][0] - 12)
    yb = (np.sin(2 * np.pi * f * tb) + 0.25 * np.sin(4 * np.pi * f * tb)) * np.minimum(1, tb / 0.02) * np.exp(-tb * 0.5) * 0.15
    i = int(t0 * SR); j = min(N, i + nb)
    if i < N: bass[i:j] += yb[: j - i]
    for e in range(8):
        te = t0 + e * BEAT / 2
        if te < 0.15: continue
        m = CH[ci][1 + e % 4] + 12; np_ = int(0.35 * SR); tt = np.arange(np_) / SR
        y = np.sin(2 * np.pi * mtof(m) * tt) * np.exp(-tt * 10) * np.minimum(1, tt / 0.003)
        place(pulse, y * (0.022 if te < LIFT else 0.032), te, 1.0, -0.4 if e % 2 else 0.4)
    if t0 >= LIFT - 0.01:
        for e in range(4):
            nk = int(0.25 * SR); tk = np.arange(nk) / SR
            ky = np.sin(2 * np.pi * (48 + 90 * np.exp(-tk * 30)) * tk) * np.exp(-tk * 14) * 0.22
            i = int((t0 + e * BEAT) * SR); j = min(N, i + nk)
            if i < N: kick[i:j] += ky[: j - i]
music = pad + pulse + lp(bass, 300)[:, None] + lp(kick, 200)[:, None]
music *= np.clip((END - t_all) / 1.4, 0, 1)[:, None] * np.clip(t_all / 0.4, 0, 1)[:, None]
irn = int(2.2 * SR); irt = np.arange(irn) / SR
ir = np.stack([rng.standard_normal(irn), rng.standard_normal(irn)], 1) * np.exp(-irt * 3)[:, None]
ir = lp(ir.T, 5000).T; ir /= np.sqrt((ir ** 2).sum())
music = music + np.stack([fftconvolve(music[:, c], ir[:, c])[:N] for c in range(2)], 1) * 0.35

fx = np.zeros((N, 2))
def click(g=0.1):
    n = int(0.03 * SR); tt = np.arange(n) / SR
    return (np.sin(2 * np.pi * 2400 * tt) * 0.5 + bp(rng.standard_normal(n), 2000, 6000) * 0.5) * np.exp(-tt * 260) * g
def tick(): n = int(0.05 * SR); tt = np.arange(n) / SR; return np.sin(2 * np.pi * 1700 * tt) * np.exp(-tt * 110) * 0.08
def shimmer(dur=1.4):
    n = int(dur * SR); tt = np.arange(n) / SR
    y = sum(np.sin(2 * np.pi * f * tt) * np.exp(-tt * d) for f, d in [(1318.5, 2.5), (1568.0, 3), (1975.5, 3.5), (2637.0, 4.5)])
    return y * np.minimum(1, tt / 0.02) * 0.03
def whoosh(dur=0.6):
    n = int(dur * SR); tt = np.arange(n) / SR
    return bp(rng.standard_normal(n), 400, 3000) * np.sin(np.pi * tt / dur) ** 2 * 0.06
def thud():
    n = int(0.3 * SR); tt = np.arange(n) / SR
    return np.sin(2 * np.pi * (60 + 80 * np.exp(-tt * 25)) * tt) * np.exp(-tt * 12) * 0.25
for k in ["a2", "a3", "a4", "c"]: place(fx, whoosh(), S[k] - 0.3)
place(fx, whoosh(0.8), S["b"] - 0.4)
for k in ["p1"]:
    for i in range(3): place(fx, tick(), B["a2"][k] + i * 0.22)
for k in ["id", "addr", "inc"]:
    for i in range(6): place(fx, click(0.07), B["a2"][k] + i * 0.05 + rng.uniform(0, 0.02), 1.0, rng.uniform(-0.3, 0.3))
place(fx, thud(), B["a2"]["again"])
place(fx, thud() * 0.8, B["a3"]["stat"])
place(fx, shimmer(2.0), B["a4"]["dp"])
for s in T["segs"][1:]: place(fx, tick() * 0.7, s["t"])
place(fx, shimmer(1.2) * 0.6, B["b9"]["soon"])
place(fx, shimmer(1.6) * 0.8, S["c"] + 0.1)
place(fx, shimmer(2.0), B["c2"]["word"])
n = int(1.6 * SR); tt = np.arange(n) / SR
place(fx, np.sin(2 * np.pi * 55 * tt) * np.sin(np.pi * tt / 1.6) ** 2 * 0.16, B["c2"]["follow"])

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
print("wrote", OUT)

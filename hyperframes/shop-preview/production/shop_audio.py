# 30s preview soundtrack: 95 BPM electric-piano bed, muted percussion, paper/wood foley, ducked narration. Synthesized.
import json, math, subprocess, sys
import numpy as np, soundfile as sf
from scipy.signal import fftconvolve, butter, sosfilt

T = json.load(open(sys.argv[1])); VODIR = sys.argv[2]; OUT = sys.argv[3]
SR = 48000; END = T["end"]; N = int(END * SR); rng = np.random.default_rng(5)
mtof = lambda m: 440.0 * 2 ** ((m - 69) / 12)
lp = lambda x, f, o=2: sosfilt(butter(o, f, "low", fs=SR, output="sos"), x)
hp = lambda x, f, o=2: sosfilt(butter(o, f, "high", fs=SR, output="sos"), x)
bp = lambda x, lo, hi, o=2: sosfilt(butter(o, [lo, hi], "band", fs=SR, output="sos"), x)
def place(buf, x, t, g=1.0, pan=0.0):
    i = int(t * SR); j = min(N, i + len(x))
    if i < 0 or j <= i: return
    l, r = math.cos((pan + 1) * math.pi / 4) * 1.414, math.sin((pan + 1) * math.pi / 4) * 1.414
    buf[i:j, 0] += x[: j - i] * g * l; buf[i:j, 1] += x[: j - i] * g * r

# ---- music: D major, Dmaj9 - Bm9 - Gmaj9 - A7sus, resolving to Dmaj9 ----
BPM = 95; BEAT = 60 / BPM; BAR = 4 * BEAT; T0 = 0.6
CH = [[50, 54, 57, 61, 64], [47, 50, 54, 57, 61], [43, 47, 50, 54, 57], [45, 50, 52, 55, 59]]
ROOT = [38, 35, 31, 33]
FINAL = [50, 54, 57, 61, 64, 69]
def epiano(f, dur, vel):
    n = int(dur * SR); t = np.arange(n) / SR
    idx = 1.8 * vel * np.exp(-t / 0.35) + 0.25                      # FM brightness decays like a tine
    y = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * t))
    y += 0.22 * np.exp(-t / 0.05) * np.sin(2 * np.pi * f * 7.0 * t)  # bell attack
    env = np.minimum(1, t / 0.004) * np.exp(-t / 1.6) * np.minimum(1, (dur - t) / 0.12)
    return y * env * vel
music = np.zeros((N, 2)); perc = np.zeros((N, 2)); bass = np.zeros(N)
nb = int((END - T0) / BAR) + 1
for b in range(nb):
    t0 = T0 + b * BAR
    final = t0 >= END - 2.2
    chord = FINAL if final else CH[b % 4]
    # comp: beat 1 and the "and" of 2 (soft), gentle strum spread
    hits = [(0, 0.55, 2.4)] if final else [(0, 0.5, 1.4), (1.5, 0.32, 1.0), (3, 0.26, 0.7)]
    for beat, vel, dur in hits:
        for k, m in enumerate(chord):
            y = epiano(mtof(m), min(dur, END - (t0 + beat * BEAT)) if final else dur, vel * (0.9 if k else 1.0))
            place(music, y * 0.05, t0 + beat * BEAT + k * 0.012, 1.0, -0.4 + 0.8 * k / (len(chord) - 1))
    # bass
    if not final or b == nb - 1:
        for beat in ([0, 2.5] if not final else [0]):
            n2 = int(BEAT * (1.3 if not final else 3.0) * SR); tt = np.arange(n2) / SR; f = mtof(ROOT[b % 4] if not final else 38)
            y = (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(4 * np.pi * f * tt)) * np.minimum(1, tt / 0.01) * np.exp(-tt * 1.8) * 0.2
            i = int((t0 + beat * BEAT) * SR); j = min(N, i + n2)
            if i < N: bass[i:j] += y[: j - i]
    # muted percussion: soft kick 1&3, rim 2&4, shaker 8ths — out for the last bar
    if final or t0 < T0 + BAR * 0.99: continue
    for beat in range(4):
        tb = t0 + beat * BEAT
        if beat in (0, 2):
            n3 = int(0.25 * SR); tt = np.arange(n3) / SR; f = 50 + 60 * np.exp(-tt * 35)
            place(perc, np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 14) * 0.22, tb)
        else:
            n3 = int(0.05 * SR); tt = np.arange(n3) / SR
            rim = (bp(rng.standard_normal(n3), 1200, 3500) * 0.5 + np.sin(2 * np.pi * 1700 * tt) * 0.4) * np.exp(-tt * 120) * 0.07
            place(perc, rim, tb, 1.0, 0.2)
        for h in (0, 0.5):
            n4 = int(0.06 * SR); tt = np.arange(n4) / SR
            sh = hp(rng.standard_normal(n4), 6000) * np.exp(-tt * 70) * (0.022 if h else 0.012)
            place(perc, sh, tb + h * BEAT, 1.0, -0.3)
music += lp(bass, 350)[:, None] + perc
# tremolo-free stereo room
irn = int(1.8 * SR); irt = np.arange(irn) / SR
ir = np.stack([rng.standard_normal(irn), rng.standard_normal(irn)], 1) * np.exp(-irt * 3.6)[:, None]
ir = lp(ir.T, 4500).T; ir /= np.sqrt((ir ** 2).sum())
music = music + np.stack([fftconvolve(music[:, c], ir[:, c])[:N] for c in range(2)], 1) * 0.35
t_all = np.arange(N) / SR
music *= (np.clip((t_all - 0.45) / 0.6, 0, 1) * np.clip((END - t_all) / 1.4, 0, 1))[:, None]

# ---- foley ----
fx = np.zeros((N, 2))
def rustle(dur, dens=900, g=0.18):
    n = int(dur * SR); y = np.zeros(n); k = rng.poisson(dens * dur)
    for p in rng.integers(0, n - 400, k):
        L = rng.integers(60, 300); y[p:p + L] += rng.standard_normal(L) * np.exp(-np.arange(L) / (L / 4)) * rng.uniform(0.2, 1)
    env = np.sin(np.pi * np.clip(np.arange(n) / n, 0, 1)) ** 0.7
    return bp(y, 1500, 7500) * env * g
def knock():
    n = int(0.3 * SR); tt = np.arange(n) / SR
    return (np.sin(2 * np.pi * 190 * tt) * np.exp(-tt * 28) * 0.5 + bp(rng.standard_normal(n), 400, 1800) * np.exp(-tt * 60) * 0.25) * 0.35
def slide(dur):
    n = int(dur * SR); tt = np.arange(n) / SR
    return lp(rng.standard_normal(n), 2200) * np.sin(np.pi * tt / dur) ** 1.5 * 0.05
place(fx, rustle(0.75), 0.0, 1.0, -0.15)          # opens the video, before the music
place(fx, rustle(0.5, 600, 0.1), 1.3, 1.0, 0.1)   # box settles in the bag
place(fx, knock(), 5.85, 1.0, 0.25)               # sign set down on the counter
place(fx, slide(1.6), 24.4, 1.0, -0.2)            # bag slides to the customer
room = np.stack([lp(rng.standard_normal(N), 900), lp(rng.standard_normal(N), 900)], 1) * 0.004
fx += room * np.clip((END - t_all) / 1.0, 0, 1)[:, None]

# ---- narration as one continuous track ----
vo = np.zeros((N, 2))
for name, t in T["vo"].items():
    x, sr = sf.read(f"{VODIR}/{name}.wav", dtype="float32")
    x = np.interp(np.arange(int(len(x) * SR / sr)) * sr / SR, np.arange(len(x)), x)
    place(vo, x, t)
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
m = subprocess.run(["ffmpeg", "-hide_banner", "-i", "/tmp/_mix.wav", "-af", "loudnorm=I=-14:TP=-1.5:LRA=8:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
j = json.loads(m[m.rindex("{"):])
ln = (f"loudnorm=I=-14:TP=-1.5:LRA=8:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}"
      f":measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "/tmp/_mix.wav", "-af", f"{ln},alimiter=limit=0.84:level=false,aresample=48000",
                "-ar", "48000", "-c:a", "pcm_s16le", OUT], check=True)
print("wrote", OUT)

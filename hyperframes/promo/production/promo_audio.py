# Score + sound design + narration mix for the Digipae promo. Everything is synthesized; times come from timing.json.
import json, math, subprocess, sys
import numpy as np, soundfile as sf
from scipy.signal import fftconvolve, butter, sosfilt

T = json.load(open(sys.argv[1])); VODIR = sys.argv[2]; OUT = sys.argv[3]
SR = 48000; END = T["end"]; N = int(END * SR)
rng = np.random.default_rng(11)
mtof = lambda m: 440.0 * 2 ** ((m - 69) / 12)
t_all = np.arange(N) / SR

def lp(x, f, o=2): return sosfilt(butter(o, f, "low", fs=SR, output="sos"), x)
def hp(x, f, o=2): return sosfilt(butter(o, f, "high", fs=SR, output="sos"), x)
def bp(x, lo, hi, o=2): return sosfilt(butter(o, [lo, hi], "band", fs=SR, output="sos"), x)
def place(buf, x, t, gain=1.0, pan=0.0):
    i = int(t * SR); j = min(N, i + len(x))
    if j <= i or i < 0: return
    l, r = math.cos((pan + 1) * math.pi / 4), math.sin((pan + 1) * math.pi / 4)
    buf[i:j, 0] += x[: j - i] * gain * l * 1.414; buf[i:j, 1] += x[: j - i] * gain * r * 1.414

# ---------------- music: 100 BPM, Fmaj7 - Dm7 - Bbmaj7 - Csus ----------------
BPM = 100; BEAT = 60 / BPM; BAR = 4 * BEAT
CH = [[53, 57, 60, 64], [50, 53, 57, 60], [46, 50, 53, 57], [48, 53, 55, 62]]
ROOT = [41, 38, 34, 36]
DRUMS_IN, DRUMS_OUT = T["scenes"][0]["start"] - BEAT, T["outroStart"] + 0.2
pad = np.zeros((N, 2)); pluck = np.zeros((N, 2)); bass = np.zeros(N); drums = np.zeros((N, 2))

def saw(f, n, phase=0.0):
    t = np.arange(n) / SR; y = np.zeros(n)
    for k in range(1, int(5000 / f) + 1): y += np.sin(2 * np.pi * f * k * t + phase * k) / k
    return y
nbars = int(END / BAR) + 2
for b in range(nbars):
    t0 = b * BAR; ci = b // 2 % 4 if False else b % 4
    dur = BAR + 0.9; n = int(dur * SR)
    env = np.minimum(1, np.arange(n) / (0.5 * SR)) * np.minimum(1, (n - np.arange(n)) / (0.9 * SR))
    for k, m in enumerate(CH[ci]):
        for det, pan in [(-7, -0.6), (7, 0.6)]:
            f = mtof(m) * 2 ** (det / 1200)
            v = lp(saw(f, n, phase=k + det), 1400) * env * 0.035
            place(pad, v, t0, 1.0, pan)
    # bass: root on beat 1 and the "and" of 3
    for bt in [0, 2.5]:
        n2 = int(BEAT * 1.4 * SR); tt = np.arange(n2) / SR
        f = mtof(ROOT[ci]); y = np.sin(2 * np.pi * f * tt) + 0.25 * np.sin(4 * np.pi * f * tt)
        y *= np.minimum(1, tt / 0.01) * np.exp(-tt * 2.2) * 0.22
        i = int((t0 + bt * BEAT) * SR); j = min(N, i + n2)
        if i < N: bass[i:j] += y[: j - i]
    # pluck arpeggio in 8ths, one octave up
    notes = [CH[ci][k % 4] + 12 for k in [0, 1, 2, 3, 2, 1, 3, 2]]
    for k, m in enumerate(notes):
        tn = t0 + k * BEAT / 2
        n3 = int(0.6 * SR); tt = np.arange(n3) / SR; f = mtof(m)
        y = (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(4 * np.pi * f * tt) * np.exp(-tt * 18)) * np.exp(-tt * 7) * np.minimum(1, tt / 0.004)
        place(pluck, y * 0.055, tn, 1.0, -0.35 if k % 2 else 0.35)
    # drums only while the product scenes play
    for beat in range(4):
        tb = t0 + beat * BEAT
        if not (DRUMS_IN <= tb < DRUMS_OUT): continue
        n4 = int(0.35 * SR); tt = np.arange(n4) / SR
        f = 48 + 90 * np.exp(-tt * 30); ph = 2 * np.pi * np.cumsum(f) / SR
        k_ = np.sin(ph) * np.exp(-tt * 9) * 0.32
        place(drums, k_, tb)
        h = hp(rng.standard_normal(int(0.05 * SR)), 7000) * np.exp(-np.arange(int(0.05 * SR)) / SR * 90) * 0.035
        place(drums, h, tb + BEAT / 2, 1.0, 0.25)
bass = lp(bass, 400)

# sidechain pad + pluck to the kick
duck = np.ones(N)
for b in range(nbars):
    for beat in range(4):
        tb = b * BAR + beat * BEAT
        if DRUMS_IN <= tb < DRUMS_OUT:
            i = int(tb * SR); n5 = int(0.3 * SR); j = min(N, i + n5)
            if i < N: duck[i:j] = np.minimum(duck[i:j], 1 - 0.35 * np.exp(-np.arange(j - i) / SR * 12))
pad *= duck[:, None]; pluck *= duck[:, None]

# delay on pluck (dotted 8th ping-pong), reverb on pad + pluck
d = int(0.75 * BEAT * SR); fb = 0.35
wet = np.zeros_like(pluck); src = pluck.copy()
for k in range(1, 5):
    sh = d * k
    if sh >= N: break
    ch = k % 2
    wet[sh:, ch] += src[:-sh, 0 if ch else 1] * (fb ** k)
pluck = pluck + lp(wet.T, 3500).T
ir_n = int(2.6 * SR); irt = np.arange(ir_n) / SR
ir = np.stack([rng.standard_normal(ir_n), rng.standard_normal(ir_n)], 1) * np.exp(-irt * 2.6)[:, None]
ir = lp(ir.T, 5000).T; ir /= np.sqrt((ir ** 2).sum())
send = pad * 0.6 + pluck
rev = np.stack([fftconvolve(send[:, c], ir[:, c])[:N] for c in range(2)], 1) * 0.55
music = pad + pluck + rev + bass[:, None] + drums
# fades: music swells in under the logo, settles out under the end card
fade = np.minimum(1, t_all / 1.2) * np.clip((END - t_all) / 2.2, 0, 1)
music *= fade[:, None]

# ---------------- narration ----------------
vo = np.zeros((N, 2))
for name, t in T["vo"].items():
    x, sr = sf.read(f"{VODIR}/{name}.wav", dtype="float32")
    x = np.interp(np.arange(int(len(x) * SR / sr)) * sr / SR, np.arange(len(x)), x)
    place(vo, x, t, 1.0, 0.0)
# light voice chain: high-pass, presence
vo = hp(vo.T, 75).T
vo_env = lp(np.abs(vo).mean(1), 4)
vo_env = vo_env / (vo_env.max() + 1e-9)
# duck music ~8 dB under speech (smoothed so it breathes)
gate = (vo_env > 0.04).astype(float)
gate = lp(np.convolve(gate, np.ones(int(0.25 * SR)) / int(0.25 * SR), "same"), 3)
music *= (1 - 0.6 * np.clip(gate, 0, 1))[:, None]

# ---------------- sound design ----------------
sfx = np.zeros((N, 2))
def whoosh():
    n = int(0.7 * SR); tt = np.arange(n) / SR
    x = rng.standard_normal(n); env = np.sin(np.pi * np.clip(tt / 0.7, 0, 1)) ** 2.2
    lo = bp(x, 300, 1200) * np.linspace(1, 0.2, n); hi = bp(x, 1500, 6000) * np.linspace(0.2, 1, n)
    return (lo + hi * 0.6) * env * 0.16
def tap():
    n = int(0.06 * SR); tt = np.arange(n) / SR
    return (np.sin(2 * np.pi * 1900 * tt) * 0.6 + hp(rng.standard_normal(n), 3000) * 0.3) * np.exp(-tt * 120) * 0.22
def tick():
    a = tap() * 0.8; n = len(a); out = np.zeros(n + int(0.07 * SR)); out[:n] += a; out[int(0.07 * SR):] += a * 0.7; return out
def chime():
    n = int(1.4 * SR); tt = np.arange(n) / SR; y = np.zeros(n)
    for f, dl, g in [(1046.5, 0, 1), (1318.5, 0.08, 0.9), (1568.0, 0.16, 0.7)]:
        s = np.clip(tt - dl, 0, None)
        y += g * (np.sin(2 * np.pi * f * s) + 0.2 * np.sin(4 * np.pi * f * s)) * np.exp(-s * 4) * (tt >= dl)
    return y * 0.07
def pop():
    n = int(0.12 * SR); tt = np.arange(n) / SR; f = 320 + 500 * tt / 0.12
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 30) * 0.16
def logo():
    n = int(2.0 * SR); tt = np.arange(n) / SR
    boom = np.sin(2 * np.pi * (45 + 40 * np.exp(-tt * 20)) * tt) * np.exp(-tt * 3.5) * 0.35
    shimmer = sum(np.sin(2 * np.pi * f * tt) * np.exp(-tt * k) for f, k in [(1760, 3), (2637, 4), (3520, 5)]) * 0.025
    return boom + shimmer
GEN = {"whoosh": whoosh, "tap": tap, "tick": tick, "chime": chime, "pop": pop, "logo": logo}
for t, kind in T["sfx"]:
    x = GEN[kind]()
    if kind == "logo":
        sw = whoosh() * 0.8; place(sfx, sw, t - 0.55, 1.0, 0)
    place(sfx, x, t, 1.0, 0.15 if kind in ("tap", "pop") else 0.0)
sfx_rev = np.stack([fftconvolve(sfx[:, c], ir[:, c])[:N] for c in range(2)], 1) * 0.25
sfx = sfx + sfx_rev

# ---------------- stems -> master ----------------
def lufs(x, path):
    sf.write(path, x.astype(np.float32), SR)
    o = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    return float(o.split("I:")[-1].split("LUFS")[0])
vo_l = lufs(vo, "/tmp/_vo.wav"); mu_l = lufs(music, "/tmp/_mu.wav")
vo *= 10 ** ((-17 - vo_l) / 20)
music *= 10 ** ((-27 - mu_l) / 20)      # bed sits ~10 LU under the voice
mix = vo + music + sfx
sf.write("/tmp/_mix.wav", mix.astype(np.float32), SR)
meas = subprocess.run(["ffmpeg", "-hide_banner", "-i", "/tmp/_mix.wav", "-af", "loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
j = json.loads(meas[meas.rindex("{"):])
ln = (f"loudnorm=I=-16:TP=-1.5:LRA=9:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}"
      f":measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "/tmp/_mix.wav", "-af", f"{ln},alimiter=limit=0.84:level=false,aresample=48000", "-ar", "48000", "-c:a", "pcm_s16le", OUT], check=True)
print("vo", round(vo_l, 1), "music", round(mu_l, 1), "->", OUT)

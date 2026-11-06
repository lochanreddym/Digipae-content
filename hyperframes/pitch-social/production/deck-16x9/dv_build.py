# 16:9 narrated deck video: slides + real app section (reuses the synced social cut) + end card, captions, score, -14 LUFS.
import json, re, subprocess, os, math
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFont, ImageFilter
SP = os.path.dirname(os.path.abspath(__file__)); D = f"{SP}/dv"; PV = f"{SP}/pv"; SL = f"{SP}/deckvid/sl"
REPO = "/home/user/Digipae-content"; ICON = f"{REPO}/hyperframes/pitch-social/assets/digipae-icon.png"
os.chdir(D); os.makedirs("clips", exist_ok=True)
L = {m["name"]: m for m in json.load(open("lines.json"))}
PT = json.load(open(f"{PV}/timing.json")); PL = {m["name"]: m for m in json.load(open(f"{PV}/lines.json"))}
FPS = 30; fr = lambda x: round(round(x * FPS) / FPS, 4)
NAVY = (5, 13, 23); W, H = 1920, 1080; SX, SY, SW, SH = 96, 14, 1728, 972      # slide frame; captions live in the band below
font = lambda w, s: ImageFont.truetype(f"/usr/share/fonts/opentype/inter/Inter-{w}.otf", s)
dfont = lambda s: ImageFont.truetype("/usr/share/fonts/opentype/inter/InterDisplay-ExtraBold.otf", s)

def bg():
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((x - 960) / 1100) ** 2 + ((y - 470) / 700) ** 2); k = np.clip(1 - r, 0, 1) ** 1.6
    c = np.array(NAVY, np.float32) + k[..., None] * (np.array((18, 48, 74), np.float32) - np.array(NAVY, np.float32))
    c += np.random.default_rng(0).uniform(-0.6, 0.6, c.shape)          # dither against banding
    return Image.fromarray(np.clip(c, 0, 255).astype(np.uint8))

# ---- sequence ----
SEQ = [("slide", "d01", 1), ("slide", "d02", 2), ("slide", "d03", 3), ("slide", "d04", 4), ("slide", "d05", 5), ("demo",),
       ("slide", "d06", 6), ("slide", "d07", 7), ("slide", "d09", 9), ("slide", "d10", 10), ("end", "d13")]
LEAD, TAIL = 0.45, 0.75
VO, items, t = {}, [], 0.0
B0 = PT["segs"][0]["t"]; BDUR = round(PT["segs"][-1]["t"] + PT["segs"][-1]["dur"] - B0, 4)
for it in SEQ:
    if it[0] == "demo":
        dur = fr(0.5 + BDUR + 0.4)
        for n, v in PT["vo"].items():
            if n.startswith("b"): VO[n] = round(t + 0.5 + v - B0, 3)
        items.append({"kind": "demo", "t": t, "dur": dur}); t += dur; continue
    n = it[1]; dur = fr(LEAD + L[n]["dur"] + TAIL + (1.6 if it[0] == "end" else 0))
    VO[n] = round(t + LEAD, 3); items.append({"kind": it[0], "line": n, "slide": it[2] if len(it) > 2 else None, "t": t, "dur": dur}); t += dur
END = fr(t)

# ---- stills ----
def slide_frame(k):
    im = bg(); s = Image.open(f"{SL}/s-{k:02d}.png").convert("RGB").resize((SW, SH), Image.LANCZOS)
    sh = Image.new("L", (W, H), 0); ImageDraw.Draw(sh).rounded_rectangle((SX, SY + 10, SX + SW, SY + SH + 10), 18, fill=150)
    im = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), im, sh.filter(ImageFilter.GaussianBlur(24)))
    m = Image.new("L", (SW, SH), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, SW - 1, SH - 1), 18, fill=255)
    im.paste(s, (SX, SY), m); return im
def demo_bg():
    im = bg(); d = ImageDraw.Draw(im)
    d.rounded_rectangle((150, 300, 618, 352), 26, outline=(55, 213, 232), width=2, fill=(10, 40, 55))
    d.text((175, 309), "REAL APP · PRODUCT PREVIEW", font=font("Bold", 26), fill=(55, 213, 232))
    d.text((150, 390), "Here's the app,", font=dfont(84), fill=(244, 248, 251))
    d.text((150, 485), "today.", font=dfont(84), fill=(55, 213, 232))
    d.text((150, 620), "Screen recording, retimed so each step\nlands on its narration. Document\nauto-retrieval is shown as coming soon.", font=font("Medium", 32), fill=(164, 180, 195), spacing=12)
    d.rounded_rectangle((1196, 22, 1196 + 470, 22 + 1004), 64, fill=(0, 0, 0), outline=(44, 74, 102), width=3)
    return im
def end_card():
    im = bg(); d = ImageDraw.Draw(im)
    ic = Image.open(ICON).convert("RGBA").resize((150, 152), Image.LANCZOS); im.paste(ic, (885, 120), ic)
    d.text((960, 330), "DigiPae", font=dfont(120), fill=(244, 248, 251), anchor="mm")
    q = "“Government services should be easier to connect to,\neasier to navigate, and easier to build upon.”"
    d.multiline_text((960, 500), q, font=font("SemiBold", 46), fill=(55, 213, 232), anchor="mm", align="center", spacing=16)
    d.rounded_rectangle((640, 640, 1280, 712), 36, fill=(244, 248, 251))
    d.text((960, 676), "Building toward Plaid for government", font=font("Bold", 34), fill=(8, 21, 34), anchor="mm")
    d.text((960, 770), "digipae.com  ·  Operated by CEIVIS LLC", font=font("Medium", 30), fill=(164, 180, 195), anchor="mm")
    d.text((960, 880), "“Plaid for government” is an analogy only; not affiliated with Plaid. The app shown is a product preview;\nsome features are in development. Statistics are sourced in the deck appendix.",
           font=font("Regular", 24), fill=(164, 180, 195), anchor="mm", align="center", spacing=8)
    return im

# ---- clips ----
def run(a): subprocess.run(["ffmpeg", "-v", "error", "-y", *a], check=True)
enc = ["-c:v", "libx264", "-crf", "17", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", str(FPS), "-threads", "2"]
for i, it in enumerate(items):
    out = f"clips/c{i:02d}.mp4"; it["file"] = out; n = int(round(it["dur"] * FPS))
    fade = f"fade=in:st=0:d=0.3:color=0x050d17,fade=out:st={it['dur'] - 0.3}:d=0.3:color=0x050d17"
    if it["kind"] in ("slide", "end"):
        (slide_frame(it["slide"]) if it["kind"] == "slide" else end_card()).save("still.png")
        z = f"zoompan=z='1+0.035*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s={W}x{H}:fps={FPS}"
        run(["-loop", "1", "-i", "still.png", "-vf", f"scale={W*2}:{H*2},{z},{fade}", "-frames:v", str(n), *enc, out])
    else:
        demo_bg().save("demobg.png")
        m = Image.new("L", (452, 982), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, 451, 981), 54, fill=255); m.save("mask.png")
        fc = (f"[1:v]scale=452:982,setpts=PTS+0.5/TB[v];[2:v]format=gray[m];[v][m]alphamerge[vm];"
              f"[0:v][vm]overlay=1205:33:eof_action=pass,{fade}")
        run(["-loop", "1", "-t", str(it["dur"]), "-i", "demobg.png", "-i", f"{REPO}/hyperframes/pitch-social/assets/demo.mp4", "-loop", "1", "-i", "mask.png",
             "-filter_complex", fc, "-frames:v", str(n), *enc, out])
open("clips/list.txt", "w").write("\n".join(f"file '{os.path.basename(it['file'])}'" for it in items))
run(["-f", "concat", "-safe", "0", "-i", "clips/list.txt", "-c", "copy", "video.mp4"])

# ---- captions (ASS) ----
def phrases(text, maxw=9):
    out, cur = [], []
    for w in text.split():
        cur.append(w)
        if re.search(r"[.,:;?!]$", w) and len(cur) >= 3 or len(cur) >= maxw: out.append(cur); cur = []
    if cur:
        if out and len(cur) < 3: out[-1] += cur
        else: out.append(cur)
    return out
caps = []
for n, start in VO.items():
    if n.startswith("b"):
        for c in PT["captions"]:
            if c["part"] == "b": pass
        continue
    text = L[n]["spoken"].replace("Digipay", "DigiPae").replace("Login dot gov", "Login.gov").replace("ID dot me", "ID.me").replace("ninety two million dollars", "$92 million").replace("ten and a half billion", "10.5 billion").replace("two in three", "2 in 3")
    ps = phrases(text); tot = sum(len(" ".join(p)) for p in ps); acc = 0
    for p in ps:
        s = start + L[n]["dur"] * acc / tot; acc += len(" ".join(p)); e = start + L[n]["dur"] * acc / tot
        caps.append((s - 0.05, e, " ".join(p)))
for c in PT["captions"]:                                            # the app section reuses the social cut's word-timed captions
    if c["part"] == "b":
        off = items[5]["t"] + 0.5 - B0; caps.append((c["s"] + off, c["e"] + off, c["text"]))
caps.sort()
for i in range(len(caps) - 1):
    if caps[i][1] > caps[i + 1][0]: caps[i] = (caps[i][0], caps[i + 1][0], caps[i][2])
ts = lambda x: f"{int(x//3600)}:{int(x%3600//60):02d}:{x%60:05.2f}"
ass = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "", "[V4+ Styles]",
       "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
       "Style: Cap,Inter SemiBold,38,&H00FBF8F4,&H00FFFFFF,&HE0170D05,&H80000000,0,0,0,0,100,100,0,0,3,14,0,2,200,200,22,1", "", "[Events]",
       "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
ass += [f"Dialogue: 0,{ts(s)},{ts(e)},Cap,,0,0,0,,{t}" for s, e, t in caps]
open("caps.ass", "w").write("\n".join(ass) + "\n")
json.dump({"end": END, "vo": VO, "items": items}, open("dv_timing.json", "w"), indent=1)

# ---- audio: soft score + whooshes at cuts + VO, ducked, -14 LUFS ----
SR = 48000; N = int(END * SR); rng = np.random.default_rng(3)
from scipy.signal import butter, sosfilt, fftconvolve
lp = lambda x, f: sosfilt(butter(2, f, "low", fs=SR, output="sos"), x)
bpf = lambda x, a, b: sosfilt(butter(2, [a, b], "band", fs=SR, output="sos"), x)
mtof = lambda m: 440.0 * 2 ** ((m - 69) / 12)
CH = [[45, 52, 57, 60, 64], [41, 53, 57, 60, 65], [48, 52, 55, 60, 67], [43, 50, 55, 59, 62]]
BAR = 4 * 60 / 84; mus = np.zeros((N, 2)); tt_all = np.arange(N) / SR
for b, t0 in enumerate(np.arange(0, END + BAR, BAR)):
    n = int((BAR + 1.2) * SR); tt = np.arange(n) / SR; env = np.minimum(1, tt / 0.8) * np.minimum(1, (n / SR - tt) / 1.2)
    y = sum(np.sin(2 * np.pi * mtof(m) * tt + k) * (0.5 if k else 0.8) for k, m in enumerate(CH[b % 4])) * env
    i = int(t0 * SR); j = min(N, i + n)
    if i < N: mus[i:j, 0] += lp(y, 1400)[: j - i] * 0.02; mus[i:j, 1] += lp(y, 1400)[: j - i] * 0.02
    for e in range(8):
        te = t0 + e * BAR / 8; np_ = int(0.3 * SR); t2 = np.arange(np_) / SR
        p = np.sin(2 * np.pi * mtof(CH[b % 4][1 + e % 4] + 12) * t2) * np.exp(-t2 * 11) * 0.012
        i = int(te * SR); j = min(N, i + np_)
        if i < N: mus[i:j, e % 2] += p[: j - i]
mus *= (np.clip(tt_all / 1.0, 0, 1) * np.clip((END - tt_all) / 2.0, 0, 1))[:, None]
for it in items[1:]:
    n = int(0.7 * SR); t2 = np.arange(n) / SR; w = bpf(rng.standard_normal(n), 400, 3000) * np.sin(np.pi * t2 / 0.7) ** 2 * 0.035
    i = int((it["t"] - 0.35) * SR); mus[i:i + n] += w[:, None]
vo = np.zeros(N)
for n, t0 in VO.items():
    x, sr = sf.read(f"{PV if n.startswith('b') else D}/{n}.wav", dtype="float32")
    x = np.interp(np.arange(int(len(x) * SR / sr)) * sr / SR, np.arange(len(x)), x); i = int(t0 * SR); vo[i:i + len(x)] += x[: N - i]
env = lp(np.abs(vo), 4); env /= env.max() + 1e-9
gate = np.clip(lp(np.convolve((env > 0.04).astype(float), np.ones(int(0.25 * SR)) / int(0.25 * SR), "same"), 3), 0, 1)
mus *= (1 - 0.45 * gate)[:, None]
def lufs(x):
    sf.write("_x.wav", x.astype(np.float32), SR)
    o = subprocess.run(["ffmpeg", "-hide_banner", "-i", "_x.wav", "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    return float(o.split("I:")[-1].split("LUFS")[0])
vo2 = np.stack([vo, vo], 1); vo2 *= 10 ** ((-16 - lufs(vo2)) / 20); mus *= 10 ** ((-26 - lufs(mus)) / 20)
sf.write("_mix.wav", (vo2 + mus).astype(np.float32), SR)
m = subprocess.run(["ffmpeg", "-hide_banner", "-i", "_mix.wav", "-af", "loudnorm=I=-14:TP=-1.5:LRA=9:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
j = json.loads(m[m.rindex("{"):])
ln = (f"loudnorm=I=-14:TP=-1.5:LRA=9:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}"
      f":measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
run(["-i", "_mix.wav", "-af", f"{ln},alimiter=limit=0.84:level=false,aresample=48000", "-ar", "48000", "mix.wav"])
run(["-i", "video.mp4", "-i", "mix.wav", "-vf", "ass=caps.ass", *enc, "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", "digipae-pitch-deck-16x9.mp4"])
print("END", END)

# Lay narration lines on the timeline, master the VO track, and emit captions + visual sync anchors.
import json, subprocess, numpy as np, soundfile as sf
L = {m["name"]: m for m in json.load(open("lines.json"))}
GAP = {"hook": 0.5, "scan": 0.45, "portal": 0.3, "rate": 0.45, "payout": 0.45, "setup": 0.4, "outro": 0.85}
order = ["hook", "scan", "portal", "rate", "payout", "setup", "outro"]
t = 0.0; start = {}
for n in order:
    t += GAP[n]; start[n] = round(t, 3); t += L[n]["dur"]
END = round(t + 1.15, 2)
end = {n: start[n] + L[n]["dur"] for n in order}
W = lambda n, i: start[n] + L[n]["asr"][i]["s"]           # absolute time of the i-th spoken word

# old timeline time -> new time; segments are shifted, never stretched
anchors = [
    (0.0, 0.0),
    (3.0, start["scan"] - 0.15),
    (3.2, W("scan", 1) - 0.08),          # brackets lock on "scan"
    (4.3, W("scan", 6) - 0.08),          # sheet rises on "confirmed"
    (5.55, start["portal"] - 0.45),      # phone leaves, portal arrives with "Every sale lands"
    (6.65, end["portal"] + 0.05),
    (7.0, start["rate"] - 0.15),         # rate card frame
    (7.2, W("rate", 3) - 0.1),           # 1.29% on "one point two nine"
    (7.95, W("rate", 8) - 0.1),          # checklist on "No monthly fee"
    (11.65, end["rate"] + 0.05),
    (12.1, start["payout"] - 0.2),
    (15.65, start["setup"] - 0.4),
    (16.05, start["setup"] - 0.15),
    (17.7, end["setup"] + 0.1),
    (18.1, start["outro"] - 0.55),       # logo lands, then "Digipae"
    (21.0, END),
]
for (o1, n1), (o2, n2) in zip(anchors, anchors[1:]):
    assert n2 > n1, (o1, o2)

# caption tokens mapped onto spoken word indices
CAP = {
  "hook":   [("Every",0),("fee,",1),("shown",2),("before",3),("you",4),("accept",5),("it.",6)],
  "scan":   [("Customers",0),("scan",1),("to",2),("pay,",3),"|",("and",4),("it's",5),("confirmed",6),("right",7),("in",8),("the",9),("app.",10)],
  "portal": [("Every",0),("sale",1),("lands",2),("in",3),("your",4),("merchant",5),("portal.",6)],
  "rate":   [("One",0),("flat",1),("rate.",2),("1.29%.",3),"|",("No",8),("monthly",9),("fee.",10),("No",11),("minimum.",12)],
  "payout": [("Free",0),("next-day",1),("payouts.",3),("Every",4),("time.",5)],
  "setup":  [("No",0),("hardware.",1),("No",2),("setup",3),("fee.",4)],
  "outro":  [("Digipae.",0),"|",("See",3),("the",4),("fee.",5),("Keep",6),("the",7),("rest.",8)],
}
chunks = []
for n in order:
    cur = []
    for tok in CAP[n] + ["|"]:
        if tok == "|":
            if cur: chunks.append({"words": cur}); cur = []
            continue
        txt, i = tok; cur.append({"t": round(W(n, i), 3), "w": txt})
    chunks[-1]["lineEnd"] = end[n]
for c in chunks: c["s"] = round(c["words"][0]["t"] - 0.12, 3)
for i, c in enumerate(chunks):
    nxt = chunks[i + 1]["s"] if i + 1 < len(chunks) else END
    c["e"] = round(min(nxt, c.get("lineEnd", c["words"][-1]["t"] + 0.9) + 0.25), 3)
    c.pop("lineEnd", None)

# narration track: lines at their starts, cleaned and mastered for web
sr = 24000
track = np.zeros(int(END * sr) + sr, np.float32)
for n in order:
    x, _ = sf.read(f"{n}.wav", dtype="float32"); i = int(start[n] * sr)
    track[i:i + len(x)] += x
sf.write("vo_raw.wav", track[: int(END * sr)], sr)
chain = "highpass=f=70,equalizer=f=250:t=q:w=1:g=-1.5,equalizer=f=4000:t=q:w=1.2:g=1.5,acompressor=threshold=-22dB:ratio=2.5:attack=6:release=120:makeup=2dB"
meas = subprocess.run(["ffmpeg", "-hide_banner", "-i", "vo_raw.wav", "-af", chain + ",loudnorm=I=-16:TP=-1.5:LRA=7:print_format=json", "-f", "null", "-"],
                      capture_output=True, text=True).stderr
j = json.loads(meas[meas.rindex("{"):])
ln = (f"loudnorm=I=-16:TP=-1.5:LRA=7:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}"
      f":measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "vo_raw.wav", "-af", f"{chain},{ln},aresample=48000", "-ac", "2", "-c:a", "pcm_s16le", "vo.wav"], check=True)
json.dump({"end": END, "starts": start, "anchors": anchors, "captions": chunks}, open("timing.json", "w"), indent=1)
print("END", END); print({n: round(start[n], 2) for n in order})
for c in chunks: print(f"{c['s']:6.2f}-{c['e']:6.2f}", " ".join(w["w"] for w in c["words"]))

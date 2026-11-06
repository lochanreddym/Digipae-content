# Scene timing, caption tokens and sound-effect cues for the 8-screen promo, all derived from the narration.
import json, re
L = {m["name"]: m for m in json.load(open("lines.json"))}
INTRO, LEAD, TAIL = 3.0, 0.75, 0.7
scenes, t = [], INTRO
vo = {"intro": 1.25}
for n in ["s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8"]:
    v = t + LEAD; vo[n] = round(v, 3)
    end = v + L[n]["dur"] + TAIL
    scenes.append({"id": n, "start": round(t, 3), "end": round(end, 3), "vo": round(v, 3)}); t = end
vo["outro"] = round(t + 0.95, 3)
END = round(vo["outro"] + L["outro"]["dur"] + 1.7, 2)

def words(n):
    return [{"w": w["w"], "t": round(vo[n] + w["s"], 3)} for w in L[n]["asr"]]
W = {n: words(n) for n in vo}

def fix(n, ws):
    out, i = [], 0
    while i < len(ws):
        w = ws[i]["w"]
        if w.lower() == "did" and i + 2 < len(ws) and ws[i+1]["w"].lower() == "you" and ws[i+2]["w"].lower().startswith("pay"):
            out.append({"w": "Digipae.", "t": ws[i]["t"]}); i += 3; continue
        w = {"id,": "ID,", "id": "ID", "face": "Face", "identity?": "identity.", "one": "One" if n == "outro" else "one",
             "and": "And" if (n == "s8" and i == 0) else "and"}.get(w, w)
        out.append({"w": w, "t": ws[i]["t"]}); i += 1
    return out

# captions: one phrase per sentence; long sentences split at the comma nearest the middle
def phrases(ws):
    sent, cur = [], []
    for w in ws:
        cur.append(w)
        if w["w"][-1] in ".?!": sent.append(cur); cur = []
    if cur: sent.append(cur)
    out = []
    for snt in sent:
        if len(snt) <= 6: out.append(snt); continue
        commas = [i for i, w in enumerate(snt[:-1]) if w["w"].endswith(",") and 2 <= i + 1 <= len(snt) - 2]
        cut = min(commas, key=lambda i: abs(i + 1 - len(snt) / 2)) + 1 if commas else len(snt) // 2
        out += [snt[:cut], snt[cut:]]
    return out
caps = []
for n in ["s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8"]:
    ws = fix(n, W[n])
    for i in range(len(ws) - 1):
        if ws[i]["w"] == "government" and ws[i + 1]["w"].startswith("verified"):
            ws[i]["w"] = "government-" + ws[i + 1]["w"]; ws[i + 1]["w"] = None
    ws = [w for w in ws if w["w"]]
    for ph in phrases(ws): caps.append({"words": ph})
    caps[-1]["lineEnd"] = vo[n] + L[n]["dur"]
for c in caps: c["s"] = round(c["words"][0]["t"] - 0.12, 3)
for i, c in enumerate(caps):
    nxt = caps[i + 1]["s"] if i + 1 < len(caps) else END
    stop = c.pop("lineEnd", None) or (c["words"][-1]["t"] + 0.7)
    c["e"] = round(min(nxt, stop + 0.3), 3)

def at(n, k):  # absolute time of the k-th spoken word of line n
    return W[n][k]["t"]

# beats: (time, kind) — visuals in index.html and sounds in the mix both read these
beats = {
  "s1": {"count": at("s1", 0), "lift": at("s1", 2), "qr": at("s1", 4)},
  "s2": {"lock": at("s2", 0) + 0.15, "pay": at("s2", 2), "tap": at("s2", 4), "done": at("s2", 10) - 0.05, "chips": at("s2", 11)},
  "s3": {"tap": at("s3", 0), "list": at("s3", 2), "verify": at("s3", 5), "lock": at("s3", 6)},
  "s4": {"lift": at("s4", 2), "hide": at("s4", 5), "grid": at("s4", 0) + 0.2, "tap": at("s4", 8)},
  "s5": {"count": at("s5", 0), "scroll": at("s5", 1), "tap": at("s5", 6), "export": at("s5", 8)},
  "s6": {"stats": at("s6", 1), "rewards": at("s6", 2), "accounts": at("s6", 4), "card": at("s6", 6)},
  "s7": {"scan": at("s7", 0), "dots": at("s7", 3), "unlock": at("s7", 8) + 0.1},
  "s8": {"stamp": at("s8", 4), "access": at("s8", 7), "devices": at("s8", 8), "privacy": at("s8", 10)},
}
sfx = []
for s in scenes[1:]: sfx.append((s["start"] - 0.25, "whoosh"))
sfx += [(scenes[0]["start"] - 0.2, "whoosh"), (vo["outro"] - 0.95, "whoosh")]
sfx += [(beats["s2"]["lock"], "tick"), (beats["s2"]["tap"], "tap"), (beats["s2"]["done"], "chime"),
        (beats["s3"]["tap"], "tap"), (beats["s3"]["verify"], "tick"), (beats["s4"]["lift"], "pop"),
        (beats["s4"]["tap"], "tap"), (beats["s5"]["tap"], "tap"), (beats["s6"]["card"], "pop"),
        (beats["s7"]["unlock"], "chime"), (beats["s8"]["stamp"], "pop"), (beats["s1"]["lift"], "pop"),
        (0.85, "logo"), (vo["outro"] - 0.4, "logo")]
json.dump({"end": END, "intro": INTRO, "vo": vo, "scenes": scenes, "captions": caps, "beats": beats,
           "sfx": sorted(sfx), "outroStart": round(t, 3)}, open("timing.json", "w"), indent=1)
print("END", END)
for s in scenes: print(s)
for c in caps: print(f"{c['s']:6.2f}-{c['e']:6.2f}", " ".join(w["w"] for w in c["words"]))

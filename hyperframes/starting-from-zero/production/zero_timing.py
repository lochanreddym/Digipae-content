# Timeline for "Stop starting from zero": narration placement, scene windows, word-anchored beats, captions.
import json
L = {m["name"]: m for m in json.load(open("lines.json"))}
GAP = {"v1": 0.4, "v2": 0.25, "v3": 1.0, "v4": 0.45, "v5": 0.5, "v6": 0.45, "v7": 0.45, "v8": 0.5, "v9": 0.65}
order = list(GAP)
VO, t = {}, 0.0
for n in order:
    t += GAP[n]; VO[n] = round(t, 3); t += L[n]["dur"]
END = round(t + 1.3, 2)
E = {n: round(VO[n] + L[n]["dur"], 3) for n in order}
W = lambda n, i: round(VO[n] + L[n]["asr"][i]["s"], 3)
# scene windows: each scene opens a beat before its line
S = {"s1": 0.0, "s2": VO["v2"] - 0.1, "s3": E["v2"] + 0.6, "s4": VO["v4"] - 0.3, "s5": VO["v5"] - 0.35,
     "s6": VO["v6"] - 0.35, "s7": VO["v7"] - 0.35, "s8": VO["v8"] - 0.4, "fin": VO["v9"] - 0.55, "end": END}
B = {
  "s1": {"type": W("v1", 7) - 0.15, "doc": W("v1", 11) - 0.1, "form4": W("v1", 15) - 0.1},
  "s2": {"l1": W("v2", 0), "l2": W("v2", 1), "l3": W("v2", 2), "l4": W("v2", 3), "rep": W("v2", 4), "silence": E["v2"] + 0.05},
  "s3": {"perm": W("v3", 3) - 0.1, "phone": W("v3", 2) - 0.2},
  "s4": {"data": VO["v4"] + 0.05, "toggle": W("v4", 5) + 0.1, "press": W("v4", 7) - 0.1, "release": W("v4", 11) - 0.05, "perm": W("v4", 7)},
  "s5": {"verify": W("v5", 4) - 0.1, "packet": W("v5", 5), "request": W("v5", 9) - 0.15, "tap": W("v5", 12) - 0.05, "reuse": W("v5", 9)},
  "s6": {"request": W("v6", 4) - 0.1, "card": W("v6", 7) - 0.15, "approve": W("v6", 13) - 0.05, "tunnel": W("v6", 14) + 0.25},
  "s7": {"discover": W("v7", 3) - 0.1, "programs": W("v7", 5) - 0.2, "tap": W("v7", 9) - 0.05, "need": W("v7", 13) - 0.15, "apply": W("v7", 16) - 0.1},
  "s8": {"lines": W("v8", 3) - 0.1, "people": W("v8", 6) - 0.1, "services": W("v8", 8) - 0.05, "connect": W("v8", 10) - 0.1},
  "fin": {"word": W("v9", 0) - 0.05, "line1": W("v9", 1) - 0.05, "plaid": W("v9", 3) - 0.1},
}
# phrase captions (on-screen text uses the brand spelling DigiPae)
P = [("v1", "Every time you apply for a public service,", 0, 7), ("v1", "you may be asked for the same information again…", 8, 16),
     ("v2", "…identity, address, income, documents —", 0, 3), ("v2", "over and over.", 4, 6),
     ("v3", "DigiPae is exploring a consent-based", 0, 3), ("v3", "connection layer for government data.", 4, 8),
     ("v4", "You see what information is requested.", 0, 5), ("v4", "You decide what can be shared.", 6, 11),
     ("v5", "The vision is simple: verified information", 0, 5), ("v5", "that can be reused when you choose —", 6, 12), ("v5", "instead of starting from zero every time.", 13, 19),
     ("v6", "Eventually, that could mean retrieving the right record", 0, 7), ("v6", "from the right source — with user permission.", 8, 14),
     ("v7", "And helping people understand what programs", 0, 5), ("v7", "may fit their situation —", 6, 9), ("v7", "and what they'll need before they apply.", 10, 16),
     ("v8", "We're building toward infrastructure", 0, 3), ("v8", "that helps people and public services connect more simply.", 4, 12),
     ]  # final line is carried by the on-screen brand card
caps = []
for k, (n, text, a, b) in enumerate(P):
    s = W(n, a) - 0.1
    last_of_line = k + 1 == len(P) or P[k + 1][0] != n
    nxt = W(P[k + 1][0], P[k + 1][2]) - 0.1 if k + 1 < len(P) else END
    e = min(nxt, E[n] + 0.3) if last_of_line else nxt
    caps.append({"text": text, "s": round(s, 3), "e": round(e, 3)})
json.dump({"end": END, "vo": VO, "voEnd": E, "scenes": S, "beats": B, "captions": caps}, open("timing.json", "w"), indent=1)
print("END", END); print({k: round(v, 2) for k, v in S.items()})

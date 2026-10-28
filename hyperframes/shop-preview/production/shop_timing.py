# 30s vertical preview: narration placement, phrase captions and visual beats, from ASR word timings.
import json
L = {m["name"]: m for m in json.load(open("lines.json"))}
VO = {"l1": 0.55, "l2": 5.25, "l3": 10.35, "l4": 18.35, "l5": 24.4}
END = 30.0
W = lambda n, i: round(VO[n] + L[n]["asr"][i]["s"], 3)
# phrases: (line, caption text, first word idx, last word idx)
P = [("l1", "You run the shop.", 0, 3), ("l1", "Checkout shouldn't steal the spotlight.", 4, 8),
     ("l2", "Meet Digipae.", 0, 1), ("l2", "Here's a preview of QR checkout", 2, 8), ("l2", "for local shops.", 9, 11),
     ("l3", "A customer scans your code in Digipae,", 0, 6), ("l3", "reviews the amount,", 7, 9), ("l3", "and confirms with their wallet PIN.", 10, 15),
     ("l4", "The payment appears in your merchant dashboard,", 0, 6), ("l4", "alongside your sales activity.", 7, 10),
     ("l5", "Built around everyday business.", 0, 3), ("l5", "Follow Digipae for product updates.", 4, 8)]
caps = []
for k, (n, text, a, b) in enumerate(P):
    s = W(n, a) - 0.1
    line_end = VO[n] + L[n]["dur"]
    nxt = W(P[k + 1][0], P[k + 1][2]) - 0.1 if k + 1 < len(P) else END
    e = min(nxt, (line_end + 0.35) if (k + 1 == len(P) or P[k + 1][0] != n) else nxt)
    caps.append({"text": text, "s": round(s, 3), "e": round(e, 3)})
beats = {
  "scan": W("l3", 2) - 0.15, "review": W("l3", 7) - 0.1, "confirm": W("l3", 9 + 2) - 0.1,
  "pin": W("l3", 14), "done": round(VO["l3"] + L["l3"]["dur"] + 0.15, 3),
  "rowHi": W("l4", 2) - 0.1, "pullback": W("l4", 7) - 0.2,
  "endcard": W("l5", 4) - 0.25,
}
json.dump({"end": END, "vo": VO, "captions": caps, "beats": beats}, open("timing.json", "w"), indent=1)
for c in caps: print(f"{c['s']:6.2f}-{c['e']:6.2f}  {c['text']}")
print(beats)

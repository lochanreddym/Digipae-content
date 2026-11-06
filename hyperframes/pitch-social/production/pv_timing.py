# Timeline for the DigiPae social pitch: VO placement, footage segments (each app step lands on its line), beats, captions.
import json
L = {m["name"]: m for m in json.load(open("lines.json"))}
fr = lambda x: round(round(x * 30) / 30, 4)          # snap to 30 fps frames
W = lambda n, i: round(VO[n] + L[n]["asr"][i]["s"], 3)
VO = {}
# Part A · problem (motion graphics)
t = 0.3
for n, gap in [("a1", 0), ("a2", 0.4), ("a3", 0.45), ("a4", 0.5)]:
    t += gap; VO[n] = round(t, 3); t += L[n]["dur"]
B0 = fr(t + 0.45)                                     # app demo starts
# Part B · real app recording. (line, src_in, src_out, step label). Cuts sit on screen changes in the recording.
SEG = [("b1", 1.60, 3.90, "Open the app"), ("b2", 8.70, 16.60, "Sign in"), ("b3", 16.60, 23.00, "Verify"),
       ("b4", 23.00, 27.30, "Consent"), ("b5", 27.30, 35.95, "Secure PIN"), ("b6", 35.95, 41.15, "Home"),
       ("b7", 41.15, 43.65, "Documents"), ("b8", 43.65, 55.40, "Government IDs"), ("b9", 55.40, 58.45, "Coming soon"),
       ("b10", 58.45, 71.60, "Consent first")]
segs, t = [], B0
for n, a, b, lab in SEG:
    src = b - a; need = L[n]["dur"] + 0.5
    D = fr(max(need, src / 3.0))
    sp = min(src / D, 3.0) if src / D > 1 else max(src / D, 0.9)   # below 0.9x: play at 0.9x then hold last frame
    VO[n] = round(t + 0.12, 3)
    segs.append({"line": n, "in": a, "out": b, "t": round(t, 4), "dur": D, "speed": round(sp, 4), "label": lab})
    t = round(t + D, 4)
B1 = t
# Part C · close
VO["c1"] = round(B1 + 0.45, 3); VO["c2"] = round(VO["c1"] + L["c1"]["dur"] + 0.45, 3)
END = fr(VO["c2"] + L["c2"]["dur"] + 2.1)
E = {n: round(VO[n] + L[n]["dur"], 3) for n in VO}
S = {"a1": 0, "a2": VO["a2"] - 0.25, "a3": VO["a3"] - 0.3, "a4": VO["a4"] - 0.3, "b": B0, "c": B1, "fin": VO["c2"] - 0.35, "end": END}
BT = {
  "a1": {"zero": W("a1", 9)},
  "a2": {"p1": W("a2", 0), "acc": W("a2", 2), "id": W("a2", 6), "addr": W("a2", 7), "inc": W("a2", 9), "again": W("a2", 12)},
  "a3": {"stat": W("a3", 9) - 0.1, "lost": W("a3", 15), "paper": W("a3", 18) - 0.05},
  "a4": {"fin": W("a4", 0), "gov": W("a4", 5), "dp": W("a4", 9) - 0.1, "think": W("a4", 13)},
  "b9": {"soon": W("b9", 8) - 0.1, "vault": W("b9", 10) - 0.1},
  "c1": {"docs": W("c1", 5) - 0.05, "ver": W("c1", 6) - 0.05, "elig": W("c1", 8) - 0.05},
  "c2": {"word": VO["c2"] - 0.05, "plaid": W("c2", 2) - 0.05, "follow": W("c2", 6) - 0.05},
}
P = [("a1", "Applying for a public service", 0, 4), ("a1", "still means starting from zero.", 5, 9),
     ("a2", "Three portals. Three accounts.", 0, 3), ("a2", "The same identity, address, and income,", 4, 9), ("a2", "typed in again every time.", 10, 14),
     ("a3", "In the final month of the Medicaid unwinding,", 0, 7), ("a3", "about 2 in 3 people who lost coverage lost it for paperwork reasons.", 8, 19),
     ("a4", "Finance got a connection layer.", 0, 4), ("a4", "Government services never did.", 5, 8), ("a4", "DigiPae is building it. Think Plaid, but for government.", 9, 17),
     ("b1", "Here's the app, today.", 0, 3), ("b2", "Sign in with just your phone number.", 0, 6), ("b3", "A one-time code confirms it's really you.", 0, 6),
     ("b4", "Before anything happens, you see exactly what you're agreeing to.", 0, 9), ("b5", "Then you lock it with your own PIN.", 0, 7),
     ("b6", "Your home screen holds your digital ID,", 0, 6), ("b6", "ready to verify.", 7, 9), ("b7", "Documents are organized by category.", 0, 4),
     ("b8", "Government IDs alone covers licenses,", 0, 4), ("b8", "passports, green cards, work permits, and more.", 5, 11),
     ("b9", "Pulling a license straight from the issuer is coming soon.", 0, 9), ("b9", "For now, you upload a copy to your vault.", 10, 17),
     ("b10", "Consent first. Only where access is permitted.", 0, 6),
     ("c1", "One consent-based connection", 0, 2), ("c1", "for government documents, verification, and eligibility.", 3, 8)]
caps = []
for k, (n, text, a, b) in enumerate(P):
    s = W(n, a) - 0.08
    last = k + 1 == len(P) or P[k + 1][0] != n
    nxt = W(P[k + 1][0], P[k + 1][2]) - 0.08 if k + 1 < len(P) else END
    e = min(nxt, E[n] + 0.35) if last else nxt
    caps.append({"text": text, "s": round(s, 3), "e": round(e, 3), "part": n[0]})
json.dump({"end": END, "vo": VO, "voEnd": E, "scenes": S, "beats": BT, "segs": segs, "captions": caps}, open("timing.json", "w"), indent=1)
print("END", END, "B", B0, B1)
for s in segs: print(s)

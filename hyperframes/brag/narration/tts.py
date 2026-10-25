import json, sys, numpy as np, soundfile as sf, sherpa_onnx as s
K = sys.argv[1]
c = s.OfflineTtsConfig(model=s.OfflineTtsModelConfig(kokoro=s.OfflineTtsKokoroModelConfig(
    model=f"{K}/model.onnx", voices=f"{K}/voices.bin", tokens=f"{K}/tokens.txt", data_dir=f"{K}/espeak-ng-data",
    dict_dir=f"{K}/dict", lexicon=f"{K}/lexicon-digipae.txt,{K}/lexicon-us-en.txt,{K}/lexicon-zh.txt"), num_threads=4))
tts = s.OfflineTts(c)
# spoken text (for the voice) and caption text (what appears on screen)
LINES = [
  ("hook",   "Every fee, shown before you accept it.",                         "Every fee, shown before you accept it."),
  ("scan",   "Customers scan to pay, and it's confirmed right in the app.", "Customers scan to pay, and it's confirmed right in the app."),
  ("portal", "Every sale lands in your merchant portal.",                      "Every sale lands in your merchant portal."),
  ("rate",   "One flat rate. One point two nine percent. No monthly fee. No minimum.", "One flat rate. 1.29%. No monthly fee. No minimum."),
  ("payout", "Free next-day payouts. Every time.",                             "Free next-day payouts. Every time."),
  ("setup",  "No hardware. No setup fee.",                                     "No hardware. No setup fee."),
  ("outro",  "Digipay. See the fee. Keep the rest.",                          "Digipae. See the fee. Keep the rest."),
]
meta = []
for name, spoken, cap in LINES:
    a = tts.generate(spoken, sid=3, speed=1.0)
    x = np.array(a.samples, dtype=np.float32)
    # trim leading/trailing silence
    idx = np.flatnonzero(np.abs(x) > 0.01)
    x = x[max(0, idx[0] - int(0.03 * a.sample_rate)): idx[-1] + int(0.08 * a.sample_rate)]
    sf.write(f"{name}.wav", x, a.sample_rate)
    meta.append({"name": name, "spoken": spoken, "caption": cap, "dur": round(len(x) / a.sample_rate, 3)})
    print(f"{name:7s} {len(x)/a.sample_rate:5.2f}s  {spoken}")
json.dump(meta, open("lines.json", "w"), indent=1)
print("sr", a.sample_rate, "total speech", round(sum(m["dur"] for m in meta), 2))

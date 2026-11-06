# Narration for "Stop starting from zero": each line voiced, ASR-verified, retried on dropped words.
import json, re, sys, numpy as np, soundfile as sf, sherpa_onnx as s
K, M, SPEED = sys.argv[1], sys.argv[2], float(sys.argv[3])
tts = s.OfflineTts(s.OfflineTtsConfig(model=s.OfflineTtsModelConfig(kokoro=s.OfflineTtsKokoroModelConfig(
    model=f"{K}/model.onnx", voices=f"{K}/voices.bin", tokens=f"{K}/tokens.txt", data_dir=f"{K}/espeak-ng-data",
    dict_dir=f"{K}/dict", lexicon=f"{K}/lexicon-digipae.txt,{K}/lexicon-us-en.txt,{K}/lexicon-zh.txt"), num_threads=4)))
rec = s.OfflineRecognizer.from_transducer(encoder=f"{M}/encoder.int8.onnx", decoder=f"{M}/decoder.int8.onnx",
    joiner=f"{M}/joiner.int8.onnx", tokens=f"{M}/tokens.txt", model_type="nemo_transducer", num_threads=4)
LINES = [tuple(x) for x in json.load(open("script.json"))]
_OLD = [
  ("v1", "Every time you apply for a public service, you may be asked for the same information again."),
  ("v2", "Identity. Address. Income. Documents. Over and over."),
  ("v3", "Digipay is exploring a consent-based connection layer for government data."),
  ("v4", "You see what information is requested. You decide what can be shared."),
  ("v5", "The vision is simple: verified information that can be reused when you choose, instead of starting from zero every time."),
  ("v6", "Eventually, that could mean retrieving the right record from the right source, with user permission."),
  ("v7", "And helping people understand what programs may fit their situation, and what they'll need before they apply."),
  ("v8", "We're building toward infrastructure that helps people and public services connect more simply."),
  ("v9", "Digipay. Building toward Plaid for government."),
]
only = set(sys.argv[4].split(",")) if len(sys.argv) > 4 else None
norm = lambda t: re.sub(r"[^a-z0-9 ]", "", t.lower().replace("-", " ")).split()
try: out = {m["name"]: m for m in json.load(open("lines.json"))}
except Exception: out = {}
for name, text in LINES:
    if only and name not in only: continue
    best = None
    for _ in range(4):
        a = tts.generate(text, sid=3, speed=SPEED); x = np.array(a.samples, np.float32)
        idx = np.flatnonzero(np.abs(x) > 0.01); x = x[max(0, idx[0] - 720): idx[-1] + 1920]
        st = rec.create_stream(); st.accept_waveform(a.sample_rate, x); rec.decode_stream(st)
        miss = [w for w in norm(text) if w not in norm(st.result.text) and w not in ("digipay",)]
        if best is None or len(miss) < best[0]: best = (len(miss), x, st.result.text)
        if not miss: break
    n, x, heard = best; sf.write(f"{name}.wav", x, 24000)
    out[name] = {"name": name, "spoken": text, "dur": round(len(x) / 24000, 3)}
    print(f"{name} {len(x)/24000:5.2f}s {len(text.split())/(len(x)/24000)*60:4.0f}wpm miss={n} heard: {heard}")
json.dump([out[k] for k in sorted(out)], open("lines.json", "w"), indent=1)

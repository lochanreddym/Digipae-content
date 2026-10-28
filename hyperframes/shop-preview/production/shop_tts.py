# Narration for the 30s local-shop preview: each line voiced + ASR-verified, at a pace near 135 wpm.
import json, re, sys, numpy as np, soundfile as sf, sherpa_onnx as s
K, M = sys.argv[1], sys.argv[2]; SPEED = float(sys.argv[3])
tts = s.OfflineTts(s.OfflineTtsConfig(model=s.OfflineTtsModelConfig(kokoro=s.OfflineTtsKokoroModelConfig(
    model=f"{K}/model.onnx", voices=f"{K}/voices.bin", tokens=f"{K}/tokens.txt", data_dir=f"{K}/espeak-ng-data",
    dict_dir=f"{K}/dict", lexicon=f"{K}/lexicon-digipae.txt,{K}/lexicon-us-en.txt,{K}/lexicon-zh.txt"), num_threads=4)))
rec = s.OfflineRecognizer.from_transducer(encoder=f"{M}/encoder.int8.onnx", decoder=f"{M}/decoder.int8.onnx",
    joiner=f"{M}/joiner.int8.onnx", tokens=f"{M}/tokens.txt", model_type="nemo_transducer", num_threads=4)
LINES = [
  ("l1", "You run the shop. Checkout shouldn't steal the spotlight."),
  ("l2", "Meet Digipay. Here's a preview of QR checkout for local shops."),
  ("l3", "A customer scans your code in Digipay, reviews the amount, and confirms with their wallet PIN."),
  ("l4", "The payment appears in your merchant dashboard, alongside your sales activity."),
  ("l5", "Built around everyday business. Follow Digipay for product updates."),
]
norm = lambda t: re.sub(r"[^a-z0-9 ]", "", t.lower().replace("-", " ")).split()
out = []
for name, text in LINES:
    best = None
    for _ in range(4):
        a = tts.generate(text, sid=3, speed=SPEED); x = np.array(a.samples, np.float32)
        idx = np.flatnonzero(np.abs(x) > 0.01); x = x[max(0, idx[0] - 720): idx[-1] + 1920]
        st = rec.create_stream(); st.accept_waveform(a.sample_rate, x); rec.decode_stream(st)
        miss = [w for w in norm(text) if w not in norm(st.result.text) and w not in ("digipay", "qr", "pin")]
        if best is None or len(miss) < best[0]: best = (len(miss), x, st.result.text)
        if not miss: break
    n, x, heard = best; sf.write(f"{name}.wav", x, 24000)
    wpm = len(text.split()) / (len(x) / 24000) * 60
    out.append({"name": name, "spoken": text, "dur": round(len(x) / 24000, 3)})
    print(f"{name} {len(x)/24000:5.2f}s {wpm:4.0f}wpm miss={n} heard: {heard}")
json.dump(out, open("lines.json", "w"), indent=1)

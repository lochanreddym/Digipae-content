# Voice every line for the 8-screen promo, verify each take by ASR, keep the first clean one.
import json, re, sys, numpy as np, soundfile as sf, sherpa_onnx as s
K, M = sys.argv[1], sys.argv[2]
tts = s.OfflineTts(s.OfflineTtsConfig(model=s.OfflineTtsModelConfig(kokoro=s.OfflineTtsKokoroModelConfig(
    model=f"{K}/model.onnx", voices=f"{K}/voices.bin", tokens=f"{K}/tokens.txt", data_dir=f"{K}/espeak-ng-data",
    dict_dir=f"{K}/dict", lexicon=f"{K}/lexicon-digipae.txt,{K}/lexicon-us-en.txt,{K}/lexicon-zh.txt"), num_threads=4)))
rec = s.OfflineRecognizer.from_transducer(encoder=f"{M}/encoder.int8.onnx", decoder=f"{M}/decoder.int8.onnx",
    joiner=f"{M}/joiner.int8.onnx", tokens=f"{M}/tokens.txt", model_type="nemo_transducer", num_threads=4)
LINES = [
  ("intro", "Meet Digipay."),
  ("s1", "Your government-verified ID, always with you."),
  ("s2", "Scan any QR code, confirm with Face ID, and you're done. Zero hidden fees."),
  ("s3", "Upload a document once. It's verified, encrypted, and ready whenever you need it."),
  ("s4", "Prove you're over twenty-one, without revealing your birthday. Share the proof, never the document."),
  ("s5", "Every payment, in plain sight. Search, filter and export in seconds."),
  ("s6", "Your balance, rewards and linked accounts, all in one wallet."),
  ("s7", "Face ID and two-fifty-six-bit encryption, fully on your device."),
  ("s8", "And you stay in control of your access, devices and privacy."),
  ("outro", "Digipay. Your identity. Your money. One secure app."),
]
norm = lambda t: re.sub(r"[^a-z0-9 ]", "", t.lower().replace("-", " ")).split()
out = []
for name, text in LINES:
    best = None
    for attempt in range(4):
        a = tts.generate(text, sid=3, speed=1.0)
        x = np.array(a.samples, np.float32)
        idx = np.flatnonzero(np.abs(x) > 0.01); x = x[max(0, idx[0] - 720): idx[-1] + 1920]
        st = rec.create_stream(); st.accept_waveform(a.sample_rate, x); rec.decode_stream(st)
        heard = st.result.text
        want, got = norm(text), norm(heard)
        miss = [w for w in want if w not in got and w not in ("digipay", "twenty", "one", "two", "fifty", "six", "bit", "id", "qr")]
        if best is None or len(miss) < best[0]: best = (len(miss), x, heard)
        if not miss: break
    n, x, heard = best
    sf.write(f"{name}.wav", x, 24000)
    out.append({"name": name, "spoken": text, "dur": round(len(x) / 24000, 3)})
    print(f"{name:5s} {len(x)/24000:5.2f}s miss={n} heard: {heard}")
json.dump(out, open("lines.json", "w"), indent=1)

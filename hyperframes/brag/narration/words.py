import json, sys, soundfile as sf, sherpa_onnx
M = sys.argv[1]
rec = sherpa_onnx.OfflineRecognizer.from_transducer(encoder=f"{M}/encoder.int8.onnx", decoder=f"{M}/decoder.int8.onnx",
    joiner=f"{M}/joiner.int8.onnx", tokens=f"{M}/tokens.txt", model_type="nemo_transducer", num_threads=4)
lines = json.load(open("lines.json"))
for m in lines:
    x, sr = sf.read(m["name"] + ".wav", dtype="float32")
    st = rec.create_stream(); st.accept_waveform(sr, x); rec.decode_stream(st)
    r = st.result; ws = []
    for tok, t in zip(r.tokens, r.timestamps):
        if tok.startswith(" ") or not ws: ws.append({"w": tok.strip(), "s": round(t, 3)})
        else: ws[-1]["w"] += tok
    m["asr"] = ws
    print(m["name"], " ".join(f"{w['w']}@{w['s']}" for w in ws))
json.dump(lines, open("lines.json", "w"), indent=1)

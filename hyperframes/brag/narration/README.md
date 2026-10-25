# Narration

Female voiceover (Kokoro `af_heart`, run via sherpa-onnx) synced to the visuals.

1. `tts.py <kokoro-dir>`: one WAV per line. `lexicon-digipae.txt` adds "Digipay" (how the brand is said) and "payouts", which aren't in the stock lexicon.
2. `words.py <parakeet-dir>`: word timestamps for each line (NVIDIA Parakeet ASR).
3. `build_vo.py`: places the lines, masters `assets/vo.wav` to -16 LUFS, and writes `timing.json` (caption words and the scene anchors that `index.html` uses to shift each visual beat onto the word that names it).

Models come from the sherpa-onnx GitHub releases (`tts-models/kokoro-multi-lang-v1_0`, `asr-models/sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8`).

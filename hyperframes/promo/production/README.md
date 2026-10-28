# Digipae app promo: production pipeline

The 8 App Store slides (`reference-slide1..8.png`) are rebuilt as vector UI in `templates/index.html.tmpl`, so they stay sharp at 1080p and every element can animate.

| Step | Script | Output |
|---|---|---|
| 1. Voice | `promo_tts.py <kokoro> <parakeet>` | one WAV per line, each take checked by ASR and redone if a word drops |
| 2. Word timing | `words.py <parakeet>` | word timestamps into `lines.json` |
| 3. Timeline | `promo_timing.py` | `timing.json`: scene starts, caption phrases, per-word beats (taps, pop-outs, counters) and SFX cues |
| 4. Sound | `promo_audio.py timing.json <vo-dir> assets/mix.wav` | synthesized 100 BPM score + SFX + ducked narration, -16 LUFS |
| 5. Build | `python3 build.py production/timing.json` | `index.html` |
| 6. Render | `npx hyperframes render -o promo.mp4` | 1920x1080, 30fps |

Voice: Kokoro `af_heart`. `lexicon-digipae.txt` adds words missing from Kokoro's dictionary (Digipay, payouts, verified, encrypted, rewards, devices, QR, ID).
Models: sherpa-onnx GitHub releases (`tts-models/kokoro-multi-lang-v1_0`, `asr-models/sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8`).

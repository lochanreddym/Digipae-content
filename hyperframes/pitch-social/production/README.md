# DigiPae pitch videos: production notes

Two cuts are built from the investor deck (`pitch-deck/`) and the screen recording of the real app (Drive file `1fv6EArtMg-gSb2PNIpgZkY1fmGs_nrTn`).

| Output | Format | How it's built |
|---|---|---|
| `out/digipae-pitch-social.mp4` | 1080×1920, 71s, -14 LUFS | HyperFrames composition (`templates/index.html.tmpl` → `build.py` → `render`) |
| `out/digipae-pitch-deck-16x9.mp4` | 1920×1080, 2m38s, -14 LUFS | `deck-16x9/dv_build.py` (ffmpeg: deck slides, the same synced app section, end card, burned captions) |

The MP4s are gitignored. Rebuild them with the steps below.

## How the sync works
1. `pv_tts.py`: Kokoro voices each line in `script.json` (af_heart, `lexicon-digipae.txt`). Parakeet ASR checks every take, and any take with a dropped word is retried.
2. `words.py`: word timestamps go into `lines.json`.
3. `pv_timing.py`: the recording is split at its real screen changes (login, code, consent, PIN, home, documents, Government IDs, the "coming soon" modal, back home). Each segment is retimed (0.9×–3×, with a held last frame where needed) so it lasts exactly as long as its line. That puts every step on screen while it is being described.
4. `pv_cut.py`: cuts `assets/demo.mp4` from the recording, one segment at a time to stay within memory limits.
5. `pv_audio.py`: synthesized score, SFX, VO ducking, and two-pass loudnorm to -14 LUFS.

## Claims guardrails
- "Plaid for government" is an analogy; both end cards say "not affiliated with Plaid".
- The app is labelled a product preview. Document auto-retrieval is described as "coming soon", matching the app's own modal.
- The only statistic is the KFF ≈2-in-3 procedural share, with its source on screen. The 16:9 cut also uses the deck's sourced figures.
- The 16:9 cut skips the slides that still carry "To confirm" placeholders for traction, team, pricing and the ask (8, 11, 12, 13).

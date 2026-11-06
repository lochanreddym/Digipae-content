#!/bin/bash
# Smoke-tests every tool in the video toolchain with a real render/transcode/download.
set -uo pipefail
cd "$(dirname "$0")/.."
OUT=$(mktemp -d)
trap 'rm -rf "$OUT"; [ -n "${SRV:-}" ] && kill "$SRV" 2>/dev/null' EXIT
fail=0
ok()  { echo "  ✅ $1"; }
bad() { echo "  ‼️  $1"; fail=1; }

echo "FFmpeg"
if ffmpeg -v error -f lavfi -i testsrc2=size=320x240:rate=30:duration=1 -f lavfi -i sine=d=1 \
     -c:v libx264 -c:a aac -shortest "$OUT/ff.mp4" && ffprobe -v error "$OUT/ff.mp4"; then
  ok "$(ffmpeg -version | head -1 | cut -d' ' -f1-3) encodes H.264/AAC"
else bad "ffmpeg encode failed"; fi

echo "Remotion"
if npx --no-install remotion render remotion/index.ts LogoReveal "$OUT/remotion.mp4" --scale=0.25 \
     --log=error >/dev/null 2>"$OUT/remotion.log" && [ -s "$OUT/remotion.mp4" ]; then
  ok "rendered LogoReveal ($(npx --no-install remotion versions 2>/dev/null | grep -m1 -oE '4\.[0-9.]+'))"
else bad "remotion render failed: $(tail -3 "$OUT/remotion.log")"; fi

echo "HyperFrames"
if (cd hyperframes/logo-test && npx --no-install hyperframes lint . >/dev/null \
     && npx --no-install hyperframes render -o "$OUT/hf.mp4" >"$OUT/hf.log" 2>&1) && [ -s "$OUT/hf.mp4" ]; then
  ok "linted and rendered hyperframes/logo-test ($(npx --no-install hyperframes --version))"
else bad "hyperframes render failed: $(tail -3 "$OUT/hf.log")"; fi

echo "whisper.cpp"
MODEL="${WHISPER_MODEL_PATH:-$HOME/.cache/hyperframes/whisper/models/ggml-base.en.bin}"
JFK="$HOME/.local/src/whisper.cpp/samples/jfk.wav"
if ! command -v whisper-cli >/dev/null; then bad "whisper-cli not on PATH"
elif [ ! -s "$MODEL" ]; then bad "whisper-cli built, but no model at $MODEL (allow huggingface.co in Network access)"
elif whisper-cli -m "$MODEL" -f "$JFK" -nt -np 2>/dev/null | grep -qi "ask not what your country"; then
  ok "transcribed the JFK sample correctly"
else bad "whisper-cli transcription failed"; fi

echo "yt-dlp"
mkdir -p "$OUT/srv" && cp "$OUT/ff.mp4" "$OUT/srv/clip.mp4" 2>/dev/null
python3 -m http.server 8799 --bind 127.0.0.1 --directory "$OUT/srv" >/dev/null 2>&1 & SRV=$!
sleep 1
if yt-dlp -q --no-progress -o "$OUT/dl.%(ext)s" http://127.0.0.1:8799/clip.mp4 && cmp -s "$OUT/srv/clip.mp4" "$OUT/dl.mp4"; then
  ok "yt-dlp $(yt-dlp --version) downloaded a test video byte-for-byte"
else bad "yt-dlp download failed"; fi

exit $fail

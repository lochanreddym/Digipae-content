#!/bin/bash
# Sets up the video-editing toolchain for Claude Code cloud sessions:
# FFmpeg, Remotion, HyperFrames, whisper.cpp and yt-dlp.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "$CLAUDE_PROJECT_DIR"
log() { echo "[session-start] $*" >&2; }

WHISPER_REF=231638a0717b7822784297e5980965ffcec05810
WHISPER_SRC="$HOME/.local/src/whisper.cpp"
WHISPER_MODELS="$HOME/.cache/hyperframes/whisper/models"
WHISPER_MODEL="${WHISPER_MODEL:-base.en}"

# FFmpeg
if ! command -v ffmpeg >/dev/null || ! command -v ffprobe >/dev/null; then
  log "installing ffmpeg"
  apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq ffmpeg
fi

# Remotion + HyperFrames (npm)
log "installing npm packages"
npm install --no-audit --no-fund --loglevel=error

# Remotion renders with the preinstalled headless Chrome; its own download host is not reachable.
HEADLESS=$(ls -d /opt/pw-browsers/chromium_headless_shell-*/*/chrome-headless-shell 2>/dev/null | head -1 || true)
if [ -n "$HEADLESS" ] && [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  echo "export REMOTION_BROWSER_EXECUTABLE=\"$HEADLESS\"" >> "$CLAUDE_ENV_FILE"
fi

# HyperFrames downloads its own pinned Chrome into ~/.cache/puppeteer
log "ensuring HyperFrames browser"
npx --no-install hyperframes browser ensure >/dev/null || log "WARNING: hyperframes browser ensure failed"

# yt-dlp (kept current: site extractors break often)
log "installing yt-dlp"
pip install -q -U "yt-dlp[default]" 2>&1 | grep -v "Running pip as the 'root' user" >&2 || true

# whisper.cpp, built from source and pinned
if ! command -v whisper-cli >/dev/null; then
  log "building whisper.cpp"
  if [ ! -d "$WHISPER_SRC/.git" ]; then
    git clone -q https://github.com/ggml-org/whisper.cpp "$WHISPER_SRC"
  fi
  git -C "$WHISPER_SRC" fetch -q --depth 1 origin "$WHISPER_REF"
  git -C "$WHISPER_SRC" checkout -q "$WHISPER_REF"
  cmake -S "$WHISPER_SRC" -B "$WHISPER_SRC/build" -DCMAKE_BUILD_TYPE=Release \
    -DGGML_NATIVE=OFF -DBUILD_SHARED_LIBS=OFF -DWHISPER_BUILD_TESTS=OFF >/dev/null
  cmake --build "$WHISPER_SRC/build" -j"$(nproc)" --target whisper-cli >/dev/null
  ln -sf "$WHISPER_SRC/build/bin/whisper-cli" /usr/local/bin/whisper-cli
fi

# Whisper model weights live on Hugging Face; the network policy must allow huggingface.co.
mkdir -p "$WHISPER_MODELS"
if [ ! -s "$WHISPER_MODELS/ggml-$WHISPER_MODEL.bin" ]; then
  log "downloading whisper model $WHISPER_MODEL"
  if ! curl -fsSL --max-time 600 -o "$WHISPER_MODELS/ggml-$WHISPER_MODEL.bin.part" \
      "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-$WHISPER_MODEL.bin"; then
    rm -f "$WHISPER_MODELS/ggml-$WHISPER_MODEL.bin.part"
    log "WARNING: could not download the whisper model (is huggingface.co allowed in Network access?)"
  else
    mv "$WHISPER_MODELS/ggml-$WHISPER_MODEL.bin.part" "$WHISPER_MODELS/ggml-$WHISPER_MODEL.bin"
  fi
fi
if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  echo "export WHISPER_MODEL_PATH=\"$WHISPER_MODELS/ggml-$WHISPER_MODEL.bin\"" >> "$CLAUDE_ENV_FILE"
fi

log "done"

# Digipae-content

## Video toolchain

Cloud sessions install everything automatically via `.claude/hooks/session-start.sh`:

| Tool | Use | Where |
|---|---|---|
| FFmpeg | cut, join, grade, mix, convert | system package |
| Remotion | React video compositions | `remotion/` (`npm run remotion:render -- LogoReveal out/x.mp4`) |
| HyperFrames | HTML + GSAP motion graphics | `hyperframes/` (`cd hyperframes/logo-test && npx hyperframes render -o out.mp4`) |
| whisper.cpp | speech-to-text / captions | `whisper-cli`, models in `~/.cache/hyperframes/whisper/models` |
| yt-dlp | download reference videos | `yt-dlp <url>` |

Run `npm run check-tools` to smoke-test all five.

Network access for the cloud environment must allow `huggingface.co` (whisper model weights) and any site you want yt-dlp to download from (e.g. `youtube.com`, `googlevideo.com`).

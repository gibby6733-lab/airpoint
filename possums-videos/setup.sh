#!/usr/bin/env bash
# One-time setup: Python TTS deps + Kokoro voice model (downloaded, not committed).
set -euo pipefail
cd "$(dirname "$0")"
pip install -q kokoro-onnx soundfile numpy
mkdir -p tts
[ -f tts/kokoro.onnx ] || curl -sSL -o tts/kokoro.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.int8.onnx
[ -f tts/voices.bin ] || curl -sSL -o tts/voices.bin https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
command -v ffmpeg >/dev/null || echo "WARNING: ffmpeg not found"
node -e "require('playwright')" 2>/dev/null || echo "WARNING: playwright not installed (npm i playwright && npx playwright install chromium)"
echo "setup done"

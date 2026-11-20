#!/usr/bin/env bash
# usage: mafia/make_story.sh <story_dir>   (images/, narration.txt or narration.<audio>, optional script.txt/config.json)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; ROOT="$HERE/.."
D="$(cd "$1" && pwd)"
cp "$HERE/story.html" "$D/episode.html"
python3 "$HERE/build_story.py" "$D" "$ROOT/tts"
node "$ROOT/render.js" "$D"
ffprobe -v error -select_streams v:0 -show_entries stream=width,height -show_entries format=duration -of csv=p=0 "$D/episode.mp4"

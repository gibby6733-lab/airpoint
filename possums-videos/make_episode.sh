#!/usr/bin/env bash
# usage: ./make_episode.sh episodes/day01   -> writes episodes/day01/episode.mp4
set -euo pipefail
cd "$(dirname "$0")"
EP="${1:?episode dir}"
python3 build_audio.py "$EP" tts
node render.js "$EP"
ffprobe -v error -show_entries format=duration -of csv=p=0 "$EP/episode.mp4"

#!/bin/bash
# usage: ./render_parallel.sh <episode_dir> [workers=4]   -> <episode_dir>/episode.mp4 (video rendered in chunks, then joined + audio)
set -e
DIR=$1; N=${2:-4}; cd "$(dirname "$0")"
DUR=$(python3 -c "import json;print(json.load(open('$DIR/timeline.json'))['duration'])")
TOTAL=$(python3 -c "import math;print(math.ceil($DUR*30))")
TMP="$DIR/_parts"; rm -rf "$TMP"; mkdir -p "$TMP"; : > "$TMP/list.txt"
for i in $(seq 0 $((N-1))); do
  A=$((TOTAL*i/N)); Z=$((TOTAL*(i+1)/N))
  node render_part.js "$DIR" $A $Z "$TMP/p$i.mp4" &
  echo "file 'p$i.mp4'" >> "$TMP/list.txt"
done
wait
VW=$(python3 -c "import json;print(json.load(open('$DIR/timeline.json')).get('width',1080))"); VH=$(python3 -c "import json;print(json.load(open('$DIR/timeline.json')).get('height',1920))")
ASP=$([ "$VW" -gt "$VH" ] && echo 16:9 || echo 9:16)
ffmpeg -y -loglevel error -f concat -safe 0 -i "$TMP/list.txt" -i "$DIR/audio.wav" -c:v copy -aspect $ASP \
  -af loudnorm=I=-14:TP=-1.5:LRA=11 -c:a aac -b:a 192k -ar 48000 -shortest -movflags +faststart "$DIR/episode.mp4"
rm -rf "$TMP"; echo "wrote $DIR/episode.mp4"

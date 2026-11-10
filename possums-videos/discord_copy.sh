#!/usr/bin/env bash
# usage: ./discord_copy.sh in.mp4 out.mp4  -> re-encodes to fit Discord's 10 MB bot upload limit (target ~9.3 MB)
set -euo pipefail
IN="$1"; OUT="$2"; TARGET_KB=$((93 * 1024 / 10))
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$IN")
VK=$(python3 -c "print(int($TARGET_KB*8/$DUR - 128))")
TMP=$(mktemp -d)
ffmpeg -loglevel error -y -i "$IN" -c:v libx264 -preset slow -tune animation -b:v ${VK}k -pass 1 -passlogfile "$TMP/p" -an -f mp4 /dev/null
ffmpeg -loglevel error -y -i "$IN" -c:v libx264 -preset slow -tune animation -b:v ${VK}k -pass 2 -passlogfile "$TMP/p" \
  -vf "scale=1080:1920,setsar=1" -aspect 9:16 -c:a aac -b:a 128k -movflags +faststart "$OUT"
rm -rf "$TMP"; ls -la "$OUT" | awk '{printf "%.1f MB\n", $5/1048576}'

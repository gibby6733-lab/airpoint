#!/bin/bash
# Join partA + intro + partB1..4 into one 60 fps episode. Episode parts are silent; the intro keeps its audio.
set -e
cd "$(dirname "$0")/.."
R=episode/render
OUT=${1:-$R/MEDIAN_S01E01_NothingSells_picturelock.mp4}
for p in partA partB1 partB2 partB3 partB4; do
  ffmpeg -y -loglevel error -i $R/$p.mp4 -f lavfi -i anullsrc=r=48000:cl=stereo -shortest -c:v copy -c:a aac -b:a 192k $R/${p}_a.mp4
done
ffmpeg -y -loglevel error -i intro/MEDIAN_INTRO_FINAL.mp4 -c:v libx264 -profile:v high -preset medium -crf 18 -pix_fmt yuv420p -r 60 -c:a aac -b:a 192k -ar 48000 -ac 2 $R/intro_a.mp4
ffmpeg -y -loglevel error -i $R/partA_a.mp4 -i $R/intro_a.mp4 -i $R/partB1_a.mp4 -i $R/partB2_a.mp4 -i $R/partB3_a.mp4 -i $R/partB4_a.mp4 \
 -filter_complex "[0:v][0:a][1:v][1:a][2:v][2:a][3:v][3:a][4:v][4:a][5:v][5:a]concat=n=6:v=1:a=1[v][a]" \
 -map "[v]" -map "[a]" -c:v libx264 -profile:v high -preset medium -crf 19 -pix_fmt yuv420p -r 60 -c:a aac -b:a 192k -movflags +faststart "$OUT"
ffprobe -v error -select_streams v -show_entries stream=r_frame_rate,nb_frames -show_entries format=duration,size -of default=nw=1 "$OUT"

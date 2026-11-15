#!/bin/bash
cd /home/user/airpoint/median-series
cat episode/render/jobs.txt | xargs -P 4 -L 1 bash -c 'node tools/render-episode.js $0 $1 $2 60 > ${2%.mp4}.log 2>&1'
echo ALLDONE > episode/render/done.flag

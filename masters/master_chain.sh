#!/bin/bash
# usage: master.sh <in> <out> <pre_limiter_gain_dB>
IN="$1"; OUT="$2"; G="$3"
ffmpeg -y -hide_banner -nostats -loglevel error -i "$IN" -filter_complex "
[0:a]highpass=f=28:poles=2,
 equalizer=f=55:t=q:w=0.9:g=1.5,
 equalizer=f=320:t=q:w=1.1:g=-2.5,
 equalizer=f=650:t=q:w=1.4:g=-1,
 equalizer=f=3000:t=q:w=0.8:g=3,
 equalizer=f=5000:t=q:w=1.2:g=1,
 highshelf=f=13000:g=-1.2,
 deesser=i=0.35:m=0.5:f=0.55:s=o,
 acrossover=split=130:order=4th[lo][hi];
[lo]pan=stereo|c0=0.5*c0+0.5*c1|c1=0.5*c0+0.5*c1[lomono];
[hi]stereotools=slev=1.55[hiwide];
[lomono][hiwide]amix=inputs=2:normalize=0,asplit[dry][vsrc];
[vsrc]pan=mono|c0=0.5*c0+0.5*c1,highpass=f=250,lowpass=f=6500,equalizer=f=3000:t=q:w=1:g=2,adelay=17,asplit[va][vb];
[vb]volume=-1[vbn];
[va]volume=0.38[vap];
[vbn]volume=0.38,pan=mono|c0=-1*c0[vbneg];
[vap][vbneg]join=inputs=2:channel_layout=stereo[vside];
[dry][vside]amix=inputs=2:normalize=0,
 acompressor=threshold=-14dB:ratio=2:attack=30:release=200:knee=6:makeup=1.5dB,
 volume=${G}dB,
 asoftclip=type=tanh:threshold=0.95:output=1:oversample=4,
 alimiter=limit=0.84:attack=3:release=60:level=0:asc=1,
 aresample=44100,
 alimiter=limit=0.88:attack=1:release=40:level=0
" -c:a pcm_s24le "$OUT"

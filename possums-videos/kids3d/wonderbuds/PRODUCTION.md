# WonderBuds production pipeline

Permanent assets (never rebuild per episode): `cast.js` (5 characters), `bible.json` + `BIBLE.md` (designs, voices, speech habits),
`village.js` (WonderBuds Village + collision footprints), `intro/` (show intro, plays before every episode), `../voice.py`, `../sound.py`.

## Quality gates — a video is NOT rendered or delivered until all pass
1. **Collision QC** — `node kids3d/render.js <episode_dir> --qc` must print `PASS`.
   It checks every character 15×/second against every prop footprint in the village (benches, slides, lamps, trees, houses…)
   and against each other. Any new prop added to a location must get a footprint in `village.js` (`ob({...})`).
   Each episode page must expose `window.OBST` and `window.qcProbe(t)` (see `intro/episode.html`).
2. Still-frame review of every scene (faces visible, nothing cut off, nobody facing away from camera while talking).
3. Audio: every line uses the speaker's permanent voice profile; dialogue louder than music.

## Rendering
- CPU (this cloud machine, no graphics card): ~1 hour per minute of 1080p video.
- GPU (a PC with a graphics card): `node kids3d/render.js <episode_dir> --gpu` — uses the real graphics card, many times faster.

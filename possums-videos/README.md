# Mudville Possums — daily video generator

Original animated series: "The worst football team in America." Every like on TikTok + Instagram = +$1 to the team fund; the most-liked comment (across both) picks the next upgrade.

## Format rules
- 9:16, 1080x1920, 30 fps, 60–70 seconds
- Voice: Kokoro `am_michael`, speed ~1.15
- Mix: music ≈ -25 dB and SFX ≈ -15 dB relative to voice; final loudness -14 LUFS
- Ending teases **tomorrow's** game; CTA says likes on TikTok + Instagram count, most-liked comment wins
- Arena stays run-down until fans pay for upgrades (see `state.json`)

## Daily workflow
1. User sends: likes on TikTok + Instagram, and the winning comment.
2. Update `state.json` (fund, upgrades, record, history).
3. `cp -r episodes/dayNN episodes/dayNN+1`, edit `script.json` lines (scene + text + sfx) and add/modify scenes in `episode.html` (`SCENES` object; `drawStadium` for arena upgrades; HUD day/fund in `hud()`/`fundAt()`).
4. `./make_episode.sh episodes/dayNN+1` → check duration is 60–70 s, adjust text if not.

## Files
- `build_audio.py` — TTS voiceover, original chiptune music, synthesized SFX, mix, `timeline.json`
- `render.js` — renders `episode.html` frame by frame with Playwright and muxes with ffmpeg
- `profile.js` — renders profile pictures into `assets/`
- `setup.sh` — installs TTS deps and downloads the voice model

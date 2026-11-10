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

## Discord delivery
One channel per sport (football / soccer / baseball). Each day: video + caption + hashtags.
- `channels.json` — channel ids (Discord: Developer Mode → right-click channel → Copy Channel ID)
- `episodes/dayNN/caption.txt` — caption + hashtags (≤ 2000 chars)
- `./discord_copy.sh episodes/dayNN/episode.mp4 episodes/dayNN/discord.mp4` — fits the 10 MB bot upload limit
- `python3 post_discord.py football episodes/dayNN` (add `--dry-run` to preview)
- Bot token is never stored in the repo: it is a network secret on the cloud environment
  (host `discord.com`, header `Authorization`, value `Bot <token>`). Bot needs Send Messages + Attach Files.

## Daily input from the user (source of truth)
Each day the user sends, per sport:
1. Total likes on the previous post (TikTok + Instagram) → add $1 per like to `fund_dollars` in `state.json`.
2. The most-liked comment (across both platforms) → that's the upgrade/action for the next episode.
   - Affordable: buy it (subtract price), redraw that part of the arena, show the purchase on screen.
   - Not affordable: "saving up" bit; buy the cheapest version or put money toward it.
   - Non-upgrade comment (e.g. "can I be a hot dog seller"): work it in as a story beat / new character.
Log both in `state.json` → `history`.

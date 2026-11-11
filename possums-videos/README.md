# Mudville Possums — daily video generator

Original animated series: "The worst football team in America." TikTok only. Every like = +$1 to the team fund; the most-liked comment picks the next upgrade.

## Format rules
- 9:16, 1080x1920, 30 fps, 60–70 seconds
- Voice: Kokoro `am_michael`, speed ~1.15
- Mix: music ≈ -25 dB and SFX ≈ -15 dB relative to voice; final loudness -14 LUFS
- Ending teases **tomorrow's** game; CTA says every like on this video counts, most-liked comment wins (TikTok only; never mention Instagram)
- Football hashtags (exactly these, nothing else): #football #footballfunny #animation #Mudvillepossums
- Captions: 100 characters MAX including hashtags and emojis (count emojis as 2). Check with python before posting.
- Captions: only common emojis that show on iPhone (e.g. 🏈 💵 👇 🏟️ 🌱 🥅 📟 🚽 😬 😂 🔥 ❤️); never text codes like [Red heart].
  Always paste the caption in chat too, ready to copy.
- Arena stays run-down until fans pay for upgrades (see `state.json`)

## Daily workflow
1. User sends: TikTok likes, and the winning TikTok comment.
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
1. Likes on the previous post: TikTok + Instagram (if posted there) → add $1 per like to `fund_dollars` in `state.json`.
2. The most-liked TikTok comment → that's the upgrade/action for the next episode.
   - Affordable: buy it (subtract price), redraw that part of the arena, show the purchase on screen.
   - Not affordable: "saving up" bit; buy the cheapest version or put money toward it.
   - Non-upgrade comment (e.g. "can I be a hot dog seller"): work it in as a story beat / new character.
Log both in `state.json` → `history`.

## Multiple sports (series/)
- `series/core.js` — shared engine (characters, HUD, captions, roster cards, versus, standings, upgrade shop, frame loop).
  Each `series/<sport>/dayNN/episode.html` loads it and defines `TEAM`, `drawStadium()` and the game scenes.
- Football (Mudville Possums) still lives in `episodes/` (standalone, predates the core).
- Soccer: Bramblewood Pigeons — `series/soccer/` (parking-lot pitch, shopping-cart goals)
- Baseball: Crabapple Raccoons — `series/baseball/` (pizza-box bases, mattress backstop, cornfield outfield)
- Per-sport `state.json` and `profile.png` live in `series/<sport>/`.
- Build: `./make_episode.sh series/soccer/day01` · Profile pic: `node series/profile.js series/soccer/day01 out.png`

## Posting schedule
- Day 1 posted to TikTok on 2026-11-11. Next real episode = Day 2, built from Day 1's TikTok likes + comments.
- `episodes/demo_day02/` is a test run only (posted to Discord during the demo, not to TikTok). Don't treat it as canon.

## Mafia story (separate series)
`mafia/` — images + narration + time-marked script → animated 9:16 story with paper-cut transitions, SFX and tense
music. Daily material comes from the #mafia-story Discord channel. See `.claude/skills/mafia-story/SKILL.md`.

---
name: generate-day
description: Make the next daily Mudville Possums football episode. Asks for the winning TikTok comment and the like count, updates the team fund/upgrades, writes and renders the 60-70 s 9:16 video, and posts it to the #football-channel on Discord. Use when the user says "generate day N", "make tomorrow's video", or runs /generate-day.
argument-hint: "[likes] [\"top comment\"] [comment likes]"
---

# Generate the next Mudville Possums episode

Project: `possums-videos/` (read its `README.md` first — format rules live there). Football only.
Team memory: `possums-videos/state.json` (fund, record, upgrades, stadium, roster, history).
Last episode: the highest `possums-videos/episodes/dayNN/`. New day = `after_day + 1`.

## 1. Ask for the inputs (skip any the user already gave as arguments)
Use **AskUserQuestion** in ONE call with these questions:
- **Top comment** — "What was the most-liked comment on the Day N TikTok?" Options: the shop items that
  aren't bought yet from `state.json` → `upgrade_prices` (e.g. "Gear", "Stands", "Field", "Goal posts"). The
  user picks one or types the exact comment in "Other".
- **Video likes** — "How many likes did the Day N TikTok get? (type the exact number in Other)". Options:
  "Under 100", "100–1,000" are only hints; if the user picks one instead of typing a number, ask for the
  exact number in chat before continuing. Every like = $1, so the number must be exact.
- **Comment likes** — "How many likes did that comment get?" Options: "Under 10", "10–100" (+ Other).
  Only used on screen ("312 likes"); a range is fine.
Do not start building until you have: exact video likes + the comment text.

## 2. Update the team (`state.json`)
- `fund_dollars += likes`. Log `{day, likes, winning_comment, comment_likes}` in `history`.
- Comment is a shop upgrade and affordable → buy it (subtract price), update `stadium`/`upgrades_owned`.
  Not affordable → "saving up" bit; buy a cheap/funny version or put the money aside.
  Not an upgrade (e.g. "can I be a hot dog seller") → work it in as a story beat / new character; keep the money.
- Pick tomorrow's opponent (invent a new team in the same style) and the game result (Possums usually lose,
  occasionally a lucky win). Record it.

## 3. Write the episode
- `cp -r episodes/day<prev> episodes/day<new>`; delete its mp4/wav/timeline/stills.
- Edit `script.json` lines. Keep this beat order, ~16-19 lines:
  Day intro → fund update ("You gave us N likes = $N") → show the winning comment on screen → buy/build the
  upgrade (show it in the arena) → short game: 3-4 funny plays, scoreboard → standings → "Tomorrow, <team>" tease
  → CTA ("Every like on this video is a dollar. The most liked comment picks our upgrade…" + remaining shop items).
- TikTok only: never mention Instagram. Narration says "this video", not platform names.
- Edit `episode.html`: day number in `hud()`/stamps ("DAY N"), fund logic `fundAt()`, opponent logos/colors,
  `drawStadium()` to show bought upgrades (the arena only improves where fans paid), new scenes as needed,
  shop items/prices in the `cta` scene. Keep the run-down look everywhere not upgraded.
- `caption.txt`: Day N hook line, "Every like = +$1 for the team 💵", "Most-liked comment picks the upgrade 👇",
  remaining upgrades, tomorrow's opponent, then EXACTLY these hashtags and no others:
  `#football #footballfunny #animation #Mudvillepossums`

## 4. Build and check
- `cd possums-videos && ./setup.sh` if `tts/` is missing.
- `python3 build_audio.py episodes/day<new> tts` → duration must be **60-70 s**; trim/extend lines and rebuild if not.
  Levels line should show music ≈ -25 dB, sfx ≈ -15 dB vs voice.
- Render stills at 75% of each line (`node render.js <ep> --stills t1,t2,...`), look at them, fix overlaps,
  cut-off text, or anything off-model.
- `node render.js episodes/day<new>` → verify 1080x1920, 9:16, duration.
- `./discord_copy.sh episodes/day<new>/episode.mp4 episodes/day<new>/discord.mp4` (< 10 MB).

## 5. Deliver
- `python3 post_discord.py football episodes/day<new>` (posts video + caption to #football-channel).
  If Discord returns 401, the bot token on the cloud environment needs replacing — tell the user; do not retry blindly.
- Copy the full-quality mp4 to the scratchpad and send it with SendUserFile (best quality for TikTok upload).
- Commit `possums-videos/` (not mp4/wav — gitignored) and push to the working branch.
- Reply briefly: new fund total, what was bought, the game result, video length, and that it's posted to Discord.

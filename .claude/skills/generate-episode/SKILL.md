---
name: generate-episode
description: Make the next REALITY RELOADED episode (Jayden trapped in a VR game universe; THE PLAYERS vote A or B). Use when the user says "generate episode N", "next reloaded episode", or sends the A/B vote result for REALITY RELOADED.
---

# REALITY RELOADED — next episode

Project: `possums-videos/series/reloaded/`. Story bible + every past vote: `series.json` (read it first). Engine:
`engine.html` (2D flat cartoon, 9:16, 60 fps, Instagram/TikTok-safe HUD). Last episode = highest `epNN/`.

## 1. Get the REAL vote result (never invent it)
- The previous episode ended with exactly two options (A / B). Use the real result: from the user, or from the
  📊 vote count the hourly routine posts in #reloaded comment-replies (`python3 discord_say.py reloaded_replies ...`).
- If no result was given, ask: "What won, A or B? (and the % if you have it)". Do NOT make the episode until you have it.
- Tie → the next episode opens with a sudden-decision moment (THE SYSTEM forces a coin flip) or ask for a tiebreaker.
- Save it: `series.json` → history[-1].result = {"winner": "A", "pct": 72} (pct may be null).

## 2. Write the episode (`epNN/script.json`, copy the previous one as a template)
- Speakers: `"j"` = Jayden (am_puck 1.2), `"system"` = THE SYSTEM (bm_george 1.0, robot). Keep `speakers`, `fps: 60`, `crf: 16`.
- Structure (61-75 s total, must be OVER 1 minute for TikTok pay):
  1. HOOK in the first 1-2 s (danger/funny/shock line, e.g. Jayden mid-chase).
  2. LOBBY: THE SYSTEM announces the vote: "Option A received 72% of the votes." / "Most of you chose…" (real numbers only)
     and Jayden reacts ("WAIT. YOU GUYS PICKED THAT?").
  3. Play out the WINNING choice (consequences that matter), then the next quest or the next portal.
  4. TWIST (enemy, glitch, hidden objective, Player 002, rival).
  5. CLIFFHANGER + Jayden talks to THE PLAYERS (begs / blames / thanks them).
  6. `vote` scene with EXACTLY TWO options `a`, `b` (both interesting, neither obviously better), THE SYSTEM line
     "The Players decide. Comment A or B. You have twenty four hours."
- Games: use REAL game names (see `series.json` → world_ideas, worlds_rule), but draw everything in our own style: never copy
  official characters, skins, logos, UI art or maps. Show each game through its gameplay ideas.
  A game can last 2-4 episodes. Track inventory, abilities, completed games, open mysteries in `series.json` → state.
- Big reveal every 5-10 episodes (see mystery_plan). Never reset the story.
- Cinematic style (series.json → style): shots cut automatically every ~2 s; add first-person hand shots (scene `pov`, obj, reach),
  `rule` ("RULE #1: ..."), `day`, `time`, `timer` (seconds countdown, null hides it) like the reference reels.
- Scenes available: fall, bedroom, lobby (system=true shows the orb), sys (panel lines), portalgo (world, col, enter),
  island (drop, jx, bots, storm, p2, boss, blimp), pov (obj, reach), vote (a, b). Line fields: quest, world, hp, rule, day, time, timer, auto (false = no shot cuts), stamps
  [[text, word, x, y, size, color, rot]] (y ≥ 700 so the HUD stays clear). Add a new world scene to engine.html when
  the story enters a new game (same style: flat 2D, thick outlines), then copy engine.html to epNN/episode.html.

## 3. Build + check
`python3 build_audio.py series/reloaded/epNN tts` (61-75 s) → stills (`node render.js <dir> --stills ...`), check
overlaps/side crops → `./render_parallel.sh series/reloaded/epNN 4` (background, ~9 min) →
`./discord_copy.sh <dir>/episode.mp4 <dir>/discord.mp4` → `python3 viral_check.py <dir>` (fix ❌ when cheap).

## 4. Deliver
- Cover `thumbnail.png` (vote screen or the biggest moment + "EPISODE N" + hook), `title.txt`
  ("REALITY RELOADED Ep N: <title> 🎮 #gaming #animation #reallifegaming #choosewisely #fyp" style, < 100 chars),
  `caption.txt` (hook, "A: … / B: …", "Comment A or B 👇 24 hours", iPhone emojis only, hashtags
  `#gaming #animation #gamer #storytime #fyp`).
- `python3 post_discord.py reloaded series/reloaded/epNN`, SendUserFile the mp4, update `series.json` history
  (new entry with the vote options, result null), commit + push.

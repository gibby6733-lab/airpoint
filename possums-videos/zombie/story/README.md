# Zombie apocalypse story Shorts (YouTube Shorts + TikTok + Instagram) → #apocalypse-videos

Format (from the user): ONE survivor on screen. Each day = a short story, then ONE "would you rather" question at
the end. Say the two answers plainly ("Would you rather X? Or Y?") — never "A" / "B". The user posts the poll in the
comments; the winning answer decides the next day's story. Every other day a new character can be introduced and/or leave.
State: `state.json` (survivor, companions, history with poll winners).
Build: `python3 zombie/build_episode.py zombie/story/dayNN tts` (copy state.json into the day dir first),
`node zombie/short_series.js zombie/story/dayNN`, `./discord_copy.sh …`, `python3 post_discord.py apocalypse zombie/story/dayNN`.
Question screen: hud="wyr" with opt1/opt2 (+ countdown hold, then vote=True).
Captions: common iPhone emojis only, pasted in chat too.

## v2 format (from Day 1 remake)
- **Hook (0-5 s):** big on-screen line + voice ("Zombies won't kill you first. Dirty water will.").
- **Cole is smart:** ex-science teacher, explains *why*. Base: Bellwood Public Library (+ river, roof).
- **Every video is a lesson:** one real, accurate survival skill. LESSON tag on top, green STEP cards, recap on the poll screen.
- Still: one person on screen, story, ONE would-you-rather at the end, answers said plainly, user posts the poll.
- Build: `python3 dayNN/make_script.py` → `cp engine.html dayNN/episode.html` → `python3 ../build_episode.py zombie/story/dayNN tts`
  → `node render.js zombie/story/dayNN` → `./discord_copy.sh …` → `python3 post_discord.py apocalypse zombie/story/dayNN`.

## v3 "What If" style (current)
- Narrator talks to the viewer as **you** (`sp: narr`, speed 1.12). Day 2+ opens with the poll result ("Most of you said…").
- Hook = 3 big stakes cards (`cards: [{t, w, c, big: true}]`, `scene: stakes`).
- Every line gets 1-3 number cards (`cards`, `w` = word they pop on, `strike` crosses one out). Cards alternate punch-in zooms = fast cuts.
- Base = side cutaway (`scene: base`, `cam2: roof|up|f2|f1|base|all`, `you: [floor, x, pose, flip]`, props gutter/cans/diverter/dirt, `rain`, `doorShake`, `crack`, `jugs`, `fill0/fill1`).
- Lessons must be real, checkable facts. Still ONE would-you-rather at the end.

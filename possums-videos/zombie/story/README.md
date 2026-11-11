# Zombie apocalypse story Shorts (YouTube Shorts + TikTok + Instagram) → #apocalypse-videos

Format (from the user): ONE survivor on screen. Each day = a short story, then ONE "would you rather" question at
the end. Say the two answers plainly ("Would you rather X? Or Y?") — never "A" / "B". The user posts the poll in the
comments; the winning answer decides the next day's story. Every other day a new character can be introduced and/or leave.
State: `state.json` (survivor, companions, history with poll winners).
Build: `python3 zombie/build_episode.py zombie/story/dayNN tts` (copy state.json into the day dir first),
`node zombie/short_series.js zombie/story/dayNN`, `./discord_copy.sh …`, `python3 post_discord.py apocalypse zombie/story/dayNN`.
Question screen: hud="wyr" with opt1/opt2 (+ countdown hold, then vote=True).
Captions: common iPhone emojis only, pasted in chat too.

# "Would You Survive?" — YouTube Shorts (evergreen, one-off topics) → #would-you-survive

Each video: hook → setup with real facts → 3 A/B choices (question line + 2.6 s countdown) → reveal what really
happened ("A = YOU LIVE") → death/survivor toll → "comment your answers + next disaster". 60-70 s, 9:16.
Facts must be well documented; list them at the top of the topic's make_script.py.

Build: `python3 <topic>/make_script.py`, `python3 zombie/build_episode.py survive/<topic> tts`,
`cp survive/engine.html survive/<topic>/episode.html`, `node render.js survive/<topic>`,
`./discord_copy.sh …/episode.mp4 …/discord.mp4`, `python3 post_discord.py survive survive/<topic>`.
New topics usually need new scene drawings in engine.html (SC object).

- Captions: 100 characters MAX including hashtags and emojis (count emojis as 2). Check with python before posting.
Captions: common iPhone emojis only (never text codes like [Red heart]); paste the caption in chat too.
Hashtags: #shorts #wouldyousurvive + 2 topic tags.
Each video also gets `description.txt` for YouTube: hook, setting with real facts, the 3 choices, "what really
happened" answers, the toll, comment + next-disaster call to action, hashtags. Paste it in chat with the title.

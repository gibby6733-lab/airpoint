# Would You Rather: Zombie Apocalypse (YouTube Shorts + TikTok + Instagram) → #apocalypse-videos

Each video: hook → N questions ("Would you rather A? Or B?" + 2.6 s countdown over A/B cards with emoji icons) →
"Vote in the poll in the comments". The user posts the poll in the comments themselves; the video only asks.
Build: edit `<dir>/make_script.py` (Q list), `python3 zombie/build_episode.py <dir> tts`, `cp zombie/wyr/engine.html <dir>/episode.html`,
`node render.js <dir>`, `./discord_copy.sh …`, `python3 post_discord.py apocalypse <dir>`.
Captions: common iPhone emojis only, pasted in chat too.

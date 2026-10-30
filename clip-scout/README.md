# Clip Scout

Every day, Clip Scout scans top Twitch streamers, picks the 5 best clips from
the last 24 hours, and sends each one to you on Telegram as a video with a
hook, caption and hashtags ready to post.

## How it picks clips

1. **Streamers:** the 50 most-watched live streamers right now, plus everyone in
   `streamers.txt`.
2. **Clips:** each streamer's most-viewed clips from the last 24 hours.
3. **Ranking:** by views, with a mild boost for newer clips.
4. **Rules:** at most 2 clips per streamer; several clips of the same moment
   count as one; clips already sent (tracked in `seen_clips.json` for 14 days)
   are skipped.

## What you get on Telegram

Each clip arrives as its own message: the original horizontal (16:9) MP4,
uncropped and not re-encoded, with this text under it:

```
#1 · 🎮 KaiCenat · Just Chatting
👁 48,210 views · ⏱ 29s

🪝 Hook: Chat lost it when KaiCenat did this 💀

📝 Caption: he really said that on stream — KaiCenat playing Just Chatting

🏷 #twitch #twitchclips #Kaicenat #JustChatting #gaming #streamer #clips #fyp #viral

🔗 https://clips.twitch.tv/...
```

If a clip is over 50 MB (the Telegram bot upload limit), or the download
fails, you get the same text with the link instead, and a warning is logged.
Downloaded files are deleted after sending.

## Setup (one time, ~10 minutes)

1. **Twitch app:** at <https://dev.twitch.tv/console/apps>, register an app
   (OAuth redirect `http://localhost`, category "Other"). Copy the
   **Client ID** and create a **Client Secret**.
2. **Telegram bot:** message [@BotFather](https://t.me/BotFather), send
   `/newbot`, and copy the **bot token**. Send your new bot any message, then
   open `https://api.telegram.org/bot<TOKEN>/getUpdates` and copy
   `"chat":{"id": ...}`. That number is your **chat ID**.
3. **GitHub secrets:** in this repo, go to Settings → Secrets and variables →
   Actions, and add `TWITCH_CLIENT_ID`, `TWITCH_CLIENT_SECRET`,
   `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`.
4. **Merge to `main`.** GitHub only runs scheduled workflows from the default
   branch. After that, it runs daily at 15:17 UTC. To run it right away, use
   Actions → clip-scout → Run workflow.

## Running it yourself

```bash
pip install -r requirements.txt
export TWITCH_CLIENT_ID=... TWITCH_CLIENT_SECRET=...
export TELEGRAM_BOT_TOKEN=... TELEGRAM_CHAT_ID=...

python clip_scout.py --dry-run      # print the picks, send nothing
python clip_scout.py                # send the top 5 as videos
python clip_scout.py --no-download  # send links only
```

Other options: `--top`, `--per-streamer`, `--hours`, `--live-streamers`,
`--streamers-file`. See `python clip_scout.py --help`.

**ffmpeg may be needed.** Twitch clips are usually a single MP4 that yt-dlp
saves as-is, but install ffmpeg (`brew install ffmpeg` / `apt install ffmpeg`)
in case a clip needs remuxing. The GitHub workflow installs it for you.

Tests: `pip install pytest && python -m pytest tests`.

## Note on reposting

Clips belong to the streamers. Credit them (the streamer name is in every
caption), and check each platform's rules before reposting.

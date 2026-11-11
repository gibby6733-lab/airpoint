"""Post a day's video + caption to a sport's Discord channel.

usage: python3 post_discord.py <sport> <episode_dir> [--dry-run]

- channel ids live in channels.json: {"football": "123...", "soccer": "...", "baseball": "..."}
- caption comes from <episode_dir>/caption.txt
- video is <episode_dir>/discord.mp4 (made by discord_copy.sh, must be < 10 MB)
- the bot token is NOT stored here: the session's network proxy adds the
  Authorization header for discord.com, so a placeholder is sent from code.
"""
import json, os, sys, uuid, urllib.request, urllib.error

sport, ep = sys.argv[1], sys.argv[2]
dry = "--dry-run" in sys.argv
here = os.path.dirname(os.path.abspath(__file__))
channels = json.load(open(os.path.join(here, "channels.json")))
channel = channels.get(sport)
if not channel or not channel.isdigit():
    sys.exit(f"no channel id for {sport!r} in channels.json")

caption = open(os.path.join(ep, "caption.txt")).read().strip()
tp = os.path.join(ep, "title.txt")  # optional video title (e.g. YouTube Shorts title with hashtags)
if os.path.exists(tp):
    caption = f"🎬 **TITLE**\n{open(tp).read().strip()}\n\n📝 **CAPTION**\n{caption}"
if len(caption) > 2000:
    sys.exit(f"caption is {len(caption)} chars; Discord's limit is 2000")
video = os.path.join(ep, "discord.mp4")
size = os.path.getsize(video)
if size >= 10 * 1024 * 1024:
    sys.exit(f"{video} is {size / 1048576:.1f} MB; run discord_copy.sh first (limit 10 MB)")

fname = f"{sport}_{os.path.basename(os.path.normpath(ep))}.mp4"
payload = {"content": caption, "attachments": [{"id": 0, "filename": fname}]}
if dry:
    print(f"[dry run] would post {fname} ({size / 1048576:.1f} MB) to channel {channel}:\n{caption}")
    sys.exit(0)

b = uuid.uuid4().hex
body = b"".join([
    f"--{b}\r\nContent-Disposition: form-data; name=\"payload_json\"\r\nContent-Type: application/json\r\n\r\n".encode(),
    json.dumps(payload).encode(), b"\r\n",
    f"--{b}\r\nContent-Disposition: form-data; name=\"files[0]\"; filename=\"{fname}\"\r\nContent-Type: video/mp4\r\n\r\n".encode(),
    open(video, "rb").read(), f"\r\n--{b}--\r\n".encode(),
])
req = urllib.request.Request(
    f"https://discord.com/api/v10/channels/{channel}/messages", data=body, method="POST",
    headers={"Content-Type": f"multipart/form-data; boundary={b}",
             "Authorization": "Bot placeholder-replaced-by-proxy",
             "User-Agent": "DiscordBot (daily-video-poster, 1.0)"})
try:
    with urllib.request.urlopen(req, timeout=120) as r:
        msg = json.load(r)
        print(f"posted to {sport} channel (message id {msg['id']})")
except urllib.error.HTTPError as e:
    print(f"Discord error {e.code}: {e.read().decode()[:400]}")
    sys.exit(1)

"""Post comment replies to #comment-replies, ONE message per reply (copy-paste friendly).

usage: python3 discord_replies.py replies.json
replies.json: [{"user": "jaxsuiiii123", "comment": "Yo can I be the wide receiver", "reply": "\"Trust\" is all we got 😂"}, ...]
Each message's text is ONLY the reply (so Discord "Copy Text" copies just that); who it's for + their comment shows in
a small embed box under it (embeds aren't copied).
"""
import json, os, sys, time, urllib.request, urllib.error
here = os.path.dirname(os.path.abspath(__file__))
ch = json.load(open(os.path.join(here, "channels.json")))["replies"]
GUILD = "1569811326786605097"
H = {"Authorization": "Bot proxy-injected", "Content-Type": "application/json", "User-Agent": "DiscordBot (daily-video-poster, 1.0)"}
def post(body):
    for _ in range(6):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(f"https://discord.com/api/v10/channels/{ch}/messages", method="POST", data=json.dumps(body).encode(), headers=H), timeout=30))
        except urllib.error.HTTPError as e:
            if e.code == 429: time.sleep(json.loads(e.read()).get("retry_after", 1) + .3); continue
            raise
items = json.load(open(sys.argv[1]))
post({"content": f"⚡ **{len(items)} replies below.** Long-press a reply → Copy Text → paste it on that comment 👇"})
first = None
for i, it in enumerate(items, 1):
    c = it.get("comment", "")[:180]
    m = post({"content": it["reply"], "embeds": [{"description": f"#{i} • 💬 **@{it['user']}**: {c}", "color": 0x2E86C1}]})
    first = first or m["id"]
    time.sleep(1.1)  # stay under Discord's rate limit
# Discord opens at the bottom, so end with a jump link back to reply #1 (replies read top to bottom)
post({"content": f"⬆️ **Start at #1** → https://discord.com/channels/{GUILD}/{ch}/{first}  (then scroll down in order)"})
print("posted", len(items))

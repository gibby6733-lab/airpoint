"""Post comment replies to #comment-replies, ONE message per reply (copy-paste friendly).

usage: python3 discord_replies.py replies.json
replies.json: [{"user": "jaxsuiiii123", "comment": "Yo can I be the wide receiver", "reply": "\"Trust\" is all we got 😂"}, ...]
For each comment: a small grey label message (#n • @user: comment), then the reply alone in its own message
(so Discord "Copy Text" copies just the reply). Read top to bottom; ends with a jump link to #1.
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
post({"content": f"⚡ **{len(items)} replies.** Each grey line says who it's for, the reply is right UNDER it. Long-press the reply → Copy Text 👇"})
first = None
for i, it in enumerate(items, 1):
    c = it.get("comment", "")[:150].replace("\n", " ")
    m = post({"content": f"-# #{i} • @{it['user']}: {c}"})  # small grey label ABOVE the reply
    first = first or m["id"]
    time.sleep(.8)
    post({"content": it["reply"]})                          # reply alone, so Copy Text copies only this
    time.sleep(.8)  # stay under Discord's rate limit
# Discord opens at the bottom, so end with a jump link back to #1 (read top to bottom)
post({"content": f"⬆️ **Start at #1** → https://discord.com/channels/{GUILD}/{ch}/{first}  (then scroll down in order)"})
print("posted", len(items))

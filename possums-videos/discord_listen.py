"""Watch a Discord channel and print one line per new human message (for a Claude session's Monitor).

usage: python3 discord_listen.py <sport>      (channel id from channels.json)
Output lines:  MSG <message_id> <username>: <content>
If content comes back empty, the bot lacks the Message Content intent (Developer Portal -> Bot ->
Privileged Gateway Intents -> Message Content Intent) unless the message @mentions the bot.
"""
import json, os, sys, time, urllib.request, urllib.error

here = os.path.dirname(os.path.abspath(__file__))
channel = json.load(open(os.path.join(here, "channels.json")))[sys.argv[1]]
API = f"https://discord.com/api/v10/channels/{channel}/messages"
HDR = {"Authorization": "Bot proxy-injected", "User-Agent": "DiscordBot (daily-video-poster, 1.0)"}

def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=HDR), timeout=20) as r:
        return json.load(r)

last = get(API + "?limit=1")
last_id = last[0]["id"] if last else "0"
print(f"LISTENING channel={channel}", flush=True)
while True:
    try:
        msgs = get(f"{API}?after={last_id}&limit=50")
        for m in sorted(msgs, key=lambda m: int(m["id"])):
            last_id = m["id"]
            if m["author"].get("bot"):
                continue
            content = m["content"].replace("\n", " / ")
            if not content and not m.get("attachments"):
                content = "<empty: enable Message Content Intent or @mention the bot>"
            print(f"MSG {m['id']} {m['author']['username']}: {content}", flush=True)
    except urllib.error.HTTPError as e:
        print(f"ERROR http {e.code}", flush=True)
        if e.code in (401, 403):
            sys.exit(1)
    except Exception as e:  # network blips: keep watching
        print(f"WARN {type(e).__name__}", flush=True)
    time.sleep(4)

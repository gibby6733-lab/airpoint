"""usage: python3 discord_say.py <sport> "message text"   -> bot posts a text message in that sport's channel"""
import json, os, sys, urllib.request
here = os.path.dirname(os.path.abspath(__file__))
ch = json.load(open(os.path.join(here, "channels.json")))[sys.argv[1]]
req = urllib.request.Request(f"https://discord.com/api/v10/channels/{ch}/messages", method="POST",
    data=json.dumps({"content": sys.argv[2][:2000]}).encode(),
    headers={"Content-Type": "application/json", "Authorization": "Bot proxy-injected", "User-Agent": "DiscordBot (daily-video-poster, 1.0)"})
print("sent", json.load(urllib.request.urlopen(req, timeout=30))["id"])

"""usage: python3 discord_image.py <channel_key> <image.png> ["optional text"]   -> bot posts one image (e.g. a thumbnail)"""
import json, os, sys, uuid, urllib.request
here = os.path.dirname(os.path.abspath(__file__))
ch = json.load(open(os.path.join(here, "channels.json")))[sys.argv[1]]
img, text = sys.argv[2], (sys.argv[3] if len(sys.argv) > 3 else "")
name = os.path.basename(img); b = uuid.uuid4().hex
body = b"".join([f"--{b}\r\nContent-Disposition: form-data; name=\"payload_json\"\r\nContent-Type: application/json\r\n\r\n".encode(),
    json.dumps({"content": text, "attachments": [{"id": 0, "filename": name}]}).encode(), b"\r\n",
    f"--{b}\r\nContent-Disposition: form-data; name=\"files[0]\"; filename=\"{name}\"\r\nContent-Type: image/png\r\n\r\n".encode(),
    open(img, "rb").read(), f"\r\n--{b}--\r\n".encode()])
req = urllib.request.Request(f"https://discord.com/api/v10/channels/{ch}/messages", data=body, method="POST",
    headers={"Content-Type": f"multipart/form-data; boundary={b}", "Authorization": "Bot proxy-injected", "User-Agent": "DiscordBot (daily-video-poster, 1.0)"})
print("sent", json.load(urllib.request.urlopen(req, timeout=60))["id"])

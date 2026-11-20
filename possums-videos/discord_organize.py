import json, time, urllib.request, urllib.error, sys
G = "1569811326786605097"
API = "https://discord.com/api/v10"
HDR = {"Authorization": "Bot proxy-injected", "Content-Type": "application/json", "User-Agent": "DiscordBot (server-organizer, 1.0)", "X-Audit-Log-Reason": "Organize server layout"}
def call(method, path, body=None):
    for attempt in range(5):
        req = urllib.request.Request(API + path, method=method, headers=HDR, data=json.dumps(body).encode() if body is not None else None)
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                t = r.read(); return json.loads(t) if t else {}
        except urllib.error.HTTPError as e:
            msg = e.read().decode()
            if e.code == 429: time.sleep(json.loads(msg).get("retry_after", 1) + .2); continue
            raise SystemExit(f"{method} {path} -> {e.code} {msg[:300]}")
chans = call("GET", f"/guilds/{G}/channels")
by = {c["name"]: c for c in chans}
if "--check" in sys.argv:
    # harmless test: rename the voice category to its current name
    c = by["Voice Channels"]; call("PATCH", f"/channels/{c['id']}", {"name": c["name"]}); print("permission ok"); sys.exit()

def cat(name, pos, existing=None):
    if existing: return call("PATCH", f"/channels/{existing}", {"name": name, "position": pos})
    found = next((c for c in chans if c["type"] == 4 and c["name"] == name), None)
    if found: return call("PATCH", f"/channels/{found['id']}", {"position": pos})
    return call("POST", f"/guilds/{G}/channels", {"name": name, "type": 4, "position": pos})
start = cat("📌 START HERE", 0)
foot = cat("🏈 MUDVILLE POSSUMS", 1)
apoc = cat("🧟 APOCALYPSE", 2)
mafia = cat("🕵️ MAFIA STORIES", 3)
comm = cat("💬 COMMUNITY", 4, by["Text Channels"]["id"])
voice = cat("🔊 VOICE", 5, by["Voice Channels"]["id"])
def text(name, parent, pos, topic=None, existing=None):
    body = {"name": name, "parent_id": parent["id"], "position": pos}
    if topic: body["topic"] = topic
    if existing: return call("PATCH", f"/channels/{existing}", body)
    found = next((c for c in chans if c["type"] == 0 and c["name"] == name), None)
    if found: return call("PATCH", f"/channels/{found['id']}", body)
    return call("POST", f"/guilds/{G}/channels", {**body, "type": 0})
welcome = text("welcome", start, 0, "What this server is")
how = text("how-it-works", start, 1, "Bot commands for each series")
text("possums-videos", foot, 0, "Mudville Possums — daily football episodes. Type: generate day N", by["football-channel"]["id"])
text("apocalypse-videos", apoc, 0, "Daily zombie apocalypse Shorts", by["apocalypse-channel"]["id"])
text("mafia-stories", mafia, 0, "Post images + narration + script + prompt, then: make video", by["mafia-storys"]["id"])
text("general", comm, 0, None, by["general"]["id"])
text("chat", comm, 1, None, by["normal-chat"]["id"])
print(json.dumps({"welcome": welcome["id"], "how": how["id"]}))

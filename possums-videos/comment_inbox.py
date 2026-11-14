"""Print the #comment-replies messages that haven't been answered yet (posted after the bot's last message).

usage: python3 comment_inbox.py <channel key>   (replies / tenk_replies / possums_stats / possums_results / tenk_results)
Prints NOTHING_NEW if there's nothing to do. Otherwise prints each pending message's text, and saves attachments
(screenshots, .txt pastes, screen recordings -> 1 frame/sec) to inbox/ and prints their paths.
"""
import json, os, sys, subprocess, urllib.request
here = os.path.dirname(os.path.abspath(__file__))
KEY = sys.argv[1] if len(sys.argv) > 1 else "replies"  # replies (Possums) or baseball_replies (Raccoons)
ch = json.load(open(os.path.join(here, "channels.json")))[KEY]
HDR = {"Authorization": "Bot proxy-injected", "User-Agent": "DiscordBot (daily-video-poster, 1.0)"}
msgs = json.load(urllib.request.urlopen(urllib.request.Request(f"https://discord.com/api/v10/channels/{ch}/messages?limit=50", headers=HDR), timeout=30))
msgs.sort(key=lambda m: int(m["id"]))
if KEY.endswith("_results"):   # results channels: everything since the last build started (bot message starting with 🔨), so results can come in pieces
    last_bot = max((int(m["id"]) for m in msgs if m["author"].get("bot") and m["content"].startswith("🔨")), default=0)
    if not any(not m["author"].get("bot") and int(m["id"]) > max((int(x["id"]) for x in msgs if x["author"].get("bot")), default=0) for m in msgs):
        print("NOTHING_NEW"); raise SystemExit   # nothing new since the bot last spoke (it already answered / asked for the missing piece)
else:
    last_bot = max((int(m["id"]) for m in msgs if m["author"].get("bot")), default=0)
pending = [m for m in msgs if not m["author"].get("bot") and m.get("type", 0) in (0, 19) and int(m["id"]) > last_bot]
if not pending:
    print("NOTHING_NEW"); raise SystemExit
os.makedirs(os.path.join(here, "inbox"), exist_ok=True)
for m in pending:
    print(f"===== MESSAGE {m['id']} from {m['author'].get('username')}")
    if m["content"]: print(m["content"])
    for i, a in enumerate(m.get("attachments", [])):
        ext = os.path.splitext(a.get("filename", ""))[1].lower() or ".png"
        dest = os.path.join(here, "inbox", f"{m['id']}_{i}{ext}")
        with urllib.request.urlopen(urllib.request.Request(a["url"], headers={"User-Agent": HDR["User-Agent"]}), timeout=60) as r:
            open(dest, "wb").write(r.read())
        if ext in (".mp4", ".mov", ".webm", ".m4v"):
            fd = dest.rsplit(".", 1)[0] + "_frames"; os.makedirs(fd, exist_ok=True)
            subprocess.run(["ffmpeg", "-loglevel", "error", "-i", dest, "-vf", "fps=1,scale=720:-1", os.path.join(fd, "f%03d.jpg")])
            print(f"[screen recording frames: {fd}/ ({len(os.listdir(fd))} images) - read them all]")
        elif ext == ".txt":
            print(open(dest, errors="ignore").read())
        else:
            print(f"[image: {dest} - read it]")

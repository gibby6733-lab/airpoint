#!/usr/bin/env python3
"""Clip Scout: find the best recent clips from top Twitch streamers and send
them to Telegram with a hook, caption and hashtags.

Run `python clip_scout.py --help` for options. Configuration comes from
environment variables (see README.md).
"""
import argparse
import hashlib
import json
import logging
import math
import os
import re
import shutil
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

log = logging.getLogger("clip-scout")

HELIX = "https://api.twitch.tv/helix"
TELEGRAM_UPLOAD_LIMIT = 50 * 1024 * 1024  # bot API upload limit
CAPTION_LIMIT = 1024
MESSAGE_LIMIT = 4096
SEEN_RETENTION_DAYS = 14
SAME_MOMENT_SECONDS = 45  # clips of one VOD this close together are one moment

HERE = Path(__file__).resolve().parent
DEFAULT_SEEN_FILE = HERE / "seen_clips.json"
DEFAULT_STREAMERS_FILE = HERE / "streamers.txt"

HOOKS = [
    "{streamer} was NOT ready for this 😳",
    "Chat lost it when {streamer} did this 💀",
    "Wait for it... 👀",
    "This is why {streamer} is top of Twitch right now 🔥",
    "Nobody expected this from {streamer} 😂",
    "{streamer}'s reaction says it all 😭",
    "The clip everyone's sharing today 📈",
    "{streamer} just broke the stream 🤯",
]


# --------------------------------------------------------------------------- Twitch

class Twitch:
    def __init__(self, client_id, client_secret, session=None):
        self.client_id = client_id
        self.session = session or requests.Session()
        resp = self.session.post(
            "https://id.twitch.tv/oauth2/token",
            params={
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "client_credentials",
            },
            timeout=30,
        )
        resp.raise_for_status()
        self.token = resp.json()["access_token"]

    def get(self, path, params):
        resp = self.session.get(
            f"{HELIX}/{path}",
            params=params,
            headers={"Client-ID": self.client_id, "Authorization": f"Bearer {self.token}"},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json().get("data", [])

    def top_live_streamers(self, count):
        """Broadcasters of the most-watched live streams right now."""
        streams, cursor = [], None
        while len(streams) < count:
            params = {"first": min(100, count - len(streams))}
            if cursor:
                params["after"] = cursor
            resp = self.session.get(
                f"{HELIX}/streams",
                params=params,
                headers={"Client-ID": self.client_id, "Authorization": f"Bearer {self.token}"},
                timeout=30,
            )
            resp.raise_for_status()
            body = resp.json()
            streams.extend(body.get("data", []))
            cursor = body.get("pagination", {}).get("cursor")
            if not cursor or not body.get("data"):
                break
        return [{"id": s["user_id"], "login": s["user_login"], "name": s["user_name"]} for s in streams]

    def users_by_login(self, logins):
        users = []
        for i in range(0, len(logins), 100):
            batch = logins[i : i + 100]
            users.extend(self.get("users", [("login", login) for login in batch]))
        return [{"id": u["id"], "login": u["login"], "name": u["display_name"]} for u in users]

    def clips(self, broadcaster_id, since, limit=20):
        """Clips created since `since`, which Helix returns most-viewed first."""
        return self.get(
            "clips",
            {
                "broadcaster_id": broadcaster_id,
                "started_at": since.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "ended_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "first": limit,
            },
        )

    def game_names(self, game_ids):
        ids = sorted({g for g in game_ids if g})
        names = {}
        for i in range(0, len(ids), 100):
            for game in self.get("games", [("id", gid) for gid in ids[i : i + 100]]):
                names[game["id"]] = game["name"]
        return names


# --------------------------------------------------------------------------- ranking

def parse_time(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def score(clip, now):
    """Views, gently discounted by age so fresh clips can beat older ones."""
    age_hours = max(0.0, (now - parse_time(clip["created_at"])).total_seconds() / 3600)
    return clip["view_count"] / math.sqrt(age_hours + 2)


def same_moment(a, b):
    if a["broadcaster_id"] != b["broadcaster_id"]:
        return False
    if not a.get("video_id") or a.get("video_id") != b.get("video_id"):
        return False
    if a.get("vod_offset") is None or b.get("vod_offset") is None:
        return False
    return abs(a["vod_offset"] - b["vod_offset"]) <= SAME_MOMENT_SECONDS


def rank_clips(clips, seen_ids, top_n=5, per_streamer=2, now=None):
    """Pick the top clips: skip already-sent ones, collapse clips of the same
    moment, cap clips per streamer."""
    now = now or datetime.now(timezone.utc)
    unique = {c["id"]: c for c in clips if c["id"] not in seen_ids}
    ordered = sorted(unique.values(), key=lambda c: score(c, now), reverse=True)

    picked, per = [], {}
    for clip in ordered:
        if per.get(clip["broadcaster_id"], 0) >= per_streamer:
            continue
        if any(same_moment(clip, p) for p in picked):
            continue
        picked.append(clip)
        per[clip["broadcaster_id"]] = per.get(clip["broadcaster_id"], 0) + 1
        if len(picked) >= top_n:
            break
    return picked


# --------------------------------------------------------------------------- captions

def hashtag(text):
    tag = re.sub(r"[^0-9A-Za-z_]", "", text.title().replace(" ", ""))
    return f"#{tag}" if tag else ""


def build_post(clip, game_name=""):
    streamer = clip["broadcaster_name"]
    pick = int(hashlib.sha1(clip["id"].encode()).hexdigest(), 16) % len(HOOKS)
    hook = HOOKS[pick].format(streamer=streamer)

    title = clip["title"].strip() or "You have to see this"
    caption = f"{title} — {streamer}"
    if game_name:
        caption += f" playing {game_name}"

    tags =["#twitch", "#twitchclips", hashtag(streamer)]
    if game_name:
        tags.append(hashtag(game_name))
    tags += ["#gaming", "#streamer", "#clips", "#fyp", "#viral"]
    tags = list(dict.fromkeys(t for t in tags if t))

    return {
        "hook": hook,
        "caption": caption,
        "hashtags": " ".join(tags),
        "streamer": streamer,
        "game": game_name,
        "url": clip["url"],
        "views": clip["view_count"],
        "duration": clip.get("duration", 0),
    }


def format_text(post, rank, limit=CAPTION_LIMIT):
    """Message text under the video. Shortens the caption line if needed to
    stay within Telegram's limit, keeping the link and hashtags intact."""
    head = f"#{rank} · 🎮 {post['streamer']}" + (f" · {post['game']}" if post["game"] else "")
    stats = f"👁 {post['views']:,} views · ⏱ {post['duration']:.0f}s"
    hook = f"🪝 Hook: {post['hook']}"
    tail = f"🏷 {post['hashtags']}\n\n🔗 {post['url']}"

    def render(caption):
        return f"{head}\n{stats}\n\n{hook}\n\n📝 Caption: {caption}\n\n{tail}"

    text = render(post["caption"])
    if len(text) > limit:
        room = len(post["caption"]) - (len(text) - limit) - 1
        text = render(post["caption"][: max(0, room)].rstrip() + "…")
    return text[:limit]


# --------------------------------------------------------------------------- download + telegram

def download_clip(url, folder):
    """Download the clip as-is (original 16:9 MP4, no re-encode)."""
    import yt_dlp

    opts = {
        "format": "best[ext=mp4]/best",
        "outtmpl": str(Path(folder) / "%(id)s.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return Path(ydl.prepare_filename(info))


class Telegram:
    def __init__(self, token, chat_id, session=None):
        self.base = f"https://api.telegram.org/bot{token}"
        self.chat_id = chat_id
        self.session = session or requests.Session()

    def _check(self, resp):
        body = resp.json() if resp.content else {}
        if not resp.ok or not body.get("ok"):
            raise RuntimeError(f"Telegram error {resp.status_code}: {body.get('description', resp.text)}")
        return body

    def send_message(self, text):
        resp = self.session.post(
            f"{self.base}/sendMessage",
            data={"chat_id": self.chat_id, "text": text[:MESSAGE_LIMIT], "disable_web_page_preview": "false"},
            timeout=60,
        )
        return self._check(resp)

    def send_video(self, path, caption):
        with open(path, "rb") as fh:
            resp = self.session.post(
                f"{self.base}/sendVideo",
                data={"chat_id": self.chat_id, "caption": caption[:CAPTION_LIMIT], "supports_streaming": "true"},
                files={"video": (Path(path).name, fh, "video/mp4")},
                timeout=300,
            )
        return self._check(resp)


def deliver(telegram, post, rank, download, workdir):
    """Send one clip as its own message. Falls back to a link if the video
    can't be uploaded."""
    text = format_text(post, rank)
    if not download:
        telegram.send_message(text)
        return "link"

    path = None
    try:
        path = download_clip(post["url"], workdir)
        size = path.stat().st_size
        if size > TELEGRAM_UPLOAD_LIMIT:
            log.warning("Clip %s is %.1f MB (over 50 MB); sending link instead", post["url"], size / 1e6)
            telegram.send_message(text)
            return "link"
        telegram.send_video(path, text)
        return "video"
    except Exception as exc:  # download/upload failed: still deliver the clip
        log.warning("Could not send video for %s (%s); sending link instead", post["url"], exc)
        telegram.send_message(text)
        return "link"
    finally:
        if path and path.exists():
            path.unlink()


# --------------------------------------------------------------------------- state

def load_seen(path):
    try:
        data = json.loads(Path(path).read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    cutoff = datetime.now(timezone.utc) - timedelta(days=SEEN_RETENTION_DAYS)
    return {cid: ts for cid, ts in data.items() if parse_time(ts) >= cutoff}


def save_seen(path, seen):
    Path(path).write_text(json.dumps(seen, indent=2, sort_keys=True) + "\n")


def read_streamers_file(path):
    if not Path(path).exists():
        return []
    logins = []
    for line in Path(path).read_text().splitlines():
        line = line.split("#", 1)[0].strip().lower()
        if line:
            logins.append(line)
    return logins


# --------------------------------------------------------------------------- main

def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Send the top recent Twitch clips to Telegram.")
    p.add_argument("--top", type=int, default=5, help="how many clips to send (default 5)")
    p.add_argument("--per-streamer", type=int, default=2, help="max clips per streamer (default 2)")
    p.add_argument("--hours", type=int, default=24, help="look back this many hours (default 24)")
    p.add_argument("--live-streamers", type=int, default=50,
                   help="also scan the N most-watched live streamers (default 50, 0 to disable)")
    p.add_argument("--streamers-file", default=str(DEFAULT_STREAMERS_FILE),
                   help="file of Twitch logins to always scan, one per line")
    p.add_argument("--seen-file", default=str(DEFAULT_SEEN_FILE), help="where sent clip IDs are remembered")
    p.add_argument("--dry-run", action="store_true", help="print the picks; send nothing, remember nothing")
    p.add_argument("--no-download", action="store_true", help="send links only instead of video files")
    p.add_argument("-v", "--verbose", action="store_true")
    return p.parse_args(argv)


def require_env(*names):
    missing = [n for n in names if not os.environ.get(n)]
    if missing:
        sys.exit(f"Missing environment variables: {', '.join(missing)} (see README.md)")
    return [os.environ[n] for n in names]


def main(argv=None):
    args = parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(levelname)s %(message)s")

    client_id, client_secret = require_env("TWITCH_CLIENT_ID", "TWITCH_CLIENT_SECRET")
    twitch = Twitch(client_id, client_secret)

    streamers = {}
    fixed = read_streamers_file(args.streamers_file)
    if fixed:
        for user in twitch.users_by_login(fixed):
            streamers[user["id"]] = user
    if args.live_streamers > 0:
        for user in twitch.top_live_streamers(args.live_streamers):
            streamers.setdefault(user["id"], user)
    log.info("Scanning %d streamers", len(streamers))

    since = datetime.now(timezone.utc) - timedelta(hours=args.hours)
    clips = []
    for user in streamers.values():
        try:
            clips.extend(twitch.clips(user["id"], since))
        except requests.RequestException as exc:
            log.warning("Skipping %s: %s", user["login"], exc)
    log.info("Found %d clips from the last %dh", len(clips), args.hours)

    seen = load_seen(args.seen_file)
    picks = rank_clips(clips, set(seen), top_n=args.top, per_streamer=args.per_streamer)
    if not picks:
        log.info("No new clips to send")
        return 0

    games = twitch.game_names(c.get("game_id") for c in picks)
    posts = [build_post(c, games.get(c.get("game_id"), "")) for c in picks]

    if args.dry_run:
        for rank, post in enumerate(posts, 1):
            print(format_text(post, rank))
            print("-" * 40)
        return 0

    token, chat_id = require_env("TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID")
    telegram = Telegram(token, chat_id)
    download = not args.no_download
    if download and not shutil.which("ffmpeg"):
        log.debug("ffmpeg not found; fine for most Twitch clips, install it if downloads fail")

    workdir = tempfile.mkdtemp(prefix="clip-scout-")
    try:
        for rank, (clip, post) in enumerate(zip(picks, posts), 1):
            try:
                how = deliver(telegram, post, rank, download, workdir)
            except Exception as exc:
                log.error("Failed to send %s: %s", post["url"], exc)
                continue
            log.info("Sent #%d %s (%s)", rank, post["url"], how)
            seen[clip["id"]] = datetime.now(timezone.utc).isoformat()
            save_seen(args.seen_file, seen)
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

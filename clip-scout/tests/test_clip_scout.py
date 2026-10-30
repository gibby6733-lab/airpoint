import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import clip_scout as cs  # noqa: E402

NOW = datetime(2026, 10, 30, 12, tzinfo=timezone.utc)


def clip(cid, streamer, views, hours_ago=1, video_id="", offset=None, title="Big play"):
    return {
        "id": cid,
        "url": f"https://clips.twitch.tv/{cid}",
        "broadcaster_id": streamer,
        "broadcaster_name": streamer.title(),
        "title": title,
        "view_count": views,
        "created_at": (NOW - timedelta(hours=hours_ago)).isoformat().replace("+00:00", "Z"),
        "video_id": video_id,
        "vod_offset": offset,
        "game_id": "1",
        "duration": 30.0,
    }


def test_caps_two_per_streamer_and_top_five():
    clips = [clip(f"a{i}", "alpha", 1000 - i) for i in range(4)]
    clips += [clip(f"b{i}", "beta", 500 - i) for i in range(4)]
    clips += [clip("c0", "gamma", 100)]
    picks = cs.rank_clips(clips, set(), now=NOW)
    assert [p["id"] for p in picks] == ["a0", "a1", "b0", "b1", "c0"]


def test_skips_seen_and_same_moment():
    clips = [
        clip("x1", "alpha", 900, video_id="v", offset=100),
        clip("x2", "alpha", 800, video_id="v", offset=120),  # same moment as x1
        clip("x3", "alpha", 700, video_id="v", offset=900),
        clip("y1", "beta", 950),
    ]
    picks = cs.rank_clips(clips, {"y1"}, now=NOW)
    assert [p["id"] for p in picks] == ["x1", "x3"]


def test_fresh_clips_can_outrank_older_ones():
    old = clip("old", "alpha", 1000, hours_ago=23)
    new = clip("new", "beta", 600, hours_ago=1)
    assert cs.rank_clips([old, new], set(), now=NOW)[0]["id"] == "new"


def test_text_fits_caption_limit_and_keeps_link():
    post = cs.build_post(clip("z", "alpha", 10, title="w" * 2000), "Just Chatting")
    text = cs.format_text(post, 1)
    assert len(text) <= cs.CAPTION_LIMIT
    assert post["url"] in text and "#JustChatting" in text and "#Alpha" in text


def test_deliver_falls_back_to_link_when_too_big(tmp_path, monkeypatch):
    big = tmp_path / "big.mp4"
    with open(big, "wb") as fh:
        fh.truncate(cs.TELEGRAM_UPLOAD_LIMIT + 1)
    monkeypatch.setattr(cs, "download_clip", lambda url, folder: big)

    class FakeTelegram:
        def __init__(self):
            self.calls = []

        def send_message(self, text):
            self.calls.append("message")

        def send_video(self, path, caption):
            self.calls.append("video")

    tg = FakeTelegram()
    post = cs.build_post(clip("z", "alpha", 10))
    assert cs.deliver(tg, post, 1, True, tmp_path) == "link"
    assert tg.calls == ["message"] and not big.exists()


def test_deliver_sends_video_and_deletes_file(tmp_path, monkeypatch):
    small = tmp_path / "small.mp4"
    small.write_bytes(b"0" * 10)
    monkeypatch.setattr(cs, "download_clip", lambda url, folder: small)
    sent = []

    class FakeTelegram:
        def send_message(self, text):
            sent.append("message")

        def send_video(self, path, caption):
            sent.append(("video", caption))

    post = cs.build_post(clip("z", "alpha", 10))
    assert cs.deliver(FakeTelegram(), post, 1, True, tmp_path) == "video"
    assert sent[0][0] == "video" and post["url"] in sent[0][1]
    assert not small.exists()


def test_no_download_sends_link_only(tmp_path, monkeypatch):
    monkeypatch.setattr(cs, "download_clip", lambda *a: (_ for _ in ()).throw(AssertionError("downloaded")))
    sent = []

    class FakeTelegram:
        def send_message(self, text):
            sent.append(text)

    post = cs.build_post(clip("z", "alpha", 10))
    assert cs.deliver(FakeTelegram(), post, 1, False, tmp_path) == "link"
    assert len(sent) == 1

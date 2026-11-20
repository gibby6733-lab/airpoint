"""Daily reminder in #make-a-video: come back to Claude and make today's 10-min "Your Move" video (+ an idea to start from).

usage: python3 yourmove_reminder.py [--dry-run]
"""
import datetime, json, os, sys, urllib.request
from zoneinfo import ZoneInfo

CLAUDE = "https://claude.ai/code/session_013umtZoLEZ37bGJSpkYeTGU"
IDEAS = [  # (title, one-line hook)
    ("Your Move: Escape a Sinking Cruise Ship", "The ship tips 30 degrees and 3,000 people race for 20 lifeboats."),
    ("Your Move: Survive 7 Days Lost in the Amazon", "No signal, no map, and the river is full of things that bite."),
    ("Your Move: Escape a Skyscraper Earthquake", "You're on floor 60 when the building starts to sway."),
    ("Your Move: Survive a Plane Crash in the Desert", "120°F, one bottle of water, and the wreck is on fire."),
    ("Your Move: Escape a Volcano Town", "The ash turns day into night and you have 2 hours."),
    ("Your Move: Survive a Blizzard in a Broken-Down Car", "-20°F, half a tank of gas, and no one knows you're here."),
    ("Your Move: Stranded at Sea on a Life Raft", "Sharks, sunburn and no fresh water. 14 days to the shipping lane."),
    ("Your Move: Escape a Zombie Airport", "The last plane leaves Gate 47 in 30 minutes."),
    ("Your Move: Survive a Tornado Outbreak", "Three tornadoes, one town, and your basement is flooding."),
    ("Your Move: Escape a Flooding Subway", "The water is at your knees and rising an inch a minute."),
    ("Your Move: Survive the Arctic After a Shipwreck", "Polar bears, ice and 3 months of darkness."),
    ("Your Move: Escape a Zombie Cruise Ship", "2,000 passengers, 1 infected, and you're in the middle of the ocean."),
    ("Your Move: Survive a Wildfire in the Mountains", "The fire moves faster than you can run uphill."),
    ("Your Move: Escape a Collapsed Mine", "800 feet underground, your light is dying and the air is thinning."),
]

if __name__ == "__main__":
    today = datetime.datetime.now(ZoneInfo("America/New_York")).date()
    title, hook = IDEAS[today.toordinal() % len(IDEAS)]
    txt = (f"🎬 **Time to make today's Your Move video!**\n\n"
           f"👉 Open Claude and say **\"make a Your Move video\"**: {CLAUDE}\n\n"
           f"💡 **Idea for today:** {title}\n_{hook}_\n\n"
           f"⏱️ 10 min • 16:9 • stick-man style • about 1 hour to write + render. Tap ✅ in #yourmove-calendar when it's done.")
    if "--dry-run" in sys.argv:
        print(txt); sys.exit(0)
    here = os.path.dirname(os.path.abspath(__file__))
    ch = json.load(open(os.path.join(here, "channels.json")))["yourmove_reminder"]
    req = urllib.request.Request(f"https://discord.com/api/v10/channels/{ch}/messages", method="POST", data=json.dumps({"content": txt}).encode(),
        headers={"Content-Type": "application/json", "Authorization": "Bot proxy-injected", "User-Agent": "DiscordBot (daily-video-poster, 1.0)"})
    print("sent", json.load(urllib.request.urlopen(req, timeout=30))["id"])

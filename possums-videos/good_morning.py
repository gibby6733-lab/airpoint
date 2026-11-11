"""Post the daily good-morning message + a motivational quote to the #good-morning channel.

usage: python3 good_morning.py [--dry-run]
The quote rotates by date (a different one every day, no repeats until the list runs out).
"""
import datetime, json, os, sys, urllib.request

QUOTES = [  # (quote, author, emojis)
    ("You miss 100% of the shots you don't take.", "Wayne Gretzky", "🏒🎯"),
    ("I've failed over and over and over again in my life. And that is why I succeed.", "Michael Jordan", "🏀🐐"),
    ("Hard work beats talent when talent doesn't work hard.", "Tim Notke", "💪⚒️"),
    ("Do or do not. There is no try.", "Yoda", "⚔️✨"),
    ("Don't quit. Suffer now and live the rest of your life as a champion.", "Muhammad Ali", "🥊🏆"),
    ("Stay hungry, stay foolish.", "Steve Jobs", "🍎🔥"),
    ("Discipline is the bridge between goals and accomplishment.", "Jim Rohn", "🌉🎯"),
    ("Champions keep playing until they get it right.", "Billie Jean King", "🎾🏆"),
    ("The harder the battle, the sweeter the victory.", "Les Brown", "⚔️🍯"),
    ("Your time is limited, so don't waste it living someone else's life.", "Steve Jobs", "⏳🚀"),
    ("What we do in life echoes in eternity.", "Maximus, Gladiator", "🛡️⚔️"),
    ("Pressure is a privilege.", "Billie Jean King", "💎🔥"),
    ("It's not about how hard you hit. It's about how hard you can get hit and keep moving forward.", "Rocky Balboa", "🥊🏃‍♂️"),
    ("Don't watch the clock; do what it does. Keep going.", "Sam Levenson", "⏰➡️"),
    ("The only way to do great work is to love what you do.", "Steve Jobs", "❤️🛠️"),
    ("Opportunities don't happen. You create them.", "Chris Grosser", "🚪🔑"),
    ("The difference between ordinary and extraordinary is that little extra.", "Jimmy Johnson", "⭐🏈"),
    ("Fall seven times, stand up eight.", "Japanese proverb", "🧗‍♂️💯"),
    ("Be so good they can't ignore you.", "Steve Martin", "👀🔥"),
    ("Dream big and dare to fail.", "Norman Vaughan", "🌟🚀"),
    ("Act as if what you do makes a difference. It does.", "William James", "🌍✅"),
    ("Hard choices, easy life. Easy choices, hard life.", "Jerzy Gregorek", "⚖️💪"),
    ("We are what we repeatedly do. Excellence, then, is not an act, but a habit.", "Will Durant", "🔁🏅"),
    ("Start where you are. Use what you have. Do what you can.", "Arthur Ashe", "📍🎾"),
    ("You don't have to be great to start, but you have to start to be great.", "Zig Ziglar", "🏁🚀"),
    ("Winners never quit and quitters never win.", "Vince Lombardi", "🏈🏆"),
    ("Today I will do what others won't, so tomorrow I can do what others can't.", "Jerry Rice", "🏈⏰"),
    ("Don't be afraid to give up the good to go for the great.", "John D. Rockefeller", "💰📈"),
    ("Make each day your masterpiece.", "John Wooden", "🎨🏀"),
    ("It's hard to beat a person who never gives up.", "Babe Ruth", "⚾💪"),
    ("Small daily improvements over time lead to stunning results.", "Robin Sharma", "📈🌱"),
    ("Motivation is what gets you started. Habit is what keeps you going.", "Jim Ryun", "🏃‍♂️🔁"),
    ("If it doesn't challenge you, it won't change you.", "Fred DeVito", "🏋️‍♂️🔥"),
    ("I am the greatest. I said that even before I knew I was.", "Muhammad Ali", "👑🥊"),
]

def message(day=None):
    day = day or datetime.date.today()
    q, who, emo = QUOTES[day.toordinal() % len(QUOTES)]
    return (f"☀️ Good Morning Daddy Gibby and Daddy Adam! 💪 Let's Get Ready To Attack the Day! 🔥🚀\n\n"
            f"{emo} \"{q}\"\n— {who}")

if __name__ == "__main__":
    text = message()
    if "--dry-run" in sys.argv:
        print(text); sys.exit(0)
    here = os.path.dirname(os.path.abspath(__file__))
    ch = json.load(open(os.path.join(here, "channels.json")))["morning"]
    req = urllib.request.Request(f"https://discord.com/api/v10/channels/{ch}/messages", method="POST",
        data=json.dumps({"content": text}).encode(),
        headers={"Content-Type": "application/json", "Authorization": "Bot proxy-injected", "User-Agent": "DiscordBot (daily-video-poster, 1.0)"})
    print("sent", json.load(urllib.request.urlopen(req, timeout=30))["id"])

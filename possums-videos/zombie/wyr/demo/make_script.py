"""Would You Rather: Zombie Apocalypse — demo. Each question = narrator line + 3 s countdown hold (A/B cards).
The user adds the poll in the comments; the video just asks."""
import json, os
B = []
def b(sp, text="", **kw): B.append({"sp": sp, "text": text, **kw})
Q = [("Have fast zombies that are dumb", "🏃", "slow zombies that are smart", "🧠"),
     ("Hide out in a shopping mall", "🏬", "hide out in a prison", "🔒"),
     ("Have unlimited food but no weapons", "🥫", "unlimited weapons but no food", "🪓"),
     ("Survive totally alone", "🧍", "survive with your most annoying relative", "🗣️"),
     ("Get bitten with 24 hours left", "⏳", "be the last human on Earth", "🌍")]
b("cole", "Would you rather. Zombie apocalypse edition. Pick fast.", scene="hook", intensity=.5, sfx=[["sting", .05], ["groan", .6]])
for i, (a, ae, bb, be) in enumerate(Q, 1):
    ex = dict(scene="q", n=i, of=len(Q), a=a, ae=ae, b2=bb[0].upper() + bb[1:], be=be)
    b("cole", f"Would you rather {a.lower()}? Or {bb}?", intensity=.5 + i * .08, **ex)
    b("", hold=2.6, countdown=True, sfx=[["tick", 0], ["tick", .33], ["tick", .66]], **ex)
b("cole", "Vote in the poll in the comments. And tell us why.", scene="cta", intensity=.35)
json.dump({"series": "Would You Rather: Zombie Apocalypse", "episode": 1, "title": "Demo", "vertical": True, "mix": {"music": .08, "ambience": .04},
           "width": 1080, "height": 1920, "beats": B}, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "script.json"), "w"), indent=1, ensure_ascii=False)
print(len(B), "beats,", sum(len(x["text"].split()) for x in B), "words")

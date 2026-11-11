"""Zombie story Shorts — Day 1. One survivor (Cole). Story, then ONE would-you-rather question with two plain options."""
import json, os
B = []
def b(sp, text="", **kw): B.append({"sp": sp, "text": text, **kw})
Q1, Q2 = "Sneak out the back and run for the woods", "Barricade the door and wait it out"
b("cole", "Day one. Everyone I know is gone. It's just me now.", loc="station_ext", tod="night", wx="rain", cast=["cole:.5:idle"], z={"n": 6, "x0": 1.05, "x1": .8, "depth": "far"}, props=["sign", "pumps", "lantern"], fx=["lightning"], focus=.5, intensity=.45, sfx=[["thunder", .1]])
b("cole", "Forty one days ago, the dead started walking. I've been hiding in this old gas station ever since.", tod="day", wx=None, z=None, fx=[], focus=.45, intensity=.25)
b("cole", "This morning, I opened my last can of beans.", loc="station_int", props=["shelves", "radio", "cooler"], cast=["cole:.5:idle"], focus=.5, intensity=.3)
b("cole", "So I had no choice. I walked into town.", loc="road", tod="day", props=["cars"], cast=["cole:.5:run"], focus=.5, sfx=[["steps", .1]])
b("cole", "Bellwood was quiet. Too quiet.", loc="town", wx="fog", cast=["cole:.45:idle"], focus=.45, intensity=.45)
b("cole", "Then I heard something moving inside the pharmacy.", cast=["cole:.42:scared"], z={"n": 1, "x0": .62, "x1": .58, "depth": "mid"}, focus=.5, intensity=.65, sfx=[["groan", .5]])
b("cole", "I ran. And they followed me. All the way home.", loc="road", tod="dusk", wx=None, cast=["cole:.52:run"], z={"n": 8, "x0": .15, "x1": .3, "depth": "mid"}, focus=.45, intensity=.85, sfx=[["steps", 0], ["groan", .5]])
b("cole", "Now there's a crowd of them outside my door. And they're not leaving.", loc="station_ext", tod="night", cast=["cole:.4:scared"], z={"n": 12, "x0": .9, "x1": .62, "depth": "mid"}, props=["sign", "pumps", "lantern"], focus=.5, intensity=.9, sfx=[["groan", .3], ["bang", .7]])
b("cole", f"So, would you rather {Q1.lower()}? Or {Q2.lower()}?", hud="wyr", opt1=Q1, opt2=Q2, intensity=.7, sfx=[["sting", .05]])
b("", hold=2.6, hud="wyr", opt1=Q1, opt2=Q2, countdown=True, sfx=[["tick", 0], ["tick", .33], ["tick", .66]])
b("cole", "Vote in the poll. Tomorrow, you'll see what happens.", hud="wyr", opt1=Q1, opt2=Q2, vote=True, intensity=.4)
json.dump({"series": "Zombie story", "episode": 1, "day": 1, "title": "Day 1", "vertical": True, "mix": {"music": .08, "ambience": .045},
           "beats": B}, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "script.json"), "w"), indent=1)
print(len(B), "beats,", sum(len(x["text"].split()) for x in B), "words")

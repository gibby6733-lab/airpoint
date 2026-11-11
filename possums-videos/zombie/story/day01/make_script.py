"""Zombie survival — Day 1 (v3 "what if" style). Second-person narrator ("you"), stakes-card hook, number cards
every 1-3 s teaching real survival math, side-cutaway library base with camera pans, ONE would-you-rather at the end.
Lesson: rainwater harvesting (1 in of rain on 1,000 sq ft = ~600 gal; dump the first flush; strain; rolling boil 1 min;
~1 gallon per person per day)."""
import json, os
B = []
def b(text="", **kw): B.append({"sp": "narr" if text else "", "text": text, **kw})
def C(t, w=None, **o): return {"t": t, "w": w, **o}
R, G, Y = "#ff5a4a", "#7cd67c", "#ffe14a"
Q1, Q2 = "Carry all your water down to the stone basement", "Stay on the roof and keep collecting while the storm lasts"
b("Three hundred dead are circling your library. And you have three days of water.", scene="stakes", tod="night", intensity=.7,
  cards=[C("300 ZOMBIES", "hundred", c=R, big=True), C("1 LIBRARY", "library", big=True), C("3 DAYS OF WATER", "days", c=Y, big=True)], sfx=[["sting", 0], ["groan", .6]])
b("The taps died this morning.", scene="sink", cards=[C("TAPS: OFF", "taps", c=R)], intensity=.4, sfx=[["tick", .3]])
b("Here's the math. You can go three weeks without food.", scene="base", cam2="f2", you=["f2", 760, "think", 1], tod="day", cards=[C("FOOD: 3 WEEKS", "three")])
b("But only about three days without water.", scene="base", cam2="f2", you=["f2", 600, "scared"], tod="day", jugs=1, cards=[C("WATER: 3 DAYS", "three", c=R)], sfx=[["sting", .1]])
b("So you don't go out. You go up.", scene="base", cam2="roof", you=["roof", 420, "point"], tod="day", cards=[C("DON'T GO OUT", "out", c=R, strike=True), C("GO UP", "up", c=G)], sfx=[["whoosh", .1], ["steps", .4]])
b("This roof is flat. Six thousand square feet.", scene="base", cam2="up", you=["roof", 420, "idle"], tod="day", cards=[C("ROOF: 6,000 SQ FT", "six")])
b("One inch of rain on a thousand square feet gives you about six hundred gallons.", scene="base", cam2="roof", you=["roof", 420, "point"], tod="day",
  cards=[C("1 INCH OF RAIN", "inch"), C("× 1,000 SQ FT", "thousand"), C("= 600 GALLONS", "gallons", c=G)])
b("So one storm on this roof can drop over three thousand gallons.", scene="base", cam2="up", you=["roof", 420, "idle"], tod="day", cards=[C("1 STORM = 3,000+ GAL", "three", c=G)], sfx=[["ding", 1.6]])
b("You block the drains, and run every gutter into a trash can.", scene="base", cam2="roof", you=["roof", 360, "idle"], props=["gutter", "cans"], fill0=0, tod="day", cards=[C("GUTTERS → TRASH CANS", "gutter")], sfx=[["scrape", .3]])
b("But roof water is dirty. Bird droppings. Dust. Dead leaves.", scene="base", cam2="roof", you=["roof", 360, "scared"], props=["gutter", "cans", "dirt"], fill0=0, tod="day", cards=[C("ROOF WATER = DIRTY", "dirty", c=R)])
b("So, rule one. Dump the first flush.", scene="base", cam2="roof", you=["roof", 420, "point"], props=["gutter", "cans", "diverter"], fill0=0, tod="dusk", cards=[C("RULE 1: DUMP THE FIRST FLUSH", "dump", c=Y)])
b("The first few minutes of rain wash the roof. You let that water go.", scene="base", cam2="roof", you=["roof", 420, "idle"], props=["gutter", "cans", "diverter"], rain=True, fill0=0, tod="dusk", wx="rain", cards=[C("FIRST 5 MINUTES → DUMP", "minutes")])
b("Then you strain it through a T-shirt to catch the grit.", scene="cloth", wx=None, cards=[C("STRAIN: T-SHIRT", "strain")])
b("And boil it. A rolling boil, for one full minute.", scene="boil", cards=[C("ROLLING BOIL", "rolling", c=Y), C("1 MINUTE = SAFE", "minute", c=G)], sfx=[["whoosh", .1]])
b("One person needs about a gallon a day. Half to drink. Half to cook and wash.", scene="base", cam2="f2", you=["f2", 520, "think"], tod="dusk", jugs=4,
  cards=[C("1 PERSON = 1 GAL / DAY", "gallon"), C("½ DRINK • ½ COOK & WASH", "half", c=Y)])
b("Night three. The storm finally comes.", scene="base", cam2="up", you=["roof", 420, "idle"], props=["gutter", "cans"], rain=True, tod="night", fx=["lightning"], wx="rain", fill0=.1, fill1=.3, intensity=.6, cards=[C("NIGHT 3", "night", c=Y)], sfx=[["thunder", .2]])
b("Rain hammers the roof, and your cans start to fill.", scene="base", cam2="roof", you=["roof", 420, "cheer"], props=["gutter", "cans"], rain=True, tod="night", fill0=.3, fill1=.8, cards=[C("+40 GALLONS", "fill", c=G)], sfx=[["ding", 1.8]])
b("But rain on plastic is loud. And down below, three hundred heads turn up.", scene="heads", intensity=.85, cards=[C("300 HEADS TURN", "heads", c=R)], sfx=[["thunder", .1], ["groan", 1.6]])
b("They can't climb. But the back door is wood.", scene="base", cam2="f1", tod="night", doorShake=True, wx="rain", fx=[], intensity=.9, cards=[C("THEY CAN'T CLIMB", "climb"), C("BACK DOOR: WOOD", "wood", c=R)], sfx=[["bang", .3], ["bang", 1.1], ["bang", 1.9]])
b("And you hear it start to crack.", scene="base", cam2="f1", tod="night", doorShake=True, crack=True, fx=["shake"], intensity=1, cards=[C("CRACK", "crack", c=R)], sfx=[["crash", .9]])
b(f"So, would you rather {Q1.lower()}? Or {Q2.lower()}?", scene="question", opt1=Q1, opt2=Q2, fx=[], wx=None, intensity=.6, sfx=[["sting", .05]])
b("", hold=2.6, scene="question", opt1=Q1, opt2=Q2, countdown=True, sfx=[["tick", 0], ["tick", .87], ["tick", 1.73]])
b("Vote in the poll. Tomorrow, you'll see what happens.", scene="question", opt1=Q1, opt2=Q2, vote=True, recap="TODAY: DUMP FIRST FLUSH • STRAIN • BOIL 1 MIN")
json.dump({"series": "Zombie survival", "episode": 1, "day": 1, "title": "Day 1", "lesson": "RAINWATER = LIFE", "vertical": True, "lead": .15,
           "speeds": {"narr": 1.12}, "width": 1080, "height": 1920, "mix": {"music": .06, "ambience": .035}, "beats": B},
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "script.json"), "w"), indent=1)
print(len(B), "beats,", sum(len(x["text"].split()) for x in B), "words")

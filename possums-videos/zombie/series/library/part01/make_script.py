"""WHAT IF YOU HID IN A LIBRARY? Part 1 (90 s). Second person, calm deep narrator, cards + paper fact cards."""
import json, os
B = []
def b(text="", **kw): B.append({"sp": "deep" if text else "", "text": text, **kw})
def C(t, w=None, **o): return {"t": t, "w": w, **o}
R, G, Y = "#ff5a4a", "#7cd67c", "#ffe14a"
RULES = ["RULE 1: SILENCE", "RULE 2: NO LIGHT AT NIGHT"]
Q1, Q2 = "Carry all your water down to the stone basement", "Stay on the roof and keep collecting while the storm lasts"
b("Three hundred dead are walking past your library. Not one of them knows you're inside.", scene="stakes", intensity=.6,
  cards=[C("300 DEAD", "hundred", c=R, big=True), C("1 LIBRARY", "library", big=True), C("1 OF YOU", "inside", c=Y, big=True)], sfx=[["sting", 0], ["groan", 1.2]])
b("In a library, silence was always the rule. Now it's the only thing keeping you alive.", scene="library_ext", tod="dusk", pose="idle",
  titleCard=["WHAT IF YOU HID IN A LIBRARY?", "PART 1"], sfx=[["whoosh", .1]])
b("Day zero. Every phone in the city screams at once.", scene="phone", date="DAY 0", clock="11:52", intensity=.7, sfx=[["static", .3], ["sting", .9]])
b("You lock the doors. Stone walls, two feet thick. One door. Windows too high to climb.", scene="base", cam2="all", you=["f2", 540, "idle"], tod="day", rules=RULES,
  cards=[C("STONE: 2 FT", "stone"), C("1 DOOR", "door"), C("WINDOWS: TOO HIGH", "windows")], sfx=[["bang", .4]])
b("Two vending machines. Four hundred snacks. Six weeks, if you're careful.", scene="base", cam2="f2", you=["f2", 760, "think", 1], tod="day", rules=RULES,
  cards=[C("400 SNACKS", "hundred"), C("= 6 WEEKS", "weeks", c=G)])
b("Rule two. No light at night. In a city with no power, one flashlight can be seen for miles.", scene="base", cam2="f2", you=["f2", 600, "point"], tod="night", rules=RULES,
  cards=[C("RULE 2: NO LIGHT AT NIGHT", "light", c=Y), C("SEEN FOR MILES", "miles", c=R)], sfx=[["tick", .2]])
b("So you sit in the dark, and listen to them shuffle past the walls.", scene="base", cam2="f1", tod="night", sfx=[["groan", .8], ["steps", 1.5]])
b("Day three. The taps die.", scene="sink", tod="night", cards=[C("TAPS: OFF", "taps", c=R)], sfx=[["tick", .5]])
b("You have two bottles of water left.", scene="base", cam2="f2", you=["f2", 600, "scared"], tod="day", jugs=2, rules=RULES, cards=[C("WATER: 2 BOTTLES", "two", c=R)])
b("Every survivor learns the rule of three. Three days without water. Three weeks without food.", scene="paper",
  paper={"title": "THE RULE OF 3", "lines": [["3 MINUTES - AIR", "#2a2622"], ["3 DAYS - WATER", "#c0392b"], ["3 WEEKS - FOOD", "#2a2622"]], "src": "the survival rule of threes (rough limits for an average adult)"})
b("So you don't go out. You go up.", scene="base", cam2="roof", you=["roof", 420, "point"], tod="day", rules=RULES,
  cards=[C("DON'T GO OUT", "out", c=R, strike=True), C("GO UP", "up", c=G)], sfx=[["whoosh", .1], ["steps", .4]])
b("One inch of rain on a thousand square feet of roof gives you about six hundred gallons.", scene="paper",
  paper={"title": "ROOF MATH", "lines": ["1 INCH OF RAIN", "x 1,000 SQ FT OF ROOF", [" = 623 GALLONS", "#1f7a3a"]], "icon": "drops", "src": "rainwater harvesting rule: 0.623 gallons per square foot per inch"})
b("Your roof is six thousand square feet. One storm could give you three thousand gallons.", scene="base", cam2="up", you=["roof", 420, "idle"], tod="day",
  cards=[C("ROOF: 6,000 SQ FT", "six"), C("1 STORM = 3,000+ GAL", "three", c=G)], sfx=[["ding", 3.0]])
b("You block the drains, and run every gutter into a trash can.", scene="base", cam2="roof", you=["roof", 360, "idle"], props=["gutter", "cans"], fill0=0, tod="day",
  cards=[C("GUTTERS → TRASH CANS", "gutter")], sfx=[["scrape", .3]])
b("Rule three. Dump the first flush. It washes the bird droppings off the roof.", scene="base", cam2="roof", you=["roof", 420, "point"], props=["gutter", "cans", "diverter", "dirt"], fill0=0, tod="dusk",
  cards=[C("RULE 3: DUMP THE FIRST FLUSH", "dump", c=Y)])
b("Then strain it through a shirt, and boil it for one full minute.", scene="boil", cards=[C("STRAIN", "strain"), C("BOIL: 1 MINUTE", "boil", c=Y)], sfx=[["whoosh", .1]])
b("Night three. The storm comes, and your cans start to fill.", scene="base", cam2="roof", you=["roof", 420, "cheer"], props=["gutter", "cans"], rain=True, tod="night", fx=["lightning"], wx="rain", fill0=.1, fill1=.7, intensity=.6,
  cards=[C("NIGHT 3", "night", c=Y), C("+40 GALLONS", "fill", c=G)], sfx=[["thunder", .2]])
b("But rain on plastic is loud. And three hundred heads turn up.", scene="heads", intensity=.85, cards=[C("300 HEADS TURN", "heads", c=R)], sfx=[["thunder", .1], ["groan", 1.4]])
b("They can't climb. But the back door is wood.", scene="base", cam2="f1", tod="night", doorShake=True, wx="rain", fx=[], intensity=.9,
  cards=[C("THEY CAN'T CLIMB", "climb"), C("BACK DOOR: WOOD", "wood", c=R)], sfx=[["bang", .3], ["bang", 1.1], ["bang", 1.9]])
b("And you hear it crack.", scene="base", cam2="f1", tod="night", doorShake=True, crack=True, fx=["shake"], intensity=1, cards=[C("CRACK", "crack", c=R)], sfx=[["crash", .7]])
b("Your water is up on the roof. Your only way down is the stairs. You have time for one thing.", scene="base", cam2="up", you=["roof", 420, "scared"], props=["gutter", "cans"], rain=True, fill0=.7, tod="night", fx=[], intensity=.9,
  cards=[C("TIME FOR 1 THING", "one", c=Y)], sfx=[["bang", .5], ["bang", 2.2]])
b(f"Would you rather {Q1.lower()}? Or {Q2.lower()}?", scene="question", opt1=Q1, opt2=Q2, fx=[], wx=None, intensity=.6, sfx=[["sting", .05]])
b("", hold=2.4, scene="question", opt1=Q1, opt2=Q2, countdown=True, sfx=[["tick", 0], ["tick", .87], ["tick", 1.73]])
b("Vote in the poll. Part two, tomorrow.", scene="question", opt1=Q1, opt2=Q2, vote=True, recap="RULES: SILENCE • NO LIGHT • DUMP FIRST FLUSH")
json.dump({"series": "What if you hid in a library?", "episode": 1, "day": 1, "title": "Part 1", "lesson": "RAINWATER = LIFE", "vertical": True, "lead": .15, "target": 90,
           "speeds": {"deep": 1.1}, "width": 1080, "height": 1920, "mix": {"music": .06, "ambience": .035}, "beats": B},
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "script.json"), "w"), indent=1)
print(len(B), "beats,", sum(len(x["text"].split()) for x in B), "words")

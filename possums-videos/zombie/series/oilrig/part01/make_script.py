"""WHAT IF YOU HAD TO REACH THE OIL RIG? Part 1 (90 s). Action journey: rooftops -> apartment -> radio -> streets -> harbor."""
import json, os
B = []
def b(text="", sp="deep", **kw): B.append({"sp": sp if text else "", "text": text, **kw})
def C(t, w=None, **o): return {"t": t, "w": w, **o}
R, G, Y = "#ff5a4a", "#7cd67c", "#ffe14a"
Q1, Q2 = "Jump in and swim for the last boat", "Take the fishing boat with half a tank of fuel"
b("Two hundred dead are chasing you across the rooftops. And the next gap is six feet wide.", scene="rooftops", rx=[150, 640], tod="night", intensity=.9,
  cards=[C("200 DEAD", "hundred", c=R, big=True), C("GAP: 6 FT", "gap", c=Y, big=True)], sfx=[["steps", 0], ["groan", .8], ["steps", 2.0]])
b("You don't slow down.", scene="rooftops", rx=[640, 1080], ease=False, tod="night", intensity=1, sfx=[["whoosh", .2], ["crash", 1.0]])
b("Six hours earlier, you were asleep.", scene="apartment", youX=330, pose="idle", titleCard=["WHAT IF YOU HAD TO REACH THE OIL RIG?", "PART 1"], intensity=.3, sfx=[["whoosh", .1]])
b("Then every phone in the city screamed at once.", scene="phone", date="DAY 0", clock="11:52", intensity=.7, sfx=[["static", .2], ["sting", .8]])
b("Outside, the street is screaming. Smoke to the east.", scene="apartment", fire=True, youX=300, pose="scared", intensity=.8, sfx=[["scream", .2]])
b("This is the Ocean Star oil platform, twelve miles offshore. The dead can't reach us. Boats leave the harbor at dawn.", sp="radio", scene="radio", intensity=.5, sfx=[["static", 0]])
b("Three miles to the harbor. Twelve miles of sea. Sunrise is at six.", scene="map", cards=[C("SUNRISE: 6:00 AM", "sunrise", c=Y)])
b("You grab a bag. Water, a flashlight, a lighter, a knife.", scene="apartment", youX=420, pose="point", bag=True, fire=True)
b("One gallon of water a day, per person. You can carry two. That's two days.", scene="apartment", fire=True, youX=420, pose="think", cards=[C("1 GALLON / DAY", "gallon"), C("YOU HAVE: 2 DAYS", "two", c=R)])
b("But your street is full of them.", scene="street", z={"n": 9, "x0": .3, "x1": .45, "depth": "mid"}, intensity=.7, cards=[C("STREET: BLOCKED", "full", c=R)], sfx=[["groan", .4]])
b("A car alarm hits a hundred and twenty decibels. As loud as a rock concert.", scene="paper",
  paper={"title": "THE LOUDEST THING ON THE BLOCK", "lines": ["CAR ALARM: 120 dB", "ROCK CONCERT: 120 dB", ["THE DEAD GO TO NOISE", "#c0392b"]], "src": "typical car alarms are rated around 110-125 decibels"})
b("So you smash a window, and every dead thing on the block turns toward it.", scene="street", alarm=True, smash=True, z={"n": 9, "x0": .55, "x1": .25, "depth": "mid"}, you=[900, 1000, "point", 1], intensity=.9,
  cards=[C("DECOY", "smash", c=Y)], sfx=[["crash", .5], ["rattle", .9]])
b("You run the other way. Then the alarm dies, and they come back for you.", scene="street", z={"n": 12, "x0": -.1, "x1": .45, "depth": "mid"}, you=[600, 1150, "run"], scroll=400, intensity=1,
  sfx=[["steps", 0], ["groan", 2.4], ["steps", 3.0]])
b("Twelve of them. One of you. And they never get tired.", scene="street", z={"n": 12, "x0": .45, "x1": .6, "depth": "near"}, you=[1150, 1250, "run"], intensity=1, cards=[C("12 vs 1", "twelve", c=R)], sfx=[["groan", .2]])
b("So you take the roofs. Which brings you here.", scene="rooftops", rx=[1100, 1600], tod="night", intensity=.9, cards=[C("TAKE THE ROOFS", "roofs", c=Y)], sfx=[["steps", 0], ["steps", 1.4]])
b("You jump. You make it. Three of them don't.", scene="rooftops", rx=[1600, 2050], ease=False, chasers=6, gapZ=200, tod="night", intensity=1,
  cards=[C("3 DOWN", "three", c=G)], sfx=[["whoosh", .1], ["crash", .9], ["groan", 1.5]])
b("Dawn. The harbor. The last boat is already pulling away.", scene="harbor", tod="dusk", bigBoat=[640, 1000], you=[500, 690, "run"], z=None, intensity=.7,
  cards=[C("5:58 AM", "dawn", c=Y), C("LAST BOAT", "boat", c=R)], sfx=[["engine", .3]])
b("You scream at it. Nobody turns around.", scene="harbor", tod="dusk", bigBoat=[1000, 1060], you=[690, 690, "scared"], cards=[C("NOBODY HEARS", "nobody", c=R)], sfx=[["scream", 0]])
b("And behind you, they're coming down the pier.", scene="harbor", tod="dusk", bigBoat=[1000, 1250], fishing=True, you=[690, 700, "scared", 1], z={"n": 8, "x0": -.25, "x1": .05, "depth": "mid"}, intensity=1,
  sfx=[["groan", .2], ["steps", .8]])
b("Cold water has a rule. One minute of shock. Ten minutes before your arms quit. One hour before you pass out.", scene="paper",
  paper={"title": "THE 1-10-1 RULE", "lines": [["1 MINUTE - COLD SHOCK", "#c0392b"], "10 MINUTES - ARMS QUIT", "1 HOUR - YOU PASS OUT"], "icon": "drops", "src": "cold water immersion: the 1-10-1 principle"})
b("The boat is two hundred yards out. In this water, that's five minutes of swimming.", scene="harbor", tod="dusk", bigBoat=[1250, 1300], you=[700, 700, "think"], z={"n": 8, "x0": .05, "x1": .05, "depth": "mid"}, cards=[C("200 YARDS", "two"), C("= 5 MIN SWIM", "five", c=Y)])
b("At the end of the pier, a fishing boat. Half a tank of fuel. Twelve miles to the rig.", scene="harbor", tod="dusk", bigBoat=[1250, 1400], fishing=True, you=[700, 720, "point"], z={"n": 8, "x0": .05, "x1": .2, "depth": "mid"},
  cards=[C("FUEL: HALF", "half", c=Y), C("RIG: 12 MILES", "twelve")], sfx=[["groan", 1.0]])
b(f"Would you rather {Q1.lower()}? Or {Q2.lower()}?", scene="question", opt1=Q1, opt2=Q2, intensity=.6, sfx=[["sting", .05]])
b("", hold=2.4, scene="question", opt1=Q1, opt2=Q2, countdown=True, sfx=[["tick", 0], ["tick", .8], ["tick", 1.6]])
b("Vote in the poll. Part two, tomorrow.", scene="question", opt1=Q1, opt2=Q2, vote=True, recap="1-10-1: SHOCK • ARMS QUIT • PASS OUT")
json.dump({"series": "What if you had to reach the oil rig?", "episode": 1, "day": 1, "title": "Part 1", "lesson": "NOISE IS A WEAPON", "vertical": True, "lead": .15, "target": 90,
           "speeds": {"deep": 1.12}, "width": 1080, "height": 1920, "mix": {"music": .065, "ambience": .035}, "beats": B},
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "script.json"), "w"), indent=1)
print(len(B), "beats,", sum(len(x["text"].split()) for x in B), "words")

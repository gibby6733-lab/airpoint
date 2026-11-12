"""WHAT IF YOU HAD TO REACH THE OIL RIG? Part 2 (90 s). Poll: most took the FISHING BOAT. Pier escape -> open sea -> fog -> fuel runs out."""
import json, os
B = []
def b(text="", sp="deep", **kw): B.append({"sp": sp if text else "", "text": text, **kw})
def C(t, w=None, **o): return {"t": t, "w": w, **o}
R, G, Y = "#ff5a4a", "#7cd67c", "#ffe14a"
Q1, Q2 = "Climb onto the drifting sailboat", "Row toward the fog horn with the oars"
b("Most of you said take the fishing boat.", scene="voted", poll=[["TAKE THE FISHING BOAT", None, "#1f9d55"]], sfx=[["reveal", .1]])
b("So you run.", scene="harbor", tod="dusk", fishing=True, you=[640, 860, "run"], z={"n": 8, "x0": .02, "x1": .3, "depth": "mid"}, titleCard=["WHAT IF YOU HAD TO REACH THE OIL RIG?", "PART 2"], intensity=1, sfx=[["steps", 0], ["groan", .6]])
b("They're ten feet behind you. You jump in and cut the rope.", scene="harbor", tod="dusk", fishing=True, you=[860, 880, "run"], z={"n": 8, "x0": .3, "x1": .45, "depth": "mid"}, intensity=1,
  cards=[C("10 FT", "ten", c=R, big=True)], sfx=[["groan", .2], ["whoosh", .7]])
b("You pull the cord. Nothing. Again. Nothing.", scene="sea", tod="dusk", pier=True, z={"n": 8, "x0": .05, "x1": .25, "depth": "mid"}, boat=[600, 600], you=[-40, "scared"], intensity=1,
  cards=[C("PULL 1", "cord", c=R), C("PULL 2", "again", c=R)], sfx=[["rattle", .25], ["rattle", .75], ["groan", .9]])
b("Third pull. The engine roars.", scene="sea", tod="dusk", pier=True, z={"n": 8, "x0": .25, "x1": .3, "depth": "mid"}, boat=[600, 700], speed=.6, you=[-40, "point"], intensity=1,
  cards=[C("PULL 3", "third", c=G)], sfx=[["engine", .4]])
b("And a hand grabs the back of the boat.", scene="sea", tod="dusk", boat=[700, 700], speed=.6, grab=[.3, 2], you=[-40, "scared"], fx=["shake"], intensity=1,
  cards=[C("GRAB", "hand", c=R, big=True)], sfx=[["crash", .35], ["groan", .5]])
b("You kick. It lets go, and sinks without a sound.", scene="sea", tod="dusk", boat=[700, 600], speed=.8, grab=[0, .45], you=[-40, "point", 1], intensity=.8, sfx=[["bang", .15], ["whoosh", .55]])
b("Open water. Twelve miles to the rig. Half a tank.", scene="sea", tod="day", rig=[880, .8], boat=[400, 560], speed=1, you=[-40, "idle"], intensity=.6,
  cards=[C("RIG: 12 MILES", "twelve"), C("FUEL: HALF", "half", c=Y)], sfx=[["engine", 0]])
b("Here's the thing about boats. Full throttle drinks fuel. Slow down, and the same tank goes a lot farther.", scene="paper",
  paper={"title": "FULL THROTTLE = EMPTY TANK", "lines": [["FULL SPEED: WORST MILES PER GALLON", "#c0392b"], "CRUISING SPEED: BEST RANGE", ["SLOW GOES FARTHER", "#1f9d55"]], "src": "boating fuel guides: best miles per gallon is at cruising speed, not wide open"})
b("So you throttle back. Slow. Every drop counts.", scene="sea", tod="day", rig=[880, .8], boat=[560, 600], speed=.35, you=[-40, "think"], cards=[C("HALF THROTTLE", "throttle", c=G)], sfx=[["engine", .1]])
b("Then the fog rolls in. The rig disappears. So does everything else.", scene="sea", tod="day", rig=[880, .8], fog=[0, 1], boat=[600, 600], speed=.35, you=[-40, "scared"], intensity=.7,
  cards=[C("VISIBILITY: 20 FT", "everything", c=R)], sfx=[["sting", .3]])
b("No compass. No GPS. Just gray.", scene="sea", tod="day", fog=1, boat=[600, 600], speed=.3, you=[-40, "think"], intensity=.6)
b("Then you hear it. One long horn blast.", scene="sea", tod="day", fog=1, horn=[880, 1050], boat=[600, 600], speed=.3, you=[-40, "point"], intensity=.7,
  cards=[C("HOOOONK", "horn", c=Y, big=True)], sfx=[["engine", .5]])
b("In fog, ships and platforms sound a long blast at least every two minutes. Follow the sound.", scene="paper",
  paper={"title": "THE FOG RULE", "lines": ["1 LONG BLAST", ["AT LEAST EVERY 2 MINUTES", "#c0392b"], ["FOLLOW THE SOUND", "#1f9d55"]], "icon": "drops", "src": "International Regulations for Preventing Collisions at Sea (COLREGs), Rule 35"})
b("Two minutes later, again. You turn toward it.", scene="sea", tod="day", fog=1, horn=[880, 1050], boat=[600, 700], speed=.35, you=[-40, "point"], cards=[C("EVERY 2 MIN", "two", c=G)])
b("Then the engine coughs. And dies.", scene="sea", tod="day", fog=1, cough=True, boat=[700, 700], you=[-40, "scared"], intensity=.9,
  cards=[C("FUEL: EMPTY", "coughs", c=R), C("4 MILES LEFT", "dies", c=Y)], sfx=[["sputter", .2], ["sting", .8]])
b("Something bumps the hull. Then again. You're not alone out here.", scene="sea", tod="day", fog=.8, floaters=9, boat=[700, 700], tilt=.06, you=[-40, "scared"], fx=["shake"], intensity=1,
  cards=[C("BUMP", "bumps", c=R), C("BUMP", "again", c=R)], sfx=[["bang", .2], ["bang", .5], ["groan", .8]])
b("Remember the rule. One minute of shock. Ten before your arms quit. Nobody swims four miles.", scene="sea", tod="day", fog=.8, floaters=9, boat=[700, 700], you=[-40, "think"],
  cards=[C("1-10-1", "rule", c=Y, big=True), C("NO SWIMMING", "nobody", c=R)])
b("Then, through the fog, a sailboat. Drifting. Nobody at the wheel. Its sail is still up.", scene="sea", tod="day", fog=[.9, .6], floaters=6, sail=[-150, 260, .9], boat=[760, 760], you=[-40, "point", 1], intensity=.7,
  cards=[C("SAILBOAT", "sailboat", c=G), C("NOBODY ON BOARD?", "nobody", c=Y)], sfx=[["sting", .2]])
b("The current pulls you toward it. The horn is the other way.", scene="sea", tod="day", fog=.6, floaters=6, sail=[260, 330, .9], horn=[980, 1050], boat=[760, 720], you=[-40, "think"],
  cards=[C("HORN →", "horn", c=Y)], sfx=[["engine", .4]])
b(f"Would you rather {Q1.lower()}? Or {Q2.lower()}?", scene="question", opt1=Q1, opt2=Q2, intensity=.6, sfx=[["sting", .05]])
b("", hold=2.4, scene="question", opt1=Q1, opt2=Q2, countdown=True, sfx=[["tick", 0], ["tick", .8], ["tick", 1.6]])
b("Vote in the poll. Part three, tomorrow.", scene="question", opt1=Q1, opt2=Q2, vote=True, recap="FOG HORN: EVERY 2 MINUTES")
json.dump({"series": "What if you had to reach the oil rig?", "episode": 2, "day": 2, "title": "Part 2", "lesson": "SLOW GOES FARTHER", "vertical": True, "style": "stick", "lead": .15, "target": 90,
           "speeds": {"deep": 1.12}, "width": 1080, "height": 1920, "mix": {"music": .065, "ambience": .035}, "beats": B},
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "script.json"), "w"), indent=1)
print(len(B), "beats,", sum(len(x["text"].split()) for x in B), "words")

"""Zombie survival lessons — Day 1. Cole (ex-science teacher) at the Bellwood Public Library.
Hook in the first 5 s, a real survival lesson (safe drinking water), then ONE would-you-rather question."""
import json, os
B = []
def b(sp, text="", **kw): B.append({"sp": sp, "text": text, **kw})
Q1, Q2 = "Keep boiling water and risk the smoke", "Put out the fire and live on what you have left"
b("cole", "Zombies won't kill you first. Dirty water will. Here's how I stayed alive.", scene="hook", h1="ZOMBIES WON'T KILL YOU FIRST.", h2="DIRTY WATER WILL.", tod="night", z=None, sfx=[["sting", 0], ["whoosh", .5]])
b("cole", "I'm Cole. I used to teach science. Now I teach survival.", scene="library_ext", tod="night", tag="COLE • EX-SCIENCE TEACHER", pose="talk")
b("cole", "I picked this library on purpose. Stone walls, one door, and windows too high to climb.", scene="library_ext", tag="1 DOOR • THICK STONE WALLS", pose="point")
b("cole", "But on day three, the taps stopped running.", scene="sink", tod="night", sfx=[["tick", .2], ["tick", 1.1]])
b("cole", "Here's the science. You can last about three weeks without food. But only about three days without water.", scene="library_int", pose="think", tag="3 WEEKS FOOD • 3 DAYS WATER")
b("cole", "So I went to the river. But river water can carry bacteria and parasites.", scene="river", tod="day", showBottle=True, z={"n": 4, "x0": 1.1, "x1": .95, "depth": "far", "turn": True}, sfx=[["groan", .8]])
b("cole", "They make you sick, and you lose even more water. Out here, that can kill you.", scene="warn", tod="day", z=None)
b("cole", "Step one. Pour it through a cloth to catch the dirt.", scene="step", n=1, title="FILTER THROUGH CLOTH", sub="Clears dirt. Does NOT kill germs.", tod="night")
b("cole", "Step two. Bring it to a rolling boil for one full minute. Three minutes if you're high in the mountains.", scene="step", n=2, title="ROLLING BOIL: 1 MINUTE", sub="3 minutes at high altitude", sfx=[["whoosh", 0]])
b("cole", "Step three. Let it cool, and store it in clean, covered jars.", scene="step", n=3, title="STORE IT COVERED", sub="Clean jars. Lids on.", sfx=[["ding", 1.2]])
b("cole", "But there's a problem. The smoke from my fire can be seen for miles.", scene="roof", tod="dusk", pose="idle", z={"n": 5, "x0": 1.2, "x1": 1.0, "depth": "far", "turn": True})
b("cole", "And tonight, they saw it.", scene="roof", tod="night", pose="scared", z={"n": 10, "x0": 1.05, "x1": .78, "depth": "mid", "turn": True}, fx=["shake"], sfx=[["groan", .1], ["bang", .9]])
b("cole", f"So, would you rather {Q1.lower()}? Or {Q2.lower()}?", scene="question", opt1=Q1, opt2=Q2, z=None, fx=[], sfx=[["sting", .05]])
b("", hold=2.6, scene="question", opt1=Q1, opt2=Q2, countdown=True, sfx=[["tick", 0], ["tick", .87], ["tick", 1.73]])
b("cole", "Vote in the poll. Tomorrow, you'll see what happens.", scene="question", opt1=Q1, opt2=Q2, vote=True, recap="TODAY: FILTER • BOIL 1 MIN • COVER")
json.dump({"series": "Zombie survival lessons", "episode": 1, "day": 1, "title": "Day 1", "lesson": "SAFE DRINKING WATER", "vertical": True, "lead": .15,
           "width": 1080, "height": 1920, "mix": {"music": .08, "ambience": .045}, "beats": B},
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "script.json"), "w"), indent=1)
print(len(B), "beats,", sum(len(x["text"].split()) for x in B), "words")

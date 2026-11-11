"""Would You Survive? — The Titanic (YouTube Shorts, 9:16).
Facts used (well documented): iceberg 11:40 PM Apr 14 1912; sank ~2:20 AM; ~2,224 aboard, ~1,500 died, ~700 survived;
20 lifeboats with ~1,178 seats; first boat (No. 7) left ~12:45 AM with ~28 of 65 seats filled; water about -2 C;
Carpathia arrived ~4 AM; about 30 men survived standing on overturned Collapsible B."""
import json, os
B = []
def b(sp, text="", **kw): B.append({"sp": sp, "text": text, **kw})
b("narr", "Would you survive the Titanic? Three choices. Let's see.", scene="hook", intensity=.4, sfx=[["sting", .05]])
b("narr", "Eleven forty PM. The ship just hit an iceberg.", scene="impact", clock="11:40 PM", intensity=.6, sfx=[["crash", .55], ["scrape", .6]])
b("narr", "There are lifeboat seats for only half the people on board.", scene="stat", intensity=.5)
b("narr", "Choice one. Get in the first lifeboat? Or stay on the warm ship?", scene="choice", n=1, q="The crew starts loading lifeboats", a="Get in the first lifeboat", bb="Stay on the warm ship", intensity=.55)
b("", hold=2.6, scene="choice", n=1, q="The crew starts loading lifeboats", a="Get in the first lifeboat", bb="Stay on the warm ship", countdown=True, sfx=[["tick", 0], ["tick", .33], ["tick", .66]])
b("narr", "The first lifeboat left with just twenty eight people. It had room for sixty five. If you got in, you live.", scene="lifeboat", clock="12:45 AM", win="A", intensity=.45, sfx=[["ding", .9]])
b("narr", "Choice two. Two AM. The ship is tilting. Jump now? Or climb to the back?", scene="choice", n=2, q="2 AM. The ship is tilting", a="Jump into the ocean now", bb="Climb to the back of the ship", intensity=.7)
b("", hold=2.6, scene="choice", n=2, q="2 AM. The ship is tilting", a="Jump into the ocean now", bb="Climb to the back of the ship", countdown=True, sfx=[["tick", 0], ["tick", .33], ["tick", .66]])
b("narr", "The water is minus two degrees. Jump early, and you last minutes. Climbing buys you time.", scene="cold", clock="2:00 AM", win="B", intensity=.75, sfx=[["ding", .9]])
b("narr", "At two twenty, the Titanic sinks.", scene="sink", clock="2:20 AM", intensity=.9, sfx=[["crash", .3], ["thunder", .4]])
b("narr", "Choice three. You're in freezing water. Swim to a flipped lifeboat? Or float and wait?", scene="choice", n=3, q="You're in the freezing water", a="Swim to a flipped lifeboat", bb="Float and wait for rescue", intensity=.8)
b("", hold=2.6, scene="choice", n=3, q="You're in the freezing water", a="Swim to a flipped lifeboat", bb="Float and wait for rescue", countdown=True, sfx=[["tick", 0], ["tick", .33], ["tick", .66]])
b("narr", "Rescue doesn't come until four AM. But about thirty men survived standing on a flipped lifeboat. Swim.", scene="collapsible", clock="4:00 AM", win="A", intensity=.5, sfx=[["ding", .95]])
b("narr", "About fifteen hundred people died that night. Around seven hundred survived.", scene="result", intensity=.35)
b("narr", "Would you have made it? Comment your answers. And what disaster should we survive next?", scene="cta", intensity=.3)
json.dump({"series": "Would You Survive?", "episode": 1, "title": "The Titanic", "vertical": True, "mix": {"music": .075, "ambience": .035}, "width": 1080, "height": 1920, "beats": B},
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "script.json"), "w"), indent=1)
print(len(B), "beats,", sum(len(x["text"].split()) for x in B), "words")

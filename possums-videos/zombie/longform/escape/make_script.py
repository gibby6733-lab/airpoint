"""YOUR MOVE: Escape the City Before It Falls — 10 min, 16:9 (1920x1080), stick-man style.
10 chapters, each a new location with action + a "Your move" choice (both outcomes shown) + real facts."""
import json, os
B = []
CLOCK = {"v": "6:00 AM"}
def b(text="", sp="deep", **kw):
    if "clock" in kw: CLOCK["v"] = kw["clock"]
    B.append({"sp": sp if text else "", "text": text, "clock": CLOCK["v"], **{k: v for k, v in kw.items() if k != "clock"}})
def C(t, w=None, **o): return {"t": t, "w": w, **o}
def you(x0, x1=None, pose="idle", y=900, flip=False, s=.72, y1=None): return {"x0": x0, "x1": x0 if x1 is None else x1, "y0": y, "y1": y if y1 is None else y1, "pose": pose, "flip": flip, "s": s}
def Z(n, x0, x1, y=900, s=.62, spread=420, turn=False): return {"n": n, "x0": x0, "x1": x1, "y": y, "s": s, "spread": spread, "turn": turn}
R, G, Y = "#ff5a4a", "#7cd67c", "#ffe14a"
def choice(bg, q, o1, o2, **kw):
    b(f"Your move. {q}", scene="choice", bg=bg, opt1=o1, opt2=o2, intensity=.6, sfx=[["sting", .05]], **kw)
    b("", hold=2.6, scene="choice", bg=bg, opt1=o1, opt2=o2, countdown=True, sfx=[["tick", 0], ["tick", .87], ["tick", 1.73]], **kw)

# ---------------- COLD OPEN (flash-forward)
b("The last helicopter out of the city lifts off in ten seconds.", scene="helipad", clock="8:59 PM", heli="hover", you=you(300, 520, "run"), zz=Z(12, -300, 60, spread=500), efx=["wind"], intensity=1,
  cards=[C("LAST HELICOPTER", "helicopter", c=Y), C("10 SECONDS", "ten", c=R)], sfx=[["engine", 0], ["groan", 1.5]])
b("And five hundred dead are between you and it.", scene="helipad", heli="hover", you=you(520, 600, "scared"), zz=Z(16, -100, 260, spread=600), efx=["wind", "shake"], intensity=1,
  cards=[C("500 DEAD", "hundred", c=R, big=True)], sfx=[["groan", .2], ["bang", 1.2]])
b("Below you, the whole city is burning. And you are one jump from getting out.", scene="helipad", heli="hover", you=you(600, pose="point"), zz=Z(16, 0, 300, spread=600), efx=["wind"], intensity=.9, rewind=True, sfx=[["engine", .2]])
b("Twenty four hours ago, you were asleep. Every choice from here is your move. Get them right, and you live.", scene="title", intensity=.5, sfx=[["whoosh", .1], ["reveal", 1.0]])
b("Here's how this works. Every chapter, you get one choice. Pause the video, pick your move, and keep count. At the end, we'll see if you made it.", scene="title", intensity=.4, sfx=[["tick", 2.0]])

# ---------------- 1. APARTMENT
b("Six A.M. Every phone in the city screams at once.", scene="apartment", chapter=["1", "THE APARTMENT"], clock="6:00 AM", you=you(1200, pose="scared"), phone=True, intensity=.6, sfx=[["static", .2], ["sting", .6]])
b("You run to the window. Down on the street, people are running. And some of the people chasing them are not people anymore.", scene="apartment", you=you(1200, 700, "run", flip=True), fire=True, intensity=.8, sfx=[["scream", 1.5], ["groan", 3.0]])
b("On the news, a reporter is mid sentence when something pulls her off camera.", scene="apartment", you=you(1250, pose="scared", flip=True), tv="attack", intensity=.7, sfx=[["scream", 1.6], ["static", 2.2]])
b("Across the street, a building is on fire. Then your power cuts out.", scene="apartment", you=you(1250, 900, "point", flip=True), fire=True, power="off", intensity=.7, sfx=[["crash", 2.0]])
b("And someone is pounding on your door. Not knocking. Pounding.", scene="apartment", you=you(900, 1000, "scared"), fire=True, power="off", door="pound", efx=["shake"], intensity=.9, sfx=[["bang", .2], ["bang", .9], ["bang", 1.6], ["bang", 2.3]])
b("You've got about ten seconds to think. So you think about what matters. Water. Food. A way out.", scene="apartment", you=you(1000, pose="think"), fire=True, power="off", door="pound", intensity=.8, cards=[C("WATER", "water"), C("FOOD", "food"), C("A WAY OUT", "way", c=Y)], sfx=[["bang", .4], ["bang", 2.0]])
b("The door frame cracks.", scene="apartment", you=you(1000, pose="scared"), fire=True, power="off", door="pound", efx=["shake"], intensity=1, sfx=[["crash", .2]])
choice("apartment", "Barricade the door? Or grab your bag and run, right now?", "Barricade the door", "Grab your bag and run")
b("If you barricaded, you're safe. For an hour. Then the smoke from across the street fills your floor.", scene="apartment", stamp="wrong", you=you(1000, pose="scared"), fire=True, power="off", smoke=1, sfx=[["sting", 0]])
b("You crawl to the window to breathe. Twelve floors up. No way down. And the door is still blocked by everything you own.", scene="apartment", stamp="wrong", you=you(700, pose="scared"), fire=True, power="off", smoke=1, intensity=.9, sfx=[["cough", .5], ["cough", 2.5]])
b("Most people who die in fires never touch a flame. It's the smoke that gets them.", scene="paper", paper={"title": "FIRE FACT", "lines": ["MOST FIRE DEATHS:", ["SMOKE, NOT FLAMES", "#c0392b"], "STAY LOW. GET OUT EARLY."], "src": "smoke inhalation causes the majority of fire deaths (U.S. fire safety data)"})
b("If you ran, good move. You open the door just as your neighbor lunges. He's already turned.", scene="apartment", stamp="right", you=you(1000, 1150, "run"), neighbor="lunge", fire=True, power="off", intensity=1, sfx=[["groan", .5], ["whoosh", 1.4]])
b("He flies past you, into your apartment. You slam the door behind him.", scene="apartment", you=you(1150, 1250, "point"), neighbor="inside", door="slam", fire=True, power="off", efx=["shake"], sfx=[["bang", .9]])
b("You grab the bag you packed for camping last summer. Water bottle. Flashlight. Knife. First aid kit.", scene="apartment", you=you(1250, 1150, "point", flip=True), fire=True, power="off", intensity=.6,
  cards=[C("WATER", "water"), C("FLASHLIGHT", "flashlight"), C("FIRST AID", "first", c=G)], sfx=[["rattle", .5]])
b("Rule one of any emergency. Don't wait for someone to tell you to leave.", scene="paper", paper={"title": "RULE ONE", "lines": [["DON'T WAIT", "#c0392b"], "FOR PERMISSION", "TO LEAVE"], "src": "evacuation guidance: leave early, before routes are blocked"})

# ---------------- 2. STAIRWELL
b("The hallway lights are flashing red. Fire alarm. And somewhere below you, someone is screaming.", scene="stairwell", chapter=["2", "THE STAIRWELL"], clock="6:20 AM", you=you(300, 600, "run", y=430), intensity=.8, sfx=[["sting", .1], ["scream", 2.0]])
b("Your building has twelve floors. And the elevator still works.", scene="stairwell", you=you(980, pose="think", y=430), lift="open", intensity=.5, cards=[C("12 FLOORS", "twelve")], sfx=[["ding", 1.6]])
choice("stairwell", "The elevator? Or the stairs?", "Take the elevator", "Take the stairs")
b("If you took the elevator, it stops between floors four and five. Then the doors start to open. From the outside.", scene="stairwell", stamp="wrong", lift="stuck", you=you(980, pose="scared", y=700), intensity=.9, sfx=[["crash", .2], ["scrape", 2.6]])
b("Grey fingers slide through the gap. Then a face. Then another. You're in a steel box, and they're opening it.", scene="stairwell", stamp="wrong", lift="stuck", intensity=1, efx=["shake"], sfx=[["groan", .3], ["scrape", 1.5]])
b("In an emergency, never take the elevator. When the power goes, it becomes a steel box with no way out.", scene="paper", paper={"title": "EMERGENCY RULE", "lines": [["NEVER THE ELEVATOR", "#c0392b"], "POWER FAILS = TRAPPED", "ALWAYS TAKE THE STAIRS"], "src": "standard fire and emergency evacuation guidance"})
b("If you took the stairs, good move. But ten floors down, the dead are already coming up.", scene="stairwell", stamp="right", you=you(560, 700, "run", y=430), zz=Z(8, 300, 700, y=900, s=.5, spread=380), intensity=.9, sfx=[["steps", 0], ["groan", 1.5]])
b("So you do what you did as a kid. You slide down the railing, straight over their heads.", scene="stairwell", slide=True, you=you(400, 1500, "cheer", y=430, y1=880), zz=Z(8, 500, 700, y=900, s=.5, spread=380), efx=["speed"], intensity=1, sfx=[["whoosh", .2], ["scrape", .8]])
b("Your hands burn. Your bag almost rips off your back. But you're moving faster than anything on those stairs.", scene="stairwell", slide=True, zz=Z(8, 600, 750, y=900, s=.5, spread=380), efx=["speed"], intensity=1, sfx=[["whoosh", .2]])
b("The lobby. And the front door is locked.", scene="stairwell", you=you(1400, 1450, "scared", y=880), intensity=.9, sfx=[["rattle", .5]])
b("So you rip the fire extinguisher off the wall, and you swing.", scene="stairwell", you=you(1400, 1450, "push", y=880), intensity=1, sfx=[["whoosh", .6], ["crash", 1.2]])
b("You hit the lobby running, and go straight through the glass door.", scene="stairwell", you=you(1500, 1900, "run", y=880), glass=True, efx=["shake"], intensity=1, sfx=[["crash", 1.2]])

# ---------------- 3. HIGHWAY
b("Seven A.M. The highway out of the city is one giant parking lot. Ten thousand cars. Nobody's moving.", scene="highway", chapter=["3", "THE HIGHWAY"], clock="7:00 AM", pan=[0, 300], you=you(300, 500, "idle", y=760), intensity=.5,
  cards=[C("10,000 CARS", "thousand"), C("0 MPH", "nobody", c=R)], sfx=[["engine", .3]])
b("Car doors hang open. Engines still running. People left everything and ran.", scene="highway", pan=[300, 300], you=you(500, 560, "think", y=760), intensity=.5, sfx=[["engine", .2]])
b("Somewhere behind you, a truck horn is stuck on. Nobody is left to let go of it.", scene="highway", pan=[300, 300], you=you(560, pose="scared", y=760), intensity=.6, sfx=[["engine", .2]])
b("And the dead are walking between the lanes.", scene="highway", pan=[300, 500], you=you(500, pose="scared", y=760), zz=Z(9, 900, 700, y=960, s=.55, spread=900), intensity=.8, sfx=[["groan", .3]])
b("So you run across the roofs. Car to car to car.", scene="highway", pan=[500, 1400], hop=True, you=you(420, 1500, "run", y=760), zz=Z(9, 700, 900, y=960, s=.55, spread=900), efx=["speed"], intensity=1, sfx=[["bang", .3], ["bang", .9], ["bang", 1.5], ["bang", 2.1]])
b("Then a car alarm goes off under your feet. A hundred and twenty decibels.", scene="highway", pan=[1400, 1450], alarm=True, you=you(900, pose="scared", y=760), zz=Z(12, 300, 600, y=960, s=.55, spread=1300), intensity=1,
  cards=[C("CAR ALARM: 120 dB", "hundred", c=R)], sfx=[["rattle", .1], ["sting", .5]])
b("Every head on the highway turns toward you.", scene="highway", pan=[1450, 1450], alarm=True, you=you(900, pose="scared", y=760), zz=Z(16, 200, 650, y=960, s=.55, spread=1500), efx=["shake"], intensity=1, sfx=[["groan", .2]])
b("You've got maybe forty seconds before they reach you.", scene="highway", pan=[1450, 1450], alarm=True, you=you(900, pose="scared", y=760), zz=Z(16, 300, 700, y=960, s=.55, spread=1500), intensity=1, cards=[C("40 SECONDS", "forty", c=R)], sfx=[["tick", .2], ["tick", 1.0], ["tick", 1.8]])
choice("highway", "Steal the motorcycle next to you? Or keep going on foot?", "Steal the motorcycle", "Keep going on foot")
b("If you took the motorcycle, the keys aren't in it. You lose forty seconds. That's all they need.", scene="highway", stamp="wrong", pan=[1450, 1450], bike=True, you=you(900, pose="scared", y=890), zz=Z(16, 500, 800, y=960, s=.55, spread=900), intensity=1, sfx=[["sputter", .3], ["groan", 2.2]])
b("Engines are loud. On a silent highway, an engine is a dinner bell.", scene="paper", paper={"title": "NOISE = DANGER", "lines": ["SILENT CITY", ["ENGINE = DINNER BELL", "#c0392b"], "QUIET BEATS FAST"], "src": "in a quiet city, engine noise carries for blocks"})
b("If you kept going on foot, good move. You drop off the side of the road, and down into the subway.", scene="highway", stamp="right", pan=[1450, 1700], you=you(900, 1700, "run", y=760, y1=1100), zz=Z(16, 400, 700, y=960, s=.55, spread=900), intensity=.9, sfx=[["whoosh", 1.5]])
b("Ten seconds after you disappear down the stairs, the first of them reaches the car where you were standing.", scene="highway", pan=[1700, 1700], alarm=True, zz=Z(16, 700, 1100, y=960, s=.55, spread=1300), intensity=.8, sfx=[["groan", .4]])

# ---------------- 4. SUBWAY
b("Eight thirty. The subway is pitch black. Your flashlight is the only light underground.", scene="subway", chapter=["4", "THE SUBWAY"], clock="8:30 AM", pan=[0, 300], you=you(500, 700, "idle", y=880), intensity=.6, sfx=[["tick", .5], ["steps", 1.5]])
b("Somewhere in the dark, water is dripping. And every drop sounds like footsteps.", scene="subway", pan=[300, 300], you=you(700, pose="scared", y=880), intensity=.7, sfx=[["tick", .3], ["tick", 1.1], ["tick", 1.9], ["steps", 2.6]])
b("Then your flashlight catches something on the tracks ahead. It's moving. It's a rat. Hundreds of them. All running the same way.", scene="subway", pan=[300, 300], rats=True, you=you(700, pose="scared", y=880), intensity=.7, sfx=[["scrape", .8]])
b("Then you hear it. A train. Running on its own. Nobody driving.", scene="subway", pan=[300, 300], you=you(700, pose="scared", y=880), train="far", intensity=.8, sfx=[["engine", .4]])
b("You press flat against the wall as it screams past, three inches from your face.", scene="subway", pan=[300, 300], you=you(700, pose="scared", y=880), train="pass", efx=["shake", "sparks"], intensity=1, sfx=[["engine", 0], ["scrape", .5], ["whoosh", 1.0]])
b("In the windows, you see faces. Pressed against the glass. Not one of them is blinking.", scene="subway", pan=[300, 300], you=you(700, pose="scared", y=880), train="pass", efx=["shake"], intensity=1, sfx=[["engine", 0], ["groan", 1.5]])
b("Down here, the rail next to the tracks carries over six hundred volts. One step on it, and it's over.", scene="paper", paper={"title": "THE THIRD RAIL", "lines": ["600-750 VOLTS", ["ALWAYS ON", "#c0392b"], "NEVER STEP ON IT"], "src": "subway third rails typically carry about 600-750 volts DC"})
b("Then the tunnel splits.", scene="subway", pan=[300, 600], split=True, you=you(700, 900, "think", y=880), intensity=.6, sfx=[["tick", .3]])
choice("subway", "Follow the tracks? Or follow the rats along the ledge?", "Follow the tracks", "Follow the rats along the ledge")
b("If you followed the tracks, a second train comes. And there's nowhere to stand but the third rail.", scene="subway", stamp="wrong", pan=[600, 600], train="pass", you=you(900, pose="scared", y=880), efx=["shake", "sparks"], intensity=1, sfx=[["engine", 0], ["crash", 1.6]])
b("Six hundred volts or a train. There's no good way out of that tunnel.", scene="subway", stamp="wrong", pan=[600, 600], you=you(900, pose="scared", y=880), efx=["sparks"], intensity=1, sfx=[["crash", .5]])
b("If you followed the rats, good move. Rats run from danger, and they always know the way up.", scene="subway", stamp="right", pan=[600, 1100], rats=True, you=you(600, 1300, "run", y=700), intensity=.7, sfx=[["steps", 0]])
b("Two hundred yards later, daylight through a grate. A ladder. Up.", scene="subway", pan=[1100, 1300], rats=True, you=you(900, 1300, "run", y=700), intensity=.5, sfx=[["steps", 0], ["rattle", 2.0]])

# ---------------- 5. HOSPITAL
b("Ten A.M. The tunnel comes up under City Hospital.", scene="hospital", chapter=["5", "THE HOSPITAL"], clock="10:00 AM", you=you(200, 500, "idle"), flicker=True, intensity=.6, sfx=[["static", .5]])
b("The emergency room doors are wide open. Gurneys everywhere. Nobody behind the desk.", scene="hospital", you=you(500, 700, "think"), flicker=True, intensity=.6, sfx=[["static", .3]])
b("Your arm is cut from the glass door. Out here, one infected cut can kill you.", scene="paper", paper={"title": "WHY YOU NEED MEDICINE", "lines": ["BEFORE ANTIBIOTICS:", ["A SMALL CUT COULD KILL", "#c0392b"], "CLEAN IT. COVER IT."], "src": "before penicillin (1940s), infected wounds were a leading cause of death"})
b("The lights flicker. And at the end of the corridor stands a surgeon. Still in his mask.", scene="hospital", you=you(500, pose="scared"), surgeon=1500, flicker=True, intensity=.9, sfx=[["static", .3], ["groan", 2.0]])
b("He runs at you. You kick a gurney straight down the hall into him.", scene="hospital", you=you(500, 560, "point"), surgeon=1200, gurney=[600, 1150], efx=["shake"], intensity=1, sfx=[["scrape", .4], ["crash", 1.6]])
b("He goes down. He doesn't stay down. You don't wait to see more.", scene="hospital", you=you(560, 900, "run"), surgeon=1350, intensity=1, sfx=[["groan", .5], ["steps", 1.2]])
choice("hospital", "The pharmacy? Or the blood bank?", "The pharmacy", "The blood bank")
b("If you picked the blood bank, the smell of blood wakes up the whole ward. They come out of every room.", scene="hospital", stamp="wrong", you=you(800, pose="scared"), zz=Z(10, 1700, 1100, spread=700, turn=True), flicker=True, intensity=1, sfx=[["groan", .2], ["groan", 1.5]])
b("Ten doors. Ten of them. And you're standing in the middle of the hall.", scene="hospital", stamp="wrong", you=you(800, pose="scared"), zz=Z(12, 1500, 950, spread=900, turn=True), flicker=True, efx=["shake"], intensity=1, sfx=[["groan", .2]])
b("If you picked the pharmacy, good move. Antibiotics, bandages, painkillers. You clean the cut, and you go.", scene="hospital", stamp="right", pharmacy=True, you=you(900, 1100, "idle"), intensity=.6, sfx=[["rattle", .5]])
b("The right way to treat a cut out here. Clean it with clean water. Press to stop the bleeding. Cover it. Change it every day.", scene="paper", paper={"title": "WOUND CARE", "lines": ["1. CLEAN IT", "2. PRESS IT", ["3. COVER IT", "#1f7a3a"]], "src": "basic first aid for minor cuts and scrapes"})

# ---------------- 6. MALL
b("Halfway. Five moves down. If you got all five right, you're already doing better than most of this city.", scene="paper", paper={"title": "HALFWAY CHECK", "lines": [["5 / 10 MOVES", "#2a2622"], "HOW MANY DID", ["YOU GET RIGHT?", "#c0392b"]], "src": "keep count - your final score is at the end"})
b("Noon. The mall. Every exit is chained shut, but the sports store is wide open.", scene="mall", chapter=["6", "THE MALL"], clock="12:00 PM", pan=[0, 400], you=you(300, 700, "run"), intensity=.6, sfx=[["steps", 0]])
b("You grab gloves, a helmet, and a bottle of water from a cooler that still feels cold.", scene="mall", pan=[400, 400], you=you(700, pose="point"), intensity=.5, cards=[C("GLOVES", "gloves"), C("HELMET", "helmet"), C("WATER", "water", c=G)], sfx=[["rattle", .5]])
b("Then the escalator starts moving. And it's full of them.", scene="mall", pan=[400, 400], escalator=True, you=you(700, pose="scared"), zz=Z(7, 1500, 1250, y=900, s=.55, spread=500, turn=True), intensity=.9, sfx=[["engine", .2], ["groan", 1.0]])
b("They tumble down the steps on top of each other. Twenty of them. And more behind.", scene="mall", pan=[400, 400], escalator=True, you=you(700, 600, "scared"), zz=Z(9, 1450, 1150, y=900, s=.55, spread=500, turn=True), efx=["shake"], intensity=1, cards=[C("20+", "twenty", c=R)], sfx=[["crash", .5], ["groan", 1.5]])
b("A person can run about six miles an hour. On a bike, you can do fifteen.", scene="paper", paper={"title": "SPEED MATH", "lines": ["RUNNING: ~6 MPH", ["BIKE: ~15 MPH", "#1f7a3a"], "THE DEAD: AS FAST AS YOU"], "src": "typical jogging and casual cycling speeds"})
choice("mall", "Grab a bike? Or a skateboard?", "Grab a skateboard", "Grab a bike")
b("If you took the skateboard, the wheels catch on broken glass, and you go flying.", scene="mall", stamp="wrong", pan=[400, 600], board=True, you=you(700, 900, "scared"), zz=Z(7, 1300, 1000, s=.55, spread=500, turn=True), efx=["shake"], intensity=1, sfx=[["scrape", .3], ["crash", 1.3]])
b("You hit the tile hard. And by the time you look up, they're already on you.", scene="mall", stamp="wrong", pan=[600, 600], you=you(900, pose="scared"), zz=Z(9, 1300, 1050, s=.55, spread=500, turn=True), intensity=1, sfx=[["groan", .3]])
b("If you took the bike, good move. You ride it straight through the food court, and out the loading dock.", scene="mall", stamp="right", pan=[600, 1800], bike=True, you=you(400, 1500, "run"), zz=Z(7, 900, 1200, s=.55, spread=600, turn=True), efx=["speed"], intensity=1, sfx=[["whoosh", .2], ["crash", 2.5]])
b("Behind you, the food court tables go flying as they chase. But on two wheels, you are gone.", scene="mall", pan=[1800, 2200], bike=True, you=you(600, 1700, "run"), zz=Z(9, 500, 700, s=.55, spread=600, turn=True), efx=["speed"], intensity=1, sfx=[["crash", .5], ["whoosh", 1.8]])
b("The loading dock door is jammed halfway. You duck flat on the handlebars and slide right under it.", scene="mall", pan=[2200, 2400], bike=True, you=you(900, 1800, "run"), efx=["speed"], intensity=1, sfx=[["scrape", .6], ["whoosh", 1.5]])

# ---------------- 7. ROOFTOPS
b("Three P.M. The streets are blocked, so you go up. Roof to roof.", scene="rooftops", chapter=["7", "THE ROOFTOPS"], clock="3:00 PM", rx=[200, 900], intensity=.9, sfx=[["steps", 0], ["steps", 1.2]])
b("From up here, you can see the whole city. Smoke in every direction. And one helicopter circling a tower downtown.", scene="rooftops", rx=[900, 900], chasers=0, intensity=.5, cards=[C("1 HELICOPTER", "helicopter", c=Y)], sfx=[["engine", 1.5]])
b("You clear one gap. Then another.", scene="rooftops", rx=[900, 2300], chasers=6, intensity=1, sfx=[["whoosh", .3], ["bang", .9], ["whoosh", 1.7], ["bang", 2.3]])
b("Twice, your foot slips on loose gravel. Twice, you catch yourself.", scene="rooftops", rx=[2000, 2300], chasers=4, intensity=1, sfx=[["scrape", .4], ["scrape", 1.8]])
b("Then the next gap is twelve feet. With a bag on your back, you'll make eight. Maybe.", scene="rooftops", rx=[2300, 2560], bigGap=True, intensity=.9, cards=[C("GAP: 12 FT", "twelve", c=R), C("YOUR JUMP: ~8 FT", "eight", c=Y)])
choice("rooftops", "Jump it anyway? Or use the window cleaner's rope across the gap?", "Jump it anyway", "Use the window cleaner's rope")
b("If you jumped, you hit the far wall, and you hang by your fingertips. Right above them.", scene="rooftops", stamp="wrong", rx=[2560, 2560], bigGap=True, hang=True, intensity=1, sfx=[["crash", .2], ["groan", 1.5]])
b("Your fingers slip one at a time. And sixty feet below, they're waiting with their arms up.", scene="rooftops", stamp="wrong", rx=[2560, 2560], bigGap=True, hang=True, intensity=1, sfx=[["groan", .5]])
b("If you took the rope, good move. Hand over hand, over sixty feet of nothing.", scene="rooftops", stamp="right", rx=[2560, 2560], bigGap=True, rope=True, intensity=.9, sfx=[["rattle", .3]])
b("Your arms are shaking when you reach the other side. But you're across. And they're not.", scene="rooftops", rx=[3100, 3500], chasers=0, intensity=.6, sfx=[["steps", .5]])

# ---------------- 8. BRIDGE
b("Five P.M. The river bridge. The only way across. And it's packed. A thousand dead, shoulder to shoulder.", scene="bridge", chapter=["8", "THE BRIDGE"], clock="5:00 PM", you=you(250, 400, "idle", y=640), zz=Z(20, 900, 800, y=640, s=.42, spread=1000, turn=True), intensity=.8,
  cards=[C("1,000 DEAD", "thousand", c=R)], sfx=[["groan", 1.0]])
b("Cars bumper to bumper. And between them, every one of the dead is facing your way.", scene="bridge", you=you(400, pose="scared", y=640), zz=Z(20, 800, 700, y=640, s=.42, spread=1000, turn=True), intensity=.9, sfx=[["groan", .5]])
choice("bridge", "Push through on the bridge? Or jump into the river?", "Push through the bridge", "Jump into the river")
b("If you pushed through, you make it forty feet. Then hands grab your bag, and pull you down.", scene="bridge", stamp="wrong", you=you(550, pose="scared", y=640), zz=Z(20, 500, 600, y=640, s=.42, spread=900), intensity=1, sfx=[["groan", .3], ["scream", 2.0]])
b("A thousand of them. One of you. The bridge was never a path. It was a trap.", scene="bridge", stamp="wrong", zz=Z(24, 550, 600, y=640, s=.42, spread=900), intensity=1, sfx=[["groan", .3]])
b("If you jumped, good move. Feet first. Arms crossed. Body straight.", scene="bridge", stamp="right", dive=True, you=you(450, 520, "cheer", y=640, y1=1050), zz=Z(20, 900, 800, y=640, s=.42, spread=1000, turn=True), intensity=1, sfx=[["whoosh", .2], ["crash", 1.4]])
b("You hit the water like a pencil. It's so cold, it punches the air right out of your lungs.", scene="bridge", swim=True, you=you(560, 620, "idle", y=1000), intensity=.9, sfx=[["crash", .1], ["cough", 2.0]])
b("Cold water has a rule. One minute to control your breathing. Ten minutes before your arms quit. One hour before you pass out.", scene="paper", paper={"title": "THE 1-10-1 RULE", "lines": [["1 MIN - BREATHE", "#c0392b"], "10 MIN - ARMS QUIT", "1 HOUR - PASS OUT"], "src": "cold water immersion: the 1-10-1 principle"})
b("You float. You breathe. And you let the current carry you to the far bank.", scene="bridge", swim=True, you=you(500, 1500, "idle", y=1000), zz=Z(20, 900, 850, y=640, s=.42, spread=1000, turn=True), intensity=.5, sfx=[["whoosh", .5]])
b("You crawl out on the far bank, soaked and freezing. Wet clothes pull heat out of your body way faster than air.", scene="bridge", swim=True, you=you(1500, 1700, "idle", y=1000), intensity=.5, sfx=[["cough", .5]])
b("Water steals your body heat about twenty five times faster than air. So you wring out every layer, and you keep moving.", scene="paper", paper={"title": "WET = COLD", "lines": ["WATER PULLS HEAT", ["~25x FASTER", "#c0392b"], "THAN AIR"], "src": "water conducts heat roughly 25 times faster than air"})
b("Behind you, on the bridge, a thousand heads watch you go. Not one of them follows you into the water.", scene="bridge", zz=Z(20, 900, 850, y=640, s=.42, spread=1000, turn=True), intensity=.5, sfx=[["groan", .8]])

# ---------------- 9. CHECKPOINT
b("Seven P.M. Searchlights. A military checkpoint. Soldiers checking everyone for bites.", scene="checkpoint", chapter=["9", "THE CHECKPOINT"], clock="7:00 PM", you=you(300, 650, "idle"), intensity=.6, sfx=[["engine", .3]])
b("A soldier with a megaphone. Hands where we can see them. One at a time.", scene="checkpoint", you=you(650, pose="cheer"), intensity=.7, sfx=[["static", .2]])
b("You have a scratch on your arm. From the glass. Not a bite. But they can't know that.", scene="checkpoint", you=you(650, pose="scared"), scratch=True, intensity=.8, cards=[C("SCRATCH ≠ BITE", "scratch", c=Y)])
b("The soldier's flashlight stops on your arm.", scene="checkpoint", you=you(650, pose="scared"), scratch=True, intensity=.9, sfx=[["sting", .3]])
choice("checkpoint", "Tell them about the scratch? Or hide it?", "Hide the scratch", "Tell them the truth")
b("If you hid it, they find it anyway. To them, hidden means bitten. The gate closes in your face.", scene="checkpoint", stamp="wrong", gate="close", you=you(650, pose="scared"), intensity=1, sfx=[["bang", 1.5]])
b("Through the fence, you can see the tents, the lights, the hot food. And you're on the wrong side of it.", scene="checkpoint", stamp="wrong", gate="closed", you=you(650, pose="scared"), intensity=.9, sfx=[["groan", 2.0]])
b("If you told them, good move. The medic checks it, cleans it, and waves you through.", scene="checkpoint", stamp="right", gate="open", medic=True, you=you(650, 1300, "run"), intensity=.6, sfx=[["ding", 1.2]])
b("Behind the fence, tents, lights, hot food. And a sign. Last helicopter, nine P.M.", scene="checkpoint", gate="open", you=you(1300, 1500, "point"), intensity=.6, cards=[C("LAST HELICOPTER: 9 PM", "nine", c=R)])
b("You look at your watch. Eight fifty. You run.", scene="checkpoint", gate="open", clock="8:50 PM", you=you(1300, 1900, "run"), efx=["speed"], intensity=1, sfx=[["tick", .2], ["steps", .8]])

# ---------------- 10. HELIPAD
b("Ten floors of stairs. Your legs are burning. Then the roof door.", scene="stairwell", chapter=["10", "THE HELIPAD"], clock="8:58 PM", you=you(400, 1500, "run", y=430, y1=430), efx=["speed"], intensity=1, sfx=[["steps", 0], ["steps", 1.2], ["bang", 2.6]])
b("Eight fifty nine P.M. The roof of the evacuation tower. The last helicopter is already lifting.", scene="helipad", clock="8:59 PM", heli="lift", you=you(300, 500, "run"), intensity=1, efx=["wind"], sfx=[["engine", 0]])
b("And the stairwell door bursts open behind you. Five hundred of them.", scene="helipad", heli="lift", you=you(500, 650, "run"), zz=Z(16, -300, 150, spread=600), efx=["wind", "shake"], intensity=1, sfx=[["crash", .3], ["groan", .9]])
choice("helipad", "Jump for the ladder? Or wait for the next helicopter?", "Wait for the next one", "Jump for the ladder")
b("If you waited, there is no next one.", scene="helipad", stamp="wrong", heli="gone", you=you(900, pose="scared"), zz=Z(16, 300, 650, spread=600), efx=["wind"], intensity=1, sfx=[["groan", .3]])
b("The sound of the rotors fades. And all five hundred of them turn to look at you.", scene="helipad", stamp="wrong", heli="gone", you=you(900, pose="scared"), zz=Z(16, 500, 750, spread=600), intensity=1, sfx=[["groan", .5]])
b("If you jumped, good move. Your fingers close around the last rung. And the city falls away beneath you.", scene="helipad", stamp="right", heli="away", ladder=True, intensity=.8, efx=["wind"], sfx=[["whoosh", .3], ["reveal", 2.5]])
b("For one second, the ladder swings out over nothing but fire. You don't let go.", scene="helipad", heli="away", ladder=True, efx=["wind"], intensity=.9, sfx=[["whoosh", .2]])
b("You made it.", scene="helipad", heli="sky", intensity=.4, sfx=[["reveal", .2]])
b("Below you, the city goes dark, one block at a time. Twenty four hours. Ten moves. And you're still breathing.", scene="helipad", heli="sky", intensity=.4, sfx=[["engine", .3]])

# ---------------- SCORE
b("Now count your moves. Ten out of ten, you're a legend. Seven or more, you survived. Under five, you'd be one of them.", scene="score", intensity=.5, sfx=[["ding", .5], ["ding", 2.5], ["ding", 4.5]])
b("Comment your score. And subscribe, because your next move is coming.", scene="score", cta=True, intensity=.4, sfx=[["reveal", .3]])
b("And tell me which move almost got you.", scene="score", cta=True, intensity=.3)

json.dump({"series": "Your Move", "episode": 1, "day": 1, "title": "Your Move: Escape the City Before It Falls", "lesson": "", "vertical": True, "style": "stick", "lead": .2,
           "speeds": {"deep": 1.0}, "fps": 60, "crf": 17, "width": 1920, "height": 1080, "mix": {"music": .06, "ambience": .035}, "beats": B},
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "script.json"), "w"), indent=1)
print(len(B), "beats,", sum(len(x["text"].split()) for x in B), "words")

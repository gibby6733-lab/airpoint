"""YOUR MOVE: SURVIVE THE MOUNTAIN — 10 min, 16:9 (1920x1080), stick-man style. Plane crash in the Rockies, 10 choices,
both outcomes shown, a real survival fact after each. New co-survivor: Maya (flight attendant). Cold open = the wolves."""
import json, os
B = []
CLOCK = {"v": "4:12 PM"}
def b(text="", sp="deep", **kw):
    if "clock" in kw: CLOCK["v"] = kw["clock"]
    B.append({"sp": sp if text else "", "text": text, "clock": CLOCK["v"], **{k: v for k, v in kw.items() if k != "clock"}})
def C(t, w=None, **o): return {"t": t, "w": w, **o}
def you(x0, x1=None, pose="idle", y=900, flip=False, s=.72, y1=None): return {"x0": x0, "x1": x0 if x1 is None else x1, "y0": y, "y1": y if y1 is None else y1, "pose": pose, "flip": flip, "s": s}
def P(x0, x1=None, pose="idle", flip=False, y=900): return {"x0": x0, "x1": x1, "pose": pose, "flip": flip, "y": y}
R, G, Y = "#ff5a4a", "#7cd67c", "#ffe14a"
M = dict(scene="mountain")
def choice(bg, q, o1, o2, **kw):
    b(f"Your move. {q}", scene="choice", bg=bg, opt1=o1, opt2=o2, intensity=.6, sfx=[["sting", .05]], **kw)
    b("", hold=2.6, scene="choice", bg=bg, opt1=o1, opt2=o2, countdown=True, sfx=[["tick", 0], ["tick", .87], ["tick", 1.73]], **kw)
WOLF_NIGHT = dict(tod="night", trees=9, snow=.25, wind=.4)

# ---------------- COLD OPEN (flash-forward to chapter 9)
b("Night three. Twelve wolves. One fire. And it's burning out.", **M, **WOLF_NIGHT, clock="2:00 AM", camp=[960, 1], campLvl=.5, wolves={"n": 7, "r0": 760, "r1": 560, "walk": True},
  you=you(780, pose="scared"), pal=P(1140, pose="scared", flip=True), intensity=1, cards=[C("12 WOLVES", "twelve", c=R, big=True), C("FIRE: DYING", "burning", c=Y, big=True)], sfx=[["bark", .3], ["bark", 1.8]])
b("The biggest one steps into the light. And Maya whispers. Don't run.", **M, **WOLF_NIGHT, camp=[960, 1], campLvl=.45, wolves={"n": 7, "r0": 560, "r1": 450},
  you=you(780, pose="scared"), pal=P(1140, pose="scared", flip=True), intensity=1, rewind=True, cards=[C("DON'T RUN", "run", c=R, big=True)], sfx=[["bark", .6], ["sting", 2.0]])
b("Four days earlier, you were on a plane.", scene="title", intensity=.5, sfx=[["whoosh", .1], ["reveal", .8]])
b("This is Your Move. Ten choices. Pause the video, pick your move, and keep count. Get them right, and you walk off this mountain.", scene="title", intensity=.4, sfx=[["tick", 2.0]])

# ---------------- 1. THE PLANE
b("Flight two eleven. Thirty eight thousand feet over the Rocky Mountains. You're halfway through a movie.", scene="cabin", chapter=["1", "THE PLANE"], clock="4:12 PM", you=you(560, pose="idle", y=880, s=.6), intensity=.4,
  cards=[C("38,000 FT", "thirty")], sfx=[["engine", .2]])
b("Ladies and gentlemen, we've lost an engine. Please return to your seats and fasten your seatbelts.", sp="radio", scene="cabin", storm=True, tilt=.02, alarm=True, you=you(560, pose="scared", y=880, s=.6), intensity=.7, sfx=[["static", 0], ["sting", .8]])
b("Then the second engine goes quiet. And the oxygen masks drop.", scene="cabin", storm=True, tilt=.05, alarm=True, masks=.35, you=you(560, pose="scared", y=880, s=.6), efx=["shake"], intensity=1,
  cards=[C("0 ENGINES", "second", c=R, big=True)], sfx=[["sputter", .2], ["sting", 1.6]])
b("Out the window there are no clouds anymore. Just trees. Getting closer, fast.", scene="cabin", storm=True, tilt=.06, alarm=True, masks=0, you=you(560, pose="scared", y=880, s=.6), efx=["shake"], intensity=1, cards=[C("TREES", "trees", c=R)], sfx=[["whoosh", .3]])
b("Heads down! Brace! Brace! Brace!", sp="mags", scene="cabin", storm=True, tilt=.06, alarm=True, masks=0, pal=P(1350, pose="point", flip=True, y=880), you=you(560, pose="scared", y=880, s=.6), efx=["shake"], intensity=1, sfx=[["scream", .4]])
b("Your bag is right above you. Your phone, your jacket, everything you brought.", scene="cabin", storm=True, tilt=.05, alarm=True, masks=0, you=you(560, pose="think", y=880, s=.6), intensity=.9, cards=[C("YOUR BAG", "bag", c=Y)], sfx=[["rattle", .3]])
choice("cabin", "Grab your bag? Or get your head down?", "Grab your bag from the bin", "Head down and brace")
b("If you grabbed your bag, you're standing when the plane hits the trees. You don't remember the next hour.", scene="cabin", stamp="wrong", storm=True, alarm=True, impact=.45, you=you(560, pose="point", y=880, s=.6), efx=["shake"], intensity=1, sfx=[["crash", 1.4]])
b("In a crash, the brace position protects your head from flying debris and the seat in front of you. Bags can be replaced. Heads can't.", scene="paper",
  paper={"title": "BRACE POSITION", "lines": ["HEAD DOWN", "HANDS ON YOUR HEAD", ["BAGS CAN WAIT", "#c0392b"]], "src": "FAA passenger safety guidance on brace positions"})
b("If you braced, good move. You feel the belly of the plane scrape the treetops. Then the whole world goes white.", scene="cabin", stamp="right", storm=True, alarm=True, impact=.55, you=you(560, pose="think", y=880, s=.6), efx=["shake"], intensity=1, sfx=[["scrape", .5], ["crash", 2.2]])

# ---------------- 2. THE WRECK
b("You wake up face down in the snow. The plane is in two pieces. And the back half is on fire.", **M, tod="day", chapter=["2", "THE WRECK"], clock="4:40 PM", wreck=[1250, .9], burn=True, snow=.15, you=you(380, pose="scared"), intensity=.8,
  cards=[C("2 PIECES", "pieces", c=Y), C("FIRE", "fire", c=R)], sfx=[["crash", .2], ["whoosh", 2.0]])
b("Someone is still inside. The flight attendant. Maya.", **M, tod="day", wreck=[1250, .9], burn=True, snow=.15, you=you(380, 980, "run"), intensity=.9, cards=[C("MAYA", "maya", c=Y)], sfx=[["steps", 0]])
b("You drag her out by the jacket, ten seconds before the fuel tank goes up.", **M, tod="day", wreck=[1250, .9], burn=True, snow=.15, you=you(980, 520, "run", flip=True), pal=P(1060, 600, "scared", True), efx=["shake"], intensity=1,
  cards=[C("10 SECONDS", "ten", c=R)], sfx=[["bang", 2.6], ["crash", 2.8]])
b("Thank you. I'm Maya. Is anyone else...?", sp="mags", **M, tod="day", wreck=[1250, .9], burn=True, snow=.15, you=you(520, pose="idle"), pal=P(640, pose="talk", flip=True), intensity=.5)
b("Her leg is cut. Not deep, but she can only limp.", **M, tod="day", wreck=[1250, .9], burn=True, snow=.15, you=you(520, pose="think"), pal=P(640, pose="scared", flip=True), intensity=.5, cards=[C("MAYA: HURT LEG", "leg", c=R)])
b("You check what you have. A lighter. A water bottle. And from the plane's emergency kit, one red flare. Remember that flare.", **M, tod="day", wreck=[1250, .9], burn=True, snow=.15, you=you(520, pose="point"), pal=P(640, pose="idle", flip=True), intensity=.5,
  cards=[C("LIGHTER", "lighter"), C("WATER BOTTLE", "water"), C("1 FLARE", "flare", c=Y)], sfx=[["rattle", .3]])
b("Nobody else. Just the two of you, somewhere in the mountains. And the sun goes down in one hour.", **M, tod="dusk", wreck=[1250, .9], burn=True, snow=.2, you=you(520, pose="think"), pal=P(640, pose="scared", flip=True), intensity=.6,
  cards=[C("JUST YOU TWO", "two", c=Y), C("SUNSET: 1 HOUR", "sun", c=R)])
b("Far below, you think you can see a road. Maybe. It's a long way down.", **M, tod="dusk", wreck=[1250, .9], snow=.2, you=you(520, pose="point"), pal=P(640, pose="idle", flip=True), intensity=.5, cards=[C("ROAD?", "road", c=Y)])
choice("mountain", "Walk down the mountain to find help? Or stay with the wreck?", "Walk down to find help", "Stay with the wreck", tod="dusk", wreck=[1250, .9])
b("If you walked, night catches you halfway down. In the dark, every slope looks the same. You're lost, and nobody knows where to look.", **M, stamp="wrong", tod="night", trees=6, snow=.35, tracks=900, you=you(300, 1100, "run"), pal=P(200, 1000, "run"), intensity=.9, sfx=[["sting", 0]])
b("In the morning, rescuers reach the wreck in twenty minutes. It takes them three days to find you.", **M, stamp="wrong", tod="dawn", wreck=[1250, .9], heli=[1500, 1300, 200, 220, .45], intensity=.6, sfx=[["engine", .3]])
b("Search teams look for the wreck first. From the air, a plane is huge. A person is a dot.", scene="paper",
  paper={"title": "STAY WITH THE WRECK", "lines": ["A PLANE IS BIG", "A PERSON IS A DOT", ["STAY WITH THE WRECK", "#c0392b"]], "src": "standard aviation search and rescue advice"})
b("If you stayed, good move. The front half still has walls and a roof. That's your shelter tonight.", **M, stamp="right", tod="dusk", wreck=[1250, .9], snow=.2, you=you(700, 900, "point"), pal=P(560, 820, "idle"), intensity=.5)

# ---------------- 3. THE THIRST
b("Night one. Your lips are cracking. You haven't had a drink since the plane.", **M, tod="night", chapter=["3", "THE THIRST"], clock="11:00 PM", wreck=[1350, .9], camp=[700, .8], snow=.15, you=you(520, pose="think"), pal=P(880, pose="idle", flip=True), intensity=.4,
  cards=[C("THIRSTY", "lips", c=R)])
b("And you're sitting on a mountain made of water.", **M, tod="night", wreck=[1350, .9], camp=[700, .8], snow=.15, you=you(520, pose="point"), pal=P(880, pose="idle", flip=True), intensity=.4, cards=[C("SNOW = WATER?", "water", c=Y)])
b("We could just eat the snow, right?", sp="mags", **M, tod="night", wreck=[1350, .9], camp=[700, .8], snow=.15, you=you(520, pose="idle"), pal=P(880, pose="talk", flip=True), intensity=.4)
choice("mountain", "Eat the snow? Or melt it first?", "Eat the snow", "Melt it by the fire", tod="night", wreck=[1350, .9], camp=[700, .8])
b("If you ate it, your body burns its own heat to melt every mouthful. Ten minutes later, you're shaking. Hard.", **M, stamp="wrong", tod="night", wreck=[1350, .9], camp=[700, .5], snow=.2, you=you(520, pose="scared"), pal=P(880, pose="scared", flip=True), efx=["shake"], intensity=.8,
  cards=[C("SHIVERING", "shaking", c=R)])
b("Eating snow lowers your body temperature and costs you energy you can't spare. Always melt it first.", scene="paper",
  paper={"title": "THE SNOW RULE", "lines": ["EATING SNOW", ["STEALS BODY HEAT", "#c0392b"], "MELT IT FIRST"], "src": "wilderness survival guidance on hypothermia"})
b("If you melted it, good move. A water bottle from the plane, held over the fire. Warm water. The best thing you've ever tasted.", **M, stamp="right", tod="night", wreck=[1350, .9], camp=[700, 1], snow=.15, you=you(600, pose="cheer"), pal=P(880, pose="idle", flip=True), intensity=.4, sfx=[["ding", .4]])
b("The rule of threes. Three hours without shelter in this cold. Three days without water. You've solved both. For now.", **M, tod="night", wreck=[1350, .9], camp=[700, 1], snow=.15, you=you(600, pose="idle"), pal=P(880, pose="idle", flip=True), intensity=.4,
  cards=[C("3 HOURS: SHELTER", "hours", c=G), C("3 DAYS: WATER", "days", c=G)])

b("Somewhere far off, something howls. Then another. Maya pretends she didn't hear it.", **M, tod="night", wreck=[1350, .9], camp=[700, .9], snow=.15, trees=5, you=you(600, pose="scared"), pal=P(880, pose="scared", flip=True), intensity=.7, sfx=[["bark", .8], ["bark", 2.2]])
# ---------------- 4. THE SIGNAL
b("Morning. Day two. You hear it before you see it. An engine. A search helicopter.", **M, tod="day", chapter=["4", "THE SIGNAL"], clock="8:15 AM", wreck=[1350, .9], heli=[2100, 1500, 180, 160, .28], you=you(520, pose="point"), pal=P(760, pose="scared", flip=True), intensity=.7,
  cards=[C("HELICOPTER", "helicopter", c=G)], sfx=[["engine", .2]])
b("It's high. It's fast. And it's about to fly right past you.", **M, tod="day", wreck=[1350, .9], heli=[1500, 900, 160, 150, .28], you=you(520, pose="scared"), pal=P(760, pose="scared", flip=True), intensity=.8, sfx=[["engine", 0]])
b("Wave! Make them see us!", sp="mags", **M, tod="day", wreck=[1350, .9], heli=[900, 600, 150, 150, .28], you=you(520, pose="scared"), pal=P(760, pose="cheer", flip=True), intensity=.8)
b("You have maybe thirty seconds before it's over the next ridge and gone.", **M, tod="day", wreck=[1350, .9], heli=[700, 500, 150, 150, .28], you=you(520, pose="think"), pal=P(760, pose="cheer", flip=True), intensity=.9, cards=[C("30 SECONDS", "thirty", c=R)], sfx=[["tick", .5], ["tick", 1.5]])
choice("mountain", "Build three signal fires? Or jump, wave and scream?", "Build three signal fires", "Jump, wave and scream", tod="day", wreck=[1350, .9])
b("If you waved, you're a dot in the snow, waving its arms. From the air, you look like a rock. The helicopter flies on.", **M, stamp="wrong", tod="day", wreck=[1350, .9], heli=[600, -300, 150, 120, .28], you=you(520, pose="cheer"), pal=P(760, pose="cheer", flip=True), intensity=.6, sfx=[["engine", .3]])
b("Three of anything is the signal for distress. Three fires. Three whistles. Three piles of rocks. And on snow, dark smoke stands out.", scene="paper",
  paper={"title": "THE SIGNAL", "lines": ["3 OF ANYTHING", ["= HELP", "#c0392b"], "DARK SMOKE ON WHITE SNOW"], "src": "internationally recognized distress signals"})
b("If you built three fires and threw seat foam on them for black smoke, good move. The helicopter banks. It circles once. It saw you.", **M, stamp="right", tod="day", three="lit", heli=[1500, 900, 200, 160, .4], you=you(380, pose="cheer"), pal=P(1450, pose="cheer", flip=True), intensity=.8,
  cards=[C("THEY SAW YOU", "saw", c=G, big=True)], sfx=[["engine", .3]])
b("Maya runs to the cockpit radio. It crackles to life.", **M, tod="day", wreck=[1350, .9], you=you(520, pose="idle"), pal=P(760, 1150, "run"), intensity=.5, sfx=[["static", .5]])
b("Survivors spotted. Storm incoming. Earliest rescue is forty eight hours.", sp="radio", **M, tod="storm", wreck=[1350, .9], snow=.3, wind=.6, you=you(520, pose="scared"), pal=P(1150, pose="scared"), intensity=.8,
  cards=[C("48 HOURS", "forty", c=R, big=True)], sfx=[["static", 0], ["thunder", 2.4]])

# ---------------- 5. THE STORM
b("The storm hits like a wall. Sixty mile an hour winds. You can't see your own feet.", **M, tod="storm", chapter=["5", "THE STORM"], clock="1:30 PM", wreck=[1350, .9], snow=1, wind=1.2, white=.45, you=you(520, pose="scared"), pal=P(700, pose="scared", flip=True), efx=["shake"], intensity=1,
  cards=[C("60 MPH WIND", "sixty", c=R)], sfx=[["thunder", .3], ["whoosh", 1.5]])
b("The wreck is groaning in the wind. Three hundred yards away, there's a line of trees. Real shelter.", **M, tod="storm", wreck=[1350, .9], trees=8, snow=1, wind=1.2, white=.35, you=you(520, pose="point"), pal=P(700, pose="scared", flip=True), intensity=.9,
  cards=[C("TREES: 300 YARDS", "three", c=Y)], sfx=[["scrape", .4]])
choice("mountain", "Walk to the trees through the whiteout? Or dig in where you are?", "Walk to the trees", "Dig in and wait", tod="storm", wreck=[1350, .9], snow=1, white=.4)
b("If you walked, you walk for an hour. And end up right back at the wreck. You walked in a circle.", **M, stamp="wrong", tod="storm", wreck=[1350, .9], snow=1, wind=1.2, white=[.4, .75], tracks=1400, you=you(300, 1200, "run"), pal=P(200, 1100, "run"), intensity=.9)
b("And you've burned an hour of body heat you'll never get back.", **M, stamp="wrong", tod="storm", wreck=[1350, .9], snow=1, wind=1.2, white=.6, you=you(1200, pose="scared"), pal=P(1050, pose="scared"), intensity=.8)
b("In a whiteout, people walk in circles. With no landmarks, nobody walks straight. Scientists have actually tested it.", scene="paper",
  paper={"title": "WHITEOUT", "lines": ["NO LANDMARKS", ["= YOU WALK IN CIRCLES", "#c0392b"], "STAY PUT"], "src": "Souman et al., Current Biology (2009): people walk in circles without visual cues"})
b("If you dug in, good move. A trench in the snow behind the wreck, lined with seat cushions. Snow is one of the best insulators on Earth.", **M, stamp="right", tod="storm", wreck=[1350, .9], snow=.9, wind=1, white=.3, you=you(620, pose="push"), pal=P(820, pose="push", flip=True), intensity=.6,
  cards=[C("SNOW = INSULATION", "insulators", c=G)])
b("At midnight, Maya stops talking. Her lips are blue. And she's stopped shivering.", **M, tod="storm", snow=.9, wind=1, white=.3, wreck=[1350, .9], you=you(620, pose="scared"), pal=P(820, pose="idle", flip=True), intensity=.9, cards=[C("STOPPED SHIVERING", "shivering", c=R)], sfx=[["sting", 1.2]])
b("Shivering is your body fighting the cold. When it stops, the fight is being lost. You pull her close and share your heat until she starts shaking again.", scene="paper",
  paper={"title": "HYPOTHERMIA", "lines": ["SHIVERING = FIGHTING BACK", ["NO SHIVERING = DANGER", "#c0392b"], "SHARE BODY HEAT"], "src": "medical first-aid guidance on hypothermia"})
b("The storm screams all night. By morning, the wreck is gone. Buried under six feet of snow.", **M, tod="dawn", snow=.2, you=you(620, pose="scared"), pal=P(820, pose="scared", flip=True), intensity=.6,
  cards=[C("6 FT OF SNOW", "six", c=R)], sfx=[["sting", .4]])

b("Quick check. Halfway through. If you're five for five, don't get cocky. Chapter eight gets almost everybody.", scene="title", intensity=.4, sfx=[["tick", .5], ["sting", 3.0]])
# ---------------- 6. THE SLOPE
b("Day three. The radio is buried with the wreck. If you want to be found, you have to get lower. Down to the valley.", **M, tod="day", chapter=["6", "THE SLOPE"], clock="7:40 AM", slope=True, ridge=True, you=you(1300, pose="think"), pal=P(1480, pose="idle", flip=True), intensity=.5)
b("Straight down the open slope is twenty minutes. Along the rocky ridge, it's two hours.", **M, tod="day", slope=True, ridge=True, you=you(1300, pose="point", flip=True), pal=P(1480, pose="idle", flip=True), intensity=.5,
  cards=[C("SLOPE: 20 MIN", "twenty", c=Y), C("RIDGE: 2 HOURS", "two", c=Y)])
b("The slope's faster. I'm freezing. Let's go.", sp="mags", **M, tod="day", slope=True, ridge=True, you=you(1300, pose="idle"), pal=P(1480, pose="talk", flip=True), intensity=.5)
choice("mountain", "The fast open slope? Or the long ridge?", "The fast open slope", "The long ridge", tod="day", slope=True, ridge=True)
b("If you took the slope, halfway down you hear a crack. Like a gunshot. Then the whole hill starts to move.", **M, stamp="wrong", tod="day", slope=True, avalanche=[.45, 1], you=you(700, 1300, "run"), pal=P(560, 1150, "run"), efx=["shake"], intensity=1, sfx=[["crash", 2.4], ["thunder", 2.6]])
b("You dive behind a boulder. The snow roars past for ten seconds. Then silence. Maya is gone.", **M, stamp="wrong", tod="day", slope=True, snow=.6, you=you(900, pose="scared"), efx=["shake"], intensity=1, sfx=[["thunder", .2], ["sting", 3.0]])
b("Most avalanches happen on slopes between thirty and forty five degrees. And fresh snow from a storm makes it far worse.", scene="paper",
  paper={"title": "AVALANCHE FACT", "lines": ["30 TO 45 DEGREE SLOPES", ["FRESH SNOW = DANGER", "#c0392b"], "STAY ON THE RIDGES"], "src": "avalanche safety centers (e.g. avalanche.org)"})
b("If you took the ridge, good move. Two hours in, you hear the crack anyway. And watch the slope you almost took slide away below you.", **M, stamp="right", tod="day", slope=True, ridge=True, avalanche=[.4, 1], you=you(1350, pose="point", flip=True), pal=P(1520, pose="scared", flip=True), intensity=.9, sfx=[["thunder", 1.8]])

b("We would have been under that.", sp="mags", **M, tod="day", slope=True, ridge=True, snow=.3, you=you(1350, pose="scared", flip=True), pal=P(1520, pose="talk", flip=True), intensity=.6)
# ---------------- 7. THE RIVER
b("By noon, you reach the valley floor. And a frozen river blocks the way.", **M, tod="day", chapter=["7", "THE RIVER"], clock="12:10 PM", river=True, trees=7, you=you(420, pose="idle", y=1000), pal=P(600, pose="idle", flip=True, y=1000), intensity=.5)
b("The ice looks solid. It's twenty steps across. On the other side, the forest looks a lot like a way out.", **M, tod="day", river=True, trees=7, you=you(420, pose="point", y=1000), pal=P(600, pose="idle", flip=True, y=1000), intensity=.5,
  cards=[C("20 STEPS", "twenty", c=Y)])
b("My leg can't do two more hours of this.", sp="mags", **M, tod="day", river=True, trees=7, you=you(420, pose="idle", y=1000), pal=P(600, pose="talk", flip=True, y=1000), intensity=.5)
choice("mountain", "Follow the river downstream? Or walk across the ice?", "Follow the river downstream", "Walk across the ice", tod="day", river=True, trees=7)
b("If you crossed, step fifteen goes straight through. The water is so cold it knocks the air out of your lungs.", **M, stamp="wrong", tod="day", river=True, crack=[.2, .5], hole=.5, crackX=1000, trees=7, you=you(700, 1000, "scared", y=905), efx=["shake"], intensity=1,
  cards=[C("THIN ICE", "fifteen", c=R)], sfx=[["crash", 1.4], ["scream", 1.6]])
b("Ice over moving water is thinner, and you can't tell by looking. You need at least four inches of solid ice. And remember the cold water rule. One minute of shock. Ten before your arms quit.", scene="paper",
  paper={"title": "THE ICE RULE", "lines": ["4 INCHES MINIMUM", ["RIVER ICE = THIN ICE", "#c0392b"], "1 MIN SHOCK • 10 MIN ARMS"], "src": "ice safety guidance (e.g. Minnesota DNR) + cold-water 1-10-1 principle"})
b("If you followed the river, good move. Rivers run downhill. And downhill is where people live.", **M, stamp="right", tod="day", river=True, trees=7, tracks=1600, you=you(300, 1300, "run", y=1000), pal=P(150, 1150, "run", y=1000), intensity=.6,
  cards=[C("DOWNHILL = PEOPLE", "downhill", c=G)])
b("An hour later, you find old tire tracks along the bank, half filled with snow. Somebody drove here. Once.", **M, tod="day", river=True, trees=7, tracks=1800, you=you(900, pose="point", y=1000), pal=P(1080, pose="cheer", flip=True, y=1000), intensity=.5, cards=[C("TIRE TRACKS", "tire", c=G)])
b("But by sunset, there's still no town. And it's starting to snow again.", **M, tod="dusk", river=True, trees=7, snow=.4, you=you(1100, pose="scared", y=1000), pal=P(1280, pose="scared", flip=True, y=1000), intensity=.6)

# ---------------- 8. THE CAVE
b("You find a cave in the rocks. Out of the wind. Maya almost cries.", scene="cave", chapter=["8", "THE CAVE"], clock="6:30 PM", you=you(560, pose="idle"), pal=P(720, pose="cheer"), intensity=.4, sfx=[["whoosh", .2]])
b("Your legs feel like concrete. Your stomach stopped growling yesterday. That's not a good sign. But it's not the thing that kills you.", scene="cave", you=you(560, pose="scared"), pal=P(720, pose="idle"), intensity=.5)
b("You can survive about three weeks without food. Cold and thirst will get you long before hunger does.", scene="paper",
  paper={"title": "THE RULE OF THREES", "lines": ["3 HOURS WITHOUT SHELTER", "3 DAYS WITHOUT WATER", ["3 WEEKS WITHOUT FOOD", "#c0392b"]], "src": "the survival rule of threes (rough guide)"})
b("And the cave goes deep. It's warmer further in. Way warmer.", scene="cave", you=you(720, pose="point"), pal=P(560, pose="idle"), intensity=.5, cards=[C("WARMER INSIDE?", "warmer", c=Y)])
choice("cave", "Sleep deep inside the cave? Or stay by the entrance with a fire?", "Go deep inside", "Stay by the entrance with a fire")
b("If you went deep, that warm air is coming from something breathing. Something big. And it just woke up.", scene="cave", stamp="wrong", bear="wake", wakeAt=.55, you=you(1150, 900, "scared"), pal=P(1000, 760, "scared"), efx=["shake"], intensity=1,
  cards=[C("BEAR", "big", c=R, big=True)], sfx=[["sting", 2.2], ["scream", 3.0]])
b("You back out slowly, never turning your back on it. It doesn't follow you. This time.", scene="cave", stamp="wrong", bear="wake", wakeAt=0, you=you(760, 420, "scared", flip=True), pal=P(640, 320, "scared", True), intensity=.9, sfx=[["sting", .5]])
b("Warm, quiet caves are exactly where bears sleep through winter. Stay near the entrance, where you can see out and get out.", scene="paper",
  paper={"title": "THE CAVE RULE", "lines": ["WARM CAVE?", ["IT MIGHT BE TAKEN", "#c0392b"], "STAY BY THE EXIT"], "src": "wildlife safety guidance"})
b("If you stayed by the entrance, good move. Fire in the cave mouth, smoke drifting out, warmth bouncing off the rock. You sleep for the first time in two days.", scene="cave", stamp="right", camp=[640, 1], you=you(820, pose="idle"), pal=P(960, pose="idle"), intensity=.3)
b("Then, at two in the morning, Maya shakes you awake. Eyes. Outside. A lot of eyes.", scene="cave", camp=[640, .7], you=you(820, pose="scared"), pal=P(960, pose="point", flip=True), intensity=.9, cards=[C("EYES", "eyes", c=R, big=True)], sfx=[["sting", .2], ["bark", 3.0]])

# ---------------- 9. THE WOLVES
b("Twelve wolves. One fire. And it's burning out. You've seen this before.", **M, **WOLF_NIGHT, chapter=["9", "THE WOLVES"], clock="2:00 AM", camp=[960, 1], campLvl=.5, wolves={"n": 7, "r0": 760, "r1": 560, "walk": True},
  you=you(780, pose="scared"), pal=P(1140, pose="scared", flip=True), intensity=1, cards=[C("12 WOLVES", "twelve", c=R)], sfx=[["bark", .4], ["bark", 2.0]])
b("The biggest one steps into the light.", **M, **WOLF_NIGHT, camp=[960, 1], campLvl=.45, wolves={"n": 7, "r0": 560, "r1": 450}, you=you(780, pose="scared"), pal=P(1140, pose="scared", flip=True), intensity=1, sfx=[["bark", .8]])
b("Don't run. Please. Don't run.", sp="mags", **M, **WOLF_NIGHT, camp=[960, 1], campLvl=.45, wolves={"n": 7, "r0": 450, "r1": 440}, you=you(780, pose="scared"), pal=P(1140, pose="talk", flip=True), intensity=1)
b("Their breath steams in the firelight. You can hear them breathing.", **M, **WOLF_NIGHT, camp=[960, 1], campLvl=.45, wolves={"n": 7, "r0": 440, "r1": 420}, you=you(780, pose="scared"), pal=P(1140, pose="scared", flip=True), intensity=1, sfx=[["bark", 1.6]])
choice("mountain", "Stand tall and make noise? Or run for the trees?", "Stand tall and make noise", "Run for the trees", **WOLF_NIGHT, camp=[960, 1], wolves={"n": 7, "r0": 450, "r1": 450})
b("If you ran, you just told twelve hunters you're prey. Wolves chase whatever runs. And in deep snow, they are much faster than you.", **M, stamp="wrong", **WOLF_NIGHT, camp=[960, .4], wolves={"n": 7, "r0": 450, "r1": 160, "walk": True}, you=you(780, 200, "run", flip=True), pal=P(1140, 300, "run", True), intensity=1, sfx=[["bark", .3], ["bark", 1.0], ["scream", 2.4]])
b("Never run from a predator. Make yourself big, make noise, and keep the fire between you. Wolf attacks on people are rare. Running makes one far more likely.", scene="paper",
  paper={"title": "THE PREDATOR RULE", "lines": [["NEVER RUN", "#c0392b"], "LOOK BIG • MAKE NOISE", "KEEP THE FIRE BETWEEN YOU"], "src": "wildlife agency guidance on wolf encounters"})
b("If you stood your ground, good move. You throw the last branch on the fire, raise your arms, and roar. Maya bangs two pieces of the plane together.", **M, stamp="right", **WOLF_NIGHT, camp=[960, 1], campLvl=1, wolves={"n": 7, "r0": 450, "r1": 620}, you=you(780, pose="cheer"), pal=P(1140, pose="cheer", flip=True), intensity=1,
  sfx=[["bang", 2.6], ["bang", 3.0], ["bang", 3.4]])
b("It lasts eleven minutes. The longest eleven minutes of your life.", **M, **WOLF_NIGHT, camp=[960, 1], campLvl=1, wolves={"n": 7, "r0": 620, "r1": 640}, you=you(780, pose="cheer"), pal=P(1140, pose="cheer", flip=True), intensity=.8, cards=[C("11 MINUTES", "eleven", c=Y)], sfx=[["bark", 1.4]])
b("One by one, the eyes slide back into the dark.", **M, **WOLF_NIGHT, camp=[960, 1], wolves={"n": 7, "r0": 620, "r1": 1100, "walk": True}, you=you(780, pose="idle"), pal=P(1140, pose="idle", flip=True), intensity=.5)

# ---------------- 10. THE FLARE
b("Day four. Dawn. You have one thing left from the plane. A single emergency flare.", **M, tod="dawn", chapter=["10", "THE FLARE"], clock="6:50 AM", trees=6, you=you(800, pose="point"), pal=P(980, pose="idle", flip=True), intensity=.5,
  cards=[C("1 FLARE", "single", c=Y, big=True)])
b("Then you hear it. Rotors. Far away, somewhere behind the ridge.", **M, tod="dawn", trees=6, you=you(800, pose="scared"), pal=P(980, pose="point", flip=True), intensity=.8, sfx=[["engine", .4]])
b("Light it! Light it now!", sp="mags", **M, tod="dawn", trees=6, you=you(800, pose="scared"), pal=P(980, pose="talk", flip=True), intensity=.9)
choice("mountain", "Light the flare now? Or wait until you can see the helicopter?", "Light it now", "Wait until you see it", tod="dawn", trees=6)
b("If you lit it now, a hand flare burns for about a minute. The helicopter clears the ridge two minutes later. Your flare is ash.", **M, stamp="wrong", tod="dawn", trees=6, flare=[880, 600], you=you(800, pose="cheer"), pal=P(980, pose="cheer", flip=True), intensity=.8, sfx=[["sting", 3.0]])
b("You hear it pass overhead, behind the trees. You scream until your voice cracks. It never sees you.", **M, stamp="wrong", tod="dawn", trees=6, heli=[1200, -200, 120, 100, .3], you=you(800, pose="cheer"), pal=P(980, pose="scared", flip=True), intensity=.8, sfx=[["engine", 0]])
b("A hand flare burns for about one minute. Save it until the aircraft can actually see you.", scene="paper",
  paper={"title": "THE FLARE RULE", "lines": ["ONE FLARE", ["= ONE MINUTE", "#c0392b"], "WAIT UNTIL YOU SEE THEM"], "src": "maritime and aviation signaling guidance"})
b("If you waited, good move. The helicopter clears the ridge. You light the flare and hold it over your head. Bright red light. Red smoke.", **M, stamp="right", tod="dawn", trees=6, flare=[880, 600], heli=[2200, 1300, 220, 260, .55], you=you(800, pose="cheer"), pal=P(980, pose="cheer", flip=True), intensity=1,
  sfx=[["engine", 0], ["whoosh", 2.4]])
b("It turns. It's coming straight for you.", **M, tod="dawn", trees=6, flare=[880, 600], heli=[1300, 960, 260, 300, .7, 0, True], you=you(800, pose="cheer"), pal=P(980, pose="cheer", flip=True), intensity=1, sfx=[["engine", 0]])
b("Fifty seconds of flare left. Forty. The pilot dips the nose.", **M, tod="dawn", trees=6, flare=[880, 600], heli=[960, 960, 300, 300, .75, 0, True], you=you(800, pose="cheer"), pal=P(980, pose="cheer", flip=True), intensity=1, cards=[C("0:40", "forty", c=R)], sfx=[["engine", 0]])
b("We see you. Hold your position. We're coming down.", sp="radio", **M, tod="day", trees=6, heli=[960, 960, 300, 300, .75, 300, True], you=you(800, pose="cheer"), pal=P(980, pose="cheer", flip=True), intensity=.8, sfx=[["static", 0]])
b("A rescuer drops down on a cable, grabs Maya first, then you. The ground falls away below your boots.", **M, tod="day", trees=6, heli=[960, 960, 300, 260, .75, 320], you=you(960, 960, "hang", y=900, y1=700), intensity=.8, sfx=[["engine", 0], ["whoosh", 2.0]])
b("Maya grabs your hand and yells over the rotors. Your move. Every single time.", sp="mags", **M, tod="day", heli=[960, 1100, 260, 200, .75], intensity=.5)
b("You made it. Four days. Ten moves. Two people walked off that mountain.", **M, tod="day", trees=6, heli=[960, 1500, 300, 160, .75], intensity=.4, sfx=[["reveal", .2]])

b("Back home, the news calls it a miracle. It wasn't a miracle. It was ten good moves.", scene="title", intensity=.4, sfx=[["reveal", .4]])
# ---------------- SCORE
b("Now count your moves. Ten out of ten, you're a legend. Seven or more, you survived. Under five, you're wolf food.", scene="score", intensity=.5, sfx=[["ding", .5], ["ding", 2.5], ["ding", 4.5]])
b("Comment your score. And subscribe, because your next move is coming.", scene="score", cta=True, intensity=.4, sfx=[["reveal", .3]])
b("And tell me which move almost got you.", scene="score", cta=True, intensity=.3)

json.dump({"series": "Your Move", "episode": 2, "day": 2, "title": "Your Move: Survive the Mountain", "lesson": "", "vertical": True, "style": "stick", "lead": .2,
           "theme": "mountain", "titleText": "SURVIVE THE MOUNTAIN", "titleSub": "10 MOVES • 4 DAYS", "badLabel": "WOLF FOOD",
           "speeds": {"deep": 1.0}, "fps": 30, "crf": 17, "width": 1920, "height": 1080, "mix": {"music": .06, "ambience": .035}, "beats": B},
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "script.json"), "w"), indent=1)
print(len(B), "beats,", sum(len(x["text"].split()) for x in B), "words")

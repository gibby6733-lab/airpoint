import sys, soundfile as sf
from kokoro_onnx import Kokoro
K = "kokoro/"
k = Kokoro(K + "kokoro-v1.0.onnx", K + "voices-v1.0.bin")
LINES = [
 "April fourteenth, nineteen twelve. The North Atlantic. Everyone blames the iceberg... but the iceberg was only the last link, in a chain of seven failures.",
 "Failure one: speed. Titanic was running at about twenty-two knots, at night, through waters she'd been warned were full of ice. That was standard practice. Keep your speed... and trust the lookouts.",
 "Failure two: the warnings. Six ice warnings came in that day. But the radio operators were buried in passengers' private messages. A warning of ice dead ahead never reached the bridge. And when the Californian tried one last time, she was told: Shut up. I am busy.",
 "Failure three: no binoculars. An officer was moved off the crew just before sailing... and he kept the key to the binocular locker. So the lookouts searched the dark with their bare eyes.",
 "Failure four: seen too late. There was no moon. The sea was flat as glass, with no waves breaking at the iceberg's base to give it away. At eleven forty p.m., the lookout rang the bell. Thirty-seven seconds. The ship turned... just enough to scrape. Not enough to miss.",
 "Failure five: weak rivets. There was no giant gash. In the curved bow, workers had hammered in iron rivets by hand, some full of slag. Under the strain, their heads snapped, and the plates sprang apart. About twelve square feet of openings... was all it took.",
 "Failure six: short bulkheads. Titanic could stay afloat with four compartments flooded. The iceberg opened five. And the walls between them stopped short of the top. As the bow sank, water spilled over each one... like an ice cube tray.",
 "Failure seven: the lifeboats. Twenty boats, for two thousand, two hundred and twenty-four people. Seats for barely half... and that was perfectly legal. The first boat lowered carried about twenty-eight people. It had room for sixty-five.",
 "And one more. Help was in sight. The Californian sat stopped in the ice, maybe ten to twenty miles away. Her crew saw the rockets. Her radio operator... had gone to bed.",
 "Two twenty a.m. Two hours and forty minutes after the collision, Titanic was gone. The rescue ship Carpathia arrived after dawn. More than fifteen hundred people died. Only about seven hundred and ten survived.",
 "So why did the Titanic really sink? Not one mistake. A chain of them. And it changed the sea for good: lifeboats for everyone, a twenty-four hour radio watch... and an Ice Patrol that still tracks icebergs today.",
]
voice = sys.argv[1] if len(sys.argv) > 1 else "bm_george"
for i, t in enumerate(LINES):
    a, sr = k.create(t, voice=voice, speed=0.92, lang="en-gb")
    sf.write(f"narr/{i:02d}.wav", a, sr)
    print(i, round(len(a) / sr, 2))

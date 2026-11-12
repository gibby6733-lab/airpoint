"""Add a flash-forward cold open + rewind to a built episode (run AFTER build_audio.py).

usage: python3 cold_open.py <episode_dir> <scene> <start_word>
  Copies the line with that scene to the front of the video, from <start_word> (minus 1 s) to the end of the line,
  then a short reversed-audio "rewind" before the real start. Keeps timeline_main.json / audio_main.wav as the originals,
  so you can re-run it after rebuilding. The engine shows the REWIND effect (line flag "rewind") and hides the HUD
  during the cold open (line flag "cold"). Adds ~3-4.5 s: aim the narration at ~62-66 s so the total lands at 60-70 s.
"""
import copy, json, os, shutil, subprocess, sys
d, scene, word = sys.argv[1], sys.argv[2], sys.argv[3].lower()
tm, am = os.path.join(d, "timeline_main.json"), os.path.join(d, "audio_main.wav")
if not os.path.exists(tm) or os.path.getmtime(os.path.join(d, "timeline.json")) > os.path.getmtime(tm) + 1:
    shutil.copy(os.path.join(d, "timeline.json"), tm); shutil.copy(os.path.join(d, "audio.wav"), am)   # fresh build
t = json.load(open(tm)); o = next(l for l in t["lines"] if l["scene"] == scene)
w0 = next(w["s"] for w in o["words"] if w["w"].lower().strip(".,!?'\"").startswith(word))
A, B = w0 - 1.0, o["end"] + .25; LEAD, GAP = .1, .55; D = LEAD + (B - A) + GAP; sh = LEAD - A
c = copy.deepcopy(o); c["start"] += sh; c["end"] = c["start"] + (o["end"] - o["start"])
c["words"] = [dict(w, s=round(w["s"] + sh, 3)) for w in o["words"] if w["s"] >= A - .05]
c["sfx_times"] = [[n, round(s + sh, 3)] for n, s in o.get("sfx_times", []) if s >= A]; c.update(cold=True, rewind=True, text=" ".join(w["w"] for w in c["words"]))
for l in t["lines"]:
    l["start"] = round(l["start"] + D, 3); l["end"] = round(l["end"] + D, 3)
    l["words"] = [dict(w, s=round(w["s"] + D, 3)) for w in l["words"]]; l["sfx_times"] = [[n, round(s + D, 3)] for n, s in l.get("sfx_times", [])]
t["lines"].insert(0, c); t["duration"] = round(t["duration"] + D, 3)
json.dump(t, open(os.path.join(d, "timeline.json"), "w"), indent=1)
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", am, "-filter_complex",
    f"[0:a]atrim={A}:{B},asetpts=PTS-STARTPTS,adelay={int(LEAD * 1000)}:all=1[c];[0:a]atrim={B - 1.1}:{B},asetpts=PTS-STARTPTS,areverse,atempo=2.0,volume=0.8,apad=whole_dur={GAP}[r];"
    "[0:a]asetpts=PTS-STARTPTS[o];[c][r][o]concat=n=3:v=0:a=1[out]", "-map", "[out]", os.path.join(d, "audio.wav")], check=True)
print(f"cold open: {scene} from '{word}' ({B - A:.1f}s) | new duration {t['duration']:.1f}s")

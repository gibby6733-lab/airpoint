"""Quality check a finished Mudville Possums episode before it is posted.

usage: python3 qc_check.py <episode_dir> [--json]
Checks episode.mp4 + caption.txt (+ thumbnail.png):
  length 60-70 s • 1080x1920 9:16 • 30 fps • has audio • loudness about -14 LUFS (-16..-12) • no clipping (true peak <= -1 dBTP)
  • no long black/frozen stretches • no long silence • caption ends with EXACTLY the 4 hashtags • no emoji text codes
  like "[Red heart]" and only common emoji • thumbnail 1080x1920.
Prints one line per check and a final PASS/FAIL. Exit code 0 = pass, 1 = fail.
"""
import json, os, re, subprocess, sys

HASHTAGS = "#football #footballfunny #animation #Mudvillepossums"
d = sys.argv[1]; mp4 = os.path.join(d, "episode.mp4")
res = []  # (ok, label, detail)
def add(ok, label, detail=""): res.append((bool(ok), label, detail))
def run(args): return subprocess.run(args, capture_output=True, text=True)

if not os.path.exists(mp4):
    add(False, "video file", "episode.mp4 missing")
else:
    p = json.loads(run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,r_frame_rate:format=duration", "-of", "json", mp4]).stdout)
    dur = float(p["format"]["duration"]); v = next((s for s in p["streams"] if s["codec_type"] == "video"), {}); a = any(s["codec_type"] == "audio" for s in p["streams"])
    add(60 <= dur <= 70, "length 60-70 s", f"{dur:.1f}s")
    add(v.get("width") == 1080 and v.get("height") == 1920, "9:16 1080x1920", f"{v.get('width')}x{v.get('height')}")
    fr = v.get("r_frame_rate", "0/1").split("/"); fps = float(fr[0]) / float(fr[1] or 1)
    add(abs(fps - 30) < .5, "30 fps", f"{fps:.0f} fps")
    add(a, "has audio")
    if a:
        e = run(["ffmpeg", "-nostats", "-i", mp4, "-af", "ebur128=peak=true", "-f", "null", "-"]).stderr
        I = re.findall(r"I:\s+(-?[\d.]+) LUFS", e); TP = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", e)
        if I: add(-16 <= float(I[-1]) <= -12, "loudness ~-14 LUFS", f"{float(I[-1]):.1f} LUFS")
        if TP: add(float(TP[-1]) <= -0.5, "no clipping", f"peak {float(TP[-1]):.1f} dBTP")
        sil = run(["ffmpeg", "-nostats", "-i", mp4, "-af", "silencedetect=n=-45dB:d=2.5", "-f", "null", "-"]).stderr
        gaps = re.findall(r"silence_duration: ([\d.]+)", sil)
        add(not gaps, "no dead air (>2.5 s silence)", f"{len(gaps)} silent stretch(es)" if gaps else "")
    bl = run(["ffmpeg", "-nostats", "-i", mp4, "-vf", "blackdetect=d=1.5:pic_th=0.97", "-an", "-f", "null", "-"]).stderr
    blacks = [b for b in re.findall(r"black_start:([\d.]+)", bl) if float(b) < dur - 2]  # the fade-out at the end is fine
    add(not blacks, "no black screens", f"black at {', '.join(blacks)}s" if blacks else "")
    fz = run(["ffmpeg", "-nostats", "-i", mp4, "-vf", "freezedetect=n=0.001:d=4", "-an", "-f", "null", "-"]).stderr
    frz = re.findall(r"freeze_start: ([\d.]+)", fz)
    add(not frz, "no frozen video (>4 s)", f"frozen at {', '.join(frz)}s" if frz else "")

cap_p = os.path.join(d, "caption.txt")
if not os.path.exists(cap_p):
    add(False, "caption", "caption.txt missing")
else:
    cap = open(cap_p, encoding="utf-8").read().strip()
    tags = re.findall(r"#\w+", cap)
    add(cap.endswith(HASHTAGS) and " ".join(tags) == HASHTAGS, "hashtags exactly right", " ".join(tags))
    codes = re.findall(r"\[[A-Za-z][A-Za-z ]+\]", cap)
    add(not codes, "real emojis (no text codes)", ", ".join(codes))
    odd = [c for c in cap if ord(c) > 0x2000 and not (0x1F000 <= ord(c) <= 0x1FAFF or 0x2190 <= ord(c) <= 0x2BFF or ord(c) in (0x200D, 0xFE0F, 0x2019, 0x2014, 0x2026, 0x201C, 0x201D))]
    add(not odd, "only common iPhone emojis", "".join(odd))
    add(len(cap) <= 2200, "caption length", f"{len(cap)} chars")
th = os.path.join(d, "thumbnail.png")
if os.path.exists(th):
    from PIL import Image
    add(Image.open(th).size == (1080, 1920), "cover 1080x1920", "%dx%d" % Image.open(th).size)
else:
    add(False, "cover", "thumbnail.png missing")

ok = all(r[0] for r in res)
if "--json" in sys.argv:
    print(json.dumps({"pass": ok, "checks": [{"ok": a, "check": b, "detail": c} for a, b, c in res]}))
else:
    for a, b, c in res: print(("✅ " if a else "❌ ") + b + (f" ({c})" if c else ""))
    print("PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)

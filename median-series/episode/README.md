# S01E01 "Nothing Sells": picture-lock build (no voices yet)

- **Output:** 1920×1080, **60 fps**, about **14:53** (episode body 14:21 plus the 31.9s main title inserted after SC 02).
- **Dialogue:** on-screen subtitles timed from word count (natural pace) until real voices replace them.
- **Audio:** silent except the locked intro. Voices, SFX and music come **after picture approval**.

## How it's built
| File | Role |
|---|---|
| `ep101.html` | the episode page (renders any moment with `renderAt(t)`) |
| `engine.js` | timeline builder, character placement, camera, captions, inserts, wipes |
| `sets.js` | all locations (classroom, garage, mall, diner, gym, ValuBarn, Cube, etc.) and full-screen inserts |
| `ep101.js` | per-shot staging and every gag animation (filmstrip, siren, cash, riot, extinguisher, VOID+ ad, glowing box…) |
| `ep101_script.json/.js` | parsed from `05-episode-101-script.md` by `tools/parse_script.py` |
| `ep101_cues.json` | every shot and line with start/end time, the cue sheet for recording voices |

## Render
```
node tools/preview-shots.js <dir>                       # one still per shot, for review
node tools/render-episode.js <start> <end> <out.mp4> 60 # render a time range at 60 fps
episode/render/run.sh                                   # full parallel render (4 workers)
```
The final files (`episode/render/*.mp4`) are too large for git and are delivered separately.

## When voices are approved
1. Record each line in its locked voice (`voice-cast.md`).
2. Replace word-count timing with the real clip lengths in the timeline builder.
3. Re-render; the shots, gags and camera moves all re-time automatically.

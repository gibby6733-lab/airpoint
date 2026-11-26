# Gator Bend

Cutout-style animated shorts (vertical 1080x1920) rendered from a script file.
Original characters, set in the fictional town of Gator Bend, Florida.

## Pipeline

| Stage | What it does | File |
| --- | --- | --- |
| 1. Script | Beats: who talks, what they say, expression, pose, camera, reactions | `script.json` |
| 2. Voices + timing | Records each line (audio first), works out mouth shapes per frame and caption word timings | `scripts/make-voices.mjs` → `src/generated/timeline.json` |
| 3. Render | Remotion draws the paper cutout world, syncs mouths, moves the camera, burns in captions | `src/` |

### How the cutout look is built

- **Paper texture:** every shape is filled with procedural grain and fiber noise (`src/paper.tsx`).
- **Depth and shadows:** each card has a depth level (0–3). Higher cards cast larger, softer shadows, like paper stacked under a lamp.
- **Modular rig:** every kid is the same rig with swappable arm poses, eye directions, blinks, brows and 9 mouth shapes (`src/characters.tsx`).
- **Choppy motion:** characters and props change pose on twos (every 2nd frame) with no in-betweens. Walks are a side-to-side tilt plus a hop.
- **Camera:** `wide`, `two:a,b`, `close:x`, `push:x` (slow push-in), `close:gator`. Hard cuts between beats, like a sitcom.
- **Lighting:** a warm overhead hot-spot with falloff toward the corners.

## Commands

```bash
npm install
npm run voices    # script.json -> audio + timeline (run after every script edit)
npm run studio    # live preview in the browser
npm run render    # -> out/episode.mp4
```

On a normal computer, drop `--browser-executable=...` from the `render` script and Remotion will download its own browser.

## Voices

- **Default:** `espeak-ng`, free and offline, but robotic. Mouths follow the loudness of the audio.
- **ElevenLabs:** set `ELEVENLABS_API_KEY` and put a `elevenlabsVoiceId` on each cast member in `script.json`. This uses ElevenLabs' character timestamps, so mouths and captions follow the real timing. (This path is written but has not been run yet.)

## Not built yet

- Step 3 of the plan: trending topic → Claude/Grok writes a `script.json` automatically.
- Step 4 of the plan: auto-publish to YouTube or TikTok.
- More backgrounds, plus the adult cast (Hector, Mayor Fitch, etc.).

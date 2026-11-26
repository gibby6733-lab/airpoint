# Gator Bend

Cutout-style animated shorts (vertical 1080x1920) rendered from a script file.
Original characters, set in the fictional town of Gator Bend, Florida.

## Pipeline

| Stage | What it does | File |
| --- | --- | --- |
| 1. Script | Beats: who talks, what they say, expression, pose, camera, reactions | `script.json` |
| 2. Voices + timing | Records each line (audio first), times every word, picks a mouth shape for every sound, synthesizes the music and foley | `scripts/make-voices.mjs` (+ `align.py`, `make-music.py`) → `src/generated/timeline.json` |
| 3. Render | Remotion draws the paper cutout world, syncs mouths, moves the camera, burns in captions | `src/` |

### How the cutout look is built

- **Paper texture** (`src/paper.tsx`): every card has a scissor-cut edge (its silhouette is nudged by noise), a dyed-paper surface (blotchy color, grain, fibers), light flecks, and a pale rim along the cut edge.
- **Boil:** the cut edges are re-cut every 4 frames, so they shimmer slightly like hand-made animation.
- **Depth and shadows:** each card has a depth level (0–3). Higher cards cast larger, softer shadows, like paper stacked under a lamp.
- **Modular rig:** a huge round head sitting straight on a short bell-shaped body, stub arms, mitten hands and only the feet showing. Every kid is the same rig with swappable arm poses, eye directions, blinks, brows and 9 mouth shapes (`src/characters.tsx`).
- **Flat scenery:** background cards have no black outlines; only characters and props are inked.
- **Choppy motion:** characters and props change pose on twos (every 2nd frame) with no in-betweens. Walks are a side-to-side tilt plus a hop.
- **Camera:** `wide`, `two:a,b`, `close:x`, `push:x` (slow push-in), `close:gator`. Hard cuts between beats, like a sitcom.
- **Lighting:** a warm overhead hot-spot with falloff toward the corners.

### Lip-sync

`scripts/align.py` runs Whisper (`faster-whisper` base.en, free, offline) on each recorded line to find when every word was actually said. Each word is split into phonemes with `espeak-ng`, and each phoneme becomes a mouth shape:

| Mouth | Sounds |
| --- | --- |
| closed | m, b, p |
| F | f, v |
| O | oh, oo, w, r |
| wide | ah, eye, a |
| E | ee, s, z, sh, ch, th |
| open | everything else |

Mouths change on twos, like the rest of the animation. The recognizer also checks the voice: if a word in the script wasn't heard (say Kokoro garbled it), `npm run voices` prints `CHECK, not heard: ...`. Rewording the `text` usually fixes it; the `caption` can keep the original wording.

### Acting

- **Head turns:** face features slide toward whoever the character is looking at (the speaker, or `look` on the beat: a cast name, `gator` or `bus`).
- **Talking:** the head rocks on each new word, with a small lift.
- **Punch words:** an ALL-CAPS or `!` word in the caption triggers `emphasisPose` and a hop.
- **Reactions:** `reactions` sets listeners' expressions. Scared kids jump, then shake.
- **Sweat:** `"sweat": ["tucker"]` on a beat makes sweat fly off those kids.

### Sound

`scripts/make-music.py` synthesizes everything (Karplus-Strong plucked strings): an opening strum sting, a ukulele-style bed that ducks under dialogue, a title sting, footsteps on the walk-in, and the gator's chomp clacks.

### Opening titles

`src/Intro.tsx` opens every episode (7.5s): each kid slaps onto their own paper card with a name and tagline, then the gang hops into a line-up under the logo, someone shouts the title, and everyone turns to stare at Wade. Names, taglines, card colors, the shout line and the tagline under the logo live in the `intro` block of `script.json`. The jingle comes from `make-music.py`.

Compositions: `Episode` (intro + scene, the one you post), `Intro`, `Scene`.

## Commands

```bash
npm install
npm run voices    # script.json -> audio + timeline (run after every script edit)
npm run studio    # live preview in the browser
npm run render    # -> out/episode.mp4 (intro + scene)
```

On a normal computer, drop `--browser-executable=...` from the `render` script and Remotion will download its own browser.

## Voices

The voice stage uses the first engine available:

1. **ElevenLabs:** set `ELEVENLABS_API_KEY` and put an `elevenlabsVoiceId` on a cast member. This uses ElevenLabs' character timestamps, so mouths and captions follow the real timing. (This path is written but has not been run yet.)
2. **Kokoro-82M (default):** free neural voices that run offline, Apache-2.0 licensed. The adult voices are pitched up into cartoon kids with `rubberband`, which keeps the speed the same. Each kid's `kokoro` entry in `script.json` sets `voice` (one voice or a blend like `am_liam:0.6,af_nicole:0.4`), `speed` and `pitch`. One-time setup:
   ```bash
   python3 -m venv .venv && .venv/bin/pip install kokoro-onnx soundfile
   mkdir -p models/voices
   B=https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX/resolve/main
   curl -L -o models/kokoro.onnx $B/onnx/model.onnx
   for v in am_echo am_liam af_nicole am_puck am_onyx; do curl -L -o models/voices/$v.bin $B/voices/$v.bin; done
   .venv/bin/pip install faster-whisper   # lip-sync aligner; its model downloads on first run
   ```
   If Hugging Face downloads fail behind a proxy, set `HF_HUB_DISABLE_XET=1`.
3. **espeak-ng:** robotic last resort.

## Not built yet

- Step 3 of the plan: trending topic → Claude/Grok writes a `script.json` automatically.
- Step 4 of the plan: auto-publish to YouTube or TikTok.
- More backgrounds, plus the adult cast (Hector, Mayor Fitch, etc.).

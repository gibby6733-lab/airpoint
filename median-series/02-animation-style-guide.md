# MEDIAN — Animation Style Guide (v1.0)

> **Core visual idea: "Beige world, neon intrusions."**
> Median itself is drawn in a muted, slightly dusty palette: perfectly average, comfortable, a little sad. **Anything a corporation brings in (products, apps, AI, signs, ads) is drawn in hot, saturated neon** with a soft glow. The satire shows up visually before anyone speaks: you can always see what doesn't belong.

---

## 1. Look and feel

| Element | Rule |
|---|---|
| **Format** | Clean, flat 2D, **16:9 at 1920×1080, 24 fps**. Dialogue scenes are animated on twos (12 drawings per second); fast action is on ones. Shorts are reframed to 9:16 (see section 9). |
| **Line** | Characters: a 4 px warm near-black outline (#2B2118), plus a 3 px **white sticker rim** around the outside of the silhouette. Backgrounds: thinner 2 px lines in a darker version of the local color, *never black*. That separates characters from backgrounds. |
| **Shading** | Characters get **one flat shadow tone** (20% darker, multiplied) and no gradients. Backgrounds get a **subtle risograph-style grain texture plus soft halftone dots** in the shadows. |
| **Shapes** | Soft rounded rectangles, no sharp corners, except for corporate products, which are sleek, perfectly geometric and glossy. (That's the visual joke: Median is soft; corporations are sharp.) |
| **Perspective** | Mostly flat theatrical staging with simple depth layers (foreground, characters, midground, background). Cinematic angles are saved for comedy (low angles for Dex's grand moments, dramatic dolly-zooms for revelations, overhead shots for crowd chaos). |
| **Faces** | All acting comes from **eyebrows, eye shape and mouth**. Eyes are white ovals with dot pupils. Squash and stretch on heads for big reactions. |

### What it must NOT look like
- Not paper cutout or construction-paper textures. Those belong to another show.
- Not an anime-style or 3D-shaded look.
- No four kids in winter hats standing at a bus stop as a default composition.
- No gradient-heavy "AI art" look. If it looks like a generic AI image, it's off-model.

---

## 2. Color system

### The Median palette (town, everyday life)
| Token | Hex | Use |
|---|---|---|
| `median-beige` | #E8DCC2 | sky on overcast days, walls |
| `median-tan` | #C9B48F | buildings, roads, cardboard |
| `median-sage` | #A7B08A | grass, trees, school walls |
| `median-dusty-blue` | #8FA5B5 | sky, water, cars |
| `median-brick` | #A9644E | the school, Town Hall |
| `median-grey` | #8C8781 | pavement, shadows |
| `median-night` | #2F3550 | night sky |

### The intrusion palette (corporate, tech, test products ONLY)
| Token | Hex | Use |
|---|---|---|
| `neon-magenta` | #FF2E93 | consumer products and apps |
| `neon-cyan` | #22E5FF | AI, screens, tech |
| `neon-lime` | #B6FF3B | food and drink products |
| `neon-violet` | #9B5CFF | Aggregate Insights branding (also the Cube's glow at night) |
| `glow` | outer glow, 12 px, 60% opacity | applied to all neon objects |

**Rule:** a neon color *never* appears on a Median-native object. If a neon color is spreading onto houses, clothes or people, it means the test is taking over the town. Use that on purpose as an escalation signal in Act 2 and Act 3.

### Character colors
These are locked in `01-show-bible.md`, section 4. Kenzie's pink puffer is the *only* near-neon item on a main character, and it's deliberate: she is partly corporate already.

### Lighting presets (use these four; don't invent new ones per scene)
| Preset | Description |
|---|---|
| `DAY-FLAT` | Default. Soft, shadowless overcast light. Median is always slightly cloudy. |
| `GOLDEN` | Warm late-afternoon light, long shadows, for emotional beats only. |
| `NIGHT` | Deep blue ambient light with yellow porch lights and neon spill. |
| `MIRROR-ROOM` | Fluorescent, slightly green, with a buzzing tube. Used for Focus Fridays and Aggregate Insights interiors. |

---

## 3. Character animation rules
1. **On-model, always.** Proportions, colors and accessories never change mid-scene. Accessory checklist (check in every shot): Dex's headset, Wren's headphones, Marcus's fanny pack and earpiece, Gordy's hat, glasses and keys, Kenzie's phone and ring light, Tunk's loose overall strap and Object of the Week.
2. **Limited, well-timed animation.** The comedy comes from timing, not motion volume. Hold poses. Let a character stand still while someone else panics.
3. **The "Median Stare":** a full held beat (12–24 frames) of total stillness before or after a punchline. It's the show's comedic rhythm. Use it.
4. **Exaggerated takes are rare and huge.** A full squash-and-stretch freak-out happens at most two or three times an episode, which keeps them funny.
5. **Walk cycles:** one locked walk cycle per character, reused everywhere.
   - Dex: chin up, big stride, arms swinging like a CEO.
   - Wren: hands in pockets, slight slouch, steady pace.
   - Marcus: fast, short steps, checking his phone.
   - Gordy: a bouncy waddle, keys jangling (sound cue every step).
   - Kenzie: walking backward while filming herself.
   - Tunk: a slow, loose amble, occasionally stopping to pick something up.
6. **Lip sync:** a 9-shape mouth chart (rest, A/I, E, O, U, F/V, L, M/B/P, W/Q), lip-synced to the final voice track only, never to scratch audio.
7. **Blinks:** characters blink every 3–5 seconds. Wren blinks slower; Gordy blinks faster.

---

## 4. Camera language
| Shot | When to use it |
|---|---|
| **Wide establishing** | Start of every new location, 1–2 seconds, always with the same angle per location (locked "establishing plates"). |
| **Group two-shot or four-shot** | Default for gang conversations. Characters at the same eye level, framed by the line-up order. |
| **Single medium close-up** | Punchlines and character reactions. |
| **Slow push-in** | Someone realizes something terrible. |
| **Snap zoom (6 frames)** | A sudden revelation, always with a sound sting. |
| **Low angle** | Dex's "visionary" moments, and corporate villains. |
| **High overhead** | Crowd chaos, and the town seen as a "petri dish." |
| **Through the mirror** | From Frink's side of the Mirror Room, slightly tinted violet. This is the show's signature "they're watching" shot. |
| **Phone-screen POV** | Kenzie's footage: vertical frame inside the 16:9 frame, with captions and a follower counter. Easy to cut into Shorts. |

**Transitions:** hard cuts by default. The one signature transition is the **"Recall Wipe"**: a beige-and-violet striped bar wipes the screen with a quick siren chirp. It's used between acts and makes episodes recognizable.

---

## 5. Sound identity
- **Main theme:** a cheerful, *slightly too cheerful* 1970s civic marching-band tune with kazoo and glockenspiel, which gets distorted when things go wrong.
- **The Median Minute jingle:** a filmstrip-era jingle for exposition cutaways: *"♪ Median, Median, right in the middle! ♪"*, with a beep for each "slide" change.
- **The Recall Siren:** a civil-defense wail followed by a calm PA voice. It's the signature act-break sound.
- **Frink's clipboard:** a crisp pen click and scribble, the sound of being judged.
- **Gordy's keys:** a jingle on every step.
- **Room tone:** every location has a looping ambience (school hallway hum, diner fryer, the Cube's low electrical drone). Silence is used on purpose for awkward beats.

---

## 6. Typography and graphics
- **Show logo:** **MEDIAN** in a heavy rounded slab serif, beige with a dark outline, with the "I" replaced by a small **bell curve** icon.
- **On-screen text (signs, products):** clean sans-serif for corporate signage, hand-painted serif for local Median signs.
- **Kenzie's follower counter:** a pink pill shape in the top-right corner of her POV shots, with numbers in a bold sans-serif.
- **Act cards:** none. Use the Recall Wipe instead.

---

## 7. Locked prompt tokens (for AI image and video generation)

> Paste these **exactly**. Don't paraphrase them. Consistency comes from repeating identical text.

### STYLE TOKEN (prefix to every image prompt)
```
MEDIAN-STYLE: flat 2D cartoon, clean vector look, bold 4px warm near-black outlines with a 3px white sticker-rim around characters, single flat shadow tone, no gradients, soft rounded-rectangle shapes, large white oval eyes with small black dot pupils, thick floating eyebrows, mitten hands with four fingers, head-to-body ratio 1:1.6, muted beige-sage-dusty-blue small-town palette with subtle risograph grain in backgrounds, overcast soft light, adult animated sitcom look, 16:9
```

### NEGATIVE TOKEN (to avoid)
```
no photorealism, no 3D render, no anime, no gradients, no paper cutout texture, no extra fingers, no text artifacts, no brand logos, no style drift, no changing outfit colors
```

### CHARACTER TOKENS
```
[DEX] 12-year-old boy, tallest of the group, light peach skin, sandy blond hair in a tall swoop with one cowlick sticking straight up at the back, upward-tilted confident eyes, oversized charcoal blazer with pushed-up sleeves over a red hoodie with hood outside the collar, tan chinos, white sneakers with red laces, black headset microphone with loose dangling cable
```
```
[WREN] 12-year-old girl, deep brown skin, black box braids in a big high bun with two loose front braids, half-lidded unimpressed eyes with one eyebrow raised, olive green army jacket with small crescent-moon pin on collar, grey t-shirt, black jeans, worn purple high-top sneakers, chunky white over-ear headphones around her neck
```
```
[MARCUS] 12-year-old boy, shortest of the group, olive tan skin, dark brown hair slicked straight back and shiny, narrow calculating eyes, tucked-in navy polo with small dollar-sign-in-circle logo, khaki shorts, braided brown belt, loafers with white socks, gold fanny pack worn across the chest stuffed with cash, Bluetooth earpiece in right ear
```
```
[GORDY] 12-year-old boy, round body, warm medium brown skin, messy black hair under a khaki bucket hat with metallic silver lining, very large round thick black glasses with white tape on the bridge, mustard-yellow short-sleeve button-up over a space-logo t-shirt, cargo shorts with overstuffed pockets, tall white socks, velcro sneakers, lanyard with many keys
```
```
[KENZIE] 12-year-old girl, fair skin with pink undertones, platinum blonde tight high ponytail with scrunchie, big bright eyes with three bold lashes each, cropped hot-pink puffer jacket over white tank top, light-wash wide-leg jeans, white platform sneakers, holding up a phone with a clip-on ring light that glows on her face
```
```
[TUNK] 12-year-old boy, tall and lanky with long arms, sunburned light skin with freckles and pink nose, reddish-brown buzz cut with small zig-zag scar on left side of head, small calm far-apart eyes, missing front tooth, faded denim overalls with one strap hanging off, stained white t-shirt, rubber barn boots
```
```
[FRINK] middle-aged man, pale grey skin tone, thinning combed-over grey hair, rimless glasses, expressionless face, grey zip windbreaker with small violet bar-chart logo, lanyard badge, holding a clipboard
```
```
[KRUPP] woman in her 60s, large teased auburn hair, pastel peach skirt suit with shoulder pads, pearl necklace, huge toothy smile, holding giant gold ribbon-cutting scissors
```

### LOCATION TOKENS
```
[LOC-SCHOOL-EXT] 1970s single-story brick middle school, beige trim, flagpole, banner reading "ABOVE AVERAGE IS BELOW US", half-full parking lot, flat Nebraska horizon, overcast
```
```
[LOC-CLASSROOM-7B] beige middle-school classroom, rows of laminate desks, green chalkboard, motivational poster about compromise, a single outlet with five chargers plugged in, windows showing cornfield
```
```
[LOC-MIRROR-ROOM] fluorescent-lit beige meeting room inside town hall, long folding table with paper plates of sandwiches, one entire wall is a large dark one-way mirror, slightly green lighting, buzzing tube light
```
```
[LOC-THE-MEAN] small-town greasy-spoon diner, red vinyl booths, chrome counter, chalkboard reading "TODAY'S TEST SPECIAL:", pie case, window to main street
```
```
[LOC-VALUBARN] enormous big-box superstore interior, beige shelving, a glowing neon endcap labeled "COMING TO AMERICA SOON"
```
```
[LOC-CUBE-EXT] seamless black glass cube building in the middle of a cornfield, no visible doors, faint violet glow at the edges, overcast sky
```
```
[LOC-RECALL-HILL] large grassy landfill hill made of discarded consumer products, faintly glowing neon items poking out of the dirt, a crooked chain-link fence, farmhouse visible at its base
```
```
[LOC-PRUITT-GARAGE] suburban garage converted to a "lab", spray-painted sign "PRUITT LABS", whiteboard covered in nonsense diagrams, folding table, beanbag chairs, a dented minifridge
```
```
[LOC-TOWN-SIGN] roadside welcome sign reading "WELCOME TO MEDIAN — NEITHER HERE NOR THERE — POP. 4,812" with a flip-number population display, cornfields both sides
```

**How to use them:** `STYLE TOKEN + [LOCATION] + [CHARACTER(S)] + expression + action + camera`. For example:

```
MEDIAN-STYLE: … , [LOC-PRUITT-GARAGE], [DEX] standing on a folding chair pointing at the whiteboard with a triumphant grin, [WREN] in a beanbag with arms crossed and one eyebrow raised, low-angle medium shot, DAY-FLAT lighting
```

---

## 8. Asset library (build once, reuse forever)
| Asset | Contents | Count |
|---|---|---|
| **Character model sheets** | turnaround (front, 3/4, side, back), 12-expression sheet, 9-shape mouth chart, 6 hand poses, color callouts | 6 main + 10 recurring |
| **Character rigs** | puppet rigs built from the model sheets (head turns, arm IK, mouth swap) | 6 main + 10 recurring |
| **Background plates** | each location at 3 locked angles (wide, reverse, close) × 2 lighting presets | 10 locations, about 60 plates |
| **Props** | phones, school items, recurring props, Tunk's Objects of the Week | grows each episode |
| **Crowd kit** | 24 generic townspeople in 3 color variations each, which covers any crowd | 72 |
| **FX** | neon glow, the Recall Wipe, sparkles, sweat drops, dust clouds, explosions | about 20 |
| **Audio kit** | theme, stings, Recall Siren, room tones, Foley | about 60 files |

---

## 9. YouTube Shorts framing
- Compose key gag shots with a **centered "safe column"** (the middle 608 px of 1920) so they can be cropped to 9:16 without losing the joke.
- Kenzie's phone-POV footage is natively vertical, so use it for Shorts.
- Keep burned-in captions out of the master. Add them per Short.

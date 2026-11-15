# MEDIAN — Production Workflow (v1.0)

> **Goal:** a 10–15 minute episode every 2–3 weeks with one or two people, using AI where it's strong and normal animation tools where AI is still weak.

---

## 0. An honest take on AI animation in 2026 (read this first)

Your three instincts (lock the characters, build one reusable town, produce scene by scene) are exactly right. Here's the one more rule that decides whether this works:

**Don't rely on text-to-video AI for dialogue scenes.** Today's AI video models are good at short, dramatic, wordless shots. They're still unreliable at keeping a character exactly on-model across 100+ shots, and at clean lip sync on flat 2D designs. A show like this is about 70% people standing still and talking, and that's the part AI video does *worst*.

**The approach that works: a hybrid "puppet" pipeline.**

| Stage | Use AI for | Use conventional tools for |
|---|---|---|
| Design | model sheets, expression sheets, background plates | vector cleanup (so designs are mathematically identical) |
| Dialogue scenes (about 70%) | voice performances | **rigged 2D puppets** animated from the voice track (automatic lip sync) |
| Action and chaos inserts (about 20%) | image-to-video from **approved keyframes**, 2–5 second shots | compositing over locked backgrounds |
| Crowd and establishing shots (about 10%) | generated plates and crowd variations | reuse library |
| Sound | voices, some SFX | music library, Foley, mixing |

This is roughly how small studios make flat-style adult cartoons on tight budgets: the characters are puppets, and acting comes from timing and voice. Simple art makes that possible, so it's a feature rather than a compromise.

**Suggested tools (pick one per row; none are required):**
| Job | Options |
|---|---|
| Model sheets and backgrounds | an AI image generator with reference-image / character-consistency features → vector cleanup in Illustrator, Affinity Designer or Inkscape |
| Puppet rigging and animation | Adobe Character Animator (fastest lip sync), Reallusion Cartoon Animator 5, Moho Pro, or Toon Boom Harmony (most professional) |
| Voices | professional or friend voice actors (best), or AI voice with **one locked voice ID per character** (e.g. ElevenLabs) |
| AI video inserts | any image-to-video model that accepts a start frame (and ideally an end frame) |
| Editing | DaVinci Resolve (free), Premiere Pro or CapCut |
| Music | a royalty-free library plus a commissioned main theme |
| Project tracking | a single spreadsheet or Airtable base (template below) |

> **Legal note:** keep every character, name, logo and product fictional. Never generate or include real brand logos, real celebrities' likenesses or voice clones of real people. Parody of public *ideas and trends* is fine; using someone's identity is not.

---

## 1. Phase 0: series setup (one time only, about 2–3 weeks)

1. **Lock the designs.**
   - Generate each character from the locked token in `02-animation-style-guide.md` §7. Make 20–40 candidates per character and pick one.
   - Turn the chosen image into a **clean vector master**, so every later asset is traced from the *same file* and never generated again.
   - Build each model sheet: front, 3/4, side and back turnaround; 12 expressions (neutral, happy, laughing, angry, furious, sad, crying, shocked, smug, scheming, scared, deadpan); the 9-shape mouth chart; 6 hand poses; color callouts.
   - **Rule:** the vector master is canon. If an AI output disagrees with the master, the AI output is wrong.
2. **Build the rigs.** Rig each main character from the vector master (head turns at 3/4 and side, blinking, eyebrow controls, arm IK and the mouth chart).
3. **Build the town.** Make every location in the location token list at three locked angles (wide, reverse, close-up), and in DAY-FLAT and NIGHT lighting. Save them as layered files (foreground, midground, background) for parallax.
4. **Cast the voices.** One voice per character, and keep the actor or voice ID permanently. Record a **voice bible clip** for each character: 30 seconds of sample lines that everyone matches against later.
5. **Make the audio kit.** Main theme, Median Minute jingle, Recall Siren, Recall Wipe sting, room tones and the stingers library.
6. **Set up the folders and naming convention:**

```
MEDIAN/
  00_bible/                 (these docs, model sheets, voice bible)
  01_assets/
    characters/  DEX/ WREN/ MARCUS/ GORDY/ KENZIE/ TUNK/ recurring/
    locations/   LOC-SCHOOL-EXT/ LOC-CLASSROOM-7B/ ...
    props/  fx/  crowd/  audio_kit/
  02_episodes/
    S01E01_NothingSells/
      script/  boards/  audio/vo/  audio/sfx/  scenes/  edit/  export/  youtube/
  03_continuity/continuity-log.md
```

**File naming:** `S01E01_SC04_SH03_v02.ext` (season, episode, scene, shot, version). Every version is kept; nothing is overwritten.

---

## 2. Phase 1: per-episode pipeline (13 stages)

| # | Stage | Output | Gate (must pass to move on) | Time |
|---|---|---|---|---|
| 1 | **Concept** | logline, satire target, A/B plots, twist, payoff | Passes the "Why now / Why Median / Why these kids" test | 0.5 day |
| 2 | **Beat outline** | 4-act beat sheet, about 25 beats | Every beat escalates or turns; no filler | 0.5 day |
| 3 | **Script** | full script (about 12–16 pages for 12–14 min) | Passes the comedy pass (§4) and a table read | 2 days |
| 4 | **Scene breakdown** | scene list with characters, location, props, Object of the Week | Every asset needed exists or is listed for creation | 0.5 day |
| 5 | **Visual prompts and storyboards** | one keyframe per shot, built from locked tokens | On-model check against the vector masters | 1–2 days |
| 6 | **Shot list** | characters, expressions, actions, camera and transitions per shot | Approved animatic order | (with 5) |
| 7 | **Asset creation** | any new props, guest characters or new backgrounds | Matches the style guide | 0.5–1 day |
| 8 | **Voice recording** | final dialogue per line, file per line | Matches the voice bible; timing and pauses as scripted | 1 day |
| 9 | **Animatic** | storyboards cut to the final voice track | Runtime and pacing locked (there's no fixing pacing later) | 0.5 day |
| 10 | **Animation** | puppet scenes plus AI inserts plus composites | On-model, continuity-checked | 4–6 days |
| 11 | **Sound and music** | SFX, Foley, room tones, music cues, mix (-14 LUFS for YouTube) | Dialogue always intelligible | 1 day |
| 12 | **Edit and QC** | locked cut plus a QC report (§5) | Passes all QC items | 1 day |
| 13 | **YouTube package** | title, thumbnail, description, tags, chapters, captions, 3–5 Shorts | Package checklist (§6) | 0.5 day |

**Total:** about **12–15 working days per episode for one person**, about 7–9 with two. Episodes get faster after the first three because the asset library keeps growing.

### Scene-by-scene, not episode-by-episode
Produce **one scene at a time, end to end**: voice, then animatic, then animation, then a rough mix. Never generate a whole episode in one pass. Each scene is its own folder with its own versioned shots, so a broken scene never contaminates the rest of the episode.

### The AI insert protocol (for any shot made with AI video)
1. Start from an **approved keyframe** built on the locked tokens and checked against the vector master.
2. Generate **2–5 second** shots only. Longer shots drift.
3. Use **start frame + end frame** control whenever the tool supports it.
4. **No dialogue in AI shots.** If a character speaks in the shot, it's a puppet shot.
5. Generate 3–6 takes, pick the most on-model one, and reject anything with drift (wrong colors, missing accessories, extra fingers).
6. Log the prompt, seed and model in the shot's folder so the shot can be reproduced.

---

## 3. Continuity system
- **`continuity-log.md`**: after every episode, log:
  - the population sign number,
  - Frink's File line,
  - Tunk's Object of the Week,
  - every lasting change (injuries, bans, debts, destroyed locations, new Recall Hill items, relationship shifts),
  - new recurring characters or props added to the library.
- **Before writing each new episode**, read the log. At least one callback to an earlier episode per episode.
- **The accessory checklist** (style guide §3) runs on every single shot during QC.

---

## 4. Writers' room comedy pass (do this on every script draft)
Read the script aloud and check each item:
1. **Hook:** is there a laugh or a "wait, what?" within the first 15 seconds?
2. **Laugh density:** a solid laugh at least every 20–30 seconds, and a big one every 2–3 minutes.
3. **Distinct voices:** cover the names. Can you still tell who's talking? If not, rewrite the line.
4. **Escalation:** is each act bigger than the last? If Act 3 isn't bigger than Act 2, the episode isn't done.
5. **The twist:** does it change what the episode was *about*, not just what happens?
6. **No speeches:** if a character states the theme, undercut it within three seconds.
7. **Kill your darlings:** if a joke has to be explained, cut it. If a scene can be removed and the story still works, remove it.
8. **The cynic check:** is the episode punching *at* something specific? "Everything is dumb" is not satire. Satire needs a target and a point of view.
9. **The offense check:** dark and offensive humor is in scope, but aim it at **power, institutions, trends and hypocrisy**, not at people for who they are. The edge should come from the *idea*, not from punching down. This also keeps the channel safe from demonetization and age-restriction.

---

## 5. Quality control checklist (before export)
| Area | Check |
|---|---|
| **Story** | Is it genuinely funny on a second watch? Does the ending pay off? |
| **Characters** | Every shot on-model: proportions, colors, accessories (style guide §3). |
| **Dialogue** | Natural, distinct voices; no AI-sounding phrasing ("Let's dive in," "It's important to remember…"). |
| **Pacing** | No scene longer than 90 seconds without a turn; no dead air except intentional Median Stares. |
| **Animation** | No popping, flickering or drift in AI inserts; lip sync is clean. |
| **Continuity** | Props and wardrobe stay consistent within scenes; the population sign and callbacks match the continuity log. |
| **Audio** | Dialogue clear over music; levels about -14 LUFS integrated; no clipping; room tone under every scene. |
| **Legal** | No real logos, celebrities, real-person voice clones or copyrighted music. |
| **YouTube policy** | Content is adult satire, but avoid gratuitous gore and sexual content; mark the video "not made for kids" (it's an adult cartoon). |
| **Profanity** | Cursing is allowed in episodes. To protect ad revenue: no strong profanity in the first ~7 seconds; keep titles, thumbnails, descriptions and the opening hook clean; avoid stacking swears back to back; and bleep or cut swears in Shorts when an ad-friendly version is wanted. Check YouTube's current advertiser-friendly guidelines before each upload, since the profanity rules change. Keep an uncensored master plus a bleeped version, so each upload can use the right one. |

**Rule:** if the episode feels generic, it doesn't ship. Rewrite the weakest scene before anything else.

---

## 6. YouTube package checklist (per episode)
- **Title:** under 60 characters, curiosity-driven, and never the same as the episode title alone. Format: *"[Hook phrase] | MEDIAN S1E1"*.
- **Thumbnail:** one face with a strong expression, one prop, a maximum of three words of text, and a beige background with a neon prop (the show's visual signature works at thumbnail size).
- **Description:** two hook lines, then the episode summary, chapters, the series playlist link and a cast note.
- **Chapters:** one per act (the Recall Wipes are natural chapter points).
- **Tags and keywords:** "adult animation," "animated comedy," "satire cartoon," plus episode-specific topics.
- **Captions:** upload the script-accurate SRT, not auto-captions.
- **Shorts (3–5):** each 20–50 seconds, vertical, one complete joke with a setup and a punchline. Pin a comment linking the full episode.
- **End screen:** next episode plus a subscribe prompt. End the episode on the Frink's File line to tease the next one.
- **Posting rhythm:** one full episode every 2–3 weeks, with Shorts spread across the weeks in between (about 2–3 per week).

---

## 7. Episode tracker (spreadsheet columns)
`Episode | Stage (1–13) | Scene | Shot | Characters | Location | Type (puppet/AI insert/plate) | Status | Version | Notes | Continuity items | Owner | Due`

# WonderBuds — Permanent Character Bible

Five best animal friends who live in WonderBuds Village. **These designs, colors and voices are permanent** — every episode loads the same 3D models from `cast.js` and the same voice profiles from `bible.json`. Never redesign or re-voice a character without a story reason.

Series catchphrase: **“Let's go, WonderBuds!”** · Audience: ages 3–8 · Reference sheets: `ref/stills/` (lineup + front/side/back + 6 expressions per character) · Voice samples: `ref/WonderBuds_voices.mp3`

## Rosie the Red panda — The Leader

**Look:** Rust-orange fur, white face markings and cheek patches, dark brown arms and legs, bushy ringed tail, teal scarf, little yellow backpack.  
**Height:** 2.6 units (scene scale)  
**Colors:** fur `#c8562a`, dark fur `#5a2a1e`, face markings `#fff3e0`, scarf `#20b2aa`, backpack `#ffc93c`

**Personality:** Brave, curious, energetic; first to say yes to an adventure; keeps the group together and always checks everyone is OK.  
**Special strength:** Courage and leadership — she has a compass and a map in her backpack and always finds the way.  
**Voice:** Bright, confident, clear; speaks in short excited bursts. *(Kokoro `af_bella`, speed 1.04, pitch ×1.24)*  
**Catchphrases:** “Let's go, WonderBuds!” · “Adventure time!” · “Follow me!” · “Everybody OK? Good!”  
**Movement:** Purposeful march, points the way, fists on hips when proud.  
**Running joke:** Her map is always upside down at first.

**Signature expressions:** happy, laugh, surprised, nervous, thinking, ready! (see reference sheet)

## Pudding the Hippo — The Funny One

**Look:** Round lavender hippo, big soft snout, tiny ears, two little teeth, rainbow propeller beanie that spins when he's excited.  
**Height:** 2.4 units (scene scale)  
**Colors:** fur `#b9a3e3`, belly `#e3d7f7`, snout `#d4c2f2`, hat `rainbow propeller beanie`

**Personality:** Silly, goofy, loves snacks and puns; turns mistakes into laughs; very loyal and huggable.  
**Special strength:** Makes everyone laugh when they're worried — and he's surprisingly strong.  
**Voice:** Goofy, bouncy, a bit slower, laughs a lot (hee-hee!). *(Kokoro `am_puck`, speed 1.0, pitch ×1.16)*  
**Catchphrases:** “Oopsie-doodle!” · “Is it snack time?” · “Hee-hee-hee!” · “I meant to do that!”  
**Movement:** Waddles, belly-bounces, spins his propeller.  
**Running joke:** Always hungry; his propeller spins when he's excited.

**Signature expressions:** happy, laugh, surprised, nervous, thinking, ready! (see reference sheet)

## Ollie the Owl — The Smart One

**Look:** Sky-blue owlet, heart-shaped pale face, ear tufts, big round glasses, red bowtie, cream chest with chevrons.  
**Height:** 2.2 units (scene scale)  
**Colors:** feathers `#5aa9e6`, face disc `#d6ecfb`, belly `#f4ead2`, glasses `#33415c`, bowtie `#ff6b6b`, beak feet `#ffa94d`

**Personality:** Thoughtful, curious about how things work, loves puzzles and facts; a bit of a perfectionist.  
**Special strength:** Solves puzzles and spots clues nobody else sees.  
**Voice:** Gentle British accent, precise, says 'Hmm…' before ideas. *(Kokoro `bm_fable`, speed 1.0, pitch ×1.42)*  
**Catchphrases:** “Hmm, let me think…” · “I've got it!” · “Fascinating!” · “According to my calculations…”  
**Movement:** Pushes his glasses up, taps his chin with a wing, hops when excited.  
**Running joke:** His calculations are always right except about snacks.

**Signature expressions:** happy, laugh, surprised, nervous, thinking, ready! (see reference sheet)

## Clover the Bunny — The Shy One

**Look:** Cream bunny with very long ears (one floppy), pink nose, mint hoodie, little daisy clip on her ear, fluffy tail.  
**Height:** 2.3 units (scene scale)  
**Colors:** fur `#f6e7dc`, inner ear `#ffb3c7`, hoodie `#8fdcc2`, flower clip `#ffd43b`

**Personality:** Sweet, kind, notices feelings; sometimes nervous, but finds her courage when friends need her.  
**Special strength:** Super hearing with her long ears, and kindness that calms everyone down.  
**Voice:** Soft, gentle, a little breathy; slows down when nervous. *(Kokoro `af_nicole`, speed 1.0, pitch ×1.32)*  
**Catchphrases:** “M-maybe I can try…” · “I can hear something!” · “We can do it together.” · “Oh my carrots!”  
**Movement:** Small careful steps, holds her ears when nervous, little hops when happy.  
**Running joke:** Says 'Oh my carrots!' when surprised.

**Signature expressions:** happy, laugh, surprised, nervous, thinking, ready! (see reference sheet)

## Ziggy the Monkey — The Energetic One

**Look:** Chocolate-brown monkey, peach face and belly, long curly tail, red sneakers, yellow lightning-bolt headband.  
**Height:** 2.5 units (scene scale)  
**Colors:** fur `#8a5a3c`, face belly `#f2c9a0`, sneakers `#ff4a4a`, headband `#ffd43b`

**Personality:** Super playful, never stops moving, races ahead, counts everything out loud; huge heart.  
**Special strength:** Speed and climbing — gets to high places nobody else can reach.  
**Voice:** Fast, high, excited; repeats words: 'Ready? Ready! READY!' *(Kokoro `af_sky`, speed 1.18, pitch ×1.48)*  
**Catchphrases:** “Zoom zoom!” · “Ready? Ready! READY!” · “Race you there!” · “Wheeee!”  
**Movement:** Bounces in place, cartwheels, swings by his tail.  
**Running joke:** Races ahead and has to zoom back.

**Signature expressions:** happy, laugh, surprised, nervous, thinking, ready! (see reference sheet)

## Voice rules
- Each character always uses their own voice profile above; the narrator (`af_heart`) only opens and closes episodes.
- Pitch order (low → high): Pudding (≈140 Hz) · Ollie (≈160 Hz, British) · Clover (≈195 Hz, soft & slow) · Rosie (≈240 Hz, clear) · Ziggy (≈240 Hz but very fast and excited).
- Dialogue lines in scripts are always labelled with the speaker id; the build pipeline picks the voice from that id, so a line can never get the wrong voice.

## Friendships & dynamics
- Rosie leads, but always asks Ollie for ideas and checks on Clover.
- Pudding and Ziggy are the chaos duo; Ziggy races ahead, Pudding gets stuck, everyone laughs.
- Clover is quiet until the big moment — her hearing or kindness saves the day at least once per episode.
- Ollie's plans are great, except when snacks are involved (Pudding's favourite joke).

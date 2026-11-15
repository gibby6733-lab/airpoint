# MEDIAN — Main Title Sequence ("Welcome to Median")

**Length:** 30 seconds · **Format:** 1920×1080, 24 fps · **Used on:** every episode, after the cold open.
**Animatic:** `median_intro_animatic_v02.mp4` (silent, with lyric captions and timing locked).
**Source:** `intro.html` (every shot is code, so it re-renders the same way every time). Rebuild with:
```
node tools/render-intro.js <framesDir> 24
ffmpeg -framerate 24 -i <framesDir>/%04d.png -c:v libx264 -pix_fmt yuv420p intro/median_intro_animatic_v02.mp4
```

## What we took from the reference (structure only)
A short, sung, upbeat theme: a lead singer trades lines with each kid, every kid gets one line that sums up who they are, one kid gets an "off" gag line, and it ends on a title button. Everything else is ours: an original song, original lyrics, our own band style (a 1970s civic marching band with kazoo, not acoustic folk), and our own town and cast.

## Song: "Median, Median" (original lyrics, v02)
**v02 change:** the v01 "Come on down to ___" refrain was too close to South Park's song, so it's gone. The hook is now the show's own Median Minute jingle (*"Median, Median, right in the middle!"*), so the intro and the exposition cutaways share one musical identity.

**Style:** a 1970s municipal marching band, *slightly too cheerful*. Kazoo lead, glockenspiel, tuba, snare, about 132 BPM, played like a town parade or a civic PSA jingle. **Music note:** keep it brass-band and parade-like. Avoid acoustic folk, country and bluegrass so it never echoes South Park's theme. The band chorus chants the hook, and the kids answer in their locked voices.

| Time | Who | Line |
|---|---|---|
| 0:00–0:03 | — | Kazoo fanfare. Snare roll. |
| 0:03–0:06 | BAND | ♪ Median! Median! Right in the middle! ♪ |
| 0:06–0:07.6 | DEX | ♪ This is gonna change the world— ♪ |
| 0:07.6–0:09 | WREN | ♪ —it's gonna change a little. ♪ *(flat)* |
| 0:09–0:12 | BAND | ♪ Median! Median! Average and proud! ♪ |
| 0:12–0:13.5 | MARCUS | ♪ Everything's on sale today— ♪ |
| 0:13.5–0:15 | GORDY | ♪ —and someone's watching from the cloud! ♪ |
| 0:15–0:18 | BAND | ♪ Median! Median! America tries it first! ♪ |
| 0:18–0:21 | KENZIE | ♪ Like and subscribe or it's literally the worst! ♪ |
| 0:21–0:24 | TUNK | *(calm, off-key, half-spoken)* Grandpa says don't eat the hill… the hill eats first. **(the band falters for a beat)** |
| 0:24–0:27.5 | BAND | ♪ Median! Median! Neither here nor there! ♪ |
| 0:27.5–0:30 | ALL | ♪ MEDIAN! ♪ → pen click + "PROMISING." stamp |

## Shot list
| # | Time | Shot | Action / gag |
|---|---|---|---|
| 1 | 0:00–0:03 | Route 9 welcome sign, cornfields | A beige car drives past. The population sign flips 4,812 → **4,813** → **4,812** (running gag). |
| 2 | 0:03–0:06 | Downtown pan: The Mean → ValuBarn → Town Hall → Thornbury statue | The neon "COMING TO AMERICA SOON" sign pulses: the corporate intrusion color. |
| 3 | 0:06–0:09 | Pruitt Labs garage | Dex bounces on the beat, arms out. Wren stands perfectly still with arms crossed (that's the joke). |
| 4 | 0:09–0:12 | The Cube in the corn | The violet glow pulses and the corn sways. |
| 5 | 0:12–0:15 | Mirror Room, Focus Friday | Marcus bops with his fanny pack. On "watching through the wall," **an eye opens in the one-way mirror**, darts and blinks. |
| 6 | 0:15–0:18 | ValuBarn endcap | Neon test products pop onto the shelf on the beat. |
| 7 | 0:18–0:21 | Kenzie's phone, LIVE | The follower counter rockets from 2,304 to 1,000,000. |
| 8 | 0:21–0:24 | Recall Hill at dusk | Tunk stands still. The junk on the hill glows, and **the hill opens a violet eye**. |
| 9 | 0:24–0:27.5 | Main street line-up | The cast pops in shortest to tallest. The neon flickers. **Frink's silhouette appears in a window.** |
| 10 | 0:27.5–0:30 | Logo | MEDIAN with the bell-curve "I" slams in. Tagline. The red **PROMISING.** stamp lands with a pen click. |

## Season-long gags built in (change these over time)
- **Population sign:** shows the current number from the continuity log.
- **Endcap products (shot 6):** swap in that episode's test product.
- **Recall Hill (shot 8):** add each episode's failed product to the junk.
- **Frink's window (shot 9):** one tiny change per episode, rewarding freeze-frame fans.

## Audio plan (not produced yet)
| Piece | Tool | Estimated cost |
|---|---|---|
| Music bed and band vocal, 30s, 2 takes | ElevenLabs Music v2.5 | **3,000 credits** (~$0.60) |
| Kid lines, 7 lines × 2 takes, in the locked cast voices | ElevenLabs v4 | **~700 credits** (~$0.14) |
| Pen click, siren chirp, kazoo stings | ElevenLabs sound effects, or a free SFX library | small / free |
| **Total** | | **~3,700 credits (~$0.75)** |

# Test assets
- Dex style test v01 (Higgs, Z Image model, 0.15 credits) — APPROVED as the style reference: https://d8j0ntlcm91z4.cloudfront.net/user_3DXzq9HIhpW4Z3Co0u37C3qLEaq/hf_20261115_143756_c63099c1-6ac8-454e-8c9b-64c1a486ab6a.png

# Vector masters (canon)
- `characters/dex_front_v01.svg`: Dex, front view, hand-built vector master. Every part is a named layer (`legs`, `shoes`, `arm-left`, `arm-right`, `torso`, `hood`, `head`, `hair`, `cowlick`, `eye-left`, `eye-right`, `headset`) for rigging. Render it with `node tools/render-svg.js`.

# Cast model sheets v02 (canon, approved style)
Each sheet has a front view, side view, 4 expressions and palette. `*_front_v02.svg` is the front view on its own, for rigging and compositing.
| Character | Sheet | Expressions |
|---|---|---|
| Dex | `characters/dex_sheet_v02.svg` | smug, revelation, betrayed, deflated |
| Wren | `characters/wren_sheet_v02.svg` | deadpan, eye-roll, caught, rare smile |
| Marcus | `characters/marcus_sheet_v02.svg` | scheming, calculating, panic, impressed-defeat |
| Gordy | `characters/gordy_sheet_v02.svg` | intense, horrified, excited, sad |
| Kenzie | `characters/kenzie_sheet_v02.svg` | camera on, camera off, pinpoint, hollow |
| Tunk | `characters/tunk_sheet_v02.svg` | blank, "huh.", gap smile, unsettling |
| Line-up | `characters/cast_lineup_v02.png` | rebuild with `python3 tools/lineup.py` |

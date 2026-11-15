"""Generate MEDIAN side characters (front view, same vector style as the main cast).
Usage: python3 tools/gen_side_chars.py   -> assets/characters/side/<id>.svg
Each file: viewBox 'x -10 .. ' with feet at y=800 and head top near y=40 (adults ~1.2x kid height)."""
import os
OUT = os.path.join(os.path.dirname(__file__), '..', 'assets', 'characters', 'side')
os.makedirs(OUT, exist_ok=True)

FILTER = '''<filter id="st" x="-15%" y="-15%" width="130%" height="130%">
<feMorphology in="SourceAlpha" operator="dilate" radius="6" result="g"/><feFlood flood-color="#FFF"/><feComposite in2="g" operator="in" result="r"/>
<feMerge><feMergeNode in="r"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'''
OL = 'stroke="#2B2118" stroke-width="3.5" stroke-linejoin="round" stroke-linecap="round"'

def darker(hexc, f=0.82):
    h = hexc.lstrip('#'); r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return '#%02X%02X%02X' % (int(r*f), int(g*f), int(b*f))

def hair_svg(style, c):
    d = darker(c)
    if style == 'bald':
        return ''
    if style == 'combover':
        return f'<path fill="{c}" {OL} d="M-102,160 Q-108,90 -40,80 Q40,70 100,110 Q60,96 0,104 Q-60,112 -102,160Z"/>'
    if style == 'short':
        return f'<path fill="{c}" {OL} d="M-102,170 Q-112,66 0,60 Q112,66 102,170 Q92,120 0,112 Q-92,120 -102,170Z"/>'
    if style == 'teased':  # mayor: big teased hair
        return (f'<path fill="{c}" {OL} d="M-130,230 Q-170,90 -80,40 Q0,-10 80,40 Q170,90 130,230 Q110,140 60,118 Q0,96 -60,118 Q-110,140 -130,230Z"/>'
                f'<path fill="{d}" d="M-80,60 Q0,20 80,60 Q0,44 -80,60Z"/>')
    if style == 'bob':
        return f'<path fill="{c}" {OL} d="M-118,260 Q-128,60 0,56 Q128,60 118,260 Q100,250 96,170 Q60,118 0,114 Q-60,118 -96,170 Q-100,250 -118,260Z"/>'
    if style == 'bun':
        return (f'<circle fill="{c}" {OL} cx="0" cy="44" r="36"/>'
                f'<path fill="{c}" {OL} d="M-102,170 Q-112,66 0,62 Q112,66 102,170 Q92,120 0,112 Q-92,120 -102,170Z"/>')
    if style == 'curly':
        return (f'<path fill="{c}" {OL} d="M-118,200 Q-150,120 -100,80 Q-90,30 -40,40 Q0,0 40,40 Q90,30 100,80 Q150,120 118,200 Q100,130 0,118 Q-100,130 -118,200Z"/>')
    if style == 'cap':  # police cap
        return (f'<path fill="{c}" {OL} d="M-100,130 Q-96,50 0,46 Q96,50 100,130Z"/>'
                f'<path fill="#1A1A1A" {OL} d="M-110,128 h220 q4,16 -10,20 h-200 q-14,-4 -10,-20z"/>'
                f'<circle fill="#E8C547" {OL} cx="0" cy="96" r="12" stroke-width="2"/>')
    if style == 'beanie':
        return f'<path fill="{c}" {OL} d="M-104,160 Q-112,50 0,46 Q112,50 104,160Z"/><rect fill="{d}" x="-106" y="136" width="212" height="28" rx="10" {OL}/>'
    return ''

def person(pid, skin, hair='short', haircol='#4A3426', top='#8FA5B5', topstyle='shirt', pants='#5E5248', shoes='#3A2A1E',
           height=1.0, width=1.0, glasses=False, mustache=False, extra='', brow='#3A2A1E', lids=False, blush=True, mouth='smile', kid=False):
    sk = darker(skin)
    w = 1.0 * width
    torso_top, torso_bot = (290, 476) if kid else (292, 540)
    leg_bot = 618 if kid else 760
    tw = 78 * w
    parts = []
    # legs + shoes
    parts.append(f'<rect fill="{pants}" {OL} x="{-tw*0.82:.0f}" y="{torso_bot-14}" width="{tw*0.74:.0f}" height="{leg_bot-torso_bot+14}" rx="10"/>')
    parts.append(f'<rect fill="{pants}" {OL} x="{tw*0.08:.0f}" y="{torso_bot-14}" width="{tw*0.74:.0f}" height="{leg_bot-torso_bot+14}" rx="10"/>')
    parts.append(f'<path fill="{shoes}" {OL} d="M{-tw*0.82-18:.0f},{leg_bot+40} Q{-tw*0.82-20:.0f},{leg_bot+2} {-tw*0.82+10:.0f},{leg_bot} h{tw*0.6:.0f} q10,0 10,14 v26z"/>')
    parts.append(f'<path fill="{shoes}" {OL} d="M{tw*0.82+18:.0f},{leg_bot+40} Q{tw*0.82+20:.0f},{leg_bot+2} {tw*0.82-10:.0f},{leg_bot} h{-tw*0.6:.0f} q-10,0 -10,14 v26z"/>')
    # arms (behind torso edges)
    for sgn in (-1, 1):
        x = sgn * (tw + 6)
        parts.append(f'<rect fill="{top}" {OL} x="{x-17 if sgn>0 else x-17:.0f}" y="{torso_top+12}" width="34" height="{(torso_bot-torso_top)*0.72:.0f}" rx="16"/>')
        parts.append(f'<ellipse fill="{skin}" {OL} cx="{x:.0f}" cy="{torso_top+12+(torso_bot-torso_top)*0.72+14:.0f}" rx="18" ry="20"/>')
    # torso
    parts.append(f'<rect fill="{top}" {OL} x="{-tw:.0f}" y="{torso_top}" width="{2*tw:.0f}" height="{torso_bot-torso_top}" rx="{26*w:.0f}"/>')
    if topstyle == 'suit':
        parts.append(f'<path fill="#FFFFFF" {OL} d="M-26,{torso_top+2} L0,{torso_top+70} L26,{torso_top+2}Z"/>')
        parts.append(f'<path fill="{darker(top)}" {OL} d="M-30,{torso_top} L-56,{torso_top+6} L-10,{torso_top+110}Z M30,{torso_top} L56,{torso_top+6} L10,{torso_top+110}Z"/>')
    if topstyle == 'windbreaker':
        parts.append(f'<path stroke="#2B2118" stroke-width="3" d="M0,{torso_top+8} V{torso_bot-6}"/>')
        parts.append(f'<path fill="#9B5CFF" d="M{tw*0.35:.0f},{torso_top+40} h22 v10 h-22z M{tw*0.35:.0f},{torso_top+54} h14 v10 h-14z"/>')
    if topstyle == 'uniform':
        parts.append(f'<circle fill="#E8C547" {OL} cx="{-tw*0.45:.0f}" cy="{torso_top+46}" r="12" stroke-width="2.5"/>')
        parts.append(f'<rect fill="#1A1A1A" x="{-tw:.0f}" y="{torso_bot-40}" width="{2*tw:.0f}" height="16"/>')
        parts.append(f'<path stroke="#2B2118" stroke-width="3" d="M0,{torso_top+8} V{torso_bot-44}"/>')
    if topstyle == 'apron':
        parts.append(f'<path fill="#F4ECD8" {OL} d="M-46,{torso_top+30} h92 v{torso_bot-torso_top-20} h-92z"/>')
        parts.append(f'<rect fill="#D6453D" x="-30" y="{torso_top+80}" width="60" height="6"/>')
    if topstyle == 'cardigan':
        parts.append(f'<rect fill="#F4ECD8" {OL} x="-26" y="{torso_top+2}" width="52" height="{torso_bot-torso_top-6}"/>')
        parts.append(f'<circle fill="#2B2118" cx="-34" cy="{torso_top+60}" r="4"/><circle fill="#2B2118" cx="-34" cy="{torso_top+110}" r="4"/>')
    if topstyle == 'polo':
        parts.append(f'<path fill="{darker(top)}" {OL} d="M-46,{torso_top+2} L0,{torso_top+12} L46,{torso_top+2} L36,{torso_top+30} L0,{torso_top+18} L-36,{torso_top+30}Z"/>')
    if topstyle == 'hoodie':
        parts.append(f'<path fill="{darker(top)}" {OL} d="M-80,{torso_top+4} Q0,{torso_top-36} 80,{torso_top+4} Q0,{torso_top+30} -80,{torso_top+4}Z"/>')
        parts.append(f'<rect fill="{darker(top)}" {OL} x="-50" y="{torso_bot-90}" width="100" height="50" rx="8"/>')
    # head
    head = []
    head.append(f'<ellipse fill="{skin}" {OL} cx="-104" cy="196" rx="15" ry="20"/><ellipse fill="{skin}" {OL} cx="104" cy="196" rx="15" ry="20"/>')
    head.append(f'<rect fill="{skin}" {OL} x="-100" y="66" width="200" height="218" rx="90"/>')
    head.append(hair_svg(hair, haircol))
    if blush:
        head.append(f'<ellipse fill="#E8806E" opacity=".35" cx="-60" cy="226" rx="17" ry="10"/><ellipse fill="#E8806E" opacity=".35" cx="60" cy="226" rx="17" ry="10"/>')
    head.append(f'<path fill="{sk}" stroke="#2B2118" stroke-width="2" d="M-10,202 Q0,222 10,202 Q8,216 0,218 Q-8,216 -10,202Z"/>')
    head.append(f'<ellipse fill="#FFF" {OL} cx="-40" cy="178" rx="26" ry="28"/><ellipse fill="#FFF" {OL} cx="40" cy="178" rx="26" ry="28"/>')
    head.append('<circle fill="#2B2118" cx="-38" cy="182" r="8"/><circle fill="#2B2118" cx="38" cy="182" r="8"/>')
    if lids:
        head.append(f'<path fill="{skin}" d="M-68,148 h56 v30 Q-40,172 -68,178Z M68,148 h-56 v30 Q40,172 68,178Z"/>'
                    f'<path fill="none" {OL} d="M-68,176 Q-40,170 -12,176 M68,176 Q40,170 12,176"/>')
    head.append(f'<path fill="{brow}" d="M-70,140 Q-42,130 -14,140 L-14,150 Q-42,142 -70,150Z M70,140 Q42,130 14,140 L14,150 Q42,142 70,150Z"/>')
    if glasses:
        head.append('<g fill="none" stroke="#2B2118" stroke-width="4"><rect x="-74" y="150" width="64" height="56" rx="16"/><rect x="10" y="150" width="64" height="56" rx="16"/><path d="M-10,174 h20"/></g>')
    if mustache:
        head.append(f'<path fill="{haircol}" {OL} stroke-width="2.5" d="M-38,234 Q-20,220 0,230 Q20,220 38,234 Q20,246 0,238 Q-20,246 -38,234Z"/>')
    if mouth == 'smile':
        head.append(f'<path fill="none" {OL} d="M-26,246 Q0,262 26,246"/>')
    elif mouth == 'flat':
        head.append(f'<path fill="none" {OL} d="M-20,250 H20"/>')
    elif mouth == 'grin':
        head.append(f'<path fill="#FFF" {OL} d="M-40,238 Q0,256 40,238 Q34,270 0,272 Q-34,270 -40,238Z"/><path stroke="#2B2118" stroke-width="2" d="M-36,250 Q0,262 36,250"/>')
    elif mouth == 'frown':
        head.append(f'<path fill="none" {OL} d="M-22,256 Q0,242 22,256"/>')
    hs = 1.0
    body = '\n'.join(parts) + f'\n<g transform="translate(0,{0 if kid else 6}) scale({hs})">' + '\n'.join(head) + '</g>\n' + extra
    top_y = -20
    vb_h = 860 if not kid else 700
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="-200 {top_y} 400 {vb_h}" width="400" height="{vb_h}">
<!-- MEDIAN side character: {pid} -->
<defs>{FILTER}</defs><g filter="url(#st)">{body}</g></svg>'''
    import re
    def _dedupe(m):
        tag=m.group(0); seen={}
        for a in re.finditer(r'\s([\w-]+)="[^"]*"',tag): seen.setdefault(a.group(1),[]).append(a)
        for k,v in seen.items():
            for a in v[:-1]: tag=tag.replace(a.group(0),'',1)
        return tag
    svg=re.sub(r'<[a-zA-Z][^<>]*>',_dedupe,svg)
    open(os.path.join(OUT, pid + '.svg'), 'w').write(svg)

CLIP = '<g transform="translate(110,430) rotate(-10)"><rect fill="#B8986A" stroke="#2B2118" stroke-width="3.5" x="-32" y="-46" width="64" height="88" rx="6"/><rect fill="#F4ECD8" x="-24" y="-30" width="48" height="64"/><rect fill="#9AA0A8" stroke="#2B2118" stroke-width="2" x="-14" y="-52" width="28" height="12" rx="3"/></g>'
SCISSORS = '<g transform="translate(-120,420) rotate(-30)"><circle fill="none" stroke="#2B2118" stroke-width="10" cx="-20" cy="60" r="22"/><circle fill="none" stroke="#D4A93A" stroke-width="6" cx="-20" cy="60" r="22"/><circle fill="none" stroke="#2B2118" stroke-width="10" cx="22" cy="60" r="22"/><circle fill="none" stroke="#D4A93A" stroke-width="6" cx="22" cy="60" r="22"/><path fill="#D4A93A" stroke="#2B2118" stroke-width="3" d="M-12,40 L6,-120 L14,-118 L6,40Z M12,40 L-6,-120 L-14,-118 L-6,40Z"/></g>'
WHISTLE = '<path stroke="#C42" stroke-width="4" fill="none" d="M-30,300 Q0,380 30,300"/><rect fill="#C4C8CC" stroke="#2B2118" stroke-width="3" x="-14" y="372" width="28" height="16" rx="6"/>'
LANYARD = '<path stroke="#9B5CFF" stroke-width="6" fill="none" d="M-34,296 L0,400 L34,296"/><rect fill="#FFFFFF" stroke="#2B2118" stroke-width="3" x="-20" y="400" width="40" height="52" rx="4"/>'
CIG = '<rect fill="#FFFFFF" stroke="#2B2118" stroke-width="2" x="88" y="120" width="34" height="8" rx="3" transform="rotate(-30 105 124)"/>'
PEARLS = '<g fill="#F4F1EA" stroke="#2B2118" stroke-width="1.5">' + ''.join(f'<circle cx="{x}" cy="{306+abs(x)*0.25:.0f}" r="7"/>' for x in range(-48, 50, 16)) + '</g>'
PHONE = '<rect fill="#2B2D33" stroke="#2B2118" stroke-width="3" x="-140" y="330" width="40" height="70" rx="6" transform="rotate(-10 -120 365)"/>'
BOX = '<g transform="translate(0,470)"><rect fill="#111114" stroke="#FF2E93" stroke-width="4" x="-50" y="-40" width="100" height="80" rx="6"/><text x="0" y="10" text-anchor="middle" font-family="DejaVu Sans" font-weight="800" font-size="26" fill="#FF2E93">VOID</text></g>'

# Recurring characters (locked in the show bible)
person('frink', '#E2D6C8', 'combover', '#9A968E', '#8C8781', 'windbreaker', '#5E5A54', '#3A3A3A', width=0.95, glasses=True, extra=CLIP+LANYARD, brow='#6E6A62', lids=True, blush=False, mouth='flat')
person('krupp', '#F2C9A5', 'teased', '#B5502A', '#F2B49A', 'suit', '#F2B49A', '#E0766A', width=1.05, extra=SCISSORS+PEARLS, mouth='grin')
person('bev', '#E8BFA0', 'curly', '#9AA0A8', '#D6453D', 'apron', '#3C3F47', '#2B2118', width=1.15, extra=CIG, lids=True, mouth='flat')
person('kevin', '#D9A580', 'cap', '#24375E', '#24375E', 'uniform', '#24375E', '#1A1A1A', width=1.55, mustache=True, mouth='smile')
person('mallory', '#8A5A3C', 'cap', '#24375E', '#24375E', 'uniform', '#24375E', '#1A1A1A', width=0.95, lids=True, mouth='flat')
person('gaines', '#A8724A', 'bald', '#2B2118', '#4A6A4A', 'polo', '#3C3F47', '#2B2118', width=1.2, extra=WHISTLE, mustache=True, mouth='frown')
person('okonkwo', '#6E4A30', 'bun', '#1E1A1A', '#7A9A8A', 'cardigan', '#5E5248', '#7A5236', width=1.0, glasses=True, mouth='smile')
person('man_suitcase', '#E8C4A8', 'short', '#6A5A4A', '#B8A07A', 'cardigan', '#5E5248', '#3A2A1E', width=1.0, lids=True, mouth='frown', extra='<g transform="translate(130,520)"><rect fill="#7A5236" stroke="#2B2118" stroke-width="3.5" x="-40" y="0" width="80" height="60" rx="8"/><path fill="none" stroke="#2B2118" stroke-width="5" d="M-14,0 v-12 h28 v12"/></g>')
person('yoga_mom', '#F4D3C4', 'bun', '#C9A060', '#9B5CFF', 'shirt', '#2B2D33', '#FFFFFF', width=0.9, mouth='smile', extra=BOX)
person('teen', '#C9956B', 'beanie', '#3C8A6A', '#3C8A6A', 'hoodie', '#2B2D33', '#FFFFFF', width=1.0, kid=True, lids=True, mouth='grin', extra=BOX)
person('younger_kid', '#F2C9A5', 'short', '#8A5A3A', '#F0C24A', 'shirt', '#5876A3', '#D6453D', width=0.85, kid=True, mouth='grin')
person('shaking_man', '#D9A580', 'short', '#2B2118', '#7AA86A', 'polo', '#5E5248', '#3A2A1E', width=1.1, mouth='grin', mustache=True, extra=BOX)
# generic townspeople / crowd (varied palette)
crowd = [('#F2C9A5','short','#6A4A2A','#8FA5B5','#5E5248'),('#8A5A3C','curly','#1E1A1A','#E2B33C','#3C3F47'),('#E8BFA0','bob','#C9A060','#A9644E','#2B2D33'),
         ('#C9956B','bald','#000000','#7AA86A','#5E5248'),('#6E4A30','bun','#1E1A1A','#D6453D','#2B2D33'),('#F4D3C4','combover','#B8B4AE','#C9B48F','#3C3F47'),
         ('#A8724A','short','#2B2118','#5876A3','#8C8460'),('#E2D6C8','bob','#6A2A2A','#7A9A8A','#5E5248')]
for i,(sk,h,hc,top,pants) in enumerate(crowd):
    person(f'town{i+1}', sk, h, hc, top, ['shirt','polo','cardigan','shirt'][i%4], pants, '#3A2A1E', width=[1.0,1.15,0.95,1.25,0.9,1.0,1.1,0.95][i], mouth=['smile','flat','grin','smile','flat','smile','grin','flat'][i])
print('ok', sorted(os.listdir(OUT)))

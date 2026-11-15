"""Cut the 4 expression heads out of each *_sheet_v02.svg as standalone SVGs: assets/characters/expr/<char>_<expr>.svg"""
import re, os
D='assets/characters'; os.makedirs(f'{D}/expr',exist_ok=True)
names={'dex':['smug','revelation','betrayed','deflated'],'wren':['deadpan','eyeroll','caught','smile'],
 'marcus':['scheming','calculating','panic','defeat'],'gordy':['intense','horrified','excited','sad'],
 'kenzie':['camon','camoff','pinpoint','hollow'],'tunk':['blank','huh','gapsmile','unsettling']}
for c,ex in names.items():
    s=open(f'{D}/{c}_sheet_v02.svg').read()
    s=re.sub(r'<g transform="translate\(40,760\)">.*?</g>\s*</g>','',s,flags=re.S)
    s=s.replace('<rect width="1600" height="900" fill="#F7EEDD"/>','')
    pos=re.findall(r'filter="url\(#sticker\)" transform="translate\((\d+),(\d+)\) scale\(0\.62\)"',s)
    assert len(pos)==4,(c,pos)
    for (x,y),e in zip(pos,ex):
        x,y=int(x),int(y)
        out=s.replace('viewBox="0 0 1600 900" width="1600" height="900"',f'viewBox="{x-100} {y-12} 205 205" width="410" height="410"',1)
        open(f'{D}/expr/{c}_{e}.svg','w').write(out)
print('ok')

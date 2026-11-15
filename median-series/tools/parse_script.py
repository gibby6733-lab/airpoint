"""Parse 05-episode-101-script.md into episode/ep101_script.json: scenes -> ordered beats (shot / line)."""
import re, json
src=open('05-episode-101-script.md').read().split('# PRODUCTION PACKAGE')[0]
scenes=[]; cur=None; who=None; paren=None
for raw in src.splitlines():
    l=raw.rstrip()
    m=re.match(r'^### SC (\d+)',l)
    if m: cur={'sc':int(m.group(1)),'beats':[]}; scenes.append(cur); who=None; continue
    if cur is None: continue
    m=re.match(r'^`SHOT ([\d.]+)',l)
    if m: cur['beats'].append({'t':'shot','id':m.group(1)}); who=None; continue
    m=re.match(r'^> \*\*([^*]+)\*\*\s*$',l)
    if m: who=m.group(1).strip(); paren=None; continue
    if l.startswith('> ') and who:
        txt=l[2:].strip()
        pm=re.match(r'^\*\((.*)\)\*$',txt)
        if pm: paren=pm.group(1); continue
        txt=re.sub(r'\*\*\(BEEP\)\*\*\s*','',txt).replace('\\*','*').replace('**','')
        txt=re.sub(r'^\*(.*)\*$',r'\1',txt).strip()
        if txt: cur['beats'].append({'t':'line','who':who,'text':txt,'paren':paren}); paren=None
        continue
    if not l.startswith('>'): who=None
json.dump(scenes,open('episode/ep101_script.json','w'),indent=1,ensure_ascii=False)
n=sum(1 for s in scenes for b in s['beats'] if b['t']=='line'); w=sum(len(b['text'].split()) for s in scenes for b in s['beats'] if b['t']=='line')
print('scenes',len(scenes),'lines',n,'words',w)
whos=sorted({b['who'] for s in scenes for b in s['beats'] if b['t']=='line'}); print(whos)
open('episode/ep101_script.js','w').write('window.SCRIPT='+json.dumps(scenes,ensure_ascii=False)+';')

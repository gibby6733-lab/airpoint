"""Build the cast line-up: render each *_front_v02.svg transparent, trim to its outline, scale by height index, compose.
Usage: python3 tools/lineup.py   (writes assets/characters/cast_lineup_v02.png)"""
import subprocess, os, json
from PIL import Image, ImageDraw, ImageFont
D=os.path.join(os.path.dirname(__file__),'..','assets','characters')
cast=[('marcus','MARCUS',0.88),('gordy','GORDY',0.96),('wren','WREN',1.00),('kenzie','KENZIE',1.04),('tunk','TUNK',1.06),('dex','DEX',1.10)]
js="""const {chromium}=require('playwright');const fs=require('fs');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:560,height:700},deviceScaleFactor:2});
for(const f of JSON.parse(process.argv[2])){await p.goto('file://'+f+'.svg');await p.screenshot({path:f+'.tmp.png',omitBackground:true});}await b.close();})();"""
tmpjs=os.path.join(D,'_r.js'); open(tmpjs,'w').write(js)
files=[os.path.abspath(os.path.join(D,f'{c}_front_v02')) for c,_,_ in cast]
subprocess.run(['node',tmpjs,json.dumps(files)],check=True); os.remove(tmpjs)
H=620; imgs=[]
for (c,n,h),f in zip(cast,files):
    im=Image.open(f+'.tmp.png'); im=im.crop(im.getbbox()); os.remove(f+'.tmp.png')
    t=int(H*h/1.10); im=im.resize((int(im.width*t/im.height),t),Image.LANCZOS); imgs.append(im)
gap=40; W=sum(i.width for i in imgs)+gap*(len(imgs)+1); base=760
canvas=Image.new('RGB',(W,880),'#F7EEDD'); d=ImageDraw.Draw(canvas)
def font(sz,bold=True):
    for p in ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']:
        if os.path.exists(p): return ImageFont.truetype(p,sz)
    return ImageFont.load_default()
d.text((40,28),'MEDIAN — MAIN CAST LINE-UP v02',fill='#3A2A1E',font=font(28))
d.text((40,68),'Locked order (shortest → tallest) · scaled by height index',fill='#7A6A58',font=font(16,False))
d.line((20,base+4,W-20,base+4),fill='#C9B48F',width=4)
x=gap
for im,(c,n,h) in zip(imgs,cast):
    canvas.paste(im,(x,base-im.height),im)
    cx=x+im.width//2; f1=font(18); f2=font(14,False)
    d.text((cx,base+30),n,fill='#3A2A1E',font=f1,anchor='mm'); d.text((cx,base+54),f'{h:.2f}',fill='#7A6A58',font=f2,anchor='mm')
    x+=im.width+gap
canvas.save(os.path.join(D,'cast_lineup_v02.png')); print(W)

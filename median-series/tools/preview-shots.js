// Render one still per shot (middle of the shot) for review. Usage: node tools/preview-shots.js <outDir>
const { chromium } = require('playwright'); const path=require('path');
(async()=>{const out=process.argv[2];const b=await chromium.launch();const p=await b.newPage({viewport:{width:1920,height:1080}});
p.on('pageerror',e=>console.log('PAGEERROR',e.message));p.on('console',m=>{if(m.type()==='error')console.log('CONSOLE',m.text())});
await p.goto('file://'+path.resolve(__dirname,'../episode/ep101.html'));await p.waitForFunction(()=>window.READY,null,{timeout:20000});await p.waitForTimeout(1500);
const segs=await p.evaluate(()=>window.TL.map(s=>({id:s.id,a:s.start,b:s.end})));
console.log('DUR',await p.evaluate(()=>window.DUR),'INTRO_AT',await p.evaluate(()=>window.INTRO_AT),'shots',segs.length);
for(const s of segs){const t=s.a+(s.b-s.a)*0.6;await p.evaluate(t=>window.renderAt(t),t);await p.waitForTimeout(60);await p.locator('#stage').screenshot({path:`${out}/${s.id}.png`});}
await b.close();})();

const { chromium } = require('playwright');
const path=require('path');
(async()=>{
  const b=await chromium.launch();const pg=await b.newPage({viewport:{width:1080,height:1920}});
  pg.on('pageerror',e=>console.log('PAGEERR',e.message));pg.on('console',m=>{if(m.type()==='error')console.log('CONSOLE',m.text())});
  await pg.goto('file://'+path.resolve('episode.html'));await pg.evaluate(()=>document.fonts.ready);
  const meta=await pg.evaluate(()=>window.META);console.log(JSON.stringify(meta));
  const times=process.argv.slice(2).map(Number);
  require('fs').mkdirSync('prev',{recursive:true});
  for(const [i,t] of times.entries()){const t0=Date.now();await pg.evaluate(t=>window.render(t),t);await pg.screenshot({path:`prev/f${String(i).padStart(2,'0')}.jpg`,type:'jpeg',quality:80});console.log(t,Date.now()-t0,'ms')}
  await b.close();
})();

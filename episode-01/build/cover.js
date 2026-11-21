const { chromium } = require('playwright');const path=require('path');
(async()=>{const b=await chromium.launch();const pg=await b.newPage({viewport:{width:1080,height:1920}});
 pg.on('pageerror',e=>console.log('PAGEERR',e.message));
 await pg.goto('file://'+path.resolve('episode.html'));await pg.evaluate(()=>document.fonts.ready);
 await pg.evaluate(()=>window.renderCover());await pg.screenshot({path:process.argv[2]||'../cover.png'});await b.close()})();

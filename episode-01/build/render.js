const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path=require('path'),fs=require('fs');
(async()=>{
  const FPS=30;
  const b=await chromium.launch();const pg=await b.newPage({viewport:{width:1080,height:1920}});
  pg.on('pageerror',e=>console.log('PAGEERR',e.message));
  await pg.goto('file://'+path.resolve('episode.html'));await pg.evaluate(()=>document.fonts.ready);
  const meta=await pg.evaluate(()=>window.META);fs.writeFileSync('meta.json',JSON.stringify(meta));
  if(process.argv[2]==='meta'){await b.close();return}
  const n=Math.ceil(meta.TOTAL*FPS);
  const ff=spawn('ffmpeg',['-y','-v','error','-f','image2pipe','-framerate',String(FPS),'-c:v','mjpeg','-i','-','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','video.mp4'],{stdio:['pipe','inherit','inherit']});
  const t0=Date.now();
  for(let i=0;i<n;i++){
    await pg.evaluate(t=>window.render(t),i/FPS);
    const buf=await pg.screenshot({type:'jpeg',quality:93});
    if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));
    if(i%150===0)console.log(`frame ${i}/${n} ${((Date.now()-t0)/1000).toFixed(0)}s`);
  }
  ff.stdin.end();await new Promise(r=>ff.on('close',r));await b.close();
  console.log('done',((Date.now()-t0)/1000).toFixed(0),'s');
})();

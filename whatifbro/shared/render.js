// Usage: node render.js <episode_dir> [meta|preview t1 t2 ...|full]
const { chromium } = require('playwright');const { spawn, execFileSync } = require('child_process');
const path=require('path'),fs=require('fs');
(async()=>{
  const ep=path.resolve(process.argv[2]);const mode=process.argv[3]||'full';const FPS=30;
  const b=await chromium.launch();const pg=await b.newPage({viewport:{width:1080,height:1920}});
  pg.on('pageerror',e=>console.log('PAGEERR',e.message));
  await pg.goto('file://'+ep+'/episode.html');await pg.evaluate(()=>document.fonts.ready);
  const meta=await pg.evaluate(()=>window.META);fs.writeFileSync(ep+'/meta.json',JSON.stringify(meta));
  if(mode==='meta'){console.log('TOTAL',meta.TOTAL.toFixed(2));await b.close();return}
  if(mode==='cover'){await pg.evaluate(()=>window.renderCover());await pg.screenshot({path:ep+'/cover.png'});await b.close();console.log('cover');return}
  if(mode==='preview'){const ts=process.argv.slice(4).map(Number);fs.mkdirSync(ep+'/prev',{recursive:true});for(const f of fs.readdirSync(ep+'/prev'))fs.unlinkSync(ep+'/prev/'+f);
    for(const [i,t] of ts.entries()){await pg.evaluate(t=>window.render(t),t);await pg.screenshot({path:`${ep}/prev/f${String(i).padStart(2,'0')}.jpg`,type:'jpeg',quality:80})}
    await b.close();execFileSync('ffmpeg',['-v','error','-y','-i',ep+'/prev/f%02d.jpg','-vf',`scale=270:-1,tile=${Math.min(ts.length,8)}x${Math.ceil(ts.length/8)}:padding=6`,'-frames:v','1',ep+'/prev/sheet.jpg']);console.log('sheet');return}
  const n=Math.ceil(meta.TOTAL*FPS);
  const ff=spawn('ffmpeg',['-y','-v','error','-f','image2pipe','-framerate',String(FPS),'-c:v','mjpeg','-i','-','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p',ep+'/video.mp4'],{stdio:['pipe','inherit','inherit']});
  const t0=Date.now();
  for(let i=0;i<n;i++){await pg.evaluate(t=>window.render(t),i/FPS);const buf=await pg.screenshot({type:'jpeg',quality:93});
    if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));if(i%300===0)console.log(path.basename(ep),`frame ${i}/${n} ${((Date.now()-t0)/1000).toFixed(0)}s`)}
  ff.stdin.end();await new Promise(r=>ff.on('close',r));await b.close();
  const name=fs.readFileSync(ep+'/name.txt','utf8').trim();
  execFileSync('ffmpeg',['-v','error','-y','-i',ep+'/video.mp4','-i',ep+'/audio/mix.wav','-af','loudnorm=I=-14:TP=-1.5:LRA=11','-c:v','libx264','-preset','slow','-crf','24','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-ar','44100','-movflags','+faststart','-shortest',ep+'/'+name+'.mp4']);
  fs.unlinkSync(ep+'/video.mp4');
  console.log(path.basename(ep),'done',((Date.now()-t0)/1000).toFixed(0),'s ->',name+'.mp4');
})();

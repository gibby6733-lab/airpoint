// Render a time range of episode/ep101.html to a 60 fps video segment, piping frames straight to ffmpeg.
// Usage: node tools/render-episode.js <startSec> <endSec> <out.mp4> [fps=60]
const { chromium } = require('playwright'); const path=require('path'); const { spawn }=require('child_process');
(async()=>{const [a,b,out]=[+process.argv[2],+process.argv[3],process.argv[4]]; const fps=+(process.argv[5]||60);
const ff=spawn('ffmpeg',['-y','-loglevel','error','-f','image2pipe','-framerate',String(fps),'-c:v','mjpeg','-i','-','-c:v','libx264','-profile:v','high','-preset','medium','-crf','18','-pix_fmt','yuv420p','-r',String(fps),out],{stdio:['pipe','inherit','inherit']});
const br=await chromium.launch(); const p=await br.newPage({viewport:{width:1920,height:1080}});
p.on('pageerror',e=>console.error('PAGEERROR',e.message));
await p.goto('file://'+path.resolve(__dirname,'../episode/ep101.html')); await p.waitForFunction(()=>window.READY); await p.waitForTimeout(1500);
const n0=Math.round(a*fps), n1=Math.round(b*fps);
for(let i=n0;i<n1;i++){await p.evaluate(t=>window.renderAt(t),i/fps);
 const buf=await p.screenshot({type:'jpeg',quality:94,clip:{x:0,y:0,width:1920,height:1080}});
 if(!ff.stdin.write(buf)) await new Promise(r=>ff.stdin.once('drain',r));
 if((i-n0)%600===0) console.log(out,'frame',i-n0,'/',n1-n0);}
ff.stdin.end(); await new Promise(r=>ff.on('close',r)); await br.close(); console.log('done',out);})();

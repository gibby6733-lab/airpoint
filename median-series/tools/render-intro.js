// Renders intro/intro.html frame-by-frame to PNGs, then (via ffmpeg) to MP4.
// Usage: node tools/render-intro.js <framesDir> [fps]
const { chromium } = require('playwright'); const path=require('path'); const fs=require('fs');
(async()=>{const dir=process.argv[2], fps=+(process.argv[3]||24); fs.mkdirSync(dir,{recursive:true});
const b=await chromium.launch(); const p=await b.newPage({viewport:{width:1920,height:1080}});
await p.goto('file://'+path.resolve(__dirname,'../intro/intro.html')); await p.waitForTimeout(800);
const N=30*fps; for(let i=0;i<N;i++){await p.evaluate(t=>window.renderAt(t), i/fps);
 await p.locator('#stage').screenshot({path:path.join(dir,String(i).padStart(4,'0')+'.png')});}
await b.close();})();

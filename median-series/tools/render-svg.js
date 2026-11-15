// Render an SVG character to PNG on the Median beige background.
// Usage: node tools/render-svg.js <in.svg> <out.png> [bgColor]
const { chromium } = require('playwright');
const fs=require('fs'),path=require('path');
(async()=>{const [svg,out,bg]=process.argv.slice(2);const b=await chromium.launch();const p=await b.newPage({viewport:{width:+(process.argv[5]||500),height:+(process.argv[6]||820)},deviceScaleFactor:1});
await p.setContent(`<body style="margin:0;background:${bg||'#E8DCC2'}">${fs.readFileSync(svg,'utf8')}</body>`);await p.screenshot({path:out});await b.close();})();

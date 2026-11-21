// What If Bro — shared animation engine (extracted from episode 1)
// ================= helpers =================
const W=1080,H=1920,INK='#16111f',SKIN='#f6e6cc',LIME='#b7f23a',PURP='#7b2cf0',CREAM='#fffdf6';
const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x));
const lerp=(a,b,t)=>a+(b-a)*t;
const p=(t,a,b)=>clamp((t-a)/(b-a));
const eOut=x=>1-Math.pow(1-x,3);
const eIn=x=>x*x*x;
const eIO=x=>x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2;
const eBack=x=>{const c1=1.9,c3=c1+1;return 1+c3*Math.pow(x-1,3)+c1*Math.pow(x-1,2)};
const pop=(t,t0,d=.35)=>t<t0?0:eBack(p(t,t0,t0+d));
function rng(seed){return function(){seed|=0;seed=seed+0x6D2B79F5|0;let t=Math.imul(seed^seed>>>15,1|seed);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}
const esc=s=>s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
function shake(t,t0,dur=.35,amp=22){if(t<t0||t>t0+dur)return[0,0];const k=1-(t-t0)/dur;return[Math.sin(t*90)*amp*k,Math.cos(t*77)*amp*k]}
const g=(tr,inner,extra='')=>`<g transform="${tr}" ${extra}>${inner}</g>`;
function txt(x,y,s,size,fill,o={}){const font=o.font||'Lucky';const sw=o.sw??size*0.16;const anchor=o.anchor||'middle';const rot=o.rot?` transform="rotate(${o.rot} ${x} ${y})"`:'';
  return `<text x="${x}" y="${y}" font-family="${font}" font-weight="700" font-size="${size}" text-anchor="${anchor}" fill="${fill}" stroke="${o.stroke||INK}" stroke-width="${sw}" paint-order="stroke" stroke-linejoin="round" letter-spacing="${o.ls||0}"${rot} ${o.extra||''}>${esc(s)}</text>`}
// ================= characters =================
function youHead(o={}){
  const eyes=o.eyes||'open', lx=o.look?o.look[0]:0, ly=o.look?o.look[1]:0;
  let eyeSvg='';
  if(eyes==='closed'){eyeSvg=`<path d="M-160 -10 C-130 20 -75 20 -45 -10" fill="none" stroke-width="15"/><path d="M45 -10 C75 20 130 20 160 -10" fill="none" stroke-width="15"/>`}
  else{const rx=eyes==='huge'?92:72, ry=eyes==='huge'?104:84, pr=eyes==='huge'?13:20;
    eyeSvg=`<ellipse cx="-102" cy="-20" rx="${rx}" ry="${ry}" fill="${CREAM}" stroke-width="15"/><ellipse cx="102" cy="-20" rx="${rx}" ry="${ry}" fill="${CREAM}" stroke-width="15"/>
    <circle cx="${-94+lx}" cy="${-8+ly}" r="${pr}" fill="${INK}" stroke="none"/><circle cx="${94+lx}" cy="${-8+ly}" r="${pr}" fill="${INK}" stroke="none"/>
    <circle cx="${-87+lx}" cy="${-16+ly}" r="6" fill="${CREAM}" stroke="none"/><circle cx="${101+lx}" cy="${-16+ly}" r="6" fill="${CREAM}" stroke="none"/>`}
  const mouth=o.mouth==='smile'?`<path d="M-45 130 C-20 165 20 165 45 130" fill="none" stroke-width="13"/>`:
              o.mouth==='o'?`<ellipse cx="0" cy="145" rx="22" ry="28" fill="#5a1a2a" stroke-width="12"/>`:
              o.mouth==='grit'?`<rect x="-50" y="125" width="100" height="36" rx="12" fill="${CREAM}" stroke-width="11"/><path d="M-17 125 V161 M17 125 V161" stroke-width="7"/>`:
              `<path d="M-20 140 C-8 128 8 128 20 140" fill="none" stroke-width="13"/>`;
  const brows=o.brows==='angry'?`<path d="M-152 -128 L-60 -100" stroke-width="15"/><path d="M60 -100 L152 -128" stroke-width="15"/>`:
     `<path d="M-152 -108 C-122 -128 -87 -132 -60 -120" fill="none" stroke-width="15"/><path d="M60 -120 C88 -132 123 -128 152 -108" fill="none" stroke-width="15"/>`;
  const blush=o.blush?`<ellipse cx="-170" cy="95" rx="58" ry="26" fill="#ff5d7a" opacity=".75" stroke="none"/><ellipse cx="170" cy="95" rx="58" ry="26" fill="#ff5d7a" opacity=".75" stroke="none"/>`:
     `<ellipse cx="-177" cy="100" rx="34" ry="16" fill="#ff8fa3" opacity=".6" stroke="none"/><ellipse cx="177" cy="100" rx="34" ry="16" fill="#ff8fa3" opacity=".6" stroke="none"/>`;
  const sweat=o.sweat===false?'':`<g transform="translate(194 -170)"><path d="M0 0 C24 40 36 62 36 80 C36 102 20 116 0 116 C-20 116 -36 102 -36 80 C-36 62 -24 40 0 0 Z" fill="#7fd6ff" stroke-width="12"/><path d="M-14 70 C-16 85 -10 96 -2 100" fill="none" stroke="#fff" stroke-width="8"/></g>`;
  return `<g stroke="${INK}" stroke-linecap="round" stroke-linejoin="round">
    ${o.noShoulders?'':`<path d="M-312 560 C-302 360 -182 290 0 290 C182 290 302 360 312 560 Z" fill="${o.hood||LIME}" stroke-width="16"/><path d="M-82 300 C-62 360 62 360 82 300" fill="none" stroke-width="12"/>`}
    <path d="M-50 220 L-50 300 C-22 318 22 318 50 300 L50 220 Z" fill="${o.skin||'#f3dcc0'}" stroke-width="14"/>
    <ellipse cx="-250" cy="20" rx="34" ry="52" fill="${o.skin||SKIN}" stroke-width="14"/><ellipse cx="250" cy="20" rx="34" ry="52" fill="${o.skin||SKIN}" stroke-width="14"/>
    <ellipse cx="0" cy="0" rx="255" ry="265" fill="${o.skin||SKIN}" stroke-width="18"/>
    <path d="M-42 -250 C-32 -295 8 -300 0 -260 C28 -300 73 -285 48 -245" fill="none" stroke-width="14"/>
    ${brows}${eyeSvg}${blush}${mouth}${sweat}
  </g>`;
}
// full body You (for the 2014 film). origin = head center
function youBody(o={}){
  const wave=o.wave??null; // angle in deg for right arm
  let arm='';
  if(wave!==null){const a=wave*Math.PI/180;const sx=170,sy=330;const hx=sx+Math.cos(a)*260,hy=sy-Math.sin(a)*260;
    arm=`<path d="M${sx} ${sy} L${hx} ${hy}" stroke="${INK}" stroke-width="74" stroke-linecap="round"/><path d="M${sx} ${sy} L${hx} ${hy}" stroke="${o.hood||LIME}" stroke-width="50" stroke-linecap="round"/><circle cx="${hx}" cy="${hy}" r="46" fill="${o.skin||SKIN}" stroke="${INK}" stroke-width="14"/>`}
  else arm=`<path d="M170 330 L230 620" stroke="${INK}" stroke-width="74" stroke-linecap="round"/><path d="M170 330 L230 620" stroke="${o.hood||LIME}" stroke-width="50" stroke-linecap="round"/><circle cx="232" cy="630" r="46" fill="${o.skin||SKIN}" stroke="${INK}" stroke-width="14"/>`;
  return `<g stroke-linejoin="round">
   <rect x="-120" y="640" width="90" height="230" rx="30" fill="#3a2c5e" stroke="${INK}" stroke-width="14"/><rect x="30" y="640" width="90" height="230" rx="30" fill="#3a2c5e" stroke="${INK}" stroke-width="14"/>
   <ellipse cx="-80" cy="880" rx="80" ry="38" fill="${CREAM}" stroke="${INK}" stroke-width="14"/><ellipse cx="80" cy="880" rx="80" ry="38" fill="${CREAM}" stroke="${INK}" stroke-width="14"/>
   <path d="M-170 330 L-230 620" stroke="${INK}" stroke-width="74" stroke-linecap="round"/><path d="M-170 330 L-230 620" stroke="${o.hood||LIME}" stroke-width="50" stroke-linecap="round"/><circle cx="-232" cy="630" r="46" fill="${o.skin||SKIN}" stroke="${INK}" stroke-width="14"/>
   <rect x="-200" y="270" width="400" height="420" rx="130" fill="${o.hood||LIME}" stroke="${INK}" stroke-width="16"/>
   ${arm}
   ${youHead(Object.assign({noShoulders:true},o))}
  </g>`;
}
// little control-room worker. origin = body center
function worker(o={}){
  const shirt=o.shirt||'#ff6b6b', skin=o.skin||'#f6e6cc', w=o.wide?95:72;
  const lh=o.lh||[-95,55], rh=o.rh||[95,55];
  const look=o.look||[0,0];
  const arm=(sx,sy,h)=>`<path d="M${sx} ${sy} L${h[0]} ${h[1]}" stroke="${INK}" stroke-width="34" stroke-linecap="round"/><path d="M${sx} ${sy} L${h[0]} ${h[1]}" stroke="${shirt}" stroke-width="20" stroke-linecap="round"/><circle cx="${h[0]}" cy="${h[1]}" r="17" fill="${skin}" stroke="${INK}" stroke-width="8"/>`;
  let eyes='';const ex=26,ey=-132;
  switch(o.eyes||'normal'){
    case 'droopy': eyes=`<circle cx="${-ex}" cy="${ey}" r="18" fill="${CREAM}" stroke="${INK}" stroke-width="7"/><circle cx="${ex}" cy="${ey}" r="18" fill="${CREAM}" stroke="${INK}" stroke-width="7"/><circle cx="${-ex+look[0]}" cy="${ey+7+look[1]}" r="7" fill="${INK}"/><circle cx="${ex+look[0]}" cy="${ey+7+look[1]}" r="7" fill="${INK}"/><path d="M${-ex-20} ${ey-2} H${-ex+20} M${ex-20} ${ey-2} H${ex+20}" stroke="${INK}" stroke-width="8"/><path d="M${-ex-18} ${ey-3} A18 18 0 0 1 ${-ex+18} ${ey-3} Z M${ex-18} ${ey-3} A18 18 0 0 1 ${ex+18} ${ey-3} Z" fill="${skin}"/>`;break;
    case 'frantic': eyes=`<circle cx="${-ex-2}" cy="${ey}" r="25" fill="${CREAM}" stroke="${INK}" stroke-width="7"/><circle cx="${ex+2}" cy="${ey}" r="25" fill="${CREAM}" stroke="${INK}" stroke-width="7"/><circle cx="${-ex-2+look[0]}" cy="${ey+look[1]}" r="5" fill="${INK}"/><circle cx="${ex+2+look[0]}" cy="${ey+look[1]}" r="5" fill="${INK}"/>`;break;
    case 'happy': eyes=`<path d="M${-ex-15} ${ey+5} Q${-ex} ${ey-15} ${-ex+15} ${ey+5} M${ex-15} ${ey+5} Q${ex} ${ey-15} ${ex+15} ${ey+5}" fill="none" stroke="${INK}" stroke-width="8" stroke-linecap="round"/>`;break;
    case 'closed': eyes=`<path d="M${-ex-15} ${ey} Q${-ex} ${ey+14} ${-ex+15} ${ey} M${ex-15} ${ey} Q${ex} ${ey+14} ${ex+15} ${ey}" fill="none" stroke="${INK}" stroke-width="8" stroke-linecap="round"/>`;break;
    case 'creepy': eyes=`<path d="M${-ex-16} ${ey+4} Q${-ex} ${ey-8} ${-ex+16} ${ey+4} Z M${ex-16} ${ey+4} Q${ex} ${ey-8} ${ex+16} ${ey+4} Z" fill="${CREAM}" stroke="${INK}" stroke-width="6"/><circle cx="${-ex+look[0]}" cy="${ey+1}" r="5" fill="${INK}"/><circle cx="${ex+look[0]}" cy="${ey+1}" r="5" fill="${INK}"/>`;break;
    default: eyes=`<circle cx="${-ex}" cy="${ey}" r="17" fill="${CREAM}" stroke="${INK}" stroke-width="7"/><circle cx="${ex}" cy="${ey}" r="17" fill="${CREAM}" stroke="${INK}" stroke-width="7"/><circle cx="${-ex+look[0]}" cy="${ey+3+look[1]}" r="7" fill="${INK}"/><circle cx="${ex+look[0]}" cy="${ey+3+look[1]}" r="7" fill="${INK}"/>`;
  }
  const my=-88;
  const mouths={flat:`<path d="M-14 ${my} H14" stroke="${INK}" stroke-width="8" stroke-linecap="round"/>`,
    smile:`<path d="M-20 ${my-4} Q0 ${my+16} 20 ${my-4}" fill="none" stroke="${INK}" stroke-width="8" stroke-linecap="round"/>`,
    grin:`<path d="M-34 ${my-8} Q0 ${my+30} 34 ${my-8} Z" fill="${CREAM}" stroke="${INK}" stroke-width="7" stroke-linejoin="round"/><path d="M-20 ${my-6} V${my+8} M0 ${my-6} V${my+12} M20 ${my-6} V${my+8}" stroke="${INK}" stroke-width="4"/>`,
    o:`<ellipse cx="0" cy="${my}" rx="12" ry="15" fill="#5a1a2a" stroke="${INK}" stroke-width="7"/>`,
    scream:`<ellipse cx="0" cy="${my+2}" rx="20" ry="24" fill="#5a1a2a" stroke="${INK}" stroke-width="7"/>`,
    drool:`<path d="M-14 ${my} H14" stroke="${INK}" stroke-width="8" stroke-linecap="round"/><path d="M10 ${my} q4 22 0 28 q-6 -4 -2 -28" fill="#9fe3ff" stroke="${INK}" stroke-width="4"/>`};
  const hat=o.hat==='chef'?`<path d="M-55 -195 C-95 -205 -90 -265 -45 -255 C-40 -300 40 -300 45 -255 C90 -265 95 -205 55 -195 Z" fill="#fff" stroke="${INK}" stroke-width="8"/><rect x="-55" y="-205" width="110" height="28" rx="8" fill="#fff" stroke="${INK}" stroke-width="8"/>`:'';
  const hair=o.hair==='spike'?`<path d="M-40 -192 L-30 -225 L-10 -196 L5 -232 L20 -196 L40 -222 L42 -190" fill="${o.hairCol||INK}" stroke="${INK}" stroke-width="6" stroke-linejoin="round"/>`:
             o.hair==='bald'?`<path d="M-30 -190 Q0 -205 30 -190" fill="none" stroke="${INK}" stroke-width="6"/>`:
             o.hair==='tuft'?`<path d="M-8 -192 C-4 -215 12 -218 8 -198 C20 -214 34 -206 22 -190" fill="none" stroke="${INK}" stroke-width="7" stroke-linecap="round"/>`:'';
  const glasses=o.glasses?`<g fill="${o.glint?'#e8f4ff':'none'}" fill-opacity=".85" stroke="${INK}" stroke-width="7"><circle cx="${-ex}" cy="${ey}" r="24"/><circle cx="${ex}" cy="${ey}" r="24"/><path d="M-2 ${ey} H2"/></g>`:'';
  const headset=o.headset?`<path d="M-72 -130 C-72 -215 72 -215 72 -130" fill="none" stroke="#2b2240" stroke-width="12"/><rect x="-84" y="-150" width="22" height="44" rx="9" fill="#2b2240"/><rect x="62" y="-150" width="22" height="44" rx="9" fill="#2b2240"/><path d="M-72 -110 Q-60 -78 -25 -80" fill="none" stroke="#2b2240" stroke-width="6"/>`:'';
  return `<g>
    <rect x="-48" y="70" width="34" height="58" rx="14" fill="#2b2240" stroke="${INK}" stroke-width="8"/><rect x="14" y="70" width="34" height="58" rx="14" fill="#2b2240" stroke="${INK}" stroke-width="8"/>
    ${o.armsBehind?'':''}
    <rect x="${-w}" y="-62" width="${w*2}" height="150" rx="${o.wide?70:52}" fill="${shirt}" stroke="${INK}" stroke-width="10"/>
    ${o.tie?`<path d="M0 -58 L-12 -40 L0 20 L12 -40 Z" fill="${o.tie}" stroke="${INK}" stroke-width="6"/>`:''}
    ${o.badge?`<rect x="${-w+20}" y="-20" width="62" height="34" rx="6" fill="#fff" stroke="${INK}" stroke-width="6"/><text x="${-w+51}" y="6" font-family="Fred" font-weight="700" font-size="20" text-anchor="middle" fill="${INK}">${esc(o.badge)}</text>`:''}
    <circle cx="0" cy="-128" r="74" fill="${skin}" stroke="${INK}" stroke-width="10"/>
    ${hair}${hat}${headset}
    <ellipse cx="-50" cy="-100" rx="14" ry="8" fill="#ff8fa3" opacity=".55"/><ellipse cx="50" cy="-100" rx="14" ry="8" fill="#ff8fa3" opacity=".55"/>
    ${eyes}${glasses}${mouths[o.mouth||'flat']}
    ${o.sweat?`<path d="M58 -190 c10 16 15 25 15 32 a15 15 0 0 1 -30 0 c0 -7 5 -16 15 -32z" fill="#7fd6ff" stroke="${INK}" stroke-width="6"/>`:''}
    ${o.noArms?'':arm(-w+12,-20,lh)+arm(w-12,-20,rh)}
    ${o.front||''}
  </g>`;
}

// ================= environment =================
const R0=rng(42);
const FOLDS=Array.from({length:46},()=>{const x=R0()*1200-60,y=R0()*1300-80;let d=`M${x.toFixed(0)} ${y.toFixed(0)}`;let cx=x,cy=y;for(let k=0;k<4;k++){const dx=40+R0()*90,dy=(R0()-.5)*120;d+=` q${(dx/2).toFixed(0)} ${(dy*1.6).toFixed(0)} ${dx.toFixed(0)} ${dy.toFixed(0)}`;cx+=dx;cy+=dy}return d});
function wall(dark=0){
  return `<rect width="${W}" height="${H}" fill="url(#wallG)"/>
  <g fill="none" stroke="#ff9ad5" stroke-width="10" stroke-linecap="round" opacity="${.16-dark*.08}">${FOLDS.map(d=>`<path d="${d}"/>`).join('')}</g>
  <rect y="1260" width="${W}" height="${H-1260}" fill="#2a1450"/>
  <path d="M0 1260 H${W}" stroke="${INK}" stroke-width="12"/>
  <g stroke="#3d2070" stroke-width="6">${[...Array(9)].map((_,i)=>`<path d="M${540+(i-4)*60} 1260 L${540+(i-4)*260} ${H}"/>`).join('')}</g>`;
}
function eyeWindow(content,label='LIVE FEED',rec=true,t=0){
  return `<g><rect x="170" y="170" width="740" height="430" rx="40" fill="#1b0f33" stroke="${INK}" stroke-width="14"/>
  <clipPath id="wclip"><rect x="190" y="190" width="700" height="390" rx="28"/></clipPath>
  <g clip-path="url(#wclip)">${content}</g>
  <rect x="190" y="190" width="700" height="390" rx="28" fill="none" stroke="#8b6cff" stroke-width="6"/>
  ${rec?`<circle cx="232" cy="232" r="13" fill="#ff3b4f" opacity="${Math.sin(t*6)>0?1:.25}"/>`:''}
  ${txt(258,244,label,32,'#fff',{anchor:'start',font:'Fred',sw:6})}
  <rect x="500" y="600" width="80" height="80" fill="#2b2240" stroke="${INK}" stroke-width="10"/></g>`;
}
function hallwayView(t){
  // school hallway with lockers, slight sway
  const sway=Math.sin(t*1.3)*8;
  let lock='';for(let i=0;i<10;i++){const x=150+i*95+sway;lock+=`<rect x="${x}" y="300" width="88" height="250" fill="#3f8cff" stroke="${INK}" stroke-width="6"/><path d="M${x+20} 330 h48 M${x+20} 345 h48 M${x+20} 360 h48" stroke="${INK}" stroke-width="4"/><circle cx="${x+72}" cy="430" r="6" fill="${INK}"/>`}
  return `<rect x="150" y="150" width="800" height="470" fill="#f4ecd8"/><rect x="150" y="540" width="800" height="80" fill="#c9b99a"/>${lock}`;
}
function desk(x,y,w=330,col='#5b3fa8'){return `<g><rect x="${x-w/2}" y="${y}" width="${w}" height="150" rx="16" fill="${col}" stroke="${INK}" stroke-width="10"/><rect x="${x-w/2-14}" y="${y-18}" width="${w+28}" height="34" rx="12" fill="#8a6cf0" stroke="${INK}" stroke-width="10"/></g>`}
function sign(x,y,label,col='#ffe23a',size=54,rot=0){
  const w=label.length*size*0.62+70;
  return `<g transform="translate(${x} ${y}) rotate(${rot})"><path d="M${-w/3} -70 L0 -130 L${w/3} -70" fill="none" stroke="${INK}" stroke-width="6"/><circle cx="0" cy="-130" r="10" fill="${INK}"/>
  <rect x="${-w/2}" y="-70" width="${w}" height="${size*1.6}" rx="18" fill="${col}" stroke="${INK}" stroke-width="10"/>${txt(0,-70+size*1.14,label,size,INK,{font:'Fred',sw:0})}</g>`}
function stamp(x,y,label,col,k,rot=-12,size=88){
  if(k<=0)return '';const s=lerp(2.6,1,clamp(k)),op=clamp(k*3);
  const w=label.length*size*0.66+60;
  return `<g transform="translate(${x} ${y}) rotate(${rot}) scale(${s})" opacity="${op}"><rect x="${-w/2}" y="${-size*0.85}" width="${w}" height="${size*1.5}" rx="14" fill="none" stroke="${col}" stroke-width="14"/>${txt(0,size*0.35,label,size,col,{sw:0,ls:3})}</g>`;
}
function bubble(x,y,w,h,lines,k,size=46,tail=[0,1]){
  if(k<=0)return '';const s=clamp(k,0,1.3);
  const tl=`M${-40+tail[0]*0} ${h/2-4} L${tail[0]*120-30} ${h/2+70} L40 ${h/2-4}`;
  return `<g transform="translate(${x} ${y}) scale(${s})"><path d="${tl}" fill="#fff" stroke="${INK}" stroke-width="10" stroke-linejoin="round"/><rect x="${-w/2}" y="${-h/2}" width="${w}" height="${h}" rx="44" fill="#fff" stroke="${INK}" stroke-width="10"/><path d="M-36 ${h/2-5} L36 ${h/2-5}" stroke="#fff" stroke-width="14"/>
  ${lines.map((l,i)=>txt(0,-h/2+size*1.15+i*size*1.12+ (h-lines.length*size*1.12-size*0.3)/2 - 8,l,size,INK,{font:'Fred',sw:0})).join('')}</g>`;
}
function zz(x,y,t,ph=0){let s='';for(let i=0;i<3;i++){const q=((t*0.6+ph+i/3)%1);s+=txt(x+q*60+i*10,y-q*160,'Z',40+q*30,'#cfe8ff',{sw:7,extra:`opacity="${(1-q).toFixed(2)}"`})}return s}
function phone(x,y,rot,t,glow=true){return `<g transform="translate(${x} ${y}) rotate(${rot})">${glow?`<ellipse cx="0" cy="-40" rx="130" ry="110" fill="#6fd0ff" opacity="${.22+.05*Math.sin(t*8)}"/>`:''}<rect x="-34" y="-62" width="68" height="124" rx="14" fill="#1e1e2e" stroke="${INK}" stroke-width="8"/><rect x="-26" y="-52" width="52" height="100" rx="6" fill="#7fd6ff"/>${[0,1,2,3].map(i=>{const yy=-44+(((i*26-t*90)%104)+104)%104;return `<rect x="-20" y="${yy}" width="40" height="14" rx="4" fill="#fff" opacity=".9"/>`}).join('')}</g>`}
function bigButton(x,y,press,lit){
  const dy=press*28;
  return `<g transform="translate(${x} ${y})"><rect x="-150" y="40" width="300" height="300" rx="20" fill="#3a3550" stroke="${INK}" stroke-width="12"/><rect x="-120" y="70" width="240" height="60" rx="10" fill="#ffe23a" stroke="${INK}" stroke-width="8"/>${txt(0,118,'PANIC',46,INK,{font:'Fred',sw:0})}
  <ellipse cx="0" cy="40" rx="170" ry="50" fill="#555070" stroke="${INK}" stroke-width="12"/>
  <path d="M-130 ${30+dy} C-130 ${-90+dy} 130 ${-90+dy} 130 ${30+dy} Z" fill="${lit?'#ff4d5e':'#e0243a'}" stroke="${INK}" stroke-width="12"/>
  <ellipse cx="-50" cy="${-30+dy}" rx="40" ry="18" fill="#fff" opacity=".45"/></g>`}
function alarm(t,t0,dur){if(t<t0||t>t0+dur)return '';const ph=Math.sin((t-t0)*22)>0;const fade=1-p(t,t0+dur-.25,t0+dur);
  return `<rect width="${W}" height="${H}" fill="#ff1f3d" opacity="${(ph?.38:.1)*fade}"/>
  <g transform="translate(540 120)"><circle r="70" fill="#ff3b4f" stroke="${INK}" stroke-width="10"/><g transform="rotate(${(t-t0)*720})"><path d="M0 0 L900 -180 L900 180 Z" fill="#ff6b7a" opacity="${.25*fade}"/><path d="M0 0 L-900 -180 L-900 180 Z" fill="#ff6b7a" opacity="${.25*fade}"/></g></g>`}
function food(x,y,kind,s=1,rot=0){
  const tr=`translate(${x} ${y}) rotate(${rot}) scale(${s})`;
  if(kind==='burger')return g(tr,`<path d="M-80 -10 C-80 -80 80 -80 80 -10 Z" fill="#f2a03d" stroke="${INK}" stroke-width="8"/><rect x="-86" y="-12" width="172" height="20" rx="8" fill="#5ac94a" stroke="${INK}" stroke-width="7"/><rect x="-84" y="6" width="168" height="26" rx="10" fill="#7a3b1d" stroke="${INK}" stroke-width="7"/><rect x="-80" y="30" width="160" height="28" rx="12" fill="#f2a03d" stroke="${INK}" stroke-width="8"/><circle cx="-30" cy="-50" r="4" fill="#fff"/><circle cx="10" cy="-58" r="4" fill="#fff"/><circle cx="40" cy="-44" r="4" fill="#fff"/>`);
  if(kind==='pizza')return g(tr,`<path d="M0 70 L-70 -60 Q0 -95 70 -60 Z" fill="#ffd36b" stroke="${INK}" stroke-width="8" stroke-linejoin="round"/><path d="M-70 -60 Q0 -95 70 -60" fill="none" stroke="#d9822b" stroke-width="18"/><circle cx="-15" cy="-25" r="12" fill="#e0453a"/><circle cx="20" cy="0" r="11" fill="#e0453a"/><circle cx="0" cy="30" r="9" fill="#e0453a"/>`);
  if(kind==='fries')return g(tr,`${[-40,-20,0,20,40].map((f,i)=>`<rect x="${f-8}" y="${-90+(i%2)*14}" width="16" height="90" rx="5" fill="#ffd84d" stroke="${INK}" stroke-width="5"/>`).join('')}<path d="M-60 -20 L60 -20 L45 70 L-45 70 Z" fill="#e0243a" stroke="${INK}" stroke-width="8" stroke-linejoin="round"/>`);
  if(kind==='donut')return g(tr,`<circle r="60" fill="#e6a55c" stroke="${INK}" stroke-width="8"/><circle r="52" fill="#ff8fd0"/><circle r="20" fill="#2a1450" stroke="${INK}" stroke-width="8"/><path d="M-30 -20 l10 4 M20 -35 l8 8 M30 15 l10 -4 M-25 30 l6 8" stroke="#fff" stroke-width="6" stroke-linecap="round"/>`);
  return '';
}
function vhs(x,y,label,col,s=1,rot=0){
  return g(`translate(${x} ${y}) rotate(${rot}) scale(${s})`,`<rect x="-170" y="-95" width="340" height="190" rx="14" fill="#1e1a2a" stroke="${INK}" stroke-width="10"/><rect x="-150" y="-78" width="300" height="78" rx="8" fill="${col}" stroke="${INK}" stroke-width="6"/>
   <circle cx="-70" cy="45" r="26" fill="#2e2a40" stroke="#555" stroke-width="5"/><circle cx="70" cy="45" r="26" fill="#2e2a40" stroke="#555" stroke-width="5"/><rect x="-36" y="30" width="72" height="30" rx="6" fill="#0d0b14"/>
   ${label.map((l,i)=>txt(0,-46+i*34+(label.length===1?16:0),l,label.length===1?44:28,INK,{font:'Fred',sw:0})).join('')}`)}
function shelves(x,y,w,rows,seed,lit=1){
  const r=rng(seed);let s=`<rect x="${x}" y="${y}" width="${w}" height="${rows*150+30}" fill="#2b1d42" stroke="${INK}" stroke-width="10"/>`;
  const cols=['#ff8fd0','#7fd6ff','#ffe23a','#b7f23a','#ff9b5e','#c9a6ff'];
  for(let rI=0;rI<rows;rI++){const yy=y+20+rI*150;let xx=x+16;
    while(xx<x+w-40){const tw=26+r()*16;s+=`<rect x="${xx}" y="${yy+10+r()*12}" width="${tw}" height="${118}" rx="4" fill="#1a1426" stroke="${INK}" stroke-width="5"/><rect x="${xx+4}" y="${yy+40}" width="${tw-8}" height="40" fill="${cols[Math.floor(r()*cols.length)]}" opacity="${.85*lit}"/>`;xx+=tw+4}
    s+=`<rect x="${x}" y="${yy+130}" width="${w}" height="20" fill="#4a3470" stroke="${INK}" stroke-width="6"/>`}
  return s;
}

function cam(z,fx,fy,inner,dx=0,dy=0){return `<g transform="translate(${540+dx} ${960+dy}) scale(${z}) translate(${-fx} ${-fy})">${inner}</g>`}
function badge(x,y,r,inner,label,col,rot=0){
  return g(`translate(${x} ${y}) rotate(${rot})`,`<clipPath id="bc${Math.round(x)}${Math.round(y)}"><circle r="${r}"/></clipPath><circle r="${r}" fill="url(#wallG)"/><g clip-path="url(#bc${Math.round(x)}${Math.round(y)})">${inner}</g><circle r="${r}" fill="none" stroke="${INK}" stroke-width="14"/><circle r="${r-12}" fill="none" stroke="#fff" stroke-width="5" opacity=".5"/>
   <g transform="translate(0 ${r-6}) rotate(-4)"><rect x="${-label.length*20-28}" y="-36" width="${label.length*40+56}" height="72" rx="22" fill="${col}" stroke="${INK}" stroke-width="10"/>${txt(0,20,label,48,INK,{font:'Fred',sw:0})}</g>`);
}
const DEFS=`<defs>
<linearGradient id="wallG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4a1f86"/><stop offset=".65" stop-color="#7a2a8f"/><stop offset="1" stop-color="#3a1466"/></linearGradient>
<radialGradient id="purpG" cx="50%" cy="42%" r="70%"><stop offset="0%" stop-color="#9b4dff"/><stop offset="100%" stop-color="#4f10b8"/></radialGradient>
<radialGradient id="vigG" cx="50%" cy="50%" r="70%"><stop offset="55%" stop-color="#000" stop-opacity="0"/><stop offset="100%" stop-color="#2a1a05" stop-opacity=".75"/></radialGradient>
<radialGradient id="vig2" cx="50%" cy="48%" r="75%"><stop offset="60%" stop-color="#000" stop-opacity="0"/><stop offset="100%" stop-color="#000" stop-opacity=".45"/></radialGradient>
<filter id="glow" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="30"/></filter>
<filter id="boil" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence id="boilT" type="fractalNoise" baseFrequency="0.018" numOctaves="2" seed="1" result="n"/><feDisplacementMap in="SourceGraphic" in2="n" scale="7" xChannelSelector="R" yChannelSelector="G"/></filter>
<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence id="grainT" type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed="3" stitchTiles="stitch"/><feColorMatrix type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.6 0"/><feComposite operator="in" in2="SourceGraphic"/></filter>
<filter id="paper" x="0" y="0" width="100%" height="100%"><feTurbulence id="paperT" type="fractalNoise" baseFrequency="0.035" numOctaves="3" seed="5"/><feColorMatrix type="matrix" values="0 0 0 0 1  0 0 0 0 .95  0 0 0 0 .85  0 0 0 0.9 -0.35"/><feComposite operator="in" in2="SourceGraphic"/></filter>
</defs>`;

// ---- extra hair styles for worker(): pass o.hairSvg to add custom hair on top
// ================= generic props =================
function sparkles(cx,cy,rx,ry,t,n=6,col='#fff6a8'){let s='';for(let i=0;i<n;i++){const a=i*(6.283/n)+t*1.6;s+=g(`translate(${cx+Math.cos(a)*rx} ${cy+Math.sin(a)*ry}) scale(${.55+.4*Math.sin(t*8+i)})`,`<path d="M0 -40 L10 -10 L40 0 L10 10 L0 40 L-10 10 L-40 0 L-10 -10 Z" fill="${col}" stroke="${INK}" stroke-width="5"/>`)}return s}
function speedLines(t,col='#fff',op=.35){const r=rng(Math.floor(t*12));let s='';for(let i=0;i<26;i++){const a=r()*6.283,r1=520+r()*200;s+=`<path d="M${540+Math.cos(a)*r1} ${960+Math.sin(a)*r1} L${540+Math.cos(a)*1500} ${960+Math.sin(a)*1500}" stroke="${col}" stroke-width="${6+r()*14}" opacity="${op}"/>`}return s}
function burst(col='#fff',op=.16,cx=540,cy=960,n=18){return `<g transform="translate(${cx} ${cy})" opacity="${op}">${[...Array(n)].map((_,i)=>{const a=i*2*Math.PI/n;return `<path d="M0 0 L${Math.cos(a)*1600} ${Math.sin(a)*1600} L${Math.cos(a+Math.PI/n)*1600} ${Math.sin(a+Math.PI/n)*1600} Z" fill="${col}"/>`}).join('')}</g>`}
function bg(c1,c2){return `<defs><linearGradient id="bgG${c1.slice(1)}${c2.slice(1)}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${c1}"/><stop offset="1" stop-color="${c2}"/></linearGradient></defs><rect width="${W}" height="${H}" fill="url(#bgG${c1.slice(1)}${c2.slice(1)})"/>`}
function floor(y,col,line=INK){return `<rect y="${y}" width="${W}" height="${H-y}" fill="${col}"/><path d="M0 ${y} H${W}" stroke="${line}" stroke-width="12"/>`}
// full-screen interstitial card (e.g. "DAY 3", "ROUND 2")
function titleCard(t,t0,big,small='',col='#ffe23a',bgc='#16111f'){
  const k=pop(t,t0,.35);
  return `<rect width="${W}" height="${H}" fill="${bgc}"/>`+burst(col,.10)+g(`translate(540 900) scale(${k}) rotate(-4)`,txt(0,0,big,230,col,{sw:26})+(small?txt(0,140,small,70,'#fff',{sw:12,font:'Fred'}):''));
}
// health / progress bar
function hpBar(x,y,w,val,label,col='#ff2e4d',o={}){
  const h=o.h||64;val=clamp(val);
  return `<g transform="translate(${x} ${y})">${label?txt(0,-18,label,o.ls||44,'#fff',{anchor:'start',sw:9}):''}<rect x="0" y="0" width="${w}" height="${h}" rx="${h/2}" fill="#2a1450" stroke="${INK}" stroke-width="10"/><rect x="8" y="8" width="${Math.max(0,(w-16)*val)}" height="${h-16}" rx="${(h-16)/2}" fill="${col}"/><rect x="18" y="13" width="${Math.max(0,(w-36)*val)}" height="${(h-16)*.28}" rx="6" fill="#fff" opacity=".4"/>${o.text?txt(w/2,h*.72,o.text,h*.62,'#fff',{sw:8}):''}</g>`;
}
function arrowDown(x,y,s=1,col='#ffe23a'){return g(`translate(${x} ${y}) scale(${s})`,`<path d="M0 0 L0 110 M-40 70 L0 115 L40 70" stroke="${INK}" stroke-width="30" fill="none" stroke-linecap="round" stroke-linejoin="round"/><path d="M0 0 L0 110 M-40 70 L0 115 L40 70" stroke="${col}" stroke-width="14" fill="none" stroke-linecap="round" stroke-linejoin="round"/>`)}
function exclaim(x,y,k,col='#ff2e4d'){if(k<=0)return '';return g(`translate(${x} ${y}) scale(${k})`,txt(0,0,'!',170,col,{sw:20}))}
function heart(x,y,s=1,col='#ff4d7a'){return g(`translate(${x} ${y}) scale(${s})`,`<path d="M0 30 C-60 -10 -50 -70 0 -40 C50 -70 60 -10 0 30 Z" fill="${col}" stroke="${INK}" stroke-width="8" stroke-linejoin="round"/>`)}
function door(x,y,w,h,col='#8a5a35',open=0){return `<g transform="translate(${x} ${y})"><rect x="${-w/2-14}" y="-14" width="${w+28}" height="${h+14}" fill="#2a1a10" stroke="${INK}" stroke-width="10"/>${open>0?`<rect x="${-w/2}" y="0" width="${w}" height="${h}" fill="#fff6c8"/>`:''}<g transform="scale(${1-open*.85} 1) translate(${open*-w*.08} 0)"><rect x="${-w/2}" y="0" width="${w}" height="${h}" fill="${col}" stroke="${INK}" stroke-width="10"/><circle cx="${w/2-34}" cy="${h/2}" r="12" fill="#ffd36b" stroke="${INK}" stroke-width="5"/></g></g>`}
// generic crowd of workers
function crowd(t,y,n,s,seed,o={}){const r=rng(seed);const cols=['#ff5d6c','#5ac94a','#4f7cff','#ff9b3d','#c9a6ff','#7fd6ff','#ffd84d'];const hairs=['spike','tuft','bald',''];let out='';
  for(let i=0;i<n;i++){const x=(i+.5)*W/n+(r()-.5)*40;const bob=Math.sin(t*(o.bounce||3)+i)*(o.amp??6);const up=o.cheer?(Math.sin(t*10+i)>0?-200:-140):60;
    out+=g(`translate(${x} ${y+bob+(i%2)*30}) scale(${s*(0.9+r()*.2)})`,worker({shirt:cols[Math.floor(r()*cols.length)],skin:['#f6e6cc','#e7c09a','#b98a5e','#8d5b3a'][Math.floor(r()*4)],eyes:o.eyes||'happy',mouth:o.mouth||'smile',hair:hairs[Math.floor(r()*hairs.length)],lh:[-90,up],rh:[90,up]}))}
  return out}

// ================= episode framework =================
let SEG=[],CHUNKS=[],END_CARD=0,TOTAL=0;
const S=i=>SEG[i][0], E=i=>SEG[i][1];
function initEpisode(){
  const lines=window.SCRIPT.lines;
  SEG=lines.map((l,i)=>[window.TIMING[i][0],window.TIMING[i][1],(l.cap??l.t),(l.kw||[]).map(k=>k.toUpperCase()),l.capColor||null]);
  END_CARD=SEG[SEG.length-1][1]+(window.SCRIPT.endPad??0.4);
  TOTAL=END_CARD+(window.SCRIPT.endHold??2.8);
  CHUNKS=[];
  SEG.forEach(([a,b,text,kw,cc],si)=>{
    if(!text)return;
    const words=text.toUpperCase().split(/\s+/);const groups=[];let cur=[];
    words.forEach(w=>{const len=(cur.join(' ')+' '+w).trim().length;if(cur.length>=3||(cur.length&&len>15)){groups.push(cur);cur=[]}cur.push(w)});
    if(cur.length)groups.push(cur);
    const total=groups.reduce((s,gp)=>s+gp.join(' ').length+2,0);let acc=0;
    groups.forEach(gp=>{const l=gp.join(' ').length+2;const s0=a+(b-a)*acc/total;acc+=l;const s1=a+(b-a)*acc/total;CHUNKS.push({t0:s0,t1:s1,words:gp,kw,si,cc})});
  });
  for(let i=0;i<CHUNKS.length;i++){const n=CHUNKS[i+1];CHUNKS[i].show1=n?Math.min(n.t0,CHUNKS[i].t1+0.6):CHUNKS[i].t1+0.6}
  window.META={TOTAL,END_CARD,cues:SEG.map(s=>s[0]),ends:SEG.map(s=>s[1])};
  window.render(0);
}
function captions(t){
  if(t>=END_CARD)return '';
  const c=CHUNKS.find(c=>t>=c.t0&&t<c.show1);if(!c)return '';
  const k=pop(t,c.t0,.18);const s=lerp(.7,1,k);
  const str=c.words.join(' ');const size=Math.min(112,940/(str.length*0.56));
  const base=c.cc||'#ffffff';
  let tsp=c.words.map((w,i)=>`<tspan fill="${c.kw.includes(w)?'#ffe23a':base}">${esc(w)}${i<c.words.length-1?' ':''}</tspan>`).join('');
  const y=window.SCRIPT.capY||1500;
  return `<g transform="translate(540 ${y}) scale(${s}) rotate(${(c.si%2?1:-1)*1.2})"><text x="0" y="0" font-family="Lucky" font-size="${size}" text-anchor="middle" stroke="${INK}" stroke-width="${size*0.2}" paint-order="stroke" stroke-linejoin="round" letter-spacing="2">${tsp}</text></g>`;
}
// standard end card (no comment ask)
function sceneEndCard(t){
  const t0=END_CARD;
  let s=`<rect width="${W}" height="${H}" fill="url(#purpG)"/>`;
  for(let i=0;i<4;i++){const ph=(t*.4+i/4)%1;s+=txt(150+i*260,700-ph*300,'?',80,LIME,{sw:12,extra:`opacity="${(Math.sin(ph*Math.PI)*.8).toFixed(2)}"`})}
  const k=pop(t,t0,.4);
  s+=g(`translate(540 900) scale(${.9*k})`,youHead({look:[Math.sin(t*3)*16,4],mouth:'smile',sweat:true}));
  s+=g(`translate(540 300) scale(${pop(t,t0+.15,.35)}) rotate(-3)`,txt(0,0,'NEW WHAT IF',120,'#fff',{sw:18})+txt(0,135,'EVERY DAY',120,LIME,{sw:18}));
  const ka=pop(t,t0+.5,.35),bob=Math.sin(t*6)*10;
  if(ka>0)s+=g(`translate(540 ${1420+bob}) scale(${ka})`,`<rect x="-300" y="-85" width="600" height="160" rx="80" fill="#ff2e5c" stroke="${INK}" stroke-width="14"/>${txt(0,32,'FOLLOW',104,'#fff',{sw:16})}`);
  const kh=pop(t,t0+.85,.35);
  if(kh>0)s+=g(`translate(540 1640) scale(${kh})`,txt(0,0,'@whatifbro',66,'#fff',{font:'Fred',sw:12}));
  return s;
}
function wrapSvg(body,cap=''){
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">${DEFS}
   <g filter="url(#boil)">${body}</g>
   <rect width="${W}" height="${H}" fill="#fff" filter="url(#paper)" opacity=".10"/>
   <rect width="${W}" height="${H}" fill="#000" filter="url(#grain)" opacity=".28"/>
   <rect width="${W}" height="${H}" fill="url(#vig2)"/>
   <g filter="url(#boil)">${cap}</g></svg>`;
}
// window.SCENES = [[startTime, fn], ...] in order; end card is automatic
window.render=function(t){
  let body='';
  if(t>=END_CARD&&END_CARD>0)body=sceneEndCard(t);
  else{const list=window.SCENES();let fn=list[0][1];for(const [a,f] of list){if(t>=a)fn=f}body=fn(t)}
  const st=document.getElementById('stage');st.innerHTML=wrapSvg(body,captions(t));
  st.querySelector('#boilT').setAttribute('seed',Math.floor(t*8)%7+1);
  st.querySelector('#grainT').setAttribute('seed',Math.floor(t*24)%11+1);
  return true;
};
// cover template: o={l1,l2,ep,hero:{...youHead opts}, badges:[{inner,label,col}] (up to 4), heroExtra}
function coverTemplate(o){
  let s=`<rect width="${W}" height="${H}" fill="url(#purpG)"/>`+burst('#fff',.18,540,1080);
  const f1=Math.min(100,940/(o.l1.length*.56)),f2=Math.min(128,960/(o.l2.length*.6));
  s+=g('rotate(-3 540 450)',txt(540,420,o.l1,f1,'#fff',{sw:18})+txt(540,550,o.l2,f2,LIME,{sw:20}));
  s+=g('translate(540 1110) scale(.86)',youHead(Object.assign({eyes:'huge',look:[0,6],mouth:'grit',sweat:true},o.hero||{})));
  if(o.heroExtra)s+=o.heroExtra;
  const pos=[[190,830,135,-6],[890,830,135,6],[175,1340,125,-4],[905,1340,125,4]];
  (o.badges||[]).forEach((b,i)=>{const [x,y,r,rot]=pos[i];s+=badge(x,y,r,b.inner,b.label,b.col,rot)});
  s+=g('translate(540 1555) rotate(-2)',`<rect x="-220" y="-62" width="440" height="108" rx="54" fill="#ff2e5c" stroke="${INK}" stroke-width="12"/>${txt(0,20,'EPISODE '+o.ep,68,'#fff',{sw:11})}`);
  return s;
}
window.renderCover=function(){document.getElementById('stage').innerHTML=wrapSvg(window.COVER());return true};
function you(x,y,s,o={}){return g(`translate(${x} ${y}) scale(${s})`,youBody(o))}

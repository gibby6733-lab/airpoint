// S01E01 "Nothing Sells": staging (per shot) and gag animations (ACTS). All motion is a pure function of time.
(function(){
const {ease,easeOut,lerp}=window.EZ;
const $=id=>document.getElementById(id);
const fx=(html)=>{$('fx').innerHTML=html;};
const lineOf=(seg,who,n=0)=>seg.lines.filter(l=>l.who.startsWith(who))[n];
const clamp01=x=>x<0?0:x>1?1:x;
const KIDS=(floor,k,xs,dys={})=>({floor,k,list:['marcus','gordy','wren','kenzie','tunk','dex'].map((id,i)=>({id,x:xs[i],dy:dys[id]||0}))});
const fmt=n=>Math.round(n).toLocaleString('en-US');
const ACTS={};

// ---------- SC1 ----------
const BRUNCH=(xs,y,t,scream)=>xs.map((x,i)=>`<g transform="translate(${x},${y}) rotate(${-8+i*5})"><rect x="-40" y="-14" width="80" height="28" rx="8" fill="#B6FF3B" stroke="#2B2118" stroke-width="4"/><rect x="-40" y="-14" width="80" height="28" rx="8" fill="none" stroke="#B6FF3B" stroke-width="10" opacity=".35"/></g>`).join('')+
 (scream?xs.map((x,i)=>`<g transform="translate(${x+30},${y-90+Math.sin(t*40+i)*4})" opacity="${scream}"><path d="M-46,-26 h92 v40 h-50 l-14,18 l-4,-18 h-24z" fill="#FFF" stroke="#2B2118" stroke-width="4"/><text x="0" y="2" text-anchor="middle" font-family="DejaVu Sans" font-weight="800" font-size="22" fill="#D6453D">eee!</text></g>`).join(''):'');
ACTS.brunch=(lt,D,seg,t)=>{const bite=seg.lines[0]?seg.lines[0].end:1;const sc=lt>bite-seg.start+0.15&&lt<bite-seg.start+1.2?1:0;
 fx(`<svg width="1920" height="1080">${BRUNCH([420,760,1100,1440],700-(lt>bite-seg.start?40:0),t,sc)}</svg>`);
 const tube=$('tube'); if(tube) tube.setAttribute('opacity',0.5+0.5*Math.abs(Math.sin(t*3)));
 return {shake:sc?3:0};};
ACTS.brunch2=(lt,D,seg,t)=>{fx(`<svg width="1920" height="1080">${BRUNCH([420,760,1100,1440],660,t,0)}</svg>`);};
ACTS.scribble=(lt,D,seg,t)=>{fx(`<svg width="1920" height="1080"><rect width="1920" height="1080" fill="#9B5CFF" opacity=".10"/></svg>`);return {chars:{frink:{rot:Math.sin(t*14)*(lt>0.6&&lt<1.6?1.5:0)}}};};
ACTS.promising=(lt,D)=>{const p=$('promtext');if(p){const n=Math.floor(clamp01((lt-0.3)/1.2)*10);p.textContent='PROMISING.'.slice(0,n);}};
ACTS.promising2=(lt,D)=>{ACTS.promising(lt,D);const u=$('underline'),u2=$('underline2');if(u){u.setAttribute('opacity',lt>1.7?1:0);u.setAttribute('stroke-dasharray','700');u.setAttribute('stroke-dashoffset',700*(1-clamp01((lt-1.7)/0.35)));}
 if(u2){u2.setAttribute('opacity',lt>2.2?1:0);u2.setAttribute('stroke-dasharray','640');u2.setAttribute('stroke-dashoffset',640*(1-clamp01((lt-2.2)/0.35)));}};
// ---------- SC2 ----------
ACTS.vanman=(lt,D,seg,t)=>{const v=$('van');if(v)v.setAttribute('transform',`translate(${lerp(-420,2300,ease(clamp01(lt/3.2)))},${820+Math.sin(t*22)*2})`);
 const pop=$('pop');if(pop)pop.textContent=(lt>1.6&&lt<4.4)?'4,813':'4,812';
 const walk=clamp01((lt-2.6)/3.4); const step=Math.sin(t*9)*6;
 return {chars:{man_suitcase:{dx:lerp(0,-1250,walk),dy:-Math.abs(step),rot:Math.sin(t*9)*2,op:lt<2.4?0:1}}};};
// ---------- SC3 ----------
const SLIDES=[
 ['#C9B48F','HI THERE, CITIZEN!','<circle cx="0" cy="0" r="120" fill="#F4ECD8" stroke="#2B2118" stroke-width="8"/><circle cx="-40" cy="-20" r="14" fill="#2B2118"/><circle cx="40" cy="-20" r="14" fill="#2B2118"/><path d="M-60,40 Q0,90 60,40" stroke="#2B2118" stroke-width="10" fill="none"/>'],
 ['#D8C9A6','1871','<rect x="-260" y="60" width="520" height="40" fill="#A7B08A"/><ellipse cx="0" cy="60" rx="90" ry="30" fill="#8C8781" stroke="#2B2118" stroke-width="6"/><circle cx="0" cy="-60" r="40" fill="#E8BFA0" stroke="#2B2118" stroke-width="6"/><rect x="-40" y="-20" width="80" height="80" rx="20" fill="#5E5248" stroke="#2B2118" stroke-width="6"/><rect x="-50" y="-112" width="100" height="20" fill="#2B2118"/>'],
 ['#D8C9A6','...STILL 1882','<ellipse cx="0" cy="60" rx="90" ry="30" fill="#8C8781" stroke="#2B2118" stroke-width="6"/><circle cx="0" cy="-60" r="40" fill="#E8BFA0" stroke="#2B2118" stroke-width="6"/><rect x="-40" y="-20" width="80" height="80" rx="20" fill="#5E5248" stroke="#2B2118" stroke-width="6"/><path d="M-120,-160 q60,-40 120,0" stroke="#5E5248" stroke-width="6" fill="none"/><text x="130" y="-100" font-family="DejaVu Serif" font-size="40" fill="#5E5248">...</text>'],
 ['#C9C2AE','1987','<path d="M-160,120 L0,-140 L160,120Z" fill="#111114" stroke="#9B5CFF" stroke-width="8"/>'+Array.from({length:8},(_,i)=>`<path d="M${-260+i*70},140 V60" stroke="#6E7A4C" stroke-width="8"/>`).join('')],
 ['#E8DCC2','SUPER IMPORTANT!','<text x="0" y="40" text-anchor="middle" font-family="DejaVu Serif" font-weight="700" font-size="160" fill="#D6453D">!</text>'],
 ['#E8DCC2','MEDIAN TODAY = AMERICA TOMORROW','<rect x="-300" y="-120" width="600" height="240" rx="20" fill="#8FA5B5" stroke="#2B2118" stroke-width="6"/><circle cx="-140" cy="0" r="40" fill="#FF2E93"/><circle cx="-30" cy="-30" r="30" fill="#FF2E93" opacity=".8"/><circle cx="80" cy="20" r="34" fill="#FF2E93" opacity=".7"/><circle cx="190" cy="-10" r="26" fill="#FF2E93" opacity=".6"/>'],
 ['#C9B48F','STAY AVERAGE!','<rect x="-80" y="-100" width="160" height="200" rx="30" fill="#F4ECD8" stroke="#2B2118" stroke-width="6"/><path d="M-60,60 C-30,60 -20,-70 0,-70 C20,-70 30,60 60,60" stroke="#9B5CFF" stroke-width="10" fill="none"/>'],
 ['#2B2118','','<rect x="-300" y="-180" width="600" height="360" fill="#111" /><path d="M-300,0 Q0,-60 300,30" stroke="#FFF" stroke-width="4" opacity=".4"/>']];
const slideSvg=(i,lt)=>{const s=SLIDES[i];return `<g><rect x="-560" y="-430" width="1120" height="860" fill="${s[0]}" stroke="#F4ECD8" stroke-width="14"/><g transform="translate(0,${s[1]?40:0})">${s[2]}</g>${s[1]?`<text x="0" y="-300" text-anchor="middle" font-family="DejaVu Serif" font-weight="700" font-size="${s[1].length>20?48:72}" fill="#2B2118">${s[1]}</text>`:''}<rect x="-560" y="-430" width="1120" height="860" fill="#C08040" opacity=".12"/></g>`;};
ACTS.filmstrip=(lt,D,seg,t)=>{const g=$('slides');if(!g)return;const L=seg.lines;let i=0;L.forEach((l,j)=>{if(seg.start+lt>=l.start)i=j;});
 const base=seg.id==='3.2'?0:6; const idx=Math.min(SLIDES.length-1,base+i+(seg.id==='3.2'&&i>=2?0:0));
 const wob=Math.sin(t*1.7)*3, jit=Math.sin(t*37)*1.5;
 g.setAttribute('transform',`translate(${960+jit},${520+wob}) scale(${seg.id==='3.3'&&i===1?1+0.02*Math.sin(t*30):1})`);
 g.innerHTML=slideSvg(seg.id==='3.3'&&i===1?7:idx,lt);};
ACTS.dexFreeze=(lt,D,seg,t)=>{return {chars:{dex:{sy:1+0.015*Math.sin(t*1.3)}}};};
ACTS.snapSiren=(lt,D,seg,t)=>{const pa=seg.lines.find(l=>l.who.startsWith('PA'));const ps=pa?pa.start-seg.start:99, pe=pa?pa.end-seg.start:99;
 const red=lt>ps-0.6&&lt<pe?0.18+0.12*Math.sin(t*12):0;
 fx(`<svg width="1920" height="1080"><rect width="1920" height="1080" fill="#D6453D" opacity="${red}"/></svg>`);
 const out={};
 if(lt<0.25){out.cam={x:330,y:420,z:lerp(1,2.4,easeOut(lt/0.12))};} else if(lt<0.9){out.cam={x:330,y:420,z:2.4};}
 if(lt>pe) {out.chars={};['marcus','gordy','wren','kenzie','tunk','dex'].forEach(c=>out.chars[c]={sy:1});} // Median Stare: nobody moves
 return out;};
ACTS.squeak=(lt,D,seg,t)=>{const sq=lt>D-1.4&&lt<D-0.6;fx(`<svg width="1920" height="1080"><g transform="translate(1440,830) rotate(-10)"><rect x="-44" y="-14" width="88" height="28" rx="8" fill="#B6FF3B" stroke="#2B2118" stroke-width="4"/><path d="M10,-14 l12,-12 l6,10z" fill="#E8DCC2"/></g>${sq?'<text x="1510" y="770" font-family="DejaVu Sans" font-weight="800" font-size="34" fill="#D6453D">squeak.</text>':''}</svg>`);};
// ---------- SC4 ----------
ACTS.garageEst=(lt)=>{const g=$('glow');if(g)g.setAttribute('opacity',0);const p=$('pricesign');if(p)p.setAttribute('opacity',0);};
const BOXHELD=(x,y)=>`<g transform="translate(${x},${y})"><rect x="-60" y="-46" width="120" height="92" fill="#C9A060" stroke="#2B2118" stroke-width="5"/><path d="M-60,-46 l20,-16 h80 l20,16" fill="#B8935A" stroke="#2B2118" stroke-width="5"/><path d="M-20,-30 h40" stroke="#8C6A3A" stroke-width="4"/></g>`;
ACTS.tunkEnter=(lt,D,seg,t)=>{const k=easeOut(clamp01((lt-0.4)/1.0));const dx=lerp(260,0,k);
 fx(`<svg width="1920" height="1080">${BOXHELD(1660+dx,800)}</svg>`);
 return {chars:{tunk:{dx,dy:-Math.abs(Math.sin(t*8))*(k<1?8:0)}}};};
ACTS.boxHeld=()=>{fx(`<svg width="1920" height="1080">${BOXHELD(1660,800)}</svg>`);};
ACTS.reveal=(lt,D,seg,t)=>{ACTS.boxHeld();const w=lt<1.2?0.25*(1-lt/1.2):0;$('fx').insertAdjacentHTML('beforeend',`<svg width="1920" height="1080" style="position:absolute;left:0;top:0"><rect width="1920" height="1080" fill="#FFF" opacity="${w}"/></svg>`);};
ACTS.calc=(lt,D,seg,t)=>{fx(`<svg width="1920" height="1080">${BOXHELD(1660,800)}<g transform="translate(800,700) rotate(${Math.sin(t*30)*2})"><rect x="-34" y="-52" width="68" height="104" rx="8" fill="#2B2D33" stroke="#2B2118" stroke-width="4"/><rect x="-24" y="-42" width="48" height="22" fill="#9FD4C8"/><text x="0" y="-25" text-anchor="middle" font-family="DejaVu Sans Mono" font-size="20" font-weight="700" fill="#111">${lt>1.5?'∞':'0.00'}</text></g></svg>`);};
ACTS.cash=(lt,D,seg,t)=>{const o=clamp01((lt-1.2)/0.4);let s='';for(let i=0;i<10;i++){const a=i*0.7+lt*1.5;s+=`<rect x="${1700+Math.cos(a)*60*o}" y="${640-o*120+Math.sin(a)*30}" width="60" height="30" rx="4" fill="#7DBA6A" stroke="#2B2118" stroke-width="3" transform="rotate(${i*30+lt*40} ${1700} ${640})" opacity="${o}"/>`;}
 const hum=lt>D-2.2?`<rect width="1920" height="1080" fill="#9B5CFF" opacity="${0.06+0.04*Math.sin(t*20)}"/>`:'';
 fx(`<svg width="1920" height="1080">${BOXHELD(1660,800)}${s}${hum}</svg>`);};
// ---------- SC5 ----------
const phoneScene=(who,boxOpen,extra='')=>`<div style="position:absolute;inset:0;background:#E6E0CF"></div><div style="position:absolute;left:0;right:0;top:600px;bottom:0;background:#C9C2AE"></div>
 <img src="../assets/characters/${who}" style="position:absolute;left:80px;top:160px;height:820px">${extra}`;
ACTS.stream1=(lt,D,seg,t)=>{const pin=$('phonein');if(!pin)return;const key='k1';if(pin.dataset.k!==key){pin.dataset.k=key;pin.innerHTML=phoneScene('kenzie_front_v02.svg',0,'<svg id="pbox" style="position:absolute;left:300px;top:520px" width="300" height="300" viewBox="-150 -150 300 300"></svg>');}
 const open=clamp01((lt-3.0)/0.6);$('pbox').innerHTML=window.voidBox(0,0,1.6)+(open?`<rect x="-96" y="-96" width="192" height="30" fill="#111114" stroke="#FF2E93" stroke-width="4" transform="rotate(${-open*60} -96 -80)"/>`:'');
 $('fol').textContent='2,304';$('viewers').textContent='Viewers: 4';};
ACTS.stream2=(lt,D,seg,t)=>{ACTS.stream1(4,D,seg,t);const c=$('comments');if(c)c.innerHTML=lt>0.5?`<rect x="660" y="880" width="560" height="64" rx="20" fill="#FFF" opacity=".9"/><text x="690" y="922" font-family="DejaVu Sans" font-size="28" fill="#2B2118">@user4: is this a prank</text>`:'';};
ACTS.stackIdle=(lt,D,seg,t)=>{};
ACTS.counterExplode=(lt,D,seg,t)=>{const b=$('bigcount');const k=clamp01(lt/(D-0.3));const v=k<0.15?4:k<0.35?12:k<0.55?380:k<0.75?fmt(lerp(380,9400,(k-0.55)/0.2)):'9,400';if(b){b.textContent='Viewers: '+v;b.setAttribute('font-size',110);}
 return {};};
// ---------- SC6 montage ----------
ACTS.line6=(lt,D,seg,t)=>{const g=$('glow');if(g)g.setAttribute('opacity',0.25+0.15*Math.sin(t*5));const p=$('price');};
ACTS.kevinBox=(lt,D,seg,t)=>{const pin=$('phonein');if(!pin)return;if(pin.dataset.k!=='kev'){pin.dataset.k='kev';pin.innerHTML=phoneScene('side/kevin.svg',0,'<svg id="pbox" style="position:absolute;left:330px;top:560px" width="300" height="300" viewBox="-150 -150 300 300"></svg><div id="tear" style="position:absolute;left:250px;top:360px;width:14px;height:24px;border-radius:50%;background:#7FC4FF;opacity:0"></div>');}
 $('pbox').innerHTML=window.voidBox(0,0,1.5);const tr=$('tear');if(tr){const k=clamp01((lt-1.5)/1.2);tr.style.opacity=k>0?1:0;tr.style.top=(360+k*90)+'px';}
 $('fol').textContent=fmt(lerp(2304,48000,clamp01(lt/D)));$('viewers').textContent='Viewers: '+fmt(lerp(400,9000,clamp01(lt/D)));};
ACTS.yoga=(lt,D,seg,t)=>{const pin=$('phonein');if(!pin)return;if(pin.dataset.k!=='yoga'){pin.dataset.k='yoga';pin.innerHTML=phoneScene('side/yoga_mom.svg',0,'<div style="position:absolute;left:0;right:0;top:600px;height:40px;background:#8C8781"></div>');}
 $('fol').textContent=fmt(lerp(48000,120000,clamp01(lt/D)));$('viewers').textContent='Viewers: 12,880';};
ACTS.teen=(lt,D,seg,t)=>{const pin=$('phonein');if(!pin)return;if(pin.dataset.k!=='teen'){pin.dataset.k='teen';pin.innerHTML=phoneScene('side/teen.svg',0,'<div style="position:absolute;left:380px;top:420px;width:200px;height:340px;border-radius:30px;background:#2B2D33"></div>');}
 $('fol').textContent=fmt(lerp(310000,520000,clamp01(lt/D)));$('viewers').textContent='Viewers: 88,104';};
ACTS.ledger=(lt,D)=>{const g=$('graph');if(!g)return;const k=clamp01(lt/(D-0.4));let d='M300,980';const N=40;for(let i=1;i<=N*k;i++){const x=300+i*40, y=980-Math.pow(i/N,3)*1100;d+=` L${x},${y}`;}g.setAttribute('d',d);};
ACTS.ribbon=(lt,D,seg,t)=>{const cut=lt>D*0.55;const g=$('glow');if(g)g.setAttribute('opacity',0.3);
 fx(`<svg width="1920" height="1080">${cut?`<path d="M300,620 Q240,700 260,760" stroke="#D6453D" stroke-width="16" fill="none"/><path d="M980,620 Q1040,700 1020,760" stroke="#D6453D" stroke-width="16" fill="none"/>`:'<path d="M300,620 H980" stroke="#D6453D" stroke-width="16"/><circle cx="640" cy="620" r="30" fill="#D6453D" stroke="#2B2118" stroke-width="4"/>'}</svg>`);
 return {chars:{krupp:{rot:cut?0:Math.sin(t*6)*2},town1:{dy:-Math.abs(Math.sin(t*8))*(cut?14:0)},town5:{dy:-Math.abs(Math.sin(t*8+1))*(cut?14:0)},town7:{dy:-Math.abs(Math.sin(t*8+2))*(cut?14:0)}}};};
ACTS.priceFlip=(lt,D)=>{const p=$('pricetxt'),s=$('pricesub');if(!p)return;const k=lt/D;
 if(k<0.3){p.textContent='$40';s.textContent='';}else if(k<0.55){p.textContent='$90';s.textContent='';}else{p.textContent='$200';s.textContent='LIMITED EDITION: BLACK ON BLACK';}
 const fl=(k>0.28&&k<0.32)||(k>0.53&&k<0.57);p.setAttribute('transform',fl?`translate(960,520) scale(1,0.1) translate(-960,-520)`:'');};
ACTS.counterBig=(lt,D,seg)=>{const b=$('bigcount');if(!b)return;const k=clamp01(lt/(D-0.3));const pts=[2304,48000,310000,960000];const i=Math.min(3,Math.floor(k*4));const kk=k*4-i;const v=i<3?lerp(pts[i],pts[i+1],ease(kk)):960000;b.textContent=fmt(v);};
ACTS.shame=(lt,D)=>{const s=$('shamevoid');if(s)s.setAttribute('opacity',lt>1.0?1:0);if(s)s.setAttribute('transform',`translate(0,${lt>1.0?0:-40})`);};
// ---------- SC7 ----------
ACTS.usmap=(lt,D,seg,t)=>{document.querySelectorAll('#usmap .st').forEach((r,i)=>{const on=lt*3>i*0.35;r.setAttribute('fill',on?'#FF2E93':'#4A5068');});};
// ---------- SC8 ----------
ACTS.slideBox=(lt,D,seg,t)=>{const bevSlide=seg.lines.find(l=>/house/.test(l.text));const st=bevSlide?bevSlide.start-seg.start:D;const c=$('countervoid');if(c){const k=easeOut(clamp01((lt-st)/0.6));c.setAttribute('opacity',lt>st?1:0);c.setAttribute('transform',`translate(${lerp(300,0,k)},0)`);}
 const s=$('shamevoid');if(s)s.setAttribute('opacity',1);};
ACTS.boxThere=()=>{const c=$('countervoid');if(c)c.setAttribute('opacity',1);const s=$('shamevoid');if(s)s.setAttribute('opacity',1);};
// ---------- SC9 ----------
ACTS.bedWide=(lt,D,seg,t)=>{const tb=Math.abs(Math.sin(t*25))*2;return {chars:{wren:{rot:lt>1.4&&lt<2.4?-6:lt>2.4&&lt<3.4?6:0}},shake:0.6};};
ACTS.lid=(lt,D,seg,t)=>{const k=easeOut(clamp01((lt-0.6)/1.4));fx(`<svg width="1920" height="1080"><g transform="translate(1060,${600-k*120}) rotate(${-k*35})"><rect x="-50" y="-44" width="100" height="16" fill="#111114" stroke="#FF2E93" stroke-width="3"/></g><circle cx="1000" cy="${560-k*60}" r="26" fill="#7A4A2E" stroke="#2B2118" stroke-width="4"/><circle cx="1120" cy="${560-k*60}" r="26" fill="#7A4A2E" stroke="#2B2118" stroke-width="4"/></svg>`);};
ACTS.binShove=(lt,D)=>{const b=$('binvoid');if(b)b.setAttribute('transform',`translate(${lerp(-500,0,easeOut(clamp01(lt/0.8)))},0)`);};
ACTS.taps=(lt,D,seg,t)=>{const q=$('qty'),th=$('thumb');if(!q)return;const n=1+Math.min(4,Math.floor(Math.max(0,lt-0.6)/0.55));q.textContent=n;const ph=((lt-0.6)%0.55)/0.55;if(th)th.setAttribute('cy',lt>0.6&&ph<0.3?800:840);};
// ---------- SC10 ----------
ACTS.dexStage=(lt,D,seg,t)=>{fx(`<svg width="1920" height="1080"><path d="M960,0 L740,700 L1180,700Z" fill="#FFF7D6" opacity=".22"/><g opacity=".85">${Array.from({length:6},(_,i)=>`<circle cx="${960+Math.sin(i*2.1)*260}" cy="${360+Math.cos(i*1.7)*200}" r="3" fill="#FFF"/>`).join('')}</g></svg>`);
 return {chars:{dex:{dy:0,sy:1+0.01*Math.sin(t*3)}}};};
ACTS.clap=(lt,D,seg,t)=>{const k=clamp01((lt-0.8)/1.2);document.querySelectorAll('#bg .fan').forEach(g=>{const i=+g.dataset.i;const on=(i===37)||k>((i*7)%40)/40;g.setAttribute('transform',on?`translate(0,${-Math.abs(Math.sin(t*14+i))*10})`:'');});};
ACTS.marcusIn=(lt,D,seg,t)=>{const k=easeOut(clamp01(lt/1.0));return {chars:{marcus:{dx:lerp(500,0,k),dy:-Math.abs(Math.sin(t*9))*(k<1?8:0)}}};};
ACTS.gainesUp=(lt,D,seg,t)=>({chars:{gaines:{dy:lerp(80,0,easeOut(clamp01(lt/0.6)))}}});
ACTS.wingsCount=(lt,D,seg,t)=>{fx(`<svg width="1920" height="1080"><g transform="translate(1260,320)"><rect x="-170" y="-40" width="340" height="80" rx="40" fill="#F05A9A" stroke="#2B2118" stroke-width="5"/><text x="0" y="16" text-anchor="middle" font-family="DejaVu Sans" font-weight="800" font-size="44" fill="#FFF">999,998</text></g></svg>`);};
ACTS.million=(lt,D,seg,t)=>{const b=$('bigcount');if(b)b.textContent=lt<0.8?'999,999':'1,000,000';const c=$('confetti');if(c){c.setAttribute('opacity',lt>0.8?1:0);c.querySelectorAll('.cf').forEach(r=>{const i=+r.dataset.i;const tt=lt-0.8;r.setAttribute('x',200+(i*97)%1520+Math.sin(tt*3+i)*30);r.setAttribute('y',-40+tt*(300+(i%7)*60)%1200);r.setAttribute('transform',`rotate(${tt*200+i*20} ${200+(i*97)%1520} ${-40+tt*(300+(i%7)*60)%1200})`);});}};
// ---------- SC11 ----------
const crowdJit=(t,amt)=>{const o={};['town1','town2','town3','town4','town5','town6','town7','town8','shaking_man','kevin'].forEach((c,i)=>o[c]={dx:Math.sin(t*7+i*1.7)*amt,dy:-Math.abs(Math.sin(t*9+i))*amt*0.8,rot:Math.sin(t*6+i)*amt*0.2});return o;};
ACTS.storeWide=(lt,D,seg,t)=>{const n=$('neonspill');if(n)n.setAttribute('opacity',0.10+0.04*Math.sin(t*4));return {chars:crowdJit(t,2)};};
ACTS.shakeBox=(lt,D,seg,t)=>{const o={chars:crowdJit(t,1)};o.chars.shaking_man={rot:Math.sin(t*30)*4};fx(`<svg width="1920" height="1080"></svg>`);return o;};
const flyAnim=(t,n=22)=>{const f=$('flying');if(f){f.setAttribute('opacity',1);f.querySelectorAll('.fly').forEach(g=>{const i=+g.dataset.i;if(i>=n){g.setAttribute('opacity',0);return;}g.setAttribute('opacity',1);const tt=(t+i*0.13)%1.6;const x=(i*173)%1920, y=1000-tt*900+tt*tt*420;g.setAttribute('transform',`translate(${x+tt*(i%2?200:-200)},${y}) rotate(${tt*360*(i%2?1:-1)})`);});}};
ACTS.riot=(lt,D,seg,t)=>{flyAnim(t);
 const n=$('neonspill');if(n)n.setAttribute('opacity',0.18+0.08*Math.sin(t*9));return {chars:crowdJit(t,14),shake:6};};
ACTS.boxHit=(lt,D,seg,t)=>{flyAnim(t,10);const ow=seg.lines.find(l=>/Ow/.test(l.text));const hs=ow?ow.start-seg.start-0.3:D;const k=clamp01((lt-hs+0.6)/0.6);
 fx(`<svg width="1920" height="1080">${lt<hs+0.05?window.voidBox(lerp(1500,420,k),lerp(900,330,k),0.6):''}</svg>`);return {chars:{kenzie:{rot:lt>hs&&lt<hs+0.4?-8:0},...crowdJit(t,8)},shake:lt>hs&&lt<hs+0.3?10:2};};
ACTS.fire=(lt,D,seg,t)=>{flyAnim(t,12);const f=$('fire');if(f){f.setAttribute('opacity',clamp01((lt-0.6)/0.4));f.querySelectorAll('.flame').forEach((p,i)=>p.setAttribute('transform',`scale(1,${1+0.15*Math.sin(t*14+i)})`));}return {chars:crowdJit(t,8),shake:2};};
ACTS.fireOn=(lt,D,seg,t)=>{flyAnim(t,8);const f=$('fire');if(f){f.setAttribute('opacity',1);f.querySelectorAll('.flame').forEach((p,i)=>p.setAttribute('transform',`scale(1,${1+0.15*Math.sin(t*14+i)})`));}return {chars:crowdJit(t,6)};};
ACTS.extinguish=(lt,D,seg,t)=>{flyAnim(t,lt<2.4?8:0);const walk=easeOut(clamp01(lt/1.6));const spray=lt>1.6&&lt<3.2;const done=lt>2.4;
 const f=$('fire');if(f)f.setAttribute('opacity',lt<2.0?1:0);const fo=$('foam');if(fo)fo.setAttribute('opacity',lt>2.0?1:0);
 let s='';if(spray){for(let i=0;i<30;i++){const k=((lt*3+i*0.07)%1);s+=`<circle cx="${lerp(760,1200,k)}" cy="${lerp(640,560,k)+Math.sin(i)*30*k}" r="${10+k*24}" fill="#FFF" stroke="#2B2118" stroke-width="2" opacity="${1-k*0.3}"/>`;}}
 const krFoam=done?`<g opacity="${clamp01((lt-2.4)/0.4)}">${Array.from({length:22},(_,i)=>`<circle cx="${1200+Math.sin(i*2.3)*90}" cy="${420+(i%11)*48}" r="${34+(i%3)*10}" fill="#FFF" stroke="#2B2118" stroke-width="3"/>`).join('')}</g>`:'';
 fx(`<svg width="1920" height="1080">${s}${krFoam}</svg>`);
 return {chars:{tunk:{dx:lerp(-500,0,walk),dy:-Math.abs(Math.sin(t*6))*(walk<1?6:0)},...(lt>2.4?{}:crowdJit(t,5))}};};
ACTS.foamed=(lt,D,seg,t)=>{fx(`<svg width="1920" height="1080">${Array.from({length:22},(_,i)=>`<circle cx="${1200+Math.sin(i*2.3)*90}" cy="${420+(i%11)*48}" r="${34+(i%3)*10}" fill="#FFF" stroke="#2B2118" stroke-width="3"/>`).join('')}</svg>`);const fo=$('foam');if(fo)fo.setAttribute('opacity',1);};
ACTS.backToBack=(lt,D,seg,t)=>{flyAnim(t,12);return {chars:crowdJit(t,10),shake:2};};
ACTS.panFind=(lt,D,seg,t)=>{flyAnim(t,10);const k=ease(clamp01(lt/(D-0.6)));return {cam:{x:lerp(300,1560,k),y:560,z:1.7},chars:crowdJit(t,8)};};
ACTS.stack30=(lt,D,seg,t)=>{flyAnim(t,6);let s='';for(let r=0;r<10;r++)s+=window.voidBox(1560+Math.sin(r*1.3+t*2)*6,820-r*46,0.5);fx(`<svg width="1920" height="1080">${s}<rect width="1920" height="1080" fill="#FF2E93" opacity=".06"/></svg>`);return {chars:{}};};
ACTS.freeze=(lt,D,seg,t)=>{flyAnim(t,0);fx(`<svg width="1920" height="1080"><rect width="1920" height="1080" fill="#000" opacity="${0.1*clamp01(lt/0.6)}"/></svg>`);const f=$('flying');if(f)f.setAttribute('opacity',0);};
ACTS.doors=(lt,D,seg,t)=>{const k=easeOut(clamp01((lt-0.4)/1.2));fx(`<svg width="1920" height="1080"><rect width="1920" height="1080" fill="#000" opacity=".25"/><rect x="${760-k*260}" y="260" width="${400+k*520}" height="640" fill="#FFF7E0"/><g transform="translate(960,${900})" opacity="${clamp01((lt-1.0)/0.6)}"><circle cy="-470" r="56" fill="#2B2118"/><rect x="-80" y="-410" width="160" height="300" rx="40" fill="#2B2118"/><rect x="-60" y="-110" width="50" height="110" fill="#2B2118"/><rect x="10" y="-110" width="50" height="110" fill="#2B2118"/><rect x="80" y="-330" width="60" height="80" fill="#2B2118" transform="rotate(-10 110 -290)"/></g></svg>`);};
ACTS.frinkWalk=(lt,D,seg,t)=>{const k=ease(clamp01(lt/2.2));const o={frink:{dx:lerp(500,0,k),dy:-Math.abs(Math.sin(t*5))*(k<1?5:0)}};const fade=clamp01((lt-3)/1.2);['town1','town2','town3','town4','town5','town6','town7','town8','shaking_man'].forEach((c,i)=>o[c]={dx:(i%2?1:-1)*fade*900,op:1-fade});return {chars:o};};
// ---------- SC12 ----------
ACTS.contract=(lt,D,seg,t)=>{fx(`<svg width="1920" height="1080"><g transform="translate(560,820) rotate(-6)"><rect x="-150" y="-30" width="300" height="200" fill="#F4ECD8" stroke="#2B2118" stroke-width="5"/>${[0,1,2,3,4].map(i=>`<rect x="-120" y="${-10+i*26}" width="${200+(i*31)%60}" height="7" fill="#9A968E"/>`).join('')}<text x="0" y="150" text-anchor="middle" font-family="DejaVu Sans" font-weight="800" font-size="20" fill="#2B2118">§40(c)</text></g></svg>`);};
ACTS.mirrorAd=(lt,D,seg,t)=>{const b=$('adbox');if(b)b.setAttribute('transform',`translate(960,470) scale(${3.2+0.08*Math.sin(t*2)}) rotate(${Math.sin(t)*3})`);const f=$('fine');const fl=seg.lines[1];if(f)f.setAttribute('opacity',fl&&seg.start+lt>=fl.start?1:0);};
ACTS.stare6=(lt,D,seg,t)=>{const first=seg.lines[0]?seg.lines[0].start-seg.start:D;const o={};if(lt<first)['marcus','gordy','wren','kenzie','tunk','dex'].forEach(c=>o[c]={sy:1});return {chars:o};};
// ---------- SC13/14 ----------
ACTS.golden=(lt,D,seg,t)=>{fx(`<svg width="1920" height="1080"><path d="M1920,200 L600,1080 L1920,1080Z" fill="#FFB347" opacity=".10"/>${BOXHELD(1300,840)}</svg>`);};
ACTS.counterDown=(lt,D,seg,t)=>{const b=$('bigcount');if(!b)return;const pre=seg.cfg.pre||2.6;const k=clamp01(lt/(pre-0.2));const pts=[1000000,400000,31000,2304,2303];const i=Math.min(3,Math.floor(k*4));const v=k>=1?2303:lerp(pts[i],pts[i+1],ease(k*4-i));b.textContent=fmt(v);ACTS.golden(lt,D,seg,t);};
ACTS.payback=(lt,D,seg,t)=>{const k=easeOut(clamp01((lt-0.3)/0.8));fx(`<svg width="1920" height="1080"><path d="M1920,200 L600,1080 L1920,1080Z" fill="#FFB347" opacity=".10"/>${BOXHELD(1300,840)}<g transform="translate(${lerp(1260,1560,k)},${lerp(860,830,k)})"><rect x="-50" y="-22" width="100" height="44" rx="6" fill="#7DBA6A" stroke="#2B2118" stroke-width="4"/><text x="0" y="10" text-anchor="middle" font-family="DejaVu Sans" font-weight="800" font-size="26" fill="#2B2118">$$$</text></g></svg>`);};
ACTS.lick=(lt,D,seg,t)=>{ACTS.golden(lt,D,seg,t);const k=lt>0.5&&lt<D-0.3?1:0;return {chars:{tunk:{rot:k*-12,dy:k*10}}};};
ACTS.lastBox=(lt,D,seg,t)=>{const pick=clamp01((lt-1.0)/0.8);fx(`<svg width="1920" height="1080"><path d="M1920,200 L600,1080 L1920,1080Z" fill="#FFB347" opacity=".10"/>${BOXHELD(lerp(1300,1660,ease(pick)),lerp(840,760,ease(pick)))}</svg>`);};
ACTS.glowface=(lt,D,seg,t)=>{const g=$('glowface');if(g)g.style.transform=`scale(${1+0.02*Math.sin(t*2)})`;};
ACTS.tunkLeave=(lt,D,seg,t)=>{const k=ease(clamp01((lt-0.6)/2.4));fx(`<svg width="1920" height="1080"><path d="M1920,200 L600,1080 L1920,1080Z" fill="#FFB347" opacity=".10"/>${BOXHELD(1660+k*700,760)}</svg>`);return {chars:{tunk:{dx:k*700,dy:-Math.abs(Math.sin(t*6))*(k>0&&k<1?6:0)}}};};
ACTS.gordyPoint=(lt,D,seg,t)=>{ACTS.golden(lt,D,seg,t);fx('');return {chars:{gordy:{dy:-lerp(0,40,easeOut(clamp01(lt/0.5))),rot:Math.sin(t*20)*1.5}}};};
ACTS.folder=(lt,D)=>{const a='Subjects: six.',b='Influence index: anomalous.';const k=lt;const f1=$('f1'),f2=$('f2'),f3=$('f3');if(!f1)return;f1.textContent=a.slice(0,Math.floor(clamp01(k/1.2)*a.length));f2.textContent=b.slice(0,Math.floor(clamp01((k-1.4)/1.6)*b.length));f3.textContent=k>3.6?'Promising.':'';};
ACTS.endSign=(lt,D,seg,t)=>{const p=$('pop');if(p)p.textContent='4,812';const end=clamp01((lt-(D-2.4))/1.0);fx(`<svg width="1920" height="1080"><rect width="1920" height="1080" fill="#D6453D" opacity="${lt<D-2.6?0.08+0.06*Math.sin(t*10):0}"/><rect width="1920" height="1080" fill="#000" opacity="${end}"/><text x="960" y="560" text-anchor="middle" font-family="DejaVu Serif" font-weight="700" font-size="120" fill="#F4ECD8" opacity="${end}">MEDIAN</text><text x="960" y="640" text-anchor="middle" font-family="DejaVu Sans" font-size="34" fill="#C9B48F" opacity="${end}">Episode 1 · "Nothing Sells"</text></svg>`);};

window.ACTS=ACTS;

// ================= STAGING =================
const kidsRow=(floor,k)=>KIDS(floor,k,[330,590,850,1110,1370,1630]);
const S={};
S[1]={bg:'mirror',cast:{floor:1000,k:0.72,list:[{id:'town1',x:420},{id:'kevin',x:760},{id:'town3',x:1100},{id:'town6',x:1440}]},shots:{
 '1.1':{act:'brunch',pre:0.8,post:0.3},
 '1.2':{cam:{who:'kevin',z:2.1,head:true},act:'brunch2',post:0.6},
 '1.3':{bg:'behind',cast:{floor:1080,k:0.95,list:[{id:'frink',x:300}]},act:'scribble',pre:2.0,cam:{x:700,y:560,z:1}},
 '1.4':{insert:'clipboard',act:'promising',pre:2.2}}};
S[2]={bg:'townsign',cast:{floor:1010,k:0.42,list:[{id:'man_suitcase',x:1880}]},shots:{
 '2.1':{act:'vanman',pre:4.6,post:0.6},'2.2':{skip:true}}};
S[3]={bg:'classroom',cast:{floor:1050,k:0.8,list:[...kidsRow(1050,0.8).list,{id:'okonkwo',x:1830,dy:-30,s:0.7}]},shots:{
 '3.1':{post:0.3},
 '3.2':{insert:'filmstrip',act:'filmstrip',pre:0.8},
 '3.3':{insert:'filmstrip',act:'filmstrip',post:0.8},
 '3.4':{cam:{who:'dex',z:1.6,push:1.14,head:true},act:'dexFreeze',pre:0.9},
 '3.5':{act:'snapSiren',post:1.2,cam:{x:980,y:600,z:1.05}},
 '3.6':{cam:{who:'tunk',z:1.9},act:'squeak',post:1.6}}};
const G=(list)=>({floor:1000,k:0.78,list});
const garageCast=G([{id:'wren',x:300,dy:70},{id:'dex',x:560,dy:-90},{id:'marcus',x:860},{id:'gordy',x:1060,dy:110},{id:'kenzie',x:1280},{id:'tunk',x:1660}]);
S[4]={bg:'garage',cast:garageCast,shots:{
 '4.1':{bg:'garage_ext',hideCast:true,act:'garageEst',pre:2.4},
 '4.2':{bg:'garage',cam:{who:'dex',z:1.55,head:true,y:400},post:1.2},
 '4.3':{},
 '4.4':{act:'tunkEnter',pre:1.6,cam:{x:1450,y:560,z:1.35}},
 '4.5':{act:'reveal',cam:{who:'dex',z:1.5,push:1.16,head:true}},
 '4.6':{act:'calc',cam:{who:'marcus',z:1.7,head:true}},
 '4.7':{act:'boxHeld',cam:{x:980,y:600,z:1.18}},
 '4.8':{act:'cash',cam:{who:'tunk',z:1.8,head:true},post:2.2}}};
S[5]={bg:'mall',cast:G([{id:'wren',x:200,dy:20},{id:'dex',x:560},{id:'marcus',x:780},{id:'gordy',x:1000}]),shots:{
 '5.1':{insert:'phone',act:'stream1'},
 '5.2':{insert:'phone',act:'stream2',pre:2.0},
 '5.3':{},
 '5.4':{cam:{who:'gordy',z:1.5,head:true,push:1.1}},
 '5.5':{insert:'counter',act:'counterExplode',pre:3.0},
 '5.6':{cu:'kenzie_pinpoint',cuBg:'#F05A9A',post:0.8}}};
const lineCast={floor:1010,k:0.55,list:[1,2,3,4,5,6,7,8].map((n,i)=>({id:'town'+n,x:1280+i*80,dy:-(i%2)*10}))};
S[6]={bg:'garage_ext',cast:lineCast,shots:{
 '6.1':{act:'line6',pre:2.0,wipeIn:true},
 '6.2':{insert:'phone',act:'kevinBox',pre:0.6,post:0.4},
 '6.3':{insert:'phone',act:'yoga',pre:0.4},
 '6.4':{insert:'ledger',act:'ledger',pre:2.0},
 '6.5':{bg:'garage_ext',cast:{floor:1010,k:0.62,list:[{id:'krupp',x:640},{id:'town1',x:1300},{id:'town5',x:1460},{id:'town7',x:1620}]},act:'ribbon',pre:0.6,post:1.2},
 '6.6':{insert:'price',act:'priceFlip',pre:3.2},
 '6.7':{insert:'phone',act:'teen'},
 '6.8':{insert:'counter',act:'counterBig',pre:2.6},
 '6.9':{bg:'mean',cast:{floor:960,k:0.7,list:[{id:'bev',x:1500}]},act:'shame',pre:2.4,cam:{x:1450,y:440,z:1.25}}}};
S[7]={bg:'cube',cast:{floor:1040,k:0.8,list:[{id:'frink',x:560}]},shots:{
 '7.1':{act:'usmap',pre:1.2},
 '7.2':{cam:{who:'frink',z:2.0,head:true,push:1.06},pre:1.2,post:0.6},
 '7.3':{insert:'clipboard',act:'promising2',pre:3.0}}};
S[8]={bg:'mean',cast:{floor:1000,k:0.78,list:[{id:'wren',x:720,dy:40},{id:'bev',x:1180,dy:-40,s:0.95}]},shots:{
 '8.1':{cam:{x:940,y:560,z:1.12}},
 '8.2':{act:'slideBox',cam:{x:1150,y:480,z:1.08}},
 '8.3':{act:'boxThere',cam:{who:'wren',z:1.9,head:true,push:1.05},pre:1.6}}};
S[9]={bg:'bedroom',cast:{floor:860,k:0.62,list:[{id:'wren',x:860}]},shots:{
 '9.1':{act:'bedWide',pre:3.6},
 '9.2':{act:'lid',cam:{x:1060,y:560,z:2.3},pre:2.4},
 '9.3':{cu:'wren_smile',cuBg:'#2E3550',pre:1.4,post:0.8},
 '9.4':{insert:'bin',act:'binShove',pre:1.8},
 '9.5':{insert:'cartqty',act:'taps',pre:3.0}}};
S[10]={bg:'gym',cast:{floor:700,k:0.66,list:[{id:'dex',x:960}]},shots:{
 '10.1':{act:'dexStage',cam:{who:'dex',z:1.25,head:true,push:1.08},lineScale:1.15},
 '10.2':{bg:'gym_crowd',hideCast:true,act:'clap',pre:3.0},
 '10.3':{bg:'wings',cast:{floor:1040,k:0.82,list:[{id:'kenzie',x:720},{id:'gordy',x:1180}]}},
 '10.4':{bg:'gym',cast:{floor:700,k:0.66,list:[{id:'dex',x:960}]},act:'dexStage',cam:{who:'dex',z:1.15,push:1.05}},
 '10.5':{cast:{floor:700,k:0.66,list:[{id:'dex',x:760},{id:'marcus',x:1240}]},act:'marcusIn',cam:{x:1000,y:420,z:1.2}},
 '10.6':{bg:'gym_crowd',cast:{floor:1180,k:0.75,list:[{id:'gaines',x:960}]},act:'gainesUp'},
 '10.7':{bg:'wings',cast:{floor:1040,k:0.82,list:[{id:'kenzie',x:900}]},act:'wingsCount'},
 '10.8':{cast:{floor:1040,k:0.82,list:[{id:'kenzie',x:820},{id:'younger_kid',x:1240}]}},
 '10.9':{insert:'counter',act:'million',pre:2.4}}};
const storeCrowd=[1,2,3,4,5,6,7,8].map((n,i)=>({id:'town'+n,x:120+i*240,dy:(i%2)*30}));
S[11]={bg:'valubarn',cast:{floor:1060,k:0.58,list:storeCrowd},shots:{
 '11.1':{act:'storeWide',pre:3.0,wipeIn:true},
 '11.2':{cast:{floor:1000,k:0.72,list:[{id:'dex',x:330},{id:'town3',x:760}]},cam:{x:540,y:560,z:1.25}},
 '11.3':{cast:{floor:1000,k:0.72,list:[{id:'town2',x:1180},{id:'marcus',x:1580}]},cam:{x:1380,y:560,z:1.25}},
 '11.4':{cast:{floor:1040,k:0.66,list:[...storeCrowd.slice(0,3),{id:'gordy',x:760},{id:'shaking_man',x:1120},...storeCrowd.slice(5)]},act:'shakeBox'},
 '11.5':{cast:{floor:1040,k:0.66,list:[{id:'gordy',x:760},{id:'shaking_man',x:1120}]},cam:{who:'gordy',z:1.5,head:true,push:1.18}},
 '11.6':{cast:{floor:1060,k:0.58,list:storeCrowd},act:'riot',pre:2.4},
 '11.7':{cast:{floor:1060,k:0.66,list:[{id:'town3',x:800},{id:'kevin',x:1100}]},act:'riot',pre:1.8},
 '11.8':{cast:{floor:1060,k:0.58,list:storeCrowd},act:'riot',pre:2.4},
 '11.9':{cast:{floor:1060,k:0.6,list:[...storeCrowd,{id:'kenzie',x:420,dy:-320,z:2000}]},act:'boxHit',cam:{x:420,y:420,z:1.4}},
 '11.10':{cast:{floor:1060,k:0.6,list:[...storeCrowd.slice(0,4),{id:'mallory',x:1700,z:2000}]},act:'fire'},
 '11.11':{cast:{floor:1060,k:0.66,list:[{id:'krupp',x:1200}]},act:'fireOn',cam:{x:1080,y:500,z:1.25}},
 '11.12':{cast:{floor:1060,k:0.66,list:[{id:'tunk',x:640},{id:'krupp',x:1200}]},act:'extinguish',pre:3.4,post:1.0,cam:{x:920,y:560,z:1.12}},
 '11.13':{cast:{floor:1060,k:0.66,list:[...storeCrowd,{id:'dex',x:860,z:2000},{id:'marcus',x:1060,flip:true,z:2000}]},act:'backToBack',cam:{x:960,y:560,z:1.3}},
 '11.14':{cast:{floor:1060,k:0.6,list:[...storeCrowd,{id:'wren',x:1560,z:900}]},act:'panFind',pre:2.6,noCap:true},
 '11.15':{cast:{floor:1060,k:0.66,list:[{id:'kenzie',x:300,dy:-300},{id:'dex',x:880},{id:'wren',x:1500}]},act:'stack30',cam:{x:1100,y:560,z:1.1}},
 '11.16':{cast:{floor:1060,k:0.58,list:storeCrowd},act:'freeze',pre:1.8},
 '11.17':{act:'doors',pre:2.6},
 '11.18':{cast:{floor:1060,k:0.6,list:[...storeCrowd,{id:'frink',x:1100,z:2000},{id:'gordy',x:500,z:2000},{id:'wren',x:700,z:2000},{id:'dex',x:880,z:1900}]},act:'frinkWalk',pre:1.0}}};
const mirrorKids={floor:1060,k:0.72,list:['marcus','gordy','wren','kenzie','tunk','dex'].map((id,i)=>({id,x:330+i*230}))};
S[12]={bg:'mirror',cast:{...mirrorKids,list:[...mirrorKids.list,{id:'frink',x:1760,dy:-40,s:0.85}]},shots:{
 '12.1':{cam:{x:960,y:560,z:1.0}},
 '12.2':{cam:{who:'frink',z:1.6,head:true,push:1.06}},
 '12.3':{act:'contract',cam:{who:'marcus',z:1.8,head:true}},
 '12.4':{insert:'mirrorad',act:'mirrorAd',pre:0.8},
 '12.5':{insert:'appstore',pre:2.6},
 '12.6':{act:'stare6',pre:1.2,cam:{x:960,y:600,z:1.02}}}};
const wreck={floor:1000,k:0.78,list:[{id:'wren',x:300,dy:70},{id:'gordy',x:540,dy:110},{id:'kenzie',x:780,dy:40},{id:'dex',x:1020,dy:30},{id:'marcus',x:1260},{id:'tunk',x:1680}]};
S[13]={bg:'garage_wreck',cast:wreck,shots:{
 '13.1':{act:'golden',pre:2.6},
 '13.2':{insert:'counter',insertPreOnly:true,act:'counterDown',pre:2.8},
 '13.3':{act:'payback',cam:{x:1440,y:560,z:1.35}},
 '13.4':{act:'golden',cam:{x:420,y:600,z:1.55}},
 '13.5':{act:'golden',cam:{who:'tunk',z:1.7,head:true},post:1.2},
 '13.6':{act:'lick',cam:{who:'tunk',z:1.5},post:0.6}}};
S[14]={bg:'garage_wreck',cast:wreck,shots:{
 '14.1':{act:'lastBox',pre:2.2,cam:{x:1450,y:640,z:1.5}},
 '14.2':{insert:'boxglow',act:'glowface',pre:1.4},
 '14.3':{act:'tunkLeave',pre:0.4,post:2.4,cam:{x:1500,y:560,z:1.2}},
 '14.4':{act:'gordyPoint',cam:{who:'gordy',z:1.6,head:true},post:0.6},
 '14.5':{bg:'cube_night',cast:{floor:1100,k:0.75,list:[{id:'frink',x:960,dy:60}]},pre:2.2,wipeIn:true},
 '14.6':{insert:'folder',act:'folder',pre:5.0},
 '14.7':{bg:'townsign_night',hideCast:true,act:'endSign',pre:1.0,post:3.6}}};
window.STAGING=S;
})();

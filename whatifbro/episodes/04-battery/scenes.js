// Episode 4 — What if your phone battery was your health bar?
const YELLOW_SKIN='#ffe066',YELLOW_HOOD='#ffcf1a';
function batLevel(t){
  const k=[[0,100],[S(1),100],[S(4),80],[S(5),60],[S(7),50],[S(9),30],[S(12),15],[S(15),5],[S(17),2],[S(25),2],[S(26),9],[S(28),10]];
  let v=100;for(let i=0;i<k.length;i++){if(t>=k[i][0]){const n=k[i+1];v=n?lerp(k[i][1],n[1],clamp((t-k[i][0])/.6)):k[i][1];if(n&&t<n[0]&&k[i][1]!==n[1]){v=k[i][1]}}}
  // smooth: jump to next value over .6s after its cue
  for(let i=1;i<k.length;i++){if(t>=k[i][0]&&t<k[i][0]+.6)v=lerp(k[i-1][1],k[i][1],eOut(p(t,k[i][0],k[i][0]+.6)))}
  if(t>=S(25)&&t<S(28))v=lerp(2,10,p(t,S(25),S(28)));
  return v;
}
function batteryHUD(t){
  const v=batLevel(t);const low=t>=S(9)&&t<S(25);const col=low?'#ffcf1a':v>50?'#4cd964':v>20?'#ffcf1a':'#ff3b30';
  const charging=t>=S(25);const blink=v<=5&&!charging&&Math.sin(t*8)<0;
  return g('translate(540 300)',`<rect x="-230" y="-60" width="420" height="130" rx="30" fill="#16111f" stroke="${INK}" stroke-width="10"/><rect x="200" y="-22" width="28" height="54" rx="8" fill="#16111f"/>
   <rect x="-212" y="-42" width="${Math.max(10,384*v/100)}" height="94" rx="18" fill="${blink?'#5a1010':col}"/>${txt(-20,30,Math.round(v)+'%',76,'#fff',{sw:12})}
   ${charging?`<path d="M150 -50 L100 10 L135 10 L110 70 L175 -5 L140 -5 Z" fill="#ffe23a" stroke="${INK}" stroke-width="7" stroke-linejoin="round" transform="translate(80 0)"/>`:''}`);
}
function phoneBig(x,y,s,inner,rot=0){return g(`translate(${x} ${y}) rotate(${rot}) scale(${s})`,`<rect x="-200" y="-380" width="400" height="760" rx="60" fill="#1e1e2e" stroke="${INK}" stroke-width="14"/><rect x="-176" y="-350" width="352" height="700" rx="40" fill="#f4f4ff"/><rect x="-60" y="-345" width="120" height="30" rx="15" fill="#1e1e2e"/>${inner}`)}
function couch(x,y){return `<g transform="translate(${x} ${y})"><rect x="-420" y="-160" width="840" height="200" rx="60" fill="#c9a6ff" stroke="${INK}" stroke-width="12"/><rect x="-460" y="-60" width="920" height="200" rx="50" fill="#a07ee8" stroke="${INK}" stroke-width="12"/><rect x="-400" y="140" width="40" height="80" fill="${INK}"/><rect x="360" y="140" width="40" height="80" fill="${INK}"/></g>`}
function outlet(x,y,s=1,glow=0){return g(`translate(${x} ${y}) scale(${s})`,`${glow?`<circle r="${220+Math.sin(glow*6)*12}" fill="#fff8c0" opacity=".35"/><circle r="140" fill="#fff8c0" opacity=".45"/>`:''}<rect x="-80" y="-110" width="160" height="220" rx="22" fill="#f4f4f4" stroke="${INK}" stroke-width="10"/><rect x="-36" y="-60" width="14" height="40" rx="4" fill="${INK}"/><rect x="22" y="-60" width="14" height="40" rx="4" fill="${INK}"/><path d="M-14 40 A14 14 0 0 1 14 40 V60 H-14 Z" fill="${INK}"/>`)}
function plug(x,y,s=1,rot=0){return g(`translate(${x} ${y}) rotate(${rot}) scale(${s})`,`<path d="M0 60 Q0 300 -200 380" stroke="#f4f4f4" stroke-width="40" fill="none" stroke-linecap="round"/><path d="M0 60 Q0 300 -200 380" stroke="${INK}" stroke-width="54" fill="none" stroke-linecap="round" opacity=".25"/><rect x="-60" y="-80" width="120" height="150" rx="20" fill="#f4f4f4" stroke="${INK}" stroke-width="10"/><rect x="-36" y="-150" width="72" height="80" rx="8" fill="#c8ccd6" stroke="${INK}" stroke-width="8"/><rect x="-22" y="-140" width="44" height="22" fill="${INK}"/>`)}
function bedroom(){return bg('#bfe9ff','#8fd0ff')+`<rect x="660" y="260" width="300" height="300" rx="16" fill="#fff6c8" stroke="${INK}" stroke-width="12"/><circle cx="810" cy="410" r="70" fill="#ffd23a"/><path d="M810 260 V560 M660 410 H960" stroke="${INK}" stroke-width="10"/>`+floor(1280,'#a8693a')}
function lowYou(t,o={}){const low=t>=S(10)&&t<S(25);return Object.assign(low?{skin:YELLOW_SKIN,hood:YELLOW_HOOD}:{},o)}

window.SCENES=()=>[
 [0,t=>{ // hook
   const z=lerp(1,1.12,p(t,0,S(1)));
   let s=bg('#9b4dff','#4f10b8')+burst('#fff',.15,540,960);
   s+=g('translate(540 1000) scale(.9)',youHead({eyes:'huge',look:[0,-30],mouth:'o',sweat:true}));
   return cam(z,540,960,s)+batteryHUD(t);
 }],
 [S(1),t=>{ // unstoppable + backflip
   let s=bedroom()+sparkles(540,800,330,330,t,6);
   const flip=p(t,S(3)+.1,S(3)+1.0);const jump=Math.sin(flip*Math.PI)*380;
   s+=g(`translate(540 ${820-jump}) rotate(${eIO(flip)*360} 0 300)`,g('scale(.48)',youBody({eyes:'open',mouth:'smile',sweat:false,wave:t<S(3)?110+Math.sin(t*8)*15:null,brows:'angry'})));
   if(t>=S(2))s=s; // keep
   let out=s;
   if(t>=S(2)&&t<S(3))out+=g(`translate(540 560) scale(${pop(t,S(2),.3)}) rotate(-5)`,txt(0,0,'UNSTOPPABLE',120,'#ffd23a',{sw:18}));
   if(t>=S(3)+1.0)out+=g(`translate(540 560) scale(${pop(t,S(3)+1.0,.3)}) rotate(4)`,txt(0,0,'FIRST TRY!',120,LIME,{sw:18}));
   return out+batteryHUD(t);
 }],
 [S(4),t=>{ // couch scrolling, two hours, knees
   let s=bg('#ffcf9e','#f4a86c')+floor(1280,'#8a5530')+couch(540,1180);
   const lat=t>=S(5);
   s+=g(`translate(540 ${lat?820:800}) scale(.46)`,youBody({eyes:lat?'huge':'open',look:[0,30],mouth:'flat',sweat:lat,wave:30}));
   s+=phone(660,830,-10,t,true);
   if(t>=S(5)){const kc=pop(t,S(5),.3);s+=g(`translate(820 420) scale(${kc})`,`<circle r="130" fill="#fff" stroke="${INK}" stroke-width="12"/><path d="M0 0 V-90" stroke="${INK}" stroke-width="14" stroke-linecap="round" transform="rotate(${(t-S(5))*720})"/><path d="M0 0 L60 0" stroke="${INK}" stroke-width="14" stroke-linecap="round" transform="rotate(${(t-S(5))*60})"/>`)+txt(820,620,'+2 HOURS',70,'#ff2e4d',{sw:12})}
   if(t>=S(6)){[0,1].forEach(i=>{const k=pop(t,S(6)+.4+i*.5,.25);if(k>0)s+=g(`translate(${430+i*240} ${1150}) scale(${k}) rotate(${i?8:-8})`,`<rect x="-110" y="-45" width="220" height="80" rx="20" fill="#fff" stroke="${INK}" stroke-width="8"/>`+txt(0,15,'*CREAK*',44,INK,{font:'Fred',sw:0}))})}
   return s+batteryHUD(t);
 }],
 [S(7),t=>{ // friend asks for charger, you hiss
   let s=bg('#ffd6f0','#ff9ad5')+floor(1280,'#7a4a8a');
   const hiss=t>=S(8);
   s+=g(`translate(300 840) scale(.46)`,youBody({eyes:hiss?'huge':'open',mouth:hiss?'grit':'flat',brows:hiss?'angry':null,sweat:false,look:[30,0]}));
   s+=g(`translate(${hiss?820:760} 1020) scale(1.2)`,worker({shirt:'#4f7cff',eyes:hiss?'frantic':'happy',mouth:hiss?'o':'smile',hair:'tuft',lh:[-140,-20],rh:[90,60]}));
   s+=g('translate(560 1080) rotate(-20)',`<rect x="-40" y="-25" width="80" height="50" rx="10" fill="#fff" stroke="${INK}" stroke-width="7"/><path d="M40 0 Q120 0 160 80" stroke="#fff" stroke-width="14" fill="none"/>`);
   if(!hiss&&t>=S(7)+1.2)s+=bubble(720,560,560,170,['CAN I BORROW','YOUR CHARGER?'],eBack(p(t,S(7)+1.2,S(7)+1.5)),50);
   if(hiss)s+=g(`translate(320 500) scale(${pop(t,S(8),.3)}) rotate(-8)`,txt(0,0,'HSSSSS',150,'#ff2e4d',{sw:20}));
   return cam(1,540,960,s,...shake(t,S(8),.5,18))+batteryHUD(t);
 }],
 [S(9),t=>{ // low power: yellow, slow
   let s=bg('#d8f0ff','#a8d8f0')+floor(1280,'#7d8496');
   if(t<S(11)){
     const kt=pop(t,S(9)+.4,.3);
     s+=phoneBig(780,620,.55,txt(0,-200,'Low Power',40,INK,{font:'Fred',sw:0})+`<rect x="-110" y="-150" width="220" height="90" rx="45" fill="${t>=S(9)+.9?'#ffcf1a':'#ccc'}" stroke="${INK}" stroke-width="6"/><circle cx="${t>=S(9)+.9?60:-60}" cy="-105" r="38" fill="#fff" stroke="${INK}" stroke-width="5"/>`,6);
     s+=you(330,800,.46,lowYou(t,{eyes:t>=S(10)?'huge':'open',mouth:t>=S(10)?'o':'flat',sweat:t>=S(10)}));
     if(t>=S(10))s+=sparkles(330,950,250,330,t,5,'#ffe066');
     return s+batteryHUD(t);}
   // slow motion
   const walk=(t-S(11))*30;const blink=((t-S(11))%2.2)<1.1;
   s+=`<rect x="0" y="1270" width="1080" height="20" fill="#5a5f6e"/>`;
   s+=you(200+walk,820,.44,lowYou(t,{eyes:blink?'closed':'open',mouth:'flat',sweat:false}));
   const sx=lerp(120,900,p(t,S(11),S(12)));
   s+=g(`translate(${sx} 1250) scale(.9)`,`<ellipse cx="0" cy="0" rx="70" ry="30" fill="#b7f23a" stroke="${INK}" stroke-width="7"/><circle cx="10" cy="-40" r="44" fill="#d9a66b" stroke="${INK}" stroke-width="8"/><path d="M10 -40 m-20 0 a20 20 0 1 0 20 -20" fill="none" stroke="${INK}" stroke-width="6"/><path d="M-60 -10 L-80 -50 M-70 -10 L-100 -40" stroke="${INK}" stroke-width="6"/>`)+txt(sx,1120,'ZOOM',50,'#fff',{sw:9});
   if(t>=S(11)+3.2)s+=g('translate(540 520)',txt(0,0,'...SLOWER',110,'#ffcf1a',{sw:16}));
   return s+batteryHUD(t);
 }],
 [S(12),t=>{ // popup
   let s=bg('#d8f0ff','#a8d8f0')+floor(1280,'#7d8496');
   s+=g('translate(540 1000) scale(.8)',youHead(lowYou(t,{eyes:'huge',mouth:'grit',sweat:true})));
   const closed=t>=S(14)+.5&&t<S(14)+.9;
   const big=t>=S(14)+.9;
   const kp=pop(t,S(12)+1.0,.3);
   if(kp>0&&!closed){const sc=big?1.3:1;s+=`<rect width="${W}" height="${H}" fill="#000" opacity=".25"/>`+g(`translate(540 ${big?820:860}) scale(${kp*sc})`,`<rect x="-330" y="-190" width="660" height="380" rx="44" fill="#f2f2f7" stroke="${INK}" stroke-width="10"/>${txt(0,-90,'Battery Low',62,INK,{font:'Fred',sw:0})}${txt(0,-20,'15% remaining',40,'#555',{font:'Fred',sw:0})}<path d="M-330 60 H330" stroke="#bbb" stroke-width="4"/>${txt(0,140,'Close',54,'#0a7aff',{font:'Fred',sw:0})}`)}
   if(t>=S(14)&&t<S(14)+.5)s+=g(`translate(540 1000)`,`<circle r="40" fill="#0a7aff" opacity=".35"/>`);
   return s+batteryHUD(t);
 }],
 [S(15),t=>{ // the will
   let s=`<rect width="${W}" height="${H}" fill="#2a1a10"/>`+`<rect x="0" y="1100" width="${W}" height="820" fill="#6b4226"/>`;
   s+=g('translate(540 820) rotate(-3)',`<rect x="-340" y="-440" width="680" height="880" fill="#fff8e6" stroke="${INK}" stroke-width="12"/>${txt(0,-330,'MY WILL',100,INK,{sw:0})}${[...Array(8)].map((_,i)=>`<path d="M-280 ${-230+i*80} H280" stroke="#cbd" stroke-width="4"/>`).join('')}`+
     (t>=S(15)+.9?txt(-260,-170,'I LEAVE',56,INK,{font:'Fred',sw:0,anchor:'start'}):'')+(t>=S(16)?txt(-260,-90,'EVERYTHING',56,INK,{font:'Fred',sw:0,anchor:'start'}):'')+(t>=S(16)+1.4?txt(-260,-10,'TO MY CHARGER',56,'#d1252f',{font:'Fred',sw:0,anchor:'start'})+g('translate(0 220)',plug(0,0,.9,0)+heart(110,-150,1.2)):''));
   s+=g(`translate(${760+Math.sin(t*20)*10} ${900+Math.cos(t*17)*8}) rotate(30)`,`<rect x="-14" y="-150" width="28" height="220" fill="#ffd23a" stroke="${INK}" stroke-width="7"/><path d="M-14 70 L0 110 L14 70 Z" fill="#f6d7a8" stroke="${INK}" stroke-width="6"/>`);
   return s+batteryHUD(t);
 }],
 [S(17),t=>{ // dark hallway, the light, crawl
   let s=`<rect width="${W}" height="${H}" fill="#07060f"/>`;
   const k=p(t,S(17)+.5,S(18));
   s+=outlet(820,980,1.0,k>0?t:0);
   if(t>=S(18))s+=g(`translate(820 760) scale(${pop(t,S(18),.3)})`,txt(0,0,'OUTLET',80,'#fff8c0',{sw:12}));
   const crawl=t>=S(19)?eIO(p(t,S(19),S(20)+.3)):0;
   s+=g(`translate(${lerp(160,560,crawl)+Math.sin(t*8)*6} 1180) rotate(-70) scale(.36)`,youBody(lowYou(t,{eyes:'huge',mouth:'grit',sweat:true,wave:170})));
   return s+batteryHUD(t);
 }],
 [S(20),t=>{ // the usb flip saga
   let s=`<rect width="${W}" height="${H}" fill="#1a1530"/>`+burst('#fff',.06);
   s+=outlet(540,520,1.6,0);
   const tries=[[S(20)+.4,S(21)],[S(22),S(23)],[S(24),S(24)+.9]];
   let rot=0,yy=1150;
   if(t>=S(22))rot=180;if(t>=S(24))rot=0;
   const near=tries.some(([a,b])=>t>=a&&t<b+.4);
   yy=near?950:1150;
   const flipping=(t>=S(22)&&t<S(22)+.3)||(t>=S(24)&&t<S(24)+.3);
   s+=plug(540,yy,1.2,flipping?lerp(0,180,p(t,t>=S(24)?S(24):S(22),(t>=S(24)?S(24):S(22))+.3)):rot);
   [[S(21),'X','#ff2e4d'],[S(23),'X','#ff2e4d']].forEach(([tt,l,c],i)=>{if(t>=tt&&t<tt+.9)s+=g(`translate(540 760) scale(${pop(t,tt,.2)})`,txt(0,60,l,260,c,{sw:22}))});
   if(t>=S(24)+.9){s+=g(`translate(540 760) scale(${pop(t,S(24)+.9,.3)})`,`<circle r="120" fill="#4cd964" stroke="${INK}" stroke-width="12"/><path d="M-55 0 L-15 40 L60 -45" stroke="#fff" stroke-width="26" fill="none" stroke-linecap="round" stroke-linejoin="round"/>`)+txt(540,1480-150,'???',90,'#ffd23a',{sw:14})}
   return s+batteryHUD(t);
 }],
 [S(25),t=>{ // charging, alive, update
   let s=bg('#9bffb0','#3fc26a')+burst('#fff',.25);
   s+=outlet(900,900,.8,0)+`<path d="M900 960 Q900 1200 640 1150" stroke="#f4f4f4" stroke-width="26" fill="none"/>`;
   const alive=t>=S(26);
   s+=you(540,800,.46,{eyes:alive?'open':'closed',mouth:alive?'smile':'flat',sweat:false,wave:alive?140+Math.sin(t*9)*15:null});
   if(t>=S(25))s+=g('translate(540 520)',`<path d="M40 -120 L-60 20 L0 20 L-40 140 L80 -10 L20 -10 Z" fill="#ffe23a" stroke="${INK}" stroke-width="10" stroke-linejoin="round" transform="scale(${1+.08*Math.sin(t*10)})"/>`);
   if(alive)s+=sparkles(540,900,330,330,t,6);
   let out=s;
   if(t>=S(27)+.5){const k=pop(t,S(27)+.5,.35);out+=`<rect width="${W}" height="${H}" fill="#000" opacity="${.5*clamp(k)}"/>`+g(`translate(540 820) scale(${k})`,`<rect x="-400" y="-280" width="800" height="560" rx="50" fill="#f2f2f7" stroke="${INK}" stroke-width="12"/>${txt(0,-170,'Software Update',64,INK,{font:'Fred',sw:0})}${txt(0,-90,'DO NOT UNPLUG',62,'#ff3b30',{font:'Fred',sw:0})}`+hpBar(-300,0,600,(t-S(27))*.004,'',`#0a7aff`,{h:56})+(t>=S(29)?txt(0,180,'4 HOURS LEFT',64,'#ff3b30',{sw:0,font:'Fred'}):txt(0,180,'Estimating...',50,'#555',{sw:0,font:'Fred'})))}
   if(t>=S(30)){out=bg('#3a2c5e','#1e1636')+floor(1280,'#2a1450')+outlet(140,900,.6,0)+`<path d="M140 950 Q160 1100 300 1100" stroke="#f4f4f4" stroke-width="18" fill="none"/>`+you(330,820,.42,{eyes:'open',mouth:'flat',sweat:true})+
      g('translate(760 1060) scale(.9)',worker({shirt:'#ff5d6c',eyes:'happy',mouth:'grin',hair:'spike',lh:[-90,-160],rh:[90,-160]})+'')+g('translate(940 1080) scale(.8)',worker({shirt:'#4f7cff',eyes:'happy',mouth:'grin',hair:'tuft',lh:[-90,-150],rh:[90,-150]}))+txt(820,560,'PARTY',100,'#ff9ad5',{sw:14})+[...Array(6)].map((_,i)=>`<circle cx="${620+i*80}" cy="${400+((i*37)%60)}" r="16" fill="${['#ff2e4d','#ffd23a','#7fd6ff'][i%3]}" opacity="${Math.sin(t*8+i)>0?1:.3}"/>`).join('')}
   return out+batteryHUD(t);
 }],
];

window.COVER=()=>coverTemplate({l1:'WHAT IF YOUR BATTERY',l2:'WAS YOUR HEALTH?',ep:4,
  hero:{eyes:'huge',mouth:'grit',skin:'#ffe066',hood:'#ffcf1a'},
  heroExtra:g('translate(540 680) scale(.7)',`<rect x="-230" y="-60" width="420" height="130" rx="30" fill="#16111f" stroke="${INK}" stroke-width="10"/><rect x="200" y="-22" width="28" height="54" rx="8" fill="#16111f"/><rect x="-212" y="-42" width="40" height="94" rx="18" fill="#ff3b30"/>${txt(-20,30,'1%',76,'#fff',{sw:12})}`),
  badges:[
   {inner:txt(0,40,'100%',90,'#4cd964',{sw:12}),label:'7 AM',col:'#4cd964'},
   {inner:txt(0,40,'HSSS',90,'#ff2e4d',{sw:12}),label:'CHARGER?',col:'#ff9ad5'},
   {inner:outlet(0,0,.8,1),label:'THE LIGHT',col:'#fff8c0'},
   {inner:plug(0,30,.7,180),label:'WRONG WAY',col:'#ff5d6c'},
  ]});

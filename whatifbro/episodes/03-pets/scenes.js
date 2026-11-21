// Episode 3 — What if you could hear your pet's thoughts?
function dog(x,y,s,o={},t=0){
  const wag=Math.sin(t*(o.wagSpeed||14))*(o.wag??25);const sad=o.mood==='sad',happy=o.mood!=='sad';
  const eyes=sad?`<ellipse cx="-38" cy="-160" rx="17" ry="20" fill="${INK}"/><ellipse cx="38" cy="-160" rx="17" ry="20" fill="${INK}"/><circle cx="-32" cy="-168" r="6" fill="#fff"/><circle cx="44" cy="-168" r="6" fill="#fff"/><path d="M-60 -190 L-20 -182 M60 -190 L20 -182" stroke="${INK}" stroke-width="8" stroke-linecap="round"/><path d="M-40 -138 q-4 20 -8 30" stroke="#7fd6ff" stroke-width="10" stroke-linecap="round"/>`
    :`<circle cx="-38" cy="-165" r="${o.big?26:20}" fill="${INK}"/><circle cx="38" cy="-165" r="${o.big?26:20}" fill="${INK}"/><circle cx="-30" cy="-174" r="8" fill="#fff"/><circle cx="46" cy="-174" r="8" fill="#fff"/>`;
  const tongue=happy&&!o.paper?`<path d="M-18 -92 Q0 -40 18 -92 Z" fill="#ff7a9a" stroke="${INK}" stroke-width="6"/>`:'';
  const paper=o.paper?`<g transform="translate(0 -95) rotate(-8)"><rect x="-80" y="-10" width="160" height="110" fill="#fff" stroke="${INK}" stroke-width="7"/><path d="M-60 15 H60 M-60 40 H60 M-60 65 H30" stroke="#9aa" stroke-width="6"/>${txt(0,8,'HOMEWORK',20,'#d1252f',{font:'Fred',sw:0})}<path d="M40 -10 L60 20 L80 -10" fill="#f4e4c8" stroke="${INK}" stroke-width="5"/></g>`:'';
  return g(`translate(${x} ${y}) scale(${s})`,`
   <path d="M90 60 Q170 ${20-wag} ${190} ${-60-wag}" fill="none" stroke="${INK}" stroke-width="36" stroke-linecap="round"/><path d="M90 60 Q170 ${20-wag} ${190} ${-60-wag}" fill="none" stroke="#e8a85a" stroke-width="20" stroke-linecap="round"/>
   <ellipse cx="0" cy="60" rx="125" ry="135" fill="#e8a85a" stroke="${INK}" stroke-width="10"/><ellipse cx="0" cy="80" rx="70" ry="90" fill="#f6d7a8"/>
   <ellipse cx="-55" cy="185" rx="42" ry="28" fill="#f6d7a8" stroke="${INK}" stroke-width="8"/><ellipse cx="55" cy="185" rx="42" ry="28" fill="#f6d7a8" stroke="${INK}" stroke-width="8"/>
   <ellipse cx="-105" cy="-130" rx="40" ry="85" fill="#a8693a" stroke="${INK}" stroke-width="9" transform="rotate(${sad?25:12} -105 -170)"/><ellipse cx="105" cy="-130" rx="40" ry="85" fill="#a8693a" stroke="${INK}" stroke-width="9" transform="rotate(${sad?-25:-12} 105 -170)"/>
   <circle cx="0" cy="-150" r="110" fill="#e8a85a" stroke="${INK}" stroke-width="10"/>
   <ellipse cx="0" cy="-105" rx="60" ry="45" fill="#f6d7a8" stroke="${INK}" stroke-width="7"/><ellipse cx="0" cy="-125" rx="22" ry="15" fill="${INK}"/>
   ${eyes}${tongue}${paper}`);
}
function cat(x,y,s,o={},t=0){
  const eyesK=o.eyes||'meh';const tail=Math.sin(t*2)*15;
  let eyes='';
  if(eyesK==='meh')eyes=`<path d="M-62 -150 Q-38 -168 -14 -150 Q-38 -138 -62 -150 Z M14 -150 Q38 -168 62 -150 Q38 -138 14 -150 Z" fill="#b7f23a" stroke="${INK}" stroke-width="6"/><rect x="-41" y="-160" width="6" height="18" rx="3" fill="${INK}"/><rect x="35" y="-160" width="6" height="18" rx="3" fill="${INK}"/><path d="M-66 -158 H-10 M10 -158 H66" stroke="${INK}" stroke-width="8" stroke-linecap="round"/>`;
  else if(eyesK==='wide')eyes=`<circle cx="-38" cy="-150" r="24" fill="#b7f23a" stroke="${INK}" stroke-width="6"/><circle cx="38" cy="-150" r="24" fill="#b7f23a" stroke="${INK}" stroke-width="6"/><rect x="-42" y="-168" width="8" height="36" rx="4" fill="${INK}"/><rect x="34" y="-168" width="8" height="36" rx="4" fill="${INK}"/>`;
  else if(eyesK==='glow')eyes=`<path d="M-62 -150 Q-38 -170 -14 -150 Q-38 -136 -62 -150 Z M14 -150 Q38 -170 62 -150 Q38 -136 14 -150 Z" fill="#fff35a"/><rect x="-41" y="-160" width="6" height="18" rx="3" fill="${INK}"/><rect x="35" y="-160" width="6" height="18" rx="3" fill="${INK}"/>`;
  const col=o.col||'#8a8f9e';
  const suit=o.suit?`<path d="M-95 20 Q0 -30 95 20 L110 190 L-110 190 Z" fill="#2b2d3a" stroke="${INK}" stroke-width="9"/><path d="M-30 -20 L0 60 L30 -20 Z" fill="#fff" stroke="${INK}" stroke-width="6"/><path d="M-10 -10 L0 50 L10 -10 Z" fill="#d1252f"/>`:'';
  const paw=o.paw?`<g transform="translate(${o.paw[0]} ${o.paw[1]})"><path d="M-60 40 L0 0" stroke="${INK}" stroke-width="44" stroke-linecap="round"/><path d="M-60 40 L0 0" stroke="${col}" stroke-width="28" stroke-linecap="round"/><circle r="26" fill="${col}" stroke="${INK}" stroke-width="8"/></g>`:'';
  return g(`translate(${x} ${y}) scale(${s})`,`
   <path d="M80 160 Q220 140 200 ${30+tail} Q190 ${-20+tail} 150 ${0+tail}" fill="none" stroke="${INK}" stroke-width="34" stroke-linecap="round"/><path d="M80 160 Q220 140 200 ${30+tail} Q190 ${-20+tail} 150 ${0+tail}" fill="none" stroke="${col}" stroke-width="20" stroke-linecap="round"/>
   <path d="M-100 190 Q-120 20 0 0 Q120 20 100 190 Z" fill="${col}" stroke="${INK}" stroke-width="10"/><ellipse cx="0" cy="110" rx="50" ry="70" fill="#d8dbe4"/>${suit}
   <ellipse cx="-50" cy="190" rx="38" ry="22" fill="${col}" stroke="${INK}" stroke-width="8"/><ellipse cx="50" cy="190" rx="38" ry="22" fill="${col}" stroke="${INK}" stroke-width="8"/>
   <path d="M-90 -170 L-80 -270 L-20 -215 Z M90 -170 L80 -270 L20 -215 Z" fill="${col}" stroke="${INK}" stroke-width="9" stroke-linejoin="round"/><path d="M-75 -185 L-72 -240 L-40 -212 Z M75 -185 L72 -240 L40 -212 Z" fill="#ffb3c7"/>
   <ellipse cx="0" cy="-130" rx="105" ry="92" fill="${col}" stroke="${INK}" stroke-width="10"/>
   ${eyes}<path d="M-8 -118 L8 -118 L0 -108 Z" fill="#ff8fa3" stroke="${INK}" stroke-width="4"/><path d="M0 -108 Q-12 -92 -22 -100 M0 -108 Q12 -92 22 -100" fill="none" stroke="${INK}" stroke-width="5" stroke-linecap="round"/>
   <path d="M-40 -110 L-110 -120 M-40 -102 L-108 -95 M40 -110 L110 -120 M40 -102 L108 -95" stroke="${INK}" stroke-width="4"/>
   ${o.glasses?`<g fill="none" stroke="${INK}" stroke-width="6"><circle cx="-38" cy="-150" r="28"/><circle cx="38" cy="-150" r="28"/><path d="M-10 -150 H10"/></g>`:''}${paw}`);
}
function fish(x,y,s,flip=false,t=0,o={}){const f=Math.sin(t*10)*10;return g(`translate(${x} ${y}) scale(${flip?-s:s} ${s})`,`<path d="M70 0 L140 ${-50+f} L140 ${50+f} Z" fill="#ff9b3d" stroke="${INK}" stroke-width="8" stroke-linejoin="round"/><ellipse cx="0" cy="0" rx="90" ry="60" fill="#ffae4d" stroke="${INK}" stroke-width="9"/><path d="M-10 -55 Q20 -90 50 -50" fill="#ff9b3d" stroke="${INK}" stroke-width="7"/><circle cx="-45" cy="-12" r="${o.big?26:20}" fill="#fff" stroke="${INK}" stroke-width="6"/><circle cx="${-50+Math.sin(t*3)*6}" cy="-12" r="${o.big?8:9}" fill="${INK}"/><ellipse cx="-80" cy="20" rx="8" ry="${o.o?14:5}" fill="${INK}"/>`)}
function bowl(x,y,s,inner){return g(`translate(${x} ${y}) scale(${s})`,`<clipPath id="bowlC"><circle r="300"/></clipPath><circle r="300" fill="#bfe9ff" opacity=".55"/><g clip-path="url(#bowlC)"><rect x="-320" y="-160" width="640" height="500" fill="#7fd6ff" opacity=".55"/>${inner}<rect x="-320" y="230" width="640" height="100" fill="#e8d29a"/></g><circle r="300" fill="none" stroke="${INK}" stroke-width="12"/><path d="M-200 -190 Q-240 -120 -230 -40" stroke="#fff" stroke-width="18" fill="none" stroke-linecap="round" opacity=".7"/><ellipse cx="0" cy="-260" rx="170" ry="30" fill="none" stroke="${INK}" stroke-width="10"/>`)}
function castle(x,y,s){return g(`translate(${x} ${y}) scale(${s})`,`<rect x="-70" y="-90" width="140" height="120" fill="#c9a6ff" stroke="${INK}" stroke-width="8"/><rect x="-100" y="-150" width="50" height="180" fill="#c9a6ff" stroke="${INK}" stroke-width="8"/><rect x="50" y="-150" width="50" height="180" fill="#c9a6ff" stroke="${INK}" stroke-width="8"/><path d="M-30 30 V-20 A30 30 0 0 1 30 -20 V30" fill="#5b3fa8" stroke="${INK}" stroke-width="6"/><path d="M-100 -150 v-20 h12 v12 h13 v-12 h12 v20 M50 -150 v-20 h12 v12 h13 v-12 h12 v20" fill="#c9a6ff" stroke="${INK}" stroke-width="6"/>`)}
function room(night=0){let s=bg('#ffcf9e','#f4a86c')+`<rect x="660" y="260" width="300" height="300" rx="16" fill="${night?'#18225a':'#bfe9ff'}" stroke="${INK}" stroke-width="12"/><path d="M810 260 V560 M660 410 H960" stroke="${INK}" stroke-width="10"/>`;
  s+=`<g stroke="#f7b98a" stroke-width="14" opacity=".6">${[...Array(10)].map((_,i)=>`<path d="M${i*120} 0 V1280"/>`).join('')}</g>`+floor(1280,'#a8693a');
  s+=`<g stroke="#8a5530" stroke-width="5">${[...Array(6)].map((_,i)=>`<path d="M0 ${1360+i*100} H1080"/>`).join('')}</g>`;
  if(night)s+=`<rect width="${W}" height="${H}" fill="#0a0c2a" opacity="${night}"/>`;return s}
function thought(x,y,w,h,inner,k){if(k<=0)return '';return g(`translate(${x} ${y}) scale(${k})`,`<circle cx="${-w*.25}" cy="${h/2+40}" r="22" fill="#fff" stroke="${INK}" stroke-width="7"/><circle cx="${-w*.32}" cy="${h/2+85}" r="13" fill="#fff" stroke="${INK}" stroke-width="6"/><rect x="${-w/2}" y="${-h/2}" width="${w}" height="${h}" rx="${h/2}" fill="#fff" stroke="${INK}" stroke-width="10"/>${inner}`)}
function bedWithYou(t,o={}){return `<rect x="80" y="1000" width="920" height="320" rx="30" fill="#5b3fa8" stroke="${INK}" stroke-width="12"/><rect x="60" y="760" width="80" height="560" rx="20" fill="#a8693a" stroke="${INK}" stroke-width="10"/>`+g(`translate(380 860) scale(.5)`,youHead(Object.assign({noShoulders:true,sweat:false},o)))+`<path d="M110 1000 C300 940 700 940 980 1000 L980 1180 L110 1180 Z" fill="${LIME}" stroke="${INK}" stroke-width="12"/>`}

window.SCENES=()=>[
 [0,t=>{ // hook
   const z=lerp(1,1.12,p(t,0,S(1)));
   let s=bg('#9b4dff','#4f10b8')+burst('#fff',.15,540,900);
   s+=g('translate(540 960) scale(.9)',youHead({eyes:'huge',look:[0,0],mouth:'o',sweat:true}));
   const k=[0,1,2].map(i=>pop(t,.3+i*.35,.3));
   s+=thought(230,430,300,200,dog(0,90,.45,{big:true},t),k[0])+thought(850,430,300,200,cat(0,90,.45,{},t),k[1])+thought(540,260,300,180,fish(0,0,.8,false,t),k[2]);
   return cam(z,540,900,s);
 }],
 [S(1),t=>{ // dog staring in morning
   let s=room()+bedWithYou(t,{eyes:t>S(1)+.6?'huge':'closed',look:[30,30],mouth:'flat'});
   s+=dog(760,1250,1.0,{big:true,wag:t>=S(2)?40:10,wagSpeed:t>=S(2)?24:6},t);
   if(t>=S(2)){s+=thought(560,450,700,260,heart(-200,0,1.4)+txt(40,30,'BEST DAY',90,'#ff4d7a',{sw:12}),pop(t,S(2),.3));s+=sparkles(760,1000,300,200,t,5)}
   return s;
 }],
 [S(3),t=>{ // waiting by door
   const opened=t>=S(5)+.6;
   let s=room()+door(400,500,380,780,'#a8693a',opened?eOut(p(t,S(5)+.6,S(5)+.9)):0)+sign(400,450,'BATHROOM','#7fd6ff',40,0);
   if(t<S(3)+.6)s+=g(`translate(${lerp(420,400,p(t,S(3),S(3)+.6))} 0)`,you(0,800,.42,{}).replace('translate(0 800)','translate(0 800)'));
   if(!opened){s+=dog(780,1250,1.0,{mood:'sad',wag:0},t);
     if(t>=S(4)){s+=g('translate(780 700)',`<ellipse cx="0" cy="0" rx="170" ry="80" fill="#8a8f9e" stroke="${INK}" stroke-width="8"/><ellipse cx="-90" cy="10" rx="90" ry="60" fill="#8a8f9e" stroke="${INK}" stroke-width="8"/>`+[...Array(6)].map((_,i)=>{const yy=((t*500+i*90)%260);return `<path d="M${-120+i*48} ${70+yy} l-8 30" stroke="#7fd6ff" stroke-width="8" stroke-linecap="round"/>`}).join(''))}
     if(t>=S(5))s+=g(`translate(540 430) scale(${pop(t,S(5),.3)})`,`<rect x="-230" y="-70" width="460" height="130" rx="30" fill="#16111f"/>`+txt(0,30,'+0:30',100,'#ffd23a',{sw:0}));}
   else{const j=Math.abs(Math.sin(t*9))*120;s+=you(400,820,.42,{eyes:'huge',mouth:'smile',sweat:false});s+=dog(760,1250-j,1.0,{big:true,wag:45,wagSpeed:30},t)+sparkles(700,900,330,250,t,6,'#ffd23a');for(let i=0;i<4;i++)s+=heart(560+i*120,700-((t*300+i*80)%300),.8)}
   return s;
 }],
 [S(7),t=>{ // the cat
   let s=room()+`<rect x="560" y="820" width="460" height="40" fill="#a8693a" stroke="${INK}" stroke-width="10"/>`+`<path d="M540 0 L760 840 L1040 840 L860 0 Z" fill="#fff6c8" opacity=".25"/>`;
   const z=t<S(9)?lerp(1,1.25,eIO(p(t,S(7),S(8)+.5))):1;
   if(t<S(9)){s+=cat(790,630,.95,{eyes:'meh'},t);s+=you(430,760,.42,{eyes:'open',mouth:'smile',sweat:false,look:[30,-10]});return cam(z,680,720,s)}
   // years of watching: tally wall
   s=room()+cat(760,1060,1.0,{eyes:'meh',glasses:true},t);
   s+=`<rect x="80" y="320" width="440" height="560" fill="#fff8e6" stroke="${INK}" stroke-width="10" transform="rotate(-3 300 600)"/>`;
   const n=Math.floor(lerp(0,36,p(t,S(9)+.2,S(10)+.5)));let tl='';for(let i=0;i<n;i++){const gx=i%5,gy=Math.floor(i/5)%8,col=Math.floor(i/40);tl+=gx===4?`<path d="M${120+Math.floor(i/5%2)*0+0} 0" />`:''}
   for(let i=0;i<n;i++){const grp=Math.floor(i/5),k=i%5,gx=grp%2,gy=Math.floor(grp/2);const x0=130+gx*190,y0=380+gy*110;tl+=k<4?`<path d="M${x0+k*30} ${y0} V${y0+80}" stroke="${INK}" stroke-width="8" stroke-linecap="round"/>`:`<path d="M${x0-12} ${y0+70} L${x0+110} ${y0+10}" stroke="#d1252f" stroke-width="8" stroke-linecap="round"/>`}
   s+=g('rotate(-3 300 600)',tl);
   if(t>=S(10))s+=g(`translate(300 280) scale(${pop(t,S(10),.3)})`,txt(0,0,'DAY 900',100,'#ff2e4d',{sw:14}));
   return s;
 }],
 [S(11),t=>{ // wrong bowl x3
   let s=room()+cat(640,1080,1.0,{eyes:'meh'},t)+you(250,850,.4,{eyes:'open',mouth:'smile',sweat:t>=S(12)+.8});
   s+=g('translate(560 1270)',`<path d="M-110 -40 L110 -40 L80 30 L-80 30 Z" fill="#7fd6ff" stroke="${INK}" stroke-width="9"/><ellipse cx="0" cy="-40" rx="110" ry="22" fill="#c27a4a" stroke="${INK}" stroke-width="7"/>`);
   const w=['WRONG BOWL','WRONG FLAVOR','WRONG HUMAN'];
   w.forEach((l,i)=>{const kk=p(t,S(12)+.15+i*.7,S(12)+.3+i*.7);if(kk>0)s+=stamp(540,420+i*150,l,'#ff2e4d',eOut(kk),-8+i*4,76)});
   return cam(1,540,960,s,...shake(t,S(12)+1.55,.3,20));
 }],
 [S(13),t=>{ // glass push
   const push=p(t,S(13)+.4,S(13)+1.2),fall=p(t,S(13)+1.2,S(13)+1.55);
   let s=room()+`<rect x="80" y="860" width="900" height="40" fill="#a8693a" stroke="${INK}" stroke-width="10"/><rect x="120" y="900" width="40" height="380" fill="#a8693a" stroke="${INK}" stroke-width="8"/><rect x="900" y="900" width="40" height="380" fill="#a8693a" stroke="${INK}" stroke-width="8"/>`;
   s+=cat(420,660,.9,{eyes:'meh',paw:[lerp(150,215,push),-60]},t);
   const gx=lerp(700,760,push)+fall*60,gy=fall>0?lerp(780,1220,eIn(fall)):780,rot=fall*120;
   if(fall<1)s+=g(`translate(${gx} ${gy}) rotate(${rot})`,`<path d="M-45 -80 L45 -80 L35 80 L-35 80 Z" fill="#bfe9ff" fill-opacity=".7" stroke="${INK}" stroke-width="8"/><rect x="-38" y="0" width="76" height="72" fill="#7fd6ff" opacity=".7"/>`);
   else{for(let i=0;i<7;i++){const a=i*0.9,d=40+((t-S(13)-1.55)*500)%120;s+=`<path d="M${820+Math.cos(a)*d} ${1260-Math.abs(Math.sin(a))*d*.6} l14 -20 l10 16 z" fill="#bfe9ff" stroke="${INK}" stroke-width="4"/>`}}
   if(t>=S(14))s+=stamp(540,420,'WARNING','#ff2e4d',eOut(p(t,S(14),S(14)+.15)),-10,120);
   return s;
 }],
 [S(15),t=>{ // the notebook
   let s=`<rect width="${W}" height="${H}" fill="#0b0a1c"/><path d="M540 0 L180 1500 L900 1500 Z" fill="#fff4c2" opacity=".1"/>`;
   const open=t>=S(17);
   if(!open){const kc=pop(t,S(15)+.1,.4);
     s+=g(`translate(540 860) scale(${kc}) rotate(-4)`,`<rect x="-300" y="-400" width="600" height="800" rx="20" fill="#d1252f" stroke="${INK}" stroke-width="14"/><rect x="-260" y="-360" width="520" height="720" rx="10" fill="none" stroke="#ffd23a" stroke-width="6"/>${cat(0,250,.6,{eyes:'meh'},t)}`+(t>=S(16)+.7?txt(0,-120,'PLAN B',150,'#ffd23a',{sw:16}):txt(0,-140,'TOP SECRET',70,'#ffd23a',{sw:10})));}
   else{
     s+=`<g transform="translate(540 860) rotate(-2)"><rect x="-470" y="-420" width="940" height="840" rx="20" fill="#fff8e6" stroke="${INK}" stroke-width="14"/><path d="M0 -420 V420" stroke="${INK}" stroke-width="8"/>${[...Array(10)].map((_,i)=>`<path d="M-440 ${-330+i*75} H440" stroke="#bcd" stroke-width="4"/>`).join('')}</g>`;
     s+=txt(310,560,'1. BE CUTE',60,INK,{font:'Fred',sw:0,rot:-2})+cat(310,850,.55,{eyes:'wide'},t);
     if(t>=S(17)+1.4)s+=txt(780,560,'2. INHERIT',60,INK,{font:'Fred',sw:0,rot:-2})+txt(780,630,'THE HOUSE',60,'#d1252f',{font:'Fred',sw:0,rot:-2})+g('translate(780 860) scale(1.1)',`<path d="M-120 0 L0 -110 L120 0 V140 H-120 Z" fill="#ffd23a" stroke="${INK}" stroke-width="10" stroke-linejoin="round"/><rect x="-30" y="50" width="60" height="90" fill="#a8693a" stroke="${INK}" stroke-width="7"/>`)+txt(900,780,'$$$',60,'#20a84a',{sw:8});
     if(t>=S(18)){const k=pop(t,S(18)+.1,.35);s+=`<rect width="${W}" height="${H}" fill="#000" opacity=".55"/>`+g(`translate(540 900) scale(${k}) rotate(5)`,`<rect x="-400" y="-230" width="800" height="460" rx="20" fill="#fff" stroke="${INK}" stroke-width="12"/>`+txt(80,-110,'WHISKERS &',58,INK,{font:'Fred',sw:0})+txt(80,-40,'ASSOCIATES',58,INK,{font:'Fred',sw:0})+txt(80,40,'ATTORNEYS AT LAW',36,'#666',{font:'Fred',sw:0})+(t>=S(19)+.7?cat(-230,110,.62,{eyes:'meh',suit:true,glasses:true},t):`<rect x="-360" y="-180" width="250" height="300" fill="#ddd" stroke="${INK}" stroke-width="8"/>`+txt(-235,-10,'?',120,'#999',{sw:0})))}
   }
   return s;
 }],
 [S(20),t=>{ // goldfish
   let s=bg('#9b4dff','#4f10b8');
   const sw=(t-S(20))*1.2;const fx=Math.sin(sw)*170,fy=Math.cos(sw*1.7)*60;const flip=Math.cos(sw)>0;
   const reset=t>=S(22);
   const inner=castle(120,150,1.0)+fish(fx,fy-20,1.0,!flip,t,{big:t>=S(21)+.5&&!reset,o:t>=S(21)&&t<E(21)})+[0,1,2].map(i=>`<circle cx="${fx-90+i*10}" cy="${-60-((t*120+i*60)%200)}" r="${8+i*3}" fill="none" stroke="#fff" stroke-width="5"/>`).join('');
   s+=bowl(540,800,1.1,inner);
   if(t>=S(21)+.6&&t<S(22))s+=sparkles(690,1040,150,110,t,4,'#ffd23a');
   if(t>=S(23))s+=g(`translate(540 1290) scale(.32)`,youHead({eyes:'open',mouth:'flat',look:[0,-20],sweat:false,noShoulders:true}));
   if(t>=S(22))s+=txt(540,330,'???',130,'#7fd6ff',{sw:16});
   return s;
 }],
 [S(24),t=>{ // dog walks in with homework; best roommate; cat heard
   let s=room();
   const walk=eOut(p(t,S(24),S(24)+1.0));
   s+=you(330,800,.42,{eyes:t>=S(26)?'closed':'open',mouth:'smile',sweat:false,wave:t>=S(26)?60:null});
   s+=dog(lerp(1300,720,walk),1250,1.0,{big:true,paper:t<S(25)+1.6,wag:40,wagSpeed:22},t);
   if(t>=S(25)){for(let i=0;i<4;i++)s+=heart(520+i*150,760-((t*260+i*90)%260),.75)}
   if(t>=S(25)+1.6&&t<S(26))s+=g('translate(860 1330) rotate(15)',`<rect x="-70" y="-20" width="80" height="40" fill="#fff" stroke="${INK}" stroke-width="5"/><rect x="10" y="-30" width="60" height="50" fill="#fff" stroke="${INK}" stroke-width="5" transform="rotate(20)"/>`);
   if(t>=S(28)-.1){const k=p(t,S(28)-.1,S(28)+.2);s+=`<rect width="${W}" height="${H}" fill="#05030c" opacity="${.75*k}"/>`+g(`translate(${lerp(1200,900,eOut(k))} 520)`,cat(0,0,1.0,{eyes:'glow',col:'#2a2a38'},t))}
   return s;
 }],
];

window.COVER=()=>coverTemplate({l1:'WHAT IF YOU COULD',l2:"HEAR YOUR PETS?",ep:3,
  hero:{eyes:'huge',mouth:'o'},
  badges:[
   {inner:dog(0,85,.55,{big:true},0),label:'BEST DAY',col:'#ffb84d'},
   {inner:cat(0,95,.55,{eyes:'meh'},0),label:'PLAN B',col:'#ff9ad5'},
   {inner:fish(0,0,.8,false,0,{big:true})+castle(70,90,.5),label:'A CASTLE!',col:'#7fd6ff'},
   {inner:cat(0,75,.48,{eyes:'meh',suit:true,glasses:true},0),label:'LAWYER',col:'#c9a6ff'},
  ]});

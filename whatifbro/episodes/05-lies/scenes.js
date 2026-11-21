// Episode 5 — What if every lie you told appeared above your head?
function person(x,y,s,o={},hair='bun',hairCol='#5a3a22'){
  const back=hair==='long'?`<path d="M-90 -150 Q-100 20 -80 40 L80 40 Q100 20 90 -150 Q60 -230 0 -232 Q-60 -230 -90 -150 Z" fill="${hairCol}" stroke="${INK}" stroke-width="8"/>`:'';
  const front=hair==='bun'?`<circle cx="0" cy="-215" r="40" fill="${hairCol}" stroke="${INK}" stroke-width="8"/><path d="M-72 -150 Q-60 -205 0 -205 Q60 -205 72 -150 Q40 -180 0 -180 Q-40 -180 -72 -150 Z" fill="${hairCol}" stroke="${INK}" stroke-width="7"/>`
    :hair==='long'?`<path d="M-74 -140 Q-50 -205 0 -205 Q50 -205 74 -140 Q30 -170 -10 -165 Q-50 -165 -74 -140 Z" fill="${hairCol}" stroke="${INK}" stroke-width="7"/>`:'';
  return g(`translate(${x} ${y}) scale(${s})`,back+worker(Object.assign({hair:'',front},o)));
}
function lieSign(x,y,lines,k,o={}){
  if(k<=0)return '';const ok=o.ok;const col=ok?'#20c35a':'#ff2e4d';
  const w=o.w||620,h=lines.length*86+90;
  return g(`translate(${x} ${y}) scale(${Math.min(k,1.15)}) rotate(${o.rot??-3})`,`<rect x="-14" y="0" width="28" height="${o.stick??170}" fill="#a8693a" stroke="${INK}" stroke-width="8"/>
   <rect x="${-w/2}" y="${-h}" width="${w}" height="${h}" rx="24" fill="#fff8e6" stroke="${INK}" stroke-width="12"/><rect x="${-w/2+12}" y="${-h+12}" width="${w-24}" height="${h-24}" rx="16" fill="none" stroke="${col}" stroke-width="10"/>
   <g transform="translate(${-w/2+20} ${-h-26})"><rect x="0" y="0" width="${ok?170:120}" height="56" rx="14" fill="${col}" stroke="${INK}" stroke-width="7"/>${txt(ok?85:60,42,ok?'TRUE':'LIE',42,'#fff',{sw:0})}</g>
   ${lines.map((l,i)=>txt(0,-h+92+i*86,l,Math.min(72,(w-60)/(l.length*.56)),ok?'#20a84a':INK,{sw:0})).join('')}`);
}
function homeBg(){return bg('#ffe2b8','#f8c98a')+`<g stroke="#f2b87a" stroke-width="12" opacity=".5">${[...Array(10)].map((_,i)=>`<path d="M${i*120} 0 V1280"/>`).join('')}</g>`+floor(1280,'#a8693a')}
function classBg(){return bg('#cfe8d4','#a8d4b4')+`<rect x="90" y="230" width="900" height="420" rx="14" fill="#2d5a3d" stroke="#8a5530" stroke-width="22"/>${txt(540,400,'2 + 2 = ?',90,'#f4f4f4',{sw:0})}${txt(540,530,'HOMEWORK DUE',60,'#ffd23a',{sw:0})}`+floor(1280,'#c9a26b')}
function hallBg(){let s=bg('#f4ecd8','#e6dcc2');for(let i=0;i<9;i++){const x=20+i*120;s+=`<rect x="${x}" y="420" width="110" height="860" fill="#3f8cff" stroke="${INK}" stroke-width="7"/><path d="M${x+25} 470 h60 M${x+25} 490 h60 M${x+25} 510 h60" stroke="${INK}" stroke-width="5"/>`}return s+floor(1280,'#c9b99a')}
function deskRow(y){return `<rect x="60" y="${y}" width="960" height="40" rx="10" fill="#c9a26b" stroke="${INK}" stroke-width="9"/>`}
function sweater(x,y,s){return g(`translate(${x} ${y}) scale(${s})`,`<path d="M-150 -120 Q0 -170 150 -120 L170 160 L-170 160 Z" fill="#ff5d6c" stroke="${INK}" stroke-width="10" stroke-linejoin="round"/><path d="M-150 -110 L-270 60 L-220 90 L-140 -20" fill="#ff5d6c" stroke="${INK}" stroke-width="10" stroke-linejoin="round"/><path d="M150 -110 L270 60 L220 90 L140 -20" fill="#ff5d6c" stroke="${INK}" stroke-width="10" stroke-linejoin="round"/><path d="M-30 60 L-40 260 L30 260 L30 60" fill="#ff5d6c" stroke="${INK}" stroke-width="10" stroke-linejoin="round"/>${[...Array(5)].map((_,i)=>`<path d="M${-140+i*70} -40 l20 -20 l20 20" stroke="#fff" stroke-width="8" fill="none"/>`).join('')}${heart(0,40,.9,'#fff')}`)}

window.SCENES=()=>[
 [0,t=>{ // hook
   const z=lerp(1,1.1,p(t,0,S(1)));
   let s=bg('#9b4dff','#4f10b8')+burst('#fff',.15,540,1100);
   s+=g('translate(540 1150) scale(.8)',youHead({eyes:'huge',look:[0,-30],mouth:'grit',sweat:true}));
   s+=lieSign(540,840,['I DID MY','HOMEWORK'],pop(t,.6,.35),{stick:0});
   return cam(z,540,960,s);
 }],
 [S(1),t=>{ // mom morning
   let s=homeBg()+door(820,520,300,760,'#a8693a',.7);
   s+=`<rect x="60" y="1000" width="560" height="300" rx="30" fill="#5b3fa8" stroke="${INK}" stroke-width="12"/>`+g('translate(300 920) scale(.45)',youHead({eyes:'closed',mouth:'flat',sweat:false,noShoulders:true}))+`<path d="M80 1000 C200 950 500 950 620 1000 L620 1200 L80 1200 Z" fill="${LIME}" stroke="${INK}" stroke-width="12"/>`;
   if(t<S(2))s+=zz(420,820,t);
   const angry=t>=S(6);
   s+=person(820,1020,1.15,{shirt:'#ff9ad5',eyes:angry?'frantic':'normal',mouth:angry?'scream':t<S(2)?'o':'flat',lh:[-110,-40],rh:[90,60],tie:'#fff'},'bun','#5a3a22');
   if(t<S(2)&&t>=S(1)+.8)s+=bubble(760,450,540,150,['ARE YOU AWAKE?!'],eBack(p(t,S(1)+.8,S(1)+1.1)),56);
   if(t>=S(2)&&t<S(3))s+=bubble(330,620,460,150,["YEAH I'M UP!"],eBack(p(t,S(2),S(2)+.3)),56);
   s+=lieSign(300,700,['IN BED.','EYES CLOSED.'],pop(t,S(3),.35),{stick:120,w:520});
   if(angry)s+=`<g opacity=".8">${[0,1,2].map(i=>`<path d="M${760+i*40} 600 q10 -40 0 -80" stroke="#888" stroke-width="12" fill="none" stroke-linecap="round" transform="translate(0 ${-((t*200+i*40)%60)})"/>`).join('')}</g>`;
   return cam(1,540,960,s,...shake(t,S(6),.4,22));
 }],
 [S(7),t=>{ // classroom dog
   let s=classBg();
   s+=person(820,1020,1.1,{shirt:'#8a6cf0',eyes:t>=S(9)?'creepy':'normal',mouth:'flat',glasses:true,lh:[-120,-60],rh:[90,60]},'bun','#888');
   s+=you(330,800,.44,{eyes:t>=S(9)?'huge':'open',mouth:t>=S(9)?'grit':'smile',sweat:t>=S(9)});
   s+=deskRow(1190)+crowd(t,1300,5,.68,4,{eyes:t>=S(10)?'frantic':'normal',mouth:t>=S(10)?'o':'flat',amp:0});
   if(t>=S(8)&&t<S(9))s+=bubble(380,560,460,150,['MY DOG ATE IT'],eBack(p(t,S(8),S(8)+.3)),52);
   s+=lieSign(330,640,["I DON'T","HAVE A DOG."],pop(t,S(9),.35),{stick:120,w:520});
   if(t>=S(10))s+=txt(820,620,'...',120,'#fff',{sw:14});
   return s;
 }],
 [S(11),t=>{ // crush in hallway
   let s=hallBg();
   const walk=eOut(p(t,S(11),S(11)+1.2));
   s+=person(lerp(1200,800,walk),1050,1.1,{shirt:'#ff9ad5',eyes:'happy',mouth:'smile',lh:[-90,60],rh:[100,t>=S(11)+1?-150:60]},'long','#3a2a1a');
   s+=you(330,800,.44,{eyes:t>=S(13)?'huge':'open',mouth:t>=S(13)?'grit':'smile',sweat:t>=S(13),blush:t>=S(12)});
   s+=`<g transform="translate(160 440)"><circle r="90" fill="#fff" stroke="${INK}" stroke-width="10"/><path d="M0 0 V-60" stroke="${INK}" stroke-width="10" stroke-linecap="round"/><path d="M0 0 L40 20" stroke="${INK}" stroke-width="10" stroke-linecap="round" transform="rotate(${(t-S(11))*40})"/></g>`;
   if(t>=S(12)&&t<S(13))s+=bubble(400,560,560,150,["OH, DIDN'T SEE YOU"],eBack(p(t,S(12),S(12)+.3)),48);
   s+=lieSign(360,640,['WAITED HERE','40 MINUTES.'],pop(t,S(13),.35),{stick:120,w:560});
   if(t>=S(14)){for(let i=0;i<5;i++){const yy=(t*300+i*70)%220;s+=`<path d="M${250+i*45} ${760+yy} c8 14 12 22 12 28 a12 12 0 0 1 -24 0 c0 -6 4 -14 12 -28z" fill="#7fd6ff" stroke="${INK}" stroke-width="4"/>`}}
   return s;
 }],
 [S(15),t=>{ // drawing
   let s=bg('#ffe9a8','#ffd26a')+floor(1280,'#c9a26b')+`<rect x="40" y="1100" width="1000" height="60" rx="14" fill="#a8693a" stroke="${INK}" stroke-width="10"/>`;
   s+=you(300,770,.44,{eyes:t>=S(17)?'huge':'open',mouth:t>=S(16)?'smile':'flat',sweat:t>=S(17)});
   s+=g('translate(800 1040) scale(1.1)',worker({shirt:'#5ac94a',eyes:t>=S(18)+.3?'frantic':'happy',mouth:t>=S(18)+.3?'o':'smile',hair:'tuft',lh:[-150,-140],rh:[150,-140]}));
   // drawing (scribble of you)
   const show=t>=S(15)+.6;
   if(show)s+=g('translate(800 640) rotate(4)',`<rect x="-190" y="-150" width="380" height="300" fill="#fff" stroke="${INK}" stroke-width="10"/><path d="M-90 60 Q-120 -40 -40 -60 Q30 -90 60 -20 Q100 40 40 70 L80 120 M-60 60 L-90 120 M20 70 L10 120 M-40 -60 L-60 -110 L-20 -80" fill="none" stroke="#8a5530" stroke-width="9" stroke-linecap="round"/><circle cx="20" cy="-30" r="8" fill="${INK}"/>`+(t>=S(18)?txt(0,-110,'(ME?!)',40,'#ff2e4d',{font:'Fred',sw:0}):''));
   if(t>=S(16)&&t<S(17))s+=bubble(340,500,460,150,['WOW, AMAZING!'],eBack(p(t,S(16),S(16)+.3)),52);
   s+=lieSign(300,620,['IS THAT','A HORSE?'],pop(t,S(17),.35),{stick:110,w:480});
   if(t>=S(18)+.4){for(let i=0;i<2;i++)s+=`<path d="M${770+i*60} ${850} q-6 ${30+((t*200)%60)} 0 80" stroke="#7fd6ff" stroke-width="10" fill="none" stroke-linecap="round"/>`}
   return s;
 }],
 [S(19),t=>{ // texting
   let s=bg('#c9a6ff','#8a6cf0');
   s+=g('translate(540 880) scale(1.05)',`<rect x="-300" y="-560" width="600" height="1120" rx="80" fill="#1e1e2e" stroke="${INK}" stroke-width="16"/><rect x="-268" y="-520" width="536" height="1040" rx="56" fill="#f4f4ff"/>`+
     g(`translate(-120 -330) scale(${pop(t,S(19)+.5,.3)})`,`<rect x="-130" y="-55" width="300" height="100" rx="40" fill="#e5e5ea"/>`+txt(20,15,'where are u??',40,INK,{font:'Fred',sw:0}))+
     (t>=S(20)+.4?g(`translate(110 -170) scale(${pop(t,S(20)+.4,.3)})`,`<rect x="-150" y="-55" width="300" height="100" rx="40" fill="#0a7aff"/>`+txt(0,15,'5 mins away',40,'#fff',{font:'Fred',sw:0})):'')+
     (t>=S(21)?'':'')+`<rect x="-240" y="400" width="480" height="70" rx="35" fill="#fff" stroke="#ccc" stroke-width="4"/>`);
   if(t>=S(21)){s=`<rect width="${W}" height="${H}" fill="#bfe9ff"/>`+`<rect x="160" y="200" width="760" height="1100" fill="#e8f6ff" stroke="${INK}" stroke-width="12"/>`+`<path d="M400 260 Q540 200 680 260" stroke="#b8bcc8" stroke-width="22" fill="none"/>`+
     [...Array(12)].map((_,i)=>`<path d="M${330+i*38} ${300+((t*600+i*60)%300)} l-6 30" stroke="#7fd6ff" stroke-width="8" stroke-linecap="round"/>`).join('')+
     g('translate(540 900) scale(.75)',youHead({eyes:'open',mouth:'smile',sweat:false}))+phone(700,980,-10,t,true)+`<rect x="160" y="1150" width="760" height="150" fill="#fff" opacity=".5"/>`+
     lieSign(540,620,['STILL IN','THE SHOWER.'],pop(t,S(21),.35),{stick:0,w:560})}
   return s;
 }],
 [S(22),t=>{ // stop lying -> grandma
   let s=homeBg()+`<rect x="120" y="560" width="300" height="300" rx="16" fill="#fff6c8" stroke="${INK}" stroke-width="12"/>`;
   if(t<S(23)){s+=you(540,800,.46,{eyes:'open',mouth:'flat',brows:'angry',sweat:false,wave:150});s+=g(`translate(540 520) scale(${pop(t,S(22)+.4,.3)})`,txt(0,0,'NO MORE LIES',110,LIME,{sw:16}));return s}
   const showSw=t>=S(24);
   s+=person(890,1060,1.05,{shirt:'#c9a6ff',eyes:'happy',mouth:'smile',glasses:true,lh:[-150,-40],rh:[-60,-40],skin:'#f2d9c0'},'bun','#d8d8e0');
   s+=you(280,800,.44,{eyes:t>=S(25)?'huge':'open',mouth:t>=S(26)?'smile':t>=S(25)?'grit':'flat',sweat:t>=S(25)&&t<S(28),blush:t>=S(28)});
   if(showSw){const k=pop(t,S(24),.35);s+=sweater(590,760,.72*Math.min(k,1.1))}
   if(t>=S(25)&&t<S(26))s+=g(`translate(620 460) scale(${pop(t,S(25),.3)})`,txt(0,0,'3 ARMS?!',110,'#ff2e4d',{sw:16}));
   if(t>=S(26)&&t<S(27))s+=bubble(300,560,420,150,['I LOVE IT.'],eBack(p(t,S(26),S(26)+.3)),56);
   if(t>=S(27)&&t<S(28)){const q=.4+.6*Math.abs(Math.sin(t*3));s+=g(`translate(280 560) scale(${q})`,txt(0,0,'?',150,'#fff',{sw:16}))}
   if(t>=S(28)){s+=lieSign(280,640,['TRUE.'],pop(t,S(28),.4),{ok:true,stick:120,w:420});for(let i=0;i<5;i++)s+=heart(150+i*190,1300-((t*200+i*90)%400),.8);s+=sparkles(280,520,260,120,t,5)}
   if(t>=S(29))s+=g(`translate(540 1700) scale(${pop(t,S(29),.3)})`,'');
   return s;
 }],
];

window.COVER=()=>coverTemplate({l1:'WHAT IF YOUR LIES',l2:'SHOWED UP?',ep:5,
  hero:{eyes:'huge',mouth:'grit'},
  heroExtra:lieSign(540,880,["I'M 5 MIN","AWAY"],.85,{stick:0,w:460}),
  badges:[
   {inner:person(0,90,.8,{shirt:'#ff9ad5',eyes:'frantic',mouth:'scream'},'bun','#5a3a22'),label:'MOM',col:'#ff9ad5'},
   {inner:txt(0,10,'NO',90,'#ff2e4d',{sw:10})+txt(0,90,'DOG',70,INK,{sw:0}),label:'HOMEWORK',col:'#8a6cf0'},
   {inner:person(0,90,.8,{shirt:'#ff9ad5',eyes:'happy',mouth:'smile'},'long','#3a2a1a'),label:'CRUSH',col:'#ff4d7a'},
   {inner:sweater(0,0,.38),label:'3 ARMS',col:'#c9a6ff'},
  ]});

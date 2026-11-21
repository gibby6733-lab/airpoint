// Episode 2 — What if you got locked inside IKEA forever?
const BLUE='#2f63b5',YEL='#ffd23a';
function store(o={}){
  let s=bg('#3d74c9','#244f99');
  // ceiling lights
  for(let i=0;i<5;i++)s+=`<rect x="${60+i*210}" y="90" width="150" height="26" rx="10" fill="${o.dark?'#203050':'#fff9d6'}" stroke="${INK}" stroke-width="6"/>`;
  // big shelving racks in background
  for(let i=0;i<4;i++){const x=40+i*260;s+=`<rect x="${x}" y="260" width="220" height="900" fill="#1d3f7a" stroke="${INK}" stroke-width="8"/>`;
    for(let r=0;r<5;r++){s+=`<rect x="${x}" y="${300+r*180}" width="220" height="16" fill="#ff9b3d" stroke="${INK}" stroke-width="5"/>`;
      for(let b=0;b<3;b++)s+=`<rect x="${x+14+b*68}" y="${300+r*180-80}" width="58" height="80" fill="#c9a26b" stroke="${INK}" stroke-width="5"/>`}}
  s+=floor(1260,'#c9c1b2');
  s+=`<g stroke="#a89f8e" stroke-width="5">${[...Array(9)].map((_,i)=>`<path d="M${540+(i-4)*60} 1260 L${540+(i-4)*260} ${H}"/>`).join('')}</g>`;
  if(o.sign)s+=sign(540,250,o.sign,YEL,52,-1);
  if(o.dark)s+=`<rect width="${W}" height="${H}" fill="#060a1c" opacity="${o.dark}"/>`;
  return s;
}
function lamp(x,y,s=1,on=true){return g(`translate(${x} ${y}) scale(${s})`,`${on?`<path d="M-60 -230 L-200 120 L200 120 L60 -230 Z" fill="#fff4a8" opacity=".25"/>`:''}<rect x="-8" y="-200" width="16" height="400" fill="#555" stroke="${INK}" stroke-width="6"/><ellipse cx="0" cy="205" rx="70" ry="18" fill="#555" stroke="${INK}" stroke-width="8"/><path d="M-70 -200 L-40 -300 L40 -300 L70 -200 Z" fill="${on?'#fff0b0':'#d8c9a0'}" stroke="${INK}" stroke-width="9" stroke-linejoin="round"/>`)}
function bed(x,y,s=1,col='#7fd6ff'){return g(`translate(${x} ${y}) scale(${s})`,`<rect x="-200" y="-40" width="400" height="90" rx="14" fill="#a87a4e" stroke="${INK}" stroke-width="9"/><rect x="-200" y="-150" width="40" height="200" rx="10" fill="#a87a4e" stroke="${INK}" stroke-width="9"/><rect x="-180" y="-80" width="380" height="60" rx="20" fill="${col}" stroke="${INK}" stroke-width="8"/><rect x="-170" y="-110" width="90" height="45" rx="16" fill="#fff" stroke="${INK}" stroke-width="7"/>`)}
function tag(x,y,label,price){return g(`translate(${x} ${y}) rotate(-6)`,`<rect x="-80" y="-45" width="160" height="90" fill="${YEL}" stroke="${INK}" stroke-width="7"/>${txt(0,-8,label,28,INK,{font:'Fred',sw:0})}${txt(0,30,price,30,'#d1252f',{font:'Fred',sw:0})}`)}
function screw(x,y,s=1,rot=0){return g(`translate(${x} ${y}) rotate(${rot}) scale(${s})`,`<rect x="-14" y="-10" width="28" height="120" rx="6" fill="#c8ccd6" stroke="${INK}" stroke-width="7"/><path d="M-14 20 L14 30 M-14 45 L14 55 M-14 70 L14 80" stroke="${INK}" stroke-width="5"/><path d="M14 110 L0 140 L-14 110 Z" fill="#c8ccd6" stroke="${INK}" stroke-width="6"/><rect x="-36" y="-36" width="72" height="30" rx="10" fill="#dfe3ea" stroke="${INK}" stroke-width="7"/><path d="M-16 -21 H16" stroke="${INK}" stroke-width="6"/>`)}
function bookshelf(x,y,w,h,col='#f4eadc'){let s=`<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${col}" stroke="${INK}" stroke-width="8"/>`;for(let i=1;i<4;i++)s+=`<rect x="${x}" y="${y+i*h/4-6}" width="${w}" height="12" fill="#d9ccb8" stroke="${INK}" stroke-width="4"/>`;return s}
function cart(x,y,s=1){return g(`translate(${x} ${y}) scale(${s})`,`<path d="M-180 -160 L-150 40 L160 40 L190 -160 Z" fill="#ffd23a" fill-opacity=".35" stroke="${INK}" stroke-width="10" stroke-linejoin="round"/><path d="M-170 -100 H180 M-160 -40 H170 M-90 -160 L-80 40 M0 -160 L0 40 M90 -160 L80 40" stroke="${INK}" stroke-width="5" opacity=".6"/><path d="M-180 -160 L-240 -220 L-290 -220" fill="none" stroke="${INK}" stroke-width="12" stroke-linecap="round"/><circle cx="-120" cy="85" r="26" fill="#333" stroke="${INK}" stroke-width="8"/><circle cx="130" cy="85" r="26" fill="#333" stroke="${INK}" stroke-width="8"/><path d="M-150 40 L-120 60 M160 40 L130 60" stroke="${INK}" stroke-width="10"/>`)}
function crown(x,y,s=1,rot=0){return g(`translate(${x} ${y}) rotate(${rot}) scale(${s})`,`<path d="M-90 40 L-100 -50 L-50 0 L0 -70 L50 0 L100 -50 L90 40 Z" fill="#ffd23a" stroke="${INK}" stroke-width="9" stroke-linejoin="round"/><circle cx="0" cy="-10" r="12" fill="#ff4d7a" stroke="${INK}" stroke-width="5"/><circle cx="-55" cy="15" r="9" fill="#4f7cff" stroke="${INK}" stroke-width="4"/><circle cx="55" cy="15" r="9" fill="#5ac94a" stroke="${INK}" stroke-width="4"/>`)}
function meatballs(x,y,s=1){let b='';const pts=[[-60,-10],[0,-20],[60,-10],[-30,-50],[30,-50],[0,-80]];pts.forEach(([a,c])=>{b+=`<circle cx="${a}" cy="${c}" r="34" fill="#8a4a24" stroke="${INK}" stroke-width="7"/><circle cx="${a-10}" cy="${c-12}" r="8" fill="#c27a4a"/>`});
  return g(`translate(${x} ${y}) scale(${s})`,`<ellipse cx="0" cy="20" rx="160" ry="40" fill="#fff" stroke="${INK}" stroke-width="9"/><path d="M-110 10 Q-60 30 -20 5" stroke="#d1252f" stroke-width="16" fill="none" stroke-linecap="round"/>${b}`)}
// you() lives in shared engine
const beard=`<path d="M-60 -110 Q-70 -40 0 -30 Q70 -40 60 -110 Q30 -80 0 -82 Q-30 -80 -60 -110 Z" fill="#8a6a4a" stroke="${INK}" stroke-width="6"/>`;
function survivor(x,y,s,o={}){return g(`translate(${x} ${y}) scale(${s})`,worker(Object.assign({shirt:'#b7a58a',eyes:'frantic',mouth:'flat',hair:'spike',hairCol:'#8a6a4a',front:''},o))+g('',o.beard===false?'':beard))}

window.SCENES=()=>[
 [0,t=>{ // hook
   let s=store({sign:'SHOWROOM'});const z=lerp(1,1.15,p(t,0,S(1)));
   s+=lamp(800,1000,1.1,true)+tag(860,1180,'LAMP','$19.99');
   s+=you(400,800,.48,{look:[30,-5],eyes:'open',mouth:'smile',sweat:false});
   return cam(z,540,960,s);
 }],
 [S(1),t=>{ // closing time
   const dark=t>=S(3)?Math.min(.75,(t-S(3))*6):0;
   let s=store({sign:'SHOWROOM'});
   s+=lamp(800,1000,1.1,dark===0)+tag(860,1180,'LAMP','$19.99');
   s+=you(400,800,.48,{look:dark?[-30,0]:[30,-5],eyes:dark?'huge':'open',mouth:dark?'o':'smile',sweat:dark>0});
   const kc=pop(t,S(1)+.1,.3);
   if(t<S(3))s+=g(`translate(540 520) scale(${kc})`,`<rect x="-330" y="-80" width="660" height="150" rx="24" fill="#16111f" stroke="${INK}" stroke-width="10"/>${txt(0,25,'STORE CLOSED',84,'#ff2e4d',{sw:0})}`);
   s+=`<rect width="${W}" height="${H}" fill="#050818" opacity="${dark}"/>`;
   if(dark>0)s+=`<ellipse cx="400" cy="700" rx="60" ry="20" fill="#fff" opacity="0"/>`;
   return s;
 }],
 [S(4),t=>{ // shutter slam
   const k=eIn(p(t,S(4)+.05,S(4)+.3));const [sx,sy]=shake(t,S(4)+.3,.4,30);
   let s=bg('#10182c','#070a14')+floor(1300,'#2b2d36');
   s+=`<rect x="140" y="420" width="800" height="880" fill="#0b0f1c" stroke="${INK}" stroke-width="14"/>`+txt(540,380,'EXIT',90,'#5ac94a',{sw:12});
   s+=`<g><rect x="150" y="430" width="780" height="${lerp(0,860,k)}" fill="#7d8496" stroke="${INK}" stroke-width="10"/>${[...Array(Math.floor(lerp(0,860,k)/60))].map((_,i)=>`<path d="M150 ${470+i*60} H930" stroke="${INK}" stroke-width="6"/>`).join('')}</g>`;
   if(t>S(4)+.3)s+=g(`translate(540 870) scale(${pop(t,S(4)+.3,.3)})`,`<rect x="-90" y="-60" width="180" height="140" rx="16" fill="#ffd23a" stroke="${INK}" stroke-width="10"/><path d="M-55 -60 V-110 A55 55 0 0 1 55 -110 V-60" fill="none" stroke="${INK}" stroke-width="18"/><circle cy="0" r="16" fill="${INK}"/>`);
   return cam(1,540,960,s,sx,sy);
 }],
 [S(5),t=>titleCard(t,S(5),'DAY 1')],
 [S(6),t=>{ // vibe on bed + kitchen
   if(t<S(7)+1.6){
     let s=store({sign:'BEDROOMS'})+`<rect width="${W}" height="${H}" fill="#0a1030" opacity=".35"/>`;
     s+=bed(250,1180,1.0,'#ff8fd0')+bed(820,1180,1.0,'#b7f23a')+bed(540,1330,1.25,'#7fd6ff');
     s+=g(`translate(540 1230) rotate(-80) scale(.36)`,youBody({eyes:'closed',mouth:'smile',sweat:false}));
     s+=`<g transform="translate(560 1080) rotate(-80)"><rect x="-70" y="-25" width="60" height="38" rx="12" fill="${INK}"/><rect x="10" y="-25" width="60" height="38" rx="12" fill="${INK}"/><path d="M-10 -10 H10" stroke="${INK}" stroke-width="8"/></g>`;
     s+=sparkles(540,1150,320,120,t,5);
     const k50=pop(t,S(7)+.2,.3);if(k50>0)s+=g(`translate(540 560) scale(${k50}) rotate(-5)`,txt(0,0,'50 BEDS',170,'#ffd23a',{sw:22}));
     return s;}
   // kitchen
   let s=store({sign:'KITCHENS'});
   s+=`<rect x="420" y="900" width="560" height="360" fill="#f4eadc" stroke="${INK}" stroke-width="10"/><rect x="400" y="870" width="600" height="50" fill="#9a9aa8" stroke="${INK}" stroke-width="10"/><rect x="560" y="880" width="220" height="40" rx="10" fill="#555" stroke="${INK}" stroke-width="7"/>`;
   s+=`<path d="M670 880 V760 Q670 720 720 720 H760" fill="none" stroke="#b8bcc8" stroke-width="26" stroke-linecap="round"/><path d="M670 880 V760 Q670 720 720 720 H760" fill="none" stroke="${INK}" stroke-width="6" opacity=".5"/>`;
   s+=you(230,880,.42,{look:[30,10],eyes:'huge',mouth:'grit',sweat:true,wave:40});
   const kd=pop(t,S(7)+1.7,.3);if(kd>0)s+=g(`translate(780 800) scale(${kd})`,`<circle r="40" fill="#c8b89a" opacity=".8"/><circle cx="30" cy="-20" r="26" fill="#c8b89a" opacity=".7"/>`)+txt(760,620,'*NOTHING*',60,'#fff',{sw:10});
   return s;
 }],
 [S(8),t=>titleCard(t,S(8),'DAY 3')],
 [S(9),t=>{ // arrows maze top-down
   let s=bg('#c9c1b2','#b8b0a0');
   const R=330,cx=540,cy=900;
   s+=`<circle cx="${cx}" cy="${cy}" r="${R}" fill="none" stroke="#fff" stroke-width="70" opacity=".6"/>`;
   for(let i=0;i<10;i++){const a=i/10*Math.PI*2+t*.4;const x=cx+Math.cos(a)*R,y=cy+Math.sin(a)*R;s+=g(`translate(${x} ${y}) rotate(${a*180/Math.PI+90})`,`<path d="M-30 20 L0 -25 L30 20 L12 20 L12 45 L-12 45 L-12 20 Z" fill="#ffd23a" stroke="${INK}" stroke-width="6"/>`)}
   s+=sign(540,420,'EXIT  ->',YEL,48,0);
   s+=g(`translate(${cx} ${cy})`,`<rect x="-150" y="-60" width="300" height="120" rx="20" fill="${BLUE}" stroke="${INK}" stroke-width="10"/>${txt(0,22,'SHOWROOM',58,'#fff',{sw:0})}`);
   const a=(t-S(9))*1.7-Math.PI/2;const sp=t>=S(10)+1.5;
   s+=g(`translate(${cx+Math.cos(a)*R} ${cy+Math.sin(a)*R-120}) rotate(${sp?(t*400)%360:0} 0 120) scale(.26)`,youBody({eyes:sp?'huge':'open',mouth:sp?'o':'flat',look:[0,10]}));
   if(sp)s+=txt(540,1380,'@#%&!',90,'#ff2e4d',{sw:14});
   return s;
 }],
 [S(11),t=>titleCard(t,S(11),'DAY 7')],
 [S(12),t=>{ // bookshelf house, the screw
   if(t<S(13)+1.1){
     let s=store({sign:'STORAGE'});
     s+=bookshelf(220,800,200,460)+bookshelf(660,800,200,460)+`<path d="M180 820 L540 520 L900 820 Z" fill="#f4eadc" stroke="${INK}" stroke-width="10" stroke-linejoin="round"/>${bookshelf(420,980,240,280,'#e8dcc8')}<rect x="480" y="1050" width="120" height="210" fill="#a87a4e" stroke="${INK}" stroke-width="8"/>`;
     s+=you(540,770,.3,{eyes:'open',mouth:'smile',wave:110+Math.sin(t*10)*20,sweat:false});
     const kt=pop(t,S(13)+.1,.3);if(kt>0)s+=g(`translate(820 450) scale(${kt}) rotate(6)`,`<circle r="110" fill="#fff" stroke="${INK}" stroke-width="10"/><path d="M0 0 V-70 M0 0 L50 30" stroke="${INK}" stroke-width="12" stroke-linecap="round"/>`+txt(0,170,'4 HOURS',60,'#ffd23a',{sw:10}));
     return s;}
   const z=lerp(1,1.35,eIO(p(t,S(13)+1.1,S(15)+.8)));
   let s=`<rect width="${W}" height="${H}" fill="#0c0618"/><path d="M540 0 L250 1300 L830 1300 Z" fill="#fff4c2" opacity=".18"/><ellipse cx="540" cy="1300" rx="300" ry="50" fill="#fff4c2" opacity=".25"/>`;
   s+=screw(540,1050,1.6,-20+Math.sin(t*2)*3)+sparkles(540,1100,230,90,t,4);
   s+=g(`translate(540 640) scale(.6)`,youHead({eyes:'huge',look:[0,40],mouth:'grit',sweat:true,noShoulders:true}));
   if(t>=S(15))s+=g(`translate(540 380) scale(${pop(t,S(15),.3)})`,txt(0,0,'???',150,'#ff2e4d',{sw:18}));
   return cam(z,540,960,s);
 }],
 [S(16),t=>titleCard(t,S(16),'DAY 12')],
 [S(17),t=>{ // meatball zone
   let s=bg('#ffe9a8','#ffb84d')+burst('#fff',.35,540,800,22);
   s+=`<circle cx="600" cy="720" r="${300+Math.sin(t*3)*12}" fill="#fff8d0" opacity=".6"/>`;
   s+=meatballs(600,760,1.5);
   s+=sign(540,300,'MEATBALL ZONE','#d1252f',60,-2).replace(`fill="${INK}" font-family`,`fill="#fff" font-family`);
   s+=you(300,1010,.36,{eyes:t>=S(18)?'closed':'huge',mouth:'smile',sweat:false,wave:t>=S(18)?150:60});
   s+=sparkles(540,800,420,320,t,7);
   return s;
 }],
 [S(19),t=>titleCard(t,S(19),'DAY 20')],
 [S(20),t=>{ // survivors
   let s=store({sign:'WAREHOUSE',dark:.35});
   const k=[0,1,2].map(i=>pop(t,S(20)+.15+i*.18,.3));
   [[260,1040],[540,1000],[820,1040]].forEach(([x,y],i)=>{if(k[i]>0)s+=survivor(x,y,1.25*k[i],{shirt:['#b7a58a','#8aa0b7','#b78a8a'][i],eyes:i===1?'creepy':'frantic',mouth:t>=S(23)&&t<E(23)?'o':'flat',lh:[-90,60],rh:[100,t>=S(23)?-120:60]})});
   const ks=p(t,S(21)+.6,S(21)+.8);if(t<S(23)-.05)s+=stamp(540,560,'SINCE 2009','#ff2e4d',ks?eOut(ks):0,-10,96);
   const kb=p(t,S(23)-.05,S(23)+.25);if(kb>0&&t<S(24))s+=bubble(540,500,760,180,['BILLY. MALM. KALLAX.'],eBack(kb),60);
   return s;
 }],
 [S(24),t=>titleCard(t,S(24),'DAY 40')],
 [S(25),t=>{ // king
   let s=store({sign:'WAREHOUSE'})+burst('#ffd23a',.18,540,800);
   s+=`<rect x="330" y="880" width="420" height="380" fill="#c9a26b" stroke="${INK}" stroke-width="10"/><rect x="380" y="560" width="320" height="340" fill="#c9a26b" stroke="${INK}" stroke-width="10"/><path d="M380 700 H700 M540 560 V900" stroke="${INK}" stroke-width="6" opacity=".4"/>`;
   s+=you(540,650,.38,{eyes:'open',mouth:'smile',sweat:false,wave:130+Math.sin(t*6)*10});
   s+=crown(540,520,1.1,Math.sin(t*3)*4);
   s+=crowd(t,1500,5,.85,9,{cheer:true,eyes:'happy',mouth:'grin'});
   return s;
 }],
 [S(26),t=>titleCard(t,S(26),'DAY 60')],
 [S(27),t=>{ // doors open, choice: kingdom left, exit right, you in the middle
   const open=eIO(p(t,S(27)+.1,S(27)+.9));
   const fx=t<S(29)?540:t<S(30)?lerp(540,330,eIO(p(t,S(29),S(29)+.4))):lerp(330,750,eIO(p(t,S(30),S(30)+.4)));
   const z=t<S(29)?1:1.12;
   let s=`<rect x="-500" y="-200" width="2100" height="1500" fill="#244f99"/><rect x="-500" y="1300" width="2100" height="900" fill="#c9c1b2"/><path d="M-500 1300 H1600" stroke="${INK}" stroke-width="12"/>`;
   // kingdom (left)
   s+=bookshelf(-20,760,170,540)+`<rect x="150" y="1000" width="230" height="300" fill="#c9a26b" stroke="${INK}" stroke-width="10"/><rect x="180" y="820" width="170" height="200" fill="#c9a26b" stroke="${INK}" stroke-width="10"/>`+crown(265,780,.8,-6)+sign(200,560,'MY KINGDOM','#ffd23a',36,-4);
   // exit (right)
   s+=`<rect x="720" y="420" width="360" height="880" fill="#fff6c8"/>`+burst('#fff6c8',.3*open,900,860,14);
   s+=`<rect x="${720-open*170}" y="420" width="180" height="880" fill="#8fb3d9" stroke="${INK}" stroke-width="10"/><rect x="${900+open*170}" y="420" width="180" height="880" fill="#8fb3d9" stroke="${INK}" stroke-width="10"/>`;
   s+=`<rect x="700" y="400" width="400" height="30" fill="${INK}"/>`+txt(900,380,'EXIT',80,'#5ac94a',{sw:12});
   if(open>.5)s+=g(`translate(900 1080) scale(.95)`,worker({shirt:YEL,eyes:'normal',mouth:t>=S(28)&&t<E(28)?'o':'smile',hair:'tuft',lh:[-110,-40],rh:[90,60],badge:'STAFF'}));
   const kb=p(t,S(28)+.4,S(28)+.65);if(kb>0&&t<S(29))s+=bubble(760,640,520,150,["YOU'RE FREE!"],eBack(kb),62);
   const look=t>=S(30)?1:t>=S(29)?-1:0;
   const holdCart=t>=S(31)+.3;
   s+=you(520,820,.42,{eyes:t>=S(30)?'huge':'open',mouth:holdCart?'grit':'flat',look:[look*40,0],sweat:t>=S(30)});
   if(holdCart)s+=cart(lerp(260,430,eOut(p(t,S(31)+.3,S(31)+.7))),1200,.75);
   let out=cam(z,fx,900,s);
   if(t>=S(32)){const k=pop(t,S(32)+.2,.4);out+=`<rect width="${W}" height="${H}" fill="#0c0618" opacity="${.72*clamp(k)}"/>`+g(`translate(540 900) scale(${k})`,lamp(0,0,1.3,true)+txt(0,-470,'THE LAMP.',120,YEL,{sw:16}))}
   return out;
 }],
];

window.COVER=()=>coverTemplate({l1:'TRAPPED IN',l2:'IKEA FOREVER?',ep:2,
  hero:{eyes:'huge',mouth:'o',look:[0,0]},
  heroExtra:crown(540,770,.8,-8),
  badges:[
   {inner:lamp(0,70,.55,true),label:'DAY 1',col:'#7fd6ff'},
   {inner:screw(0,-40,1.2,-20),label:'1 SCREW',col:'#c8ccd6'},
   {inner:meatballs(0,40,.75),label:'MEATBALLS',col:'#ffb84d'},
   {inner:g('translate(0 60) scale(.8)',worker({shirt:'#b7a58a',eyes:'creepy',mouth:'flat',hair:'spike'})+beard),label:'SINCE 2009',col:'#ff8fd0'},
  ]});

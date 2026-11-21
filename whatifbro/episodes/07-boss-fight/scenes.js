// Episode 7 — What if job interviews were boss fights?
function bossHP(t){const k=[[0,1],[S(12),1],[S(12)+.1,.62],[S(23)+.3,.45],[S(24),.3],[S(24)+.4,.15],[S(25),.0]];let v=1;for(let i=0;i<k.length;i++){if(t>=k[i][0]){const n=k[i+1];v=k[i][1];if(i>0&&t<k[i][0]+.4)v=lerp(k[i-1][1],k[i][1],eOut(p(t,k[i][0],k[i][0]+.4)))}}return v}
function youHP(t){const k=[[0,1],[S(8),.8],[S(8)+.4,.35],[S(16),.35],[S(17),.04],[S(26),.04]];let v=1;for(let i=0;i<k.length;i++){if(t>=k[i][0]){v=k[i][1];if(i>0&&t<k[i][0]+.4)v=lerp(k[i-1][1],k[i][1],eOut(p(t,k[i][0],k[i][0]+.4)))}}return v}
function hud(t,show=1){if(show<=0)return '';return `<g opacity="${show}">`+hpBar(80,330,920,bossHP(t),'THE INTERVIEWER  LV.99','#ff2e4d',{h:60})+hpBar(80,1290,560,youHP(t),'YOU  LV.1','#4cd964',{h:54,ls:40})+`</g>`}
function office(){let s=bg('#3a3550','#232036')+`<rect x="0" y="420" width="${W}" height="560" fill="#2b2840"/>${[...Array(4)].map((_,i)=>`<rect x="${70+i*250}" y="470" width="190" height="300" rx="10" fill="#4a5a8a" stroke="${INK}" stroke-width="8"/><path d="M${70+i*250} 620 H${260+i*250} M${165+i*250} 470 V770" stroke="${INK}" stroke-width="6"/>`).join('')}`;return s+floor(1180,'#5a4a6a')}
function interviewer(x,y,s,t,o={}){const sh=o.shake?Math.sin(t*60)*8:0;return g(`translate(${x+sh} ${y}) scale(${s})`,(o.aura?`<ellipse cx="0" cy="-40" rx="${230+Math.sin(t*12)*15}" ry="${270+Math.sin(t*10)*15}" fill="#b04dff" opacity=".35"/>`:'')+worker({shirt:'#3a3f55',eyes:o.eyes||'creepy',mouth:o.mouth||'flat',hair:'bald',glasses:true,glint:true,tie:'#ff2e4d',lh:o.lh||[-110,60],rh:o.rh||[110,60],badge:'BOSS'}))}
function bossDesk(){return `<rect x="200" y="1000" width="680" height="200" rx="16" fill="#6b4226" stroke="${INK}" stroke-width="12"/><rect x="180" y="980" width="720" height="40" rx="12" fill="#8a5530" stroke="${INK}" stroke-width="10"/><rect x="560" y="930" width="140" height="50" rx="6" fill="#fff" stroke="${INK}" stroke-width="6"/>${txt(630,966,'RESUME',24,INK,{font:'Fred',sw:0})}`}
function dmg(x,y,t,t0,label,col='#ff2e4d',size=110){const k=p(t,t0,t0+1.0);if(k<=0||k>=1)return '';return g(`translate(${x} ${y-k*140}) scale(${eBack(clamp(k*3))})`,txt(0,0,label,size,col,{sw:size*.16,extra:`opacity="${(1-k*k).toFixed(2)}"`}))}
function flash(t,t0,d=.12){return t>=t0&&t<t0+d?`<rect width="${W}" height="${H}" fill="#fff" opacity=".8"/>`:''}
function cookie(x,y,s=1){return g(`translate(${x} ${y}) scale(${s})`,`<circle r="60" fill="#d9a066" stroke="${INK}" stroke-width="8"/><circle cx="-20" cy="-15" r="9" fill="#5a3a22"/><circle cx="18" cy="-25" r="8" fill="#5a3a22"/><circle cx="25" cy="15" r="9" fill="#5a3a22"/><circle cx="-15" cy="25" r="7" fill="#5a3a22"/>`)}
function arena(t,o={}){let s=office()+interviewer(540,800,1.5,t,o)+bossDesk();return s}

window.SCENES=()=>[
 [0,t=>{ // hook
   const z=lerp(1,1.1,p(t,0,S(1)));
   let s=bg('#1a0f33','#3a1466')+burst('#ff2e4d',.12,540,800);
   s+=interviewer(540,780,1.6,t,{aura:true,eyes:'creepy',mouth:'grin'});
   s+=g('translate(540 1250) scale(.42)',youHead({eyes:'huge',mouth:'grit',sweat:true}));
   s+=g(`translate(540 350) scale(${pop(t,.4,.35)}) rotate(-4)`,txt(0,0,'BOSS FIGHT',150,'#ff2e4d',{sw:20}));
   return cam(z,540,900,s);
 }],
 [S(1),t=>{ // walk in, music, hp appears, level 99
   let s=arena(t,{eyes:'creepy',mouth:'flat'});
   s+=you(820,1170,.3,{eyes:'huge',mouth:'grit',sweat:true});
   s+=hud(t,p(t,S(2),S(2)+.3));
   if(t>=S(1)+.8&&t<S(2))s+=txt(540,600,'*BOSS MUSIC*',80,'#ffd23a',{sw:12});
   if(t>=S(3)&&t<S(4))s+=g(`translate(540 560) scale(${pop(t,S(3),.3)})`,txt(0,0,'LV. 99',160,'#ff2e4d',{sw:20}));
   if(t>=S(4)){const k=pop(t,S(4)+.6,.3);s+=g(`translate(820 1180) scale(${k}) rotate(8)`,`<rect x="-120" y="-150" width="240" height="300" fill="#fff" stroke="${INK}" stroke-width="9"/>${txt(0,-90,'RESUME',36,INK,{font:'Fred',sw:0})}<path d="M-80 -50 H80 M-80 -10 H40 M-80 30 H60" stroke="#aaa" stroke-width="8"/><circle cx="40" cy="80" r="34" fill="#c27a4a" opacity=".6"/>`)+txt(820,1400,'(MADE AT 3 AM)',40,'#fff',{font:'Fred',sw:8})}
   return s;
 }],
 [S(5),t=>t<S(6)?titleCard(t,S(5),'ROUND 1','FIGHT!','#ffd23a','#1a0f33'):(()=>{ // tell me about yourself
   let s=arena(t,{eyes:'creepy',mouth:t<E(6)?'o':'grin',rh:[150,-80]});
   s+=you(820,1170,.3,{eyes:'huge',mouth:t>=S(7)?'o':'grit',sweat:true});
   if(t>=S(6)&&t<S(7))s+=bubble(540,620,700,150,['TELL ME ABOUT YOURSELF'],eBack(p(t,S(6),S(6)+.3)),46);
   if(t>=S(7)+1.2&&t<S(8))s+=bubble(540,880,640,150,['UH... MY MOM IS LINDA'],eBack(p(t,S(7)+1.2,S(7)+1.5)),46);
   s+=hud(t)+dmg(540,1140,t,S(8),'CRITICAL HIT!','#ff2e4d',100)+dmg(300,1260,t,S(8)+.2,'-45',`#ff2e4d`,90);
   return cam(1,540,960,s,...shake(t,S(8),.5,30))+flash(t,S(8));
 })()],
 [S(9),t=>t<S(10)?titleCard(t,S(9),'ROUND 2','FIGHT!','#ffd23a','#1a0f33'):(()=>{ // 5 years
   const hit=t>=S(12);
   let s=arena(t,{eyes:hit?'frantic':'creepy',mouth:hit?'scream':t<E(10)?'o':'flat',shake:hit&&t<S(12)+.8,rh:[150,-80]});
   s+=you(820,1170,.3,{eyes:'open',mouth:t>=S(11)?'smile':'grit',brows:t>=S(11)?'angry':null,sweat:t<S(11)});
   if(t>=S(10)&&t<S(11))s+=bubble(540,620,800,150,['WHERE DO YOU SEE','YOURSELF IN 5 YEARS?'],eBack(p(t,S(10),S(10)+.3)),44);
   if(t>=S(11)&&t<S(12))s+=bubble(540,880,500,150,['IN YOUR CHAIR.'],eBack(p(t,S(11),S(11)+.3)),50);
   if(t>=S(11)+.6&&t<S(12)+.1){const k=p(t,S(11)+.6,S(12)+.05);s+=g(`translate(540 ${lerp(1050,720,k)})`,`<circle r="50" fill="#ffd23a" stroke="${INK}" stroke-width="8"/>`)}
   s+=hud(t)+dmg(540,560,t,S(12),'SUPER EFFECTIVE!','#ffd23a',90)+dmg(780,460,t,S(12)+.15,'-38','#ff2e4d',90);
   return cam(1,540,960,s,...shake(t,S(12),.5,26))+flash(t,S(12));
 })()],
 [S(13),t=>t<S(13)+.9?titleCard(t,S(13),'ROUND 3','SPECIAL MOVE','#ff2e4d','#1a0f33'):(()=>{ // weakness
   const blocked=t>=S(16);
   let s=arena(t,{aura:true,eyes:'creepy',mouth:t<E(14)?'o':blocked?'grin':'flat',rh:blocked?[30,-140]:[150,-80],lh:blocked?[-30,-140]:[-110,60]});
   s+=you(820,1170,.3,{eyes:t>=S(17)?'huge':'open',mouth:t>=S(17)?'grit':'smile',sweat:t>=S(17)});
   if(t>=S(14)&&t<S(15))s+=bubble(540,620,760,150,["WHAT'S YOUR","BIGGEST WEAKNESS?"],eBack(p(t,S(14),S(14)+.3)),46);
   if(t>=S(15)+1.2&&t<S(16))s+=bubble(540,880,560,150,['I WORK TOO HARD'],eBack(p(t,S(15)+1.2,S(15)+1.5)),48);
   if(blocked){s+=g(`translate(540 700) scale(${pop(t,S(16),.3)})`,`<path d="M0 -170 L150 -110 Q150 80 0 170 Q-150 80 -150 -110 Z" fill="#7fd6ff" fill-opacity=".6" stroke="${INK}" stroke-width="12"/>`+txt(0,20,'BLOCK',70,'#fff',{sw:10}));
     if(t>=S(16)+1.0)s+=txt(540,480,'HEARD IT 4,000x',80,'#ffd23a',{sw:12})}
   s+=hud(t)+dmg(300,1260,t,S(17),'-1 HP LEFT','#ff2e4d',70);
   if(t>=S(17))s+=`<rect width="${W}" height="${H}" fill="#ff1f3d" opacity="${Math.sin(t*8)>0?.18:.05}"/>`;
   return s;
 })()],
 [S(18),t=>{ // one move left -> cookies -> freeze -> eats
   if(t<S(21)){
     let s=bg('#1a0f33','#0b0618')+burst('#ffd23a',t>=S(20)?.3:.05,540,1000);
     s+=g('translate(540 1080)',`<path d="M-260 -80 L260 -80 L230 260 L-230 260 Z" fill="#c9a26b" stroke="${INK}" stroke-width="14" stroke-linejoin="round"/><path d="M-260 -80 Q0 ${t>=S(19)+.4?-300:-120} 260 -80" fill="#b08a5a" stroke="${INK}" stroke-width="12"/>`);
     if(t>=S(19)+.4)s+=`<ellipse cx="540" cy="960" rx="${220+Math.sin(t*8)*10}" ry="140" fill="#fff8c0" opacity=".5"/>`;
     if(t>=S(20))[0,1,2].forEach(i=>s+=cookie(400+i*140,900-pop(t,S(20)+i*.12,.3)*120,1.1));
     if(t>=S(20))s+=g(`translate(540 500) scale(${pop(t,S(20),.35)})`,txt(0,0,'COOKIES',160,'#ffd23a',{sw:20}))+sparkles(540,900,330,200,t,6);
     if(t<S(19))s+=g(`translate(540 520) scale(${pop(t,S(18),.3)})`,txt(0,0,'1 MOVE LEFT',120,'#fff',{sw:16}));
     return s+hud(t,.9);}
   let s=arena(t,{eyes:t>=S(25)?'closed':t>=S(21)&&t<S(23)?'frantic':'happy',mouth:t>=S(23)&&t<S(25)?'o':t>=S(25)?'smile':'o',rh:[60,-40],lh:[-60,-40]});
   const left=t<S(23)?3:t<S(24)?2:t<S(24)+.8?Math.max(0,3-1-Math.floor((t-S(24))*4)):0;
   for(let i=0;i<left;i++)s+=cookie(400+i*140,960,.8);
   if(t>=S(22))s+=g(`translate(870 560) scale(${pop(t,S(22),.3)}) rotate(6)`,`<rect x="-160" y="-110" width="320" height="220" fill="#fff" stroke="${INK}" stroke-width="10"/><rect x="-160" y="-110" width="320" height="60" fill="#ff2e4d" stroke="${INK}" stroke-width="10"/>`+txt(0,-65,'LAST LUNCH',34,'#fff',{sw:0,font:'Fred'})+txt(0,60,'2016',90,INK,{sw:0}));
   if(t>=S(23))for(let i=0;i<6;i++){const k=((t*2+i*.17)%1);s+=`<circle cx="${540+(i-3)*40+k*80*(i%2?1:-1)}" cy="${700+k*200}" r="8" fill="#d9a066" opacity="${1-k}"/>`}
   s+=you(820,1170,.3,{eyes:'open',mouth:'smile',sweat:false});
   s+=hud(t);
   if(t>=S(25))s+=g(`translate(540 560) scale(${pop(t,S(25)+.3,.35)})`,txt(0,0,'K.O.',200,'#ff2e4d',{sw:22}));
   return s;
 }],
 [S(26),t=>{ // you win, hired, cookies forever
   if(t<S(28)){let s=bg('#ffd23a','#ff9b3d')+burst('#fff',.3);
     s+=you(540,680,.46,{eyes:'open',mouth:'smile',sweat:false,wave:150+Math.sin(t*10)*10})+sparkles(540,880,380,330,t,7);
     s+=g(`translate(540 360) scale(${pop(t,S(26),.35)}) rotate(-4)`,txt(0,0,'YOU WIN!',170,'#fff',{sw:22}));
     if(t>=S(27))s+=stamp(540,1260,'HIRED','#20a84a',eOut(p(t,S(27),S(27)+.15)),-10,130);
     return s;}
   let s=bg('#ffe2b8','#f8c98a')+floor(1280,'#c9a26b');
   s+=`<rect x="80" y="760" width="380" height="520" rx="20" fill="#c8ccd6" stroke="${INK}" stroke-width="12"/><rect x="120" y="900" width="300" height="240" rx="14" fill="#2b2240" stroke="${INK}" stroke-width="10"/><rect x="135" y="915" width="270" height="210" rx="10" fill="#ff9b3d" opacity="${.5+.3*Math.sin(t*6)}"/>${[0,1,2].map(i=>`<circle cx="${130+i*70}" cy="810" r="18" fill="#2b2240"/>`).join('')}`;
   s+=you(620,820,.42,{eyes:'open',mouth:'flat',sweat:true})+g('translate(620 712)',`<path d="M-80 0 C-110 -20 -100 -90 -50 -80 C-40 -130 40 -130 50 -80 C100 -90 110 -20 80 0 Z" fill="#fff" stroke="${INK}" stroke-width="8"/><rect x="-80" y="-10" width="160" height="30" rx="8" fill="#fff" stroke="${INK}" stroke-width="8"/>`);
   s+=interviewer(910,1080,.95,t,{eyes:'happy',mouth:'o',rh:[60,-40],lh:[-60,-40]});
   s+=cookie(890,1000,.5)+cookie(950,1010,.45);
   if(t>=S(29))s+=g(`translate(910 640) scale(${pop(t,S(29),.3)})`,txt(0,0,'FOR HIM.',80,'#ff2e4d',{sw:12}));
   if(t>=S(30))s+=stamp(540,420,'FOREVER','#ff2e4d',eOut(p(t,S(30),S(30)+.15)),-8,130);
   return s;
 }],
];

window.COVER=()=>coverTemplate({l1:'WHAT IF JOB INTERVIEWS',l2:'WERE BOSS FIGHTS?',ep:7,
  hero:{eyes:'huge',mouth:'grit',brows:'angry'},
  heroExtra:'',
  badges:[
   {inner:interviewer(0,80,.75,0,{eyes:'creepy',mouth:'grin'}),label:'LV. 99',col:'#ff2e4d'},
   {inner:txt(0,10,'CRIT',70,'#ff2e4d',{sw:10})+txt(0,80,'HIT!',70,'#ffd23a',{sw:10}),label:'ROUND 1',col:'#ffd23a'},
   {inner:`<path d="M0 -90 L80 -60 Q80 40 0 90 Q-80 40 -80 -60 Z" fill="#7fd6ff" stroke="${INK}" stroke-width="9"/>`,label:'BLOCKED',col:'#7fd6ff'},
   {inner:cookie(-35,-20,.8)+cookie(40,30,.8),label:'COOKIES',col:'#d9a066'},
  ]});

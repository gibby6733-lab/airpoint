// Episode 6 — What if you could teleport... but only 2 inches?
const STEP=34; // "two inches" on screen
function cape(t){const f=Math.sin(t*6)*25;return `<path d="M-170 290 Q-420 ${620+f} ${-400} ${960+f} L400 ${960-f} Q420 ${620-f} 170 290 Z" fill="#e0243a" stroke="${INK}" stroke-width="16" stroke-linejoin="round"/>`}
function mask(){return `<path fill-rule="evenodd" d="M-250 -60 Q0 -110 250 -60 L240 40 Q0 0 -240 40 Z M-160 -20 a58 52 0 1 0 116 0 a58 52 0 1 0 -116 0 Z M44 -20 a58 52 0 1 0 116 0 a58 52 0 1 0 -116 0 Z" fill="#16111f" opacity=".95"/>`}
function hero(x,y,s,t,o={}){return g(`translate(${x} ${y}) scale(${s})`,(o.cape?cape(t):'')+youBody(o)+(o.mask?mask():'')+(o.logo?g('translate(0 470)',`<circle r="80" fill="#ffd23a" stroke="${INK}" stroke-width="12"/>${txt(0,30,'2"',80,INK,{sw:0})}`):''))}
function ghost(x,y,s,k){if(k<=0)return '';return g(`translate(${x} ${y}) scale(${s})`,`<g opacity="${(1-k)*.6}"><ellipse cx="0" cy="300" rx="260" ry="640" fill="#9fe3ff"/></g>`)}
function zapFx(x,y,t,t0,s=1){const k=p(t,t0,t0+.45);if(k<=0||k>=1)return '';return g(`translate(${x} ${y}) scale(${s})`,`<circle r="${80+k*220}" fill="none" stroke="#9fe3ff" stroke-width="${18*(1-k)}"/>`+[...Array(8)].map((_,i)=>{const a=i*.785,r=60+k*240;return `<path d="M${Math.cos(a)*r*.5} ${Math.sin(a)*r*.5} L${Math.cos(a)*r} ${Math.sin(a)*r}" stroke="#fff35a" stroke-width="10" stroke-linecap="round" opacity="${1-k}"/>`}).join(''))}
function ruler(x,y,k,label='2 INCHES'){if(k<=0)return '';return g(`translate(${x} ${y}) scale(${k})`,`<rect x="-200" y="-40" width="400" height="80" rx="10" fill="#ffd23a" stroke="${INK}" stroke-width="9"/>${[...Array(13)].map((_,i)=>`<path d="M${-180+i*30} -40 V${i%2?-15:0}" stroke="${INK}" stroke-width="5"/>`).join('')}${txt(0,28,label,40,INK,{font:'Fred',sw:0})}`)}
function tree(x,y,s){return g(`translate(${x} ${y}) scale(${s})`,`<rect x="-40" y="-100" width="80" height="460" fill="#8a5530" stroke="${INK}" stroke-width="10"/><path d="M0 0 L-140 -150 M0 60 L130 -60" stroke="#8a5530" stroke-width="30" stroke-linecap="round"/><circle cx="-90" cy="-260" r="170" fill="#5ac94a" stroke="${INK}" stroke-width="10"/><circle cx="110" cy="-230" r="150" fill="#4cb83a" stroke="${INK}" stroke-width="10"/><circle cx="10" cy="-370" r="160" fill="#6ad45a" stroke="${INK}" stroke-width="10"/>`)}
function kitty(x,y,s,o={}){const eyes=o.meh?`<path d="M-50 -10 H-14 M14 -10 H50" stroke="${INK}" stroke-width="9" stroke-linecap="round"/><circle cx="-32" cy="0" r="6" fill="${INK}"/><circle cx="32" cy="0" r="6" fill="${INK}"/>`:`<circle cx="-32" cy="-5" r="16" fill="#fff" stroke="${INK}" stroke-width="6"/><circle cx="32" cy="-5" r="16" fill="#fff" stroke="${INK}" stroke-width="6"/><circle cx="-32" cy="-3" r="7" fill="${INK}"/><circle cx="32" cy="-3" r="7" fill="${INK}"/>`;
  return g(`translate(${x} ${y}) scale(${s})`,`<ellipse cx="0" cy="110" rx="80" ry="90" fill="#ff9b3d" stroke="${INK}" stroke-width="9"/><path d="M-70 -50 L-60 -130 L-15 -80 Z M70 -50 L60 -130 L15 -80 Z" fill="#ff9b3d" stroke="${INK}" stroke-width="8" stroke-linejoin="round"/><ellipse cx="0" cy="0" rx="85" ry="75" fill="#ff9b3d" stroke="${INK}" stroke-width="9"/>${eyes}<path d="M-6 20 L6 20 L0 28 Z" fill="#ff7a9a"/>`)}
function robber(x,y,s,o={}){return g(`translate(${x} ${y}) scale(${s})`,worker(Object.assign({shirt:'#2b2d3a',eyes:'normal',mouth:'grin',hair:'',lh:[-90,60],rh:[100,60]},o))+`<rect x="-80" y="-150" width="160" height="40" rx="12" fill="${INK}"/><circle cx="-26" cy="-132" r="12" fill="#fff"/><circle cx="26" cy="-132" r="12" fill="#fff"/><circle cx="-26" cy="-130" r="6" fill="${INK}"/><circle cx="26" cy="-130" r="6" fill="${INK}"/>`+(o.bag?`<g transform="translate(120 40)"><path d="M-60 0 Q-80 120 0 120 Q80 120 60 0 Q30 -20 0 -20 Q-30 -20 -60 0 Z" fill="#c9a26b" stroke="${INK}" stroke-width="8"/>${txt(0,80,'$',70,'#20a84a',{sw:0})}</g>`:''))}
function ball(x,y,s=1){return g(`translate(${x} ${y}) scale(${s})`,`<circle r="70" fill="#ff5d3a" stroke="${INK}" stroke-width="10"/><path d="M-70 0 Q0 -30 70 0 M0 -70 Q-30 0 0 70" stroke="#c23a1a" stroke-width="7" fill="none"/><ellipse cx="-25" cy="-30" rx="18" ry="10" fill="#fff" opacity=".5"/>`)}
function gym(){let s=bg('#ffe2a8','#f8c070')+`<rect y="220" width="${W}" height="200" fill="#4f7cff"/>${[...Array(5)].map((_,i)=>`<rect x="${i*230}" y="220" width="200" height="200" fill="none" stroke="${INK}" stroke-width="6"/>`).join('')}`+floor(1280,'#d9a066');return s+`<path d="M540 1280 V1920" stroke="#fff" stroke-width="10" opacity=".6"/>`}

window.SCENES=()=>[
 [0,t=>{ // hook
   const z=lerp(1,1.1,p(t,0,S(1)));
   let s=bg('#9b4dff','#4f10b8')+burst('#fff',.15);
   const jump=Math.floor((t*1.5))%2;
   if(t>.8)s+=ghost(540-STEP*(1-jump)*2,700,.5,((t*1.5)%1));
   s+=hero(540-STEP*jump*2,700,.5,t,{cape:true,mask:true,eyes:'open',mouth:'smile',sweat:false});
   s+=ruler(540,520,pop(t,.9,.3));
   return cam(z,540,960,s);
 }],
 [S(1),t=>{ // tingle, blink, 2 inches
   let s=bg('#bfe9ff','#8fd0ff')+`<rect x="660" y="260" width="300" height="300" rx="16" fill="#fff6c8" stroke="${INK}" stroke-width="12"/><path d="M810 260 V560 M660 410 H960" stroke="${INK}" stroke-width="10"/>`+floor(1280,'#a8693a');
   const jumps=[S(2)+.6,S(4)+.3];let x=440;jumps.forEach(j=>{if(t>=j)x-=STEP*1.2});
   jumps.forEach(j=>{if(t>=j&&t<j+.6)s+=ghost(x+STEP*1.2,820,.46,p(t,j,j+.6))});
   s+=you(x,820,.46,{eyes:t>=S(2)?'huge':'open',mouth:t>=S(2)?'o':'flat',sweat:t>=S(3)});
   if(t<S(2))s+=sparkles(x,1000,200,300,t,6,'#9fe3ff');
   jumps.forEach(j=>s+=zapFx(x+STEP*.6,1000,t,j,.8));
   if(t>=S(3))s+=ruler(440,560,pop(t,S(3),.3))+`<path d="M${440-STEP*1.2} 640 V720 M440 640 V720" stroke="#ff2e4d" stroke-width="8"/>`;
   if(t>=S(4)+.6)s+=txt(540,1380,'...',100,'#fff',{sw:12});
   return s;
 }],
 [S(5),t=>{ // superhero reveal
   let s=bg('#ffd23a','#ff9b3d')+burst('#fff',.3)+speedLines(t,'#fff',.25);
   const suited=t>=S(6)+.6;
   s+=hero(540,700,.56,t,{cape:suited,mask:suited,logo:suited,eyes:'open',mouth:'smile',sweat:false,brows:suited?'angry':null,wave:suited?150:120});
   if(t>=S(7)){const k=pop(t,S(7),.35);s+=g(`translate(540 360) scale(${k}) rotate(-4)`,`<rect x="-460" y="-120" width="920" height="230" rx="40" fill="#e0243a" stroke="${INK}" stroke-width="14"/>`+txt(0,-20,'CAPTAIN',100,'#ffd23a',{sw:14})+txt(0,90,'2 INCHES',110,'#fff',{sw:16}))}
   else if(t>=S(5))s+=g(`translate(540 380) scale(${pop(t,S(5),.3)})`,txt(0,0,'SUPERHERO?!',120,'#fff',{sw:18}));
   return s;
 }],
 [S(8),t=>{ // cat mission
   let s=bg('#bfe9ff','#e6f6ff')+`<rect y="1280" width="${W}" height="640" fill="#7ad46a"/><path d="M0 1280 H${W}" stroke="${INK}" stroke-width="12"/>`+tree(760,940,1.1);
   const down=eIO(p(t,S(11),S(11)+1.4));
   s+=kitty(lerp(700,660,down),lerp(560,1150,down),.8,{meh:t>=S(12)});
   let x=250;if(t>=S(9)+.2)x+=STEP*1.2;
   if(t>=S(9)+.2&&t<S(9)+.8)s+=ghost(250,800,.42,p(t,S(9)+.2,S(9)+.8));
   s+=hero(x,800,.42,t,{cape:true,mask:true,eyes:t>=S(12)?'open':'open',mouth:t>=S(11)?'grit':'smile',sweat:t>=S(11),wave:t<S(9)?150:null});
   s+=zapFx(x,1000,t,S(9)+.2,.7);
   if(t>=S(10))s+=ruler(300,560,pop(t,S(10),.3),'2 IN CLOSER');
   if(t>=S(8)&&t<S(9))s+=bubble(700,280,420,130,['HELP! MEOW'],eBack(p(t,S(8)+.4,S(8)+.7)),50);
   if(t>=S(12))s+=txt(660,960,'...',110,'#fff',{sw:14});
   return s;
 }],
 [S(13),t=>{ // bank robbery, stuck in wall
   if(t>=S(18)){ // news
     let s=bg('#1e1e2e','#0b0b14')+`<rect x="80" y="380" width="920" height="760" rx="30" fill="#2b2240" stroke="${INK}" stroke-width="16"/><rect x="110" y="410" width="860" height="560" fill="#bfe9ff"/>`;
     s+=`<rect x="110" y="410" width="860" height="560" fill="#7d8496"/>`+`<rect x="560" y="410" width="410" height="560" fill="#9aa3b5" stroke="${INK}" stroke-width="8"/>`+hero(560,560,.36,t,{cape:true,mask:true,eyes:'huge',mouth:'grit',sweat:true});
     s+=`<rect x="560" y="410" width="410" height="560" fill="#9aa3b5"/>${[...Array(5)].map((_,i)=>`<path d="M560 ${470+i*110} H970" stroke="#7d8496" stroke-width="6"/>`).join('')}`;
     s+=`<rect x="110" y="890" width="860" height="120" fill="#e0243a"/>`+txt(130,970,'LOCAL MAN STUCK IN WALL',56,'#fff',{anchor:'start',sw:8});
     s+=`<rect x="110" y="410" width="240" height="70" fill="#e0243a"/>`+txt(230,462,'BREAKING',44,'#fff',{sw:0});
     if(t>=S(19))s+=g(`translate(540 1260) scale(${pop(t,S(19),.3)})`,txt(0,0,'FAMOUS?',110,'#ffd23a',{sw:16}));
     return s;}
   let s=bg('#d8d0bc','#c2b89e')+floor(1300,'#8a8070');
   // vault wall on right
   const vaultX=560;
   s+=`<rect x="${vaultX}" y="200" width="560" height="1100" fill="#9aa3b5" stroke="${INK}" stroke-width="12"/><circle cx="${vaultX+260}" cy="720" r="230" fill="#7d8496" stroke="${INK}" stroke-width="14"/><circle cx="${vaultX+260}" cy="720" r="60" fill="#c8ccd6" stroke="${INK}" stroke-width="10"/>${[0,1,2,3].map(i=>`<path d="M${vaultX+260} 720 L${vaultX+260+Math.cos(i*1.57)*150} ${720+Math.sin(i*1.57)*150}" stroke="${INK}" stroke-width="16"/>`).join('')}`;
   const stuck=t>=S(14)+.5;
   const hx=stuck?vaultX+10:300;
   if(t>=S(14)+.5&&t<S(14)+1.1)s+=ghost(300,780,.42,p(t,S(14)+.5,S(14)+1.1));
   s+=hero(hx,780,.42,t,{cape:true,mask:true,eyes:stuck?'huge':'open',mouth:stuck?'grit':'smile',brows:stuck?null:'angry',sweat:stuck});
   if(stuck)s+=`<rect x="${vaultX+20}" y="660" width="260" height="660" fill="#9aa3b5"/><path d="M${vaultX+20} 660 V1300" stroke="${INK}" stroke-width="12"/>`+[...Array(4)].map((_,i)=>`<path d="M${vaultX+20} ${700+i*150} l-30 30 l20 20" stroke="${INK}" stroke-width="6" fill="none"/>`).join('');
   s+=zapFx(hx,1000,t,S(14)+.5,.8);
   // robbers
   if(t<S(14)){s+=`<rect width="${W}" height="140" y="0" fill="#e0243a" opacity="${Math.sin(t*12)>0?.35:.1}"/>`;s+=g(`translate(540 400) scale(${pop(t,S(13),.3)})`,txt(0,0,'ROBBERY!',130,'#ff2e4d',{sw:18}))}
   if(t>=S(16)){const w=eIO(p(t,S(16)-.2,S(16)+1.4));s+=robber(lerp(-150,330,w),1050,1.0,{bag:true,rh:[150,40]})+robber(lerp(-400,120,w),1060,1.0,{bag:true,rh:[150,40]})}
   if(t>=S(17)){s+=g('translate(420 820) rotate(-15)',`<rect x="-40" y="-70" width="80" height="140" rx="12" fill="#1e1e2e" stroke="${INK}" stroke-width="7"/>`);
     if(t>=S(17)+.9&&t<S(17)+1.1)s+=`<rect width="${W}" height="${H}" fill="#fff" opacity=".85"/>`}
   if(t>=S(15)&&t<S(16))s+=txt(540,470,'STUCK.',140,'#ff2e4d',{sw:18});
   return s;
 }],
 [S(20),t=>{ // dodgeball
   let s=gym();
   const champ=t>=S(26);
   if(!champ){
     let x=540;const z=[S(22),S(24)+.5,S(25)+.3,S(25)+.7];let shift=0;z.forEach((zz,i)=>{if(t>=zz)shift=(i%2?0:1)});x=540-STEP*1.3*shift;
     s+=crowd(t,1720,6,.6,12,{eyes:'normal',mouth:'o',amp:2});
     s+=hero(x,760,.42,t,{cape:true,mask:true,eyes:t>=S(21)?'huge':'open',mouth:t>=S(23)?'smile':'grit',sweat:t>=S(21)&&t<S(23)});
     z.forEach(zz=>s+=zapFx(x,960,t,zz,.7));
     // balls
     const throws=[[S(21),S(22)+.35],[S(24),S(24)+.8],[S(25),S(25)+.55],[S(25)+.4,S(25)+.95]];
     throws.forEach(([a,b],i)=>{if(t>=a&&t<b+.6){const k=(t-a)/(b-a);const bx=lerp(1200,-200,k);const by=lerp(760,700,k)+(i%2?60:-40);s+=ball(bx,by,.9)}});
     if(t>=S(23)&&t<S(24))s+=ruler(540,520,pop(t,S(23),.3),'EXACTLY 2 IN');
     if(t>=S(24)){const n=Math.min(9,Math.floor((t-S(24))*4));for(let i=0;i<n;i++)s+=txt(140+(i%3)*400,420+Math.floor(i/3)*110,'MISS',70,'#ff2e4d',{sw:10,rot:-8+i*3})}
     return s;}
   s+=burst('#ffd23a',.3,540,800)+crowd(t,1720,6,.6,12,{cheer:true,mouth:'grin'});
   s+=hero(540,700,.46,t,{cape:true,mask:true,eyes:'open',mouth:'smile',wave:150+Math.sin(t*8)*10,sweat:false});
   if(t>=S(27))s+=g(`translate(820 640) scale(${pop(t,S(27),.35)})`,`<path d="M-90 -120 H90 Q90 40 0 60 Q-90 40 -90 -120 Z" fill="#ffd23a" stroke="${INK}" stroke-width="12"/><path d="M-90 -90 Q-160 -90 -150 -20 Q-140 20 -80 10 M90 -90 Q160 -90 150 -20 Q140 20 80 10" fill="none" stroke="${INK}" stroke-width="12"/><rect x="-25" y="60" width="50" height="60" fill="#ffd23a" stroke="${INK}" stroke-width="10"/><rect x="-80" y="120" width="160" height="40" rx="8" fill="#a8693a" stroke="${INK}" stroke-width="10"/>${txt(0,-20,'#1',70,INK,{sw:0})}`)+txt(540,400,'CHAMPION',140,'#ffd23a',{sw:20});
   if(t>=S(28))s+=ruler(540,1340,pop(t,S(28)+.6,.35),'ALL YOU NEED');
   s+=sparkles(540,800,400,330,t,7);
   return s;
 }],
];

window.COVER=()=>coverTemplate({l1:'WHAT IF YOU COULD',l2:'TELEPORT 2 INCHES?',ep:6,
  hero:{eyes:'open',mouth:'smile'},
  heroExtra:g('translate(540 1110) scale(.86)',mask())+ruler(540,1440,.9),
  badges:[
   {inner:kitty(0,10,.75,{meh:true}),label:'MISSION 1',col:'#ff9b3d'},
   {inner:robber(0,90,.75,{bag:true}),label:'ROBBERY',col:'#9aa3b5'},
   {inner:txt(0,-10,'STUCK',60,'#ff2e4d',{sw:8})+txt(0,60,'IN WALL',50,INK,{sw:0}),label:'NEWS',col:'#e0243a'},
   {inner:ball(0,0,1),label:'CHAMPION',col:'#ffd23a'},
  ]});

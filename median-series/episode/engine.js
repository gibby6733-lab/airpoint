// MEDIAN episode engine — data-driven, deterministic (renderAt(t)), 60 fps safe.
// Timeline = scenes -> shots (from the script) -> lines (timed by word count until real voices replace them).
(function(){
const A='../assets/characters/';
// Character registry: src, viewBox height (units), bottom padding (units), size factor
const MAIN={dex:1.10,wren:1.00,marcus:0.88,gordy:0.96,kenzie:1.04,tunk:1.06};
const CH={};
for(const k in MAIN) CH[k]={src:A+k+'_front_v02.svg',vb:700,pad:8,sf:MAIN[k]/1.10};
['frink','krupp','bev','kevin','mallory','gaines','okonkwo','man_suitcase','yoga_mom','shaking_man','town1','town2','town3','town4','town5','town6','town7','town8']
  .forEach(k=>CH[k]={src:A+'side/'+k+'.svg',vb:860,pad:40,sf:1.0});
['teen','younger_kid'].forEach(k=>CH[k]={src:A+'side/'+k+'.svg',vb:700,pad:22,sf:0.9});
window.CH=CH;

const WHO={'DEX':'dex','WREN':'wren','WREN (O.S.)':'wren','MARCUS':'marcus','GORDY':'gordy','KENZIE':'kenzie','TUNK':'tunk',
 'FRINK':'frink','MAYOR KRUPP':'krupp','BEV':'bev','BIG KEVIN':'kevin','OFFICER MALLORY':'mallory','PRINCIPAL GAINES':'gaines',
 'MS. OKONKWO-HALE':'okonkwo','MAN':'man_suitcase','YOGA MOM':'yoga_mom','SHAKING MAN':'shaking_man','TEEN REVIEWER':'teen',
 'YOUNGER KID':'younger_kid','TOWNSPERSON 1':'town1','CUSTOMER':'town3','CUSTOMER 2':'town2'};
const GROUPS={'MARCUS, WREN, KENZIE, GORDY':['marcus','wren','kenzie','gordy']};

const ease=x=>x<=0?0:x>=1?1:x*x*(3-2*x);
const easeOut=x=>x<=0?0:x>=1?1:1-Math.pow(1-x,3);
const lerp=(a,b,k)=>a+(b-a)*k;
window.EZ={ease,easeOut,lerp};

// ---------- timeline build ----------
function lineDur(text){const w=text.replace(/[♪*]/g,'').trim().split(/\s+/).filter(Boolean).length;return Math.min(9,Math.max(1.25,w*0.36+0.65));}
window.buildTimeline=function(script,STAGING){
  const T=[];let t=0;
  for(const sc of script){
    const st=STAGING[sc.sc]; if(!st) continue;
    let shot=null; const shots=[];
    for(const b of sc.beats){
      if(b.t==='shot'){shot={id:b.id,cfg:st.shots[b.id]||{},lines:[]};shots.push(shot);}
      else if(shot) shot.lines.push(b);
    }
    let cast=st.cast||[], bg=st.bg;
    for(const s of shots){
      if(s.cfg.skip) continue;
      if(s.cfg.cast) cast=s.cfg.cast; if(s.cfg.bg) bg=s.cfg.bg;
      const seg={sc:sc.sc,id:s.id,cfg:s.cfg,cast,bg,start:t,lines:[]};
      t+=s.cfg.pre||0;
      for(const ln of s.lines){const d=(s.cfg.lineScale||1)*lineDur(ln.text)+(ln.paren?0.25:0);seg.lines.push({...ln,start:t,end:t+d});t+=d+0.12;}
      t+=s.cfg.post||0;
      t=Math.max(t,seg.start+(s.cfg.min||1.4));
      seg.end=t; T.push(seg);
    }
  }
  return T;
};

// ---------- stage ----------
const stage=()=>document.getElementById('stage');
let curBgKey=null, imgs={};
function setBg(key){
  if(key===curBgKey) return; curBgKey=key;
  document.getElementById('bg').innerHTML=(window.BG[key]||(()=>''))();
  document.getElementById('fg').innerHTML=((window.FG[key])||(()=>''))();
}
function getImg(id){
  if(!imgs[id]){const im=document.createElement('img');im.src=CH[id].src;im.className='ch';document.getElementById('cast').appendChild(im);imgs[id]=im;}
  return imgs[id];
}
window.preloadAll=function(){for(const id in CH) getImg(id).style.display='none';};
function placeChar(id,spec,k,floor,talkAmt,t,extra){
  const c=CH[id], im=getImg(id);
  const h=c.vb*k*c.sf*(spec.s||1);
  im.style.display='block';
  im.style.height=h+'px';
  const w=h*(c.vb===860?400/860:(c.vb===700&&c.src.includes('side')?400/700:560/700));
  im.style.left=(spec.x-w/2)+'px';
  im.style.top=(floor-h+c.pad*k*c.sf*(spec.s||1)+(spec.dy||0))+'px';
  const ph=(spec.x*0.013)%6.28;
  const breathe=1+0.006*Math.sin(t*2.1+ph);
  const bob=talkAmt>0?Math.abs(Math.sin(t*9.5+ph))*10*talkAmt:0;
  const sway=talkAmt>0?Math.sin(t*4.7+ph)*1.6*talkAmt:0;
  const flip=spec.flip?-1:1;
  const ex=extra||{};
  im.style.transform=`translate(${ex.dx||0}px,${(ex.dy||0)-bob}px) rotate(${sway+(ex.rot||0)}deg) scale(${flip*breathe*(ex.sx||1)},${(2-breathe)*(ex.sy||1)})`;
  im.style.opacity=ex.op==null?1:ex.op;
  im.style.zIndex=spec.z||Math.round(floor);
}
window.renderAt=function(t){
  const TL=window.TL; let seg=TL.find(s=>t>=s.start&&t<s.end)||TL[TL.length-1];
  const lt=t-seg.start, D=seg.end-seg.start, cfg=seg.cfg;
  setBg(cfg.bgKey||seg.bg);
  // who is talking
  const ln=seg.lines.find(l=>t>=l.start&&t<l.end);
  let talkers={};
  if(ln){const w=WHO[ln.who]; if(w) talkers[w]=1; (GROUPS[ln.who]||[]).forEach(x=>talkers[x]=1);}
  // cast
  for(const id in imgs) imgs[id].style.display='none';
  const k=cfg.k||seg.cast.k||0.9, floor=cfg.floor||seg.cast.floor||1000;
  // inserts first, so acts can drive them
  const ins=document.getElementById('ins');
  if(cfg.insert&&!(cfg.insertPreOnly&&lt>=(cfg.pre||0))){ins.style.display='block'; if(ins.dataset.key!==cfg.insert){ins.innerHTML=(window.INS[cfg.insert]||(()=>''))();ins.dataset.key=cfg.insert;}}
  else {ins.style.display='none';if(!cfg.insert)ins.dataset.key='';}
  document.getElementById('fx').innerHTML='';
  const fx=window.ACTS[cfg.act]?window.ACTS[cfg.act](lt,D,seg,t)||{}:{};
  if(!cfg.hideCast){
    for(const spec of (seg.cast.list||[])){
      const e=(fx.chars||{})[spec.id];
      if(e&&e.hide) continue;
      const tl=talkers[spec.id]?(ln?Math.min(1,(t-ln.start)/0.15,(ln.end-t)/0.15):0):0;
      placeChar(spec.id,spec,k,floor,tl,t,e);
    }
  }
  // camera
  const cam=cfg.cam||{z:1,x:960,y:540};
  let cx=cam.x||960, cy=cam.y||540, z=cam.z||1;
  if(cam.who){const sp=(seg.cast.list||[]).find(s=>s.id===cam.who); if(sp){cx=sp.x; const c=CH[sp.id]; cy=floor-c.vb*k*c.sf*(cam.head?0.8:0.55);}}
  const push=cam.push||1.035; z*=lerp(1,push,ease(lt/D));
  if(fx.cam){cx=fx.cam.x??cx;cy=fx.cam.y??cy;z=fx.cam.z??z;}
  const shake=fx.shake||0;
  const sx=shake?Math.sin(t*61)*shake:0, sy=shake?Math.cos(t*47)*shake:0;
  const tx=960-cx*z+sx, ty=540-cy*z+sy;
  // clamp so we never see outside the 1920x1080 world
  const ctx=Math.min(0,Math.max(1920-1920*z,tx)), cty=Math.min(0,Math.max(1080-1080*z,ty));
  document.getElementById('world').style.transform=`translate(${ctx}px,${cty}px) scale(${z})`;
  // close-up overlay
  const cu=document.getElementById('cu');
  if(cfg.cu){cu.style.display='block';cu.style.background=cfg.cuBg||'#E8DCC2';
    const img=document.getElementById('cuimg'); const src=A+'expr/'+cfg.cu+'.svg'; if(img.dataset.src!==src){img.src=src;img.dataset.src=src;}
    const who=cfg.cu.split('_')[0]; const tk=talkers[who]&&ln?1:0;
    const bob=tk?Math.abs(Math.sin(t*9.5))*12:0; const zin=lerp(1,1.06,ease(lt/D));
    img.style.transform=`translateY(${-bob}px) scale(${zin*(1+0.008*Math.sin(t*2.1))})`;
  } else cu.style.display='none';
  // inserts (screen-space)
  if(window.ACTS[cfg.act+'_post']) window.ACTS[cfg.act+'_post'](lt,D,seg,t);
  // captions
  const cap=document.getElementById('cap');
  if(ln&&!cfg.noCap){cap.style.display='block';
    const vo=/V\.O\.|O\.S\./.test(ln.who);
    cap.innerHTML=`<b>${ln.who.replace(' (V.O.)','').replace(' (O.S.)','')}</b>`+(vo?`<i>${ln.text.replace(/\*/g,'')}</i>`:ln.text.replace(/\*/g,''));}
  else cap.style.display='none';
  // act-break wipe (Recall Wipe) at scene starts flagged
  const wipe=document.getElementById('wipe');
  if(cfg.wipeIn&&lt<0.5){wipe.style.display='block';wipe.style.transform=`translateX(${lerp(0,2100,easeOut(lt/0.5))}px)`;}
  else wipe.style.display='none';
};
})();

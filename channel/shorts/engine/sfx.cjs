// Synthesized sound library (all generated with ffmpeg, no third-party samples) + mixer.
const { execFileSync } = require('child_process');
const fs = require('fs'), path = require('path');
const LIB = path.join(__dirname, 'sfxlib');
fs.mkdirSync(LIB, { recursive: true });
const ff = (args) => execFileSync('ffmpeg', ['-y', '-loglevel', 'error', ...args]);
const DEF = {
  ding: ['-f', 'lavfi', '-i', "aevalsrc='0.5*sin(2*PI*1318*t)*exp(-2.2*t)+0.35*sin(2*PI*1760*t)*exp(-3*t)':d=2"],
  bell: ['-f', 'lavfi', '-i', "aevalsrc='0.45*sin(2*PI*523*t)*exp(-1.2*t)+0.3*sin(2*PI*1046*t)*exp(-1.8*t)+0.15*sin(2*PI*1569*t)*exp(-2.5*t)':d=3"],
  thump: ['-f', 'lavfi', '-i', "aevalsrc='0.9*sin(2*PI*(70-30*t)*t)*exp(-9*t)':d=0.6"],
  boom: ['-f', 'lavfi', '-i', "aevalsrc='0.9*sin(2*PI*(48-14*t)*t)*exp(-1.6*t)+0.25*(random(0)*2-1)*exp(-6*t)':d=3"],
  whoosh: ['-f', 'lavfi', '-i', "anoisesrc=c=pink:d=0.8:a=0.6", '-af', 'bandpass=f=900:w=700,afade=t=in:d=0.35,afade=t=out:st=0.4:d=0.4'],
  riser: ['-f', 'lavfi', '-i', "aevalsrc='0.25*sin(2*PI*(120*t+90*t*t))*(t/2.4)+0.08*(random(0)*2-1)*(t/2.4)':d=2.4"],
  heartbeat: ['-f', 'lavfi', '-i', "aevalsrc='0.9*(sin(2*PI*55*t)*exp(-14*t)+sin(2*PI*50*(t-0.28))*exp(-14*(t-0.28))*gte(t,0.28))':d=0.9"],
  tick: ['-f', 'lavfi', '-i', "aevalsrc='0.6*sin(2*PI*2200*t)*exp(-90*t)':d=0.1"],
  tap: ['-f', 'lavfi', '-i', "aevalsrc='0.7*sin(2*PI*2900*t)*exp(-60*t)+0.4*sin(2*PI*1400*t)*exp(-40*t)':d=0.2"],
  static: ['-f', 'lavfi', '-i', 'anoisesrc=c=white:d=1:a=0.35', '-af', 'bandpass=f=2500:w=2000,afade=t=out:st=0.6:d=0.4'],
  splash: ['-f', 'lavfi', '-i', 'anoisesrc=c=pink:d=1.2:a=0.8', '-af', 'lowpass=f=1800,afade=t=out:st=0.05:d=1.1:curve=exp'],
  zap: ['-f', 'lavfi', '-i', "aevalsrc='0.4*sgn(sin(2*PI*120*t))*exp(-4*t)+0.35*(random(0)*2-1)*exp(-7*t)':d=0.6", '-af', 'highpass=f=300'],
  thunder: ['-f', 'lavfi', '-i', 'anoisesrc=c=brown:d=4:a=0.9', '-af', 'lowpass=f=300,afade=t=in:d=0.08,afade=t=out:st=0.4:d=3.5:curve=exp,volume=2.2'],
  alarm: ['-f', 'lavfi', '-i', "aevalsrc='0.25*sgn(sin(2*PI*(if(lt(mod(t,0.5),0.25),880,660))*t))':d=2", '-af', 'lowpass=f=3000'],
  carAlarm: ['-f', 'lavfi', '-i', "aevalsrc='0.3*sin(2*PI*(1000+300*sin(2*PI*6*t))*t)':d=2.5"],
  crash: ['-f', 'lavfi', '-i', "aevalsrc='(random(0)*2-1)*exp(-5*t)*0.8+0.3*sin(2*PI*180*t)*exp(-8*t)':d=1.2", '-af', 'bandpass=f=1500:w=2500'],
  hiss: ['-f', 'lavfi', '-i', 'anoisesrc=c=white:d=1.6:a=0.4', '-af', 'highpass=f=3000,afade=t=in:d=0.1,afade=t=out:st=1:d=0.6'],
  creak: ['-f', 'lavfi', '-i', "aevalsrc='0.35*sgn(sin(2*PI*(90+40*sin(9*t))*t))*exp(-1.2*t)':d=1.4", '-af', 'bandpass=f=600:w=500'],
  steps: ['-f', 'lavfi', '-i', "aevalsrc='0.8*sin(2*PI*60*mod(t,0.55))*exp(-25*mod(t,0.55))':d=3.3", '-af', 'lowpass=f=400'],
  sting: ['-f', 'lavfi', '-i', "aevalsrc='0.3*(sin(2*PI*220*t)+sin(2*PI*233*t)+sin(2*PI*311*t))*exp(-1.1*t)*min(1,t*30)':d=3"],
  click: ['-f', 'lavfi', '-i', "aevalsrc='0.8*(random(0)*2-1)*exp(-200*t)':d=0.05"],
  glassShake: ['-f', 'lavfi', '-i', "aevalsrc='0.5*sin(2*PI*2600*t)*exp(-30*mod(t,0.12))*exp(-1.5*t)':d=1.5"],
  phone: ['-f', 'lavfi', '-i', "aevalsrc='0.3*(sin(2*PI*440*t)+sin(2*PI*480*t))*lt(mod(t,2),1)':d=2"],
  electric: ['-f', 'lavfi', '-i', "aevalsrc='0.12*sin(2*PI*60*t)+0.08*sin(2*PI*120*t)+0.04*sin(2*PI*180*t)':d=3"],
};
const BEDS = {
  drone: (d) => ['-f', 'lavfi', '-i', `aevalsrc='0.22*sin(2*PI*55*t)+0.16*sin(2*PI*58.3*t)+0.07*sin(2*PI*110*t)*(0.6+0.4*sin(2*PI*0.1*t))+0.05*sin(2*PI*164.8*t)*(0.5+0.5*sin(2*PI*0.07*t))':d=${d}`],
  wind: (d) => ['-f', 'lavfi', '-i', `anoisesrc=c=brown:d=${d}:a=0.5`, '-af', 'lowpass=f=420,tremolo=f=0.15:d=0.6'],
  rain: (d) => ['-f', 'lavfi', '-i', `anoisesrc=c=pink:d=${d}:a=0.35`, '-af', 'highpass=f=700,lowpass=f=7000'],
  underwater: (d) => ['-f', 'lavfi', '-i', `anoisesrc=c=brown:d=${d}:a=0.6`, '-af', 'lowpass=f=250,tremolo=f=0.3:d=0.5'],
  hum: (d) => ['-f', 'lavfi', '-i', `aevalsrc='0.1*sin(2*PI*120*t)+0.05*sin(2*PI*240*t)+0.18*sin(2*PI*55*t)':d=${d}`],
};
function lib(name) {
  const f = path.join(LIB, name + '.wav');
  if (!fs.existsSync(f)) ff([...DEF[name], '-ar', '48000', '-ac', '1', f]);
  return f;
}
// mix({narration, lead, total, bed, events:[{name,t,vol}], out})
function mix(o) {
  const D = o.total.toFixed(2);
  const bedFile = (name) => { const f = path.join(LIB, `bed_${name}_${D}.wav`); if (!fs.existsSync(f)) ff([...BEDS[name](D), '-ar', '48000', '-ac', '1', f]); return f; };
  const bedName = BEDS[o.bed] ? o.bed : 'drone';
  const args = ['-i', o.narration, '-i', bedFile(bedName), '-i', bedFile('drone')];
  const bedAf = '';
  const evs = o.events.filter(e => DEF[e.name] && e.t >= 0 && e.t < o.total);
  evs.forEach(e => args.push('-i', lib(e.name)));
  const L = Math.round(o.lead * 1000);
  const fc = [`[0:a]aresample=48000,aformat=channel_layouts=mono,volume=1.0,adelay=${L}|${L},apad,asplit=2[vo][vosc]`,
    `[1:a]${bedAf}aresample=48000,aformat=channel_layouts=mono,volume=${o.bed === 'drone' ? 0.0 : 0.22},afade=t=in:d=1.5,afade=t=out:st=${(o.total - 1.5).toFixed(2)}:d=1.5[bed]`,
    `[2:a]aresample=48000,aformat=channel_layouts=mono,volume=0.38,afade=t=in:d=2,afade=t=out:st=${(o.total - 1.5).toFixed(2)}:d=1.5[drone]`];
  evs.forEach((e, i) => { const d = Math.round(e.t * 1000); fc.push(`[${i + 3}:a]aresample=48000,aformat=channel_layouts=mono,volume=${(0.55 * e.vol).toFixed(2)},adelay=${d}|${d}[e${i}]`); });
  const ins = ['[vo]', '[bed]', '[drone]', ...evs.map((_, i) => `[e${i}]`)];
  // duck bed + sfx a little under the voice
  fc.push(`${ins.slice(1).join('')}amix=inputs=${ins.length - 1}:normalize=0[fx]`);
  fc.push(`[fx][vosc]sidechaincompress=threshold=0.05:ratio=4:attack=20:release=300[fxd]`);
  fc.push(`[fxd][vo]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[out]`);
  ff([...args, '-filter_complex', fc.join(';'), '-map', '[out]', '-t', D, '-ar', '48000', '-ac', '2', o.out]);
}
module.exports = { mix, lib, NAMES: Object.keys(DEF) };

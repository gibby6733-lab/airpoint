// Stage 2 of the pipeline: script.json -> per-line audio + mouth/caption timing.
// Writes public/audio/*, public/sfx/* and src/generated/timeline.json for Remotion.
//
// Voice engines:
//   - ElevenLabs (when ELEVENLABS_API_KEY is set and a cast member has elevenlabsVoiceId):
//     uses the /with-timestamps endpoint so mouths and captions follow real character timings.
//   - espeak-ng (free, offline placeholder): mouths follow the loudness of the audio,
//     caption words are spread across the line by length.
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const script = JSON.parse(fs.readFileSync(path.join(root, "script.json"), "utf8"));
const fps = script.settings?.fps ?? 24;
const gap = script.settings?.gapSeconds ?? 0.2;
const audioDir = path.join(root, "public", "audio");
const sfxDir = path.join(root, "public", "sfx");
const genDir = path.join(root, "src", "generated");
for (const d of [audioDir, sfxDir, genDir]) fs.mkdirSync(d, { recursive: true });

const ff = (...args) => execFileSync("ffmpeg", ["-loglevel", "error", "-y", ...args]);
const duration = (file) =>
  parseFloat(
    execFileSync("ffprobe", ["-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", file]).toString(),
  );

// --- Mouth shapes -----------------------------------------------------------
// Shapes the character rig understands: closed, O, open, wide (plus smile/angry for idle faces).
// Animated "on twos" (12 changes per second) for the choppy cutout look.
function mouthFromLoudness(file, frames) {
  const pcm = execFileSync("ffmpeg", ["-loglevel", "error", "-i", file, "-f", "s16le", "-ac", "1", "-ar", "12000", "-"]);
  const samples = new Int16Array(pcm.buffer, pcm.byteOffset, Math.floor(pcm.byteLength / 2));
  const per = 12000 / fps;
  const rms = [];
  for (let f = 0; f < frames; f++) {
    let sum = 0;
    let n = 0;
    for (let i = Math.floor(f * per); i < Math.min(samples.length, Math.floor((f + 2) * per)); i++) {
      sum += samples[i] * samples[i];
      n++;
    }
    rms.push(n ? Math.sqrt(sum / n) : 0);
  }
  const peak = Math.max(...rms, 1);
  const shapes = [];
  for (let f = 0; f < frames; f++) {
    const held = f - (f % 2); // hold each mouth for two frames
    const v = rms[held] / peak;
    let s = "closed";
    if (v > 0.62) s = "wide";
    else if (v > 0.36) s = held % 4 === 0 ? "open" : "O";
    else if (v > 0.14) s = held % 4 === 0 ? "O" : "open";
    shapes.push(s);
  }
  return shapes;
}

function mouthFromCharacters(alignment, frames) {
  const shapes = new Array(frames).fill("closed");
  const { characters, character_start_times_seconds: st, character_end_times_seconds: en } = alignment;
  for (let i = 0; i < characters.length; i++) {
    const c = characters[i].toLowerCase();
    let s = null;
    if ("ae".includes(c)) s = "wide";
    else if ("iy".includes(c)) s = "open";
    else if ("ouw".includes(c)) s = "O";
    else if ("mbp".includes(c)) s = "closed";
    else if (/[a-z]/.test(c)) s = "open";
    if (!s) continue;
    for (let f = Math.floor(st[i] * fps); f <= Math.min(frames - 1, Math.floor(en[i] * fps)); f++) shapes[f] = s;
  }
  // on twos
  return shapes.map((_, f) => shapes[f - (f % 2)]);
}

// Caption words: real timings from ElevenLabs, or spread by word length for espeak.
function wordsFromCharacters(alignment, captionWords) {
  const { characters, character_start_times_seconds: st, character_end_times_seconds: en } = alignment;
  const spoken = [];
  let cur = null;
  characters.forEach((c, i) => {
    if (/\s/.test(c)) {
      if (cur) spoken.push(cur);
      cur = null;
    } else {
      cur = cur ? { ...cur, end: en[i] } : { start: st[i], end: en[i] };
    }
  });
  if (cur) spoken.push(cur);
  return spreadWords(captionWords, spoken[0]?.start ?? 0, spoken.at(-1)?.end ?? 1);
}

function spreadWords(words, start, end) {
  const weights = words.map((w) => w.replace(/[^a-z0-9]/gi, "").length + 2);
  const total = weights.reduce((a, b) => a + b, 0);
  let t = start;
  return words.map((w, i) => {
    const d = ((end - start) * weights[i]) / total;
    const item = { word: w, start: t, end: t + d };
    t += d;
    return item;
  });
}

// --- Voice engines ----------------------------------------------------------
async function elevenlabs(text, voiceId, outBase) {
  const res = await fetch(`https://api.elevenlabs.io/v1/text-to-speech/${voiceId}/with-timestamps`, {
    method: "POST",
    headers: { "xi-api-key": process.env.ELEVENLABS_API_KEY, "Content-Type": "application/json" },
    body: JSON.stringify({ text, model_id: process.env.ELEVENLABS_MODEL ?? "eleven_multilingual_v2" }),
  });
  if (!res.ok) throw new Error(`ElevenLabs ${res.status}: ${await res.text()}`);
  const json = await res.json();
  const file = `${outBase}.mp3`;
  fs.writeFileSync(file, Buffer.from(json.audio_base64, "base64"));
  return { file, alignment: json.alignment };
}

function espeak(text, voice, outBase) {
  const raw = `${outBase}.raw.wav`;
  const file = `${outBase}.wav`;
  execFileSync("espeak-ng", ["-v", voice.espeak, "-p", String(voice.pitch), "-s", String(voice.speed), "-g", "1", "-w", raw, text]);
  // Trim silence, then speed/pitch up for a cartoon-kid voice.
  const trim = "silenceremove=start_periods=1:start_threshold=-45dB";
  ff("-i", raw, "-af", `${trim},areverse,${trim},areverse,asetrate=22050*${voice.shift},aresample=44100`, file);
  fs.rmSync(raw);
  return { file, alignment: null };
}

// --- Sound effects (synthesized, no downloads) -------------------------------
function makeSfx(total) {
  const out = (n) => path.join(sfxDir, n);
  ff("-f", "lavfi", "-i",
    "aevalsrc='0.7*sin(2*PI*(110-60*t)*t)*(0.55+0.45*sin(2*PI*31*t))*min(1,8*t)*exp(-1.2*t)':s=44100:d=0.9",
    "-af", "lowpass=f=900,volume=1.6", out("burp.wav"));
  ff("-f", "lavfi", "-i", "aevalsrc='(0.35*sin(2*PI*52*t)+0.25*sin(2*PI*104*t+2*sin(2*PI*4*t)))*min(1,2*t)':s=44100:d=1.3",
    "-f", "lavfi", "-i", "anoisesrc=color=white:amplitude=0.25:d=0.6:r=44100",
    "-filter_complex", "[1]highpass=f=2500,afade=t=in:d=0.05,afade=t=out:st=0.3:d=0.3,adelay=900|900[h];[0][h]amix=inputs=2:normalize=0,lowpass=f=4000",
    out("bus.wav"));
  ff("-f", "lavfi", "-i", `anoisesrc=color=white:amplitude=0.5:d=${total.toFixed(2)}:r=44100`,
    "-af", "bandpass=f=5200:width_type=h:w=900,tremolo=f=38:d=0.9,volume=0.18,afade=t=in:d=0.5", out("ambience.wav"));
  ff("-f", "lavfi", "-i",
    "aevalsrc='0.4*(sin(2*PI*523*t)*exp(-6*t)+sin(2*PI*659*max(0,t-0.12))*exp(-6*max(0,t-0.12))*gt(t,0.12)+sin(2*PI*784*max(0,t-0.24))*exp(-4*max(0,t-0.24))*gt(t,0.24))':s=44100:d=1.1",
    out("sting.wav"));
}

// --- Build the timeline -----------------------------------------------------
const useEleven = Boolean(process.env.ELEVENLABS_API_KEY) && script.settings?.voiceEngine !== "espeak";
const beats = [];
let cursor = 0;
for (const [i, beat] of script.beats.entries()) {
  const start = Math.round(cursor * fps);
  if (beat.type === "line") {
    const cast = script.cast[beat.speaker];
    const base = path.join(audioDir, `line-${i}-${beat.speaker}`);
    const voiceId = cast.elevenlabsVoiceId;
    const { file, alignment } =
      useEleven && voiceId ? await elevenlabs(beat.text, voiceId, base) : espeak(beat.text, cast.voice, base);
    const secs = duration(file);
    const frames = Math.ceil(secs * fps);
    const captionWords = (beat.caption ?? beat.text).split(/\s+/).filter(Boolean);
    const words = (alignment ? wordsFromCharacters(alignment, captionWords) : spreadWords(captionWords, 0, secs)).map(
      (w) => ({ word: w.word, start: start + Math.round(w.start * fps), end: start + Math.round(w.end * fps) }),
    );
    const mouth = alignment ? mouthFromCharacters(alignment, frames) : mouthFromLoudness(file, frames);
    beats.push({ ...beat, index: i, start, end: start + frames, audio: `audio/${path.basename(file)}`, mouth, words });
    cursor += secs + gap;
    console.log(`line ${i} ${beat.speaker.padEnd(6)} ${secs.toFixed(2)}s  ${alignment ? "elevenlabs" : "espeak"}`);
  } else {
    const secs = beat.seconds ?? 1;
    beats.push({ ...beat, index: i, start, end: start + Math.round(secs * fps) });
    cursor += secs + (beat.type === "title" ? 0 : gap);
  }
}
const durationInFrames = Math.round(cursor * fps);
makeSfx(cursor);
const sfx = [
  ...beats.filter((b) => b.action === "gator-burp").map((b) => ({ src: "sfx/burp.wav", start: b.start })),
  ...beats.filter((b) => b.action === "bus-arrives").map((b) => ({ src: "sfx/bus.wav", start: b.start })),
  ...beats.filter((b) => b.type === "title").map((b) => ({ src: "sfx/sting.wav", start: b.start })),
];
const timeline = { title: script.title, episode: script.episode, fps, durationInFrames, cast: script.cast, beats, sfx, ambience: "sfx/ambience.wav" };
fs.writeFileSync(path.join(genDir, "timeline.json"), JSON.stringify(timeline, null, 1));
console.log(`timeline: ${(durationInFrames / fps).toFixed(2)}s, ${durationInFrames} frames`);

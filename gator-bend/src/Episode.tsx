import React from "react";
import {
  AbsoluteFill,
  Audio,
  Easing,
  Sequence,
  continueRender,
  delayRender,
  interpolate,
  staticFile,
  useCurrentFrame,
} from "remotion";
import timeline from "./generated/timeline.json";
import { Expression, Kid, MouthShape, Pose } from "./characters";
import { PaperDefs, paper } from "./paper";
import { BUS_W, Background, Bus, FEET_Y, FONT, GATOR_X, Gator, Heat, PondFront, Sun, WORLD_H, WORLD_W } from "./World";

// ---------------------------------------------------------------- types
type Word = { word: string; start: number; end: number };
type Beat = {
  index: number;
  type: "line" | "action" | "title";
  action?: string;
  who?: string;
  speaker?: string;
  expression?: string;
  pose?: string;
  camera?: string;
  look?: string;
  reactions?: Record<string, string>;
  emphasisPose?: string;
  sweat?: string[];
  start: number;
  end: number;
  audio?: string;
  mouth?: string[];
  words?: Word[];
};
type CastMember = { x: number; idlePose: string; idleExpression: string };
const T = timeline as unknown as {
  fps: number;
  durationInFrames: number;
  title: string;
  episode: string;
  cast: Record<string, CastMember>;
  beats: Beat[];
  sfx: { src: string; start: number; volume?: number }[];
  ambience: string;
};
const CAST = Object.keys(T.cast);
const ASPECT = 1920 / 1080;

// Load the caption/sign font before any frame is captured.
const fontHandle = delayRender("font");
const font = new FontFace("GBInter", `url(${staticFile("fonts/Inter-Black.otf")})`, { weight: "900" });
font.load().then(
  (f) => {
    document.fonts.add(f);
    continueRender(fontHandle);
  },
  () => continueRender(fontHandle),
);

// ---------------------------------------------------------------- helpers
// Characters and props move "on twos": one new pose every 2 frames, no in-betweens.
const onTwos = (f: number) => f - (f % 2);
const beatAt = (f: number) => T.beats.find((b) => f >= b.start && f < b.end) ?? T.beats[T.beats.length - 1];

const homeX = (name: string, f: number) => {
  const home = T.cast[name].x;
  const walk = T.beats.find((b) => b.action === "walk-in" && b.who === name);
  if (!walk) return { x: home, walking: false };
  if (f < walk.start) return { x: -400, walking: false };
  if (f >= walk.end) return { x: home, walking: false };
  const sf = onTwos(f);
  return { x: interpolate(sf, [walk.start, walk.end - 2], [home - 520, home], { extrapolateRight: "clamp" }), walking: true };
};

const gatorState = (f: number) => {
  const burp = T.beats.find((b) => b.action === "gator-burp");
  if (burp && f >= burp.start && f < burp.end) {
    const t = (f - burp.start) / (burp.end - burp.start);
    return { jaw: onTwos(f - burp.start) < 4 ? 20 : 38, burp: t };
  }
  // idle chomping on the pool noodle, stepped
  const c = Math.floor(f / 4) % 6;
  return { jaw: c === 1 ? 14 : c === 2 ? 8 : 0, burp: 0 };
};

const busX = (f: number) => {
  const b = T.beats.find((x) => x.action === "bus-arrives");
  if (!b || f < b.start) return null;
  const sf = onTwos(f);
  return interpolate(sf, [b.start, b.end - 4], [WORLD_W + 40, 230], {
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
};

// ---------------------------------------------------------------- camera
type View = { x: number; y: number; w: number; h: number };
const clampView = (cx: number, top: number, w: number): View => {
  const h = w * ASPECT;
  return {
    x: Math.min(Math.max(cx - w / 2, 0), WORLD_W - w),
    y: Math.min(Math.max(top, 0), WORLD_H - h),
    w,
    h,
  };
};
// Kids stand low in the frame (feet at 70% down) so the town fills the space above them
// and the captions sit on the street just below their feet.
const FEET_AT = 0.7;
const targetX = (name: string, f: number) => (name === "gator" ? GATOR_X - 60 : homeX(name, f).x);

const cameraFor = (beat: Beat, f: number): View => {
  const spec = beat.camera ?? "wide";
  const [kind, arg = ""] = spec.split(":");
  const names = arg.split(",").filter(Boolean);
  if (kind === "two") {
    const xs = names.map((n) => (n === "gator" ? GATOR_X : T.cast[n].x));
    const w = Math.max(1000, Math.max(...xs) - Math.min(...xs) + 560);
    return clampView((Math.max(...xs) + Math.min(...xs)) / 2, FEET_Y - FEET_AT * w * ASPECT, w);
  }
  if (kind === "close" && names[0] === "gator") {
    const w = 1000;
    return clampView(GATOR_X - 80, 2330 - 0.42 * w * ASPECT, w);
  }
  if (kind === "close") {
    const w = 680;
    return clampView(targetX(names[0], f), FEET_Y - FEET_AT * w * ASPECT, w);
  }
  if (kind === "push") {
    // slow dramatic push-in across the line
    const w = interpolate(f, [beat.start, beat.end], [860, 600], {
      easing: Easing.inOut(Easing.quad),
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });
    return clampView(targetX(names[0], f), FEET_Y - FEET_AT * w * ASPECT, w);
  }
  // wide: the establishing shot creeps in slightly over the beat
  const w = interpolate(f, [beat.start, beat.end], [WORLD_W, WORLD_W * 0.94], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return clampView(WORLD_W / 2, FEET_Y - 0.62 * w * ASPECT, w);
};

// ---------------------------------------------------------------- per-character state
const isEmphasis = (w: string) => /!$/.test(w) || (/[A-Z]{2,}/.test(w) && w === w.toUpperCase());

const kidState = (name: string, f: number) => {
  const beat = beatAt(f);
  const me = T.cast[name];
  const { x, walking } = homeX(name, f);
  const speaking = beat.type === "line" && beat.speaker === name;
  const local = f - beat.start;
  let mouth: MouthShape | null = null;
  if (speaking && beat.mouth) mouth = (beat.mouth[local] ?? "closed") as MouthShape;
  const expression = (speaking ? beat.expression : beat.reactions?.[name]) ?? me.idleExpression;
  let pose = (speaking ? beat.pose : undefined) ?? me.idlePose;
  if (!speaking && expression === "scared") pose = "arms-up";

  // which word is being said right now (drives head tilts and emphasis)
  const words = speaking ? beat.words ?? [] : [];
  const wi = words.findIndex((w) => f >= w.start && f < w.end);
  const emph = words.find((w) => isEmphasis(w.word));

  // eyes + head turn: toward whoever is talking, or whatever the beat says to look at
  const lookAt = beat.look;
  const target =
    lookAt === "gator"
      ? GATOR_X
      : lookAt === "bus"
        ? (busX(f) ?? WORLD_W) + BUS_W / 3
        : lookAt && T.cast[lookAt] && lookAt !== name
          ? homeX(lookAt, f).x
          : beat.speaker && !speaking
            ? T.cast[beat.speaker].x
            : null;
  let look = 0;
  if (target !== null && !(speaking && !lookAt)) look = Math.max(-1, Math.min(1, (target - x) / 260));
  const turn = look * 0.85;

  // blinks: a 2-frame lid swap on a per-character rhythm
  const idx = CAST.indexOf(name);
  const period = 58 + idx * 17;
  const blink = (f + idx * 23) % period < 3;

  // motion, all in held steps
  let dy = 0;
  let tilt = 0;
  let headTilt = 0;
  let step: number | null = null;
  if (walking) {
    // walk cycle on 3-frame holds: body tilts side to side and bobs, one foot lifts, arms swing
    step = Math.floor(f / 3) % 2;
    dy = step ? -14 : -4;
    tilt = step ? 4 : -4;
    headTilt = step ? -2 : 2;
  } else if (speaking) {
    if (wi >= 0) {
      headTilt = wi % 2 ? 3 : -3; // head rocks on each new word
      if (f - words[wi].start < 2) dy = -7; // little lift on each word
    }
    if (emph && f >= emph.start) {
      pose = (beat.emphasisPose ?? "point") as typeof pose;
      if (f - emph.start < 4) dy = -26; // hop on the punch word
      headTilt *= 2;
    }
  } else if (expression === "scared") {
    dy = local < 4 ? -30 : Math.floor(f / 2) % 2 ? -6 : 0; // jump, then shake
  }
  const sweat = beat.sweat?.includes(name) ? local : null;
  return { x, dy, tilt, headTilt, mouth, expression: expression as Expression, pose: pose as Pose, look, turn, blink, sweat, step };
};

// ---------------------------------------------------------------- captions
const Captions: React.FC<{ f: number }> = ({ f }) => {
  const beat = beatAt(f);
  if (beat.type !== "line" || !beat.words) return null;
  const words = beat.words;
  // the most recent word that has started (holds through pauses between words)
  let cur = 0;
  words.forEach((w, i) => {
    if (f >= w.start) cur = i;
  });
  const groupStart = cur - (cur % 3);
  const group = words.slice(groupStart, groupStart + 3);
  return (
    <div
      style={{
        position: "absolute",
        top: 1420,
        left: 60,
        right: 60,
        textAlign: "center",
        fontFamily: FONT,
        fontWeight: 900,
        fontSize: 98,
        lineHeight: 1.08,
        textTransform: "uppercase",
        letterSpacing: -1,
      }}
    >
      {group.map((w, i) => {
        const active = groupStart + i === cur;
        const pop = active && f - w.start < 2 ? 1.18 : 1;
        return (
          <span
            key={groupStart + i}
            style={{
              display: "inline-block",
              margin: "0 24px",
              color: active ? "#FFD23F" : "#FFFFFF",
              WebkitTextStroke: "16px #120a04",
              paintOrder: "stroke fill",
              transform: `scale(${pop}) rotate(${active ? -2 : 0}deg)`,
              textShadow: "0 8px 0 rgba(0,0,0,0.35)",
            }}
          >
            {w.word}
          </span>
        );
      })}
    </div>
  );
};

// ---------------------------------------------------------------- title card
const TitleCard: React.FC<{ f: number; beat: Beat }> = ({ f, beat }) => {
  const local = onTwos(f - beat.start);
  const letters = T.title.split("");
  return (
    <AbsoluteFill>
      <svg width={1080} height={1920} viewBox="0 0 1080 1920">
        <rect x={0} y={0} width={1080} height={1920} fill="#1E8F8A" filter={paper(0, 1)} />
        <g filter={paper(2, 2)}>
          <rect x={90} y={640} width={900} height={560} rx={30} fill="#F4EBD0" stroke="#1d140e" strokeWidth={8} />
          <path d="M 150 1120 Q 540 1060 930 1120" stroke="#79B84A" strokeWidth={26} fill="none" strokeLinecap="round" />
        </g>
        <g filter={paper(3, 0)}>
          {letters.map((ch, i) => {
            // two letters slap down per held pose
            const at = i * 1;
            if (local < at || ch === " ") return null;
            const row = i < 6 ? 0 : 1;
            const col = row === 0 ? i : i - 6;
            const count = row === 0 ? 5 : letters.length - 6;
            const x = 540 + (col - (count - 1) / 2) * 160;
            const y = row === 0 ? 880 : 1080;
            const pop = local - at < 2 ? 1.25 : 1;
            return (
              <g key={i} transform={`translate(${x} ${y}) rotate(${i % 2 ? 4 : -4}) scale(${pop})`}>
                <text
                  x={0}
                  y={0}
                  textAnchor="middle"
                  fontFamily={FONT}
                  fontWeight={900}
                  fontSize={190}
                  fill={row === 0 ? "#F08A24" : "#D9443A"}
                  stroke="#1d140e"
                  strokeWidth={8}
                  paintOrder="stroke"
                >
                  {ch}
                </text>
              </g>
            );
          })}
        </g>
        <text x={540} y={1300} textAnchor="middle" fontFamily={FONT} fontWeight={900} fontSize={54} fill="#FFFDF2">
          {T.episode}
        </text>
      </svg>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- the episode
export const Episode: React.FC = () => {
  const f = useCurrentFrame();
  const beat = beatAt(f);
  let view = cameraFor(beat, f);
  if (beat.action === "gator-burp") {
    // camera shake on the burp
    const k = Math.floor(f / 2);
    view = { ...view, x: view.x + ((k % 3) - 1) * 14, y: view.y + ((k % 2) * 2 - 1) * 10 };
  }
  const g = gatorState(f);
  const bx = busX(f);
  const kids = CAST.map((name) => ({ name, ...kidState(name, f) }));
  return (
    <AbsoluteFill style={{ backgroundColor: "#8FD3EE" }}>
      <PaperDefs />
      <svg width={1080} height={1920} viewBox={`${view.x} ${view.y} ${view.w} ${view.h}`}>
        <Background />
        <Sun frame={f} />
        <Heat frame={f} />
        <Gator jaw={g.jaw} burp={g.burp} frame={f} />
        <PondFront frame={f} />
        {kids.map((k) => (
          <g
            key={k.name}
            filter={paper(2, CAST.indexOf(k.name))}
            transform={`translate(${k.x} ${FEET_Y + k.dy}) rotate(${k.tilt})`}
          >
            <Kid
              name={k.name}
              pose={k.pose}
              expression={k.expression}
              mouth={k.mouth}
              lookX={k.look}
              turn={k.turn}
              headTilt={k.headTilt}
              sweat={k.sweat}
              step={k.step}
              blink={k.blink}
            />
          </g>
        ))}
        {bx !== null ? <Bus x={bx} bounce={Math.floor(f / 3) % 2 ? -6 : 0} /> : null}
      </svg>
      {/* overhead studio lamp: warm hot-spot, falloff toward the corners */}
      <AbsoluteFill
        style={{
          background: "radial-gradient(ellipse 85% 60% at 50% 40%, rgba(255,236,200,0) 0%, rgba(255,214,160,0.08) 55%, rgba(60,30,5,0.42) 100%)",
          mixBlendMode: "multiply",
        }}
      />
      <AbsoluteFill style={{ background: "rgba(255,190,110,0.07)", mixBlendMode: "soft-light" }} />
      <Captions f={f} />
      {beat.type === "title" ? <TitleCard f={f} beat={beat} /> : null}

      {/* audio: dialogue first, everything is timed to it */}
      <Audio src={staticFile(T.ambience)} volume={0.35} />
      {T.beats
        .filter((b) => b.audio)
        .map((b) => (
          <Sequence key={b.index} from={b.start}>
            <Audio src={staticFile(b.audio!)} />
          </Sequence>
        ))}
      {T.sfx.map((s, i) => (
        <Sequence key={`sfx-${i}`} from={s.start}>
          <Audio src={staticFile(s.src)} volume={s.volume ?? 0.9} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};

export const DURATION = T.durationInFrames;
export const FPS = T.fps;

// Opening titles, the same at the start of every episode (7.5s).
// Each kid slaps onto their own paper card with a name + tagline, then the whole
// gang hops into a line-up under the GATOR BEND logo and everyone looks at Wade.
// Cue points match the jingle in scripts/make-music.py.
import React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame } from "remotion";
import { Expression, Kid, Pose } from "./characters";
import { INTRO_DATA } from "./Episode";
import { INK, PaperDefs, paper } from "./paper";
import { FONT } from "./World";

export const INTRO_FRAMES = 180;
const CARD_STARTS = [6, 36, 66, 96];
const CARD_LEN = 30;
const LOGO_START = 126;

const onTwos = (f: number) => f - (f % 2);

const CARD_ACT: Record<string, { pose: Pose; expression: Expression }> = {
  danny: { pose: "idle", expression: "neutral" },
  tucker: { pose: "arms-up", expression: "worried" },
  bray: { pose: "point", expression: "excited" },
  wade: { pose: "idle", expression: "deadpan" },
};

// Slap-in offsets on held poses: from below, overshoot, settle.
const slap = (local: number) => (local < 2 ? 700 : local < 4 ? -60 : local < 6 ? 20 : 0);
// Matching squash & stretch: stretched while flying up, squashed on the landing.
const slapScale = (local: number) => (local < 4 ? "scale(0.92 1.1)" : local < 6 ? "scale(1.1 0.9)" : "");

const Card: React.FC<{ local: number; who: string; name: string; tag: string; color: string }> = ({ local, who, name, tag, color }) => {
  const l = onTwos(local);
  const act = CARD_ACT[who] ?? CARD_ACT.danny;
  const nameIn = l >= 4;
  const tagIn = l >= 8;
  return (
    <svg width={1080} height={1920} viewBox="0 0 1080 1920">
      <g filter={paper(0, 1)}>
        <rect width={1080} height={1920} fill={color} />
        {Array.from({ length: 9 }, (_, i) => (
          <path key={i} d={`M ${-400 + i * 260} 1920 L ${i * 260 + 200} 0 L ${i * 260 + 300} 0 L ${-300 + i * 260} 1920 Z`} fill="#fff" opacity={0.07} />
        ))}
      </g>
      {/* sidewalk strip the kid lands on */}
      <rect x={0} y={1480} width={1080} height={440} fill="#D2CFC6" filter={paper(1, 2)} />
      <g filter={paper(3, 0)} transform={`translate(540 ${1520 + slap(l)}) scale(1.9) ${slapScale(l)}`}>
        <Kid name={who} pose={act.pose} expression={act.expression} mouth={null} lookX={0} blink={l >= 18 && l < 20} />
      </g>
      {nameIn ? (
        <g filter={paper(3, 1)} transform={`translate(540 330) rotate(-4) scale(${l < 6 ? 1.25 : 1})`}>
          <rect x={-440} y={-150} width={880} height={210} rx={24} fill="#FFFDF2" stroke={INK} strokeWidth={8} />
          <text x={0} y={20} textAnchor="middle" fontFamily={FONT} fontWeight={900} fontSize={170} fill={color} stroke={INK} strokeWidth={7} paintOrder="stroke">
            {name}
          </text>
        </g>
      ) : null}
      {tagIn ? (
        <g filter={paper(2, 2)} transform="translate(540 500) rotate(2)">
          <rect x={-470} y={-50} width={940} height={96} rx={14} fill={INK} />
          <text x={0} y={18} textAnchor="middle" fontFamily={FONT} fontWeight={900} fontSize={tag.length > 24 ? 44 : 56} fill="#FFFDF2">
            {tag}
          </text>
        </g>
      ) : null}
    </svg>
  );
};

const LineUp: React.FC<{ local: number; cards: { who: string }[]; tagline: string }> = ({ local, cards, tagline }) => {
  const l = onTwos(local);
  const letters = "GATOR BEND".split("");
  const atWade = l >= 34; // the gang slowly turns to stare at Wade
  return (
    <svg width={1080} height={1920} viewBox="0 0 1080 1920">
      <rect width={1080} height={1920} fill="#8FD3EE" filter={paper(0, 0)} />
      {/* sun burst behind the logo, ticking round */}
      <g transform={`translate(540 760) rotate(${Math.floor(local / 4) * 6})`} filter={paper(1, 0)}>
        {Array.from({ length: 16 }, (_, i) => (
          <path key={i} transform={`rotate(${i * 22.5})`} d="M -60 -120 L 60 -120 L 0 -900 Z" fill="#FFE38A" />
        ))}
        <circle r={150} fill="#FFD23F" />
      </g>
      <rect x={0} y={1440} width={1080} height={480} fill="#79B84A" filter={paper(0, 2)} />
      <rect x={0} y={1500} width={1080} height={160} fill="#D2CFC6" filter={paper(1, 1)} />
      {cards.map((c, i) => {
        const x = 160 + i * 253;
        const appear = l - i * 2;
        if (appear < 0) return null;
        const act = CARD_ACT[c.who] ?? CARD_ACT.danny;
        const wadeX = 160 + 3 * 253;
        const look = atWade && c.who !== "wade" ? Math.max(-1, Math.min(1, (wadeX - x) / 200)) : 0;
        return (
          <g key={c.who} filter={paper(2, i % 3)} transform={`translate(${x} ${1640 + slap(appear) * 0.6}) scale(0.64) ${slapScale(appear)}`}>
            <Kid
              name={c.who}
              pose={c.who === "wade" ? "idle" : act.pose}
              expression={atWade && c.who !== "wade" ? "worried" : act.expression}
              mouth={null}
              lookX={look}
              turn={look * 0.85}
              blink={(l + i * 7) % 40 < 2}
            />
          </g>
        );
      })}
      <g filter={paper(3, 0)}>
        {letters.map((ch, i) => {
          const at = 6 + i;
          if (l < at || ch === " ") return null;
          const row = i < 6 ? 0 : 1;
          const col = row === 0 ? i : i - 6;
          const count = row === 0 ? 5 : 4;
          const x = 540 + (col - (count - 1) / 2) * 170;
          const y = row === 0 ? 700 : 920;
          const pop = l - at < 2 ? 1.3 : 1;
          return (
            <g key={i} transform={`translate(${x} ${y}) rotate(${i % 2 ? 5 : -5}) scale(${pop})`}>
              <text textAnchor="middle" fontFamily={FONT} fontWeight={900} fontSize={210} fill={row === 0 ? "#F08A24" : "#D9443A"} stroke={INK} strokeWidth={10} paintOrder="stroke">
                {ch}
              </text>
            </g>
          );
        })}
      </g>
      {l >= 22 ? (
        <g filter={paper(2, 1)} transform="translate(540 1060) rotate(-2)">
          <rect x={-300} y={-48} width={600} height={92} rx={14} fill="#FFFDF2" stroke={INK} strokeWidth={6} />
          <text y={18} textAnchor="middle" fontFamily={FONT} fontWeight={900} fontSize={54} fill="#1E8F8A">
            {tagline}
          </text>
        </g>
      ) : null}
    </svg>
  );
};

export const Intro: React.FC = () => {
  const f = useCurrentFrame();
  const data = INTRO_DATA;
  if (!data) return null;
  const cardIdx = CARD_STARTS.findIndex((s) => f >= s && f < s + CARD_LEN);
  return (
    <AbsoluteFill style={{ backgroundColor: "#1E8F8A" }}>
      <PaperDefs frame={f} />
      {f < CARD_STARTS[0] ? (
        <AbsoluteFill style={{ backgroundColor: "#1E8F8A" }} />
      ) : cardIdx >= 0 ? (
        <Card local={f - CARD_STARTS[cardIdx]} {...data.cards[cardIdx]} />
      ) : f >= LOGO_START ? (
        <LineUp local={f - LOGO_START} cards={data.cards} tagline={data.tagline} />
      ) : null}
      {/* same studio lamp as the episode */}
      <AbsoluteFill
        style={{
          background: "radial-gradient(ellipse 85% 60% at 50% 40%, rgba(255,236,200,0) 0%, rgba(255,214,160,0.08) 55%, rgba(60,30,5,0.42) 100%)",
          mixBlendMode: "multiply",
        }}
      />
      <Audio src={staticFile(data.music)} volume={0.85} />
      {data.shout ? (
        <Sequence from={LOGO_START + 8}>
          <Audio src={staticFile(data.shout.audio)} />
        </Sequence>
      ) : null}
    </AbsoluteFill>
  );
};

// The reusable character kit. Classic cutout-kid proportions: a huge round head
// sitting straight on a short bell-shaped body, stub arms with mitten hands, and
// only the feet peeking out. Every kid is the same modular rig (head, body, arm
// poses, eye directions, blinks, brows, 9 mouth shapes) with their own colors,
// hair and accessories. Feet are at (0, 0); the head is centered at (0, HEAD_Y).
import React from "react";
import { INK } from "./paper";

export type Pose = "idle" | "arms-up" | "phone" | "point";
export type Expression = "neutral" | "worried" | "smug" | "deadpan" | "excited" | "annoyed" | "scared";
export type MouthShape = "closed" | "O" | "open" | "wide" | "E" | "F" | "smile" | "angry" | "frown" | "smirk" | "flat";

export const HEAD_Y = -345;
const HRX = 168;
const HRY = 146;
const EYE_Y = -388;
const MY = -282; // mouth center
const LINE = { stroke: INK, strokeWidth: 4, strokeLinejoin: "round" as const };

export type Design = {
  skin: string;
  shirt: string;
  pants: string;
  shoes: string;
  hair: React.ReactNode; // drawn over the head, under the eyes
  face?: React.ReactNode; // cheeks, zinc, glasses (over the eyes)
  chest?: React.ReactNode;
  shirtPattern?: React.ReactNode; // clipped to the body
  seam?: boolean; // zipper line down the jacket
  sleeves?: boolean; // arms in shirt color instead of skin
  floaties?: boolean;
};

const BODY = "M -100 -252 Q -114 -252 -116 -238 L -130 -80 Q -132 -60 -112 -60 L 112 -60 Q 132 -60 130 -80 L 116 -238 Q 114 -252 100 -252 Z";

export const DESIGNS: Record<string, Design> = {
  danny: {
    skin: "#C68A62",
    shirt: "#1FA2A0",
    pants: "#C9AE7C",
    shoes: "#E85A3C",
    shirtPattern: (
      <g transform="translate(46 -150)">
        {Array.from({ length: 8 }, (_, i) => (
          <path key={i} transform={`rotate(${i * 45})`} d="M -5 -26 L 5 -26 L 0 -38 Z" fill="#FFD23F" />
        ))}
        <circle r={20} fill="#FFD23F" />
        <path d="M -9 4 Q 0 12 9 4" stroke="#C9741A" strokeWidth={3} fill="none" />
      </g>
    ),
    hair: (
      <path
        d="M -170 -340 C -184 -540, 184 -540, 170 -340 L 146 -392 L 110 -370 L 74 -410 L 36 -380 L 0 -414 L -36 -380 L -74 -410 L -110 -370 L -146 -392 Z"
        fill="#2a2320"
        {...LINE}
      />
    ),
  },
  tucker: {
    skin: "#F7D5BE",
    shirt: "#F08A24",
    pants: "#3C5AAA",
    shoes: "#F4F4F0",
    sleeves: true,
    shirtPattern: (
      <g fill="#C9661A" opacity={0.55}>
        <ellipse cx={-104} cy={-196} rx={30} ry={38} />
        <ellipse cx={104} cy={-196} rx={30} ry={38} />
        <ellipse cx={0} cy={-150} rx={26} ry={18} />
      </g>
    ),
    hair: (
      <g>
        <path d="M -132 -452 C -128 -575, 128 -575, 132 -452 Z" fill="#CDB98A" {...LINE} />
        <path d="M -133 -478 L 133 -478 L 132 -454 L -132 -454 Z" fill="#8C7A4E" />
        <ellipse cx={0} cy={-450} rx={205} ry={30} fill="#CDB98A" {...LINE} />
      </g>
    ),
    face: (
      <g>
        <circle cx={-104} cy={-300} r={22} fill="#F09A9A" />
        <circle cx={104} cy={-300} r={22} fill="#F09A9A" />
        <ellipse cx={0} cy={-322} rx={18} ry={9} fill="#FFFFFF" {...LINE} strokeWidth={3} />
      </g>
    ),
  },
  bray: {
    skin: "#EFC6A0",
    shirt: "#8240B0",
    pants: "#D23C3C",
    shoes: "#262626",
    hair: (
      <g>
        <path
          d="M -164 -390 L -184 -500 L -122 -472 L -106 -566 L -50 -508 L 0 -594 L 50 -508 L 106 -566 L 122 -472 L 184 -500 L 164 -390 C 110 -470, -110 -470, -164 -390 Z"
          fill="#F2D04A"
          {...LINE}
        />
        {/* wraparound sunglasses pushed up on the forehead */}
        <path d="M -150 -470 Q 0 -506 150 -470 L 144 -440 Q 72 -428 8 -448 Q -72 -428 -144 -440 Z" fill="#161616" {...LINE} />
        <path d="M -112 -466 Q -64 -480 -22 -474" stroke="#9fe7ff" strokeWidth={6} fill="none" />
      </g>
    ),
    chest: (
      <g>
        <path d="M -58 -228 Q 0 -168 58 -228" stroke="#6B4A2B" strokeWidth={6} fill="none" />
        <path d="M -13 -196 L 13 -196 L 0 -158 Z" fill="#FFFDF2" {...LINE} strokeWidth={3} />
      </g>
    ),
  },
  wade: {
    skin: "#F5D4B6",
    shirt: "#4E9A4A",
    pants: "#7A5A3A",
    shoes: "#3B6FD0",
    sleeves: true,
    floaties: true,
    hair: (
      <path
        d="M -166 -372 L -190 -432 L -152 -456 L -172 -516 L -108 -506 L -96 -568 L -44 -526 L 0 -580 L 44 -526 L 96 -564 L 108 -500 L 172 -516 L 152 -456 L 190 -424 L 166 -372 C 110 -456, -110 -456, -166 -372 Z"
        fill="#E06A28"
        {...LINE}
      />
    ),
    shirtPattern: (
      <g fill="#357A33">
        <rect x={-140} y={-200} width={280} height={24} />
        <rect x={-140} y={-150} width={280} height={24} />
        <rect x={-140} y={-100} width={280} height={24} />
      </g>
    ),
  },
};

type Pt = [number, number];
const SH: Pt[] = [
  [-102, -212],
  [102, -212],
];
const ARMS: Record<Pose, { l: Pt[]; r: Pt[] }> = {
  idle: { l: [SH[0], [-126, -146]], r: [SH[1], [126, -146]] },
  "arms-up": { l: [SH[0], [-150, -250], [-166, -306]], r: [SH[1], [150, -250], [166, -306]] },
  phone: { l: [SH[0], [-126, -146]], r: [SH[1], [124, -168], [66, -170]] },
  point: { l: [SH[0], [-126, -146]], r: [SH[1], [164, -250], [196, -292]] },
};

const Arm: React.FC<{ pts: Pt[]; color: string; skin: string; floatie?: boolean; swing?: number }> = ({
  pts,
  color,
  skin,
  floatie,
  swing = 0,
}) => {
  const p = pts.map((q, i) => (i === pts.length - 1 ? ([q[0] + swing, q[1]] as Pt) : q));
  const d = "M " + p.map((q) => q.join(" ")).join(" L ");
  const hand = p[p.length - 1];
  const prev = p[p.length - 2];
  const side = hand[0] > 0 ? 1 : -1;
  const ang = (Math.atan2(hand[1] - prev[1], hand[0] - prev[0]) * 180) / Math.PI - 90;
  const fl: Pt = [p[0][0] + (p[1][0] - p[0][0]) * 0.3, p[0][1] + (p[1][1] - p[0][1]) * 0.3];
  return (
    <g>
      {/* chunky sleeve: outline pass, then fill */}
      <path d={d} stroke={INK} strokeWidth={54} strokeLinecap="round" strokeLinejoin="round" fill="none" />
      <path d={d} stroke={color} strokeWidth={46} strokeLinecap="round" strokeLinejoin="round" fill="none" />
      {floatie ? (
        <g>
          <ellipse cx={fl[0]} cy={fl[1]} rx={38} ry={30} fill="#FF8A1F" {...LINE} />
          <path d={`M ${fl[0] - 36} ${fl[1] - 2} L ${fl[0] + 36} ${fl[1] - 2}`} stroke="#FFF1D6" strokeWidth={8} />
        </g>
      ) : null}
      {/* small mitten, thumb toward the body, aligned with the arm */}
      <g transform={`translate(${hand[0]} ${hand[1]}) rotate(${ang})`}>
        <ellipse cx={-side * 15} cy={2} rx={10} ry={13} fill={skin} {...LINE} strokeWidth={3.5} />
        <ellipse cx={0} cy={10} rx={21} ry={24} fill={skin} {...LINE} />
      </g>
    </g>
  );
};

const MOUTH_DARK = "#3e1010";
const TONGUE = "#E2737D";

export const Mouth: React.FC<{ shape: MouthShape }> = ({ shape }) => {
  const line = { stroke: MOUTH_DARK, strokeWidth: 6, strokeLinecap: "round" as const, fill: "none" };
  switch (shape) {
    case "closed":
      return <path d={`M -24 ${MY - 2} Q 0 ${MY + 7} 24 ${MY - 2}`} {...line} />;
    case "flat":
      return <path d={`M -22 ${MY} L 22 ${MY}`} {...line} />;
    case "smirk":
      return <path d={`M -22 ${MY + 4} Q 6 ${MY + 6} 30 ${MY - 10}`} {...line} />;
    case "frown":
      return <path d={`M -24 ${MY + 7} Q 0 ${MY - 7} 24 ${MY + 7}`} {...line} />;
    case "O":
      return <ellipse cx={0} cy={MY + 2} rx={13} ry={17} fill={MOUTH_DARK} />;
    case "open":
      return (
        <g>
          <path d={`M -28 ${MY - 8} Q 0 ${MY - 12} 28 ${MY - 8} Q 22 ${MY + 22} 0 ${MY + 22} Q -22 ${MY + 22} -28 ${MY - 8} Z`} fill={MOUTH_DARK} />
          <ellipse cx={0} cy={MY + 12} rx={12} ry={6} fill={TONGUE} />
        </g>
      );
    case "wide":
      return (
        <g>
          <path d={`M -38 ${MY - 12} Q 0 ${MY - 18} 38 ${MY - 12} Q 30 ${MY + 40} 0 ${MY + 40} Q -30 ${MY + 40} -38 ${MY - 12} Z`} fill={MOUTH_DARK} />
          <ellipse cx={0} cy={MY + 26} rx={18} ry={9} fill={TONGUE} />
        </g>
      );
    case "E":
      // teeth showing: ee, s, t, d, sh
      return (
        <g>
          <path d={`M -32 ${MY - 8} Q 0 ${MY - 12} 32 ${MY - 8} Q 26 ${MY + 14} 0 ${MY + 14} Q -26 ${MY + 14} -32 ${MY - 8} Z`} fill={MOUTH_DARK} />
          <path d={`M -28 ${MY - 8} Q 0 ${MY - 11} 28 ${MY - 8} L 26 ${MY - 1} Q 0 ${MY - 3} -26 ${MY - 1} Z`} fill="#fff" />
        </g>
      );
    case "F":
      // top teeth resting on the lower lip: f, v
      return (
        <g>
          <path d={`M -26 ${MY - 6} Q 0 ${MY - 10} 26 ${MY - 6} Q 20 ${MY + 8} 0 ${MY + 8} Q -20 ${MY + 8} -26 ${MY - 6} Z`} fill={MOUTH_DARK} />
          <rect x={-20} y={MY - 8} width={40} height={10} rx={2} fill="#fff" />
          <path d={`M -24 ${MY + 6} Q 0 ${MY + 14} 24 ${MY + 6}`} stroke="#B5615A" strokeWidth={5} fill="none" strokeLinecap="round" />
        </g>
      );
    case "smile":
      return (
        <g>
          <path d={`M -36 ${MY - 10} Q 0 ${MY + 40} 36 ${MY - 10} Z`} fill={MOUTH_DARK} />
          <path d={`M -32 ${MY - 8} L 32 ${MY - 8} L 28 ${MY + 1} L -28 ${MY + 1} Z`} fill="#fff" />
        </g>
      );
    case "angry":
      return (
        <g>
          <path d={`M -32 ${MY - 10} L 32 ${MY - 10} L 24 ${MY + 14} L -24 ${MY + 14} Z`} fill={MOUTH_DARK} />
          <rect x={-30} y={MY - 10} width={60} height={9} fill="#fff" />
        </g>
      );
  }
};

const IDLE_MOUTH: Record<Expression, MouthShape> = {
  neutral: "closed",
  worried: "frown",
  smug: "smirk",
  deadpan: "flat",
  excited: "smile",
  annoyed: "frown",
  scared: "O",
};

const Brows: React.FC<{ e: Expression }> = ({ e }) => {
  const s = { stroke: INK, strokeWidth: 9, strokeLinecap: "round" as const, fill: "none" };
  const pair = (l: string) => (
    <g>
      <path d={l} {...s} />
      <path d={l} {...s} transform="scale(-1 1)" />
    </g>
  );
  if (e === "worried" || e === "scared") return pair("M -74 -448 L -16 -462");
  if (e === "annoyed") return pair("M -74 -464 L -16 -446");
  if (e === "excited") return pair("M -76 -456 Q -46 -478 -14 -462");
  return null;
};

export type KidProps = {
  name: string;
  pose: Pose;
  expression: Expression;
  mouth: MouthShape | null; // null = not talking, use the expression's idle mouth
  lookX: number; // -1 .. 1, where the pupils point
  lookY?: number; // -1 (up, e.g. an eye-roll) .. 1 (down)
  turn?: number; // -1 .. 1, face slides toward this side (cutout "head turn")
  headTilt?: number; // degrees, pivots at the base of the head
  sweat?: number | null; // frame counter for flying sweat drops, null = dry
  step?: number | null; // walk phase 0/1 (which foot is up), null = standing
  blink: boolean;
};

const Drop: React.FC<{ x: number; y: number; flip: number }> = ({ x, y, flip }) => (
  <path
    transform={`translate(${x} ${y}) scale(${flip} 1)`}
    d="M 0 -22 Q 16 0 12 10 Q 6 22 -4 18 Q -14 12 -10 0 Q -6 -10 0 -22 Z"
    fill="#9FE0FF"
    stroke={INK}
    strokeWidth={3}
  />
);

export const Kid: React.FC<KidProps> = ({
  name,
  pose,
  expression,
  mouth,
  lookX,
  lookY = 0,
  turn = 0,
  headTilt = 0,
  sweat = null,
  step = null,
  blink,
}) => {
  // three-quarter view: when the kid turns, the body narrows, the feet step toward the turn
  // and the far arm tucks behind the body
  const tq = Math.abs(turn) > 0.3 ? Math.sign(turn) : 0;
  const d = DESIGNS[name];
  const arms = ARMS[pose];
  const big = expression === "scared";
  const erx = 45;
  const ery = big ? 62 : 55;
  const pr = big ? 5 : 7;
  const lidY = expression === "smug" ? EYE_Y + 6 : EYE_Y;
  // half-lids for the flat/sarcastic faces, lifted during an eye-roll so the pupils show
  const lid = (expression === "deadpan" || expression === "smug" || expression === "annoyed") && lookY > -0.5;
  const clipId = `body-${name}`;
  const armColor = d.sleeves ? d.shirt : d.skin;
  return (
    <g>
      {/* shoes: rounded domes; on a walk step one foot lifts and slides forward */}
      <g transform={`translate(${tq * 16} 0)`}>
      <path
        transform={step === 0 ? "translate(10 -14)" : undefined}
        d="M -116 0 Q -116 -48 -58 -48 Q -4 -48 -4 0 Z"
        fill={d.shoes}
        {...LINE}
      />
      <path
        transform={step === 1 ? "translate(-10 -14)" : undefined}
        d="M 116 0 Q 116 -48 58 -48 Q 4 -48 4 0 Z"
        fill={d.shoes}
        {...LINE}
      />
      </g>
      <path d="M -120 -78 L 120 -78 L 114 -30 L -114 -30 Z" fill={d.pants} {...LINE} />
      {/* far arm, behind the body when turned */}
      {tq !== 0 ? (
        <g transform={`translate(${tq * 38} 4)`}>
          <Arm pts={tq > 0 ? arms.l : arms.r} color={armColor} skin={d.skin} floatie={d.floaties} />
        </g>
      ) : null}
      {/* bell-shaped body */}
      <g transform={tq !== 0 ? "scale(0.94 1)" : undefined}>
      <clipPath id={clipId}>
        <path d={BODY} />
      </clipPath>
      <path d={BODY} fill={d.shirt} {...LINE} />
      {d.shirtPattern ? <g clipPath={`url(#${clipId})`}>{d.shirtPattern}</g> : null}
      {d.seam ? <path d="M 0 -220 L 0 -64" stroke={INK} strokeWidth={4} /> : null}
      <g transform={`translate(${turn * 14} 0)`}>{d.chest}</g>
      </g>
      {pose === "phone" ? (
        <g>
          <rect x={22} y={-232} width={52} height={86} rx={9} fill="#202020" {...LINE} />
          <rect x={29} y={-223} width={38} height={62} rx={4} fill="#7fd7ff" />
        </g>
      ) : null}
      {tq <= 0 ? <Arm pts={arms.l} color={armColor} skin={d.skin} floatie={d.floaties} swing={step === null ? 0 : step ? 12 : -12} /> : null}
      {tq >= 0 ? <Arm pts={arms.r} color={armColor} skin={d.skin} floatie={d.floaties} swing={step === null ? 0 : step ? 12 : -12} /> : null}
      {/* the head: its own card, sits straight on the body, no neck */}
      <g filter="url(#lift)" transform={`rotate(${headTilt} 0 -220) translate(0 -326) scale(1.08 0.955) translate(0 345)`}>
        {/* three-quarter turn: the far ear peeks out behind the head */}
        {Math.abs(turn) > 0.3 ? (
          <g transform={`translate(${-Math.sign(turn) * 160} -340)`}>
            <ellipse cx={0} cy={0} rx={26} ry={36} fill={d.skin} {...LINE} />
            <path d={`M ${-Math.sign(turn) * 6} -16 Q ${-Math.sign(turn) * 16} 0 ${-Math.sign(turn) * 6} 16`} stroke={INK} strokeWidth={3.5} fill="none" />
          </g>
        ) : null}
        <ellipse cx={0} cy={HEAD_Y} rx={HRX} ry={HRY} fill={d.skin} {...LINE} />
        <g transform={`translate(${turn * 10} 0)`}>{d.hair}</g>
        <g transform={`translate(${turn * 30} 0)`}>
        {[-1, 1].map((side) => {
          const cx = side * 41;
          return (
            <g key={side}>
              <ellipse cx={cx} cy={EYE_Y} rx={erx} ry={ery} fill="#FFFFFF" {...LINE} strokeWidth={3.5} />
              {blink ? (
                <g>
                  <ellipse cx={cx} cy={EYE_Y} rx={erx} ry={ery} fill={d.skin} {...LINE} strokeWidth={3.5} />
                  <path d={`M ${cx - 34} ${EYE_Y + 6} Q ${cx} ${EYE_Y + 16} ${cx + 34} ${EYE_Y + 6}`} stroke={INK} strokeWidth={4} fill="none" />
                </g>
              ) : (
                <g>
                  <circle cx={cx + lookX * 20 - side * 8} cy={EYE_Y + 4 + lookY * 30} r={pr} fill={INK} />
                  {lid ? (
                    <path d={`M ${cx - erx} ${lidY} A ${erx} ${ery} 0 0 1 ${cx + erx} ${lidY} Z`} fill={d.skin} {...LINE} strokeWidth={3.5} />
                  ) : null}
                </g>
              )}
            </g>
          );
        })}
        <Brows e={expression} />
        {d.face}
        <Mouth shape={mouth ?? IDLE_MOUTH[expression]} />
        </g>
      </g>
      {sweat !== null
        ? [0, 1].map((i) => {
            // two drops fly off the head on 2-frame steps, then loop
            const t = (Math.floor(sweat / 2) + i * 3) % 6;
            const side = i ? 1 : -1;
            return <Drop key={i} x={side * (150 + t * 16)} y={-440 - t * 10 + t * t * 4} flip={side} />;
          })
        : null}
    </g>
  );
};

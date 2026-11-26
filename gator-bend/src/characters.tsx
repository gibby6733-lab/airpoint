// The reusable character kit: each kid is the same modular rig (head, body, arm poses,
// eye directions, blinks, 6+ mouth shapes) with their own colors, hair and accessories.
import React from "react";
import { INK, OUTLINE } from "./paper";

export type Pose = "idle" | "arms-up" | "phone" | "point";
export type Expression = "neutral" | "worried" | "smug" | "deadpan" | "excited" | "annoyed" | "scared";
export type MouthShape = "closed" | "O" | "open" | "wide" | "smile" | "angry" | "frown" | "smirk" | "flat";

export type Design = {
  skin: string;
  shirt: string;
  shorts: string;
  shoes: string;
  hair: React.ReactNode; // drawn over the head
  face?: React.ReactNode; // drawn over the eyes (glasses, zinc, freckles)
  chest?: React.ReactNode; // necklace etc.
  shirtPattern?: React.ReactNode; // clipped to the torso
  floaties?: boolean;
};

const TORSO = "M -98 -330 L 98 -330 L 122 -148 L -122 -148 Z";

export const DESIGNS: Record<string, Design> = {
  danny: {
    skin: "#C68A62",
    shirt: "#1FA2A0",
    shorts: "#C9AE7C",
    shoes: "#E85A3C",
    hair: (
      <path
        d="M -158 -468 C -175 -650, 175 -650, 158 -468 L 124 -520 L 92 -492 L 58 -532 L 22 -500 L -18 -538 L -56 -500 L -92 -532 L -126 -496 Z"
        fill="#2a2320"
        {...OUTLINE}
      />
    ),
  },
  tucker: {
    skin: "#F7D5BE",
    shirt: "#F08A24",
    shorts: "#3C5AAA",
    shoes: "#F4F4F0",
    hair: (
      <g>
        <path d="M -125 -540 C -120 -668, 120 -668, 125 -540 Z" fill="#CDB98A" {...OUTLINE} />
        <path d="M -126 -566 L 126 -566 L 125 -542 L -125 -542 Z" fill="#8C7A4E" />
        <ellipse cx={0} cy={-540} rx={190} ry={30} fill="#CDB98A" {...OUTLINE} />
      </g>
    ),
    face: (
      <g>
        <circle cx={-98} cy={-418} r={22} fill="#F09A9A" />
        <circle cx={98} cy={-418} r={22} fill="#F09A9A" />
        <ellipse cx={0} cy={-424} rx={20} ry={10} fill="#FFFFFF" {...OUTLINE} strokeWidth={3} />
      </g>
    ),
  },
  bray: {
    skin: "#EFC6A0",
    shirt: "#8240B0",
    shorts: "#D23C3C",
    shoes: "#262626",
    hair: (
      <g>
        <path
          d="M -152 -498 L -170 -604 L -112 -578 L -98 -668 L -46 -612 L 0 -694 L 46 -612 L 98 -668 L 112 -578 L 170 -604 L 152 -498 C 100 -566, -100 -566, -152 -498 Z"
          fill="#F2D04A"
          {...OUTLINE}
        />
        {/* wraparound sunglasses pushed up on the forehead */}
        <path d="M -146 -578 Q 0 -616 146 -578 L 140 -540 Q 70 -526 8 -550 Q -70 -526 -140 -540 Z" fill="#161616" {...OUTLINE} />
        <path d="M -110 -572 Q -60 -586 -20 -580" stroke="#9fe7ff" strokeWidth={6} fill="none" />
      </g>
    ),
    chest: (
      <g>
        <path d="M -62 -328 Q 0 -262 62 -328" stroke="#6B4A2B" strokeWidth={6} fill="none" />
        <path d="M -14 -292 L 14 -292 L 0 -250 Z" fill="#FFFDF2" {...OUTLINE} strokeWidth={3} />
      </g>
    ),
  },
  wade: {
    skin: "#F5D4B6",
    shirt: "#4E9A4A",
    shorts: "#7A5A3A",
    shoes: "#3B6FD0",
    floaties: true,
    hair: (
      <path
        d="M -152 -478 L -178 -540 L -142 -562 L -162 -622 L -100 -612 L -90 -672 L -40 -632 L 0 -684 L 40 -632 L 90 -668 L 100 -606 L 162 -622 L 142 -562 L 178 -532 L 152 -478 C 100 -560, -100 -560, -152 -478 Z"
        fill="#E06A28"
        {...OUTLINE}
      />
    ),
    shirtPattern: (
      <g fill="#357A33">
        <rect x={-140} y={-300} width={280} height={26} />
        <rect x={-140} y={-246} width={280} height={26} />
        <rect x={-140} y={-192} width={280} height={26} />
      </g>
    ),
  },
};

type Pt = [number, number];
const ARMS: Record<Pose, { l: Pt[]; r: Pt[] }> = {
  idle: { l: [[-92, -312], [-138, -192]], r: [[92, -312], [138, -192]] },
  "arms-up": { l: [[-92, -312], [-160, -380], [-176, -462]], r: [[92, -312], [160, -380], [176, -462]] },
  phone: { l: [[-92, -312], [-138, -192]], r: [[92, -312], [118, -238], [52, -262]] },
  point: { l: [[-92, -312], [-138, -192]], r: [[92, -312], [168, -360], [210, -420]] },
};

const Arm: React.FC<{ pts: Pt[]; skin: string; floatie?: boolean }> = ({ pts, skin, floatie }) => {
  const d = "M " + pts.map((p) => p.join(" ")).join(" L ");
  const hand = pts[pts.length - 1];
  const [s, n] = [pts[0], pts[1]];
  const fl: Pt = [s[0] + (n[0] - s[0]) * 0.42, s[1] + (n[1] - s[1]) * 0.42];
  return (
    <g>
      <path d={d} stroke={INK} strokeWidth={48} strokeLinecap="round" strokeLinejoin="round" fill="none" />
      <path d={d} stroke={skin} strokeWidth={38} strokeLinecap="round" strokeLinejoin="round" fill="none" />
      {floatie ? (
        <g>
          <circle cx={fl[0]} cy={fl[1]} r={40} fill="#FF8A1F" {...OUTLINE} />
          <path d={`M ${fl[0] - 38} ${fl[1] - 6} L ${fl[0] + 38} ${fl[1] - 6}`} stroke="#FFF1D6" strokeWidth={10} />
        </g>
      ) : null}
      {/* mitten hand + thumb */}
      <circle cx={hand[0]} cy={hand[1]} r={30} fill={skin} {...OUTLINE} />
      <circle cx={hand[0] + (hand[0] > 0 ? -22 : 22)} cy={hand[1] - 20} r={13} fill={skin} {...OUTLINE} strokeWidth={4} />
    </g>
  );
};

const MOUTH_DARK = "#4a1414";
const TONGUE = "#E2737D";
const MY = -386; // mouth center

export const Mouth: React.FC<{ shape: MouthShape }> = ({ shape }) => {
  const line = { stroke: MOUTH_DARK, strokeWidth: 7, strokeLinecap: "round" as const, fill: "none" };
  switch (shape) {
    case "closed":
      return <path d={`M -28 ${MY - 2} Q 0 ${MY + 8} 28 ${MY - 2}`} {...line} />;
    case "flat":
      return <path d={`M -26 ${MY} L 26 ${MY}`} {...line} />;
    case "smirk":
      return <path d={`M -26 ${MY + 4} Q 6 ${MY + 6} 32 ${MY - 12}`} {...line} />;
    case "frown":
      return <path d={`M -28 ${MY + 8} Q 0 ${MY - 8} 28 ${MY + 8}`} {...line} />;
    case "O":
      return <ellipse cx={0} cy={MY} rx={14} ry={19} fill={MOUTH_DARK} />;
    case "open":
      return (
        <g>
          <ellipse cx={0} cy={MY} rx={26} ry={18} fill={MOUTH_DARK} />
          <ellipse cx={0} cy={MY + 9} rx={14} ry={7} fill={TONGUE} />
        </g>
      );
    case "wide":
      return (
        <g>
          <path d={`M -42 ${MY - 12} Q 0 ${MY - 16} 42 ${MY - 12} Q 34 ${MY + 42} 0 ${MY + 42} Q -34 ${MY + 42} -42 ${MY - 12} Z`} fill={MOUTH_DARK} />
          <ellipse cx={0} cy={MY + 28} rx={20} ry={10} fill={TONGUE} />
        </g>
      );
    case "smile":
      return (
        <g>
          <path d={`M -40 ${MY - 10} Q 0 ${MY + 46} 40 ${MY - 10} Z`} fill={MOUTH_DARK} />
          <path d={`M -36 ${MY - 8} L 36 ${MY - 8} L 32 ${MY + 2} L -32 ${MY + 2} Z`} fill="#fff" />
        </g>
      );
    case "angry":
      return (
        <g>
          <path d={`M -36 ${MY - 12} L 36 ${MY - 12} L 28 ${MY + 16} L -28 ${MY + 16} Z`} fill={MOUTH_DARK} />
          <rect x={-34} y={MY - 12} width={68} height={10} fill="#fff" />
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
  const s = { stroke: INK, strokeWidth: 10, strokeLinecap: "round" as const, fill: "none" };
  const pair = (l: string) => (
    <g>
      <path d={l} {...s} />
      <path d={l} {...s} transform="scale(-1 1)" />
    </g>
  );
  if (e === "worried" || e === "scared") return pair("M -78 -548 L -18 -566");
  if (e === "annoyed") return pair("M -78 -566 L -18 -546");
  if (e === "excited") return pair("M -80 -560 Q -50 -584 -16 -566");
  return null;
};

export type KidProps = {
  name: string;
  pose: Pose;
  expression: Expression;
  mouth: MouthShape | null; // null = not talking, use the expression's idle mouth
  lookX: number; // -1 .. 1
  blink: boolean;
};

export const Kid: React.FC<KidProps> = ({ name, pose, expression, mouth, lookX, blink }) => {
  const d = DESIGNS[name];
  const arms = ARMS[pose];
  const big = expression === "scared";
  const eyeRy = big ? 58 : 52;
  const pr = big ? 6 : 9;
  const lid = expression === "deadpan" || expression === "smug" || expression === "annoyed";
  const clipId = `torso-${name}`;
  return (
    <g>
      {/* legs + shoes */}
      <rect x={-64} y={-80} width={40} height={58} fill={d.skin} {...OUTLINE} />
      <rect x={24} y={-80} width={40} height={58} fill={d.skin} {...OUTLINE} />
      <ellipse cx={-50} cy={-16} rx={52} ry={20} fill={d.shoes} {...OUTLINE} />
      <ellipse cx={50} cy={-16} rx={52} ry={20} fill={d.shoes} {...OUTLINE} />
      <path d="M -112 -176 L 112 -176 L 108 -74 L 6 -74 L 0 -112 L -6 -74 L -108 -74 Z" fill={d.shorts} {...OUTLINE} />
      {/* torso */}
      <clipPath id={clipId}>
        <path d={TORSO} />
      </clipPath>
      <path d={TORSO} fill={d.shirt} {...OUTLINE} />
      {d.shirtPattern ? <g clipPath={`url(#${clipId})`}>{d.shirtPattern}</g> : null}
      {d.chest}
      {/* phone sits under the hand */}
      {pose === "phone" ? (
        <g>
          <rect x={22} y={-344} width={58} height={96} rx={10} fill="#202020" {...OUTLINE} />
          <rect x={30} y={-334} width={42} height={70} rx={4} fill="#7fd7ff" />
        </g>
      ) : null}
      <Arm pts={arms.l} skin={d.skin} floatie={d.floaties} />
      <Arm pts={arms.r} skin={d.skin} floatie={d.floaties} />
      {/* head: its own card above the body */}
      <g filter="url(#lift)">
        <ellipse cx={0} cy={-462} rx={158} ry={140} fill={d.skin} {...OUTLINE} />
        {d.hair}
        <g filter="url(#lift)">
          {[-1, 1].map((side) => (
            <g key={side}>
              <ellipse cx={side * 40} cy={-486} rx={41} ry={eyeRy} fill="#FFFFFF" {...OUTLINE} strokeWidth={4} />
              {blink ? (
                <g>
                  <ellipse cx={side * 40} cy={-486} rx={41} ry={eyeRy} fill={d.skin} {...OUTLINE} strokeWidth={4} />
                  <path d={`M ${side * 40 - 34} -480 Q ${side * 40} -470 ${side * 40 + 34} -480`} stroke={INK} strokeWidth={5} fill="none" />
                </g>
              ) : (
                <g>
                  <circle cx={side * 40 + lookX * 18} cy={-480} r={pr} fill={INK} />
                  {lid ? (
                    <path
                      d={`M ${side * 40 - 41} ${expression === "smug" ? -478 : -486} A 41 ${eyeRy} 0 0 1 ${side * 40 + 41} ${expression === "smug" ? -478 : -486} Z`}
                      fill={d.skin}
                      {...OUTLINE}
                      strokeWidth={4}
                    />
                  ) : null}
                </g>
              )}
            </g>
          ))}
        </g>
        <Brows e={expression} />
        {d.face}
        <Mouth shape={mouth ?? IDLE_MOUTH[expression]} />
      </g>
    </g>
  );
};

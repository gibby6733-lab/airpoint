// Construction-paper look, done with SVG filters:
//  - grain + stretched "fiber" noise multiplied into each shape's fill (visible fibers, slight color drift)
//  - a drop shadow whose size depends on how high the card sits above the layer below it
//    (the equivalent of spacing flat cards apart in 3D and letting an overhead lamp cast shadows).
import React from "react";

const SHADOW = "#2b1707";

// depth 0 = glued flat to the table, 3 = lifted highest off the background
const DEPTHS = [
  { dx: 0, dy: 0, blur: 0, op: 0 },
  { dx: 3, dy: 5, blur: 3, op: 0.32 },
  { dx: 8, dy: 12, blur: 7, op: 0.36 },
  { dx: 14, dy: 22, blur: 12, op: 0.4 },
];

const PaperFilter: React.FC<{ id: string; seed: number; depth: number }> = ({ id, seed, depth }) => {
  const d = DEPTHS[depth];
  return (
    <filter id={id} x="-20%" y="-20%" width="140%" height="140%" colorInterpolationFilters="sRGB">
      <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves={2} seed={seed} result="grain" />
      <feTurbulence type="fractalNoise" baseFrequency="0.03 0.35" numOctaves={2} seed={seed + 7} result="fiber" />
      <feComposite in="grain" in2="fiber" operator="arithmetic" k2={0.4} k3={0.6} result="mix" />
      <feColorMatrix
        in="mix"
        type="matrix"
        values="0.33 0.33 0.33 0 0  0.33 0.33 0.33 0 0  0.33 0.33 0.33 0 0  0 0 0 0 1"
        result="gray"
      />
      <feComposite in="SourceGraphic" in2="gray" operator="arithmetic" k1={0.4} k2={0.81} result="tex" />
      <feComposite in="tex" in2="SourceAlpha" operator="in" result="paper" />
      {depth > 0 ? (
        <feDropShadow in="paper" dx={d.dx} dy={d.dy} stdDeviation={d.blur} floodColor={SHADOW} floodOpacity={d.op} />
      ) : null}
    </filter>
  );
};

export const paper = (depth: 0 | 1 | 2 | 3, variant = 0) => `url(#paper-${depth}-${variant % 3})`;
export const LIFT = "url(#lift)";

export const PaperDefs: React.FC = () => (
  <svg width={0} height={0} style={{ position: "absolute" }}>
    <defs>
      {[0, 1, 2, 3].flatMap((depth) =>
        [0, 1, 2].map((v) => <PaperFilter key={`${depth}-${v}`} id={`paper-${depth}-${v}`} seed={3 + v * 13} depth={depth} />),
      )}
      {/* small shadow for parts layered on the same character (head over body, eyes over head) */}
      <filter id="lift" x="-20%" y="-20%" width="140%" height="140%">
        <feDropShadow dx={2} dy={4} stdDeviation={2} floodColor={SHADOW} floodOpacity={0.3} />
      </filter>
    </defs>
  </svg>
);

export const INK = "#1d140e";
export const OUTLINE = { stroke: INK, strokeWidth: 5, strokeLinejoin: "round" as const };

// Construction-paper look, done with SVG filters. Every card (character, prop, scenery sheet) gets:
//  1. a scissor-cut edge: the silhouette is nudged by low-frequency noise so no curve is perfect
//  2. dyed-paper surface: blotchy color variation + fine grain + short fibers
//  3. flecks: the small light specks construction paper has
//  4. a light rim along the cut edge, where the paper's core shows
//  5. a drop shadow sized by how high the card sits above the layer below
//     (flat cards spaced apart in 3D under an overhead lamp)
// The cut-edge noise changes seed every few frames ("boil"), so edges shimmer slightly like
// hand-made animation instead of sitting dead still.
import React from "react";

const SHADOW = "#2b1707";
const BOIL_FRAMES = 4; // edges re-cut every 4 frames

// depth 0 = glued flat to the table, 3 = lifted highest off the background
const DEPTHS = [
  { dx: 0, dy: 0, blur: 0, op: 0 },
  { dx: 2, dy: 4, blur: 3, op: 0.22 },
  { dx: 5, dy: 9, blur: 6, op: 0.26 },
  { dx: 9, dy: 15, blur: 9, op: 0.3 },
];

const PaperFilter: React.FC<{ id: string; seed: number; depth: number; boil: number }> = ({ id, seed, depth, boil }) => {
  const d = DEPTHS[depth];
  const edgeSeed = seed + (boil % 3) * 17;
  return (
    <filter id={id} x="-20%" y="-20%" width="140%" height="140%" colorInterpolationFilters="sRGB">
      {/* 1. scissor-cut edge */}
      <feTurbulence type="fractalNoise" baseFrequency="0.04" numOctaves={2} seed={edgeSeed} result="edgeNoise" />
      <feDisplacementMap in="SourceGraphic" in2="edgeNoise" scale={depth === 0 ? 2 : 4} xChannelSelector="R" yChannelSelector="G" result="cut" />
      {/* 2. dyed-paper surface */}
      <feTurbulence type="fractalNoise" baseFrequency="0.007" numOctaves={2} seed={seed} result="blotch" />
      <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves={2} seed={seed + 3} result="grain" />
      <feTurbulence type="fractalNoise" baseFrequency="0.05 0.3" numOctaves={2} seed={seed + 7} result="fiber" />
      <feComposite in="blotch" in2="grain" operator="arithmetic" k2={0.5} k3={0.5} result="mix1" />
      <feComposite in="mix1" in2="fiber" operator="arithmetic" k2={0.62} k3={0.38} result="mix" />
      <feColorMatrix in="mix" type="matrix" values="0.33 0.33 0.33 0 0  0.33 0.33 0.33 0 0  0.33 0.33 0.33 0 0  0 0 0 0 1" result="gray" />
      <feComposite in="cut" in2="gray" operator="arithmetic" k1={0.46} k2={0.77} result="tex" />
      <feComposite in="tex" in2="cut" operator="in" result="surface" />
      {/* 3. flecks */}
      <feTurbulence type="fractalNoise" baseFrequency="0.45" numOctaves={1} seed={seed + 11} result="speckNoise" />
      <feColorMatrix in="speckNoise" type="matrix" values="0 0 0 0 1  0 0 0 0 0.98  0 0 0 0 0.92  4.5 0 0 0 -3.5" result="specks" />
      <feComposite in="specks" in2="cut" operator="in" result="flecks" />
      {/* 4. light rim on the cut edge */}
      <feMorphology in="cut" operator="erode" radius={2.5} result="inner" />
      <feComposite in="cut" in2="inner" operator="out" result="rimShape" />
      <feFlood floodColor="#FFF6E0" floodOpacity={0.28} result="rimColor" />
      <feComposite in="rimColor" in2="rimShape" operator="in" result="rim" />
      <feMerge result="paper">
        <feMergeNode in="surface" />
        <feMergeNode in="flecks" />
        <feMergeNode in="rim" />
      </feMerge>
      {/* 5. shadow */}
      {depth > 0 ? (
        <feDropShadow in="paper" dx={d.dx} dy={d.dy} stdDeviation={d.blur} floodColor={SHADOW} floodOpacity={d.op} />
      ) : null}
    </filter>
  );
};

export const paper = (depth: 0 | 1 | 2 | 3, variant = 0) => `url(#paper-${depth}-${variant % 3})`;
export const LIFT = "url(#lift)";

export const PaperDefs: React.FC<{ frame?: number }> = ({ frame = 0 }) => {
  const boil = Math.floor(frame / BOIL_FRAMES);
  return (
    <svg width={0} height={0} style={{ position: "absolute" }}>
      <defs>
        {[0, 1, 2, 3].flatMap((depth) =>
          [0, 1, 2].map((v) => (
            <PaperFilter key={`${depth}-${v}`} id={`paper-${depth}-${v}`} seed={3 + v * 13} depth={depth} boil={boil} />
          )),
        )}
        {/* whip-pan motion blur: horizontal only */}
        <filter id="whip" x="-10%" y="0%" width="120%" height="100%">
          <feGaussianBlur stdDeviation="28 0" />
        </filter>
        {/* small shadow for parts layered on the same character (head over body, eyes over head) */}
        <filter id="lift" x="-20%" y="-20%" width="140%" height="140%">
          <feDropShadow dx={1} dy={3} stdDeviation={2} floodColor={SHADOW} floodOpacity={0.2} />
        </filter>
      </defs>
    </svg>
  );
};

export const INK = "#1d140e";
export const OUTLINE = { stroke: INK, strokeWidth: 4, strokeLinejoin: "round" as const };
// Scenery has no black outlines, just a faint darker edge where paper meets paper.
export const EDGE = { stroke: "rgba(40,20,0,0.16)", strokeWidth: 3, strokeLinejoin: "round" as const };

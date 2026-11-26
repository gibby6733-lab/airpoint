// Gator Bend, FL: background cards, the bus-stop gator, and the school bus.
// Everything is built from flat shapes; each card gets the paper filter and a
// shadow sized to how far it sits above the layer under it.
import React from "react";
import { EDGE, INK, OUTLINE, paper } from "./paper";

export const WORLD_W = 2400;
export const WORLD_H = 4266; // 9:16, so the wide shot shows the whole street
export const FEET_Y = 2640;
export const POND = { cx: 2110, cy: 2330, rx: 300, ry: 92 };
export const GATOR_X = 2190;
export const FONT = "GBInter, Inter, sans-serif";

const Txt: React.FC<{ x: number; y: number; size: number; fill: string; children: React.ReactNode; anchor?: "start" | "middle" }> = ({
  x,
  y,
  size,
  fill,
  children,
  anchor = "middle",
}) => (
  <text x={x} y={y} fontFamily={FONT} fontWeight={900} fontSize={size} fill={fill} textAnchor={anchor}>
    {children}
  </text>
);

const Palm: React.FC<{ x: number; base: number; top: number; lean: number; variant: number }> = ({ x, base, top, lean, variant }) => {
  const segs = 9;
  const pieces = [];
  for (let i = 0; i < segs; i++) {
    const t0 = i / segs;
    const t1 = (i + 1) / segs;
    const y0 = base - (base - top) * t0;
    const y1 = base - (base - top) * t1;
    const x0 = x + lean * t0 * t0;
    const x1 = x + lean * t1 * t1;
    const w0 = 46 - 18 * t0;
    const w1 = 46 - 18 * t1;
    pieces.push(
      <path
        key={i}
        d={`M ${x0 - w0} ${y0} L ${x0 + w0} ${y0} L ${x1 + w1 + 6} ${y1 + 8} L ${x1 - w1 - 6} ${y1 + 8} Z`}
        fill={i % 2 ? "#8A5A33" : "#9C6A3E"}
        {...EDGE}
      />,
    );
  }
  const cx = x + lean;
  const fronds = [-160, -120, -75, -30, 15, 60, 105, 150, 195].map((a, i) => {
    const r = (a * Math.PI) / 180;
    const L = 300 + (i % 3) * 40;
    const ex = cx + Math.cos(r) * L;
    const ey = top + Math.sin(r) * L * 0.55 + 60;
    const mx = cx + Math.cos(r) * L * 0.55;
    const my = top + Math.sin(r) * L * 0.3 - 40;
    return (
      <path
        key={a}
        d={`M ${cx} ${top} Q ${mx} ${my - 60} ${ex} ${ey} Q ${mx} ${my + 30} ${cx} ${top + 20} Z`}
        fill={i % 2 ? "#3F8F3A" : "#4FA445"}
        {...EDGE}
      />
    );
  });
  return (
    <g filter={paper(2, variant)}>
      {pieces}
      {fronds}
      <circle cx={cx - 20} cy={top + 30} r={22} fill="#6B4A2B" {...EDGE} />
      <circle cx={cx + 18} cy={top + 36} r={22} fill="#6B4A2B" {...EDGE} />
    </g>
  );
};

export const Background: React.FC = () => (
  <g>
    {/* sky + ground: the table-top sheets */}
    <g filter={paper(0, 0)}>
      <rect x={0} y={0} width={WORLD_W} height={2010} fill="#8FD3EE" />
      <rect x={0} y={2000} width={WORLD_W} height={490} fill="#79B84A" />
      <rect x={0} y={3330} width={WORLD_W} height={WORLD_H - 3330} fill="#6FAE44" />
    </g>
    {/* clouds */}
    <g filter={paper(1, 1)}>
      {[
        [420, 520, 1],
        [1300, 300, 0.8],
        [1700, 1150, 0.9],
        [520, 1250, 0.7],
      ].map(([x, y, s], i) => (
        <path
          key={i}
          transform={`translate(${x} ${y}) scale(${s})`}
          d="M -220 40 Q -230 -40 -140 -40 Q -110 -120 -10 -100 Q 60 -160 140 -80 Q 240 -80 230 20 Q 240 70 170 70 L -170 70 Q -240 70 -220 40 Z"
          fill="#FBFBF4"
          {...EDGE}
        />
      ))}
    </g>
    {/* billboard */}
    <g filter={paper(2, 2)}>
      <rect x={300} y={1700} width={34} height={330} fill="#8A5A33" {...EDGE} />
      <rect x={880} y={1700} width={34} height={330} fill="#8A5A33" {...EDGE} />
      <rect x={140} y={1420} width={940} height={380} fill="#F4EBD0" {...EDGE} strokeWidth={7} />
      <rect x={170} y={1450} width={880} height={320} fill="none" stroke="#D9443A" strokeWidth={10} />
      <Txt x={610} y={1540} size={64} fill="#1E8F8A">WELCOME TO</Txt>
      <Txt x={610} y={1655} size={92} fill="#D9443A">GATOR BEND, FL</Txt>
      <Txt x={610} y={1745} size={58} fill="#1d140e">{"“it's fine.”"}</Txt>
    </g>
    {/* strip mall */}
    <g filter={paper(1, 0)}>
      <rect x={1150} y={1640} width={1250} height={370} fill="#E8CFA6" {...EDGE} />
      <rect x={1130} y={1608} width={1290} height={50} fill="#C8A57A" {...EDGE} />
      {[
        { x: 1180, label: "VAPE", bg: "#7B3FA0", fg: "#fff" },
        { x: 1490, label: "PAWN", bg: "#F2C230", fg: INK },
        { x: 1800, label: "BOATS", bg: "#2B6CB0", fg: "#fff" },
        { x: 2110, label: "GOLD $$", bg: "#D9443A", fg: "#fff" },
      ].map((s) => (
        <g key={s.label}>
          <rect x={s.x} y={1690} width={270} height={92} fill={s.bg} {...EDGE} />
          <Txt x={s.x + 135} y={1756} size={60} fill={s.fg}>
            {s.label}
          </Txt>
          <rect x={s.x + 20} y={1820} width={140} height={190} fill="#3D6E8C" {...EDGE} />
          <rect x={s.x + 180} y={1840} width={70} height={170} fill="#5B4636" {...EDGE} />
        </g>
      ))}
    </g>
    <Palm x={1090} base={2230} top={1180} lean={-60} variant={0} />
    <Palm x={2290} base={2190} top={1300} lean={50} variant={1} />
    {/* pond (back half) + reeds */}
    <g filter={paper(1, 2)}>
      <ellipse cx={POND.cx} cy={POND.cy} rx={POND.rx} ry={POND.ry} fill="#4C93B0" {...EDGE} />
      {[1830, 1860, 2385, 2350].map((x, i) => (
        <g key={x}>
          <path d={`M ${x} ${POND.cy} L ${x + (i % 2 ? 8 : -8)} ${POND.cy - 150}`} stroke="#3F7A2E" strokeWidth={10} />
          <rect x={x - 11 + (i % 2 ? 8 : -8)} y={POND.cy - 190} width={22} height={56} rx={11} fill="#7A4A26" {...EDGE} strokeWidth={3} />
        </g>
      ))}
      <rect x={1600} y={2120} width={14} height={180} fill="#8A5A33" />
      <rect x={1520} y={2070} width={180} height={80} fill="#FFFFFF" {...EDGE} />
      <Txt x={1610} y={2104} size={26} fill="#D9443A">NO SWIMMING</Txt>
      <Txt x={1610} y={2136} size={24} fill={INK}>(lol)</Txt>
    </g>
    {/* sidewalk, curb, road */}
    <g filter={paper(0, 1)}>
      <rect x={0} y={2480} width={WORLD_W} height={214} fill="#D2CFC6" />
      {[300, 700, 1100, 1500, 1900, 2300].map((x) => (
        <path key={x} d={`M ${x} 2480 L ${x - 30} 2694`} stroke="#A9A59B" strokeWidth={5} />
      ))}
      <rect x={0} y={2690} width={WORLD_W} height={34} fill="#A9A59B" />
      <rect x={0} y={2724} width={WORLD_W} height={606} fill="#5E5F66" />
      {[0, 1, 2, 3, 4, 5].map((i) => (
        <rect key={i} x={60 + i * 420} y={3010} width={240} height={26} fill="#F2C230" />
      ))}
      <rect x={0} y={3330} width={WORLD_W} height={34} fill="#A9A59B" />
    </g>
    {/* bus stop sign */}
    <g filter={paper(2, 0)}>
      <rect x={213} y={2150} width={22} height={500} fill="#9AA0A6" {...EDGE} />
      <rect x={120} y={2120} width={210} height={150} rx={14} fill="#FFFFFF" {...EDGE} strokeWidth={6} />
      <Txt x={225} y={2186} size={52} fill="#2B6CB0">BUS</Txt>
      <Txt x={225} y={2240} size={40} fill="#2B6CB0">STOP</Txt>
    </g>
    {/* front lawn: flamingo + for-sale sign */}
    <g filter={paper(2, 1)}>
      <path d="M 420 3720 L 420 3560" stroke={INK} strokeWidth={8} />
      <path d="M 445 3720 L 440 3560" stroke={INK} strokeWidth={8} />
      <ellipse cx={440} cy={3530} rx={90} ry={56} fill="#FF7EB6" {...EDGE} />
      <path d="M 500 3510 Q 560 3400 520 3330" stroke="#FF7EB6" strokeWidth={26} fill="none" strokeLinecap="round" />
      <circle cx={520} cy={3320} r={30} fill="#FF7EB6" {...EDGE} />
      <path d="M 545 3315 L 590 3340 L 548 3345 Z" fill={INK} />
      <rect x={1560} y={3560} width={16} height={260} fill="#8A5A33" {...EDGE} />
      <rect x={1380} y={3440} width={380} height={170} fill="#FFFFFF" {...EDGE} strokeWidth={6} />
      <Txt x={1570} y={3510} size={58} fill="#D9443A">FOR SALE</Txt>
      <Txt x={1570} y={3570} size={34} fill={INK}>sinkhole adjacent</Txt>
    </g>
  </g>
);

// Sun with rays that tick around on 6-frame holds.
export const Sun: React.FC<{ frame: number }> = ({ frame }) => {
  const rot = Math.floor(frame / 6) * 7.5;
  return (
    <g filter={paper(1, 0)} transform={`translate(1960 780)`}>
      <g transform={`rotate(${rot})`}>
        {Array.from({ length: 12 }, (_, i) => (
          <path key={i} transform={`rotate(${i * 30})`} d="M -26 -205 L 26 -205 L 0 -290 Z" fill="#FFB43F" {...EDGE} />
        ))}
      </g>
      <circle r={175} fill="#FFD23F" {...EDGE} strokeWidth={6} />
    </g>
  );
};

// Heat shimmer over the road: two drawings swapped every 4 frames.
export const Heat: React.FC<{ frame: number }> = ({ frame }) => {
  const phase = Math.floor(frame / 4) % 2;
  return (
    <g opacity={0.45}>
      {[0, 1, 2, 3, 4].map((i) => {
        const x = 150 + i * 470;
        const y = 2820 + (i % 2) * 120;
        const a = phase ? 18 : -18;
        return (
          <path
            key={i}
            d={`M ${x} ${y} q 40 ${a} 80 0 t 80 0 t 80 0 t 80 0`}
            stroke="#FFFFFF"
            strokeWidth={9}
            fill="none"
            strokeLinecap="round"
          />
        );
      })}
    </g>
  );
};

// The bus-stop gator. Upper jaw is a separate card hinged at the back of the head.
export const Gator: React.FC<{ jaw: number; burp: number; frame: number }> = ({ jaw, burp, frame }) => {
  const hx = 170;
  const hy = -40;
  const r = (jaw * Math.PI) / 180;
  const tip: [number, number] = [hx - 410 * Math.cos(r), hy - 410 * Math.sin(r)];
  const teeth = (up: boolean) =>
    Array.from({ length: 9 }, (_, i) => {
      const x = -215 + i * 44;
      return <path key={i} d={`M ${x} ${hy} L ${x + 20} ${hy} L ${x + 10} ${hy + (up ? -16 : 16)} Z`} fill="#FFFDF2" stroke={INK} strokeWidth={2} />;
    });
  return (
    <g transform={`translate(${GATOR_X} ${POND.cy + 18}) scale(0.95)`}>
      <g filter={paper(2, 1)}>
        {/* inside of the mouth */}
        <path d={`M ${hx} ${hy} L -240 ${hy} L ${tip[0]} ${tip[1]} Z`} fill="#C9475E" />
        {/* pool noodle */}
        <g transform="rotate(-6 -200 -60)">
          <rect x={-420} y={-82} width={280} height={46} rx={22} fill="#FF77B7" {...OUTLINE} />
          <ellipse cx={-410} cy={-59} rx={12} ry={18} fill="#C94F8A" />
        </g>
        {/* lower jaw */}
        <path d={`M -240 ${hy} L 180 ${hy} L 180 10 L -222 10 Q -254 -6 -240 ${hy} Z`} fill="#6FA34E" {...OUTLINE} />
        {teeth(true)}
        {/* upper jaw + eyes, rotates around the hinge */}
        <g transform={`rotate(${jaw} ${hx} ${hy})`}>
          <path
            d={`M 182 ${hy} L 182 -108 Q 160 -170 86 -168 L -150 -126 Q -252 -112 -260 -72 Q -260 -46 -240 ${hy} Z`}
            fill="#4E8A3A"
            {...OUTLINE}
          />
          {teeth(false)}
          <circle cx={-226} cy={-118} r={12} fill="#4E8A3A" {...OUTLINE} strokeWidth={4} />
          {[-80, -20, 40].map((x) => (
            <path key={x} d={`M ${x} -142 L ${x + 18} -164 L ${x + 36} -146 Z`} fill="#3B6E2C" />
          ))}
          {[60, 132].map((x) => (
            <g key={x}>
              <circle cx={x} cy={-172} r={34} fill="#4E8A3A" {...OUTLINE} />
              <ellipse cx={x} cy={-176} rx={20} ry={15} fill="#F2D04A" {...OUTLINE} strokeWidth={3} />
              <ellipse cx={x + 3} cy={-176} rx={4} ry={13} fill={INK} />
            </g>
          ))}
        </g>
      </g>
      {/* burp bubbles */}
      {burp > 0
        ? [0, 1, 2, 3].map((i) => {
            const t = burp * 1.6 - i * 0.25;
            if (t <= 0) return null;
            return (
              <circle
                key={i}
                cx={-280 - i * 30 + Math.sin(i * 2) * 30}
                cy={-120 - t * 260}
                r={14 + i * 6}
                fill="#DDF3FF"
                opacity={0.85}
                {...OUTLINE}
                strokeWidth={3}
              />
            );
          })
        : null}
    </g>
  );
};

// Front half of the pond, drawn over the gator so its body sits under the water.
export const PondFront: React.FC<{ frame: number }> = ({ frame }) => {
  const ripple = Math.floor(frame / 6) % 2;
  const { cx, cy, rx, ry } = POND;
  return (
    <g filter={paper(1, 2)}>
      <path d={`M ${cx - rx} ${cy} A ${rx} ${ry} 0 0 0 ${cx + rx} ${cy} Z`} fill="#4C93B0" {...EDGE} />
      <path d={`M ${cx - 120} ${cy + 30 + ripple * 6} q 40 -14 80 0 t 80 0`} stroke="#9FD6EA" strokeWidth={8} fill="none" strokeLinecap="round" />
      <path d={`M ${cx + 40} ${cy + 55 - ripple * 6} q 40 -14 80 0 t 80 0`} stroke="#9FD6EA" strokeWidth={8} fill="none" strokeLinecap="round" />
    </g>
  );
};

export const BUS_W = 1500;
export const Bus: React.FC<{ x: number; bounce: number }> = ({ x, bounce }) => (
  <g transform={`translate(${x} ${3190 + bounce})`} filter={paper(3, 0)}>
    <rect x={0} y={-600} width={BUS_W} height={520} rx={46} fill="#F3B81E" {...OUTLINE} strokeWidth={7} />
    <rect x={0} y={-300} width={BUS_W} height={22} fill={INK} />
    <rect x={0} y={-250} width={BUS_W} height={14} fill={INK} />
    {Array.from({ length: 6 }, (_, i) => (
      <rect key={i} x={230 + i * 200} y={-555} width={160} height={150} rx={12} fill="#9FD3E8" {...OUTLINE} />
    ))}
    <rect x={40} y={-560} width={150} height={420} rx={10} fill="#7FB8CF" {...OUTLINE} />
    <path d="M 115 -560 L 115 -140" stroke={INK} strokeWidth={5} />
    <Txt x={830} y={-330} size={66} fill={INK}>GATOR BEND ELEMENTARY</Txt>
    <g transform="translate(250 -360)">
      <path d="M -40 -96 L 40 -96 L 96 -40 L 96 40 L 40 96 L -40 96 L -96 40 L -96 -40 Z" transform="scale(0.55)" fill="#D9443A" {...OUTLINE} />
      <Txt x={0} y={13} size={30} fill="#fff">STOP</Txt>
    </g>
    {[280, 1220].map((wx) => (
      <g key={wx}>
        <circle cx={wx} cy={-80} r={92} fill="#222" {...OUTLINE} />
        <circle cx={wx} cy={-80} r={38} fill="#9AA0A6" {...OUTLINE} />
      </g>
    ))}
  </g>
);

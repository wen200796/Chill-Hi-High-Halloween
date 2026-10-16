import React, { useMemo } from 'react';
import { AbsoluteFill, random } from 'remotion';
import { COLORS } from '../config/theme';
import { hash, noise1 } from '../util';

/** 夜空漸層 */
export const Sky: React.FC<{ top?: string; mid?: string; bottom?: string }> = ({
  top = COLORS.night,
  mid = COLORS.navy,
  bottom = COLORS.deepBlue,
}) => <AbsoluteFill style={{ background: `linear-gradient(180deg, ${top} 0%, ${mid} 45%, ${bottom} 100%)` }} />;

/** 星星（帶閃爍） */
export const Stars: React.FC<{ frame: number; count?: number; seed?: string; maxY?: number }> = ({
  frame,
  count = 140,
  seed = 'stars',
  maxY = 1100,
}) => {
  const stars = useMemo(
    () =>
      new Array(count).fill(0).map((_, i) => ({
        x: random(`${seed}x${i}`) * 1080,
        y: random(`${seed}y${i}`) * maxY,
        r: 0.8 + random(`${seed}r${i}`) * 2.2,
        p: random(`${seed}p${i}`) * 6,
      })),
    [count, seed, maxY],
  );
  return (
    <svg width={1080} height={1920} style={{ position: 'absolute', inset: 0 }}>
      {stars.map((s, i) => (
        <circle key={i} cx={s.x} cy={s.y} r={s.r} fill="#dfe8ff" opacity={0.35 + 0.45 * (0.5 + 0.5 * Math.sin(frame * 0.25 + s.p))} />
      ))}
    </svg>
  );
};

/** 滿月 */
export const Moon: React.FC<{ x: number; y: number; r: number; glow?: number; tint?: string }> = ({ x, y, r, glow = 1, tint = COLORS.moon }) => (
  <div style={{ position: 'absolute', left: x - r, top: y - r, width: r * 2, height: r * 2 }}>
    <div
      style={{
        position: 'absolute',
        inset: -r * 1.6,
        borderRadius: '50%',
        background: `radial-gradient(circle, rgba(200,215,255,${0.38 * glow}) 0%, rgba(120,150,255,${0.16 * glow}) 35%, rgba(60,80,200,0) 70%)`,
      }}
    />
    <div
      style={{
        position: 'absolute',
        inset: 0,
        borderRadius: '50%',
        background: `radial-gradient(circle at 38% 35%, #ffffff 0%, ${tint} 45%, #c9cbd6 80%, #9fa3b8 100%)`,
        boxShadow: `0 0 ${r * 0.5}px rgba(230,235,255,${0.8 * glow})`,
        overflow: 'hidden',
      }}
    >
      {[
        [0.3, 0.55, 0.16],
        [0.62, 0.32, 0.12],
        [0.7, 0.66, 0.2],
        [0.45, 0.2, 0.08],
        [0.22, 0.3, 0.07],
        [0.52, 0.78, 0.1],
      ].map(([cx, cy, cr], i) => (
        <div
          key={i}
          style={{
            position: 'absolute',
            left: (cx - cr) * r * 2,
            top: (cy - cr) * r * 2,
            width: cr * r * 4,
            height: cr * r * 4,
            borderRadius: '50%',
            background: 'radial-gradient(circle at 60% 60%, rgba(120,125,150,0.45), rgba(120,125,150,0.1) 70%, rgba(0,0,0,0) 75%)',
          }}
        />
      ))}
    </div>
  </div>
);

/** 飄動的雲 */
export const Clouds: React.FC<{ frame: number; color?: string; opacity?: number; y?: number; seed?: string; speed?: number }> = ({
  frame,
  color = '20,30,70',
  opacity = 0.85,
  y = 300,
  seed = 'cloud',
  speed = 1.2,
}) => {
  const items = useMemo(
    () =>
      new Array(7).fill(0).map((_, i) => ({
        x: random(`${seed}x${i}`) * 1400 - 300,
        y: y + (random(`${seed}y${i}`) - 0.5) * 520,
        w: 420 + random(`${seed}w${i}`) * 520,
        h: 90 + random(`${seed}h${i}`) * 90,
        v: 0.5 + random(`${seed}v${i}`),
      })),
    [seed, y],
  );
  return (
    <AbsoluteFill style={{ opacity }}>
      {items.map((c, i) => (
        <div
          key={i}
          style={{
            position: 'absolute',
            left: c.x + frame * c.v * speed,
            top: c.y,
            width: c.w,
            height: c.h,
            borderRadius: '50%',
            background: `radial-gradient(ellipse, rgba(${color},0.95) 0%, rgba(${color},0.6) 45%, rgba(${color},0) 72%)`,
            filter: 'blur(10px)',
          }}
        />
      ))}
    </AbsoluteFill>
  );
};

type Tower = { x: number; w: number; h: number; roof: number; spire?: number };

const TOWERS: Tower[] = [
  { x: 120, w: 70, h: 330, roof: 120 },
  { x: 205, w: 54, h: 400, roof: 140, spire: 40 },
  { x: 290, w: 96, h: 470, roof: 170, spire: 50 },
  { x: 410, w: 70, h: 560, roof: 190, spire: 60 },
  { x: 468, w: 64, h: 700, roof: 230, spire: 90 },
  { x: 560, w: 80, h: 600, roof: 200, spire: 60 },
  { x: 650, w: 96, h: 480, roof: 170, spire: 40 },
  { x: 760, w: 58, h: 410, roof: 150, spire: 30 },
  { x: 830, w: 70, h: 330, roof: 120 },
];

/** 哥德式城堡（程式產生的剪影，窗戶會微微閃爍） */
export const Castle: React.FC<{ frame: number; width?: number; color?: string; windowGlow?: number; style?: React.CSSProperties }> = ({
  frame,
  width = 1000,
  color = '#060816',
  windowGlow = 1,
  style,
}) => {
  const base = 900;
  const windows = useMemo(() => {
    const out: { x: number; y: number; w: number; h: number; s: number }[] = [];
    TOWERS.forEach((t, ti) => {
      const rows = Math.floor(t.h / 110);
      for (let r = 0; r < rows; r++) {
        if (hash(ti * 13 + r * 7) < 0.45) continue;
        const ww = Math.max(10, t.w * 0.2);
        out.push({ x: t.x + t.w / 2 - ww / 2, y: base - t.h + 70 + r * 100, w: ww, h: ww * 2, s: ti * 10 + r });
      }
    });
    // 主建築窗戶
    for (let i = 0; i < 9; i++) {
      if (hash(i * 3.3) < 0.35) continue;
      out.push({ x: 300 + i * 52, y: base - 210 + (i % 2) * 40, w: 14, h: 28, s: 200 + i });
    }
    return out;
  }, []);
  return (
    <svg viewBox="0 0 1000 1000" width={width} height={width} style={{ overflow: 'visible', ...style }}>
      <defs>
        <filter id="winGlow" x="-200%" y="-200%" width="500%" height="500%">
          <feGaussianBlur stdDeviation={5} result="b" />
          <feMerge>
            <feMergeNode in="b" />
            <feMergeNode in="b" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>
      <g fill={color}>
        {/* 山丘 */}
        <path d="M-200 1000 Q100 870 300 880 Q500 840 700 880 Q900 870 1200 1000 Z" />
        {/* 主牆 */}
        <rect x={150} y={base - 260} width={700} height={300} />
        {/* 城垛 */}
        {new Array(24).fill(0).map((_, i) => (
          <rect key={i} x={150 + i * 29.5} y={base - 282} width={16} height={24} />
        ))}
        {TOWERS.map((t, i) => (
          <g key={i}>
            <rect x={t.x} y={base - t.h} width={t.w} height={t.h} />
            <path d={`M${t.x - 10} ${base - t.h} L${t.x + t.w / 2} ${base - t.h - t.roof} L${t.x + t.w + 10} ${base - t.h} Z`} />
            {t.spire ? <rect x={t.x + t.w / 2 - 2} y={base - t.h - t.roof - t.spire} width={4} height={t.spire} /> : null}
          </g>
        ))}
        {/* 大門拱 */}
        <path d={`M455 ${base + 40} L455 ${base - 60} Q500 ${base - 120} 545 ${base - 60} L545 ${base + 40} Z`} fill="#1a0f05" />
      </g>
      <g filter="url(#winGlow)" opacity={windowGlow}>
        {windows.map((w, i) => {
          const flick = 0.65 + 0.35 * (0.5 + 0.5 * noise1(frame * 0.3, w.s));
          return <rect key={i} x={w.x} y={w.y} width={w.w} height={w.h} rx={w.w / 2} fill="#ffb347" opacity={flick} />;
        })}
        <path d={`M465 ${base + 40} L465 ${base - 55} Q500 ${base - 105} 535 ${base - 55} L535 ${base + 40} Z`} fill="#ff9a2e" opacity={0.75} />
      </g>
    </svg>
  );
};

type Branch = { d: string; w: number };

const growTree = (seed: number, x: number, y: number, len: number, ang: number, depth: number, out: Branch[]) => {
  if (depth <= 0 || len < 8) return;
  const x2 = x + Math.cos(ang) * len;
  const y2 = y + Math.sin(ang) * len;
  const bend = (hash(seed) - 0.5) * len * 0.4;
  out.push({ d: `M${x} ${y} Q${(x + x2) / 2 + bend} ${(y + y2) / 2} ${x2} ${y2}`, w: Math.max(1.2, depth * 2.6) });
  const n = depth > 5 ? 2 : 2 + Math.floor(hash(seed + 1) * 2);
  for (let i = 0; i < n; i++) {
    const da = (hash(seed + i * 7 + 3) - 0.5) * 1.3 + (i - (n - 1) / 2) * 0.5;
    growTree(seed * 1.7 + i * 31 + 11, x2, y2, len * (0.62 + hash(seed + i) * 0.2), ang + da, depth - 1, out);
  }
};

/** 枯樹剪影（畫面左右兩側框景） */
export const DeadTree: React.FC<{ seed: number; flip?: boolean; style?: React.CSSProperties; color?: string; sway?: number }> = ({
  seed,
  flip,
  style,
  color = '#020309',
  sway = 0,
}) => {
  const branches = useMemo(() => {
    const out: Branch[] = [];
    growTree(seed, 120, 1000, 260, -Math.PI / 2 + 0.25, 7, out);
    return out;
  }, [seed]);
  return (
    <svg
      viewBox="-300 0 800 1000"
      style={{ position: 'absolute', overflow: 'visible', transform: `${flip ? 'scaleX(-1)' : ''} rotate(${sway}deg)`, transformOrigin: '50% 100%', ...style }}
    >
      <g stroke={color} fill="none" strokeLinecap="round">
        {branches.map((b, i) => (
          <path key={i} d={b.d} strokeWidth={b.w} />
        ))}
      </g>
    </svg>
  );
};

/** 低空薄霧 */
export const Fog: React.FC<{ frame: number; color?: string; top?: number; opacity?: number; seed?: string }> = ({
  frame,
  color = '150,170,230',
  top = 1300,
  opacity = 0.5,
  seed = 'fog',
}) => {
  const items = useMemo(
    () =>
      new Array(9).fill(0).map((_, i) => ({
        x: random(`${seed}x${i}`) * 1500 - 400,
        y: top + random(`${seed}y${i}`) * 520,
        w: 600 + random(`${seed}w${i}`) * 700,
        h: 160 + random(`${seed}h${i}`) * 160,
        v: (random(`${seed}v${i}`) - 0.3) * 3,
      })),
    [seed, top],
  );
  return (
    <AbsoluteFill style={{ opacity, mixBlendMode: 'screen' }}>
      {items.map((f, i) => (
        <div
          key={i}
          style={{
            position: 'absolute',
            left: f.x + frame * f.v,
            top: f.y,
            width: f.w,
            height: f.h,
            borderRadius: '50%',
            background: `radial-gradient(ellipse, rgba(${color},0.55) 0%, rgba(${color},0.2) 50%, rgba(${color},0) 72%)`,
            filter: 'blur(16px)',
          }}
        />
      ))}
    </AbsoluteFill>
  );
};

/** 閃電：以中點位移法產生 */
export const Lightning: React.FC<{ seed: number; x: number; y: number; length: number; opacity: number; color?: string }> = ({
  seed,
  x,
  y,
  length,
  opacity,
  color = '#dfe6ff',
}) => {
  const d = useMemo(() => {
    let pts: [number, number][] = [
      [x, y],
      [x + (hash(seed) - 0.5) * 200, y + length],
    ];
    for (let it = 0; it < 6; it++) {
      const np: [number, number][] = [];
      for (let i = 0; i < pts.length - 1; i++) {
        const [ax, ay] = pts[i];
        const [bx, by] = pts[i + 1];
        const off = (hash(seed + it * 17 + i * 3.1) - 0.5) * (length / Math.pow(2, it)) * 0.45;
        np.push([ax, ay], [(ax + bx) / 2 + off, (ay + by) / 2]);
      }
      np.push(pts[pts.length - 1]);
      pts = np;
    }
    return pts.map((p, i) => `${i ? 'L' : 'M'}${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join(' ');
  }, [seed, x, y, length]);
  if (opacity <= 0.01) return null;
  return (
    <svg width={1080} height={1920} style={{ position: 'absolute', inset: 0, opacity }}>
      <defs>
        <filter id={`bolt${seed}`} x="-50%" y="-10%" width="200%" height="120%">
          <feGaussianBlur stdDeviation={8} result="b" />
          <feMerge>
            <feMergeNode in="b" />
            <feMergeNode in="b" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>
      <path d={d} stroke={color} strokeWidth={4} fill="none" filter={`url(#bolt${seed})`} />
    </svg>
  );
};

/** 蝙蝠群 */
export const Bats: React.FC<{ frame: number; count?: number; seed?: string; color?: string }> = ({ frame, count = 6, seed = 'bat', color = '#05060c' }) => {
  const bats = useMemo(
    () =>
      new Array(count).fill(0).map((_, i) => ({
        x0: -100 - random(`${seed}x${i}`) * 400,
        y0: 250 + random(`${seed}y${i}`) * 500,
        vx: 9 + random(`${seed}v${i}`) * 9,
        vy: -2 - random(`${seed}vy${i}`) * 3,
        s: 0.5 + random(`${seed}s${i}`) * 0.7,
        p: random(`${seed}p${i}`) * 6,
      })),
    [count, seed],
  );
  return (
    <svg width={1080} height={1920} style={{ position: 'absolute', inset: 0 }}>
      {bats.map((b, i) => {
        const flap = Math.sin(frame * 1.6 + b.p);
        const x = b.x0 + frame * b.vx;
        const y = b.y0 + frame * b.vy + Math.sin(frame * 0.3 + b.p) * 10;
        return (
          <g key={i} transform={`translate(${x} ${y}) scale(${b.s} ${b.s})`} fill={color}>
            <path
              d={`M0 0 Q-20 ${-18 * flap} -46 ${-10 * flap} Q-36 ${2} -26 ${4 - 4 * flap} Q-16 2 -8 8 L0 4 L8 8 Q16 2 26 ${4 - 4 * flap} Q36 2 46 ${-10 * flap} Q20 ${-18 * flap} 0 0 Z`}
            />
            <ellipse cx={0} cy={4} rx={6} ry={8} />
          </g>
        );
      })}
    </svg>
  );
};

/** 上升的火星 / 粒子 */
export const Embers: React.FC<{
  frame: number;
  count?: number;
  seed?: string;
  colors?: string[];
  speed?: number;
  area?: { x: number; y: number; w: number; h: number };
  size?: number;
}> = ({ frame, count = 60, seed = 'ember', colors = ['#ffb347', '#ff6a1a', '#ffd36b'], speed = 1, area = { x: 0, y: 0, w: 1080, h: 1920 }, size = 1 }) => {
  const ps = useMemo(
    () =>
      new Array(count).fill(0).map((_, i) => ({
        x: random(`${seed}x${i}`),
        y: random(`${seed}y${i}`),
        v: 0.4 + random(`${seed}v${i}`),
        r: (1.5 + random(`${seed}r${i}`) * 3.5) * size,
        c: colors[Math.floor(random(`${seed}c${i}`) * colors.length)],
        p: random(`${seed}p${i}`) * 6,
      })),
    [count, seed, colors, size],
  );
  return (
    <svg width={1080} height={1920} style={{ position: 'absolute', inset: 0 }}>
      <defs>
        <filter id={`emb-${seed}`}>
          <feGaussianBlur stdDeviation={2} result="b" />
          <feMerge>
            <feMergeNode in="b" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>
      <g filter={`url(#emb-${seed})`}>
        {ps.map((p, i) => {
          const yy = area.y + ((p.y * area.h - frame * p.v * 6 * speed) % area.h + area.h) % area.h;
          const xx = area.x + p.x * area.w + Math.sin(frame * 0.08 + p.p) * 18;
          return <circle key={i} cx={xx} cy={yy} r={p.r} fill={p.c} opacity={0.5 + 0.5 * Math.sin(frame * 0.3 + p.p)} />;
        })}
      </g>
    </svg>
  );
};

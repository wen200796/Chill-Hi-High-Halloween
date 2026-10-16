import React from 'react';
import { AbsoluteFill } from 'remotion';
import { FONTS } from '../config/theme';

/** 漫畫元素：說明框、音效字、集中線、網點 */
export const INK = '#0b0709';

/** 漫畫旁白說明框（取代電影字幕） */
export const CaptionBox: React.FC<{
  text: string;
  opacity: number;
  /** 0 → 1：從斜角彈入 */
  enter?: number;
  x?: number;
  y: number;
  size?: number;
  rotate?: number;
  bg?: string;
  color?: string;
  align?: 'left' | 'center';
  style?: React.CSSProperties;
}> = ({ text, opacity, enter = 1, x, y, size = 60, rotate = -2, bg = '#ffe94a', color = INK, align = 'center', style }) => {
  if (opacity <= 0.001) return null;
  const s = 0.6 + 0.4 * enter;
  return (
    <div
      style={{
        position: 'absolute',
        left: align === 'center' ? 0 : x,
        right: align === 'center' ? 0 : undefined,
        top: y,
        display: 'flex',
        justifyContent: align === 'center' ? 'center' : 'flex-start',
        opacity,
        ...style,
      }}
    >
      <div
        style={{
          padding: `${size * 0.22}px ${size * 0.45}px`,
          background: bg,
          border: `${Math.max(4, size * 0.09)}px solid ${INK}`,
          boxShadow: `${size * 0.16}px ${size * 0.16}px 0 ${INK}`,
          transform: `rotate(${rotate}deg) scale(${s})`,
          fontFamily: FONTS.sans,
          fontWeight: 900,
          fontSize: size,
          lineHeight: 1.2,
          color,
          letterSpacing: '0.05em',
          whiteSpace: 'pre-line',
          textAlign: 'center',
        }}
      >
        {text}
      </div>
    </div>
  );
};

/** 漫畫音效字（白字黑框 + 位移陰影） */
export const SfxWord: React.FC<{
  text: string;
  x: number;
  y: number;
  size?: number;
  rotate?: number;
  /** 0 → 1：放大彈出 */
  pop: number;
  fill?: string;
  opacity?: number;
}> = ({ text, x, y, size = 130, rotate = -10, pop, fill = '#ffffff', opacity = 1 }) => {
  if (pop <= 0.001 || opacity <= 0.001) return null;
  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: y,
        transform: `translate(-50%, -50%) rotate(${rotate}deg) scale(${0.3 + 0.7 * pop})`,
        fontFamily: FONTS.sans,
        fontWeight: 900,
        fontSize: size,
        lineHeight: 1,
        color: fill,
        WebkitTextStroke: `${size * 0.09}px ${INK}`,
        paintOrder: 'stroke fill',
        textShadow: `${size * 0.07}px ${size * 0.07}px 0 ${INK}`,
        whiteSpace: 'nowrap',
        opacity,
        letterSpacing: '0.02em',
      }}
    >
      {text}
    </div>
  );
};

/** 集中線 */
export const SpeedLines: React.FC<{ cx?: number; cy?: number; r0?: number; count?: number; color?: string; opacity?: number; seed?: number }> = ({
  cx = 540,
  cy = 760,
  r0 = 480,
  count = 90,
  color = INK,
  opacity = 0.85,
  seed = 0,
}) => {
  const lines = [];
  for (let i = 0; i < count; i++) {
    const a = (i / count) * Math.PI * 2 + ((i * 7 + seed) % 5) * 0.004;
    const w = 0.005 + (((i + seed) * 37) % 11) * 0.0016;
    const r = r0 + (((i + seed) * 53) % 7) * 34;
    const p = (rr: number, aa: number) => `${(cx + Math.cos(aa) * rr).toFixed(1)} ${(cy + Math.sin(aa) * rr).toFixed(1)}`;
    lines.push(<path key={i} d={`M${p(r, a)} L${p(2400, a - w)} L${p(2400, a + w)} Z`} fill={color} />);
  }
  return (
    <svg width={1080} height={1920} style={{ position: 'absolute', inset: 0, opacity }}>
      {lines}
    </svg>
  );
};

/** 網點底紋（Ben-Day dots） */
export const Halftone: React.FC<{ color?: string; size?: number; opacity?: number; blend?: React.CSSProperties['mixBlendMode']; id: string }> = ({
  color = INK,
  size = 14,
  opacity = 0.15,
  blend = 'multiply',
  id,
}) => (
  <svg width={1080} height={1920} style={{ position: 'absolute', inset: 0, opacity, mixBlendMode: blend, pointerEvents: 'none' }}>
    <defs>
      <pattern id={id} width={size} height={size} patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
        <circle cx={size / 2} cy={size / 2} r={size * 0.28} fill={color} />
      </pattern>
    </defs>
    <rect width={1080} height={1920} fill={`url(#${id})`} />
  </svg>
);

/** 漫畫爆炸光背景 */
export const ComicBurst: React.FC<{ c1: string; c2: string; c3: string; id: string; dots?: string }> = ({ c1, c2, c3, id, dots = '#e8463a' }) => (
  <AbsoluteFill style={{ background: `radial-gradient(ellipse 70% 55% at 50% 38%, ${c1} 0%, ${c2} 45%, ${c3} 100%)` }}>
    <Halftone id={id} color={dots} size={18} opacity={0.35} blend="normal" />
  </AbsoluteFill>
);

/** 漫畫標題字：漸層填色 + 粗黑外框 + 位移陰影 */
export const ComicTitle: React.FC<{
  text: string;
  y: number;
  size?: number;
  opacity: number;
  scale?: number;
  rotate?: number;
  gradient?: string;
}> = ({ text, y, size = 92, opacity, scale = 1, rotate = -3, gradient = 'linear-gradient(180deg, #fff3b0 0%, #ffd23f 45%, #ff8a1f 100%)' }) => {
  if (opacity <= 0.001) return null;
  const common: React.CSSProperties = {
    position: 'absolute',
    inset: 0,
    fontFamily: FONTS.sans,
    fontWeight: 900,
    fontSize: size,
    lineHeight: 1.15,
    letterSpacing: '0.02em',
    textAlign: 'center',
    whiteSpace: 'nowrap',
  };
  return (
    <div style={{ position: 'absolute', left: 0, right: 0, top: y, height: size * 1.3, opacity, transform: `rotate(${rotate}deg) scale(${scale})` }}>
      <div style={{ ...common, color: INK, WebkitTextStroke: `${size * 0.2}px ${INK}`, transform: `translate(${size * 0.08}px, ${size * 0.08}px)` }}>{text}</div>
      <div style={{ ...common, color: INK, WebkitTextStroke: `${size * 0.2}px ${INK}` }}>{text}</div>
      <div style={{ ...common, background: gradient, WebkitBackgroundClip: 'text', color: 'transparent' }}>{text}</div>
    </div>
  );
};

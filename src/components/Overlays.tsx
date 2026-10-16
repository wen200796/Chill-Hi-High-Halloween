import React from 'react';
import { AbsoluteFill, Img, staticFile } from 'remotion';
import { FONTS } from '../config/theme';
import { hash } from '../util';

/** 鏡頭：推近、位移、旋轉、震動 */
export const Camera: React.FC<{
  scale?: number;
  x?: number;
  y?: number;
  rotate?: number;
  origin?: string;
  children: React.ReactNode;
  style?: React.CSSProperties;
}> = ({ scale = 1, x = 0, y = 0, rotate = 0, origin = '50% 50%', children, style }) => (
  <AbsoluteFill
    style={{
      transform: `translate(${x}px, ${y}px) scale(${scale}) rotate(${rotate}deg)`,
      transformOrigin: origin,
      ...style,
    }}
  >
    {children}
  </AbsoluteFill>
);

/** 底片顆粒 */
export const Grain: React.FC<{ frame: number; opacity?: number }> = ({ frame, opacity = 0.07 }) => (
  <AbsoluteFill style={{ overflow: 'hidden', opacity, mixBlendMode: 'overlay', pointerEvents: 'none' }}>
    <div
      style={{
        position: 'absolute',
        inset: -512,
        backgroundImage: `url(${staticFile('assets/grain.png')})`,
        backgroundSize: '512px 512px',
        transform: `translate(${Math.floor(hash(frame) * 512)}px, ${Math.floor(hash(frame + 99) * 512)}px)`,
      }}
    />
  </AbsoluteFill>
);

/** 暗角 */
export const Vignette: React.FC<{ strength?: number }> = ({ strength = 0.75 }) => (
  <AbsoluteFill
    style={{
      background: `radial-gradient(ellipse 75% 60% at 50% 48%, rgba(0,0,0,0) 45%, rgba(0,0,0,${strength}) 100%)`,
      pointerEvents: 'none',
    }}
  />
);

/** 閃光 */
export const Flash: React.FC<{ opacity: number; color?: string }> = ({ opacity, color = '#ffffff' }) =>
  opacity > 0.001 ? <AbsoluteFill style={{ background: color, opacity, pointerEvents: 'none' }} /> : null;

/** 電影感字幕 */
export const Subtitle: React.FC<{
  text: string;
  opacity: number;
  /** 0 → 1，用於字距收合與模糊淡入 */
  enter?: number;
  y?: number;
  size?: number;
  color?: string;
  glow?: string;
  font?: 'cinematic' | 'sans';
  weight?: number;
  letterSpacing?: number;
  style?: React.CSSProperties;
}> = ({
  text,
  opacity,
  enter = 1,
  y = 1330,
  size = 76,
  color = '#f4f2ff',
  glow = 'rgba(140,150,255,0.55)',
  font = 'cinematic',
  weight = 900,
  letterSpacing = 0.08,
  style,
}) => {
  if (opacity <= 0.001) return null;
  return (
    <div
      style={{
        position: 'absolute',
        left: 60,
        right: 60,
        top: y,
        textAlign: 'center',
        fontFamily: FONTS[font],
        fontWeight: weight,
        fontSize: size,
        lineHeight: 1.3,
        color,
        opacity,
        letterSpacing: `${letterSpacing + (1 - enter) * 0.12}em`,
        filter: enter < 1 ? `blur(${(1 - enter) * 10}px)` : undefined,
        textShadow: `0 0 24px ${glow}, 0 4px 18px rgba(0,0,0,0.9), 0 0 2px rgba(0,0,0,0.9)`,
        whiteSpace: 'pre-line',
        ...style,
      }}
    >
      {text}
    </div>
  );
};

/** 分會 Logo：直接使用原始檔案，以圓形裁切去除白底 */
export const Logo: React.FC<{ src: string; size: number; style?: React.CSSProperties }> = ({ src, size, style }) => {
  // 原始檔 1920×1080，圓形徽章中心約 (959.5, 416)、半徑約 283
  const scale = size / 566;
  return (
    <div
      style={{
        width: size,
        height: size,
        borderRadius: '50%',
        overflow: 'hidden',
        position: 'relative',
        ...style,
      }}
    >
      <Img
        src={staticFile(src)}
        style={{
          position: 'absolute',
          width: 1920 * scale,
          height: 1080 * scale,
          left: -(959.5 - 283) * scale,
          top: -(416 - 283) * scale,
          maxWidth: 'none',
        }}
      />
    </div>
  );
};

import React from 'react';
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from 'remotion';
import { Bats, Embers } from '../components/Night';
import { Camera, Flash, Logo, Subtitle, Vignette } from '../components/Overlays';
import { Stage } from '../components/Stage';
import { BRAND, EVENT } from '../config/event';
import { SUBTITLES } from '../config/subtitles';
import { COLORS, FONTS } from '../config/theme';
import { CUES, SCENES, sec } from '../config/video';
import { clamp, noise1, progress } from '../util';

/** 南瓜燈 */
const Pumpkin: React.FC<{ x: number; y: number; size: number; frame: number; seed: number; flip?: boolean }> = ({ x, y, size, frame, seed, flip }) => {
  const flick = 0.75 + 0.25 * noise1(frame * 0.35, seed);
  return (
    <svg
      viewBox="0 0 200 180"
      width={size}
      height={size * 0.9}
      style={{ position: 'absolute', left: x - size / 2, top: y - size * 0.45, overflow: 'visible', transform: flip ? 'scaleX(-1)' : undefined }}
    >
      <defs>
        <radialGradient id={`pk${seed}`} cx="0.45" cy="0.4" r="0.7">
          <stop offset="0" stopColor="#ff9a2e" />
          <stop offset="0.7" stopColor="#d4560c" />
          <stop offset="1" stopColor="#6a2204" />
        </radialGradient>
        <filter id={`pkg${seed}`} x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation={6} result="b" />
          <feMerge>
            <feMergeNode in="b" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>
      <ellipse cx={100} cy={100} rx={110} ry={60} fill="#ff7a1a" opacity={0.25 * flick} filter={`url(#pkg${seed})`} />
      <path d="M96 30 Q92 10 104 0 L110 4 Q102 14 106 30 Z" fill="#3b4a1a" />
      {[-56, -28, 0, 28, 56].map((dx, i) => (
        <ellipse key={i} cx={100 + dx * 0.9} cy={100} rx={46 - Math.abs(dx) * 0.25} ry={72} fill={`url(#pk${seed})`} stroke="#5a1d04" strokeWidth={2} />
      ))}
      <g fill="#ffe08a" opacity={flick} filter={`url(#pkg${seed})`}>
        <path d="M58 80 L80 62 L88 90 Z" />
        <path d="M142 80 L120 62 L112 90 Z" />
        <path d="M100 96 L92 112 L108 112 Z" />
        <path d="M50 120 Q100 168 150 120 L136 124 L128 138 L118 128 L106 142 L96 128 L84 140 L74 126 L64 132 Z" />
      </g>
    </svg>
  );
};

const InfoRow: React.FC<{ icon: React.ReactNode; children: React.ReactNode; size: number; color?: string; opacity: number; weight?: number }> = ({
  icon,
  children,
  size,
  color = '#fff',
  opacity,
  weight = 700,
}) => (
  <div
    style={{
      display: 'flex',
      alignItems: 'center',
      gap: 22,
      opacity,
      transform: `translateY(${(1 - opacity) * 24}px)`,
      fontFamily: FONTS.sans,
      fontWeight: weight,
      fontSize: size,
      color,
      lineHeight: 1.25,
      textShadow: '0 2px 8px rgba(0,0,0,0.8)',
    }}
  >
    <div style={{ width: 54, display: 'flex', justifyContent: 'center', flexShrink: 0 }}>{icon}</div>
    <div>{children}</div>
  </div>
);

const IconCalendar = () => (
  <svg width={46} height={46} viewBox="0 0 24 24" fill="none" stroke={COLORS.orange} strokeWidth={2.2} strokeLinecap="round">
    <rect x={3} y={5} width={18} height={16} rx={2} />
    <path d="M3 10h18M8 3v4M16 3v4" />
  </svg>
);
const IconClock = () => (
  <svg width={46} height={46} viewBox="0 0 24 24" fill="none" stroke={COLORS.orange} strokeWidth={2.2} strokeLinecap="round">
    <circle cx={12} cy={12} r={9} />
    <path d="M12 7v5l3 2" />
  </svg>
);
const IconPin = () => (
  <svg width={46} height={46} viewBox="0 0 24 24" fill="none" stroke={COLORS.orange} strokeWidth={2.2} strokeLinecap="round">
    <path d="M12 22s7-6.5 7-12a7 7 0 1 0-14 0c0 5.5 7 12 7 12z" />
    <circle cx={12} cy={10} r={2.5} />
  </svg>
);

/** Scene 7｜英雄的另一種樣子 → 活動片尾 */
export const Scene7Finale: React.FC = () => {
  const frame = useCurrentFrame();
  const len = sec(SCENES.finale.end - SCENES.finale.start);
  const rel = (s: number) => sec(s - SCENES.finale.start);
  const spot = rel(CUES.finaleSpotlight);
  const cardStart = rel(CUES.endCardStart);
  const cardDone = rel(CUES.endCardComplete);

  // 普通人走向麥克風
  const walkP = progress(frame, 0, spot + 2, Easing.out(Easing.quad));
  const light = interpolate(frame, [0, spot, spot + 6], [0.25, 0.4, 1], clamp);
  const warm = interpolate(frame, [spot - 2, spot + 10], [0, 1], clamp);
  // 鏡頭上移，片尾由下方形成
  const camP = progress(frame, cardStart - 4, cardDone - 2, Easing.inOut(Easing.cubic));
  const stageScale = interpolate(camP, [0, 1], [1, 0.6]);
  const stageY = interpolate(camP, [0, 1], [0, -40]);
  const panel = progress(frame, cardStart - 2, cardStart + 10, Easing.out(Easing.cubic));
  const step = (i: number) => progress(frame, cardStart + 2 + i * 2, cardStart + 8 + i * 2, Easing.out(Easing.cubic));
  const themeIn = progress(frame, 2, 10, Easing.out(Easing.cubic));
  const sparkle = interpolate(frame, [cardDone - 1, cardDone, cardDone + 6], [0, 0.3, 0], clamp);

  return (
    <AbsoluteFill style={{ background: '#08040e' }}>
      {/* 舞台與背影：從深紫轉為暖金 */}
      <Camera
        scale={stageScale}
        y={stageY}
        origin="50% 0%"
        style={{
          WebkitMaskImage: `linear-gradient(90deg, rgba(0,0,0,${1 - camP}) 0%, #000 22%, #000 78%, rgba(0,0,0,${1 - camP}) 100%)`,
        }}
      >
        <Stage frame={frame + 30} light={light} warm={warm} person={{ progress: walkP, walk: walkP * 2.2 }} />
        <AbsoluteFill style={{ background: 'rgba(70,20,120,0.45)', mixBlendMode: 'color', opacity: 1 - warm }} />
        <AbsoluteFill style={{ background: 'radial-gradient(ellipse 60% 45% at 50% 45%, rgba(255,190,90,0.22), rgba(0,0,0,0) 70%)', opacity: warm }} />
      </Camera>
      {/* 萬聖節片尾主視覺面板 */}
      <AbsoluteFill
        style={{
          opacity: panel,
          background:
            'linear-gradient(180deg, rgba(10,3,20,0) 0%, rgba(10,3,20,0) 38%, rgba(26,6,44,0.92) 46%, #2a0b4a 62%, #3a0f52 78%, #5a1838 92%, #8a2f12 100%)',
        }}
      />
      <AbsoluteFill style={{ opacity: panel }}>
        <Bats frame={frame + 40} count={5} seed="fb" color="#12051c" />
        <Embers frame={frame} count={40} seed="femb" area={{ x: 0, y: 900, w: 1080, h: 1020 }} speed={0.7} />
        <Pumpkin x={130} y={1770} size={230} frame={frame} seed={1} />
        <Pumpkin x={960} y={1790} size={190} frame={frame} seed={2} flip />
        <Pumpkin x={300} y={1840} size={120} frame={frame} seed={3} />
      </AbsoluteFill>

      {/* 主題字幕（全段保留在畫面上方） */}
      <Subtitle
        text={SUBTITLES.finale.theme}
        opacity={themeIn}
        enter={themeIn}
        y={236}
        size={72}
        color={COLORS.warmGold}
        glow="rgba(255,160,60,0.7)"
        letterSpacing={0.04}
      />

      {/* 品牌 */}
      <div
        style={{
          position: 'absolute',
          left: 70,
          right: 70,
          top: 820,
          display: 'flex',
          alignItems: 'center',
          gap: 34,
          opacity: step(0),
          transform: `translateY(${(1 - step(0)) * 40}px)`,
        }}
      >
        <Logo src={BRAND.logo} size={200} style={{ boxShadow: '0 0 0 5px rgba(255,201,74,0.85), 0 0 40px rgba(255,140,40,0.6)', flexShrink: 0 }} />
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <div style={{ fontFamily: FONTS.sans, fontWeight: 900, fontSize: 76, color: '#fff', lineHeight: 1.05, textShadow: '0 3px 12px rgba(0,0,0,0.8)' }}>
            {BRAND.titleLines.brand}
          </div>
          <div
            style={{
              fontFamily: FONTS.cinematic,
              fontWeight: 900,
              fontSize: 92,
              lineHeight: 1.05,
              letterSpacing: '0.02em',
              background: 'linear-gradient(180deg, #ffd36b 0%, #ff8a1f 55%, #e2470e 100%)',
              WebkitBackgroundClip: 'text',
              color: 'transparent',
              filter: 'drop-shadow(0 3px 10px rgba(0,0,0,0.7))',
            }}
          >
            {BRAND.titleLines.halloween.toUpperCase()}
          </div>
          <div style={{ fontFamily: FONTS.sans, fontWeight: 700, fontSize: 42, color: '#f3e8ff', letterSpacing: '0.24em', lineHeight: 1.2 }}>
            {BRAND.titleLines.toastmasters.toUpperCase()}
          </div>
        </div>
      </div>

      {/* 行動呼籲 */}
      <div
        style={{
          position: 'absolute',
          left: 60,
          right: 60,
          top: 1080,
          textAlign: 'center',
          fontFamily: FONTS.sans,
          fontWeight: 900,
          fontSize: 62,
          lineHeight: 1.3,
          color: '#fff',
          opacity: step(1),
          transform: `translateY(${(1 - step(1)) * 30}px)`,
          textShadow: '0 0 20px rgba(255,120,40,0.45), 0 3px 10px rgba(0,0,0,0.85)',
        }}
      >
        {SUBTITLES.finale.question[0]}
        <br />
        <span style={{ color: COLORS.gold }}>{SUBTITLES.finale.question[1]}</span>
      </div>

      {/* 活動資訊：日期、時間、地點、地址分行呈現 */}
      <div
        style={{
          position: 'absolute',
          left: 110,
          right: 70,
          top: 1290,
          display: 'flex',
          flexDirection: 'column',
          gap: 10,
          padding: '26px 30px',
          borderRadius: 24,
          background: `rgba(12,4,24,${0.55 * step(2)})`,
          border: `2px solid rgba(255,140,40,${0.45 * step(2)})`,
          marginLeft: -40,
        }}
      >
        <InfoRow icon={<IconCalendar />} size={54} opacity={step(2)}>
          {EVENT.date}
        </InfoRow>
        <InfoRow icon={<IconClock />} size={54} opacity={step(3)}>
          {EVENT.time}
        </InfoRow>
        <InfoRow icon={<IconPin />} size={46} opacity={step(4)}>
          {EVENT.venue}
        </InfoRow>
        <InfoRow icon={<span />} size={34} weight={500} color="#e6dcf5" opacity={step(5)}>
          {EVENT.address}
        </InfoRow>
      </div>

      <Vignette strength={0.45} />
      <Flash opacity={sparkle} color="#ffe2b0" />
      <Flash opacity={interpolate(frame, [0, 3], [0.5, 0], clamp)} color="#000" />
    </AbsoluteFill>
  );
};

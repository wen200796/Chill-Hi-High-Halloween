import React, { useMemo } from 'react';
import { AbsoluteFill, Easing, interpolate, random, useCurrentFrame } from 'remotion';
import { Figure } from '../components/Figure';
import { Embers, Fog } from '../components/Night';
import { Camera, Flash, Subtitle, Vignette } from '../components/Overlays';
import { getCharacter } from '../config/characters';
import { SUBTITLES } from '../config/subtitles';
import { ROSTER, SCENES, sec } from '../config/video';
import { clamp, fadeInOut, hash, progress } from '../util';

const CX = 540;
const CY = 700;

/** 能量電弧環（每 2 幀重新產生鋸齒形狀，模擬電流閃動） */
const Arcs: React.FC<{ frame: number; open: number }> = ({ frame, open }) => {
  const bucket = Math.floor(frame / 2);
  const arcs = useMemo(() => {
    return new Array(16).fill(0).map((_, i) => {
      const rx = 300 + hash(i * 3.7) * 120;
      const ry = 420 + hash(i * 5.1) * 140;
      const a0 = hash(i * 9.2 + bucket * 1.3) * Math.PI * 2;
      const span = 0.9 + hash(i * 1.9 + bucket) * 1.8;
      const steps = 22;
      let d = '';
      for (let s = 0; s <= steps; s++) {
        const a = a0 + (span * s) / steps;
        const j = 1 + (hash(i * 31 + s * 7 + bucket * 13) - 0.5) * 0.16;
        const x = CX + Math.cos(a) * rx * j;
        const y = CY + Math.sin(a) * ry * j;
        d += `${s ? 'L' : 'M'}${x.toFixed(1)} ${y.toFixed(1)} `;
      }
      return { d, w: 2 + hash(i * 4.4 + bucket) * 4, c: i % 3 === 0 ? '#ffffff' : i % 3 === 1 ? '#d59bff' : '#ff6ef0' };
    });
  }, [bucket]);
  return (
    <svg width={1080} height={1920} style={{ position: 'absolute', inset: 0, transform: `scale(${open})`, transformOrigin: `${CX}px ${CY}px` }}>
      <defs>
        <filter id="arcGlow" x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur stdDeviation={7} result="b" />
          <feMerge>
            <feMergeNode in="b" />
            <feMergeNode in="b" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>
      <g filter="url(#arcGlow)" fill="none" strokeLinecap="round">
        {arcs.map((a, i) => (
          <path key={i} d={a.d} stroke={a.c} strokeWidth={a.w} />
        ))}
      </g>
    </svg>
  );
};

/** 向外擴散的能量粒子 */
const Burst: React.FC<{ frame: number }> = ({ frame }) => {
  const ps = useMemo(
    () =>
      new Array(90).fill(0).map((_, i) => ({
        a: random(`ba${i}`) * Math.PI * 2,
        v: 6 + random(`bv${i}`) * 14,
        o: random(`bo${i}`) * 60,
        r: 1.5 + random(`br${i}`) * 3.5,
      })),
    [],
  );
  return (
    <svg width={1080} height={1920} style={{ position: 'absolute', inset: 0 }}>
      {ps.map((p, i) => {
        const d = ((p.o + frame * p.v) % 900) + 120;
        const x = CX + Math.cos(p.a + d * 0.0015) * d * 0.85;
        const y = CY + Math.sin(p.a + d * 0.0015) * d * 1.05;
        return <circle key={i} cx={x} cy={y} r={p.r} fill={i % 2 ? '#f1d1ff' : '#b56bff'} opacity={Math.max(0, 1 - d / 1000)} />;
      })}
    </svg>
  );
};

/** Scene 2｜次元裂縫：紫色傳送門、背光英雄剪影、粒子、快速推近 */
export const Scene2Portal: React.FC = () => {
  const frame = useCurrentFrame();
  const len = sec(SCENES.portal.end - SCENES.portal.start);
  const t = frame / 30;
  const push = interpolate(frame, [0, len], [1.0, 1.42], { ...clamp, easing: Easing.in(Easing.cubic) });
  const open = interpolate(frame, [0, 10], [0.35, 1], { ...clamp, easing: Easing.out(Easing.back(1.6)) });
  const sub = SUBTITLES.portal;
  const subOpacity = fadeInOut(frame, sec(sub.from), sec(sub.from) + 6, len - 6, len);
  const enter = progress(frame, sec(sub.from), sec(sub.from) + 12, Easing.out(Easing.cubic));
  const lineup = ROSTER.map(getCharacter);
  const rot = frame * 2.2;

  return (
    <AbsoluteFill style={{ background: '#07020f' }}>
      <Camera scale={push} origin={`${CX}px 900px`}>
        <AbsoluteFill style={{ background: 'radial-gradient(ellipse 80% 60% at 50% 40%, #3a0d6e 0%, #16052e 55%, #05010b 100%)' }} />
        {/* 傳送門外圈光暈 */}
        <div
          style={{
            position: 'absolute',
            left: CX - 520,
            top: CY - 680,
            width: 1040,
            height: 1360,
            borderRadius: '50%',
            background: 'radial-gradient(ellipse, rgba(190,90,255,0.55) 0%, rgba(120,30,220,0.35) 40%, rgba(60,0,120,0) 70%)',
            transform: `scale(${open})`,
          }}
        />
        {/* 漩渦 */}
        <div
          style={{
            position: 'absolute',
            left: CX - 380,
            top: CY - 500,
            width: 760,
            height: 1000,
            borderRadius: '50%',
            background: `conic-gradient(from ${rot}deg, rgba(255,255,255,0.0), rgba(220,150,255,0.6), rgba(120,40,255,0.1), rgba(255,120,240,0.55), rgba(255,255,255,0.0), rgba(170,90,255,0.6), rgba(255,255,255,0))`,
            filter: 'blur(14px)',
            transform: `scale(${open})`,
            WebkitMaskImage: 'radial-gradient(ellipse, #000 30%, rgba(0,0,0,0.6) 55%, transparent 70%)',
          }}
        />
        {/* 核心強光 */}
        <div
          style={{
            position: 'absolute',
            left: CX - 300,
            top: CY - 400,
            width: 600,
            height: 800,
            borderRadius: '50%',
            background: 'radial-gradient(ellipse, #ffffff 0%, rgba(245,220,255,0.95) 18%, rgba(200,120,255,0.55) 42%, rgba(120,40,255,0) 70%)',
            transform: `scale(${open * (1 + Math.sin(frame * 0.9) * 0.03)})`,
          }}
        />
        <Arcs frame={frame} open={open} />
        <Burst frame={frame} />
        {/* 地面反光 */}
        <AbsoluteFill style={{ background: 'linear-gradient(180deg, rgba(0,0,0,0) 62%, rgba(30,5,60,0.8) 75%, #070210 100%)' }} />
        {/* 背光英雄剪影 */}
        {lineup.map((c, i) => {
          const n = lineup.length;
          const off = i - (n - 1) / 2;
          const depth = 1 - Math.abs(off) * 0.06;
          const h = 470 * depth;
          const w = h * 0.52;
          return (
            <div
              key={c.id}
              style={{
                position: 'absolute',
                left: CX + off * 112 - w / 2,
                top: 1450 - h - Math.abs(off) * 22,
                width: w,
                height: h,
                zIndex: 10 - Math.abs(off),
              }}
            >
              <Figure
                uid={`p-${c.id}`}
                archetype={c.archetype}
                t={t + i}
                rimLeft="#d38bff"
                rimRight="#ffffff"
                glow="#b46bff"
                glowStrength={0.5}
                detail={0}
                style={{ width: '100%', height: '100%' }}
              />
            </div>
          );
        })}
        <Fog frame={frame} top={1380} color="180,110,255" opacity={0.6} seed="pfog" />
        <Embers frame={frame} count={40} seed="pemb" colors={['#e6b8ff', '#b76bff', '#ffffff']} speed={1.6} />
      </Camera>
      <Vignette strength={0.7} />
      <Subtitle text={sub.text} opacity={subOpacity} enter={enter} y={1500} size={76} glow="rgba(200,120,255,0.8)" />
      <Flash opacity={interpolate(frame, [0, 4], [0.7, 0], clamp)} color="#e7d4ff" />
      <Flash opacity={interpolate(frame, [len - 4, len], [0, 1], clamp)} />
    </AbsoluteFill>
  );
};

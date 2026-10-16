import React, { useMemo } from 'react';
import { AbsoluteFill, random } from 'remotion';
import { ART_STYLE } from '../config/theme';
import { Figure } from './Figure';
import { FigureComic } from './FigureComic';

/**
 * 室內演講舞台：布幕、木地板、聚光燈、單一麥克風。
 * light：聚光燈強度 0–1；warm：0 = 冷白，1 = 溫暖金色。
 */
export const Stage: React.FC<{
  frame: number;
  light: number;
  warm?: number;
  /** 普通人（背影）：progress 0 = 畫面前方，1 = 站到麥克風前 */
  person?: { progress: number; walk: number; opacity?: number };
}> = ({ frame, light, warm = 0, person }) => {
  const beamColor = warm > 0 ? mix([235, 235, 225], [255, 200, 110], warm) : [235, 235, 225];
  const rgb = (a: number) => `rgba(${beamColor[0]},${beamColor[1]},${beamColor[2]},${a})`;
  const dust = useMemo(
    () =>
      new Array(55).fill(0).map((_, i) => ({
        x: random(`dx${i}`),
        y: random(`dy${i}`),
        r: 1 + random(`dr${i}`) * 2.5,
        v: 0.2 + random(`dv${i}`) * 0.6,
        p: random(`dp${i}`) * 6,
      })),
    [],
  );
  const MIC_X = 540;
  const FLOOR_Y = 1460;

  // 普通人：由前景走到麥克風後方
  const pp = person?.progress ?? 0;
  const personScale = 1.9 - 0.9 * pp;
  const personH = 820 * personScale;
  const personW = (personH * 520) / 1060;
  const personBottom = FLOOR_Y + 40 + (1 - pp) * 900;

  return (
    <AbsoluteFill style={{ background: '#0b0907', overflow: 'hidden' }}>
      {/* 後方布幕 */}
      <AbsoluteFill
        style={{
          background:
            'repeating-linear-gradient(90deg, #1a0d0b 0px, #2a1512 38px, #3a1d17 60px, #2a1512 84px, #1a0d0b 120px)',
          opacity: 0.9,
        }}
      />
      <AbsoluteFill style={{ background: 'linear-gradient(180deg, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.35) 45%, rgba(0,0,0,0.75) 75%)' }} />
      {/* 地板 */}
      <svg width={1080} height={1920} style={{ position: 'absolute', inset: 0 }}>
        <defs>
          <linearGradient id="floorG" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor="#2b1b10" />
            <stop offset="1" stopColor="#120b06" />
          </linearGradient>
          <radialGradient id="pool" cx="0.5" cy="0.5" r="0.5">
            <stop offset="0" stopColor={rgb(0.55 * light)} />
            <stop offset="0.6" stopColor={rgb(0.18 * light)} />
            <stop offset="1" stopColor={rgb(0)} />
          </radialGradient>
        </defs>
        <rect x={0} y={1240} width={1080} height={680} fill="url(#floorG)" />
        {new Array(17).fill(0).map((_, i) => {
          const xb = -600 + i * 142;
          return <line key={i} x1={540 + (xb - 540) * 0.25} y1={1240} x2={xb} y2={1920} stroke="#0a0604" strokeWidth={3} opacity={0.7} />;
        })}
        {[1300, 1380, 1490, 1640, 1840].map((y) => (
          <line key={y} x1={0} y1={y} x2={1080} y2={y} stroke="#0a0604" strokeWidth={2} opacity={0.4} />
        ))}
        <ellipse cx={MIC_X} cy={FLOOR_Y} rx={430} ry={120} fill="url(#pool)" />
      </svg>
      {/* 聚光燈光束 */}
      <div
        style={{
          position: 'absolute',
          left: MIC_X - 440,
          top: -120,
          width: 880,
          height: FLOOR_Y + 160,
          clipPath: 'polygon(42% 0, 58% 0, 100% 100%, 0 100%)',
          background: `linear-gradient(180deg, ${rgb(0.55 * light)} 0%, ${rgb(0.22 * light)} 60%, ${rgb(0.1 * light)} 100%)`,
          filter: 'blur(12px)',
        }}
      />
      <div
        style={{
          position: 'absolute',
          left: MIC_X - 90,
          top: -150,
          width: 180,
          height: 180,
          borderRadius: '50%',
          background: `radial-gradient(circle, ${rgb(1 * light)} 0%, ${rgb(0.5 * light)} 30%, ${rgb(0)} 70%)`,
        }}
      />
      {/* 光束中的灰塵 */}
      <svg width={1080} height={1920} style={{ position: 'absolute', inset: 0 }}>
        {dust.map((d, i) => {
          const y = ((d.y * 1400 + frame * d.v * 3) % 1400) + 40;
          const spread = (y / 1460) * 440;
          const x = MIC_X + (d.x - 0.5) * 2 * spread + Math.sin(frame * 0.05 + d.p) * 10;
          return <circle key={i} cx={x} cy={y} r={d.r} fill={rgb(0.8)} opacity={light * (0.3 + 0.4 * Math.sin(frame * 0.1 + d.p))} />;
        })}
      </svg>
      {/* 麥克風架 */}
      <Microphone x={MIC_X} floorY={FLOOR_Y} light={light} warm={warm} />
      {/* 普通人背影 */}
      {person ? (
        <div
          style={{
            position: 'absolute',
            left: MIC_X - personW / 2 - 6,
            top: personBottom - personH,
            width: personW,
            height: personH,
            opacity: person.opacity ?? 1,
          }}
        >
          {ART_STYLE === 'comic' ? (
            <FigureComic
              uid="everyday"
              archetype="everyday"
              walk={person.walk}
              rimRight={rgb(1)}
              rimLeft={rgb(0.6)}
              glow={rgb(1)}
              glowStrength={0.4 * light}
              light={0.25 + 0.75 * light}
              style={{ width: '100%', height: '100%' }}
            />
          ) : (
            <Figure
              uid="everyday"
              archetype="everyday"
              walk={person.walk}
              rimRight={rgb(0.25 + 0.6 * light)}
              rimLeft={rgb(0.15 + 0.45 * light)}
              glow={rgb(1)}
              glowStrength={0.35 * light}
              fill="#0d0a10"
              style={{ width: '100%', height: '100%' }}
            />
          )}
        </div>
      ) : null}
    </AbsoluteFill>
  );
};

const mix = (a: number[], b: number[], t: number) => a.map((v, i) => Math.round(v + (b[i] - v) * t));

export const MIC_HEAD = { x: 540, y: 860 };

export const Microphone: React.FC<{ x: number; floorY: number; light: number; warm: number }> = ({ x, floorY, light, warm }) => {
  const hl = warm > 0.5 ? '#ffe2a8' : '#f2f2f2';
  return (
    <svg width={1080} height={1920} style={{ position: 'absolute', inset: 0 }}>
      <defs>
        <linearGradient id="pole" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0" stopColor="#0c0c0e" />
          <stop offset="0.45" stopColor={hl} stopOpacity={0.55 * light + 0.1} />
          <stop offset="1" stopColor="#0c0c0e" />
        </linearGradient>
        <radialGradient id="grille" cx="0.4" cy="0.3" r="0.8">
          <stop offset="0" stopColor={hl} stopOpacity={0.9 * light + 0.1} />
          <stop offset="0.5" stopColor="#5b5b62" />
          <stop offset="1" stopColor="#141417" />
        </radialGradient>
        <pattern id="mesh" width="8" height="8" patternUnits="userSpaceOnUse">
          <path d="M0 0 L8 8 M8 0 L0 8" stroke="#000" strokeWidth={1} opacity={0.5} />
        </pattern>
      </defs>
      {/* 地面陰影 */}
      <ellipse cx={x} cy={floorY + 8} rx={150} ry={22} fill="#000" opacity={0.6} />
      {/* 三腳架 */}
      <path d={`M${x} ${floorY - 60} L${x - 130} ${floorY + 6} M${x} ${floorY - 60} L${x + 130} ${floorY + 6} M${x} ${floorY - 60} L${x} ${floorY + 14}`} stroke="#111114" strokeWidth={10} strokeLinecap="round" />
      {/* 立桿 */}
      <rect x={x - 7} y={MIC_HEAD.y + 70} width={14} height={floorY - MIC_HEAD.y - 120} fill="url(#pole)" />
      <rect x={x - 12} y={1180} width={24} height={30} rx={4} fill="#1a1a1e" />
      {/* 麥克風夾與本體 */}
      <g transform={`rotate(-18 ${MIC_HEAD.x} ${MIC_HEAD.y + 70})`}>
        <rect x={MIC_HEAD.x - 16} y={MIC_HEAD.y + 20} width={32} height={140} rx={14} fill="url(#pole)" />
        <rect x={MIC_HEAD.x - 21} y={MIC_HEAD.y + 14} width={42} height={16} rx={4} fill="#26262b" />
        <ellipse cx={MIC_HEAD.x} cy={MIC_HEAD.y - 16} rx={38} ry={44} fill="url(#grille)" />
        <ellipse cx={MIC_HEAD.x} cy={MIC_HEAD.y - 16} rx={38} ry={44} fill="url(#mesh)" />
        <ellipse cx={MIC_HEAD.x - 12} cy={MIC_HEAD.y - 36} rx={10} ry={14} fill={hl} opacity={0.5 * light} />
      </g>
    </svg>
  );
};

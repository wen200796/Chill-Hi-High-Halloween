import React from 'react';
import { AbsoluteFill, Easing, Img, interpolate, Sequence, staticFile, useCurrentFrame } from 'remotion';
import { CharacterVisual, characterGeometry } from '../components/CharacterVisual';
import { CaptionBox, ComicBurst, Halftone, INK, SfxWord, SpeedLines } from '../components/Comic';
import { Embers } from '../components/Night';
import { Camera, Flash, Vignette } from '../components/Overlays';
import { Character, getCharacter } from '../config/characters';
import { SUBTITLES } from '../config/subtitles';
import { ROSTER, rosterShotStart } from '../config/video';
import { clamp, shake } from '../util';

/** 各構圖的角色尺寸與臉部位置（以 1080×1920 畫面為準） */
const FRAMING: Record<Character['shot'], { h: number; headY: number; tilt: number }> = {
  closeup: { h: 4300, headY: 800, tilt: 0 },
  bust: { h: 2700, headY: 660, tilt: 0 },
  'low-angle': { h: 1950, headY: 330, tilt: 6 },
};

/** 漫畫格外框：白色間隔 + 黑色框線 */
const PanelFrame: React.FC = () => (
  <svg width={1080} height={1920} style={{ position: 'absolute', inset: 0 }}>
    <path d="M0 0 H1080 V1920 H0 Z M22 22 L1058 22 L1058 1898 L22 1898 Z" fill="#fbf6e8" fillRule="evenodd" />
    <rect x={22} y={22} width={1036} height={1876} fill="none" stroke={INK} strokeWidth={9} />
  </svg>
);

const RosterShot: React.FC<{ c: Character; index: number; len: number }> = ({ c, index, len }) => {
  const frame = useCurrentFrame();
  const t = (rosterShotStart(index) + frame) / 30;
  const f = FRAMING[c.shot];
  const push = interpolate(frame, [0, len], [1.0, 1.12], { ...clamp, easing: Easing.out(Easing.quad) });
  const slideIn = interpolate(frame, [0, 5], [c.slant * 120, 0], { ...clamp, easing: Easing.out(Easing.cubic) });
  const sh = shake(frame, 0, 6, 22, index + 3);
  const g = characterGeometry(c);
  const w = f.h * g.aspect;
  const left = 540 - g.headX * w;
  const top = f.headY - g.headY * f.h;
  const pop = interpolate(frame, [1, 5], [0, 1], { ...clamp, easing: Easing.out(Easing.back(2.2)) });

  return (
    <AbsoluteFill style={{ background: '#fbf6e8', overflow: 'hidden' }}>
      {/* 漫畫爆炸光背景：角色主色 + 網點 + 集中線 */}
      <ComicBurst c1="#fff6c8" c2={c.accent} c3={c.accent2} id={`rb${index}`} dots={c.accent2} />
      <SpeedLines cy={f.headY} r0={420} seed={index * 11} opacity={0.8} />
      <Camera scale={push} x={slideIn + sh.x} y={sh.y} rotate={sh.r} origin={`540px ${f.headY}px`}>
        {c.photo ? (
          <Img
            src={staticFile(c.photo)}
            style={{
              position: 'absolute',
              inset: 0,
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              objectPosition: `${(c.focus?.x ?? 0.5) * 100}% ${(c.focus?.y ?? 0.3) * 100}%`,
            }}
          />
        ) : (
          <div
            style={{
              position: 'absolute',
              left,
              top,
              width: w,
              height: f.h,
              transform: f.tilt ? `perspective(1400px) rotateX(${f.tilt}deg)` : undefined,
              transformOrigin: '50% 100%',
            }}
          >
            <CharacterVisual
              uid={`r-${c.id}`}
              c={c}
              t={t}
              rimRight="#fffbe6"
              rimLeft={c.accent}
              glow="#ffffff"
              glowStrength={0.35}
              style={{ width: '100%', height: '100%' }}
            />
          </div>
        )}
      </Camera>
      <Embers frame={frame + index * 15} count={18} seed={`re${index}`} colors={['#ffffff', c.accent]} speed={2.5} />
      <Halftone id={`rh${index}`} size={10} opacity={0.08} />
      {c.sfx ? (
        <SfxWord
          text={c.sfx}
          x={c.slant > 0 ? 760 : 320}
          y={330}
          size={c.sfx.length > 7 ? 104 : 136}
          rotate={c.slant * -9}
          pop={pop}
          fill={index % 2 ? '#ffe94a' : '#ffffff'}
        />
      ) : null}
      <PanelFrame />
      <Flash opacity={interpolate(frame, [0, 2], [0.6, 0], clamp)} />
    </AbsoluteFill>
  );
};

/** Scene 3｜角色快速登場：每個角色一個漫畫格，閃光切換 */
export const Scene3Roster: React.FC = () => {
  const frame = useCurrentFrame();
  const cast = ROSTER.map(getCharacter);
  // 每種角色類型第一次出現時，說明框加上對應的詞
  const words = cast
    .map((c, i) => ({ group: c.group, at: rosterShotStart(i) }))
    .filter((w, i, arr) => arr.findIndex((x) => x.group === w.group) === i)
    .map((w) => ({ text: SUBTITLES.roster[w.group], at: w.at }));
  const shown = words.filter((w) => frame >= w.at);
  const last = shown[shown.length - 1];
  const pop = last ? interpolate(frame, [last.at, last.at + 5], [0, 1], { ...clamp, easing: Easing.out(Easing.back(2)) }) : 0;

  return (
    <AbsoluteFill style={{ background: '#000' }}>
      {cast.map((c, i) => {
        const from = rosterShotStart(i);
        const len = rosterShotStart(i + 1) - from;
        return (
          <Sequence key={c.id} from={from} durationInFrames={len} layout="none">
            <RosterShot c={c} index={i} len={len} />
          </Sequence>
        );
      })}
      <Vignette strength={0.25} />
      {shown.length ? (
        <CaptionBox text={shown.map((w) => w.text).join('')} opacity={1} enter={0.85 + 0.15 * pop} y={1500} size={66} rotate={-2} />
      ) : null}
    </AbsoluteFill>
  );
};

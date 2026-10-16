import React from 'react';
import { AbsoluteFill, Easing, Img, interpolate, Sequence, staticFile, useCurrentFrame } from 'remotion';
import { CharacterVisual, characterGeometry } from '../components/CharacterVisual';
import { Embers } from '../components/Night';
import { Camera, Flash, Subtitle, Vignette } from '../components/Overlays';
import { Character, getCharacter } from '../config/characters';
import { SUBTITLES } from '../config/subtitles';
import { ROSTER, rosterShotStart } from '../config/video';
import { clamp, shake } from '../util';

/** 各構圖的剪影尺寸與位置（以 1080×1920 畫面為準） */
const FRAMING: Record<Character['shot'], { h: number; headY: number; tilt: number }> = {
  closeup: { h: 4700, headY: 820, tilt: 0 },
  bust: { h: 2900, headY: 660, tilt: 0 },
  'low-angle': { h: 2050, headY: 330, tilt: 7 },
};

const RosterShot: React.FC<{ c: Character; index: number; len: number }> = ({ c, index, len }) => {
  const frame = useCurrentFrame();
  const t = (rosterShotStart(index) + frame) / 30;
  const f = FRAMING[c.shot];
  const push = interpolate(frame, [0, len], [1.0, 1.13], { ...clamp, easing: Easing.out(Easing.quad) });
  const slideIn = interpolate(frame, [0, 5], [c.slant * 120, 0], { ...clamp, easing: Easing.out(Easing.cubic) });
  const sh = shake(frame, 0, 6, 22, index + 3);
  const g = characterGeometry(c);
  const w = f.h * g.aspect;
  const left = 540 - g.headX * w;
  const top = f.headY - g.headY * f.h;
  const streak = interpolate(frame, [0, len], [-500, 900], clamp);

  return (
    <AbsoluteFill style={{ background: '#030308', overflow: 'hidden' }}>
      {/* 背景：角色主色漸層 + 斜切面板 */}
      <AbsoluteFill
        style={{
          background: `linear-gradient(${c.slant > 0 ? 160 : 200}deg, ${c.accent2} 0%, #07060f 55%, #000 100%)`,
          opacity: 0.85,
        }}
      />
      <AbsoluteFill
        style={{
          background: `radial-gradient(circle at 50% ${f.headY / 19.2}%, ${c.accent}88 0%, ${c.accent}22 30%, rgba(0,0,0,0) 60%)`,
        }}
      />
      {[0, 1, 2].map((i) => (
        <div
          key={i}
          style={{
            position: 'absolute',
            left: streak - 300 + i * 260,
            top: -400,
            width: 60 + i * 30,
            height: 2800,
            background: `linear-gradient(90deg, rgba(255,255,255,0), ${i === 1 ? c.accent : '#ffffff'}55, rgba(255,255,255,0))`,
            transform: `rotate(${c.slant * 24}deg)`,
            filter: 'blur(6px)',
          }}
        />
      ))}
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
              rimRight={c.accent}
              rimLeft="#ffffff"
              glow={c.accent}
              glowStrength={0.55}
              style={{ width: '100%', height: '100%' }}
            />
          </div>
        )}
      </Camera>
      <Embers frame={frame + index * 15} count={26} seed={`re${index}`} colors={[c.accent, '#ffffff']} speed={2.5} />
      {/* 斜向切鏡遮罩 */}
      <div
        style={{
          position: 'absolute',
          left: -300,
          right: -300,
          top: 1480,
          height: 900,
          background: 'linear-gradient(180deg, rgba(0,0,0,0) 0%, rgba(0,0,0,0.85) 30%, #000 100%)',
          transform: `rotate(${c.slant * -4}deg)`,
        }}
      />
      <div
        style={{
          position: 'absolute',
          left: -200,
          right: -200,
          top: 1490,
          height: 6,
          background: c.accent,
          boxShadow: `0 0 24px ${c.accent}`,
          transform: `rotate(${c.slant * -4}deg) translateX(${interpolate(frame, [0, 8], [c.slant * -1400, 0], { ...clamp, easing: Easing.out(Easing.cubic) })}px)`,
        }}
      />
      <Flash opacity={interpolate(frame, [0, 2], [0.5, 0], clamp)} />
    </AbsoluteFill>
  );
};

/** Scene 3｜角色快速登場：每個角色一個獨立鏡頭，閃光切換 */
export const Scene3Roster: React.FC = () => {
  const frame = useCurrentFrame();
  const cast = ROSTER.map(getCharacter);
  // 每種角色類型第一次出現時，字幕加上對應的詞
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
      <Vignette strength={0.55} />
      {shown.length ? (
        <div style={{ position: 'absolute', left: 0, right: 0, top: 1480, textAlign: 'center' }}>
          {shown.map((w, i) => (
            <span
              key={w.text}
              style={{
                display: 'inline-block',
                transform: i === shown.length - 1 ? `scale(${0.6 + 0.4 * pop})` : undefined,
                opacity: i === shown.length - 1 ? pop : 0.9,
              }}
            >
              <Subtitle
                text={w.text}
                opacity={1}
                size={80}
                y={0}
                style={{ position: 'relative', left: 0, right: 0, top: 0, letterSpacing: '0.04em' }}
              />
            </span>
          ))}
        </div>
      ) : null}
    </AbsoluteFill>
  );
};

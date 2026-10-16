import React from 'react';
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from 'remotion';
import { CharacterVisual, characterGeometry } from '../components/CharacterVisual';
import { Castle, Clouds, Embers, Fog, Moon, Stars } from '../components/Night';
import { Camera, Flash, Subtitle, Vignette } from '../components/Overlays';
import { ASSEMBLY_FORMATION, getCharacter } from '../config/characters';
import { SUBTITLES } from '../config/subtitles';
import { COLORS } from '../config/theme';
import { SCENES, sec } from '../config/video';
import { clamp, fadeInOut, progress, shake } from '../util';

/** Scene 4｜史詩級集結：群像、城堡、紫橘交錯光影、主題字幕 */
export const Scene4Assemble: React.FC = () => {
  const frame = useCurrentFrame();
  const len = sec(SCENES.assemble.end - SCENES.assemble.start);
  const t = frame / 30;
  const push = interpolate(frame, [0, len], [1.0, 1.1], { ...clamp, easing: Easing.inOut(Easing.quad) });
  const rise = interpolate(frame, [0, len], [40, -20], clamp);
  const themeAt = sec(SUBTITLES.theme.from);
  const hit = shake(frame, themeAt, 10, 14, 21);
  const beam = 0.6 + 0.4 * Math.sin(frame * 0.12);

  return (
    <AbsoluteFill style={{ background: '#05020c' }}>
      <Camera scale={push} y={rise + hit.y} x={hit.x} origin="50% 70%">
        {/* 戲劇性天空：上方深藍紫、地平線橘紅 */}
        <AbsoluteFill
          style={{
            background:
              'linear-gradient(180deg, #050826 0%, #1b0f4a 30%, #4a1658 52%, #a8321f 68%, #ff7a1a 74%, #2a0a12 82%, #07030a 100%)',
          }}
        />
        <Stars frame={frame} count={80} maxY={700} seed="as" />
        <Moon x={760} y={340} r={150} glow={0.9} tint="#fde9c8" />
        <Clouds frame={frame} y={520} color="40,12,60" opacity={0.8} seed="acl" speed={1.5} />
        {/* 能量光束 */}
        {[-34, -18, 16, 30].map((a, i) => (
          <div
            key={a}
            style={{
              position: 'absolute',
              left: 540 - 70,
              top: -200,
              width: 140,
              height: 1700,
              transformOrigin: '50% 100%',
              transform: `rotate(${a + Math.sin(frame * 0.05 + i) * 3}deg)`,
              background: `linear-gradient(0deg, ${i % 2 ? 'rgba(255,140,40,0.55)' : 'rgba(170,80,255,0.55)'} 0%, rgba(0,0,0,0) 85%)`,
              filter: 'blur(18px)',
              opacity: beam,
              mixBlendMode: 'screen',
            }}
          />
        ))}
        <Castle frame={frame} width={1080} color="#0a0512" style={{ position: 'absolute', left: 0, top: 280, opacity: 0.95 }} />
        {/* 地平線火光 */}
        <AbsoluteFill style={{ background: 'radial-gradient(ellipse 70% 18% at 50% 72%, rgba(255,120,30,0.55), rgba(255,80,20,0) 70%)' }} />
        <AbsoluteFill style={{ background: 'linear-gradient(180deg, rgba(0,0,0,0) 66%, rgba(5,2,10,0.92) 80%, #040208 100%)' }} />
        {/* 群像 */}
        {[...ASSEMBLY_FORMATION]
          .sort((a, b) => a.z - b.z)
          .map((pos) => {
            const c = getCharacter(pos.id);
            const p = progress(frame, sec(pos.delay), sec(pos.delay) + 12, Easing.out(Easing.cubic));
            const h = 980 * pos.scale;
            const w = h * characterGeometry(c).aspect;
            const baseY = pos.baseY;
            return (
              <div
                key={pos.id}
                style={{
                  position: 'absolute',
                  left: pos.x * 1080 - w / 2,
                  top: baseY - h + (1 - p) * 160,
                  width: w,
                  height: h,
                  opacity: p,
                  filter: pos.z < 1 ? 'brightness(0.8)' : undefined,
                }}
              >
                <CharacterVisual
                  uid={`a-${c.id}`}
                  c={c}
                  t={t + pos.z}
                  rimLeft={COLORS.violet}
                  rimRight={COLORS.orange}
                  glow={pos.x < 0.5 ? COLORS.purple : COLORS.orange}
                  glowStrength={0.45}
                  detail={0.9}
                  style={{ width: '100%', height: '100%' }}
                />
              </div>
            );
          })}
        <Fog frame={frame} top={1380} color="190,120,255" opacity={0.45} seed="afog" />
        <Embers frame={frame} count={70} seed="aemb" speed={1.3} />
      </Camera>
      <Vignette strength={0.65} />
      {SUBTITLES.assemble.map((s) => (
        <Subtitle
          key={s.text}
          text={s.text}
          opacity={fadeInOut(frame, sec(s.from), sec(s.from) + 4, sec(s.to) - 3, sec(s.to))}
          enter={progress(frame, sec(s.from), sec(s.from) + 10, Easing.out(Easing.cubic))}
          y={1500}
          size={74}
          glow="rgba(255,140,60,0.6)"
        />
      ))}
      {/* 核心主題：大字、金色、清楚易讀 */}
      <Subtitle
        text={SUBTITLES.theme.text}
        opacity={interpolate(frame, [themeAt, themeAt + 3], [0, 1], clamp)}
        enter={progress(frame, themeAt, themeAt + 8, Easing.out(Easing.cubic))}
        y={1480}
        size={88}
        color={COLORS.warmGold}
        glow="rgba(255,150,40,0.85)"
        letterSpacing={0.03}
        style={{ transform: `scale(${interpolate(frame, [themeAt, len], [1.08, 1.0], clamp)})` }}
      />
      <Flash opacity={interpolate(frame, [themeAt - 1, themeAt, themeAt + 4], [0, 0.55, 0], clamp)} color="#ffd9a0" />
      <Flash opacity={interpolate(frame, [0, 3], [0.8, 0], clamp)} />
    </AbsoluteFill>
  );
};

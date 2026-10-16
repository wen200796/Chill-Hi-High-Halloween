import React from 'react';
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from 'remotion';
import { Bats, Castle, Clouds, DeadTree, Fog, Lightning, Moon, Sky, Stars } from '../components/Night';
import { Camera, Flash, Subtitle, Vignette } from '../components/Overlays';
import { SUBTITLES } from '../config/subtitles';
import { CUES, SCENES, sec } from '../config/video';
import { clamp, fadeInOut, progress } from '../util';

/** Scene 1｜神祕開場：月夜城堡、閃電、薄霧、鏡頭緩慢推近 */
export const Scene1Castle: React.FC = () => {
  const frame = useCurrentFrame();
  const len = sec(SCENES.castle.end - SCENES.castle.start);
  const push = interpolate(frame, [0, len], [1.0, 1.16], { ...clamp, easing: Easing.out(Easing.quad) });
  const lf = sec(CUES.lightning);
  // 閃電：兩次閃爍
  const bolt = interpolate(frame, [lf - 1, lf, lf + 1, lf + 2, lf + 3, lf + 5], [0, 1, 0.2, 0.9, 0.3, 0], clamp);
  const sub = SUBTITLES.castle;
  const subOpacity = fadeInOut(frame, sec(sub.from), sec(sub.from) + 8, len + 10, len + 11);
  const enter = progress(frame, sec(sub.from), sec(sub.from) + 14, Easing.out(Easing.cubic));
  // 由暗處淡入（第 0 幀仍可看見城堡輪廓，避免黑畫面）
  const fromDark = interpolate(frame, [0, 8], [0.55, 0], clamp);

  return (
    <AbsoluteFill style={{ background: '#02040d' }}>
      <Camera scale={push} origin="50% 58%">
        <Sky top="#02040f" mid="#0a1440" bottom="#1a2a6a" />
        <Stars frame={frame} />
        <AbsoluteFill style={{ background: `rgba(170,190,255,${bolt * 0.35})` }} />
        <Moon x={600} y={560} r={210} />
        <Clouds frame={frame} y={520} color="12,18,48" opacity={0.85} speed={2.2} />
        <Lightning seed={4} x={860} y={180} length={720} opacity={bolt} />
        <Castle frame={frame} width={1080} style={{ position: 'absolute', left: 0, top: 700 }} />
        <Bats frame={frame + 10} count={7} />
        <DeadTree seed={3} style={{ left: -380, top: 860, width: 900, height: 1100 }} />
        <DeadTree seed={9} flip style={{ left: 560, top: 820, width: 900, height: 1150 }} />
        <AbsoluteFill style={{ background: 'linear-gradient(180deg, rgba(0,0,0,0) 70%, rgba(2,4,14,0.95) 100%)' }} />
        <Fog frame={frame} top={1360} opacity={0.6} />
      </Camera>
      <Vignette strength={0.8} />
      <Subtitle text={sub.text} opacity={subOpacity} enter={enter} y={1290} size={78} />
      <AbsoluteFill style={{ background: '#000', opacity: fromDark }} />
      <Flash opacity={interpolate(frame, [len - 3, len], [0, 0.7], clamp)} color="#d9c4ff" />
    </AbsoluteFill>
  );
};

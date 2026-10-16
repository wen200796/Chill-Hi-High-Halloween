import React from 'react';
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from 'remotion';
import { Camera, Subtitle, Vignette } from '../components/Overlays';
import { Stage } from '../components/Stage';
import { SUBTITLES } from '../config/subtitles';
import { SCENES, sec } from '../config/video';
import { clamp, fadeInOut } from '../util';

/** Scene 5｜突然反轉：音樂停止，空蕩舞台與單一麥克風 */
export const Scene5Stage: React.FC = () => {
  const frame = useCurrentFrame();
  const len = sec(SCENES.stage.end - SCENES.stage.start);
  const push = interpolate(frame, [0, len], [1.0, 1.06], { ...clamp, easing: Easing.inOut(Easing.quad) });
  // 聚光燈「啪」一聲亮起
  const light = interpolate(frame, [0, 1, 2, 3], [0.15, 0.9, 0.7, 0.85], clamp);
  const sub = SUBTITLES.stage;
  return (
    <AbsoluteFill>
      <Camera scale={push} origin="50% 50%">
        <Stage frame={frame} light={light} />
      </Camera>
      <Vignette strength={0.85} />
      <Subtitle
        text={sub.text}
        opacity={fadeInOut(frame, sec(sub.from), sec(sub.from) + 3, len + 5, len + 6)}
        font="sans"
        weight={500}
        size={70}
        y={1560}
        color="#e8e8e8"
        glow="rgba(0,0,0,0)"
        letterSpacing={0.15}
      />
    </AbsoluteFill>
  );
};

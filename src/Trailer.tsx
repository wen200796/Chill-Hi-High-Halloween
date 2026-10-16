import React from 'react';
import { AbsoluteFill, Audio, Freeze, Sequence, staticFile, useCurrentFrame } from 'remotion';
import { Grain } from './components/Overlays';
import { AUDIO } from './config/audio';
import { sceneFrom, sceneLength } from './config/video';
import { ensureFonts } from './fonts';
import { Scene1Castle } from './scenes/Scene1Castle';
import { Scene2Portal } from './scenes/Scene2Portal';
import { Scene3Roster } from './scenes/Scene3Roster';
import { Scene4Assemble } from './scenes/Scene4Assemble';
import { Scene5Stage } from './scenes/Scene5Stage';
import { Scene6Challenge } from './scenes/Scene6Challenge';
import { Scene7Finale } from './scenes/Scene7Finale';

ensureFonts();

export type TrailerProps = { withMusic: boolean };

/** 主時間軸：各場景依 timeline.json 的起訖時間排列 */
export const Trailer: React.FC<TrailerProps> = ({ withMusic }) => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: '#000' }}>
      <Sequence from={sceneFrom('castle')} durationInFrames={sceneLength('castle')} name="1 神祕開場">
        <Scene1Castle />
      </Sequence>
      <Sequence from={sceneFrom('portal')} durationInFrames={sceneLength('portal')} name="2 次元裂縫">
        <Scene2Portal />
      </Sequence>
      <Sequence from={sceneFrom('roster')} durationInFrames={sceneLength('roster')} name="3 角色登場">
        <Scene3Roster />
      </Sequence>
      <Sequence from={sceneFrom('assemble')} durationInFrames={sceneLength('assemble')} name="4 英雄集結">
        <Scene4Assemble />
      </Sequence>
      {/* 音樂停止的瞬間：停格並降低飽和度 */}
      <Sequence from={sceneFrom('freeze')} durationInFrames={sceneLength('freeze')} name="4b 停格">
        <AbsoluteFill style={{ filter: 'saturate(0.35) brightness(0.8)' }}>
          <Freeze frame={sceneLength('assemble') - 1}>
            <Scene4Assemble />
          </Freeze>
        </AbsoluteFill>
      </Sequence>
      <Sequence from={sceneFrom('stage')} durationInFrames={sceneLength('stage')} name="5 突然反轉">
        <Scene5Stage />
      </Sequence>
      <Sequence from={sceneFrom('challenge')} durationInFrames={sceneLength('challenge')} name="6 即席演講">
        <Scene6Challenge />
      </Sequence>
      <Sequence from={sceneFrom('finale')} durationInFrames={sceneLength('finale')} name="7 片尾">
        <Scene7Finale />
      </Sequence>
      <Grain frame={frame} />
      <Audio src={staticFile(withMusic ? AUDIO.mix : AUDIO.sfx)} volume={AUDIO.volume} />
    </AbsoluteFill>
  );
};

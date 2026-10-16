import React from 'react';
import { Composition } from 'remotion';
import { VIDEO } from './config/video';
import { CelSpider } from './styletest/CelSpider';
import { ComicSpider } from './styletest/ComicSpider';
import { Trailer, TrailerProps } from './Trailer';

export const RemotionRoot: React.FC = () => (
  <>
    <Composition<any, TrailerProps>
      id="Trailer"
      component={Trailer}
      durationInFrames={VIDEO.durationInFrames}
      fps={VIDEO.fps}
      width={VIDEO.width}
      height={VIDEO.height}
      defaultProps={{ withMusic: true }}
    />
    <Composition<any, TrailerProps>
      id="TrailerNoMusic"
      component={Trailer}
      durationInFrames={VIDEO.durationInFrames}
      fps={VIDEO.fps}
      width={VIDEO.width}
      height={VIDEO.height}
      defaultProps={{ withMusic: false }}
    />
    {/* 風格測試（單張靜態圖） */}
    <Composition id="StyleTestCel" component={CelSpider} durationInFrames={1} fps={VIDEO.fps} width={VIDEO.width} height={VIDEO.height} />
    <Composition id="StyleTestComic" component={ComicSpider} durationInFrames={1} fps={VIDEO.fps} width={VIDEO.width} height={VIDEO.height} />
  </>
);

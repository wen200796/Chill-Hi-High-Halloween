import React from 'react';
import { Composition } from 'remotion';
import { VIDEO } from './config/video';
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
  </>
);

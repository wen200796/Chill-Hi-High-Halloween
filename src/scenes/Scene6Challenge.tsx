import React, { useMemo } from 'react';
import { AbsoluteFill, Easing, interpolate, random, staticFile, useCurrentFrame } from 'remotion';
import { Camera, Flash, Subtitle, Vignette } from '../components/Overlays';
import { MIC_HEAD, Stage } from '../components/Stage';
import { SUBTITLES } from '../config/subtitles';
import { COLORS, FONTS } from '../config/theme';
import { CUES, SCENES, sec } from '../config/video';
import { clamp, fadeInOut, shake } from '../util';

const Bokeh: React.FC<{ frame: number }> = ({ frame }) => {
  const dots = useMemo(
    () =>
      new Array(18).fill(0).map((_, i) => ({
        x: random(`bk${i}`) * 1080,
        y: random(`bky${i}`) * 1920,
        r: 40 + random(`bkr${i}`) * 90,
        a: 0.25 + random(`bka${i}`) * 0.4,
      })),
    [],
  );
  return (
    <AbsoluteFill style={{ background: 'radial-gradient(ellipse at 50% 40%, #3a2312 0%, #160c06 60%, #070403 100%)' }}>
      {dots.map((d, i) => (
        <div
          key={i}
          style={{
            position: 'absolute',
            left: d.x - d.r + Math.sin(frame * 0.03 + i) * 8,
            top: d.y - d.r,
            width: d.r * 2,
            height: d.r * 2,
            borderRadius: '50%',
            background: `radial-gradient(circle, rgba(255,190,110,${d.a}) 0%, rgba(255,160,80,${d.a * 0.6}) 55%, rgba(255,150,60,0) 72%)`,
            filter: 'blur(4px)',
          }}
        />
      ))}
    </AbsoluteFill>
  );
};

/** Scene 6｜即席演講挑戰：麥克風特寫 → 任務卡衝擊入畫 */
export const Scene6Challenge: React.FC = () => {
  const frame = useCurrentFrame();
  const len = sec(SCENES.challenge.end - SCENES.challenge.start);
  const slam = sec(CUES.cardSlam - SCENES.challenge.start);
  const lead = SUBTITLES.challenge.lead;
  const card = SUBTITLES.challenge.card;

  const micPush = interpolate(frame, [0, slam], [2.3, 2.55], clamp);
  const cardIn = interpolate(frame, [slam, slam + 5], [0, 1], { ...clamp, easing: Easing.out(Easing.back(1.8)) });
  const cardScale = interpolate(cardIn, [0, 1], [2.4, 1]);
  const cardRot = interpolate(cardIn, [0, 1], [-16, -4]);
  const sh = shake(frame, slam + 4, 9, 26, 5);
  const underline = interpolate(frame, [slam + 6, slam + 13], [1, 0], { ...clamp, easing: Easing.out(Easing.quad) });
  const noteIn = interpolate(frame, [slam + 14, slam + 18], [0, 1], clamp);
  const drift = interpolate(frame, [slam, len], [1, 1.05], clamp);

  return (
    <AbsoluteFill style={{ background: '#000' }}>
      {frame < slam ? (
        <AbsoluteFill>
          <Camera scale={micPush} origin={`${MIC_HEAD.x}px ${MIC_HEAD.y}px`} style={{ filter: 'saturate(0.8)' }}>
            <Stage frame={frame + 24} light={0.5} />
            <AbsoluteFill style={{ background: 'rgba(0,0,0,0.35)' }} />
          </Camera>
          <Vignette strength={0.85} />
          <Subtitle
            text={lead.text}
            opacity={fadeInOut(frame, sec(lead.from), sec(lead.from) + 4, slam + 2, slam + 3)}
            font="sans"
            weight={700}
            size={74}
            y={1480}
            color="#f2f2f2"
            glow="rgba(0,0,0,0)"
            letterSpacing={0.1}
          />
        </AbsoluteFill>
      ) : (
        <AbsoluteFill>
          <Camera scale={drift} x={sh.x} y={sh.y} rotate={sh.r}>
            <Bokeh frame={frame} />
            {/* 任務卡 */}
            <div
              style={{
                position: 'absolute',
                left: 80,
                top: 560,
                width: 920,
                height: 640,
                transform: `scale(${cardScale}) rotate(${cardRot}deg)`,
                transformOrigin: '50% 50%',
                background: `linear-gradient(160deg, #fbf5e6 0%, ${COLORS.paper} 55%, #e2d5b8 100%)`,
                borderRadius: 18,
                boxShadow: '0 40px 80px rgba(0,0,0,0.7), 0 0 0 2px rgba(0,0,0,0.05) inset',
                overflow: 'hidden',
              }}
            >
              {/* 紙張紋理 */}
              <div
                style={{
                  position: 'absolute',
                  inset: 0,
                  backgroundImage: `url(${staticFile('assets/grain.png')})`,
                  backgroundSize: '256px 256px',
                  mixBlendMode: 'multiply',
                  opacity: 0.12,
                }}
              />
              <div
                style={{
                  position: 'absolute',
                  left: 56,
                  top: 46,
                  padding: '6px 22px',
                  border: `4px solid ${COLORS.bloodRed}`,
                  borderRadius: 10,
                  color: COLORS.bloodRed,
                  fontFamily: FONTS.sans,
                  fontWeight: 900,
                  fontSize: 44,
                  letterSpacing: '0.15em',
                  transform: 'rotate(-3deg)',
                }}
              >
                {card.label}
              </div>
              <div
                style={{
                  position: 'absolute',
                  left: 0,
                  right: 0,
                  top: 180,
                  textAlign: 'center',
                  fontFamily: FONTS.sans,
                  fontWeight: 900,
                  fontSize: 168,
                  lineHeight: 1.1,
                  color: COLORS.ink,
                  letterSpacing: '0.02em',
                }}
              >
                {card.title}
              </div>
              <svg width={920} height={640} style={{ position: 'absolute', inset: 0 }}>
                <path
                  d="M110 400 Q300 380 470 392 T820 384"
                  stroke="#d81e2c"
                  strokeWidth={16}
                  strokeLinecap="round"
                  fill="none"
                  pathLength={1}
                  strokeDasharray={1}
                  strokeDashoffset={underline}
                />
              </svg>
              <div
                style={{
                  position: 'absolute',
                  right: 60,
                  bottom: 64,
                  fontFamily: FONTS.sans,
                  fontWeight: 700,
                  fontSize: 50,
                  color: '#5a4a3a',
                  opacity: noteIn,
                  transform: `translateY(${(1 - noteIn) * 16}px)`,
                }}
              >
                {card.note}
              </div>
            </div>
          </Camera>
          <Vignette strength={0.6} />
        </AbsoluteFill>
      )}
      <Flash opacity={interpolate(frame, [slam - 1, slam, slam + 3], [0, 0.6, 0], clamp)} color="#fff3dc" />
    </AbsoluteFill>
  );
};

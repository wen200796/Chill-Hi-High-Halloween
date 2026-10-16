import React from 'react';
import { AbsoluteFill } from 'remotion';
import { Embers, Moon, Stars } from '../components/Night';
import { Subtitle, Vignette } from '../components/Overlays';

/**
 * 風格測試：動畫賽璐璐風格（cel-shading）的角色特寫。
 * 與正式版的剪影風格不同，這裡使用：底色 / 陰影 / 亮部三層色階、深色輪廓線、
 * 高光、雙色輪廓光（左紫右橘），並讓蛛網紋路沿著頭部曲面彎曲。
 */

const OUT = '#16050b';
const RED = '#d11a2e';
const RED_SH = '#8a0b1d';
const RED_HI = '#ff5867';
const BLUE = '#2348b8';
const BLUE_SH = '#11286e';
const BLUE_HI = '#4f7cf0';

// 頭部（面罩）外形
const HEAD = 'M540 300 C690 300 760 420 756 560 C752 700 690 800 600 846 C570 862 510 862 480 846 C390 800 328 700 324 560 C320 420 390 300 540 300 Z';
// 身體：頸、肩、胸
const NECK = 'M466 800 L614 800 L652 920 L428 920 Z';
const TORSO =
  'M440 900 C380 930 250 950 170 1010 C90 1070 60 1180 50 1340 L40 1920 L1040 1920 L1030 1340 C1020 1180 990 1070 910 1010 C830 950 700 930 640 900 Z';
// 胸前紅色區塊（兩側為藍色）
const CHEST_RED =
  'M330 960 C420 940 470 930 540 930 C610 930 660 940 750 960 C800 1100 790 1300 760 1500 C700 1560 620 1580 540 1580 C460 1580 380 1560 320 1500 C290 1300 280 1100 330 960 Z';

export const CelSpider: React.FC = () => {
  const frame = 20;
  return (
    <AbsoluteFill style={{ background: '#05020c' }}>
      {/* 背景：紫色夜空 + 滿月 + 橘色地平線 */}
      <AbsoluteFill style={{ background: 'linear-gradient(180deg, #070a2a 0%, #24104e 40%, #5a1a5a 62%, #c2491f 80%, #1a0610 100%)' }} />
      <Stars frame={frame} count={90} maxY={900} seed="cs" />
      <Moon x={200} y={250} r={110} glow={1} tint="#fde9c8" />
      <AbsoluteFill style={{ background: 'radial-gradient(ellipse 60% 40% at 50% 38%, rgba(160,80,255,0.35), rgba(0,0,0,0) 70%)' }} />

      <svg width={1080} height={1920} style={{ position: 'absolute', inset: 0 }}>
        <defs>
          <clipPath id="cs-head">
            <path d={HEAD} />
          </clipPath>
          <clipPath id="cs-torso">
            <path d={TORSO} />
          </clipPath>
          <clipPath id="cs-chest">
            <path d={CHEST_RED} />
          </clipPath>
          <linearGradient id="cs-lens" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stopColor="#ffffff" />
            <stop offset="0.6" stopColor="#e8eefc" />
            <stop offset="1" stopColor="#a9b6d6" />
          </linearGradient>
          <radialGradient id="cs-spec" cx="0.5" cy="0.5" r="0.5">
            <stop offset="0" stopColor="#fff" stopOpacity={0.75} />
            <stop offset="1" stopColor="#fff" stopOpacity={0} />
          </radialGradient>
          <filter id="cs-glow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation={10} />
          </filter>
        </defs>

        {/* 背光 */}
        <path d={HEAD} fill="#b46bff" opacity={0.5} filter="url(#cs-glow)" transform="translate(540 580) scale(1.06) translate(-540 -580)" />

        {/* ===== 身體 ===== */}
        <g>
          <path d={TORSO} fill={BLUE} />
          <g clipPath="url(#cs-torso)">
            {/* 陰影面（左側背光） */}
            <path d="M0 900 L420 900 C360 1100 300 1400 260 1920 L0 1920 Z" fill={BLUE_SH} />
            {/* 亮部（右側主光） */}
            <path d="M900 1000 C990 1060 1030 1200 1040 1400 L1000 1400 C990 1230 960 1110 880 1040 Z" fill={BLUE_HI} />
            {/* 胸前紅色區塊 */}
            <path d={CHEST_RED} fill={RED} />
            <g clipPath="url(#cs-chest)">
              <path d="M300 940 C420 1000 460 1200 430 1600 L280 1600 L280 940 Z" fill={RED_SH} />
              {/* 胸肌陰影 */}
              <path d="M360 1180 C430 1240 500 1250 540 1230 C580 1250 650 1240 720 1180 C700 1230 640 1270 540 1270 C440 1270 380 1230 360 1180 Z" fill={RED_SH} />
              <path d="M540 1000 L540 1580" stroke={RED_SH} strokeWidth={6} />
              {/* 腹肌 */}
              {[1340, 1420, 1500].map((y) => (
                <path key={y} d={`M450 ${y} Q495 ${y + 14} 530 ${y} M550 ${y} Q585 ${y + 14} 630 ${y}`} stroke={RED_SH} strokeWidth={6} fill="none" />
              ))}
              {/* 亮部 */}
              <path d="M650 990 C720 1010 760 1060 770 1160 C740 1100 700 1060 640 1040 Z" fill={RED_HI} />
              {/* 蛛網紋路（沿胸部曲面） */}
              <g stroke={OUT} strokeWidth={3} fill="none" opacity={0.85}>
                {[-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5].map((i) => (
                  <path key={i} d={`M540 1040 Q${540 + i * 60} ${1200} ${540 + i * 95} 1600`} />
                ))}
                {[1100, 1180, 1270, 1370, 1480].map((y, j) => (
                  <path key={y} d={`M${300 - j * 6} ${y + 40} Q540 ${y - 40 + j * 4} ${780 + j * 6} ${y + 40}`} />
                ))}
              </g>
            </g>
            {/* 三角肌與手臂分界 */}
            <path d="M262 990 C200 1060 196 1260 226 1560" stroke={BLUE_SH} strokeWidth={10} fill="none" />
            <path d="M818 990 C880 1060 884 1260 854 1560" stroke={BLUE_SH} strokeWidth={10} fill="none" />
            <path d="M120 1060 C170 1000 230 980 262 990 C220 1040 180 1080 120 1060 Z" fill={BLUE_SH} opacity={0.6} />
            {/* 腋下藍色側邊陰影線 */}
            <path d="M330 960 C280 1100 290 1300 320 1500" stroke={BLUE_SH} strokeWidth={14} fill="none" />
          </g>
          {/* 胸前蜘蛛標誌 */}
          <g transform="translate(540 1110)" fill={OUT} stroke={OUT} strokeLinecap="round">
            <ellipse rx={16} ry={26} />
            <circle cy={-30} r={11} />
            <g strokeWidth={8} fill="none">
              <path d="M-12 -14 L-50 -44 L-62 -86" />
              <path d="M12 -14 L50 -44 L62 -86" />
              <path d="M-14 -2 L-64 -8 L-90 -40" />
              <path d="M14 -2 L64 -8 L90 -40" />
              <path d="M-14 10 L-60 28 L-82 70" />
              <path d="M14 10 L60 28 L82 70" />
              <path d="M-10 20 L-36 60 L-44 110" />
              <path d="M10 20 L36 60 L44 110" />
            </g>
          </g>
          <path d={TORSO} fill="none" stroke={OUT} strokeWidth={8} />
          <path d={CHEST_RED} fill="none" stroke={OUT} strokeWidth={5} />
        </g>

        {/* ===== 頸部 ===== */}
        <path d={NECK} fill={RED} stroke={OUT} strokeWidth={6} />
        <path d="M466 800 L540 800 L520 920 L428 920 Z" fill={RED_SH} />

        {/* ===== 頭部 ===== */}
        <path d={HEAD} fill={RED} />
        <g clipPath="url(#cs-head)">
          {/* 陰影（左側） */}
          <path d="M300 300 C420 330 450 500 430 640 C410 760 470 840 560 880 L300 880 Z" fill={RED_SH} />
          {/* 下巴陰影 */}
          <path d="M380 760 C460 820 620 820 700 760 C680 840 600 880 540 880 C480 880 400 840 380 760 Z" fill={RED_SH} opacity={0.8} />
          {/* 亮部（右上） */}
          <path d="M600 320 C700 350 750 450 752 540 C720 470 680 410 600 370 Z" fill={RED_HI} />
          <ellipse cx={640} cy={400} rx={60} ry={34} fill="url(#cs-spec)" transform="rotate(30 640 400)" />
          {/* 蛛網：放射線（由鼻樑出發） */}
          <g stroke={OUT} strokeWidth={3.5} fill="none">
            {[...Array(14)].map((_, i) => {
              const a = (i / 14) * Math.PI * 2 - Math.PI / 2;
              const ex = 540 + Math.cos(a) * 520;
              const ey = 560 + Math.sin(a) * 560;
              const cx = 540 + Math.cos(a + 0.12) * 220;
              const cy = 560 + Math.sin(a + 0.12) * 240;
              return <path key={i} d={`M540 560 Q${cx} ${cy} ${ex} ${ey}`} />;
            })}
            {/* 同心弧（隨頭部曲面變形） */}
            {[70, 130, 195, 265, 340].map((r) => (
              <ellipse key={r} cx={540} cy={560 + r * 0.08} rx={r * 0.92} ry={r * 1.02} />
            ))}
          </g>
        </g>
        <path d={HEAD} fill="none" stroke={OUT} strokeWidth={8} />

        {/* 眼睛鏡片 */}
        {[
          { d: 'M520 540 C500 470 440 430 380 446 C360 500 380 580 430 610 C480 630 520 600 520 540 Z', hi: 'M420 480 C440 470 470 476 486 496' },
          { d: 'M560 540 C580 470 640 430 700 446 C720 500 700 580 650 610 C600 630 560 600 560 540 Z', hi: 'M612 492 C630 472 660 466 684 474' },
        ].map((e, i) => (
          <g key={i}>
            <path d={e.d} fill={OUT} transform={`translate(${i ? 10 : -10} 0) scale(1.0)`} />
            <path d={e.d} fill="url(#cs-lens)" stroke={OUT} strokeWidth={14} strokeLinejoin="round" />
            <path d={e.hi} stroke="#ffffff" strokeWidth={8} strokeLinecap="round" fill="none" opacity={0.9} />
          </g>
        ))}

        {/* 輪廓光：右側橘、左側紫 */}
        <path d="M700 380 C760 460 770 620 720 740" stroke="#ffb15a" strokeWidth={10} fill="none" strokeLinecap="round" opacity={0.9} />
        <path d="M920 1020 C1000 1080 1030 1200 1036 1360" stroke="#ffb15a" strokeWidth={12} fill="none" strokeLinecap="round" opacity={0.85} />
        <path d="M360 420 C320 500 320 640 370 740" stroke="#c88bff" strokeWidth={8} fill="none" strokeLinecap="round" opacity={0.8} />
        <path d="M150 1030 C90 1090 66 1200 56 1360" stroke="#c88bff" strokeWidth={10} fill="none" strokeLinecap="round" opacity={0.8} />
      </svg>

      <Embers frame={frame} count={40} seed="cse" colors={['#ffb347', '#ff6a1a', '#e6b8ff']} />
      <Vignette strength={0.6} />
      <Subtitle text="英雄、" opacity={1} y={1480} size={80} />
    </AbsoluteFill>
  );
};

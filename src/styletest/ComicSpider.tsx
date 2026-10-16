import React from 'react';
import { AbsoluteFill, staticFile } from 'remotion';
import { FONTS } from '../config/theme';

/**
 * 風格測試：美式漫畫原作風（comic book inking）。
 * 技法：粗細變化的墨線、大塊黑色陰影（spot black）、陰影邊緣排線（hatching）、
 * 網點（Ben-Day dots）、集中線背景、平塗色彩。主光源來自右上方。
 */

const INK = '#0a0608';
const RED = '#e01b2b';
const RED_SH = '#9c0f1f';
const BLUE = '#1f4fc4';
const BLUE_SH = '#123080';

type P = [number, number];

/** 沿折線產生排線（hatching） */
const hatch = (pts: P[], len: number, angleDeg: number, step: number, taper = true) => {
  const out: string[] = [];
  const a = (angleDeg * Math.PI) / 180;
  const total = pts.slice(1).reduce((s, p, i) => s + Math.hypot(p[0] - pts[i][0], p[1] - pts[i][1]), 0);
  let d = 0;
  for (let i = 0; i < pts.length - 1; i++) {
    const [x1, y1] = pts[i];
    const [x2, y2] = pts[i + 1];
    const seg = Math.hypot(x2 - x1, y2 - y1);
    for (let s = 0; s < seg; s += step) {
      const t = s / seg;
      const x = x1 + (x2 - x1) * t;
      const y = y1 + (y2 - y1) * t;
      const k = taper ? Math.sin(Math.PI * Math.min(1, (d + s) / total)) * 0.7 + 0.3 : 1;
      const l = len * k;
      out.push(`M${x.toFixed(1)} ${y.toFixed(1)} l${(Math.cos(a) * l).toFixed(1)} ${(Math.sin(a) * l).toFixed(1)}`);
    }
    d += seg;
  }
  return out.join(' ');
};

// ---------- 形狀 ----------
const HEAD =
  'M540 286 C664 286 742 378 744 500 C746 592 720 664 684 724 C652 778 602 832 540 842 C478 832 428 778 396 724 C360 664 334 592 336 500 C338 378 416 286 540 286 Z';
const NECK = 'M448 760 C452 820 440 870 420 910 L660 910 C640 870 628 820 632 760 Z';
// 軀幹（倒三角）
const BODY =
  'M430 878 C380 898 300 908 250 928 C228 1000 238 1100 268 1200 C298 1350 318 1500 330 1920 L750 1920 C762 1500 782 1350 812 1200 C842 1100 852 1000 830 928 C780 908 700 898 650 878 C610 898 575 910 540 910 C505 910 470 898 430 878 Z';
// 手臂（在軀幹後方）
const ARM_L = 'M262 920 C172 926 100 980 82 1080 C66 1180 70 1320 80 1460 C90 1600 100 1760 110 1920 L310 1920 C298 1760 288 1600 284 1460 C280 1340 276 1250 272 1190 C250 1100 240 1000 262 920 Z';
const ARM_R = 'M818 920 C908 926 980 980 998 1080 C1014 1180 1010 1320 1000 1460 C990 1600 980 1760 970 1920 L770 1920 C782 1760 792 1600 796 1460 C800 1340 804 1250 808 1190 C830 1100 840 1000 818 920 Z';
// 胸前紅色區塊
const CHEST =
  'M280 935 C370 922 460 914 540 914 C620 914 710 922 800 935 C820 1060 812 1200 784 1340 C750 1500 660 1600 540 1610 C420 1600 330 1500 296 1340 C268 1200 260 1060 280 935 Z';
// 胸肌下緣
const PEC_L = 'M300 1150 C360 1230 450 1260 530 1230';
const PEC_R = 'M550 1230 C630 1260 720 1230 780 1150';

const Speedlines: React.FC = () => {
  const lines = [];
  for (let i = 0; i < 90; i++) {
    const a = (i / 90) * Math.PI * 2 + (i % 3) * 0.01;
    const w = 0.006 + ((i * 37) % 11) * 0.0018;
    const r0 = 520 + ((i * 53) % 7) * 40;
    const r1 = 2200;
    const p = (r: number, aa: number) => `${540 + Math.cos(aa) * r} ${620 + Math.sin(aa) * r}`;
    lines.push(<path key={i} d={`M${p(r0, a)} L${p(r1, a - w)} L${p(r1, a + w)} Z`} fill={INK} />);
  }
  return <g opacity={0.9}>{lines}</g>;
};

export const ComicSpider: React.FC = () => {
  return (
    <AbsoluteFill style={{ background: '#f6e9c8' }}>
      <svg width={1080} height={1920} style={{ position: 'absolute', inset: 0 }}>
        <defs>
          <pattern id="dotsRed" width={18} height={18} patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
            <circle cx={9} cy={9} r={5.2} fill="#e8463a" />
          </pattern>
          <pattern id="dotsInk" width={11} height={11} patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
            <circle cx={5.5} cy={5.5} r={2.4} fill={INK} />
          </pattern>
          <pattern id="dotsInkFine" width={8} height={8} patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
            <circle cx={4} cy={4} r={1.3} fill={INK} />
          </pattern>
          <radialGradient id="burst" cx="0.5" cy="0.32" r="0.75">
            <stop offset="0" stopColor="#fff6c2" />
            <stop offset="0.35" stopColor="#ffd23f" />
            <stop offset="0.75" stopColor="#ff8a1f" />
            <stop offset="1" stopColor="#c2341a" />
          </radialGradient>
          <clipPath id="cHead">
            <path d={HEAD} />
          </clipPath>
          <clipPath id="cArmL">
            <path d={ARM_L} />
          </clipPath>
          <clipPath id="cArmR">
            <path d={ARM_R} />
          </clipPath>
          <clipPath id="cBody">
            <path d={BODY} />
          </clipPath>
          <clipPath id="cChest">
            <path d={CHEST} />
          </clipPath>
          <clipPath id="cNeck">
            <path d={NECK} />
          </clipPath>
        </defs>

        {/* ===== 背景：爆炸光 + 網點 + 集中線 ===== */}
        <rect width={1080} height={1920} fill="url(#burst)" />
        <rect width={1080} height={1920} fill="url(#dotsRed)" opacity={0.35} />
        <Speedlines />

        {/* ===== 手臂 ===== */}
        {[
          { d: ARM_L, clip: 'cArmL', shade: true, cx: 190, flip: -1 },
          { d: ARM_R, clip: 'cArmR', shade: false, cx: 890, flip: 1 },
        ].map((arm) => (
          <g key={arm.clip}>
            <path d={arm.d} fill={BLUE} />
            <g clipPath={`url(#${arm.clip})`}>
              {/* 肩頭紅色（三角肌） */}
              <ellipse cx={arm.cx} cy={1020} rx={150} ry={130} fill={RED} />
              <g stroke={INK} strokeWidth={2.4} fill="none">
                {[0, 1, 2, 3, 4].map((i) => (
                  <path key={i} d={`M${arm.cx - 150} ${960 + i * 34} Q${arm.cx} ${930 + i * 40} ${arm.cx + 150} ${960 + i * 34}`} />
                ))}
                {[-2, -1, 0, 1, 2].map((i) => (
                  <path key={i} d={`M${arm.cx + i * 20} 900 Q${arm.cx + i * 40} 1020 ${arm.cx + i * 60} 1150`} />
                ))}
              </g>
              <path d={`M${arm.cx - 150} 1120 Q${arm.cx} 1180 ${arm.cx + 150} 1120`} stroke={INK} strokeWidth={6} fill="none" />
              {arm.shade ? (
                <>
                  <path d="M0 900 L150 960 C110 1200 120 1500 150 1920 L0 1920 Z" fill={BLUE_SH} />
                  <path d="M0 900 L150 960 C110 1200 120 1500 150 1920 L0 1920 Z" fill="url(#dotsInk)" opacity={0.55} />
                  <path d={hatch([[150, 1180], [140, 1450], [150, 1750]], 36, 190, 13)} stroke={INK} strokeWidth={3} />
                </>
              ) : (
                <path d="M960 1100 C990 1250 990 1450 975 1650 L955 1650 C968 1450 966 1260 940 1120 Z" fill="#6f95ff" />
              )}
              {/* 二頭肌 */}
              <path d={`M${arm.cx - arm.flip * 40} 1330 C${arm.cx} 1300 ${arm.cx + arm.flip * 50} 1360 ${arm.cx + arm.flip * 60} 1440`} stroke={INK} strokeWidth={4} fill="none" />
            </g>
            <path d={arm.d} fill="none" stroke={INK} strokeWidth={10} strokeLinejoin="round" />
          </g>
        ))}

        {/* ===== 軀幹 ===== */}
        <path d={BODY} fill={BLUE} />
        <g clipPath="url(#cBody)">
          {/* 背闊肌陰影（左側） */}
          <path d="M240 920 C300 1100 330 1400 340 1920 L240 1920 Z" fill={BLUE_SH} />
          <path d="M240 920 C300 1100 330 1400 340 1920 L240 1920 Z" fill="url(#dotsInk)" opacity={0.5} />
          <path d="M250 940 C270 1040 290 1120 300 1200 C280 1120 262 1040 250 940 Z" fill={INK} />
          <path d="M820 1000 C800 1200 780 1400 770 1700" stroke="#6f95ff" strokeWidth={10} fill="none" strokeLinecap="round" />
          {/* 胸前紅色區塊 */}
          <path d={CHEST} fill={RED} />
          <g clipPath="url(#cChest)">
            {/* 左側陰影 + 網點 */}
            <path d="M260 920 C360 1000 400 1180 380 1400 C370 1500 400 1580 460 1620 L240 1620 Z" fill={RED_SH} />
            <path d="M260 920 C360 1000 400 1180 380 1400 C370 1500 400 1580 460 1620 L240 1620 Z" fill="url(#dotsInk)" opacity={0.4} />
            {/* 胸肌下方黑色陰影（spot black） */}
            <path d={`${PEC_L} C470 1290 380 1270 300 1150 Z`} fill={INK} />
            <path d={`${PEC_R} C760 1200 700 1260 620 1268 C590 1268 566 1252 550 1230 Z`} fill={INK} opacity={0.85} />
            {/* 胸骨中線 */}
            <path d="M540 980 C536 1080 538 1160 540 1240" stroke={INK} strokeWidth={6} fill="none" strokeLinecap="round" />
            {/* 腹肌 */}
            {[1320, 1410, 1500].map((y, i) => (
              <g key={y}>
                <path d={`M448 ${y} C480 ${y + 22} 512 ${y + 22} 532 ${y + 6}`} stroke={INK} strokeWidth={6 - i} fill="none" strokeLinecap="round" />
                <path d={`M548 ${y + 6} C568 ${y + 22} 600 ${y + 22} 632 ${y}`} stroke={INK} strokeWidth={4 - i * 0.6} fill="none" strokeLinecap="round" />
              </g>
            ))}
            <path d="M540 1260 L540 1600" stroke={INK} strokeWidth={4} />
            {/* 右上亮部 */}
            <path d="M640 960 C720 975 770 1020 790 1110 C750 1060 700 1020 630 1000 Z" fill="#ff6b77" />
            {/* 蛛網 */}
            <g stroke={INK} strokeWidth={2.6} fill="none">
              {[-6, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6].map((i) => (
                <path key={i} d={`M540 1060 C${540 + i * 40} 1180 ${540 + i * 70} 1350 ${540 + i * 92} 1640`} />
              ))}
              {[1000, 1090, 1190, 1300, 1420, 1540].map((y, j) => (
                <path key={y} d={`M${250 - j * 4} ${y + 30} C380 ${y - 30} 460 ${y - 50 + j * 3} 540 ${y - 46 + j * 4} C620 ${y - 50 + j * 3} 700 ${y - 30} ${830 + j * 4} ${y + 30}`} />
              ))}
            </g>
            {/* 陰影邊緣排線 */}
            <path d={hatch([[372, 1000], [392, 1200], [376, 1420]], 34, 200, 12)} stroke={INK} strokeWidth={2.5} />
          </g>
          {/* 胸前蜘蛛 */}
          <g transform="translate(540 1080)" fill={INK} stroke={INK} strokeLinecap="round" strokeLinejoin="round">
            <ellipse rx={20} ry={32} />
            <ellipse cy={-36} rx={13} ry={14} />
            <g strokeWidth={9} fill="none">
              <path d="M-14 -18 L-56 -52 L-66 -104" />
              <path d="M14 -18 L56 -52 L66 -104" />
              <path d="M-16 -4 L-76 -12 L-104 -52" />
              <path d="M16 -4 L76 -12 L104 -52" />
              <path d="M-16 12 L-70 34 L-94 84" />
              <path d="M16 12 L70 34 L94 84" />
              <path d="M-12 24 L-42 70 L-50 128" />
              <path d="M12 24 L42 70 L50 128" />
            </g>
          </g>
          {/* 紅色區塊外框 */}
          <path d={CHEST} fill="none" stroke={INK} strokeWidth={6} />
        </g>
        <path d={BODY} fill="none" stroke={INK} strokeWidth={11} strokeLinejoin="round" />

        {/* ===== 頸部 ===== */}
        <path d={NECK} fill={RED} />
        <g clipPath="url(#cNeck)">
          <path d="M440 740 L560 740 C520 800 500 860 500 920 L420 920 Z" fill={INK} />
          <path d="M600 760 C610 820 620 870 650 910" stroke={INK} strokeWidth={5} fill="none" />
          <g stroke={INK} strokeWidth={2} fill="none">
            {[800, 850, 900].map((y) => (
              <path key={y} d={`M440 ${y} C520 ${y - 14} 580 ${y - 14} 650 ${y}`} />
            ))}
          </g>
        </g>
        <path d={NECK} fill="none" stroke={INK} strokeWidth={8} />

        {/* ===== 頭部 ===== */}
        <path d={HEAD} fill={RED} />
        <g clipPath="url(#cHead)">
          {/* 左側陰影 + 網點 */}
          <path d="M320 280 C430 330 450 500 430 620 C420 720 470 800 560 860 L320 860 Z" fill={RED_SH} />
          <path d="M320 280 C430 330 450 500 430 620 C420 720 470 800 560 860 L320 860 Z" fill="url(#dotsInk)" opacity={0.45} />
          {/* 顴骨與下巴的黑色陰影 */}
          <path d="M330 520 C360 620 390 700 450 770 C420 700 400 620 396 540 Z" fill={INK} />
          <path d="M440 790 C500 830 590 830 650 780 C620 840 580 850 540 852 C500 850 470 830 440 790 Z" fill={INK} />
          {/* 鼻子與嘴部的面罩起伏 */}
          <path d="M548 600 C560 640 566 670 552 688" stroke={INK} strokeWidth={5} fill="none" strokeLinecap="round" />
          <path d="M500 742 C524 752 556 752 580 740" stroke={INK} strokeWidth={4} fill="none" strokeLinecap="round" />
          {/* 右上亮部 */}
          <path d="M600 310 C690 340 734 420 740 510 C708 440 666 384 600 350 Z" fill="#ff6b77" />
          {/* 蛛網：放射線 */}
          <g stroke={INK} strokeWidth={3} fill="none">
            {[...Array(16)].map((_, i) => {
              const a = (i / 16) * Math.PI * 2 - Math.PI / 2;
              const ex = 540 + Math.cos(a) * 520;
              const ey = 560 + Math.sin(a) * 560;
              const cx = 540 + Math.cos(a + 0.1) * 230;
              const cy = 560 + Math.sin(a + 0.1) * 250;
              return <path key={i} d={`M540 560 Q${cx} ${cy} ${ex} ${ey}`} />;
            })}
            {[60, 115, 175, 240, 310].map((r) => {
              // 每段弧線略為下垂，模仿漫畫的網狀畫法
              const n = 16;
              let d = '';
              for (let i = 0; i <= n; i++) {
                const a = (i / n) * Math.PI * 2 - Math.PI / 2;
                const x = 540 + Math.cos(a) * r * 0.95;
                const y = 560 + r * 0.06 + Math.sin(a) * r * 1.05;
                if (i === 0) d = `M${x} ${y}`;
                else {
                  const am = ((i - 0.5) / n) * Math.PI * 2 - Math.PI / 2;
                  const mx = 540 + Math.cos(am) * r * 0.86;
                  const my = 560 + r * 0.06 + Math.sin(am) * r * 0.95;
                  d += ` Q${mx} ${my} ${x} ${y}`;
                }
              }
              return <path key={r} d={d} />;
            })}
          </g>
          {/* 陰影邊緣排線 */}
          <path d={hatch([[430, 380], [446, 520], [430, 660]], 30, 195, 11)} stroke={INK} strokeWidth={2.4} />
        </g>
        {/* 頭部外框：右側亮面細、左側陰影粗 */}
        <path d={HEAD} fill="none" stroke={INK} strokeWidth={9} />
        <path d="M400 330 C350 390 330 470 338 560 C346 650 380 720 430 780" stroke={INK} strokeWidth={10} fill="none" strokeLinecap="round" />

        {/* 眼睛：粗黑邊白色鏡片，帶憤怒角度 */}
        {[
          { d: 'M522 548 C512 488 462 438 382 432 C362 488 372 562 412 604 C452 638 516 618 522 548 Z', hi: 'M408 470 C430 458 462 462 482 482' },
          { d: 'M558 548 C568 488 618 438 698 432 C718 488 708 562 668 604 C628 638 564 618 558 548 Z', hi: 'M604 484 C624 462 656 456 680 462' },
        ].map((e, i) => (
          <g key={i}>
            <path d={e.d} fill="#ffffff" stroke={INK} strokeWidth={20} strokeLinejoin="round" />
            <path d={e.d} fill="url(#dotsInkFine)" opacity={i === 0 ? 0.25 : 0.08} />
            <path d={e.hi} stroke="#c9d6ff" strokeWidth={7} strokeLinecap="round" fill="none" />
          </g>
        ))}
      </svg>

      {/* 紙張質感 */}
      <AbsoluteFill
        style={{ backgroundImage: `url(${staticFile('assets/grain.png')})`, backgroundSize: '512px 512px', mixBlendMode: 'multiply', opacity: 0.1 }}
      />

      {/* 漫畫說明框 */}
      <div
        style={{
          position: 'absolute',
          left: 80,
          top: 120,
          padding: '14px 28px',
          background: '#ffe94a',
          border: `6px solid ${INK}`,
          boxShadow: `10px 10px 0 ${INK}`,
          transform: 'rotate(-3deg)',
          fontFamily: FONTS.sans,
          fontWeight: 900,
          fontSize: 54,
          color: INK,
          letterSpacing: '0.06em',
        }}
      >
        英雄、
      </div>
      {/* 音效字 */}
      <div
        style={{
          position: 'absolute',
          right: 60,
          top: 1650,
          transform: 'rotate(-10deg)',
          fontFamily: FONTS.sans,
          fontWeight: 900,
          fontSize: 120,
          color: '#ffffff',
          WebkitTextStroke: `10px ${INK}`,
          paintOrder: 'stroke fill',
          textShadow: `8px 8px 0 ${INK}`,
          letterSpacing: '0.02em',
        }}
      >
        THWIP!
      </div>
    </AbsoluteFill>
  );
};

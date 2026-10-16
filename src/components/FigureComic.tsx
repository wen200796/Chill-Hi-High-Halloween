import React from 'react';
import { Archetype } from '../config/characters';
import { Arm, BaseBody, BODY, bodyPath, Head, Limb, Shape } from './Figure';

/**
 * 美式漫畫風（C 風格）角色：與剪影版共用同一套人體結構與 viewBox（-60 -40 520 1060），
 * 但改為彩色服裝 + 墨線外框 + 大塊黑影 + 網點陰影 + 排線 + 高光。
 * 主光源在右上方，陰影落在畫面左側。
 */

export const INK = '#0b0709';
const SKIN = '#f2c49b';
const SKIN_PALE = '#f6efe4';

type A = Archetype | 'everyday';

type Props = {
  archetype: A;
  uid: string;
  t?: number;
  walk?: number;
  /** 背光顏色與強度 */
  glow?: string;
  glowStrength?: number;
  /** 右上主光的邊緣高光顏色 */
  rimRight?: string;
  /** 左側補光顏色 */
  rimLeft?: string;
  /** 整體亮度（舞台場景用） */
  light?: number;
  style?: React.CSSProperties;
};

type P = [number, number];

/** 沿折線產生排線 */
export const hatch = (pts: P[], len: number, angleDeg: number, step: number) => {
  const out: string[] = [];
  const a = (angleDeg * Math.PI) / 180;
  for (let i = 0; i < pts.length - 1; i++) {
    const [x1, y1] = pts[i];
    const [x2, y2] = pts[i + 1];
    const seg = Math.hypot(x2 - x1, y2 - y1);
    for (let s = 0; s < seg; s += step) {
      const k = 0.55 + 0.45 * Math.abs(Math.sin((s / seg) * Math.PI));
      const x = x1 + ((x2 - x1) * s) / seg;
      const y = y1 + ((y2 - y1) * s) / seg;
      out.push(`M${x.toFixed(1)} ${y.toFixed(1)} l${(Math.cos(a) * len * k).toFixed(1)} ${(Math.sin(a) * len * k).toFixed(1)}`);
    }
  }
  return out.join(' ');
};

// ------------------------------------------------------------------ 臉部

/** 英雄下半臉（面罩下方）：嘴、下巴、鼻影 */
const HeroJaw: React.FC<{ y?: number }> = ({ y = 0 }) => (
  <g stroke={INK} fill="none" strokeLinecap="round">
    <path d={`M200 ${150 + y} L194 ${166 + y} L204 ${167 + y}`} strokeWidth={2.5} />
    <path d={`M186 ${181 + y} Q200 ${185 + y} 214 ${180 + y}`} strokeWidth={3} />
    <path d={`M196 ${193 + y} Q200 ${196 + y} 204 ${193 + y}`} strokeWidth={2} />
  </g>
);

/** 面罩眼洞（白眼 + 小瞳孔 + 怒眉） */
const MaskEyes: React.FC<{ iris?: string; glowWhite?: boolean }> = ({ iris = '#2a5bd7', glowWhite }) => (
  <g>
    {[-1, 1].map((s) => (
      <g key={s}>
        <path d={`M${200 + s * 8} 136 Q${200 + s * 20} 126 ${200 + s * 32} 132 Q${200 + s * 22} 144 ${200 + s * 8} 140 Z`} fill="#fff" stroke={INK} strokeWidth={2.5} />
        {glowWhite ? null : <circle cx={200 + s * 19} cy={135} r={3.4} fill={iris} stroke={INK} strokeWidth={1.2} />}
        <path d={`M${200 + s * 6} 128 L${200 + s * 34} 120`} stroke={INK} strokeWidth={4} strokeLinecap="round" />
      </g>
    ))}
  </g>
);

/** 日式漫畫大眼 */
const AnimeEyes: React.FC<{ iris: string; lash?: string }> = ({ iris, lash = INK }) => (
  <g>
    {[-1, 1].map((s) => {
      const cx = 200 + s * 18;
      return (
        <g key={s}>
          <ellipse cx={cx} cy={140} rx={10} ry={13} fill="#fff" />
          <ellipse cx={cx} cy={142} rx={8} ry={11} fill={iris} stroke={INK} strokeWidth={1.2} />
          <ellipse cx={cx} cy={144} rx={4} ry={6} fill={INK} />
          <circle cx={cx + 3} cy={137} r={3} fill="#fff" />
          <path d={`M${cx - 12} ${131 + (s > 0 ? 1 : 0)} Q${cx} ${123} ${cx + 12} ${130}`} stroke={lash} strokeWidth={4} fill="none" strokeLinecap="round" />
          <path d={`M${cx - 9} 116 Q${cx} ${112} ${cx + 9} 116`} stroke={lash} strokeWidth={2} fill="none" strokeLinecap="round" />
        </g>
      );
    })}
    <path d="M200 158 L198 164" stroke={INK} strokeWidth={1.6} strokeLinecap="round" />
    <path d="M194 178 Q200 181 206 178" stroke={INK} strokeWidth={2.2} fill="none" strokeLinecap="round" />
  </g>
);

// ------------------------------------------------------------------ 服裝上色（依前後順序）

const Costume: React.FC<{ a: A; t: number; walk: number; uid: string }> = ({ a, t, walk, uid }) => {
  const sway = Math.sin(t * 5);
  const bodyMask = `url(#${uid}-body)`;
  switch (a) {
    case 'shield':
      return (
        <g>
          <g fill="#2a5bd7">
            <BaseBody legSpread={14} />
          </g>
          <g mask={bodyMask}>
            {/* 腹部紅白直條 */}
            {[0, 1, 2, 3, 4, 5].map((i) => (
              <rect key={i} x={152 + i * 16} y={392} width={16} height={86} fill={i % 2 ? '#f3f3f3' : '#d42a2a'} />
            ))}
            <rect x={136} y={476} width={128} height={22} fill="#5b3a1e" />
            {/* 紅色長靴 */}
            <rect x={0} y={830} width={400} height={200} fill="#d42a2a" />
            <path d="M120 830 L280 830" stroke={INK} strokeWidth={4} />
          </g>
          {/* 紅手套 */}
          <g fill="#d42a2a">
            <Limb a={[108, 470]} b={[106, 522]} r1={16} r2={14} />
            <ellipse cx={106} cy={534} rx={16} ry={19} />
            <Limb a={[292, 470]} b={[294, 522]} r1={16} r2={14} />
            <ellipse cx={294} cy={534} rx={16} ry={19} />
          </g>
          {/* 頭盔 + 下半臉 */}
          <g fill="#2a5bd7">
            <Head />
          </g>
          <path d="M156 150 Q200 156 244 150 L244 170 Q236 196 200 200 Q164 196 156 170 Z" fill={SKIN} />
          <path d="M150 128 L118 104 L126 126 L112 120 L124 142 L152 150 Z" fill="#f3f3f3" stroke={INK} strokeWidth={2} />
          <path d="M250 128 L282 104 L274 126 L288 120 L276 142 L248 150 Z" fill="#f3f3f3" stroke={INK} strokeWidth={2} />
          <path d="M188 116 L200 88 L212 116 L206 116 L203 108 L197 108 L194 116 Z" fill="#f3f3f3" stroke={INK} strokeWidth={1.5} />
          <MaskEyes />
          <HeroJaw />
          <path transform="translate(200 312) scale(1.1)" d="M0 -30 L8 -9 L29 -9 L12 4 L18 25 L0 12 L-18 25 L-12 4 L-29 -9 L-8 -9 Z" fill="#f3f3f3" stroke={INK} strokeWidth={2} />
        </g>
      );
    case 'spider':
      return (
        <g>
          <g fill="#2348b8">
            <BaseBody {...BODY.spider} armRaisedRight />
          </g>
          <g mask={bodyMask}>
            {/* 紅色：胸前、腰帶、靴子；藍色：身側與大腿 */}
            <path d="M150 230 L250 230 L246 470 Q200 520 154 470 Z" fill="#d11a2e" />
            <rect x={0} y={200} width={400} height={50} fill="#d11a2e" />
            <rect x={0} y={790} width={400} height={240} fill="#d11a2e" />
            <g stroke={INK} strokeWidth={1.6} fill="none">
              {[250, 290, 330, 370, 410, 450].map((y) => (
                <path key={y} d={`M150 ${y} Q200 ${y + 14} 250 ${y}`} />
              ))}
              <path d="M200 236 L200 500 M176 236 L166 480 M224 236 L234 480" />
              {[820, 860, 900, 940].map((y) => (
                <path key={y} d={`M100 ${y} Q150 ${y + 8} 200 ${y} Q250 ${y + 8} 300 ${y}`} />
              ))}
            </g>
          </g>
          {/* 手臂紅色前臂與手套 */}
          <g fill="#d11a2e">
            <Limb a={[108, 420]} b={[106, 520]} r1={14} r2={11} />
            <ellipse cx={106} cy={532} rx={15} ry={18} />
            <Limb a={[334, 176]} b={[338, 98]} r1={14} r2={11} />
            <ellipse cx={339} cy={88} rx={15} ry={18} />
          </g>
          <g fill="#d11a2e">
            <Head rx={45} />
          </g>
          {/* 面罩蛛網 */}
          <g clipPath={`url(#${uid}-headClip)`} stroke={INK} strokeWidth={1.6} fill="none">
            {[...Array(12)].map((_, i) => {
              const ang = (i * Math.PI * 2) / 12 + 0.26;
              return <line key={i} x1={200} y1={134} x2={200 + Math.cos(ang) * 90} y2={134 + Math.sin(ang) * 100} />;
            })}
            {[16, 30, 44, 58, 72].map((r) => (
              <ellipse key={r} cx={200} cy={134} rx={r} ry={r * 1.15} />
            ))}
          </g>
          <path d="M160 124 Q176 100 196 130 Q184 154 164 142 Z" fill="#f4f6ff" stroke={INK} strokeWidth={5} />
          <path d="M240 124 Q224 100 204 130 Q216 154 236 142 Z" fill="#f4f6ff" stroke={INK} strokeWidth={5} />
          {/* 胸前蜘蛛 */}
          <g transform="translate(200 296)" stroke={INK} strokeWidth={3.5} fill={INK} strokeLinecap="round">
            <ellipse rx={7} ry={13} />
            <path d="M-5 -6 L-24 -20 L-28 -36 M5 -6 L24 -20 L28 -36 M-6 2 L-28 -2 L-36 -16 M6 2 L28 -2 L36 -16 M-6 8 L-24 20 L-30 36 M6 8 L24 20 L30 36 M-4 12 L-14 32 L-16 50 M4 12 L14 32 L16 50" fill="none" />
          </g>
        </g>
      );
    case 'knight': {
      const flare = 30 + sway * 18;
      return (
        <g>
          {/* 披風 */}
          <path
            d={`M126 238 Q${70 - flare * 0.4} 600 ${8 - flare} 985 L60 960 L110 990 L160 962 L200 992 L240 962 L290 990 L340 960 L${392 + flare} 985 Q${330 + flare * 0.4} 600 274 238 Z`}
            fill="#1d1f2b"
          />
          <path d={`M150 300 Q120 600 ${90 - flare * 0.6} 960`} stroke="#3a3f55" strokeWidth={3} fill="none" />
          <path d={`M250 300 Q280 600 ${310 + flare * 0.6} 960`} stroke="#3a3f55" strokeWidth={3} fill="none" />
          <g fill="#8a909e">
            <BaseBody legSpread={18} />
          </g>
          <g mask={bodyMask}>
            <rect x={0} y={470} width={400} height={30} fill="#e0b52a" />
            {[156, 184, 216, 244].map((x) => (
              <rect key={x} x={x - 7} y={474} width={14} height={22} rx={3} fill="#b38a12" />
            ))}
            <rect x={0} y={500} width={400} height={80} fill="#1d1f2b" />
            <rect x={0} y={860} width={400} height={200} fill="#1d1f2b" />
          </g>
          <g fill="#1d1f2b">
            <Limb a={[108, 440]} b={[106, 522]} r1={16} r2={13} />
            <ellipse cx={106} cy={534} rx={16} ry={19} />
            <Limb a={[292, 440]} b={[294, 522]} r1={16} r2={13} />
            <ellipse cx={294} cy={534} rx={16} ry={19} />
            <path d="M100 250 Q200 205 300 250 L292 300 L108 300 Z" />
            <Head rx={50} />
            <path d="M152 140 L160 44 L184 100 L216 100 L240 44 L248 140 Z" />
          </g>
          {/* 鰭狀手套 */}
          <path d="M92 460 L84 448 L94 452 L88 440 L100 446" stroke="#1d1f2b" strokeWidth={6} fill="none" />
          <path d="M156 156 Q200 162 244 156 L246 170 Q236 198 200 202 Q164 198 154 170 Z" fill={SKIN} />
          <MaskEyes glowWhite />
          <HeroJaw y={4} />
          <g transform="translate(200 322)">
            <ellipse rx={50} ry={28} fill="#f2c94c" stroke={INK} strokeWidth={4} />
            <path d="M0 -8 L-6 -18 L-10 -6 Q-26 -14 -44 -2 Q-30 0 -28 10 Q-18 4 -12 14 Q-4 8 0 18 Q4 8 12 14 Q18 4 28 10 Q30 0 44 -2 Q26 -14 10 -6 L6 -18 Z" fill={INK} />
          </g>
        </g>
      );
    }
    case 'plumber':
      return (
        <g>
          <g fill="#d8232c">
            <BaseBody {...BODY.plumber} />
          </g>
          <g mask={bodyMask}>
            <rect x={0} y={440} width={400} height={600} fill="#2453c9" />
            <rect x={158} y={330} width={84} height={130} rx={8} fill="#2453c9" />
            <path d="M146 232 L172 336 L186 336 L162 232 Z M254 232 L228 336 L214 336 L238 232 Z" fill="#2453c9" />
            <rect x={0} y={940} width={400} height={80} fill="#6a3a14" />
            <path d="M200 600 L200 940" stroke={INK} strokeWidth={3} />
          </g>
          <circle cx={172} cy={350} r={9} fill="#ffd23f" stroke={INK} strokeWidth={2} />
          <circle cx={228} cy={350} r={9} fill="#ffd23f" stroke={INK} strokeWidth={2} />
          <g fill="#f8f8f8" stroke={INK} strokeWidth={2.5}>
            <ellipse cx={104} cy={530} rx={19} ry={21} />
            <ellipse cx={296} cy={530} rx={19} ry={21} />
          </g>
          <g fill={SKIN}>
            <Head rx={50} />
          </g>
          {/* 鬢角頭髮 */}
          <path d="M152 118 Q146 150 156 168 L166 160 Q160 140 164 120 Z M248 118 Q254 150 244 168 L234 160 Q240 140 236 120 Z" fill="#3a1d0a" />
          {/* 眼睛與眉 */}
          {[-1, 1].map((s) => (
            <g key={s}>
              <ellipse cx={200 + s * 14} cy={132} rx={7} ry={12} fill="#fff" stroke={INK} strokeWidth={2} />
              <ellipse cx={200 + s * 13} cy={134} rx={4.5} ry={7} fill="#2a63d4" />
              <ellipse cx={200 + s * 13} cy={135} rx={2.5} ry={4} fill={INK} />
              <circle cx={200 + s * 13 + 1.5} cy={131} r={1.6} fill="#fff" />
              <path d={`M${200 + s * 6} 116 Q${200 + s * 15} 109 ${200 + s * 24} 116`} stroke={INK} strokeWidth={5} fill="none" strokeLinecap="round" />
            </g>
          ))}
          <ellipse cx={200} cy={152} rx={16} ry={13} fill="#f4a882" stroke={INK} strokeWidth={2.5} />
          <ellipse cx={205} cy={147} rx={5} ry={3} fill="#ffd9c4" />
          <path d="M166 170 Q178 158 192 166 Q200 160 208 166 Q222 158 234 170 Q220 182 206 176 Q200 180 194 176 Q180 182 166 170 Z" fill="#2a1408" stroke={INK} strokeWidth={2} />
          <path d="M192 188 Q200 192 208 188" stroke={INK} strokeWidth={2.4} fill="none" strokeLinecap="round" />
          {/* 帽子 */}
          <path d="M144 120 C140 50 260 50 256 120 Z" fill="#d8232c" stroke={INK} strokeWidth={3} />
          <path d="M134 118 Q200 104 266 118 Q262 132 200 130 Q138 132 134 118 Z" fill="#a3131c" stroke={INK} strokeWidth={3} />
          <circle cx={200} cy={86} r={19} fill="#fff" stroke={INK} strokeWidth={2} />
          <path d="M189 97 L189 76 L200 88 L211 76 L211 97 L206 97 L206 87 L200 94 L194 87 L194 97 Z" fill="#d8232c" />
        </g>
      );
    case 'scoutSoldier':
      return (
        <g>
          <path d={`M132 236 Q${92 - sway * 6} 520 ${84 - sway * 10} 700 L${316 + sway * 10} 700 Q${308 + sway * 6} 520 268 236 Z`} fill="#2f5d3a" />
          <g fill="#ece6d8">
            <BaseBody {...BODY.scoutSoldier} />
          </g>
          <g mask={bodyMask}>
            <rect x={0} y={200} width={400} height={240} fill="#8a5a36" />
            <rect x={180} y={226} width={40} height={210} fill="#f4f1ea" />
            <rect x={0} y={820} width={400} height={220} fill="#3a2414" />
          </g>
          <g fill="#8a5a36">
            <Arm s={[124, 272]} e={[115, 404]} w={[113, 518]} />
            <Arm s={[276, 272]} e={[285, 404]} w={[287, 518]} />
          </g>
          {/* 皮帶 */}
          <g stroke="#5a3a1c" strokeWidth={6} fill="none">
            <path d="M144 300 L256 380 M256 300 L144 380" />
            <path d="M146 470 L254 470 M150 560 L176 640 M250 560 L224 640" />
          </g>
          <g fill={SKIN}>
            <Head rx={44} />
          </g>
          <AnimeEyes iris="#5a6270" />
          <path d="M148 150 C136 66 264 66 252 150 L254 186 L238 176 L236 140 Q216 120 200 128 Q184 118 164 140 L162 176 L146 186 Z" fill="#141018" stroke={INK} strokeWidth={2.5} />
          <path d="M170 92 Q190 84 206 90" stroke="#4a4058" strokeWidth={3} fill="none" />
          {/* 紅圍巾 */}
          <path d="M162 200 Q200 226 238 200 L242 236 Q200 256 158 236 Z" fill="#c8202a" stroke={INK} strokeWidth={2.5} />
          <path d="M170 232 Q160 300 176 360 L196 356 Q186 300 194 240 Z" fill="#a3121e" stroke={INK} strokeWidth={2.5} />
          {/* 雙刀 */}
          <g stroke={INK} strokeWidth={2.5}>
            <path d="M104 530 L36 742 L46 746 L114 534 Z" fill="#dfe6ef" />
            <path d="M296 530 L364 742 L354 746 L286 534 Z" fill="#dfe6ef" />
            <rect x={92} y={512} width={24} height={30} rx={4} fill="#55606e" />
            <rect x={284} y={512} width={24} height={30} rx={4} fill="#55606e" />
          </g>
          <path d="M60 690 L90 600 M340 690 L310 600" stroke="#fff" strokeWidth={3} opacity={0.8} />
        </g>
      );
    case 'joker':
      return (
        <g>
          <path d={`M126 250 L${78 - sway * 6} 800 L${322 + sway * 6} 800 L274 250 Z`} fill="#6a2fa0" />
          <g fill="#6a2fa0">
            <BaseBody legSpread={10} armRaisedRight />
          </g>
          <g mask={bodyMask}>
            <path d="M168 236 L232 236 L236 470 L164 470 Z" fill="#e8862a" />
            <path d="M184 226 L216 226 L210 300 L190 300 Z" fill="#3fae4a" />
            <rect x={0} y={940} width={400} height={100} fill="#2a1830" />
          </g>
          <path d="M168 236 L150 360 L130 250 Z M232 236 L250 360 L270 250 Z" fill="#4e1f7a" stroke={INK} strokeWidth={2.5} />
          <g fill={SKIN_PALE}>
            <Head rx={45} />
            <ellipse cx={106} cy={532} rx={15} ry={18} />
          </g>
          {/* 眼窩與眼睛 */}
          {[-1, 1].map((s) => (
            <g key={s}>
              <ellipse cx={200 + s * 18} cy={134} rx={14} ry={11} fill="#4a2a5a" opacity={0.85} />
              <ellipse cx={200 + s * 18} cy={135} rx={6} ry={4.5} fill="#f6f1c8" />
              <circle cx={200 + s * 18} cy={135} r={2.6} fill={INK} />
              <path d={`M${200 + s * 6} 118 L${200 + s * 32} 112`} stroke="#2a6a2a" strokeWidth={5} strokeLinecap="round" />
            </g>
          ))}
          <path d="M200 146 L196 160 L204 161" stroke={INK} strokeWidth={2} fill="none" />
          {/* 咧嘴大笑 */}
          <path d="M160 160 Q200 204 240 158 Q232 178 200 186 Q168 178 160 160 Z" fill="#c8102e" stroke={INK} strokeWidth={2.5} />
          <path d="M170 168 Q200 184 230 166 L226 172 Q200 186 174 174 Z" fill="#fff" stroke={INK} strokeWidth={1.2} />
          {/* 綠髮 */}
          <path
            d="M150 120 L136 76 L160 92 L158 56 L184 84 L196 44 L210 82 L232 50 L232 88 L262 70 L250 112 L268 112 L248 132 Q200 70 150 132 Z"
            fill="#3fae4a"
            stroke={INK}
            strokeWidth={3}
          />
          {/* 小丑牌 */}
          <g transform="translate(330 84) rotate(16)">
            <rect x={-38} y={-56} width={76} height={108} rx={8} fill="#f6f1e2" stroke={INK} strokeWidth={3} />
            <rect x={-31} y={-49} width={62} height={94} rx={5} fill="none" stroke="#6a1fa8" strokeWidth={3} />
            <path d="M-22 -8 Q-12 -34 0 -10 Q12 -34 22 -8 L14 14 L-14 14 Z" fill="#6a1fa8" />
            <circle cx={-22} cy={-10} r={5} fill="#2fbf55" />
            <circle cx={22} cy={-10} r={5} fill="#2fbf55" />
            <circle cx={0} cy={-12} r={5} fill="#e0213a" />
            <rect x={-14} y={18} width={28} height={8} rx={3} fill="#6a1fa8" />
          </g>
        </g>
      );
    case 'magicalGirl': {
      const s1 = Math.sin(t * 3.2) * 16;
      const s2 = Math.sin(t * 3.2 + 1.4) * 16;
      return (
        <g>
          <g fill="#f7d561" stroke={INK} strokeWidth={3}>
            <path d={`M150 84 Q${70 + s1} 300 ${88 + s1 * 1.6} 640 Q${100 + s1 * 1.6} 700 ${122 + s1 * 1.2} 640 Q${110 + s1} 360 168 92 Z`} />
            <path d={`M250 84 Q${330 + s2} 300 ${312 + s2 * 1.6} 640 Q${300 + s2 * 1.6} 700 ${278 + s2 * 1.2} 640 Q${290 + s2} 360 232 92 Z`} />
          </g>
          <g fill={SKIN}>
            <BaseBody legSpread={8} slim={16} armRaisedRight />
          </g>
          <g mask={bodyMask}>
            <rect x={0} y={226} width={400} height={240} fill="#f7f7fb" />
            <path d="M140 232 L200 300 L260 232 L270 280 L200 330 L130 280 Z" fill="#2a5ad8" />
            <rect x={0} y={820} width={400} height={220} fill="#d4263a" />
          </g>
          {/* 白手套 */}
          <g fill="#f7f7fb">
            <Limb a={[124, 420]} b={[122, 520]} r1={12} r2={10} />
            <ellipse cx={122} cy={532} rx={14} ry={17} />
            <Limb a={[330, 180]} b={[338, 98]} r1={12} r2={10} />
            <ellipse cx={339} cy={88} rx={14} ry={17} />
          </g>
          <path d="M146 455 L100 600 Q200 620 300 600 L254 455 Z" fill="#2a5ad8" stroke={INK} strokeWidth={3} />
          {[130, 165, 200, 235, 270].map((x) => (
            <path key={x} d={`M${200 + (x - 200) * 0.35} 460 L${x} 606`} stroke="#18388f" strokeWidth={2} />
          ))}
          <g fill={SKIN}>
            <Head rx={44} />
          </g>
          <AnimeEyes iris="#3a7be0" />
          <ellipse cx={176} cy={164} rx={9} ry={4} fill="#ff9aa8" opacity={0.6} />
          <ellipse cx={224} cy={164} rx={9} ry={4} fill="#ff9aa8" opacity={0.6} />
          {/* 瀏海與髮髻 */}
          <path d="M152 128 C150 74 250 74 248 128 L238 108 L228 126 L216 104 L204 124 L194 104 L182 126 L170 106 L162 128 Z" fill="#f7d561" stroke={INK} strokeWidth={2.5} />
          <circle cx={148} cy={86} r={30} fill="#f7d561" stroke={INK} strokeWidth={3} />
          <circle cx={252} cy={86} r={30} fill="#f7d561" stroke={INK} strokeWidth={3} />
          <path d="M184 100 L200 92 L216 100 L200 106 Z" fill="#ffd34a" stroke={INK} strokeWidth={2} />
          <circle cx={200} cy={99} r={4} fill="#e8264f" />
          {/* 胸前蝴蝶結 */}
          <path d="M200 286 L150 260 L158 312 Z" fill="#e8264f" stroke={INK} strokeWidth={2.5} />
          <path d="M200 286 L250 260 L242 312 Z" fill="#e8264f" stroke={INK} strokeWidth={2.5} />
          <circle cx={200} cy={286} r={11} fill="#ffd34a" stroke={INK} strokeWidth={2.5} />
          {/* 月亮魔法棒 */}
          <path d="M338 92 L346 30" stroke="#f2c0d8" strokeWidth={8} strokeLinecap="round" />
          <g transform="translate(348 20)">
            <path d="M8 -26 A26 26 0 1 0 8 26 A20 20 0 1 1 8 -26 Z" fill="#ffd34a" stroke={INK} strokeWidth={2.5} />
            <circle cx={-2} cy={0} r={6} fill="#ff5c9d" stroke={INK} strokeWidth={1.5} />
          </g>
        </g>
      );
    }
    case 'wizardStudent': {
      const sc = Math.sin(t * 4) * 14;
      return (
        <g>
          <path d={`M124 238 L${66 - sway * 5} 985 L${334 + sway * 5} 985 L276 238 Z`} fill="#17171f" />
          <path d={`M150 250 L${110 - sway * 5} 980`} stroke="#1d6b45" strokeWidth={6} />
          <path d={`M250 250 L${290 + sway * 5} 980`} stroke="#1d6b45" strokeWidth={6} />
          <g fill="#17171f">
            <BaseBody legSpread={6} armOutLeft />
          </g>
          <g mask={bodyMask}>
            <path d="M172 230 L228 230 L232 520 L168 520 Z" fill="#5d636b" />
            <path d="M180 226 L200 250 L220 226 L216 260 L200 270 L184 260 Z" fill="#f4f4f4" />
            <path d="M196 252 L204 252 L208 330 L200 340 L192 330 Z" fill="#1d6b45" />
            {[270, 290, 310].map((y) => (
              <path key={y} d={`M193 ${y} L207 ${y - 6}`} stroke="#c9d3d6" strokeWidth={4} />
            ))}
          </g>
          <g fill={SKIN}>
            <Head />
            <ellipse cx={31} cy={475} rx={14} ry={17} />
            <ellipse cx={294} cy={532} rx={14} ry={17} />
          </g>
          <AnimeEyes iris="#2f8a4a" />
          <circle cx={182} cy={140} r={16} fill="none" stroke={INK} strokeWidth={3.5} />
          <circle cx={218} cy={140} r={16} fill="none" stroke={INK} strokeWidth={3.5} />
          <line x1={198} y1={140} x2={202} y2={140} stroke={INK} strokeWidth={3} />
          {/* 亂髮 + 閃電疤 */}
          <path d="M152 118 Q150 72 196 74 Q252 70 250 120 L262 104 L252 138 Q236 100 214 112 L206 96 L196 114 L182 100 L172 120 Q160 112 148 140 L140 112 Z" fill="#141018" stroke={INK} strokeWidth={2.5} />
          <path d="M210 112 L204 120 L210 120 L204 128" stroke="#b02020" strokeWidth={2} fill="none" />
          {/* 兩側頭髮蓋住耳朵 */}
          <path d="M146 112 Q140 140 150 162 L162 156 Q156 136 160 118 Z M254 112 Q260 140 250 162 L238 156 Q244 136 240 118 Z" fill="#141018" stroke={INK} strokeWidth={2} />
          {/* 綠銀圍巾 */}
          <path
            d={`M168 214 Q200 236 232 214 L238 240 Q${260 + sc} 320 ${290 + sc} 410 L${262 + sc} 418 Q${238 + sc * 0.5} 330 214 252 Q200 258 168 240 Z`}
            fill="#1d6b45"
            stroke={INK}
            strokeWidth={2.5}
          />
          {[0, 1, 2, 3].map((i) => (
            <path key={i} d={`M${242 + i * 12 + sc * (0.2 + i * 0.2)} ${270 + i * 36} l26 -6 l4 14 l-26 6 Z`} fill="#c9d3d6" />
          ))}
          {/* 魔杖 */}
          <path d="M36 470 L-4 400" stroke="#8a5a2a" strokeWidth={7} strokeLinecap="round" />
          <circle cx={-4} cy={398} r={9} fill="#eafff3" />
        </g>
      );
    }
    case 'oldWizard':
      return (
        <g>
          <path d={`M124 238 L${60 - sway * 4} 985 L${340 + sway * 4} 985 L276 238 Z`} fill="#5b2d9a" />
          <g fill="#5b2d9a">
            <BaseBody legSpread={4} />
          </g>
          {/* 星星花紋 */}
          {[
            [120, 640],
            [260, 560],
            [180, 820],
            [300, 860],
            [90, 900],
            [230, 700],
          ].map(([x, y], i) => (
            <path key={i} transform={`translate(${x} ${y}) scale(0.5)`} d="M0 -20 L5 -6 L19 -6 L8 3 L12 17 L0 8 L-12 17 L-8 3 L-19 -6 L-5 -6 Z" fill="#ffd36b" />
          ))}
          <path d="M70 70 L84 985" stroke="#7a4a20" strokeWidth={14} strokeLinecap="round" />
          <g fill={SKIN}>
            <Head rx={46} />
            <ellipse cx={106} cy={532} rx={15} ry={18} />
          </g>
          {/* 長髮 */}
          <path d="M156 110 Q140 200 150 300 L170 290 Q160 200 170 130 Z M244 110 Q260 200 250 300 L230 290 Q240 200 230 130 Z" fill="#d6dae2" stroke={INK} strokeWidth={2} />
          {/* 眼、半月眼鏡、鼻 */}
          {[-1, 1].map((s) => (
            <g key={s}>
              <path d={`M${200 + s * 10} 134 Q${200 + s * 18} 130 ${200 + s * 26} 134`} stroke={INK} strokeWidth={3} fill="none" />
              <circle cx={200 + s * 18} cy={136} r={2.5} fill="#3a7be0" />
              <path d={`M${200 + s * 6} 124 Q${200 + s * 18} 116 ${200 + s * 30} 124`} stroke="#e6e8ee" strokeWidth={5} fill="none" strokeLinecap="round" />
              <path d={`M${200 + s * 6} 140 A12 9 0 0 0 ${200 + s * 30} 140 Z`} fill="none" stroke="#c9a24a" strokeWidth={2.5} />
            </g>
          ))}
          <path d="M200 140 L194 166 Q200 170 206 166" stroke={INK} strokeWidth={2.5} fill="none" />
          {/* 銀白長鬍 */}
          <path d="M158 164 Q200 196 242 164 Q246 300 200 470 Q154 300 158 164 Z" fill="#e6e8ee" stroke={INK} strokeWidth={3} />
          <g stroke="#9aa0ad" strokeWidth={2} fill="none">
            <path d="M200 196 Q206 320 200 440" />
            <path d="M180 196 Q178 300 190 400" />
            <path d="M220 196 Q222 300 210 400" />
          </g>
          <path d="M184 172 Q200 166 216 172" stroke="#9aa0ad" strokeWidth={3} fill="none" />
          {/* 尖帽 */}
          <ellipse cx={200} cy={104} rx={108} ry={20} fill="#4a2380" stroke={INK} strokeWidth={3} />
          <path d={`M138 104 Q178 40 ${222 + sway * 3} 4 Q${236 + sway * 3} 0 ${238 + sway * 3} 14 Q214 52 262 104 Z`} fill="#5b2d9a" stroke={INK} strokeWidth={3} />
          <path transform="translate(214 64) scale(0.5)" d="M0 -20 L5 -6 L19 -6 L8 3 L12 17 L0 8 L-12 17 L-8 3 L-19 -6 L-5 -6 Z" fill="#ffd36b" />
          {/* 法杖光球 */}
          <circle cx={72} cy={66} r={22} fill="#fff3c4" stroke={INK} strokeWidth={2} />
        </g>
      );
    case 'everyday': {
      const bob = Math.abs(Math.sin(walk * Math.PI * 2)) * -10;
      const tilt = Math.sin(walk * Math.PI * 2) * 1.5;
      return (
        <g transform={`translate(0 ${bob}) rotate(${tilt} 200 990)`}>
          <g fill="#3d5a8a">
            <BaseBody legSpread={6 + Math.sin(walk * Math.PI * 2) * 8} slim={4} />
          </g>
          <g mask={bodyMask}>
            <rect x={0} y={200} width={400} height={350} fill="#e46a3a" />
            <rect x={0} y={950} width={400} height={80} fill="#f2f2f2" />
          </g>
          <g fill={SKIN}>
            <Head />
            <ellipse cx={106} cy={532} rx={15} ry={18} />
            <ellipse cx={294} cy={532} rx={15} ry={18} />
          </g>
          <path d="M150 136 C146 70 254 70 250 136 C252 160 246 180 240 190 Q200 196 160 190 C154 180 148 160 150 136 Z" fill="#2a1a12" stroke={INK} strokeWidth={2.5} />
          <path d="M134 500 Q200 520 266 500 L270 548 Q200 566 130 548 Z" fill="#c8552c" />
        </g>
      );
    }
  }
};

/** 依角色決定陰影遮罩用的身體參數 */
const bodyParams = (a: A) => {
  switch (a) {
    case 'shield':
      return { legSpread: 14, slim: 0, raised: false, out: false };
    case 'spider':
      return { ...BODY.spider, raised: true, out: false };
    case 'knight':
      return { legSpread: 18, slim: 0, raised: false, out: false };
    case 'plumber':
      return { ...BODY.plumber, raised: false, out: false };
    case 'scoutSoldier':
      return { ...BODY.scoutSoldier, raised: false, out: false };
    case 'joker':
      return { legSpread: 10, slim: 0, raised: true, out: false };
    case 'magicalGirl':
      return { legSpread: 8, slim: 16, raised: true, out: false };
    case 'wizardStudent':
      return { legSpread: 6, slim: 0, raised: false, out: true };
    case 'oldWizard':
      return { legSpread: 4, slim: 0, raised: false, out: false };
    default:
      return { legSpread: 6, slim: 4, raised: false, out: false };
  }
};

const MUSCULAR = new Set<A>(['shield', 'spider', 'knight']);

export const FigureComic: React.FC<Props> = ({
  archetype,
  uid,
  t = 0,
  walk = 0,
  glow = '#8b3dff',
  glowStrength = 0.5,
  rimRight = '#ffffff',
  rimLeft = '#8b3dff',
  light = 1,
  style,
}) => {
  const bp = bodyParams(archetype);
  const SHADOW =
    'M-80 -60 L166 -60 C152 20 150 90 164 150 C172 190 150 230 146 280 C140 360 152 440 158 520 C160 600 168 700 170 800 C172 880 176 960 178 1060 L-80 1060 Z';
  return (
    <svg viewBox="-60 -40 520 1060" style={{ overflow: 'visible', ...style }}>
      <defs>
        <mask id={`${uid}-sil`} maskUnits="userSpaceOnUse" x={-200} y={-200} width={800} height={1400}>
          <g fill="#fff">
            <Shape a={archetype} t={t} walk={walk} />
          </g>
        </mask>
        <mask id={`${uid}-body`} maskUnits="userSpaceOnUse" x={-200} y={-200} width={800} height={1400}>
          <path d={bodyPath(bp.legSpread, bp.slim)} fill="#fff" />
        </mask>
        <clipPath id={`${uid}-headClip`}>
          <path d="M155 132 C155 74 245 74 245 132 C245 168 225 196 200 200 C175 196 155 168 155 132 Z" />
        </clipPath>
        <pattern id={`${uid}-dots`} width={7} height={7} patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
          <circle cx={3.5} cy={3.5} r={1.7} fill={INK} />
        </pattern>
        <filter id={`${uid}-ink`} x="-40%" y="-20%" width="180%" height="140%">
          {/* 背光 */}
          <feGaussianBlur in="SourceAlpha" stdDeviation={20} result="halo" />
          <feFlood floodColor={glow} floodOpacity={glowStrength} />
          <feComposite in2="halo" operator="in" result="haloC" />
          {/* 墨線外框（左側較粗） */}
          <feMorphology in="SourceAlpha" operator="dilate" radius={3.6} result="dil" />
          <feOffset in="dil" dx={-1.5} dy={1} result="dil2" />
          <feMerge result="dilAll">
            <feMergeNode in="dil" />
            <feMergeNode in="dil2" />
          </feMerge>
          <feFlood floodColor={INK} />
          <feComposite in2="dilAll" operator="in" result="outline" />
          {/* 右上主光邊緣高光 */}
          <feOffset in="SourceAlpha" dx={-3.5} dy={3} result="o1" />
          <feComposite in="SourceAlpha" in2="o1" operator="out" result="e1" />
          <feFlood floodColor={rimRight} floodOpacity={0.45} />
          <feComposite in2="e1" operator="in" result="r1" />
          {/* 左側補光 */}
          <feOffset in="SourceAlpha" dx={3} dy={1.5} result="o2" />
          <feComposite in="SourceAlpha" in2="o2" operator="out" result="e2" />
          <feFlood floodColor={rimLeft} floodOpacity={0.35} />
          <feComposite in2="e2" operator="in" result="r2" />
          <feMerge>
            <feMergeNode in="haloC" />
            <feMergeNode in="outline" />
            <feMergeNode in="SourceGraphic" />
            <feMergeNode in="r1" />
            <feMergeNode in="r2" />
          </feMerge>
        </filter>
      </defs>
      <g filter={`url(#${uid}-ink)`}>
        <g style={light < 1 ? { filter: `brightness(${0.35 + 0.65 * light})` } : undefined}>
          <Costume a={archetype} t={t} walk={walk} uid={uid} />
          {/* 陰影、網點、排線、黑影：只畫在角色範圍內 */}
          <g mask={`url(#${uid}-sil)`}>
            <path d={SHADOW} fill="#2a0c48" opacity={0.42} style={{ mixBlendMode: 'multiply' }} />
            <path d={SHADOW} fill={`url(#${uid}-dots)`} opacity={0.3} />
            <path
              d={hatch(
                [
                  [166, -40],
                  [152, 40],
                  [164, 150],
                  [148, 250],
                  [146, 300],
                  [152, 440],
                  [160, 600],
                  [170, 800],
                  [178, 1000],
                ],
                16,
                200,
                7,
              )}
              stroke={INK}
              strokeWidth={1.5}
              opacity={0.75}
            />
            {/* 下巴陰影 */}
            <path d="M166 200 Q200 218 234 200 L232 222 Q200 236 168 222 Z" fill={INK} opacity={0.75} />
            {/* 腋下與兩腿之間 */}
            <path d="M128 296 L146 300 L140 350 Z" fill={INK} />
            <path d={`M200 590 L${198 - bp.legSpread * 0.2} 960`} stroke={INK} strokeWidth={5} />
          </g>
          {/* 肌肉線條 */}
          {MUSCULAR.has(archetype) ? (
            <g stroke={INK} strokeWidth={2.6} fill="none" strokeLinecap="round" opacity={0.85}>
              <path d="M150 334 Q174 356 197 342 M203 342 Q226 356 250 334" />
              <path d="M200 296 L200 340" />
              {[388, 418, 448].map((y) => (
                <path key={y} d={`M180 ${y} Q190 ${y + 6} 197 ${y} M203 ${y} Q210 ${y + 6} 220 ${y}`} />
              ))}
              <path d="M108 300 Q118 288 134 296 M266 296 Q282 288 292 300" />
              <path d={`M${152 - bp.legSpread * 0.5} 780 Q${162 - bp.legSpread * 0.5} 790 ${172 - bp.legSpread * 0.5} 780 M${228 + bp.legSpread * 0.5} 780 Q${238 + bp.legSpread * 0.5} 790 ${248 + bp.legSpread * 0.5} 780`} />
              <path d={`M${160 - bp.legSpread * 0.2} 620 Q${166} 700 ${158 - bp.legSpread * 0.4} 760`} />
            </g>
          ) : null}
          {/* 盾牌（畫在最前面） */}
          {archetype === 'shield' ? (
            <g transform="translate(150 395)">
              <circle r={104} fill="#c41e30" stroke={INK} strokeWidth={4} />
              <circle r={84} fill="#e9ecf4" />
              <circle r={64} fill="#c41e30" />
              <circle r={44} fill="#2a5bd7" />
              <path d="M0 -36 L10 -11 L35 -11 L15 5 L22 30 L0 15 L-22 30 L-15 5 L-35 -11 L-10 -11 Z" fill="#f3f3f3" />
              <path d="M-104 0 A104 104 0 0 0 30 100 A120 120 0 0 1 -104 0 Z" fill={INK} opacity={0.5} />
              <path d="M40 -80 A90 90 0 0 1 90 -30" stroke="#fff" strokeWidth={6} fill="none" strokeLinecap="round" opacity={0.8} />
            </g>
          ) : null}
          {/* 法杖光球、魔杖光芒 */}
          {archetype === 'oldWizard' ? <circle cx={72} cy={66} r={40} fill="#ffe08a" opacity={0.35} /> : null}
          {archetype === 'wizardStudent' ? <circle cx={-4} cy={398} r={22} fill="#7dffc0" opacity={0.45} /> : null}
          {archetype === 'magicalGirl' ? <circle cx={348} cy={20} r={36} fill="#fff4b0" opacity={0.35} /> : null}
        </g>
      </g>
    </svg>
  );
};

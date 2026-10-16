import React from 'react';
import { Archetype } from '../config/characters';
import { COLORS } from '../config/theme';

/**
 * 原創角色剪影（正面站姿，viewBox 0 0 400 1000）。
 * 每個角色由共用的人體剪影 + 專屬的輪廓與發光道具組成，
 * 透過 SVG 濾鏡產生左右兩側的輪廓光與背光。
 */

type FigureProps = {
  archetype: Archetype | 'everyday';
  /** 用於產生唯一的濾鏡 id */
  uid: string;
  /** 右上方輪廓光顏色 */
  rimRight?: string;
  /** 左側輪廓光顏色 */
  rimLeft?: string;
  /** 背光顏色 */
  glow?: string;
  glowStrength?: number;
  /** 道具發光亮度 0–1（剪影模式可調暗） */
  detail?: number;
  /** 動態參數：秒，用於頭髮 / 披風飄動 */
  t?: number;
  /** 行走週期（只用於 everyday） */
  walk?: number;
  style?: React.CSSProperties;
  fill?: string;
};

const DARK = COLORS.silhouette;

/** Catmull-Rom 曲線 → 平滑封閉路徑 */
const smoothPath = (pts: [number, number][]) => {
  const n = pts.length;
  let d = `M${pts[0][0].toFixed(1)} ${pts[0][1].toFixed(1)}`;
  for (let i = 0; i < n; i++) {
    const p0 = pts[(i - 1 + n) % n];
    const p1 = pts[i];
    const p2 = pts[(i + 1) % n];
    const p3 = pts[(i + 2) % n];
    const c1 = [p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6];
    const c2 = [p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6];
    d += ` C${c1[0].toFixed(1)} ${c1[1].toFixed(1)} ${c2[0].toFixed(1)} ${c2[1].toFixed(1)} ${p2[0].toFixed(1)} ${p2[1].toFixed(1)}`;
  }
  return d + ' Z';
};

/** 錐形肢體（兩端圓角） */
const Limb: React.FC<{ a: [number, number]; b: [number, number]; r1: number; r2: number }> = ({ a, b, r1, r2 }) => {
  const dx = b[0] - a[0];
  const dy = b[1] - a[1];
  const l = Math.hypot(dx, dy) || 1;
  const nx = -dy / l;
  const ny = dx / l;
  return (
    <>
      <path d={`M${a[0] + nx * r1} ${a[1] + ny * r1} L${b[0] + nx * r2} ${b[1] + ny * r2} L${b[0] - nx * r2} ${b[1] - ny * r2} L${a[0] - nx * r1} ${a[1] - ny * r1} Z`} />
      <circle cx={a[0]} cy={a[1]} r={r1} />
      <circle cx={b[0]} cy={b[1]} r={r2} />
    </>
  );
};

type Pt = [number, number];
const Arm: React.FC<{ s: Pt; e: Pt; w: Pt }> = ({ s, e, w }) => (
  <>
    <Limb a={s} b={e} r1={21} r2={15} />
    <Limb a={e} b={w} r1={15} r2={11} />
    <ellipse cx={w[0] + (w[0] - e[0]) * 0.12} cy={w[1] + (w[1] - e[1]) * 0.12} rx={14} ry={17} />
  </>
);

// 軀幹與雙腿（左半邊，由頸部往下，右半邊以鏡射產生）
const LEFT_HALF: Pt[] = [
  [178, 196], [176, 222], [148, 232], [120, 244], [102, 268], [104, 302], [126, 332], [136, 400], [148, 462],
  [140, 522], [140, 600], [150, 700], [156, 780], [150, 862], [162, 948], [142, 972], [150, 990], [194, 990],
  [192, 948], [190, 862], [188, 780], [192, 662], [198, 588],
];

/** 軀幹與雙腿的外框路徑（也用於裁切戰衣顏色） */
const bodyPath = (legSpread = 0, slim = 0) => {
  const k = 1 - slim / 110;
  const left = LEFT_HALF.map(([x, y]): Pt => {
    let nx = 200 + (x - 200) * (y < 560 ? k : 1);
    if (y > 585) nx -= legSpread * ((y - 585) / 405);
    return [nx, y];
  });
  const right = [...left].reverse().map(([x, y]): Pt => [400 - x, y]);
  return smoothPath([...left, [200, 578], ...right]);
};

/** 各角色的體型參數 */
const BODY: Record<string, { legSpread: number; slim: number }> = {
  spider: { legSpread: 30, slim: 8 },
  plumber: { legSpread: 18, slim: -16 },
  scoutSoldier: { legSpread: 24, slim: 8 },
};

const BaseBody: React.FC<{ legSpread?: number; slim?: number; armRaisedRight?: boolean; armOutLeft?: boolean }> = ({
  legSpread = 0,
  slim = 0,
  armRaisedRight = false,
  armOutLeft = false,
}) => {
  const k = 1 - slim / 110;
  const body = bodyPath(legSpread, slim);
  const sx = (x: number) => 200 + (x - 200) * k;
  return (
    <g>
      <path d={body} />
      {armOutLeft ? <Arm s={[sx(116), 272]} e={[78, 392]} w={[36, 466]} /> : <Arm s={[sx(116), 272]} e={[sx(108), 404]} w={[sx(106), 518]} />}
      {armRaisedRight ? <Arm s={[sx(284), 266]} e={[334, 176]} w={[338, 98]} /> : <Arm s={[sx(284), 272]} e={[sx(292), 404]} w={[sx(294), 518]} />}
    </g>
  );
};

/** 頭部：頭頂 + 下顎 + 耳朵 */
const Head: React.FC<{ rx?: number; ry?: number }> = ({ rx = 46 }) => {
  const w = rx;
  return (
    <g>
      <path d={`M${200 - w} 132 C${200 - w} 74 ${200 + w} 74 ${200 + w} 132 C${200 + w} 168 ${200 + w * 0.55} 196 200 200 C${200 - w * 0.55} 196 ${200 - w} 168 ${200 - w} 132 Z`} />
      <ellipse cx={200 - w + 2} cy={140} rx={8} ry={14} />
      <ellipse cx={200 + w - 2} cy={140} rx={8} ry={14} />
    </g>
  );
};

/** 剪影形狀（全部同一深色，讓濾鏡能產生乾淨的輪廓光） */
const Shape: React.FC<{ a: FigureProps['archetype']; t: number; walk: number }> = ({ a, t, walk }) => {
  const sway = Math.sin(t * 5) * 1;
  switch (a) {
    case 'shield':
      return (
        <g>
          <BaseBody legSpread={14} />
          <Head />
          {/* 頭盔側翼 */}
          <path d="M150 128 L118 104 L126 126 L112 120 L124 142 L152 150 Z" />
          <path d="M250 128 L282 104 L274 126 L288 120 L276 142 L248 150 Z" />
          {/* 腰帶 */}
          <rect x={136} y={478} width={128} height={26} rx={6} />
        </g>
      );
    case 'plumber':
      return (
        <g>
          <BaseBody {...BODY.plumber} />
          <Head rx={50} />
          {/* 帽子 */}
          <path d="M144 120 C140 50 260 50 256 120 Z" />
          <ellipse cx={200} cy={118} rx={66} ry={14} />
        </g>
      );
    case 'scoutSoldier':
      return (
        <g>
          {/* 披風 */}
          <path d={`M132 236 Q${92 - sway * 6} 520 ${84 - sway * 10} 700 L${316 + sway * 10} 700 Q${308 + sway * 6} 520 268 236 Z`} />
          <BaseBody {...BODY.scoutSoldier} />
          <Head rx={44} />
          {/* 齊耳短髮 */}
          <path d="M148 150 C136 66 264 66 252 150 L254 186 L238 176 L236 140 Q200 118 164 140 L162 176 L146 186 Z" />
        </g>
      );
    case 'spider':
      return (
        <g>
          <BaseBody {...BODY.spider} armRaisedRight />
          <Head rx={45} ry={56} />
        </g>
      );
    case 'knight': {
      const flare = 30 + sway * 18;
      return (
        <g>
          {/* 披風 */}
          <path
            d={`M126 238 Q${70 - flare * 0.4} 600 ${8 - flare} 985 L60 960 L110 990 L160 962 L200 992 L240 962 L290 990 L340 960 L${392 + flare} 985 Q${330 + flare * 0.4} 600 274 238 Z`}
          />
          <BaseBody legSpread={18} />
          <Head rx={50} ry={58} />
          {/* 頭罩尖耳 */}
          <path d="M152 140 L160 44 L184 100 L216 100 L240 44 L248 140 Z" />
          {/* 寬肩 */}
          <path d="M100 250 Q200 205 300 250 L292 300 L108 300 Z" />
        </g>
      );
    }
    case 'joker':
      return (
        <g>
          {/* 長大衣 */}
          <path d={`M126 250 L${78 - sway * 6} 800 L${322 + sway * 6} 800 L274 250 Z`} />
          <BaseBody legSpread={10} armRaisedRight />
          <Head rx={45} ry={58} />
          {/* 蓬亂頭髮 */}
          <path
            d={`M150 120 L136 76 L160 92 L158 56 L184 84 L196 44 L210 82 L232 50 L232 88 L262 70 L250 112 L268 112 L248 132 Q200 70 150 132 Z`}
          />
        </g>
      );
    case 'magicalGirl': {
      const s1 = Math.sin(t * 3.2) * 16;
      const s2 = Math.sin(t * 3.2 + 1.4) * 16;
      return (
        <g>
          {/* 雙馬尾 */}
          <path d={`M150 84 Q${70 + s1} 300 ${88 + s1 * 1.6} 640 Q${100 + s1 * 1.6} 700 ${122 + s1 * 1.2} 640 Q${110 + s1} 360 168 92 Z`} />
          <path d={`M250 84 Q${330 + s2} 300 ${312 + s2 * 1.6} 640 Q${300 + s2 * 1.6} 700 ${278 + s2 * 1.2} 640 Q${290 + s2} 360 232 92 Z`} />
          {/* 髮髻 */}
          <circle cx={148} cy={86} r={30} />
          <circle cx={252} cy={86} r={30} />
          {/* 短裙 */}
          <path d={`M146 455 L${100 + sway * 4} 600 Q200 620 ${300 - sway * 4} 600 L254 455 Z`} />
          <BaseBody legSpread={8} slim={16} armRaisedRight />
          <Head rx={44} ry={54} />
          {/* 魔法棒 */}
          <Limb a={[340, 92]} b={[348, 26]} r1={5} r2={4} />
        </g>
      );
    }
    case 'wizardStudent': {
      const sc = Math.sin(t * 4) * 14;
      return (
        <g>
          {/* 長袍 */}
          <path d={`M124 238 L${66 - sway * 5} 985 L${334 + sway * 5} 985 L276 238 Z`} />
          <BaseBody legSpread={6} armOutLeft />
          <Head />
          {/* 亂髮 */}
          <path d="M152 118 Q150 72 196 74 Q252 70 250 120 L262 104 L252 138 Q200 96 148 140 L140 112 Z" />
          {/* 圍巾飄動 */}
          <path d={`M168 214 Q200 236 232 214 L238 240 Q${260 + sc} 320 ${290 + sc} 410 L${262 + sc} 418 Q${238 + sc * 0.5} 330 214 252 Q200 258 168 240 Z`} />
          {/* 魔杖 */}
          <Limb a={[36, 470]} b={[-4, 400]} r1={4} r2={3} />
        </g>
      );
    }
    case 'oldWizard':
      return (
        <g>
          {/* 長袍 */}
          <path d={`M124 238 L${60 - sway * 4} 985 L${340 + sway * 4} 985 L276 238 Z`} />
          <BaseBody legSpread={4} />
          <Head rx={46} ry={56} />
          {/* 尖帽 */}
          <ellipse cx={200} cy={104} rx={108} ry={20} />
          <path d={`M138 104 Q178 40 ${222 + sway * 3} 4 Q${236 + sway * 3} 0 ${238 + sway * 3} 14 Q214 52 262 104 Z`} />
          {/* 法杖 */}
          <rect x={70} y={70} width={14} height={915} rx={6} transform="rotate(-2 77 520)" />
        </g>
      );
    case 'everyday': {
      // 背影：一般上衣與長褲，以身體起伏與左右擺動表現走路
      const bob = Math.abs(Math.sin(walk * Math.PI * 2)) * -10;
      const tilt = Math.sin(walk * Math.PI * 2) * 1.5;
      return (
        <g transform={`translate(0 ${bob}) rotate(${tilt} 200 990)`}>
          <BaseBody legSpread={6 + Math.sin(walk * Math.PI * 2) * 8} slim={4} />
          <Head />
          {/* 短髮 */}
          <path d="M150 136 C146 70 254 70 250 136 C246 120 236 110 200 108 C164 110 154 120 150 136 Z" />
          {/* 上衣下擺 */}
          <path d="M134 500 Q200 520 266 500 L270 548 Q200 566 130 548 Z" />
        </g>
      );
    }
  }
};

/** 發光細節與道具（畫在剪影之上） */
const Details: React.FC<{ a: FigureProps['archetype']; uid: string; t: number; detail: number }> = ({ a, uid, t, detail }) => {
  const glowId = `${uid}-dglow`;
  const pulse = 0.85 + Math.sin(t * 9) * 0.15;
  const content = (() => {
    switch (a) {
      case 'shield':
        return (
          <g>
            {/* 頭盔 A 字與白色側翼 */}
            <path d="M150 128 L118 104 L126 126 L112 120 L124 142 L152 150 Z" fill="#e9ecf4" />
            <path d="M250 128 L282 104 L274 126 L288 120 L276 142 L248 150 Z" fill="#e9ecf4" />
            <path d="M188 116 L200 88 L212 116 L206 116 L203 108 L197 108 L194 116 Z" fill="#e9ecf4" />
            {/* 胸前星星 */}
            <path transform="translate(236 300) scale(0.9)" d="M0 -30 L8 -9 L29 -9 L12 4 L18 25 L0 12 L-18 25 L-12 4 L-29 -9 L-8 -9 Z" fill="#e9ecf4" />
            <g transform="translate(148 395)">
              <circle r={104} fill="#8e1a2c" />
              <circle r={84} fill="#c9ccd6" />
              <circle r={64} fill="#8e1a2c" />
              <circle r={44} fill="#20448f" />
              <path
                d="M0 -36 L10 -11 L35 -11 L15 5 L22 30 L0 15 L-22 30 L-15 5 L-35 -11 L-10 -11 Z"
                fill="#e9ecf4"
              />
              <circle r={104} fill={`url(#${uid}-shieldShade)`} />
            </g>
          </g>
        );
      case 'spider':
        return (
          <g>
            <clipPath id={`${uid}-suit`}>
              <path d={bodyPath(BODY.spider.legSpread, BODY.spider.slim)} />
            </clipPath>
            <g clipPath={`url(#${uid}-suit)`}>
              <rect x={0} y={200} width={400} height={800} fill="#2346b8" />
              <path d="M150 200 L250 200 L246 470 Q200 520 154 470 Z" fill="#c4142b" />
              <rect x={0} y={760} width={400} height={240} fill="#c4142b" />
              {[240, 300, 360, 420].map((y) => (
                <path key={y} d={`M154 ${y} Q200 ${y + 18} 246 ${y}`} stroke="#3a0008" strokeWidth={2} fill="none" />
              ))}
              <path d="M200 220 L200 480 M170 220 L160 470 M230 220 L240 470" stroke="#3a0008" strokeWidth={2} />
            </g>
            {/* 胸前蜘蛛 */}
            <g transform="translate(200 300)" stroke="#0a0a0a" strokeWidth={4} fill="#0a0a0a">
              <ellipse rx={8} ry={14} />
              <path d="M-6 -6 L-26 -22 M6 -6 L26 -22 M-6 2 L-28 -2 M6 2 L28 -2 M-6 8 L-24 22 M6 8 L24 22 M-4 12 L-16 34 M4 12 L16 34" fill="none" />
            </g>
            <ellipse cx={200} cy={140} rx={45} ry={56} fill="#9b1324" />
            <g clipPath={`url(#${uid}-headClip)`}>
              {[...Array(10)].map((_, i) => {
                const ang = (i * Math.PI * 2) / 10 + 0.3;
                return <line key={i} x1={200} y1={128} x2={200 + Math.cos(ang) * 80} y2={128 + Math.sin(ang) * 90} stroke="#200307" strokeWidth={2} />;
              })}
              {[20, 36, 52, 68].map((r) => (
                <ellipse key={r} cx={200} cy={128} rx={r} ry={r * 1.15} fill="none" stroke="#200307" strokeWidth={2} />
              ))}
            </g>
            <path d="M162 124 Q176 100 194 128 Q182 150 164 140 Z" fill="#f4f6ff" stroke="#111" strokeWidth={4} />
            <path d="M238 124 Q224 100 206 128 Q218 150 236 140 Z" fill="#f4f6ff" stroke="#111" strokeWidth={4} />
            <ellipse cx={200} cy={140} rx={45} ry={56} fill={`url(#${uid}-headShade)`} />
          </g>
        );
      case 'knight':
        return (
          <g>
            {/* 胸前蝙蝠標誌 */}
            <g transform="translate(200 320)">
              <ellipse rx={52} ry={30} fill="#f2c94c" stroke="#1a1a1a" strokeWidth={4} />
              <path d="M0 -8 L-6 -18 L-10 -6 Q-26 -14 -44 -2 Q-30 0 -28 10 Q-18 4 -12 14 Q-4 8 0 18 Q4 8 12 14 Q18 4 28 10 Q30 0 44 -2 Q26 -14 10 -6 L6 -18 Z" fill="#111" />
            </g>
            <path d="M170 132 L194 138 L190 146 L172 142 Z" fill="#eaf4ff" />
            <path d="M230 132 L206 138 L210 146 L228 142 Z" fill="#eaf4ff" />
          </g>
        );
      case 'joker':
        return (
          <g>
            {/* 詭異笑容 */}
            <path d="M166 158 Q200 192 236 156 Q200 178 166 158 Z" fill="#ff2a3d" />
            <circle cx={182} cy={132} r={5} fill="#f2fff4" />
            <circle cx={218} cy={132} r={5} fill="#f2fff4" />
            {/* 小丑牌 */}
            <g transform="translate(330 84) rotate(16)">
              <rect x={-38} y={-56} width={76} height={108} rx={8} fill="#f6f1e2" />
              <rect x={-31} y={-49} width={62} height={94} rx={5} fill="none" stroke="#6a1fa8" strokeWidth={3} />
              <path d="M-22 -8 Q-12 -34 0 -10 Q12 -34 22 -8 L14 14 L-14 14 Z" fill="#6a1fa8" />
              <circle cx={-22} cy={-10} r={5} fill="#2fbf55" />
              <circle cx={22} cy={-10} r={5} fill="#2fbf55" />
              <circle cx={0} cy={-12} r={5} fill="#e0213a" />
              <rect x={-14} y={18} width={28} height={8} rx={3} fill="#6a1fa8" />
            </g>
          </g>
        );
      case 'plumber':
        return (
          <g>
            <clipPath id={`${uid}-suit`}>
              <path d={bodyPath(BODY.plumber.legSpread, BODY.plumber.slim)} />
            </clipPath>
            <g clipPath={`url(#${uid}-suit)`}>
              {/* 紅色上衣 + 藍色吊帶褲 */}
              <rect x={0} y={200} width={400} height={260} fill="#c8202a" />
              <rect x={0} y={440} width={400} height={560} fill="#2453c9" />
              <rect x={158} y={330} width={84} height={130} rx={8} fill="#2453c9" />
              <path d="M150 230 L172 336 L184 336 L164 230 Z M250 230 L228 336 L216 336 L236 230 Z" fill="#2453c9" />
              <circle cx={172} cy={350} r={9} fill="#ffd23f" />
              <circle cx={228} cy={350} r={9} fill="#ffd23f" />
              <rect x={0} y={940} width={400} height={60} fill="#5a3010" />
            </g>
            {/* 紅帽與 M 字徽章 */}
            <path d="M144 120 C140 50 260 50 256 120 Z" fill="#d8232c" />
            <ellipse cx={200} cy={118} rx={66} ry={14} fill="#a8161e" />
            <circle cx={200} cy={88} r={20} fill="#ffffff" />
            <path d="M188 99 L188 77 L200 90 L212 77 L212 99 L207 99 L207 88 L200 96 L193 88 L193 99 Z" fill="#d8232c" />
            {/* 鼻子與鬍子 */}
            <ellipse cx={200} cy={150} rx={15} ry={12} fill="#f0b58a" />
            <path d="M170 168 Q185 156 200 164 Q215 156 230 168 Q216 178 200 172 Q184 178 170 168 Z" fill="#2a1408" />
            {/* 白手套 */}
            <ellipse cx={104} cy={526} rx={17} ry={19} fill="#f4f4f4" />
            <ellipse cx={296} cy={526} rx={17} ry={19} fill="#f4f4f4" />
          </g>
        );
      case 'scoutSoldier':
        return (
          <g>
            {/* 紅圍巾 */}
            <path d="M162 200 Q200 226 238 200 L242 236 Q200 256 158 236 Z" fill="#c8202a" />
            <path d="M170 232 Q160 300 176 360 L196 356 Q186 300 194 240 Z" fill="#a3121e" />
            {/* 立體機動裝置皮帶 */}
            <g stroke="#b88a5a" strokeWidth={5} fill="none">
              <path d="M140 300 L260 380 M260 300 L140 380" />
              <path d="M146 470 L254 470 M150 560 L176 640 M250 560 L224 640" />
            </g>
            {/* 雙刀 */}
            <path d="M104 530 L36 742 L46 746 L114 534 Z" fill="#dfe6ef" />
            <path d="M296 530 L364 742 L354 746 L286 534 Z" fill="#dfe6ef" />
            <rect x={92} y={512} width={24} height={30} rx={4} fill="#55606e" />
            <rect x={284} y={512} width={24} height={30} rx={4} fill="#55606e" />
          </g>
        );
      case 'magicalGirl':
        return (
          <g>
            {/* 額飾 */}
            <path d="M200 92 L206 104 L200 116 L194 104 Z" fill="#ffe26a" />
            {/* 胸前蝴蝶結 */}
            <path d="M200 280 L150 254 L158 306 Z" fill="#e8264f" />
            <path d="M200 280 L250 254 L242 306 Z" fill="#e8264f" />
            <circle cx={200} cy={280} r={12} fill="#ffd34a" />
            {/* 月亮魔法棒頭 */}
            <g transform="translate(346 22)">
              <circle r={30 * pulse} fill="#fff4b0" opacity={0.35} />
              <path d="M8 -26 A26 26 0 1 0 8 26 A20 20 0 1 1 8 -26 Z" fill="#ffd34a" />
              <circle cx={-2} cy={0} r={6} fill="#ff5c9d" />
            </g>
          </g>
        );
      case 'wizardStudent': {
        const sc = Math.sin(t * 4) * 14;
        return (
          <g>
            {/* 綠銀條紋圍巾 */}
            <path
              d={`M168 214 Q200 236 232 214 L238 240 Q${260 + sc} 320 ${290 + sc} 410 L${262 + sc} 418 Q${238 + sc * 0.5} 330 214 252 Q200 258 168 240 Z`}
              fill="#1d6b45"
            />
            {[0, 1, 2, 3].map((i) => (
              <path
                key={i}
                d={`M${242 + i * 12 + sc * (0.2 + i * 0.2)} ${270 + i * 36} l26 -6 l4 14 l-26 6 Z`}
                fill="#c9d3d6"
              />
            ))}
            {/* 圓框眼鏡反光 */}
            <circle cx={180} cy={140} r={15} fill="none" stroke="#e6f0ff" strokeWidth={3.5} />
            <circle cx={220} cy={140} r={15} fill="none" stroke="#e6f0ff" strokeWidth={3.5} />
            <line x1={195} y1={140} x2={205} y2={140} stroke="#e6f0ff" strokeWidth={3} />
            {/* 魔杖火花 */}
            <circle cx={-4} cy={398} r={22 * pulse} fill="#7dffc0" opacity={0.45} />
            <circle cx={-4} cy={398} r={8} fill="#eafff3" />
          </g>
        );
      }
      case 'oldWizard':
        return (
          <g>
            {/* 銀白長鬍 */}
            <path d="M158 168 Q200 200 242 168 Q246 300 200 470 Q154 300 158 168 Z" fill="#cfd3dc" />
            <path d="M200 200 Q206 320 200 440" stroke="#9aa0ad" strokeWidth={3} fill="none" />
            <path d="M180 200 Q178 300 190 400" stroke="#9aa0ad" strokeWidth={2} fill="none" />
            <path d="M220 200 Q222 300 210 400" stroke="#9aa0ad" strokeWidth={2} fill="none" />
            {/* 半月眼鏡 */}
            <path d="M166 136 A14 10 0 0 0 194 136 Z" fill="none" stroke="#ffe8a8" strokeWidth={3} />
            <path d="M206 136 A14 10 0 0 0 234 136 Z" fill="none" stroke="#ffe8a8" strokeWidth={3} />
            {/* 法杖光球 */}
            <circle cx={72} cy={66} r={44 * pulse} fill="#ffd36b" opacity={0.35} />
            <circle cx={72} cy={66} r={20} fill="#fff3c4" />
          </g>
        );
      default:
        return null;
    }
  })();
  return (
    <g opacity={detail} filter={`url(#${glowId})`}>
      {content}
    </g>
  );
};

export const Figure: React.FC<FigureProps> = ({
  archetype,
  uid,
  rimRight = '#ffffff',
  rimLeft = '#8b3dff',
  glow = '#8b3dff',
  glowStrength = 0.6,
  detail = 1,
  t = 0,
  walk = 0,
  style,
  fill = DARK,
}) => {
  const rimId = `${uid}-rim`;
  return (
    <svg viewBox="-60 -40 520 1060" style={{ overflow: 'visible', ...style }}>
      <defs>
        <filter id={rimId} x="-30%" y="-20%" width="160%" height="140%">
          {/* 背光 */}
          <feGaussianBlur in="SourceAlpha" stdDeviation={22} result="halo" />
          <feFlood floodColor={glow} floodOpacity={glowStrength} />
          <feComposite in2="halo" operator="in" result="haloC" />
          {/* 右上輪廓光 */}
          <feOffset in="SourceAlpha" dx={-7} dy={5} result="o1" />
          <feComposite in="SourceAlpha" in2="o1" operator="out" result="e1" />
          <feFlood floodColor={rimRight} />
          <feComposite in2="e1" operator="in" result="r1" />
          <feGaussianBlur in="r1" stdDeviation={1.6} result="r1b" />
          {/* 左側輪廓光 */}
          <feOffset in="SourceAlpha" dx={6} dy={3} result="o2" />
          <feComposite in="SourceAlpha" in2="o2" operator="out" result="e2" />
          <feFlood floodColor={rimLeft} />
          <feComposite in2="e2" operator="in" result="r2" />
          <feGaussianBlur in="r2" stdDeviation={1.6} result="r2b" />
          <feMerge>
            <feMergeNode in="haloC" />
            <feMergeNode in="SourceGraphic" />
            <feMergeNode in="r1b" />
            <feMergeNode in="r2b" />
          </feMerge>
        </filter>
        <filter id={`${uid}-dglow`} x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur in="SourceGraphic" stdDeviation={5} result="b" />
          <feMerge>
            <feMergeNode in="b" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
        <radialGradient id={`${uid}-shieldShade`} cx="0.7" cy="0.3" r="0.9">
          <stop offset="0" stopColor="#fff" stopOpacity={0.25} />
          <stop offset="0.5" stopColor="#000" stopOpacity={0.15} />
          <stop offset="1" stopColor="#000" stopOpacity={0.7} />
        </radialGradient>
        <clipPath id={`${uid}-headClip`}>
          <ellipse cx={200} cy={140} rx={45} ry={56} />
        </clipPath>
        <radialGradient id={`${uid}-headShade`} cx="0.7" cy="0.25" r="0.9">
          <stop offset="0" stopColor="#fff" stopOpacity={0.15} />
          <stop offset="1" stopColor="#000" stopOpacity={0.55} />
        </radialGradient>
      </defs>
      <g filter={`url(#${rimId})`} fill={fill}>
        <Shape a={archetype} t={t} walk={walk} />
        {detail > 0 ? <Details a={archetype} uid={uid} t={t} detail={detail} /> : null}
      </g>
    </svg>
  );
};

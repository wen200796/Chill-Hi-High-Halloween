/** 色彩與字型集中管理 */
export const COLORS = {
  night: '#050a1f',
  navy: '#0b1640',
  deepBlue: '#13235e',
  moon: '#f3f1e4',
  purple: '#8b3dff',
  violet: '#c27bff',
  magenta: '#ff3dd2',
  bloodRed: '#a3122a',
  orange: '#ff7a1a',
  gold: '#ffc94a',
  warmGold: '#ffd58a',
  silhouette: '#07070d',
  paper: '#f4ecd9',
  ink: '#1b1410',
  white: '#ffffff',
} as const;

export const FONTS = {
  /** 電影感字幕：思源宋體（Noto Serif TC） */
  cinematic: '"Noto Serif TC", "Noto Sans TC", serif',
  /** 一般字幕與活動資訊：思源黑體（Noto Sans TC） */
  sans: '"Noto Sans TC", sans-serif',
} as const;

/**
 * 字幕集中管理。時間為「該場景內」的相對秒數。
 * 場景起訖時間請見 timeline.json。
 */
export const SUBTITLES = {
  castle: { text: '當世界再次陷入危機……', from: 0.2, to: 1.5 },
  portal: { text: '英雄，即將集結。', from: 0.12, to: 1.5 },
  /** 角色登場：每種角色類型第一次出現時加上對應的詞 */
  roster: { hero: '英雄、', villain: '反派、', mage: '魔法師……' },
  assemble: [
    { text: '不同的世界。', from: 0.1, to: 1.05 },
    { text: '不同的身分。', from: 1.05, to: 2.0 },
  ],
  /** 核心主題 */
  theme: { text: '英雄不只有一種樣子。', from: 2.0, to: 3.3 },
  stage: { text: '等等……', from: 0.18, to: 0.8 },
  challenge: {
    lead: { text: '真正的挑戰是——', from: 0.05, to: 0.75 },
    card: {
      label: '今日任務',
      title: '即席演講！',
      note: '準備時間：0 秒',
    },
  },
  finale: {
    theme: '英雄不只有一種樣子。',
    question: ['這個萬聖節，', '你準備好登上舞台了嗎？'],
  },
} as const;

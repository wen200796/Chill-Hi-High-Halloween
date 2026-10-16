import timeline from './timeline.json';

/** 影片規格：1080 × 1920、30 FPS、15 秒（9:16 直式） */
export const VIDEO = {
  width: timeline.width,
  height: timeline.height,
  fps: timeline.fps,
  durationInFrames: Math.round(timeline.durationSec * timeline.fps),
} as const;

export type SceneId = keyof typeof timeline.scenes;

export const SCENES = timeline.scenes;
export const CUES = timeline.cues;
/** 角色登場順序（角色 id，見 characters.ts） */
export const ROSTER: string[] = timeline.roster;

/** 秒 → 幀 */
export const sec = (s: number) => Math.round(s * VIDEO.fps);

export const sceneFrom = (id: SceneId) => sec(SCENES[id].start);
/** 第 i 個角色鏡頭在 Scene 3 內的起始幀（平均分配場景長度） */
export const rosterShotStart = (i: number) => Math.round((i * sceneLength('roster')) / ROSTER.length);

export const sceneLength = (id: SceneId) =>
  sec(SCENES[id].end) - sec(SCENES[id].start);

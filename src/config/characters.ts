/**
 * 角色素材設定。
 *
 * 每個角色預設使用「原創剪影 + 象徵性道具」。
 *
 * 換成角色插圖（AI 繪圖或插畫師，建議）：
 *   把圖片放進 art_source/<角色 id>.png → npm run art → npm run render
 *   （prepare_art.py 會去背、對齊並寫入 src/config/art.json，這裡會自動讀取）
 *
 * 換成實際參與者照片（整張照片當背景，用於角色登場特寫）：
 *   1. 把照片放到 public/characters/（例如 public/characters/captain.jpg，建議直式、至少 1080px 寬）
 *   2. 在下面對應角色填入 photo: 'characters/captain.jpg'
 *   3. 用 focus 指定臉部在照片中的位置（0–1，左上為 0,0），特寫鏡頭會以此為中心推近
 *   4. 重新執行 npm run render
 */
import ART from './art.json';

export type Archetype =
  | 'shield'
  | 'plumber'
  | 'scoutSoldier'
  | 'spider'
  | 'knight'
  | 'joker'
  | 'magicalGirl'
  | 'wizardStudent'
  | 'oldWizard';

export type CharacterGroup = 'hero' | 'villain' | 'mage';

export type Character = {
  id: string;
  /** 只用於維護辨識，不會出現在影片中 */
  label: string;
  archetype: Archetype;
  group: CharacterGroup;
  /** 角色主色（輪廓光 / 鏡頭底色） */
  accent: string;
  /** 次要色（背景漸層） */
  accent2: string;
  /** 角色登場鏡頭的構圖 */
  shot: 'closeup' | 'bust' | 'low-angle';
  /** 斜切面板方向 */
  slant: -1 | 1;
  /** 選填：實際照片（public/ 底下的相對路徑） */
  photo?: string;
  /** 自動帶入：角色插圖（由 npm run art 產生） */
  art?: { src: string; head: { x: number; y: number } };
  /** 選填：照片臉部焦點 */
  focus?: { x: number; y: number };
};

/** 角色資料。登場順序由 timeline.json → roster 決定 */
const BASE_CHARACTERS: Character[] = [
  { id: 'captain', label: '盾牌英雄（美國隊長）', archetype: 'shield', group: 'hero', accent: '#4f8dff', accent2: '#c81d3a', shot: 'bust', slant: 1 },
  { id: 'spider', label: '蛛網英雄（蜘蛛人）', archetype: 'spider', group: 'hero', accent: '#ff3045', accent2: '#1b3fae', shot: 'closeup', slant: -1 },
  { id: 'knight', label: '黑暗騎士（蝙蝠俠）', archetype: 'knight', group: 'hero', accent: '#9fc4ff', accent2: '#1a2340', shot: 'bust', slant: 1 },
  { id: 'mario', label: '紅帽水管工（超級瑪利歐）', archetype: 'plumber', group: 'hero', accent: '#ff3b3b', accent2: '#1d4fd8', shot: 'bust', slant: -1 },
  { id: 'mikasa', label: '紅圍巾戰士（米卡莎）', archetype: 'scoutSoldier', group: 'hero', accent: '#ff4a4a', accent2: '#2f5d3a', shot: 'low-angle', slant: 1 },
  { id: 'joker', label: '小丑反派（Joker）', archetype: 'joker', group: 'villain', accent: '#62ff7a', accent2: '#6a1fa8', shot: 'closeup', slant: -1 },
  { id: 'sailor', label: '魔法少女（美少女戰士）', archetype: 'magicalGirl', group: 'mage', accent: '#ff7fd0', accent2: '#ffd34a', shot: 'bust', slant: 1 },
  { id: 'student', label: '史萊哲林學院魔法師（哈利波特）', archetype: 'wizardStudent', group: 'mage', accent: '#3dffa8', accent2: '#c9d3d6', shot: 'closeup', slant: -1 },
  { id: 'elder', label: '老巫師（鄧不利多）', archetype: 'oldWizard', group: 'mage', accent: '#ffd36b', accent2: '#5b3bbf', shot: 'low-angle', slant: 1 },
];

const ART_MAP = ART as Record<string, { src: string; head: { x: number; y: number } }>;

/** 有插圖的角色自動套用插圖 */
export const CHARACTERS: Character[] = BASE_CHARACTERS.map((c) =>
  ART_MAP[c.id] ? { ...c, art: { src: ART_MAP[c.id].src, head: ART_MAP[c.id].head } } : c,
);

/**
 * 英雄集結的隊形。
 * x：畫面水平位置 0–1；scale：大小；baseY：腳底位置（px）；z：前後順序（大者在前）；delay：登場延遲秒數
 * 後排角色站在前排角色之間的空隙，並略高於前排，讓每個角色的頭部都能被看見。
 */
export const ASSEMBLY_FORMATION: { id: string; x: number; scale: number; baseY: number; z: number; delay: number }[] = [
  { id: 'elder', x: 0.2, scale: 0.76, baseY: 1250, z: 0, delay: 0.0 },
  { id: 'spider', x: 0.4, scale: 0.72, baseY: 1240, z: 0, delay: 0.06 },
  { id: 'student', x: 0.6, scale: 0.72, baseY: 1240, z: 0, delay: 0.12 },
  { id: 'joker', x: 0.8, scale: 0.76, baseY: 1250, z: 0, delay: 0.18 },
  { id: 'mario', x: 0.1, scale: 0.78, baseY: 1450, z: 1, delay: 0.32 },
  { id: 'mikasa', x: 0.9, scale: 0.86, baseY: 1450, z: 1, delay: 0.38 },
  { id: 'captain', x: 0.3, scale: 0.86, baseY: 1450, z: 1, delay: 0.46 },
  { id: 'knight', x: 0.7, scale: 0.86, baseY: 1450, z: 1, delay: 0.52 },
  { id: 'sailor', x: 0.5, scale: 0.94, baseY: 1460, z: 2, delay: 0.64 },
];

/** 依 id 取得角色 */
export const getCharacter = (id: string) => {
  const c = CHARACTERS.find((ch) => ch.id === id);
  if (!c) throw new Error(`找不到角色 ${id}，請檢查 characters.ts 與 timeline.json`);
  return c;
};

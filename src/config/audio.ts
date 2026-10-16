/**
 * 音樂與音效檔案。由 `npm run audio`（scripts/generate_audio.py）依 timeline.json 合成。
 * - mix：音樂 + 音效（正式版）
 * - sfx：只有音效（無音樂版）
 */
export const AUDIO = {
  mix: 'audio/trailer_mix.wav',
  sfx: 'audio/trailer_sfx.wav',
  volume: 1,
} as const;

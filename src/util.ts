import { Easing, interpolate } from 'remotion';

export const clamp = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;

/** 在 [a, b] 幀之間由 0 → 1 */
export const progress = (frame: number, a: number, b: number, easing = Easing.inOut(Easing.cubic)) =>
  interpolate(frame, [a, b], [0, 1], { ...clamp, easing });

/** 淡入淡出（a 開始淡入，d 結束淡出） */
export const fadeInOut = (frame: number, a: number, b: number, c: number, d: number) =>
  interpolate(frame, [a, b, c, d], [0, 1, 1, 0], clamp);

export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

/** 可重現的雜訊（避免每次渲染結果不同） */
export const hash = (n: number) => {
  const x = Math.sin(n * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
};

/** 1D 平滑雜訊 */
export const noise1 = (t: number, seed = 0) => {
  const i = Math.floor(t);
  const f = t - i;
  const u = f * f * (3 - 2 * f);
  return lerp(hash(i + seed * 101), hash(i + 1 + seed * 101), u) * 2 - 1;
};

/** 鏡頭震動位移 */
export const shake = (frame: number, start: number, dur: number, amp: number, seed = 1) => {
  const t = frame - start;
  if (t < 0 || t > dur) return { x: 0, y: 0, r: 0 };
  const k = 1 - t / dur;
  return {
    x: noise1(frame * 0.9, seed) * amp * k,
    y: noise1(frame * 0.9, seed + 7) * amp * k,
    r: noise1(frame * 0.7, seed + 13) * amp * 0.04 * k,
  };
};

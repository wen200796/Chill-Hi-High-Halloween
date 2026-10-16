import { continueRender, delayRender } from 'remotion';
import '@fontsource/noto-sans-tc/500.css';
import '@fontsource/noto-sans-tc/700.css';
import '@fontsource/noto-sans-tc/900.css';
import '@fontsource/noto-serif-tc/900.css';
import { BRAND, EVENT } from './config/event';
import { SUBTITLES } from './config/subtitles';

/** 影片中所有會出現的文字，用來預先載入對應的字型分片（避免渲染時缺字） */
const ALL_TEXT = [
  JSON.stringify(SUBTITLES),
  JSON.stringify(EVENT),
  JSON.stringify(BRAND),
  BRAND.titleLines.halloween.toUpperCase(),
  BRAND.titleLines.toastmasters.toUpperCase(),
  '0123456789:：–—…，。！？、（）()',
].join('');

let loaded = false;

export const ensureFonts = () => {
  if (loaded || typeof document === 'undefined') return;
  loaded = true;
  const handle = delayRender('Loading Noto TC fonts');
  const specs = ['500 64px "Noto Sans TC"', '700 64px "Noto Sans TC"', '900 64px "Noto Sans TC"', '900 64px "Noto Serif TC"'];
  Promise.all(specs.map((s) => document.fonts.load(s, ALL_TEXT)))
    .then(() => document.fonts.ready)
    .then(() => continueRender(handle))
    .catch((err) => {
      console.error(err);
      continueRender(handle);
    });
};

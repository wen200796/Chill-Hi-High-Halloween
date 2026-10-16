// 渲染完整預告片：
//   output/chill_hi_high_halloween_trailer.mp4           音樂 + 音效
//   output/chill_hi_high_halloween_trailer_no_music.mp4  只有音效（無音樂版）
//   output/storyboard_preview.png                        關鍵畫面總覽
import { renderMedia, selectComposition } from '@remotion/renderer';
import { execFileSync } from 'node:child_process';
import { mkdirSync } from 'node:fs';
import path from 'node:path';
import { browserExecutable, bundleProject, ROOT } from './common.mjs';

const OUT = path.join(ROOT, 'output');
mkdirSync(OUT, { recursive: true });
// 版本後綴：V2（漫畫風）預設輸出 *_v2 檔名，可用 OUTPUT_SUFFIX 覆寫（例如 OUTPUT_SUFFIX= 代表不加後綴）
const SUFFIX = process.env.OUTPUT_SUFFIX ?? '_v2';
const main = path.join(OUT, `chill_hi_high_halloween_trailer${SUFFIX}.mp4`);
const noMusic = path.join(OUT, `chill_hi_high_halloween_trailer${SUFFIX}_no_music.mp4`);

console.log('1/4 合成音樂與音效…');
execFileSync('python3', [path.join(ROOT, 'scripts', 'generate_audio.py')], { stdio: 'inherit' });

console.log('2/4 打包專案…');
const serveUrl = await bundleProject();
const composition = await selectComposition({ serveUrl, id: 'Trailer', browserExecutable: browserExecutable() });

console.log('3/4 渲染影片…');
let last = -1;
await renderMedia({
  serveUrl,
  composition,
  codec: 'h264',
  audioCodec: 'aac',
  audioBitrate: '192k',
  crf: 18,
  pixelFormat: 'yuv420p',
  imageFormat: 'jpeg',
  jpegQuality: 92,
  concurrency: Number(process.env.CONCURRENCY ?? 4),
  outputLocation: main,
  browserExecutable: browserExecutable(),
  onProgress: ({ progress }) => {
    const p = Math.floor(progress * 10);
    if (p !== last) {
      last = p;
      console.log(`   ${p * 10}%`);
    }
  },
});

console.log('4/4 產生無音樂版與分鏡預覽…');
// 無音樂版：影像直接複製，只替換成純音效音軌
execFileSync('ffmpeg', [
  '-y', '-loglevel', 'error', '-i', main, '-i', path.join(ROOT, 'public', 'audio', 'trailer_sfx.wav'),
  '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', noMusic,
]);
execFileSync('python3', [path.join(ROOT, 'scripts', 'storyboard_preview.py'), main, path.join(OUT, `storyboard_preview${SUFFIX}.png`)], { stdio: 'inherit' });
console.log('完成：', path.relative(ROOT, main));

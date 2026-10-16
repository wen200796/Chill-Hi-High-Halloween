// 用法：node scripts/stills.mjs <輸出資料夾> <秒數...>（可用環境變數 COMP 指定其他 composition）
import { renderStill, selectComposition } from '@remotion/renderer';
import { mkdirSync } from 'node:fs';
import path from 'node:path';
import { browserExecutable, bundleProject } from './common.mjs';

const [outDir, ...times] = process.argv.slice(2);
mkdirSync(outDir, { recursive: true });
const serveUrl = await bundleProject();
const composition = await selectComposition({ serveUrl, id: process.env.COMP ?? 'Trailer', browserExecutable: browserExecutable() });
for (const s of times) {
  const frame = Math.min(composition.durationInFrames - 1, Math.round(Number(s) * composition.fps));
  const output = path.join(outDir, `t${s}.png`);
  await renderStill({ serveUrl, composition, frame, output, browserExecutable: browserExecutable() });
  console.log('still', s, '→', output);
}

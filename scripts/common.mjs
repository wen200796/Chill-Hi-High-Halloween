import { bundle } from '@remotion/bundler';
import { existsSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

/**
 * 瀏覽器：優先使用環境變數 REMOTION_BROWSER，其次使用預先安裝的 Chromium headless shell，
 * 都沒有時回傳 null，讓 Remotion 自行下載。
 */
export const browserExecutable = () => {
  const candidates = [process.env.REMOTION_BROWSER, '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell'];
  return candidates.find((p) => p && existsSync(p)) ?? null;
};

export const bundleProject = () =>
  bundle({
    entryPoint: path.join(ROOT, 'src', 'index.ts'),
    publicDir: path.join(ROOT, 'public'),
  });

# Chill Hi High Halloween Toastmasters｜15 秒直式預告片

主題：**英雄不只有一種樣子。**

以 Remotion（React）製作的 15 秒、1080 × 1920、30 FPS 萬聖節活動預告片。
前 10 秒是史詩級英雄電影預告，第 9.8 秒音樂突然停止，畫面切換到 Toastmasters 演講舞台——真正的挑戰是「即席演講！」。

## 版本

| 分支 | 風格 | 成品 |
|---|---|---|
| `V1` | 電影感剪影風格 | `output/chill_hi_high_halloween_trailer.mp4` |
| `V2`（本分支） | 美式漫畫風：彩色角色、墨線、網點、黑影、集中線、漫畫格、黃色說明框、音效字 | `output/chill_hi_high_halloween_trailer_v2.mp4` |

切換畫風：`src/config/theme.ts` 的 `ART_STYLE`（`'comic'` 或 `'silhouette'`）。
V2 刻意保留「音樂停止 → 真實舞台」那一段不做漫畫化，讓反轉更明顯；片尾再回到漫畫風。

## 成品（V2）

| 檔案 | 說明 |
|---|---|
| `output/chill_hi_high_halloween_trailer_v2.mp4` | 正式版（音樂 + 音效），H.264 / AAC |
| `output/chill_hi_high_halloween_trailer_v2_no_music.mp4` | 無音樂版（只保留音效） |
| `output/storyboard_preview_v2.png` | 0、2、4、7、9、10.5、12、13.5、14.5 秒的關鍵畫面 |
| `output/chill_hi_high_halloween_trailer.mp4` 等 | V1 成品（保留供比較） |
| `docs/storyboard_mapping.md` | 參考圖 → 影片場景的分鏡對照表 |

輸出檔名後綴由 `OUTPUT_SUFFIX` 控制（預設 `_v2`），例如 `OUTPUT_SUFFIX=_v3 npm run render`。
每個角色的漫畫音效字（WHAM!、THWIP!…）在 `src/config/characters.ts` 的 `sfx` 欄位。

## 環境需求

- Node.js 18 以上（已在 Node 22 測試）
- Python 3 + numpy、Pillow（合成音效、產生分鏡預覽）
- FFmpeg（產生無音樂版與分鏡預覽）
- Chromium：`scripts/common.mjs` 會優先使用環境變數 `REMOTION_BROWSER`，找不到時由 Remotion 自動下載

## 如何執行

```bash
npm install          # 安裝相依套件
npm run studio       # 開啟 Remotion Studio 即時預覽（可拖曳時間軸）
npm run render       # 合成音效 → 渲染 MP4 → 產生無音樂版與分鏡預覽
```

只想重新合成音樂音效：`npm run audio`。
渲染時間約 5–6 分鐘（4 核心）；可用 `CONCURRENCY=8 npm run render` 調整並行數。

## 專案結構

```
src/
  config/
    timeline.json   場景起訖時間、關鍵時間點、角色登場順序（畫面與音效共用）
    event.ts        品牌名稱與活動資訊（日期、時間、地點、地址）
    subtitles.ts    所有字幕
    characters.ts   角色設定、照片替換、英雄集結隊形
    theme.ts        色彩與字型
    audio.ts        音樂音效檔案路徑
    video.ts        影片規格（1080×1920、30 FPS、15 秒）
  components/       角色剪影、夜景、舞台、字幕、Logo 等共用元件
  scenes/           Scene1Castle … Scene7Finale，每個場景獨立
  Trailer.tsx       主時間軸
scripts/
  generate_audio.py 依 timeline.json 合成音樂與音效
  render.mjs        完整渲染流程
  stills.mjs        渲染指定秒數的靜態畫面（檢查用）
  storyboard_preview.py
public/
  assets/           Logo（原始檔案）、底片顆粒
  audio/            合成的音樂音效與分軌
```

## 如何更新活動資訊

只需修改 `src/config/event.ts`：

```ts
export const EVENT = {
  date: '10/27（二）',
  time: '19:15–21:15',
  venue: '社會創新實驗中心 107 會議室',
  address: '臺北市大安區仁愛路三段 99 號',
};
```

正式品牌名稱為 **Chill Hi High**（三個英文單字之間有空格），請勿改成 ChillHiHigh 等寫法。
Logo 使用 `public/assets/chill_hi_high_logo.png`（原始檔案，以圓形裁切顯示）。若更換 Logo 檔且徽章位置不同，請調整 `src/components/Overlays.tsx` 中 `Logo` 元件的圓心與半徑。

## 如何調整字幕

修改 `src/config/subtitles.ts`。每句字幕的 `from` / `to` 是**該場景內**的秒數；場景本身的起訖時間在 `src/config/timeline.json`。
角色登場的「英雄、反派、魔法師……」會在每種角色類型第一次出場時自動加上。

## 如何替換角色圖片

目前 9 個角色（美國隊長、蜘蛛人、蝙蝠俠、超級瑪利歐、米卡莎、Joker、美少女戰士、史萊哲林魔法師、鄧不利多）以「原創剪影 + 招牌配件」呈現。

### 換成角色插圖（建議）

1. 依 `docs/character_art_prompts.md` 的提示詞，用 AI 繪圖工具或請插畫師畫出角色全身圖（直式 2:3、純色背景、無文字）。
2. 將圖片放進 `art_source/`，檔名使用角色 id（例如 `captain.png`）。
3. `npm run art`：自動去背、裁切、對齊，寫入 `src/config/art.json`。
4. `npm run render`。

插圖會自動用在「次元裂縫」（背光剪影）、「角色登場」（特寫）與「英雄集結」（群像）三個場景；缺圖的角色維持剪影。

### 換成實際參與者照片（整張照片當特寫背景）

1. 將照片放到 `public/characters/`（建議直式、寬度至少 1080 px）。
2. 在 `src/config/characters.ts` 對應角色加上：
   ```ts
   photo: 'characters/captain.jpg',
   focus: { x: 0.5, y: 0.3 }, // 臉部在照片中的位置（0–1）
   ```
3. 執行 `npm run render`。

調整登場順序或角色數量：修改 `src/config/timeline.json` 的 `roster`（角色 id 清單），鏡頭長度會自動平均分配，音效重擊點也會同步。
英雄集結的站位在 `characters.ts` 的 `ASSEMBLY_FORMATION`。

## 音樂與音效

所有音樂與音效都由 `scripts/generate_audio.py` 以程式合成（原創、無授權問題），並依 `timeline.json` 對齊：
城堡風聲與雷聲、傳送門充電聲、角色切鏡重擊、銅管高潮、9.8 秒硬停、聚光燈開關聲、任務卡提示音、片尾溫暖鋼琴。
若要使用自己的配樂，把檔案放到 `public/audio/` 並修改 `src/config/audio.ts`。

## 如何重新渲染

```bash
npm run render
```

會依序完成：合成音效 → 打包 → 渲染 `output/chill_hi_high_halloween_trailer.mp4` → 產生無音樂版 → 產生 `output/storyboard_preview.png`。

檢查單一畫面（例如 9 秒與 14.5 秒）：

```bash
node scripts/stills.mjs output/frames 9 14.5
```

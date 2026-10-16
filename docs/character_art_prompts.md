# 角色插圖 AI 提示詞（9 張）

目標：達到 1990 年代美式漫畫封面的細緻度（粗細墨線、排線、強烈光影、肌肉結構）。
程式繪圖無法做到這種手繪細節，所以請用 AI 繪圖工具（ChatGPT、Midjourney、Gemini 等）或請插畫師繪製，
再放進 `art_source/` 執行 `npm run art`，影片會自動套用並加上推近、震動、閃光、輪廓光等動態。

## 生成規格（每張都一樣）

- 直式 **2:3**（例如 1024 × 1536），越大越好
- **全身入鏡**（頭頂到腳底完整），角色置中、面向鏡頭
- **單一純色淺灰背景**（不要場景、不要漸層），方便自動去背
- 畫面中**不要有任何文字、Logo、邊框**
- 9 張使用**同一段風格描述**，整體才會一致
- 存檔名稱用角色 id：`captain.png`、`spider.png`……

> 有些工具會拒絕直接寫出角色名稱，所以下面的提示詞只描述服裝與特徵，不寫角色名。
> 也請不要直接使用官方漫畫或電影的原圖（版權問題），用 AI 或插畫師重新繪製。

## 共用風格描述（貼在每個提示詞後面）

```
Detailed 1990s American comic book cover illustration, bold confident black ink linework
with fine crosshatching and feathering, dramatic heroic lighting from the upper right,
rich vibrant comic coloring with cel shading, anatomically detailed, full body standing
heroic pose facing the viewer, entire figure visible from head to feet, centered,
plain solid flat light grey background (#D9D9D9), no scenery, no text, no logo, no frame,
vertical 2:3 portrait, high resolution.
```

## 各角色提示詞

| id | 角色 | 提示詞（加上共用風格描述） |
|---|---|---|
| `captain` | 美國隊長 | A muscular patriotic super-soldier in a blue scale-textured suit with a large white star on the chest and red-and-white vertical stripes on the abdomen, blue cowl with a white letter "A" on the forehead and small white wings on the sides, red gloves and red boots, holding a round shield with concentric red and white rings and a white star on a blue center. |
| `spider` | 蜘蛛人 | An athletic masked hero in a red and blue full-body suit covered with a black web pattern, large white angular eye lenses with thick black borders, a black spider emblem on the chest, one hand raised in a web-shooting gesture. |
| `knight` | 蝙蝠俠 | A dark vigilante in a grey armored bodysuit with a black bat emblem inside a yellow oval on the chest, black cowl with pointed bat ears and narrow white eyes, a long dark scalloped cape flowing behind, yellow utility belt, fists clenched. |
| `mario` | 超級瑪利歐 | A cheerful short and stocky plumber with a big black mustache and round nose, red cap with a white circle and a red letter "M", red long-sleeve shirt, blue overalls with yellow buttons, white gloves and brown shoes, one fist pumping in the air. |
| `mikasa` | 米卡莎 | A young female soldier with short black bob hair and a calm, determined expression, red scarf around the neck, cropped brown jacket and green hooded cloak, white trousers, leather harness straps across the body and legs, holding two long silver blades, one in each hand. |
| `joker` | Joker | A menacing clown villain with wild green hair, chalk-white face and a wide red grin, purple suit with an orange vest and green shirt, holding up a joker playing card, sinister confident pose. |
| `sailor` | 美少女戰士 | A magical girl in a white and blue sailor-collar uniform with a large red bow on the chest, short blue pleated skirt, long blonde twin-tails with two round hair buns, golden tiara with a red gem, red knee-high boots, holding a wand topped with a golden crescent moon. |
| `student` | 史萊哲林魔法師 | A teenage wizard student with messy black hair and round glasses, black school robe with green lining, green-and-silver striped scarf, holding a wooden wand with a green magical spark at its tip. |
| `elder` | 鄧不利多 | An elderly wise wizard with a very long silver beard and long silver hair, half-moon spectacles, flowing purple robes embroidered with stars, a tall pointed wizard hat, holding a long wooden staff, kind but powerful expression. |

美少女戰士與米卡莎若想更貼近日本原作，可把共用風格描述的第一行換成：
`Detailed Japanese manga illustration, clean precise line art with screentone shading, anime cel coloring,`

## 放入影片

1. 把 9 張圖放進 `art_source/`（檔名 = 角色 id）。可以先放幾張，缺的角色會自動使用原本的剪影。
2. `npm run art`：自動去背、裁切、對齊，輸出到 `public/characters/`，並估計臉部位置寫入 `src/config/art.json`。
3. `npm run render`：重新輸出影片。

若特寫鏡頭沒對準臉，修改 `src/config/art.json` 中該角色的 `head.y`（0 = 圖片頂端，1 = 底部），
並把 `locked` 設為 `true`，之後重新執行 `npm run art` 時就不會被覆蓋。
若去背不乾淨（背景不夠純），可調整容許值：`ART_TOLERANCE=60 npm run art`。

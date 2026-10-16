#!/usr/bin/env python3
"""
把 AI 繪圖工具（或插畫師）提供的角色插圖整理成影片可用的格式。

用法：
  1. 將圖片放進 art_source/，檔名使用角色 id，例如：
       art_source/captain.png   art_source/spider.jpg   art_source/mario.webp
     角色 id：captain, spider, knight, mario, mikasa, joker, sailor, student, elder
  2. 執行 npm run art
  3. 執行 npm run render

處理內容：
  - 若圖片沒有透明背景，會從四周邊緣自動去除「單一純色背景」（請用純色背景生成）
  - 裁掉多餘空白，等比縮放到 1000×1500 畫布，腳底對齊底部、左右置中
  - 輸出 public/characters/<id>.png，並寫入 src/config/art.json（含臉部位置估計）
若自動估計的臉部位置不準，可直接修改 src/config/art.json 中的 head 數值（0–1）。
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "art_source")
OUT = os.path.join(ROOT, "public", "characters")
ART_JSON = os.path.join(ROOT, "src", "config", "art.json")
IDS = ["captain", "spider", "knight", "mario", "mikasa", "joker", "sailor", "student", "elder"]
W, H = 1000, 1500
TOL = float(os.environ.get("ART_TOLERANCE", 42))


def remove_background(im: Image.Image) -> Image.Image:
    rgba = np.asarray(im.convert("RGBA")).astype(np.float32)
    alpha = rgba[..., 3]
    border = np.concatenate([alpha[0], alpha[-1], alpha[:, 0], alpha[:, -1]])
    if np.median(border) < 128:  # 已經是透明背景
        return im.convert("RGBA")
    rgb = rgba[..., :3]
    edges = np.concatenate([rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]])
    bg = np.median(edges, axis=0)
    similar = np.sqrt(((rgb - bg) ** 2).sum(-1)) < TOL
    # 從邊緣向內擴張，只移除與邊緣相連的背景
    mask = np.zeros_like(similar)
    mask[0, :] = similar[0, :]
    mask[-1, :] = similar[-1, :]
    mask[:, 0] |= similar[:, 0]
    mask[:, -1] |= similar[:, -1]
    while True:
        grown = mask.copy()
        grown[1:] |= mask[:-1]
        grown[:-1] |= mask[1:]
        grown[:, 1:] |= mask[:, :-1]
        grown[:, :-1] |= mask[:, 1:]
        grown &= similar
        if (grown == mask).all():
            break
        mask = grown
    a = Image.fromarray(np.where(mask, 0, 255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
    out = im.convert("RGBA")
    out.putalpha(a)
    return out


def normalize(im: Image.Image):
    a = np.asarray(im)[..., 3]
    ys, xs = np.nonzero(a > 16)
    if len(xs) == 0:
        raise ValueError("圖片去背後沒有內容，請確認背景是單一純色，或調高 ART_TOLERANCE")
    im = im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    scale = min((W * 0.96) / im.width, (H * 0.97) / im.height)
    im = im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))), Image.LANCZOS)
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    x = (W - im.width) // 2
    y = H - im.height - int(H * 0.01)
    canvas.paste(im, (x, y), im)
    # 臉部位置估計：內容最上緣往下約 6.5% 人物高度
    head_y = (y + im.height * 0.065) / H
    return canvas, {"x": 0.5, "y": round(head_y, 3)}


def main():
    os.makedirs(OUT, exist_ok=True)
    art = json.load(open(ART_JSON, encoding="utf-8")) if os.path.exists(ART_JSON) else {}
    found = 0
    for cid in IDS:
        src = next((os.path.join(SRC, f) for f in sorted(os.listdir(SRC)) if os.path.splitext(f)[0] == cid), None) if os.path.isdir(SRC) else None
        if not src:
            continue
        found += 1
        im = remove_background(Image.open(src))
        canvas, head = normalize(im)
        canvas.save(os.path.join(OUT, f"{cid}.png"))
        prev = art.get(cid, {})
        art[cid] = {"src": f"characters/{cid}.png", "head": prev.get("head", head) if prev.get("locked") else head, "locked": prev.get("locked", False)}
        print(f"✓ {cid}: {os.path.relpath(src, ROOT)} → public/characters/{cid}.png（臉部位置 y≈{art[cid]['head']['y']}）")
    with open(ART_JSON, "w", encoding="utf-8") as f:
        json.dump(art, f, ensure_ascii=False, indent=2)
        f.write("\n")
    if not found:
        print("art_source/ 中沒有找到角色圖片（檔名需為角色 id，例如 captain.png）")


if __name__ == "__main__":
    main()

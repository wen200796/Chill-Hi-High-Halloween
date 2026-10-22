"""Check every lettering element against the platform safe area and render key check frames.

Safe area comes from 文字檢查框.png (guide lines at x 16/283, y 82/475.5 on 335x597),
scaled to 1080x1920 -> scene.SAFE_BOX. Output: output/storyboard/safe_check.png
"""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import scene

OUT = scene.ROOT / "output/storyboard/safe_check.png"


def bbox(arr, rot_pad=0):
    a = arr[..., 3] > 0.04
    ys, xs = np.where(a)
    x0, y0, x1, y1 = xs.min(), ys.min(), xs.max(), ys.max()
    return (x0 - rot_pad, y0 - rot_pad, x1 + rot_pad, y1 + rot_pad)


def inside(b, safe):
    return b[0] >= safe[0] and b[1] >= safe[1] and b[2] <= safe[2] and b[3] <= safe[3]


def main():
    A = scene.assets()
    safe = scene.SAFE_BOX
    items = []
    for (s, e, style, b), (_, _, en, zh) in zip(A.balloons, scene.SUBS):
        # Trickster balloons wobble +-2 deg: pad by half-width * sin(2 deg).
        bb = bbox(b["rgba"])
        pad = int((bb[2] - bb[0]) / 2 * math.sin(math.radians(2)) + 2) if style == "trickster" else 0
        items.append((f"對話框 {en}", bbox(b["rgba"], pad)))
    for (s, e, arr, c), (text, *_rest) in zip(A.tags, scene.ROLE_TAGS):
        items.append((f"名牌 {text}", bbox(arr)))
    items.append(("擬聲字 KRAK!", bbox(A.sfx_word)))
    L = A.info
    items.append(("資訊卡 底框＋陰影", bbox(L["body"])))
    items.append(("資訊卡 社團橫幅", bbox(L["ribbon"])))
    for (arr, _), (label, _t) in zip(L["rows"], scene.INFO_LINES):
        items.append((f"資訊卡 {label}列", bbox(arr)))
    items.append(("資訊卡 變裝號召", bbox(L["call"][0])))
    items.append(("資訊卡 抽獎列", bbox(L["prize_line"][0])))
    for arr, c in L["prize_chars"]:
        # Bounce up to +4% scale and +-6 deg after landing.
        b = bbox(arr)
        half = max(b[2] - b[0], b[3] - b[1]) / 2
        items.append(("資訊卡 神秘小禮(含彈跳)", bbox(arr, int(half * 0.04 + half * math.sin(math.radians(6)) + 2))))
    rows = []
    ok_all = True
    for name, b in items:
        ok = inside(b, safe)
        ok_all &= ok
        rows.append((name, b, ok))
        print(f"{'PASS' if ok else 'FAIL'}  {name:28s} x {b[0]:4d}–{b[2]:4d}  y {b[1]:4d}–{b[3]:4d}")
    print("ALL PASS" if ok_all else "SOME FAIL")

    # Key frames with the safe box drawn on.
    keys = [(1.6, "S02 名牌"), (4.0, "S04 對話框"), (6.4, "S05 對話框"),
            (8.4, "S06 名牌"), (11.0, "S08 對話框"), (13.6, "S09 對話框"),
            (17.25, "S12 擬聲字"), (19.6, "S13 資訊卡到齊"), (22.6, "S13 停留尾段")]
    font_dir = scene.FONT_DIR
    zh = ImageFont.truetype(str(font_dir / "NotoSansTC.ttf"), 26)
    zh.set_variation_by_axes([800])
    tw, th, gap = 324, 576, 24
    cols = 5
    head = 90
    rows_n = math.ceil(len(keys) / cols)
    sheet = Image.new("RGB", (cols * tw + (cols + 1) * gap, head + rows_n * (th + 60 + gap) + gap), (16, 14, 22))
    d = ImageDraw.Draw(sheet)
    title = ImageFont.truetype(str(font_dir / "NotoSansTC.ttf"), 34)
    title.set_variation_by_axes([900])
    d.text((gap, 22), f"安全框檢查：{sum(r[2] for r in rows)}/{len(rows)} 個文字元素在框內（紅框＝文字檢查框）・總長 {scene.DURATION:.1f} 秒",
           font=title, fill=(255, 255, 255))
    for i, (t, label) in enumerate(keys):
        im = Image.fromarray(scene.render_frame(t))
        dd = ImageDraw.Draw(im)
        dd.rectangle(safe, outline=(255, 40, 40), width=7)
        x = gap + (i % cols) * (tw + gap)
        y = head + (i // cols) * (th + 60 + gap)
        sheet.paste(im.resize((tw, th), Image.LANCZOS), (x, y))
        d.text((x, y + th + 10), f"{t:.2f}s  {label}", font=zh, fill=(255, 236, 140))
    sheet.save(OUT)
    print("saved", OUT)


if __name__ == "__main__":
    main()

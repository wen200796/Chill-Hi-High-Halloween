"""Render the storyboard sheet from real frames of scene.py.

Output: output/storyboard/storyboard.png and output/storyboard/frames/*.png
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import scene

ROOT = scene.ROOT
OUT = ROOT / "output/storyboard"

# (shot, key time, title, picture, action, audio)
BOARD = [
    ("S01", 0.45, "0.00–0.90 城市開場", "都市背景（左側紫綠區）",
     "雨夜都市先亮相，鏡頭快速推近紫綠霓虹大樓；雨絲、霧氣、霓虹閃爍。", "配樂：低頻氛圍＋神祕電子脈衝"),
    ("S02", 1.35, "0.90–2.00 搗蛋鬼登場", "搗蛋鬼 格1（攤手笑）",
     "從右側高速滑入，速度線＋鏡頭震動，落定時略微歪頭、露出狡猾笑容。", "SFX：短促 whoosh（0.85s）"),
    ("S03", 2.50, "2.00–3.05 笑聲", "搗蛋鬼 格3（大笑）",
     "配音前段的笑聲；臉部特寫小幅推近＋輕微晃動，切入時一格 glitch。", "VO：搗蛋鬼笑聲（配音 0.2–1.1s）\n配樂：加入不規則電子節奏"),
    ("S04", 4.00, "3.05–4.90 「Why so serious?」", "搗蛋鬼 格2（托腮斜眼）",
     "假裝思考的近景，慢推＋頭部微傾。人物略往下，上方白色歪扭對話框彈出（紫色偏移陰影），尾巴指向他；隨配音出現與收起。", "VO：Why so serious?\n配樂降低（ducking）"),
    ("S05", 6.90, "4.90–7.60 「Let's have some fun!」", "搗蛋鬼 格4（伸手邀請）",
     "慢慢漂移，在 \"fun!\" 重音處猛推向伸出的手＋速度線；對話框在上方輕晃，台詞結束時 RGB glitch。", "VO：Let's have some fun!\nSFX：電子 glitch stinger（7.15s）"),
    ("S06", 8.30, "7.60–8.80 英雄登場", "英雄 格1（正面胸像）",
     "切到冷藍色都市（月亮側）；低角度、鏡頭由胸前黃寶石往上搖到面罩；披風輕微飄動。", "SFX：深沉 cinematic impact（7.6s）\n＋披風掠風聲（8.1s）"),
    ("S07", 9.60, "8.80–10.00 鎖定目光", "英雄 格2（側望）",
     "慢推，目光朝畫面另一側；眼部冷光一閃，冷藍輪廓光。", "配樂：深沉鼓擊＋穩定低音"),
    ("S08", 11.20, "10.00–12.25 「I see your weakness.」", "英雄 格3（臉部特寫）",
     "先略高、微低頭的角度，隨台詞回正並抬眼；下方深藍切角硬框對話框沉穩滑入（避開頭盔與臉）。", "VO：I see your weakness.\n配樂降低"),
    ("S09", 13.80, "12.25–15.00 「And your potential.」", "英雄 格4（伸手）",
     "沿用原圖伸手姿勢（不扭曲），緩慢推近；下方深藍硬框對話框，不擋胸前寶石。", "VO：And your potential.\n配樂降低"),
    ("S10", 15.40, "15.00–15.85 笑容停住", "搗蛋鬼 格2（臉部大特寫）",
     "快速切回搗蛋鬼，急推後停格感；畫面去飽和一瞬。", "配樂短暫抽空（留白）"),
    ("S11", 16.40, "15.85–16.75 狡笑重現", "搗蛋鬼 格1（臉部大特寫）",
     "重新露出狡猾笑容，頭再歪一點；一格 glitch 切入。", "SFX：細微 glitch"),
    ("S12a", 17.30, "17.10 撞擊瞬間", "搗蛋鬼 格4 ＋ 英雄 格1",
     "斜向上下分割，雙方從兩側滑入；紫綠與冷藍光在中線交會，爆炸星形＋擬聲字「KRAK!」彈出（約 0.75 秒後淡出）＋震動。", "SFX：漫畫撞擊＋低頻衝擊（17.1s）\n音樂重拍"),
    ("S12b", 19.00, "17.85–19.80 對峙定格", "搗蛋鬼 格4 ＋ 英雄 格1",
     "擬聲字消失，畫面留給雙方對峙並定格到結尾；只剩極緩慢的推近與雨絲。", "殘響於 19.8s 前自然收束"),
]


def main():
    (OUT / "frames_v2").mkdir(parents=True, exist_ok=True)
    font_dir = ROOT / "output/_build/fonts"

    def zh(size, weight=700):
        f = ImageFont.truetype(str(font_dir / "NotoSansTC.ttf"), size)
        f.set_variation_by_axes([weight])
        return f

    tw, th = 330, 587
    cols, gap = 4, 30
    text_h = 300
    head = 300
    sheet_w = cols * tw + (cols + 1) * gap
    rows = (len(BOARD) + cols - 1) // cols
    sheet = Image.new("RGB", (sheet_w, head + rows * (th + text_h + gap) + gap), (16, 14, 22))
    d = ImageDraw.Draw(sheet)
    d.text((gap, 26), "分鏡 v2・漫畫對話框版（9:16・1080×1920・30fps・19.8 秒）", font=zh(34, 900), fill=(255, 255, 255))
    d.text((gap, 76), "每格皆為渲染器實際輸出的畫面。對白改為漫畫對話框：搗蛋鬼在上（白色歪扭泡泡）、英雄在下（深藍切角硬框），呼應結尾上下對峙。", font=zh(22, 400), fill=(190, 185, 210))

    # Timeline bar: shots + voice segments.
    x0, x1, y = gap, sheet_w - gap, 140
    sx = (x1 - x0) / scene.DURATION
    for i, (s, e, name) in enumerate(scene.SHOTS):
        col = (120, 60, 170) if "trickster" in name or name in ("s04_why_so_serious", "s05_have_some_fun", "s10_smile_freeze", "s11_smile_returns", "s01_city") else (40, 90, 170)
        if name == "s12_standoff":
            col = (90, 90, 110)
        d.rectangle([x0 + s * sx, y, x0 + e * sx - 2, y + 44], fill=col)
        d.text((x0 + s * sx + 4, y + 8), f"S{i + 1:02d}", font=zh(20, 700), fill=(255, 255, 255))
    for s, e, en, _ in scene.SUBS:
        d.rectangle([x0 + s * sx, y + 54, x0 + e * sx, y + 76], fill=(255, 220, 90))
    d.rectangle([x0 + (scene.JOKER_VO_AT + 0.2) * sx, y + 54, x0 + (scene.JOKER_VO_AT + 1.1) * sx, y + 76], fill=(200, 170, 70))
    for t in range(0, 21, 2):
        d.text((x0 + t * sx - 6, y + 84), f"{t}s", font=zh(18, 400), fill=(170, 170, 190))
    d.text((x0, y + 112), "■ 紫＝搗蛋鬼鏡頭　■ 藍＝英雄鏡頭　■ 灰＝對峙　黃條＝英文配音/字幕區間（深黃＝笑聲）",
           font=zh(19, 400), fill=(190, 185, 210))

    for i, (sid, t, title, pic, action, audio) in enumerate(BOARD):
        frame = Image.fromarray(scene.render_frame(t))
        frame.resize((540, 960), Image.LANCZOS).save(OUT / "frames_v2" / f"{sid}.png")
        cx = gap + (i % cols) * (tw + gap)
        cy = head + (i // cols) * (th + text_h + gap)
        sheet.paste(frame.resize((tw, th), Image.LANCZOS), (cx, cy))
        d.rectangle([cx, cy, cx + tw - 1, cy + th - 1], outline=(255, 255, 255), width=2)
        d.rectangle([cx, cy, cx + 64, cy + 34], fill=(255, 220, 90))
        d.text((cx + 8, cy + 3), sid, font=zh(22, 900), fill=(20, 15, 25))
        ty = cy + th + 10
        yy = ty
        for sub in wrap(d, title, zh(21, 900), tw):
            d.text((cx, yy), sub, font=zh(21, 900), fill=(255, 236, 140))
            yy += 30
        d.text((cx, yy + 2), "素材：" + pic, font=zh(18, 500), fill=(170, 210, 255))
        yy += 32
        body = zh(18, 400)
        for ln in [action, ""] + audio.split("\n"):
            for sub in wrap(d, ln, body, tw):
                d.text((cx, yy), sub, font=body, fill=(225, 222, 235))
                yy += 25
    sheet.save(OUT / "storyboard_v2_balloons.png")
    print("saved", OUT / "storyboard_v2_balloons.png", sheet.size)


def wrap(d, text, font, maxw):
    """Wrap mixed CJK/English text by pixel width without splitting English words."""
    import re
    tokens = re.findall(r"[A-Za-z0-9'.,!?()\-]+\s*|\s+|.", text)
    out, cur = [], ""
    for tok in tokens:
        if cur and d.textlength(cur + tok, font=font) > maxw:
            out.append(cur.rstrip())
            cur = tok.lstrip()
        else:
            cur += tok
    out.append(cur)
    return out


if __name__ == "__main__":
    main()

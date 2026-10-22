"""Storyboard sheet for the Harry x Dumbledore piece, built from real rendered frames.

Output: 哈鄧/output/storyboard/storyboard_v2.png and frames_v2/*.png
"""
import re

from PIL import Image, ImageDraw, ImageFont

import info_card
import magic_text
import scene

OUT = scene.ROOT / "output/storyboard"

BOARD = [
    ("S1", 2.60, "0.00–3.20 大廳開場", "綠區背景＋哈利 格1（全身站姿）",
     "綠區全景緩慢推向獨自站立的哈利；翡翠綠體積光、魔法粒子、地面霧氣，長袍下擺輕擺。左上「Speaker」以魔法字點亮（1.2–3.1s）。",
     "低沉弦樂 drone、風聲、魔法嗡鳴；鋼片琴三拍子主題輕輕進入"),
    ("S2a", 4.25, "3.20–4.30「I won't live by」", "哈利 格5（魔杖抵下巴）",
     "中近景慢推，單側翡翠綠光、另一側陰影；台詞跟著配音逐字點亮。",
     "VO 3.35 起；配樂壓低；每個字點亮時一聲極輕的閃光音"),
    ("S2b", 5.95, "4.30–6.70「someone else's destiny.」", "哈利 格2（手抵額、閃電疤痕）",
     "在「someone」前的空檔切近景，疤痕清楚可見；句尾停留後，字化成火花往上散去。",
     "「destiny」時加一層合唱聲墊"),
    ("S3", 8.60, "6.70–9.55 鄧不利多現身", "哈利 格3（回頭側身，前景）＋鄧不利多 格1＋藍金區背景",
     "越肩鏡頭：前景哈利由清晰轉為失焦（rack focus），焦點移到大廳另一端的鄧不利多；藍銀粒子環繞。右上「Evaluator」點亮（7.3–9.45s）。",
     "豎琴滑奏；聲場由綠轉藍，低沉的魔法嗡鳴"),
    ("S4a", 11.00, "9.55–11.40「Choose wisely,」", "鄧不利多 格3（正面胸像）",
     "慢推，鬍鬚末端微擺；英文逐字點亮，中文「做出明智的選擇。」同步點亮（藍銀字＋金色火花）。",
     "VO 9.75 起；配樂壓低"),
    ("S4b", 12.60, "11.40–13.30「Harry.」", "鄧不利多 格5（眼睛大特寫）",
     "在停頓處切到眼睛大特寫，極緩推進；「Harry.」和中文「哈利，」最後點亮（中文語序不同，前面空著的位置在這時亮起）。",
     "「Harry」前後只留一個鋼片琴單音"),
    ("S5", 16.20, "13.30–17.10 魔法對峙", "長廊區背景＋哈利 格1＋鄧不利多 格1",
     "長廊縱深構圖：哈利在左前、鄧不利多在右後，中央是地面星形紋；鏡頭緩慢拉遠；綠色與藍銀能量從魔杖往中央延伸。",
     "定音鼓滾奏漸強、弦樂顫音、能量嗡鳴、riser"),
    ("S6a", 17.18, "17.10 光芒", "同上",
     "兩股能量幾乎相觸，一道短暫光芒照亮兩人輪廓；之後兩人持續對峙，不硬定格。", "低沉魔法衝擊＋鐘聲＋殘響（全片唯一的撞擊）"),
    ("S6b", 18.75, "17.75–19.40 資訊卡登場", "同上（雙方持續動態）",
     "比照小丑版：鏡頭輕微拉遠、大廳下沉，空出穹頂；羊皮紙資訊卡浮現（深褐墨線、暗金框、皮革褐橫幅，單色不繽紛），社團橫幅貼上，日期／地點／交通由金色火花逐行寫入，接著變裝號召，「神秘小禮」四個古金色字以柔和暖光逐一點亮彈出。",
     "卡片浮現的魔法閃光音；四個字各一聲鋼片琴音"),
    ("S6c", 22.20, "19.40–25.00 資訊停留", "同上",
     "內容到齊後完整停留約 5.4 秒（同小丑版）；兩人持續呼吸、長袍擺動，能量在中央閃爍；22.0 秒「神秘小禮」再彈跳一次；最後 0.25 秒淡出。",
     "鋼片琴主題配弦樂重現，收在小調和弦，殘響在 25 秒前收完"),
]


def font(name, size, weight=None):
    f = ImageFont.truetype(str(scene.FONT_DIR / name), size)
    if weight:
        try:
            f.set_variation_by_axes([weight])
        except Exception:
            pass
    return f


def wrap(d, text, f, maxw):
    tokens = re.findall(r"[A-Za-z0-9'.,!?()「」\-]+\s*|\s+|.", text)
    out, cur = [], ""
    for tok in tokens:
        if cur and d.textlength(cur + tok, font=f) > maxw:
            out.append(cur.rstrip())
            cur = tok.lstrip()
        else:
            cur += tok
    out.append(cur)
    return out


def main():
    (OUT / "frames_v2").mkdir(parents=True, exist_ok=True)
    zh = "LXGWWenKaiTC-Bold.ttf"
    boxes = magic_text.text_bboxes() + info_card.bboxes()
    sb = scene.SAFE_BOX
    inside = sum(1 for _, b in boxes if b[0] >= sb[0] and b[1] >= sb[1] and b[2] <= sb[2] and b[3] <= sb[3])
    cols, tw, th, gap, text_h, head = 5, 280, 498, 24, 290, 250
    rows = (len(BOARD) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw + (cols + 1) * gap, head + rows * (th + text_h + gap) + gap), (12, 14, 20))
    d = ImageDraw.Draw(sheet)
    d.text((gap, 22), "史萊哲林哈利 × 鄧不利多｜分鏡 v2・加結尾資訊卡（9:16・1080×1920・24fps・25.0 秒）", font=font(zh, 36),
           fill=(235, 240, 235))
    d.text((gap, 72), f"每格都是渲染器輸出的實際畫面（紅框＝文字安全框，文字元素 {inside}/{len(boxes)} 在框內）。"
                      "音樂和音效等分鏡確認後再製作。", font=font(zh, 21), fill=(170, 185, 180))
    # Timeline bar
    x0, x1, y = gap, sheet.width - gap, 120
    sx = (x1 - x0) / scene.DURATION
    for s, e, name in scene.SHOTS:
        col = (30, 110, 70) if ("harry" in name or name == "s1_hall") else (40, 70, 140)
        if name in ("s5_standoff", "s6_hold"):
            col = (80, 85, 100)
        if name == "s3_over_shoulder":
            col = (50, 90, 110)
        d.rectangle([x0 + s * sx, y, x0 + e * sx - 2, y + 36], fill=col)
    for ln in scene.LINES:
        d.rectangle([x0 + ln[2] * sx, y + 44, x0 + ln[3] * sx, y + 62], fill=(230, 210, 120))
    d.rectangle([x0 + scene.INFO_AT * sx, y + 44, x0 + scene.DURATION * sx, y + 62], fill=(190, 150, 70))
    for t in range(0, 26, 5):
        d.text((x0 + t * sx - 6, y + 68), f"{t}s", font=font(zh, 17), fill=(150, 160, 160))
    d.text((x0, y + 92), "綠＝哈利　藍＝鄧不利多　灰＝對峙　黃條＝台詞點亮　金條＝例會資訊卡", font=font(zh, 17), fill=(150, 160, 160))
    for i, (sid, t, title, pic, action, audio) in enumerate(BOARD):
        im = Image.fromarray(scene.render_frame(t))
        im.resize((540, 960), Image.LANCZOS).save(OUT / "frames_v2" / f"{sid}.png")
        dd = ImageDraw.Draw(im)
        dd.rectangle(sb, outline=(255, 50, 50), width=4)
        cx = gap + (i % cols) * (tw + gap)
        cy = head + (i // cols) * (th + text_h + gap)
        sheet.paste(im.resize((tw, th), Image.LANCZOS), (cx, cy))
        d.rectangle([cx, cy, cx + tw - 1, cy + th - 1], outline=(220, 225, 220), width=2)
        d.rectangle([cx, cy, cx + 58, cy + 30], fill=(230, 210, 120))
        d.text((cx + 7, cy + 2), sid, font=font(zh, 21), fill=(15, 15, 20))
        yy = cy + th + 8
        for line in wrap(d, title, font(zh, 19), tw):
            d.text((cx, yy), line, font=font(zh, 19), fill=(240, 220, 140))
            yy += 26
        for line in wrap(d, "素材：" + pic, font(zh, 16), tw):
            d.text((cx, yy), line, font=font(zh, 16), fill=(150, 200, 230))
            yy += 22
        for line in wrap(d, action, font(zh, 16), tw) + [""] + wrap(d, "聲音：" + audio, font(zh, 16), tw):
            d.text((cx, yy), line, font=font(zh, 16), fill=(215, 218, 215))
            yy += 22
    sheet.save(OUT / "storyboard_v2.png")
    print("saved", OUT / "storyboard_v2.png", sheet.size, f"text units inside safe area: {inside}/{len(boxes)}")


if __name__ == "__main__":
    main()

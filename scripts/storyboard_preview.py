#!/usr/bin/env python3
"""從輸出的 MP4 擷取關鍵畫面，排成 3×3 分鏡預覽圖。用法：storyboard_preview.py <影片> <輸出 png>"""
import os
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFont

TIMES = [0, 2, 4, 7, 9, 10.5, 12, 13.5, 14.5]
LABELS = ["神祕開場", "次元裂縫", "角色登場", "英雄集結", "英雄不只有一種樣子", "等等……", "即席演講！", "勇敢上台", "活動資訊"]

video, out = sys.argv[1], sys.argv[2]
W, H, PAD, HEAD = 360, 640, 16, 56
FONT_CANDIDATES = ["/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"]
font_path = next((f for f in FONT_CANDIDATES if os.path.exists(f)), None)
font = ImageFont.truetype(font_path, 26) if font_path else ImageFont.load_default()

sheet = Image.new("RGB", (3 * W + 4 * PAD, 3 * (H + HEAD) + 4 * PAD), (12, 8, 20))
draw = ImageDraw.Draw(sheet)
with tempfile.TemporaryDirectory() as tmp:
    for i, (t, label) in enumerate(zip(TIMES, LABELS)):
        frame = os.path.join(tmp, f"{i}.png")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(t), "-i", video, "-frames:v", "1", frame], check=True)
        im = Image.open(frame).convert("RGB").resize((W, H), Image.LANCZOS)
        x = PAD + (i % 3) * (W + PAD)
        y = PAD + (i // 3) * (H + HEAD + PAD)
        draw.text((x + 4, y + 12), f"{t:>4}s  {label}", fill=(255, 201, 74), font=font)
        sheet.paste(im, (x, y + HEAD))
sheet.save(out)
print("wrote", out)

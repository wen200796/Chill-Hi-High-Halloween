"""Split the two 3x2 character sheets into panels and cut each figure off its white backdrop.

Output: 哈鄧/output/_build/cutouts/{harry,dumbledore}_{1..6}.png (RGBA) + meta.json
Panels are numbered row by row: 1-3 top (left to right), 4-6 bottom.
Source images are only read, never modified.
"""
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output/_build/cutouts"

SHEETS = {
    "harry": ("蛇徽魔法學院角色姿態集.png", [
        (5, 0, 499, 556), (521, 0, 1015, 531), (1037, 0, 1536, 532),
        (5, 558, 499, 1012), (521, 534, 1015, 1012), (1037, 536, 1536, 1012)]),
    "dumbledore": ("銀鬚巫師角色設定集.png", [
        (14, 0, 506, 528), (521, 0, 1011, 529), (1030, 0, 1536, 529),
        (14, 531, 506, 1008), (521, 531, 1011, 1008), (1030, 528, 1536, 1008)]),
}


def cut(rgb):
    mn, mx = rgb.min(axis=2), rgb.max(axis=2)
    # The backdrop is near pure white; the beard is grey-lavender (min channel <~205), so it survives.
    white = ((mn > 236) & (mx - mn < 18)).astype(np.uint8)
    # Full-body panels have a pale grey ground shadow under the feet: treat it as backdrop too
    # (only in the bottom strip, where the shoes are dark and cannot be mistaken for it).
    strip = int(rgb.shape[0] * 0.88)
    white[strip:] |= ((mn[strip:] > 170) & (mx[strip:] - mn[strip:] < 24)).astype(np.uint8)
    floor = int(rgb.shape[0] * 0.945)  # the cast-shadow line right under the soles is darker
    white[floor:] |= ((mn[floor:] > 105) & (mx[floor:] - mn[floor:] < 30)).astype(np.uint8)
    n, lab = cv2.connectedComponents(white, connectivity=4)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(border))
    # White pockets sealed off by thin hair/beard strands: absorb them when most of their rim
    # sits right next to the open background (eye whites, shirt collars and glints do not).
    for _ in range(3):
        near = cv2.dilate(bg.astype(np.uint8), np.ones((21, 21), np.uint8)).astype(bool)
        grew = False
        for l in range(1, n):
            comp = lab == l
            if bg[comp].any() or comp.sum() < 4:
                continue
            rim = cv2.dilate(comp.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & ~comp
            if near[rim].mean() > 0.45:
                bg |= comp
                grew = True
        if not grew:
            break
    fg = (~bg).astype(np.uint8) * 255
    fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    alpha = cv2.GaussianBlur(cv2.erode(fg, np.ones((2, 2), np.uint8)), (3, 3), 0).astype(np.float32) / 255
    a = np.clip(alpha, 1e-3, 1)[..., None]
    col = np.clip((rgb.astype(np.float32) - 255 * (1 - a)) / a, 0, 255)
    col = np.where(alpha[..., None] > 0.98, rgb, col)
    # A side counts as cropped when the figure reaches within a few pixels of it.
    m = fg > 0
    sides = {
        "top": bool(m[:6].any(axis=0).mean() > 0.08), "bottom": bool(m[-6:].any(axis=0).mean() > 0.08),
        "left": bool(m[:, :6].any(axis=1).mean() > 0.08), "right": bool(m[:, -6:].any(axis=1).mean() > 0.08),
    }
    return np.dstack([col.astype(np.uint8), (alpha * 255).astype(np.uint8)]), sides


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    meta = {}
    for name, (file, boxes) in SHEETS.items():
        sheet = np.asarray(Image.open(ROOT / file).convert("RGB"))
        for i, (x0, y0, x1, y1) in enumerate(boxes, 1):
            rgba, sides = cut(sheet[y0:y1, x0:x1])
            Image.fromarray(rgba, "RGBA").save(OUT / f"{name}_{i}.png")
            meta[f"{name}_{i}"] = sides
    (OUT / "meta.json").write_text(json.dumps(meta, indent=1))
    print(json.dumps(meta))


if __name__ == "__main__":
    main()

"""Split the 2x2 character sheets into four panels and cut each figure off its white backdrop.

Output: output/_build/cutouts/{joker,batman}_{1..4}.png (RGBA), numbered
1 = top-left, 2 = top-right, 3 = bottom-left, 4 = bottom-right.
Original images are only read, never modified.
"""
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output/_build/cutouts"

# Panel boxes (x0, y0, x1, y1) measured from the white gutters of each sheet.
PANELS = {
    "joker": [(18, 8, 619, 621), (635, 8, 1237, 620), (18, 629, 612, 1231), (635, 635, 1237, 1232)],
    "batman": [(20, 0, 619, 627), (636, 0, 1235, 618), (20, 627, 619, 1231), (636, 627, 1235, 1231)],
}


def cut(rgb):
    h, w, _ = rgb.shape
    mn, mx = rgb.min(axis=2), rgb.max(axis=2)
    white = ((mn > 222) & (mx - mn < 30)).astype(np.uint8)
    # Background = white regions connected to the panel border.
    n, lab = cv2.connectedComponents(white, connectivity=4)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])))
    bg = np.isin(lab, [l for l in border if l != 0 and white[lab == l].any()])
    # White pockets sealed off by thin hair strands: absorb them when most of their
    # rim sits right next to the open background (eye whites and teeth do not).
    for _ in range(3):
        near = cv2.dilate(bg.astype(np.uint8), np.ones((25, 25), np.uint8)).astype(bool)
        grew = False
        for l in range(1, n):
            comp = lab == l
            if bg[comp].any() or not white[comp].any():
                continue
            rim = cv2.dilate(comp.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & ~comp
            if near[rim].mean() > 0.3:
                bg |= comp
                grew = True
        if not grew:
            break
    fg = (~bg).astype(np.uint8) * 255
    fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    # Soft 1px edge plus white-fringe removal (un-premultiply against white).
    alpha = cv2.GaussianBlur(cv2.erode(fg, np.ones((2, 2), np.uint8)), (3, 3), 0).astype(np.float32) / 255
    a = np.clip(alpha, 1e-3, 1)[..., None]
    col = np.clip((rgb.astype(np.float32) - 255 * (1 - a)) / a, 0, 255)
    col = np.where(alpha[..., None] > 0.98, rgb, col)
    # Which panel sides the figure is cropped by (needs a soft fade when composited).
    sides = {
        "top": bool(fg[0].mean() > 25), "bottom": bool(fg[-1].mean() > 25),
        "left": bool(fg[:, 0].mean() > 25), "right": bool(fg[:, -1].mean() > 25),
    }
    return np.dstack([col.astype(np.uint8), (alpha * 255).astype(np.uint8)]), sides


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    meta = {}
    for name, boxes in PANELS.items():
        sheet = np.asarray(Image.open(ROOT / f"{name}.png").convert("RGB"))
        for i, (x0, y0, x1, y1) in enumerate(boxes, 1):
            rgba, sides = cut(sheet[y0:y1, x0:x1])
            Image.fromarray(rgba, "RGBA").save(OUT / f"{name}_{i}.png")
            meta[f"{name}_{i}"] = sides
    (OUT / "meta.json").write_text(json.dumps(meta, indent=1))
    print(json.dumps(meta, indent=1))


if __name__ == "__main__":
    main()

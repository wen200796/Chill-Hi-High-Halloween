"""Meeting-info end card, following the trickster/hero version (same content, rhythm and hold),
restyled for the wizarding piece in a restrained parchment palette (sepia ink, aged-gold rule,
leather-brown banner, one dark shadow): lines are written in by a warm spark and "神秘小禮"
glows softly in antique gold.

Timing mirrors the trickster/hero v4 card: lands 0.75 s after the flash, fully written by ~19.4 s,
then holds to the end; the prize letters bounce once more 3 s before the end.
"""
import math

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import scene

W, H = scene.W, scene.H
INFO_AT = scene.INFO_AT
CARD = (70, 340, 894, 870)          # card body, inside SAFE_BOX (52, 265, 912, 1529)
CLUB_NAME = ("Chill Hi High", "中英雙語國際演講會")
INFO_LINES = [
    ("日期", "10/27（二）19:15–21:15"),
    ("地點", "社會創新實驗中心 107 會議室"),
    ("交通", "忠孝復興站 2 號出口 步行 7 分鐘"),
]
INFO_CALL = "歡迎大家一起變裝出場！"
INFO_PRIZE = ("現場還有", "神秘小禮", "抽獎等你帶走！")
PRIZE_REBOUNCE_AT = scene.DURATION - 3.0

INK = (46, 30, 18, 255)            # sepia ink
PARCHMENT = (232, 218, 186, 255)
GOLD = (150, 116, 60, 255)         # aged gold-brown rule
LEATHER = (92, 58, 32, 255)        # banner / chips
SHADOW = (24, 16, 10, 255)
CREAM = (240, 228, 200, 255)

_L = None


def _font(name, size):
    return ImageFont.truetype(str(scene.FONT_DIR / name), size)


def _premul(img, ss):
    img = img.resize((W, H), Image.LANCZOS)
    arr = np.asarray(img).astype(np.float32) / 255
    arr[..., :3] *= arr[..., 3:4]
    return arr


def _bbox(arr):
    ys, xs = np.where(arr[..., 3] > 0.04)
    return (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)


def _build():
    ss = 2
    x0, y0, x1, y1 = [v * ss for v in CARD]
    L = {}

    def canvas():
        im = Image.new("RGBA", (W * ss, H * ss), (0, 0, 0, 0))
        return im, ImageDraw.Draw(im)

    # Body: one dark shadow, parchment, sepia ink border, aged-gold inner rule.
    im, d = canvas()
    r = 16 * ss
    d.rounded_rectangle((x0 + 12 * ss, y0 + 14 * ss, x1 + 12 * ss, y1 + 14 * ss), r, fill=SHADOW)
    d.rounded_rectangle((x0, y0, x1, y1), r, fill=PARCHMENT, outline=INK, width=6 * ss)
    inset = 16 * ss
    d.rounded_rectangle((x0 + inset, y0 + inset, x1 - inset, y1 - inset), r // 2, outline=GOLD, width=2 * ss)
    for cx, cy in ((x0 + inset, y0 + inset), (x1 - inset, y0 + inset), (x0 + inset, y1 - inset), (x1 - inset, y1 - inset)):
        k = 9 * ss
        d.polygon([(cx, cy - k), (cx + k, cy), (cx, cy + k), (cx - k, cy)], fill=GOLD, outline=INK)
    body = np.asarray(im).astype(np.float32) / 255
    # Aged-paper mottling, only on the parchment.
    rng = np.random.default_rng(3)
    n = cv2.resize(rng.random((40, 30)).astype(np.float32), (W * ss, H * ss), interpolation=cv2.INTER_CUBIC)
    n = cv2.GaussianBlur(n, (0, 0), 30 * ss)
    paper = (np.abs(body[..., :3] - np.array(PARCHMENT[:3]) / 255).sum(axis=2) < 0.02)[..., None]
    body[..., :3] = np.where(paper, body[..., :3] * (0.9 + 0.12 * n[..., None]), body[..., :3])
    L["body"] = _premul(Image.fromarray((np.clip(body, 0, 1) * 255).astype(np.uint8), "RGBA"), ss)

    # Club ribbon across the top edge: leather-brown banner, gold rule, cream lettering.
    im, d = canvas()
    en = _font("Metamorphous-Regular.ttf", 46 * ss)
    zh = _font("LXGWWenKaiTC-Bold.ttf", 36 * ss)
    ew, zw = d.textlength(CLUB_NAME[0], font=en), d.textlength(CLUB_NAME[1], font=zh)
    gap = 16 * ss
    total = ew + gap + zw
    cx, cy = (x0 + x1) / 2, y0 - 4 * ss
    rb = (cx - total / 2 - 26 * ss, cy - 36 * ss, cx + total / 2 + 26 * ss, cy + 36 * ss)
    for sgn in (-1, 1):  # swallow-tail ends
        ex = rb[0] if sgn < 0 else rb[2]
        d.polygon([(ex, rb[1] + 10 * ss), (ex + sgn * 28 * ss, rb[1] + 10 * ss), (ex + sgn * 17 * ss, cy + 5 * ss),
                   (ex + sgn * 28 * ss, rb[3] + 2 * ss), (ex, rb[3] + 2 * ss)], fill=(70, 44, 24, 255), outline=INK)
    d.rectangle(rb, fill=LEATHER, outline=INK, width=5 * ss)
    d.rectangle((rb[0] + 7 * ss, rb[1] + 7 * ss, rb[2] - 7 * ss, rb[3] - 7 * ss), outline=GOLD, width=2 * ss)
    eb = en.getbbox(CLUB_NAME[0])
    d.text((cx - total / 2, cy - (eb[3] + eb[1]) / 2), CLUB_NAME[0], font=en, fill=(226, 196, 140, 255))
    zb = zh.getbbox(CLUB_NAME[1])
    d.text((cx - total / 2 + ew + gap, cy - (zb[3] + zb[1]) / 2), CLUB_NAME[1], font=zh, fill=CREAM)
    L["ribbon"] = _premul(im, ss)
    L["ribbon_c"] = (cx / ss, cy / ss)

    # Info rows: coloured chip + ink text (each row is written in by a spark).
    chip_f = _font("LXGWWenKaiTC-Bold.ttf", 32 * ss)
    row_f = _font("LXGWWenKaiTC-Bold.ttf", 40 * ss)
    chips = [LEATHER, LEATHER, LEATHER]
    rows = []
    for i, ((label, text), col) in enumerate(zip(INFO_LINES, chips)):
        im, d = canvas()
        ry = y0 + (92 + i * 72) * ss
        lx = x0 + 42 * ss
        lw = d.textlength(label, font=chip_f)
        d.rounded_rectangle((lx, ry - 25 * ss, lx + lw + 24 * ss, ry + 25 * ss), 8 * ss, fill=col)
        cb = chip_f.getbbox(label)
        d.text((lx + 12 * ss, ry - (cb[3] + cb[1]) / 2), label, font=chip_f, fill=CREAM)
        rb_ = row_f.getbbox(text)
        d.text((lx + lw + 42 * ss, ry - (rb_[3] + rb_[1]) / 2), text, font=row_f, fill=INK)
        arr = _premul(im, ss)
        rows.append((arr, _bbox(arr)))
    L["rows"] = rows

    # Divider + call to action.
    im, d = canvas()
    dy = y0 + 312 * ss
    d.line((x0 + 60 * ss, dy, x1 - 60 * ss, dy), fill=GOLD, width=2 * ss)
    mx = (x0 + x1) / 2
    d.polygon([(mx, dy - 8 * ss), (mx + 8 * ss, dy), (mx, dy + 8 * ss), (mx - 8 * ss, dy)], fill=GOLD, outline=INK)
    call_f = _font("LXGWWenKaiTC-Bold.ttf", 42 * ss)
    cw = d.textlength(INFO_CALL, font=call_f)
    cb = call_f.getbbox(INFO_CALL)
    d.text((mx - cw / 2, dy + 52 * ss - (cb[3] + cb[1]) / 2), INFO_CALL, font=call_f, fill=(110, 40, 26, 255))
    arr = _premul(im, ss)
    L["call"] = (arr, _bbox(arr))

    # Prize line: ink lead/tail text plus four glowing gold characters.
    pre, prize, post = INFO_PRIZE
    small = _font("LXGWWenKaiTC-Bold.ttf", 38 * ss)
    big = _font("LXGWWenKaiTC-Bold.ttf", 60 * ss)
    char_w = 66 * ss
    pw, qw = d.textlength(pre, font=small), d.textlength(post, font=small)
    total = pw + 16 * ss + char_w * len(prize) + 16 * ss + qw
    py = dy + 136 * ss
    px = mx - total / 2
    im, d = canvas()
    sb = small.getbbox(pre)
    d.text((px, py - (sb[3] + sb[1]) / 2), pre, font=small, fill=INK)
    d.text((px + pw + 32 * ss + char_w * len(prize), py - (sb[3] + sb[1]) / 2), post, font=small, fill=INK)
    arr = _premul(im, ss)
    L["prize_line"] = (arr, _bbox(arr))
    chars = []
    for i, ch in enumerate(prize):
        im, d = canvas()
        ccx = px + pw + 16 * ss + char_w * (i + 0.5)
        bw = d.textlength(ch, font=big)
        bb = big.getbbox(ch)
        d.text((ccx - bw / 2, py - (bb[3] + bb[1]) / 2), ch, font=big, fill=(196, 150, 70, 255),
               stroke_width=4 * ss, stroke_fill=(52, 32, 16, 255))
        arr = _premul(im, ss)
        chars.append((arr, (ccx / ss, py / ss)))
    L["prize_chars"] = chars
    return L


def layers():
    global _L
    if _L is None:
        _L = _build()
    return _L


def _pop(canvas, arr, center, scale, alpha, rot=0.0):
    if alpha <= 0:
        return
    M = scene.affine((W, H), (center[0] / W, center[1] / H), center, scale, rot)
    scene.over(canvas, np.clip(cv2.warpAffine(arr, M, (W, H)), 0, 1), alpha)


def _spark(canvas, x, y, a):
    lay = np.zeros((H, W), np.float32)
    cv2.circle(lay, (int(x), int(y)), 5, a, -1, cv2.LINE_AA)
    cv2.line(lay, (int(x) - 24, int(y)), (int(x) + 24, int(y)), a * 0.7, 2, cv2.LINE_AA)
    cv2.line(lay, (int(x), int(y) - 22), (int(x), int(y) + 22), a * 0.5, 1, cv2.LINE_AA)
    g = cv2.GaussianBlur(lay, (0, 0), 5) * 2 + lay
    scene.screen(canvas, g[..., None] * np.array((0.95, 0.78, 0.5), np.float32), 0.8)


def _write_in(canvas, arr, bbox, t, t0, dur=0.32):
    """Reveal a pre-rendered line left to right behind a golden spark (a quill of light)."""
    k = (t - t0) / dur
    if k <= 0:
        return
    x0, y0, x1, y1 = bbox
    front = x0 + (x1 - x0 + 20) * scene.ease_out(min(k, 1.0), 2)
    xs = np.arange(W, dtype=np.float32)[None, :, None]
    ramp = np.clip((front - xs) / 20.0, 0, 1)
    scene.over(canvas, arr * ramp)
    if k < 1:
        _spark(canvas, front, (y0 + y1) / 2, 1.0)


def draw(canvas, t):
    if t < INFO_AT + 0.05:
        return canvas
    L = layers()
    bc = ((CARD[0] + CARD[2]) / 2, (CARD[1] + CARD[3]) / 2)
    k = (t - INFO_AT - 0.1) / 0.3
    if k > 0:
        # The card materialises: a soft scale-up with a brief golden rim glow.
        scale = scene.lerp(0.9, 1.0, scene.ease_out(min(k, 1)))
        _pop(canvas, L["body"], bc, scale, min(1.0, k * 1.6))
        if k < 1.6:
            g = np.zeros((H, W), np.float32)
            cv2.rectangle(g, (CARD[0], CARD[1]), (CARD[2], CARD[3]), 1.0, 4)
            g = cv2.GaussianBlur(g, (0, 0), 10) * 2.2
            scene.screen(canvas, g[..., None] * np.array((0.9, 0.72, 0.45), np.float32), 0.7 * max(0.0, 1 - k / 1.6))
    k = (t - INFO_AT - 0.25) / 0.22
    if k > 0:
        _pop(canvas, L["ribbon"], L["ribbon_c"], scene.lerp(1.15, 1.0, scene.ease_out(min(k, 1))), min(1.0, k * 1.5))
    for i, (arr, bb) in enumerate(L["rows"]):
        _write_in(canvas, arr, bb, t, INFO_AT + 0.38 + i * 0.14)
    _write_in(canvas, L["call"][0], L["call"][1], t, INFO_AT + 0.85, 0.28)
    k = (t - INFO_AT - 1.0) / 0.18
    if k > 0:
        scene.over(canvas, L["prize_line"][0], min(1.0, k))
    for i, (arr, c) in enumerate(L["prize_chars"]):
        t0 = INFO_AT + 1.1 + i * 0.12
        kk = (t - t0) / 0.16
        if kk <= 0:
            continue
        sc = scene.lerp(0.2, 1.3, scene.ease_out(kk, 3)) if kk < 1 else scene.lerp(1.3, 1.0, scene.ease(min(1.0, (kk - 1) * 1.5)))
        bob = 0.04 * math.sin((t - t0) * 6 + i * 1.3) if t > t0 + 0.4 else 0.0
        k2 = (t - PRIZE_REBOUNCE_AT - i * 0.1) / 0.25
        if 0 < k2 < 1:
            bob += 0.22 * math.sin(math.pi * k2)
        rot = 6 * math.sin((t - t0) * 3 + i)
        # Gold glow that flares when each letter ignites, then breathes gently.
        flare = max(0.0, 1 - (t - t0) / 0.5)
        g = np.zeros((H, W), np.float32)
        cv2.circle(g, (int(c[0]), int(c[1])), 30, 1.0, -1, cv2.LINE_AA)
        g = cv2.GaussianBlur(g, (0, 0), 16)
        scene.screen(canvas, g[..., None] * np.array((0.85, 0.62, 0.32), np.float32),
                     0.12 + 0.45 * flare + 0.04 * math.sin(t * 2.5 + i))
        _pop(canvas, arr, c, sc + bob, 1.0, rot)
    return canvas


def bboxes():
    """Frame-space extents of every card element at rest (+ bounce/rotation margin for the prize)."""
    L = layers()
    out = [("資訊卡 底框＋陰影", _bbox(L["body"])), ("資訊卡 社團橫幅", _bbox(L["ribbon"]))]
    for (arr, bb), (label, _) in zip(L["rows"], INFO_LINES):
        out.append((f"資訊卡 {label}列", bb))
    out.append(("資訊卡 變裝號召", L["call"][1]))
    out.append(("資訊卡 抽獎列", L["prize_line"][1]))
    for arr, c in L["prize_chars"]:
        b = _bbox(arr)
        half = max(b[2] - b[0], b[3] - b[1]) / 2
        pad = int(half * 0.26 + half * math.sin(math.radians(6)) + 2)
        out.append(("資訊卡 神秘小禮(含彈跳)", (b[0] - pad, b[1] - pad, b[2] + pad, b[3] + pad)))
    return out

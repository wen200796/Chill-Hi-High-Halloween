"""Dialogue lettering that lights up like a spell, word by word with the voice.

Each English word is "written in light": a bright spark sweeps across it, the glyphs flare
and settle into a steady glow, and embers drift off. The Chinese line ignites character by
character in step with the meaning of the English words. At the end of a line the text
dissolves upward into sparks. Harry's text burns emerald, Dumbledore's blue-silver with gold
sparks. Fonts: Metamorphous (English) and LXGW WenKai TC Bold (Chinese), both SIL OFL.
"""
import math

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import scene

W, H = scene.W, scene.H
BAND_Y0, BAND_H = 1200, 320     # text band in the lower part of SAFE_BOX (y 265-1529)
EN_ROW_Y = {1: [1316], 2: [1232, 1316]}   # glyph-top y of the English rows (by row count)
ZH_Y = 1410
EN_SIZE, ZH_SIZE = 64, 50
TAG_SIZE = 66
CENTER_X = (scene.SAFE_BOX[0] + scene.SAFE_BOX[2]) / 2   # safe area is not centered on the frame
WORD_SWEEP, CHAR_SWEEP = 0.22, 0.12
FLARE = 0.6
DISSOLVE = 0.35

STYLE = {
    "harry": dict(core=(0.86, 1.0, 0.92), glow=(0.18, 0.95, 0.48), spark=(0.75, 1.0, 0.8)),
    "dumbledore": dict(core=(1.0, 0.97, 0.9), glow=(0.5, 0.7, 1.0), spark=(1.0, 0.84, 0.5)),
}

_LINES = None
XS = np.arange(W, dtype=np.float32)[None, :]


def _font(name, size):
    return ImageFont.truetype(str(scene.FONT_DIR / name), size)


def _unit_mask(text, font, x, y, y0=BAND_Y0, h=BAND_H, ornament=False):
    img = Image.new("L", (W, h), 0)
    d = ImageDraw.Draw(img)
    d.text((x, y - y0), text, font=font, fill=255)
    if ornament:
        # Thin rules with diamond ends either side of a role title, like an inscription.
        bb = d.textbbox((x, y - y0), text, font=font)
        my = (bb[1] + bb[3]) / 2
        for sgn, edge in ((-1, bb[0] - 18), (1, bb[2] + 18)):
            end = edge + sgn * 46
            d.line((edge, my, end, my), fill=200, width=3)
            d.polygon([(end + sgn * 12, my), (end, my - 7), (end - sgn * 12, my), (end, my + 7)], fill=255)
            d.ellipse((edge - 4, my - 4, edge + 4, my + 4), fill=255)
    m = np.asarray(img).astype(np.float32) / 255
    ys, xs = np.where(m > 0.05)
    return m, (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)


def _build():
    en_f, zh_f = _font("Metamorphous-Regular.ttf", EN_SIZE), _font("LXGWWenKaiTC-Bold.ttf", ZH_SIZE)
    lines = []
    for speaker, words, at, end, zh, plan in scene.LINES:
        d = ImageDraw.Draw(Image.new("L", (8, 8)))
        units = []
        times = [at + wt for _, wt, _r in words]
        n_rows = max(r for _, _, r in words) + 1
        for row in range(n_rows):
            row_words = [(i, w) for i, (w, _, r) in enumerate(words) if r == row]
            full = " ".join(w for _, w in row_words)
            x = CENTER_X - d.textlength(full, font=en_f) / 2
            y = EN_ROW_Y[n_rows][row]
            for j, (i, word) in enumerate(row_words):
                prefix = " ".join(w for _, w in row_words[:j]) + (" " if j else "")
                m, bb = _unit_mask(word, en_f, x + d.textlength(prefix, font=en_f), y)
                units.append(dict(mask=m, bb=bb, t0=times[i], sweep=WORD_SWEEP))
        # Chinese: one unit per character, ignition times spread over the matching English words.
        zx = CENTER_X - d.textlength(zh, font=zh_f) / 2
        starts = [None] * len(zh)
        if plan is None:
            span0, span1 = times[0], times[-1] + 0.35
            for k in range(len(zh)):
                starts[k] = span0 + (span1 - span0) * k / len(zh)
        else:
            for c0, c1, wi in plan:
                s0 = times[wi]
                s1 = times[wi + 1] if wi + 1 < len(times) else s0 + 0.45
                for k in range(c0, c1):
                    starts[k] = s0 + 0.08 + (s1 - s0) * (k - c0) / max(1, c1 - c0)
        for k, ch in enumerate(zh):
            if ch.strip() == "":
                continue
            m, bb = _unit_mask(ch, zh_f, zx + d.textlength(zh[:k], font=zh_f), ZH_Y)
            units.append(dict(mask=m, bb=bb, t0=starts[k], sweep=CHAR_SWEEP))
        rng = np.random.default_rng(sum(map(ord, speaker)))  # deterministic across worker processes
        for u in units:
            x0, y0, x1, y1 = u["bb"]
            u["embers"] = [(rng.uniform(x0, x1), rng.uniform(y0, y1), rng.uniform(0, 0.5),
                            rng.uniform(25, 70), rng.uniform(-14, 14)) for _ in range(5)]
        lines.append(dict(speaker=speaker, units=units, start=at, end=end, style=STYLE[speaker],
                          y0=BAND_Y0, h=BAND_H))
    # Role titles: one inscription each, written in with a slower sweep.
    tag_f = _font("Metamorphous-Regular.ttf", TAG_SIZE)
    for text, speaker, at, end, (cx, cy) in scene.ROLE_TAGS:
        d = ImageDraw.Draw(Image.new("L", (8, 8)))
        y0, h = int(cy - 70), 140
        m, bb = _unit_mask(text, tag_f, cx - d.textlength(text, font=tag_f) / 2, cy - TAG_SIZE * 0.62, y0, h, True)
        u = dict(mask=m, bb=bb, t0=at, sweep=0.55)
        rng = np.random.default_rng(sum(map(ord, text)))
        u["embers"] = [(rng.uniform(bb[0], bb[2]), rng.uniform(bb[1], bb[3]), rng.uniform(0, 0.6),
                        rng.uniform(25, 60), rng.uniform(-14, 14)) for _ in range(14)]
        lines.append(dict(speaker=speaker, units=[u], start=at, end=end, style=STYLE[speaker], y0=y0, h=h))
    return lines


def lines():
    global _LINES
    if _LINES is None:
        _LINES = _build()
    return _LINES


def _screen(dst, rgb, amount):
    dst[:] = 1 - (1 - dst) * (1 - np.clip(rgb * amount, 0, 1))


def draw(frame, t):
    for ln in lines():
        if not (ln["start"] - 0.05 <= t <= ln["end"] + DISSOLVE):
            continue
        st = ln["style"]
        out = max(0.0, (t - ln["end"]) / DISSOLVE)
        live = 1.0 - scene.ease(out)
        y0b, hb = ln["y0"], ln["h"]
        mask = np.zeros((hb, W), np.float32)
        flare = np.zeros((hb, W), np.float32)
        sparks = []
        embers = []
        for u in ln["units"]:
            dt = t - u["t0"]
            if dt <= 0:
                continue
            x0, y0, x1, y1 = u["bb"]
            p = min(1.0, dt / u["sweep"])
            front = x0 + (x1 - x0 + 16) * scene.ease_out(p, 2)
            ramp = np.clip((front - XS) / 16.0, 0, 1)
            m = u["mask"] * ramp
            mask += m
            # Freshly lit glyphs flare, then settle.
            f = max(0.0, 1 - dt / FLARE)
            if f > 0:
                flare += m * f
            if p < 1:
                sparks.append((front, (y0 + y1) / 2, 1 - p * 0.4))
            for ex, ey, delay, rise, drift in u["embers"]:
                age = dt - delay
                life = 0.9
                if 0 < age < life and ex < front:
                    a = 1 - age / life
                    embers.append((ex + drift * age, ey - rise * age, a * 0.8))
            if out > 0:
                # Dissolving: extra sparks lift off the glyphs.
                for ex, ey, delay, rise, drift in u["embers"]:
                    embers.append((ex + drift * out, ey - rise * 2.2 * out, (1 - out) * 0.9))
        if mask.max() <= 0:
            continue
        mask = np.clip(mask, 0, 1) * live
        flare = np.clip(flare, 0, 1) * live
        band = frame[y0b:y0b + hb]
        # Soft dark underlay so the text reads over any background.
        shadow = cv2.GaussianBlur(mask, (0, 0), 7)[..., None]
        band *= 1 - 0.55 * np.clip(shadow * 1.6, 0, 1)
        shimmer = 0.92 + 0.08 * np.sin(t * 3.0 + XS / 90.0)[..., None]
        g_wide = cv2.GaussianBlur(mask + flare * 1.5, (0, 0), 14)[..., None]
        g_near = cv2.GaussianBlur(mask + flare, (0, 0), 3.5)[..., None]
        _screen(band, g_wide * np.array(st["glow"], np.float32) * shimmer, 1.5)
        _screen(band, g_near * np.array(st["glow"], np.float32), 1.1)
        _screen(band, mask[..., None] * np.array(st["core"], np.float32), 1.0)
        _screen(band, flare[..., None] * np.array((1.0, 1.0, 1.0), np.float32), 0.8)
        # The spark that writes each word, plus drifting embers.
        dots = np.zeros((hb + 80, W), np.float32)
        for x, y, a in sparks:
            cv2.circle(dots, (int(x), int(y) + 40), 5, a, -1, cv2.LINE_AA)
            cv2.line(dots, (int(x) - 26, int(y) + 40), (int(x) + 26, int(y) + 40), a * 0.7, 2, cv2.LINE_AA)
            cv2.line(dots, (int(x), int(y) + 14), (int(x), int(y) + 66), a * 0.5, 1, cv2.LINE_AA)
        for x, y, a in embers:
            if -38 < y < hb + 38:
                cv2.circle(dots, (int(x), int(y) + 40), 2, a * live if out == 0 else a, -1, cv2.LINE_AA)
        glow_d = cv2.GaussianBlur(dots, (0, 0), 4) * 2.2 + dots
        region = frame[y0b - 40:y0b + hb + 40]
        _screen(region, glow_d[..., None] * np.array(st["spark"], np.float32), 1.0)
    return frame


def text_bboxes():
    """Frame-space bounding boxes of every glyph unit (for the safe-area check)."""
    out = []
    for ln in lines():
        for u in ln["units"]:
            x0, y0, x1, y1 = u["bb"]
            out.append((ln["speaker"], (x0 - 14, y0 + ln["y0"] - 14, x1 + 14, y1 + ln["y0"] + 14)))
    return out

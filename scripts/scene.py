"""Motion-comic renderer: Trickster vs. Hero, 9:16, 1080x1920 @ 30 fps.

Everything is built from the project's own artwork:
  joker.png / batman.png (2x2 character sheets, cut out by scripts/cutout.py)
  雨夜霓虹賽博都市景觀.png (city background)
Effects (rain, fog, speed lines, light clash, halftone, glitch) are procedural.

`render_frame(t)` returns an RGB uint8 frame for time t (seconds).
"""
import json
import math
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
CUT = ROOT / "output/_build/cutouts"
FONT_DIR = ROOT / "output/_build/fonts"

W, H = 1080, 1920
FPS = 30
DURATION = 22.8

# Voice placement on the master timeline (seconds). Word timings were measured
# with forced alignment on the original files; see the report.
JOKER_VO_AT = 1.9
HERO_VO_AT = 10.0
SUBS = [
    # (start, end, english, chinese)
    (JOKER_VO_AT + 1.18, JOKER_VO_AT + 2.86, "Why so serious?", "幹嘛這麼嚴肅？"),
    (JOKER_VO_AT + 3.06, JOKER_VO_AT + 5.40, "Let's have some fun!", "讓我們來找點樂子吧！"),
    (HERO_VO_AT + 0.05, HERO_VO_AT + 2.05, "I see your weakness.", "我看見了你的弱點，"),
    (HERO_VO_AT + 2.38, HERO_VO_AT + 4.70, "And your potential.", "也看見了你的潛力。"),
]

# "balloon" = comic speech balloons (Trickster above, Hero below, echoing the final
# split screen) plus one sound-effect word on the impact; "subtitle" = plain subtitles.
LETTERING = "balloon"
# Per line in SUBS: (style, balloon center, balloon size, tail tip). Placed off faces,
# the helmet and the chest emblem.
BALLOONS = [
    ("trickster", (390, 270), (720, 320), (690, 560)),
    ("trickster", (385, 265), (730, 320), (700, 520)),
    ("hero", (540, 1610), (820, 250), (560, 1370)),
    ("hero", (520, 1620), (800, 250), (660, 1380)),
]
SFX_WORD = "KRAK!"
# Role name tags (Chinese only): (text, start, end, center, style).
ROLE_TAGS = [
    ("演講員", 1.00, 2.90, (250, 1600), "trickster"),
    ("個別講評", 7.85, 9.85, (300, 1600), "hero"),
]
# Meeting info card on the final standoff. Full street address goes in the post caption.
INFO_AT = 17.85
CLUB_NAME = ("Chill Hi High", "中英雙語國際演講會")
INFO_LINES = [
    ("日期", "10/27（二）19:15–21:15"),
    ("地點", "社會創新實驗中心 107 會議室"),
    ("交通", "忠孝復興站 2 號出口 步行 7 分鐘"),
]
INFO_CALL = "歡迎大家一起變裝出場！"
INFO_PRIZE = ("現場還有", "神秘小禮", "抽獎等你帶走！")
# In balloon mode the dialogue close-ups sit a little lower to leave headroom.
JOKER_DROP = 190 if LETTERING == "balloon" else 0

# Shot list: (start, end, name). Cuts land on voice boundaries.
SHOTS = [
    (0.00, 0.90, "s01_city"),
    (0.90, 2.00, "s02_trickster_enter"),
    (2.00, 3.05, "s03_trickster_laugh"),
    (3.05, 4.90, "s04_why_so_serious"),
    (4.90, 7.60, "s05_have_some_fun"),
    (7.60, 8.80, "s06_hero_rise"),
    (8.80, 10.00, "s07_hero_gaze"),
    (10.00, 12.25, "s08_weakness"),
    (12.25, 15.00, "s09_potential"),
    (15.00, 15.85, "s10_smile_freeze"),
    (15.85, 16.75, "s11_smile_returns"),
    (16.75, 17.85, "s12_standoff"),
    (17.85, DURATION, "s13_info"),
]

PURPLE = np.array([0.62, 0.18, 0.95], np.float32)
GREEN = np.array([0.45, 1.00, 0.35], np.float32)
BLUE = np.array([0.30, 0.62, 1.00], np.float32)
WHITE = np.array([1.0, 1.0, 1.0], np.float32)


# ----------------------------------------------------------------------------- helpers
def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def ease_out(x, p=3):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** p


def lerp(a, b, x):
    return a + (b - a) * x


def smoothstep(e0, e1, x):
    x = np.clip((x - e0) / (e1 - e0), 0, 1)
    return x * x * (3 - 2 * x)


def hash_noise(seed, t):
    """Deterministic smooth 1-D noise in [-1, 1]."""
    i = math.floor(t)
    f = t - i

    def r(k):
        return math.sin((k + seed * 101.3) * 12.9898) * 43758.5453 % 1 * 2 - 1

    return lerp(r(i), r(i + 1), f * f * (3 - 2 * f))


def shake(t, t0, amp, dur=0.35, seed=1):
    """Decaying camera shake starting at t0."""
    if t < t0 or t > t0 + dur:
        return 0.0, 0.0
    k = 1 - (t - t0) / dur
    return amp * k * k * hash_noise(seed, t * 38), amp * k * k * hash_noise(seed + 7, t * 41)


def affine(src_size, anchor, dst, scale, rot_deg):
    """Matrix mapping src pixel `anchor` (relative 0..1) to canvas point `dst`."""
    sw, sh = src_size
    ax, ay = anchor[0] * sw, anchor[1] * sh
    a = math.radians(rot_deg)
    c, s = math.cos(a) * scale, math.sin(a) * scale
    return np.array([[c, -s, dst[0] - (c * ax - s * ay)], [s, c, dst[1] - (s * ax + c * ay)]], np.float32)


def warp(img, M, interp=cv2.INTER_LINEAR):
    return cv2.warpAffine(img, M, (W, H), flags=interp, borderMode=cv2.BORDER_CONSTANT, borderValue=0)


def over(canvas, layer_premul, alpha=1.0):
    """Composite a premultiplied RGBA float layer onto an RGB canvas."""
    a = layer_premul[..., 3:4] * alpha
    canvas *= 1 - a
    canvas += layer_premul[..., :3] * alpha
    return canvas


def screen(canvas, rgb, amount=1.0):
    canvas[:] = 1 - (1 - canvas) * (1 - np.clip(rgb * amount, 0, 1))
    return canvas


# ----------------------------------------------------------------------------- assets
class Assets:
    def __init__(self):
        bg = np.asarray(Image.open(ROOT / "雨夜霓虹賽博都市景觀.png").convert("RGB")).astype(np.float32) / 255
        self.bg = bg
        self.bg_soft = cv2.GaussianBlur(bg, (0, 0), 2.2)
        meta = json.loads((CUT / "meta.json").read_text())
        self.chars = {}
        for key, sides in meta.items():
            rgba = np.asarray(Image.open(CUT / f"{key}.png")).astype(np.float32) / 255
            # Gentle upscale-friendly sharpen of the line art before any warp.
            rgb = rgba[..., :3]
            rgb = np.clip(rgb + 0.35 * (rgb - cv2.GaussianBlur(rgb, (0, 0), 1.2)), 0, 1)
            a = rgba[..., 3].copy()
            h, w = a.shape
            # Fade the sides where the panel crops the figure so no hard edge shows.
            yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
            fade = np.ones_like(a)
            if sides["bottom"]:
                fade *= smoothstep(h * 0.0, h * 0.22, h - yy)
            if sides["left"]:
                fade *= smoothstep(0, w * 0.10, xx)
            if sides["right"]:
                fade *= smoothstep(0, w * 0.10, w - xx)
            if sides["top"]:
                fade *= smoothstep(0, h * 0.04, yy)
            a *= fade
            self.chars[key] = {"rgb": rgb, "a": a, "size": (w, h)}
        self._rim_cache = {}
        self._make_textures()
        self._make_fonts()

    def char_layer(self, key, rim=None, grade=None):
        """Premultiplied RGBA of a character with optional colored rim light.

        rim: list of (color, (dx, dy), strength) – light coming from direction (dx, dy).
        grade: (mult_rgb, add_rgb) color grade applied to the figure only.
        """
        ck = (key, repr(rim), repr(grade))
        if ck in self._rim_cache:
            return self._rim_cache[ck]
        c = self.chars[key]
        rgb, a = c["rgb"].copy(), c["a"]
        if grade is not None:
            mult, add = grade
            rgb = np.clip(rgb * np.array(mult, np.float32) + np.array(add, np.float32), 0, 1)
        if rim:
            ab = cv2.GaussianBlur(a, (0, 0), 2.0)
            for color, (dx, dy), strength in rim:
                M = np.float32([[1, 0, -dx], [0, 1, -dy]])
                shifted = cv2.warpAffine(ab, M, (a.shape[1], a.shape[0]), borderValue=0)
                edge = np.clip(a - shifted, 0, 1)
                edge = cv2.GaussianBlur(edge, (0, 0), 1.2) * strength
                rgb = 1 - (1 - rgb) * (1 - np.clip(edge[..., None] * np.array(color, np.float32), 0, 1))
        out = np.dstack([rgb * a[..., None], a]).astype(np.float32)
        self._rim_cache[ck] = out
        return out

    def _make_textures(self):
        rng = np.random.default_rng(7)
        # Fog: tileable soft noise, twice the frame width so it can scroll.
        n = rng.random((60, 68)).astype(np.float32)
        n = cv2.resize(n, (W * 2, H), interpolation=cv2.INTER_CUBIC)
        n = cv2.GaussianBlur(n, (0, 0), 60)
        self.fog = (n - n.min()) / (n.max() - n.min())
        # Rain streaks (two depths).
        self.rain = []
        for depth, count in ((0.5, 260), (1.0, 120)):
            self.rain.append((depth, rng.random((count, 3)).astype(np.float32)))
        # Halftone dot screen used in the comic vignette.
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        cell = 14
        gx, gy = (xx % cell) - cell / 2, (yy % cell) - cell / 2
        d = np.sqrt(gx * gx + gy * gy)
        vign = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.58)) ** 2)
        radius = np.clip((vign - 0.55) * 14, 0, cell * 0.55)
        self.halftone = np.clip(radius - d + 0.5, 0, 1).astype(np.float32)
        self.vignette = np.clip(1 - 0.55 * np.clip(vign - 0.35, 0, 1) ** 1.6, 0, 1)[..., None].astype(np.float32)
        # Film grain frames.
        self.grain = [rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32) for _ in range(8)]
        self.speed_angles = rng.random((90, 3)).astype(np.float32)

    def _make_fonts(self):
        en = ImageFont.truetype(str(FONT_DIR / "Bangers-Regular.ttf"), 78)
        zh = ImageFont.truetype(str(FONT_DIR / "NotoSansTC.ttf"), 64)
        try:
            zh.set_variation_by_axes([900])
        except Exception:
            pass
        self.subs = []
        for s, e, en_t, zh_t in SUBS:
            img = Image.new("RGBA", (W, 230), (0, 0, 0, 0))
            d = ImageDraw.Draw(img)
            for text, font, y, fill, stroke in (
                (en_t, en, 18, (255, 255, 255, 255), 7),
                (zh_t, zh, 118, (255, 236, 120, 255), 7),
            ):
                bw = d.textlength(text, font=font)
                d.text(((W - bw) / 2 + 4, y + 5), text, font=font, fill=(0, 0, 0, 170),
                       stroke_width=stroke, stroke_fill=(0, 0, 0, 170))
                d.text(((W - bw) / 2, y), text, font=font, fill=fill, stroke_width=stroke, stroke_fill=(10, 8, 16, 255))
            arr = np.asarray(img).astype(np.float32) / 255
            arr[..., :3] *= arr[..., 3:4]
            self.subs.append((s, e, arr))
        self.balloons = [(s, e, style, make_balloon(style, c, size, tip, en_t, zh_t))
                         for (s, e, en_t, zh_t), (style, c, size, tip) in zip(SUBS, BALLOONS)]
        self.sfx_word = make_sfx_word(SFX_WORD)
        self.tags = [(s, e, make_tag(text, c, style), c) for text, s, e, c, style in ROLE_TAGS]
        self.info = make_info_card()


A = None


def assets():
    global A
    if A is None:
        A = Assets()
    return A


# ----------------------------------------------------------------------------- layers
def background(canvas, view_cx, view_cy, view_h, rot=0.0, sh=(0, 0), soft=False, mult=1.0):
    src = A.bg_soft if soft else A.bg
    M = affine((src.shape[1], src.shape[0]), (view_cx / src.shape[1], view_cy / src.shape[0]),
               (W / 2 + sh[0], H / 2 + sh[1]), H / view_h, rot)
    canvas[:] = warp(src, M) * mult
    return canvas


def put_char(canvas, layer, center, height, rot=0.0, anchor=(0.5, 0.5), alpha=1.0, interp=cv2.INTER_CUBIC):
    h, w = layer.shape[:2]
    M = affine((w, h), anchor, center, height / h, rot)
    lay = warp(layer, M, interp)
    lay = np.clip(lay, 0, 1)
    return over(canvas, lay, alpha)


def cape_wave(layer, t, amp, region):
    """Slight horizontal sway of the cape. `region(xx, yy)` gives 0..1 weight (0 = head/chest)."""
    h, w = layer.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    wgt = region(xx / w, yy / h)
    dx = amp * wgt * np.sin(2 * np.pi * (0.55 * t + yy / h * 1.3))
    dy = 0.35 * amp * wgt * np.sin(2 * np.pi * (0.4 * t + xx / w * 0.9))
    return cv2.remap(layer, xx + dx, yy + dy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)


def rain(canvas, t, color, strength=0.55, angle=0.18, speed=1.0):
    lay = np.zeros((H // 2, W // 2), np.float32)
    for depth, pts in A.rain:
        length = 40 * depth
        vy = 1500 * depth * speed
        for x, y, ph in pts:
            yy = (y * (H // 2) + t * vy * 0.5 + ph * 1000) % (H // 2 + 80) - 40
            xx = (x * (W // 2 + 200) - 100 + angle * yy)
            cv2.line(lay, (int(xx), int(yy)), (int(xx + angle * length), int(yy + length)),
                     0.35 + 0.5 * depth, 1, cv2.LINE_AA)
    lay = cv2.resize(lay, (W, H), interpolation=cv2.INTER_LINEAR)
    return screen(canvas, lay[..., None] * np.array(color, np.float32), strength)


def fog(canvas, t, color, strength=0.35, low=0.45, speed=40):
    off = int(t * speed) % W
    f = A.fog[:, off:off + W]
    yy = np.linspace(0, 1, H, dtype=np.float32)[:, None]
    mask = (f * smoothstep(low, 1.0, yy))[..., None]
    return screen(canvas, mask * np.array(color, np.float32), strength)


def speed_lines(canvas, t, focus, color=(1, 1, 1), strength=0.85, r_in=380, seed=0):
    lay = np.zeros((H, W), np.uint8)
    rnd = A.speed_angles
    flick = int(t * 24)
    for i, (a, wdt, ph) in enumerate(rnd):
        if (i + flick + seed) % 3 == 0:
            continue
        ang = (a + seed * 0.13) * 2 * np.pi
        r0 = r_in * (0.85 + 0.5 * ((ph + flick * 0.37) % 1))
        r1 = 2400
        half = 0.004 + 0.012 * wdt
        p = [
            (focus[0] + r0 * math.cos(ang), focus[1] + r0 * math.sin(ang)),
            (focus[0] + r1 * math.cos(ang - half), focus[1] + r1 * math.sin(ang - half)),
            (focus[0] + r1 * math.cos(ang + half), focus[1] + r1 * math.sin(ang + half)),
        ]
        cv2.fillPoly(lay, [np.int32(p)], 255, cv2.LINE_AA)
    m = lay.astype(np.float32)[..., None] / 255 * strength
    canvas *= 1 - m
    canvas += m * np.array(color, np.float32)
    return canvas


def glow(canvas, center, radius, color, amount):
    yy, xx = np.ogrid[0:H, 0:W]
    d2 = ((xx - center[0]) ** 2 + (yy - center[1]) ** 2) / float(radius * radius)
    g = np.exp(-d2)[..., None].astype(np.float32)
    return screen(canvas, g * np.array(color, np.float32), amount)


def eye_glint(canvas, pts, amount, color=(0.8, 0.95, 1.0)):
    for p in pts:
        glow(canvas, p, 26, color, amount)
        # tiny horizontal flare
        lay = np.zeros((H, W), np.float32)
        cv2.ellipse(lay, (int(p[0]), int(p[1])), (int(120 * amount), 3), 0, 0, 360, 1.0, -1, cv2.LINE_AA)
        lay = cv2.GaussianBlur(lay, (0, 0), 3)
        screen(canvas, lay[..., None] * np.array(color, np.float32), amount)
    return canvas


def neon_flicker(t, seed=3):
    """Mostly steady with occasional quick dips, like a failing sign."""
    v = hash_noise(seed, t * 9)
    return 0.82 if v > 0.78 else 1.0


def glitch(img, t, amount, seed=0):
    if amount <= 0:
        return img
    out = img.copy()
    shift = int(14 * amount)
    out[..., 0] = np.roll(img[..., 0], shift, axis=1)
    out[..., 2] = np.roll(img[..., 2], -shift, axis=1)
    rng = np.random.default_rng(int(t * FPS) + seed)
    for _ in range(int(6 * amount) + 1):
        y0 = rng.integers(0, H - 80)
        hgt = rng.integers(8, 70)
        out[y0:y0 + hgt] = np.roll(out[y0:y0 + hgt], int(rng.integers(-60, 60) * amount), axis=1)
    return out


def starburst(canvas, center, radius, colors, alpha, rot=0.0):
    """Comic impact burst (shape only, no lettering)."""
    if alpha <= 0:
        return canvas
    for k, (col, rs) in enumerate(zip(colors, (1.0, 0.78, 0.5))):
        pts = []
        n = 18
        for i in range(n * 2):
            ang = rot + i * math.pi / n
            r = radius * rs * (1.0 if i % 2 == 0 else 0.55 + 0.12 * math.sin(i * 7.1))
            pts.append((center[0] + r * math.cos(ang), center[1] + r * math.sin(ang) * 0.82))
        lay = np.zeros((H, W), np.uint8)
        cv2.fillPoly(lay, [np.int32(pts)], 255, cv2.LINE_AA)
        if k == 0:
            edge = np.zeros_like(lay)
            cv2.polylines(edge, [np.int32(pts)], True, 255, 10, cv2.LINE_AA)
            m = edge.astype(np.float32)[..., None] / 255 * alpha
            canvas *= 1 - m
        m = lay.astype(np.float32)[..., None] / 255 * alpha * (0.9 if k == 0 else 1.0)
        canvas *= 1 - m
        canvas += m * np.array(col, np.float32)
    return canvas


def finish(canvas, t, sat=1.0, contrast=1.06, halftone_col=(0.05, 0.02, 0.10), grain=0.025, flash=0.0):
    if sat != 1.0:
        lum = canvas.mean(axis=2, keepdims=True)
        canvas[:] = lum + (canvas - lum) * sat
    canvas[:] = np.clip((canvas - 0.5) * contrast + 0.5, 0, 1)
    canvas *= A.vignette
    ht = A.halftone[..., None] * 0.55
    canvas *= 1 - ht
    canvas += ht * np.array(halftone_col, np.float32)
    g = cv2.resize(A.grain[int(t * FPS) % len(A.grain)], (W, H), interpolation=cv2.INTER_NEAREST)
    canvas += g[..., None] * grain
    if flash > 0:
        canvas[:] = canvas * (1 - flash) + flash
    return np.clip(canvas, 0, 1)


def _font(name, size, weight=None):
    f = ImageFont.truetype(str(FONT_DIR / name), size)
    if weight:
        f.set_variation_by_axes([weight])
    return f


def make_balloon(style, center, size, tip, en_t, zh_t, ss=2):
    """Full-frame premultiplied RGBA of one speech balloon (drawn at 2x, then reduced)."""
    cw, ch = W * ss, H * ss
    cx, cy = center[0] * ss, center[1] * ss
    bw, bh = size[0] * ss / 2, size[1] * ss / 2
    tx, ty = tip[0] * ss, tip[1] * ss
    body = np.zeros((ch, cw), np.uint8)
    if style == "trickster":
        # Wobbly superellipse: playful, slightly unstable.
        pts = []
        for i in range(120):
            a = i / 120 * 2 * np.pi
            ca, sa = np.cos(a), np.sin(a)
            r = 1 + 0.035 * np.sin(5 * a + 0.7) + 0.02 * np.sin(11 * a)
            pts.append((cx + bw * r * np.sign(ca) * abs(ca) ** 0.6, cy + bh * r * np.sign(sa) * abs(sa) ** 0.6))
        cv2.fillPoly(body, [np.int32(pts)], 255, cv2.LINE_AA)
        # Curved tail.
        d = np.array([tx - cx, ty - cy], np.float32)
        d /= np.linalg.norm(d)
        nrm = np.array([-d[1], d[0]])
        base = np.array([cx, cy]) + d * np.array([bw, bh]) * 0.55
        tail = [base + nrm * 42 * ss, base + nrm * 10 * ss + d * 30 * ss, (tx, ty), base - nrm * 34 * ss]
        cv2.fillPoly(body, [np.int32(tail)], 255, cv2.LINE_AA)
        fill, ink, shadow = (1.0, 1.0, 1.0), (0.08, 0.03, 0.12), PURPLE
        shadow_off, stroke = (14 * ss, 12 * ss), 6 * ss
        en_col, zh_col = (25, 10, 35), (110, 20, 150)
        inner_glow = GREEN
    else:
        # Hard-edged chamfered box: calm, armored.
        k = 22 * ss
        x0, y0, x1, y1 = cx - bw, cy - bh, cx + bw, cy + bh
        box = [(x0 + k, y0), (x1 - k, y0), (x1, y0 + k), (x1, y1 - k), (x1 - k, y1), (x0 + k, y1), (x0, y1 - k), (x0, y0 + k)]
        cv2.fillPoly(body, [np.int32(box)], 255, cv2.LINE_AA)
        bx = min(max(tx, x0 + 80 * ss), x1 - 80 * ss)
        tail = [(bx - 34 * ss, y0 + 4), (tx, ty), (bx + 6 * ss, y0 + 4)]
        cv2.fillPoly(body, [np.int32(tail)], 255, cv2.LINE_AA)
        fill, ink, shadow = (0.03, 0.06, 0.13), (0.55, 0.78, 1.0), (0.0, 0.0, 0.0)
        shadow_off, stroke = (10 * ss, 10 * ss), 4 * ss
        en_col, zh_col = (255, 255, 255), (170, 210, 255)
        inner_glow = None
    m = body.astype(np.float32) / 255
    outline = cv2.dilate(body, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * stroke + 1,) * 2)).astype(np.float32) / 255
    if style == "hero":
        # Thin cold-blue rule inside a black border.
        outer = cv2.dilate(body, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * stroke + 9,) * 2)).astype(np.float32) / 255
    else:
        outer = outline
    sh = np.roll(np.roll(outer, shadow_off[1], 0), shadow_off[0], 1)
    rgb = np.zeros((ch, cw, 3), np.float32)
    a = np.zeros((ch, cw), np.float32)
    shadow_a = 0.85 if style == "trickster" else 0.55
    rgb += sh[..., None] * np.array(shadow, np.float32) * shadow_a
    a = np.maximum(a, sh * shadow_a)
    if style == "hero":
        rgb = rgb * (1 - outer[..., None]) + outer[..., None] * np.array((0.0, 0.0, 0.0), np.float32)
        a = np.maximum(a, outer)
    rgb = rgb * (1 - outline[..., None]) + outline[..., None] * np.array(ink, np.float32)
    a = np.maximum(a, outline)
    rgb = rgb * (1 - m[..., None]) + m[..., None] * np.array(fill, np.float32)
    if inner_glow is not None:
        # Faint green tint along the inside edge.
        edge = np.clip(m - cv2.erode(body, np.ones((18 * ss, 18 * ss), np.uint8)).astype(np.float32) / 255, 0, 1)
        edge = cv2.GaussianBlur(edge, (0, 0), 6 * ss) * m
        rgb = rgb * (1 - 0.35 * edge[..., None]) + 0.35 * edge[..., None] * np.array(inner_glow, np.float32)
    a = np.maximum(a, m) if style == "trickster" else np.maximum(a, m * 0.93)
    img = Image.fromarray((np.dstack([rgb, a]) * 255).astype(np.uint8), "RGBA")
    d = ImageDraw.Draw(img)
    en = _font("Bangers-Regular.ttf", 72 * ss)
    zh = _font("NotoSansTC.ttf", 52 * ss, 900)
    tilt = -0.0
    gap = 14 * ss
    eh = en.getbbox(en_t)[3] - en.getbbox(en_t)[1]
    zhh = zh.getbbox(zh_t)[3] - zh.getbbox(zh_t)[1]
    top = cy - (eh + gap + zhh) / 2 - (6 * ss if style == "trickster" else 2 * ss)
    for text, font, y, col in ((en_t, en, top - en.getbbox(en_t)[1], en_col),
                               (zh_t, zh, top + eh + gap - zh.getbbox(zh_t)[1], zh_col)):
        w_ = d.textlength(text, font=font)
        d.text((cx - w_ / 2, y), text, font=font, fill=col + (255,))
    img = img.resize((W, H), Image.LANCZOS)
    arr = np.asarray(img).astype(np.float32) / 255
    arr[..., :3] *= arr[..., 3:4]
    return {"rgba": arr, "center": center, "style": style, "tilt": tilt}


def make_sfx_word(word):
    """Comic sound-effect lettering, full frame, centered."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = _font("Bangers-Regular.ttf", 250)
    w_ = d.textlength(word, font=f)
    x, y = W / 2 - w_ / 2, H / 2 - 160
    d.text((x + 16, y + 16), word, font=f, fill=(110, 30, 170, 255), stroke_width=16, stroke_fill=(110, 30, 170, 255))
    d.text((x, y), word, font=f, fill=(255, 222, 60, 255), stroke_width=16, stroke_fill=(12, 8, 20, 255))
    img = img.rotate(-9, resample=Image.BICUBIC, center=(W / 2, H / 2))
    arr = np.asarray(img).astype(np.float32) / 255
    arr[..., :3] *= arr[..., 3:4]
    return arr


def _premul(img):
    arr = np.asarray(img).astype(np.float32) / 255
    arr[..., :3] *= arr[..., 3:4]
    return arr


def _shadowed_box(d, box, fill, shadow, offset, border=8, radius=0):
    x0, y0, x1, y1 = box
    d.rounded_rectangle((x0 + offset, y0 + offset, x1 + offset, y1 + offset), radius, fill=shadow)
    d.rounded_rectangle(box, radius, fill=fill, outline=(12, 8, 20, 255), width=border)


def make_tag(text, center, style):
    """Comic name tag: yellow slab, heavy ink border, colored offset shadow, tilted."""
    ss = 2
    f = _font("NotoSansTC.ttf", 84 * ss, 900)
    img = Image.new("RGBA", (W * ss, H * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    tw = d.textlength(text, font=f)
    bb = f.getbbox(text)
    padx, pady = 44 * ss, 26 * ss
    cx, cy = center[0] * ss, center[1] * ss
    box = (cx - tw / 2 - padx, cy - (bb[3] - bb[1]) / 2 - pady, cx + tw / 2 + padx, cy + (bb[3] - bb[1]) / 2 + pady)
    shadow = (120, 30, 180, 255) if style == "trickster" else (40, 110, 230, 255)
    _shadowed_box(d, box, (255, 216, 60, 255), shadow, 14 * ss, 7 * ss)
    d.text((cx - tw / 2, cy - (bb[3] - bb[1]) / 2 - bb[1]), text, font=f, fill=(18, 10, 24, 255))
    rot = -4 if style == "trickster" else 3
    img = img.rotate(rot, resample=Image.BICUBIC, center=(cx, cy)).resize((W, H), Image.LANCZOS)
    return _premul(img)


INFO_BOX = (50, 700, 1030, 1236)  # card body on the 1080x1920 frame


def make_info_card():
    """Layers of the meeting-info card, each a full-frame premultiplied RGBA, animated separately."""
    ss = 2
    x0, y0, x1, y1 = [v * ss for v in INFO_BOX]
    layers = {}

    def canvas():
        im = Image.new("RGBA", (W * ss, H * ss), (0, 0, 0, 0))
        return im, ImageDraw.Draw(im)

    def done(im):
        return _premul(im.resize((W, H), Image.LANCZOS))

    # Body: cream paper, ink border, split shadow (purple for him above, blue for him below).
    im, d = canvas()
    d.rounded_rectangle((x0 - 16 * ss, y0 - 16 * ss, x1 - 16 * ss, y1 - 16 * ss), 18 * ss, fill=(130, 40, 190, 255))
    d.rounded_rectangle((x0 + 16 * ss, y0 + 16 * ss, x1 + 16 * ss, y1 + 16 * ss), 18 * ss, fill=(40, 110, 230, 255))
    d.rounded_rectangle((x0, y0, x1, y1), 18 * ss, fill=(255, 249, 232, 255), outline=(12, 8, 20, 255), width=8 * ss)
    # Halftone dots in the lower-right corner of the paper.
    for gy in range(int(y1 - 150 * ss), int(y1 - 12 * ss), 16 * ss):
        for gx in range(int(x1 - 260 * ss), int(x1 - 12 * ss), 16 * ss):
            r = max(0, ((gx - (x1 - 260 * ss)) / (248 * ss) + (gy - (y1 - 150 * ss)) / (138 * ss)) / 2) * 4.5 * ss
            if r > 0.6 * ss:
                d.ellipse((gx - r, gy - r, gx + r, gy + r), fill=(255, 216, 60, 255))
    layers["body"] = done(im)

    # Club-name ribbon across the top edge.
    im, d = canvas()
    en = _font("Bangers-Regular.ttf", 66 * ss)
    zh = _font("NotoSansTC.ttf", 46 * ss, 900)
    ew, zw = d.textlength(CLUB_NAME[0], font=en), d.textlength(CLUB_NAME[1], font=zh)
    gap = 18 * ss
    total = ew + gap + zw
    cx, cy = (x0 + x1) / 2, y0 - 6 * ss
    rb = (cx - total / 2 - 34 * ss, cy - 50 * ss, cx + total / 2 + 34 * ss, cy + 50 * ss)
    d.rectangle((rb[0] + 10 * ss, rb[1] + 10 * ss, rb[2] + 10 * ss, rb[3] + 10 * ss), fill=(12, 8, 20, 255))
    d.rectangle(rb, fill=(255, 216, 60, 255), outline=(12, 8, 20, 255), width=6 * ss)
    tx = cx - total / 2
    d.text((tx, cy - en.getbbox("C")[3] / 2 - 4 * ss), CLUB_NAME[0], font=en, fill=(110, 25, 160, 255))
    zb = zh.getbbox(CLUB_NAME[1])
    d.text((tx + ew + gap, cy - (zb[3] + zb[1]) / 2), CLUB_NAME[1], font=zh, fill=(18, 10, 24, 255))
    im = im.rotate(2.5, resample=Image.BICUBIC, center=(cx, cy))
    layers["ribbon"] = done(im)
    layers["ribbon_c"] = (cx / ss, cy / ss)

    # Info rows: dark chip label + text.
    chip_f = _font("NotoSansTC.ttf", 36 * ss, 900)
    row_f = _font("NotoSansTC.ttf", 46 * ss, 800)
    chip_cols = [(110, 25, 160, 255), (30, 90, 200, 255), (40, 140, 90, 255)]
    rows = []
    for i, ((label, text), col) in enumerate(zip(INFO_LINES, chip_cols)):
        im, d = canvas()
        ry = y0 + (92 + i * 86) * ss
        lx = x0 + 44 * ss
        lw = d.textlength(label, font=chip_f)
        d.rounded_rectangle((lx, ry - 30 * ss, lx + lw + 30 * ss, ry + 30 * ss), 10 * ss, fill=col)
        cb = chip_f.getbbox(label)
        d.text((lx + 15 * ss, ry - (cb[3] + cb[1]) / 2), label, font=chip_f, fill=(255, 255, 255, 255))
        rb_ = row_f.getbbox(text)
        d.text((lx + lw + 54 * ss, ry - (rb_[3] + rb_[1]) / 2), text, font=row_f, fill=(22, 14, 30, 255))
        rows.append((done(im), (x0 / ss + 300, ry / ss)))
    layers["rows"] = rows

    # Divider + call to action.
    im, d = canvas()
    dy = y0 + 342 * ss
    for k in range(0, int(x1 - x0 - 88 * ss), 22 * ss):
        d.line((x0 + 44 * ss + k, dy, x0 + 44 * ss + k + 12 * ss, dy), fill=(12, 8, 20, 120), width=3 * ss)
    call_f = _font("NotoSansTC.ttf", 46 * ss, 900)
    cw = d.textlength(INFO_CALL, font=call_f)
    cb = call_f.getbbox(INFO_CALL)
    d.text(((x0 + x1) / 2 - cw / 2, dy + 56 * ss - (cb[3] + cb[1]) / 2), INFO_CALL, font=call_f, fill=(110, 25, 160, 255))
    layers["call"] = (done(im), ((x0 + x1) / 2 / ss, (dy + 56 * ss) / ss))

    # Prize line: plain lead/tail text, plus four big bouncing characters.
    pre, prize, post = INFO_PRIZE
    small = _font("NotoSansTC.ttf", 44 * ss, 900)
    big = _font("NotoSansTC.ttf", 66 * ss, 900)
    char_w = 76 * ss
    pw, qw = d.textlength(pre, font=small), d.textlength(post, font=small)
    total = pw + 16 * ss + char_w * len(prize) + 16 * ss + qw
    py = dy + 136 * ss
    px = (x0 + x1) / 2 - total / 2
    im, d = canvas()
    sb = small.getbbox(pre)
    d.text((px, py - (sb[3] + sb[1]) / 2), pre, font=small, fill=(22, 14, 30, 255))
    d.text((px + pw + 32 * ss + char_w * len(prize), py - (sb[3] + sb[1]) / 2), post, font=small, fill=(22, 14, 30, 255))
    layers["prize_line"] = (done(im), ((x0 + x1) / 2 / ss, py / ss))
    chars = []
    for i, ch in enumerate(prize):
        im, d = canvas()
        ccx = px + pw + 16 * ss + char_w * (i + 0.5)
        bw = d.textlength(ch, font=big)
        bb = big.getbbox(ch)
        d.text((ccx - bw / 2, py - (bb[3] + bb[1]) / 2), ch, font=big, fill=(255, 216, 60, 255),
               stroke_width=7 * ss, stroke_fill=(12, 8, 20, 255))
        chars.append((done(im), (ccx / ss, py / ss)))
    layers["prize_chars"] = chars
    return layers


def overlays(canvas, t):
    """Role name tags and the info card, drawn above the grade like the balloons."""
    for s, e, arr, c in A.tags:
        if s <= t <= e:
            k = (t - s) / 0.12
            scale = lerp(1.5, 1.0, ease_out(k, 3)) if k < 1 else 1.0
            pop(arr, c, scale, min(1.0, k * 1.5) * min(1.0, (e - t) / 0.15), canvas)
    if t < INFO_AT + 0.1:
        return canvas
    L = A.info
    bc = ((INFO_BOX[0] + INFO_BOX[2]) / 2, (INFO_BOX[1] + INFO_BOX[3]) / 2)

    def springy(t0, dur=0.22, start=0.3, over=1.08):
        k = (t - t0) / dur
        if k <= 0:
            return None
        if k < 1:
            return lerp(start, over, ease_out(k, 3))
        return lerp(over, 1.0, ease(min(1.0, (k - 1) * 1.5)))

    sc = springy(INFO_AT + 0.15, 0.25, 0.2, 1.05)
    if sc:
        pop(L["body"], bc, sc, min(1.0, (t - INFO_AT - 0.15) / 0.1), canvas, rot=lerp(-6, 0, min(1, sc)))
    sc = springy(INFO_AT + 0.35)
    if sc:
        pop(L["ribbon"], L["ribbon_c"], sc, 1.0, canvas)
    for i, (arr, c) in enumerate(L["rows"]):
        k = (t - INFO_AT - 0.5 - i * 0.18) / 0.2
        if k > 0:
            M = np.float32([[1, 0, lerp(-60, 0, ease_out(min(k, 1)))], [0, 1, 0]])
            over(canvas, np.clip(cv2.warpAffine(arr, M, (W, H)), 0, 1), min(1.0, k))
    k = (t - INFO_AT - 1.1) / 0.2
    if k > 0:
        arr, c = L["call"]
        pop(arr, c, lerp(0.85, 1.0, ease_out(min(k, 1))), min(1.0, k), canvas)
    k = (t - INFO_AT - 1.35) / 0.2
    if k > 0:
        arr, c = L["prize_line"]
        over(canvas, arr, min(1.0, k))
    for i, (arr, c) in enumerate(L["prize_chars"]):
        t0 = INFO_AT + 1.5 + i * 0.14
        sc = springy(t0, 0.16, 0.2, 1.3)
        if sc:
            # Keeps a gentle bounce after landing so the prize line stays lively.
            bob = 0.04 * math.sin((t - t0) * 6 + i * 1.3) if t > t0 + 0.4 else 0.0
            pop(arr, (c[0], c[1]), sc + bob, 1.0, canvas, rot=6 * math.sin((t - t0) * 3 + i))
    return canvas


def pop(arr, center, scale, alpha, canvas, rot=0.0):
    if alpha <= 0:
        return canvas
    M = affine((W, H), (center[0] / W, center[1] / H), center, scale, rot)
    return over(canvas, np.clip(warp(arr, M), 0, 1), alpha)


def lettering(canvas, t):
    if LETTERING != "balloon":
        return subtitles(canvas, t)
    for s, e, style, b in A.balloons:
        if s - 0.001 <= t <= e:
            k = (t - s) / 0.16
            if style == "trickster":
                # Springy pop with a little wobble.
                scale = 1.0 + (0.18 * math.sin(min(k, 1) * math.pi * 1.5) * (1 - min(k, 1)) if k < 1 else 0) - 0.25 * max(0, 1 - k * 2)
                rot = 2.0 * math.sin(t * 5.0)
            else:
                # Firm, quick settle.
                scale = 1.0 - 0.06 * max(0.0, 1 - k)
                rot = 0.0
            out = min(1.0, (e - t) / 0.1)
            pop(b["rgba"], b["center"], scale, min(1.0, k * 2) * out, canvas, rot)
    return canvas


def subtitles(canvas, t, y=1500):
    for s, e, arr in A.subs:
        if s - 0.001 <= t <= e:
            fade = min(1.0, (t - s) / 0.1, (e - t) / 0.1)
            region = canvas[y:y + arr.shape[0]]
            a = arr[..., 3:4] * fade
            region *= 1 - a
            region += arr[..., :3] * fade
    return canvas


# ----------------------------------------------------------------------------- shots
JOKER_RIM = [(PURPLE, (-6, -3), 1.2), (GREEN, (6, -2), 1.0)]
JOKER_GRADE = ((0.98, 0.95, 1.02), (0.02, 0.0, 0.03))
HERO_RIM = [(BLUE, (-7, -2), 1.6), (BLUE * 0.8 + 0.2, (7, -3), 1.3), ((0.6, 0.8, 1.0), (0, -7), 0.8)]
HERO_GRADE = ((1.12, 1.15, 1.25), (0.02, 0.03, 0.06))


def joker_bg(c, t, u, cx=420, cy=430, vh=880, rot=0.0, sh=(0, 0), soft=True):
    background(c, cx, cy, vh, rot, sh, soft, mult=0.85 * neon_flicker(t))
    glow(c, (W * 0.1, H * 0.35), 520, PURPLE, 0.35)
    glow(c, (W * 0.9, H * 0.55), 480, GREEN, 0.18)
    rain(c, t, (0.75, 0.6, 1.0), 0.40)
    fog(c, t, PURPLE * 0.7 + GREEN * 0.3, 0.30)


def hero_bg(c, t, cx=1260, cy=420, vh=860, rot=0.0, sh=(0, 0), soft=True):
    background(c, cx, cy, vh, rot, sh, soft, mult=0.78)
    c *= np.array([0.80, 0.92, 1.12], np.float32)
    rain(c, t, (0.6, 0.8, 1.0), 0.45, angle=0.10)
    fog(c, t, BLUE * 0.6, 0.35, low=0.5, speed=-30)


def batman_cape(xr, yr, center=0.5, inner=0.16):
    """Weight 0 around the head/chest/emblem, rising toward outer and lower cape."""
    side = smoothstep(inner, inner + 0.22, np.abs(xr - center))
    low = smoothstep(0.25, 0.9, yr)
    return side * (0.4 + 0.6 * low)


def shot_frame(t):
    a = assets()
    c = np.zeros((H, W, 3), np.float32)
    for s, e, name in SHOTS:
        if s <= t < e or (name == SHOTS[-1][2] and t >= s):
            u = (t - s) / (e - s)
            return SHOT_FUNCS[name](c, t, t - s, u), name
    raise ValueError(t)


def s01_city(c, t, lt, u):
    # Establishing: city with purple/green neon, quick push toward the left towers.
    joker_bg(c, t, u, cx=lerp(560, 470, ease(u)), cy=470, vh=lerp(940, 820, ease(u)), soft=False)
    return finish(c, t, flash=max(0, 1 - lt / 0.12) * 0.6)


def s02_trickster_enter(c, t, lt, u):
    sh = shake(t, 0.90, 22, 0.4)
    joker_bg(c, t, u, cx=lerp(470, 430, u), cy=470, vh=lerp(820, 760, u), sh=sh)
    k = ease_out(lt / 0.32, 4)
    x = lerp(W * 1.45, W * 0.50, k) + sh[0] * 1.4
    tilt = lerp(9, -3.5, ease_out(lt / 0.75)) + 1.2 * math.sin(lt * 4)
    if lt < 0.45:
        speed_lines(c, t, (W * 0.55, H * 0.42), (1, 1, 1), 0.75 * (1 - lt / 0.45), r_in=420)
    put_char(c, A.char_layer("joker_1", JOKER_RIM, JOKER_GRADE), (x, H * 0.47 + sh[1]),
             lerp(1450, 1620, ease(u)), tilt, anchor=(0.45, 0.42))
    if lt < 0.2:
        c[:] = cv2.blur(c, (int(1 + 60 * (1 - lt / 0.2)), 1))
    return finish(c, t)


def s03_trickster_laugh(c, t, lt, u):
    sh = shake(t, 2.00, 10, 0.25, seed=3)
    joker_bg(c, t, u, cx=380, cy=420, vh=lerp(700, 640, u), rot=-3, sh=sh)
    glow(c, (W * 0.5, H * 0.32), 420, GREEN, 0.25 + 0.15 * neon_flicker(t, 5))
    put_char(c, A.char_layer("joker_3", JOKER_RIM, JOKER_GRADE), (W * 0.52 + sh[0] * 1.3, H * 0.44 + sh[1]),
             lerp(1700, 1840, ease_out(u)), lerp(-2, 2.5, ease(u)) + 1.5 * math.sin(lt * 9), anchor=(0.45, 0.45))
    out = finish(c, t)
    return glitch(out, t, 0.6 if lt < 0.07 else 0.0)


def s04_why_so_serious(c, t, lt, u):
    joker_bg(c, t, u, cx=lerp(300, 340, u), cy=400, vh=700, rot=2)
    glow(c, (W * 0.25, H * 0.25), 380, PURPLE, 0.35)
    # Mock-thoughtful glance: slow push with a small head tilt toward the camera.
    put_char(c, A.char_layer("joker_2", JOKER_RIM, JOKER_GRADE), (W * 0.47, H * 0.45 + JOKER_DROP),
             lerp(1640, 1800, ease(u)), lerp(2.5, -2.0, ease(u)), anchor=(0.5, 0.42))
    return finish(c, t)


def s05_have_some_fun(c, t, lt, u):
    # Slow drift, then a punch-in toward the reaching hand on "fun!".
    fun = JOKER_VO_AT + 4.5  # the stressed word "fun"
    punch = ease_out((t - fun) / 0.35, 4) if t > fun else 0.0
    sh = shake(t, fun, 14, 0.3, seed=9)
    joker_bg(c, t, u, cx=lerp(470, 430, u), cy=460, vh=lerp(800, 740, u) - 60 * punch, rot=-2, sh=sh)
    glow(c, (W * 0.3, H * 0.55), 520, GREEN, 0.22)
    height = lerp(1500, 1620, ease(u)) + 260 * punch
    put_char(c, A.char_layer("joker_4", JOKER_RIM, JOKER_GRADE),
             (W * 0.52 + sh[0], H * 0.46 + sh[1] + JOKER_DROP * 0.8), height, lerp(-1.5, 2.0, ease(u)), anchor=(0.45, 0.42))
    if punch > 0:
        speed_lines(c, t, (W * 0.30, H * 0.52), (0.85, 1.0, 0.8), 0.55 * (1 - punch * 0.7), r_in=360, seed=4)
    out = finish(c, t)
    stinger = JOKER_VO_AT + 5.25
    g = 1.0 - abs(t - stinger) / 0.12 if abs(t - stinger) < 0.12 else 0.0
    return glitch(out, t, g * 1.2, seed=5)


def s06_hero_rise(c, t, lt, u):
    # Low angle, camera tilts up from the chest emblem to the masked face.
    sh = shake(t, 7.60, 16, 0.5, seed=11)
    hero_bg(c, t, cx=1250, cy=lerp(520, 380, ease(u)), vh=lerp(760, 820, u), rot=-4, sh=sh)
    glow(c, (W * 0.72, H * 0.12), 360, (0.75, 0.85, 1.0), 0.35)  # moonlight
    lay = cape_wave(A.char_layer("batman_1", HERO_RIM, HERO_GRADE), t, 2.2, lambda x, y: batman_cape(x, y))
    put_char(c, lay, (W * 0.5 + sh[0], lerp(H * 0.10, H * 0.62, ease(u)) + sh[1]), 2300, -4,
             anchor=(0.5, 0.25))
    flash = max(0, 1 - lt / 0.10) * 0.5
    return finish(c, t, sat=0.9, halftone_col=(0.0, 0.02, 0.08), flash=flash)


def s07_hero_gaze(c, t, lt, u):
    hero_bg(c, t, cx=lerp(1240, 1290, u), cy=360, vh=740, rot=-2)
    glow(c, (W * 0.25, H * 0.14), 380, (0.75, 0.85, 1.0), 0.3)
    lay = cape_wave(A.char_layer("batman_2", HERO_RIM, HERO_GRADE), t, 2.4,
                    lambda x, y: batman_cape(x, y, center=0.55, inner=0.2))
    hgt = lerp(1750, 1880, ease(u))
    put_char(c, lay, (W * 0.44, H * 0.52), hgt, lerp(-1.5, 0, ease(u)), anchor=(0.5, 0.45))
    # The eye catches the light as his gaze locks on (toward screen right, where the Trickster was).
    eye = (W * 0.44 + (0.76 - 0.5) * hgt, H * 0.52 + (0.10 - 0.45) * hgt * 0.84)
    eye_glint(c, [eye], 0.9 * ease((lt - 0.5) / 0.3) * (1 - ease((lt - 0.95) / 0.25)))
    return finish(c, t, sat=0.9, halftone_col=(0.0, 0.02, 0.08))


def s08_weakness(c, t, lt, u):
    # Starts slightly from above (head lowered), settles to eye level as he looks up.
    hero_bg(c, t, cx=lerp(1300, 1280, u), cy=300, vh=640, soft=True)
    glow(c, (W * 0.85, H * 0.18), 420, BLUE, 0.3)
    up = ease(lt / 1.1)
    hgt = lerp(1900, 2050, ease(u))
    cy = lerp(H * 0.58, H * 0.50, up)
    put_char(c, A.char_layer("batman_3", HERO_RIM, HERO_GRADE), (W * 0.5, cy), hgt, lerp(3.0, 0.0, up),
             anchor=(0.5, 0.48))
    ex = [(W * 0.5 + (0.355 - 0.5) * hgt, cy + (0.31 - 0.48) * hgt), (W * 0.5 + (0.62 - 0.5) * hgt, cy + (0.31 - 0.48) * hgt)]
    eye_glint(c, ex, 0.55 * ease((lt - 0.9) / 0.3))
    return finish(c, t, sat=0.9, halftone_col=(0.0, 0.02, 0.08))


def s09_potential(c, t, lt, u):
    hero_bg(c, t, cx=lerp(1180, 1230, u), cy=420, vh=lerp(780, 720, u))
    glow(c, (W * 0.3, H * 0.55), 420, (0.55, 0.75, 1.0), 0.25 + 0.15 * ease(u))
    lay = cape_wave(A.char_layer("batman_4", HERO_RIM, HERO_GRADE), t, 2.0,
                    lambda x, y: batman_cape(x, y, center=0.75, inner=0.2) * smoothstep(0.35, 0.7, x))
    put_char(c, lay, (W * 0.55, H * 0.46), lerp(1650, 1820, ease(u)), 0, anchor=(0.55, 0.45))
    return finish(c, t, sat=0.9, halftone_col=(0.0, 0.02, 0.08))


def s10_smile_freeze(c, t, lt, u):
    # Snap zoom back to the Trickster: the grin stalls for a beat.
    k = ease_out(lt / 0.18, 4)
    joker_bg(c, t, u, cx=360, cy=420, vh=640, rot=3)
    c *= 0.8
    put_char(c, A.char_layer("joker_2", JOKER_RIM, JOKER_GRADE), (W * 0.42, H * 0.50),
             lerp(2600, 2350, k), 0.0, anchor=(0.6, 0.30))
    out = finish(c, t, sat=lerp(0.4, 0.8, k), flash=max(0, 1 - lt / 0.08) * 0.35)
    return out


def s11_smile_returns(c, t, lt, u):
    joker_bg(c, t, u, cx=420, cy=420, vh=lerp(660, 620, u), rot=-3)
    glow(c, (W * 0.5, H * 0.3), 460, GREEN, 0.25)
    put_char(c, A.char_layer("joker_1", JOKER_RIM, JOKER_GRADE), (W * 0.50, H * 0.50),
             lerp(2500, 2600, ease(u)), lerp(-1, -4.5, ease(u)), anchor=(0.50, 0.24))
    return glitch(finish(c, t), t, 0.5 if lt < 0.06 else 0.0, seed=8)


IMPACT_AT = 17.10


def s12_standoff(c, t, lt, u):
    # Diagonal split: Trickster above (purple/green), Hero below (cold blue).
    slam = ease_out(lt / 0.35, 4)
    sh = shake(t, IMPACT_AT, 26, 0.55, seed=21)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    seam_y = H * 0.5 + (xx - W / 2) * -0.32
    top = np.zeros_like(c)
    bot = np.zeros_like(c)
    drift = ease(u) * 0.6
    # When the info card arrives the two halves part to make room in the middle.
    spread = ease((t - INFO_AT) / 0.5)
    # Both keep moving (no hard freeze): the Trickster sways and bobs, the Hero breathes, cape stirs.
    sway = 2.2 * math.sin(t * 1.4) + 0.8 * math.sin(t * 3.1)
    bob = 9 * math.sin(t * 1.9)
    breathe = 1 + 0.012 * math.sin(t * 1.2)
    joker_bg(top, t, u, cx=420, cy=430 + 60 * spread, vh=760 - 30 * drift, rot=-3, sh=sh)
    put_char(top, A.char_layer("joker_4", JOKER_RIM, JOKER_GRADE),
             (lerp(W * 0.1, W * 0.40, slam) + 60 * spread + sh[0], lerp(H * 0.27, 400, spread) + bob + sh[1]),
             lerp(1150 + 40 * drift, 980, spread), -6 + sway, anchor=(0.45, 0.40))
    hero_bg(bot, t, cx=1260, cy=430 - 40 * spread, vh=760 - 30 * drift, rot=-3, sh=sh)
    lay = cape_wave(A.char_layer("batman_1", HERO_RIM, HERO_GRADE), t, 2.2, lambda x, y: batman_cape(x, y))
    put_char(bot, lay, (lerp(W * 0.95, W * 0.60, slam) - 40 * spread + sh[0], lerp(H * 0.76, 1655, spread) + sh[1]),
             lerp(1200 + 40 * drift, 1000, spread) * breathe, -4 + 0.6 * math.sin(t * 0.9), anchor=(0.5, 0.42))
    m = smoothstep(-2, 2, yy - seam_y)[..., None]
    c[:] = top * (1 - m) + bot * m
    # Light clash along the seam: purple/green from above meets blue from below.
    d = (yy - seam_y)
    clash = 0.5 + 0.5 * ease((t - IMPACT_AT + 0.25) / 0.3)
    screen(c, np.exp(-np.clip(-d, 0, None) / 90)[..., None] * (PURPLE * 0.6 + GREEN * 0.4) * (d < 0)[..., None], 0.55 * clash)
    screen(c, np.exp(-np.clip(d, 0, None) / 90)[..., None] * BLUE * (d >= 0)[..., None], 0.6 * clash)
    glow(c, (W * 0.42, H * 0.47), 300, PURPLE * 0.7 + GREEN * 0.3, 0.35 * clash)
    glow(c, (W * 0.58, H * 0.53), 300, BLUE, 0.4 * clash)
    core = np.exp(-(d / 7) ** 2)[..., None]
    screen(c, core * WHITE, 0.9)
    glow(c, (W / 2, H / 2), 260 + 80 * clash, WHITE, 0.25 + 0.45 * max(0, 1 - abs(t - IMPACT_AT) / 0.35))
    burst_a = 0.0
    if IMPACT_AT <= t < IMPACT_AT + 0.45:
        burst_a = 1 - ease((t - IMPACT_AT - 0.2) / 0.25)
        r = 300 * ease_out((t - IMPACT_AT) / 0.12, 3)
        starburst(c, (W / 2 + sh[0], H / 2 + sh[1]), r, [(1, 1, 1), (0.85, 0.95, 1.0), (1, 0.95, 0.6)], burst_a,
                  rot=0.2)
        speed_lines(c, t, (W / 2, H / 2), (1, 1, 1), 0.6 * burst_a, r_in=320, seed=2)
    if LETTERING == "balloon" and IMPACT_AT <= t < IMPACT_AT + 0.75:
        k = (t - IMPACT_AT) / 0.14
        scale = lerp(0.4, 1.12, ease_out(k)) if k < 1 else lerp(1.12, 1.0, ease((k - 1) / 0.8))
        fade = 1 - ease((t - IMPACT_AT - 0.5) / 0.25)
        pop(A.sfx_word, (W / 2 + sh[0], H / 2 + sh[1]), scale, fade, c)
    flash = 0.7 * max(0, 1 - abs(t - IMPACT_AT) / 0.06) if t >= IMPACT_AT - 0.01 else 0
    out = finish(c, t, halftone_col=(0.02, 0.0, 0.06), flash=flash)
    return out


def s13_info(c, t, lt, u):
    # Same standoff, continued: the halves part and the meeting card lands in the middle.
    s0 = 16.75
    out = s12_standoff(c, t, t - s0, (t - s0) / (DURATION - s0))
    fade = ease((t - (DURATION - 0.25)) / 0.25)
    return out * (1 - fade)


SHOT_FUNCS = {name: globals()[name] for _, _, name in SHOTS}


def render_frame(t):
    frame, _ = shot_frame(t)
    # Lettering sits on top of the grade so halftone/grain never touch the text.
    frame = lettering(np.ascontiguousarray(frame, dtype=np.float32), t)
    frame = overlays(frame, t)
    if t > DURATION - 0.25:
        frame *= 1 - ease((t - (DURATION - 0.25)) / 0.25)
    return (np.clip(frame, 0, 1) * 255 + 0.5).astype(np.uint8)

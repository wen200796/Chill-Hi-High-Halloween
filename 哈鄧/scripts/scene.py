"""Harry x Dumbledore cinematic comic: 9:16, 1080x1920 @ 24 fps.

Self-contained (does not import anything from the trickster/hero project).
Built only from the files in 哈鄧/:
  蛇徽魔法學院角色姿態集.png / 銀鬚巫師角色設定集.png (3x2 sheets, cut by cutout.py)
  魔幻城堡三域大廳panorama.png (three separate bays: green | blue/gold | corridor);
  each bay is close to 9:16 on its own, so every shot uses one bay uncut and unstretched.
Light, particles, magic energy, fog and the glowing dialogue are procedural.
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
FPS = 24
# Standoff is quick (2.4 s) and the held ending keeps the trickster/hero length (7.9 s after the flash).
STANDOFF_AT = 13.30
FLASH_AT = 15.70  # energies meet
INFO_AT = FLASH_AT + 0.65   # meeting-info card starts (same offset after the impact as the trickster/hero card)
DURATION = FLASH_AT + 7.9   # 23.6 s
# Platform text-safe area for 9:16, from the project's 文字檢查框.png (guide lines at x 16/283,
# y 82/475.5 on 335x597) scaled to 1080x1920. Every glyph must stay inside.
SAFE_BOX = (52, 265, 912, 1529)

# Voice placement (s). Word timings measured by forced alignment on the original files.
HARRY_VO_AT = 3.35
DUMB_VO_AT = 9.75
# (word, offset in the voice file, row)
HARRY_WORDS = [("I", 0.00, 0), ("won't", 0.13, 0), ("live", 0.48, 0), ("by", 0.78, 0), ("someone", 0.98, 1),
               ("else's", 1.34, 1), ("destiny.", 1.81, 1)]
DUMB_WORDS = [("Choose", 0.06, 0), ("wisely,", 0.62, 0), ("Harry.", 2.05, 0)]
LINES = [
    # speaker, english words, line start, line end, chinese, chinese reveal plan
    ("harry", HARRY_WORDS, HARRY_VO_AT, 6.45, "我不會活在別人替我安排的命運裡。", None),
    # Chinese order differs: "做出明智的選擇。" lights with "Choose wisely," and "哈利，" with "Harry."
    ("dumbledore", DUMB_WORDS, DUMB_VO_AT, 13.05, "哈利，做出明智的選擇。", [(3, 11, 0), (0, 3, 2)]),
]

# Role titles (English only), lit like the dialogue: (text, style, start, end, center).
ROLE_TAGS = [
    ("Speaker", "harry", 1.20, 3.10, (300, 360)),
    ("Evaluator", "dumbledore", 7.30, 9.45, (645, 360)),
]

SHOTS = [
    (0.00, 3.20, "s1_hall"),
    (3.20, 4.30, "s2a_harry"),
    (4.30, 6.70, "s2b_harry_close"),
    (6.70, 9.55, "s3_over_shoulder"),
    (9.55, 11.40, "s4a_dumbledore"),
    (11.40, STANDOFF_AT, "s4b_dumbledore_eyes"),
    (STANDOFF_AT, FLASH_AT, "s5_standoff"),
    (FLASH_AT, DURATION, "s6_hold"),
]

FULL_BODY = {"harry_1", "dumbledore_1"}

EMERALD = np.array([0.20, 0.95, 0.50], np.float32)
EMERALD_DEEP = np.array([0.05, 0.45, 0.22], np.float32)
MIDNIGHT = np.array([0.30, 0.50, 1.00], np.float32)
SILVER = np.array([0.85, 0.90, 1.00], np.float32)
GOLD = np.array([1.00, 0.80, 0.42], np.float32)
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


def affine(src_size, anchor, dst, scale, rot_deg=0.0):
    sw, sh = src_size
    ax, ay = anchor[0] * sw, anchor[1] * sh
    a = math.radians(rot_deg)
    c, s = math.cos(a) * scale, math.sin(a) * scale
    return np.array([[c, -s, dst[0] - (c * ax - s * ay)], [s, c, dst[1] - (s * ax + c * ay)]], np.float32)


def warp(img, M, interp=cv2.INTER_LINEAR):
    return cv2.warpAffine(img, M, (W, H), flags=interp, borderMode=cv2.BORDER_CONSTANT, borderValue=0)


def over(canvas, layer, alpha=1.0):
    a = layer[..., 3:4] * alpha
    canvas *= 1 - a
    canvas += layer[..., :3] * alpha
    return canvas


def screen(canvas, rgb, amount=1.0):
    canvas[:] = 1 - (1 - canvas) * (1 - np.clip(rgb * amount, 0, 1))
    return canvas


def blur(img, sigma):
    return img if sigma < 0.3 else cv2.GaussianBlur(img, (0, 0), sigma)


# ----------------------------------------------------------------------------- assets
class Assets:
    def __init__(self):
        pano = np.asarray(Image.open(ROOT / "魔幻城堡三域大廳panorama.png").convert("RGB")).astype(np.float32) / 255
        self.pano = pano
        # The three bays, cropped where each painting starts/ends (no stretching).
        self.bay_green = pano[:, 0:540]
        self.bay_blue = pano[:, 560:1120]
        self.bay_corridor = pano[:, 1132:1672]
        meta = json.loads((CUT / "meta.json").read_text())
        self.chars = {}
        for key in meta:
            rgba = np.asarray(Image.open(CUT / f"{key}.png")).astype(np.float32) / 255
            rgb = rgba[..., :3]
            rgb = np.clip(rgb + 0.4 * (rgb - cv2.GaussianBlur(rgb, (0, 0), 1.1)), 0, 1)
            a = rgba[..., 3].copy()
            h, w = a.shape
            # Soft fades where the panel crops the figure, so no hard edge ever shows.
            yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
            sides = dict(meta[key])
            if key in FULL_BODY:
                sides["bottom"] = False  # shoes sit close to the panel edge but are not cropped
            a *= smoothstep(0, h * (0.14 if sides["bottom"] else 0.03), h - 1 - yy)
            if sides["top"]:
                a *= smoothstep(0, h * 0.10, yy)
            if sides["left"]:
                a *= smoothstep(0, w * 0.10, xx)
            if sides["right"]:
                a *= smoothstep(0, w * 0.10, w - 1 - xx)
            self.chars[key] = (rgb, a)
        self._cache = {}
        self._make_textures()

    def char(self, key, rim=(), key_light=None, grade=None):
        """Premultiplied RGBA with rim light(s) and a one-sided key light."""
        ck = (key, repr(rim), repr(key_light), repr(grade))
        if ck in self._cache:
            return self._cache[ck]
        rgb, a = self.chars[key]
        rgb = rgb.copy()
        h, w = a.shape
        if grade is not None:
            rgb = np.clip(rgb * np.array(grade[0], np.float32) + np.array(grade[1], np.float32), 0, 1)
        if key_light is not None:
            # Light from one side, falling into shadow on the other (split lighting).
            side, color, strength, shadow = key_light
            xx = np.linspace(0, 1, w, dtype=np.float32)[None, :]
            ramp = xx if side == "right" else 1 - xx
            lit = smoothstep(0.25, 1.0, ramp)[..., None]
            rgb = rgb * (shadow + (1 - shadow) * lit) + lit * np.array(color, np.float32) * strength * rgb
        if rim:
            ab = cv2.GaussianBlur(a, (0, 0), 2.0)
            for color, (dx, dy), strength in rim:
                M = np.float32([[1, 0, -dx], [0, 1, -dy]])
                shifted = cv2.warpAffine(ab, M, (w, h), borderValue=0)
                edge = cv2.GaussianBlur(np.clip(a - shifted, 0, 1), (0, 0), 1.2) * strength
                rgb = 1 - (1 - rgb) * (1 - np.clip(edge[..., None] * np.array(color, np.float32), 0, 1))
        out = np.dstack([np.clip(rgb, 0, 1) * a[..., None], a]).astype(np.float32)
        self._cache[ck] = out
        return out

    def _make_textures(self):
        rng = np.random.default_rng(11)
        n = rng.random((40, 72)).astype(np.float32)
        n = cv2.GaussianBlur(cv2.resize(n, (W * 2, H), interpolation=cv2.INTER_CUBIC), (0, 0), 50)
        self.fog = (n - n.min()) / (n.max() - n.min())
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        cell = 12
        gx, gy = (xx % cell) - cell / 2, (yy % cell) - cell / 2
        d = np.sqrt(gx * gx + gy * gy)
        vign = np.sqrt(((xx - W / 2) / (W * 0.58)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
        self.halftone = np.clip(np.clip((vign - 0.62) * 12, 0, cell * 0.5) - d + 0.5, 0, 1).astype(np.float32)
        self.bottom_fade = smoothstep(1420, 1920, yy[:, :1])[..., None].astype(np.float32)
        self.vignette = np.clip(1 - 0.6 * np.clip(vign - 0.3, 0, 1) ** 1.5, 0, 1)[..., None].astype(np.float32)
        self.grain = [rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32) for _ in range(8)]


A = None


def assets():
    global A
    if A is None:
        A = Assets()
    return A


# ----------------------------------------------------------------------------- layers
def place_bg(canvas, src, cx, cy, view_h, sigma=0.0, mult=1.0, rot=0.0):
    """Show `src` with (cx, cy) at frame center, `view_h` source pixels tall."""
    M = affine((src.shape[1], src.shape[0]), (cx / src.shape[1], cy / src.shape[0]), (W / 2, H / 2), H / view_h, rot)
    img = cv2.warpAffine(src, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    canvas[:] = blur(img, sigma) * mult
    return canvas


def put(canvas, layer, center, height, anchor=(0.5, 0.5), rot=0.0, alpha=1.0, sigma=0.0, mult=1.0):
    h, w = layer.shape[:2]
    lay = np.clip(warp(layer, affine((w, h), anchor, center, height / h, rot), cv2.INTER_CUBIC), 0, 1)
    if sigma > 0.3:
        lay = blur(lay, sigma)
    if mult != 1.0:
        lay[..., :3] *= mult
    return over(canvas, lay, alpha)


def sway(layer, t, amp, region, speed=0.5):
    """Small displacement of robe/beard regions; `region(x, y)` is 0 on the face, hands and wand."""
    h, w = layer.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    wgt = region(xx / w, yy / h)
    dx = amp * wgt * np.sin(2 * np.pi * (speed * t + yy / h * 1.2))
    dy = 0.3 * amp * wgt * np.sin(2 * np.pi * (0.7 * speed * t + xx / w))
    return cv2.remap(layer, xx + dx, yy + dy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)


def low_region(y0=0.55, x_keep=None):
    def f(x, y):
        wgt = smoothstep(y0, 1.0, y)
        if x_keep is not None:
            wgt *= 1 - np.exp(-((x - x_keep[0]) / x_keep[1]) ** 2)
        return wgt
    return f


def fog(canvas, t, color, strength=0.3, low=0.45, speed=25):
    off = int(t * speed) % W
    f = A.fog[:, off:off + W]
    yy = np.linspace(0, 1, H, dtype=np.float32)[:, None]
    return screen(canvas, (f * smoothstep(low, 1.0, yy))[..., None] * np.array(color, np.float32), strength)


def beams(canvas, t, origin_x, color, strength=0.18, spread=0.35, count=3, seed=0):
    """Soft volumetric light shafts falling from high windows."""
    lay = np.zeros((H // 2, W // 2), np.float32)
    rng = np.random.default_rng(seed)
    for k in range(count):
        x0 = origin_x / 2 + rng.uniform(-120, 120)
        ang = rng.uniform(-spread, spread) + 0.04 * math.sin(t * 0.4 + k)
        w0, w1 = rng.uniform(10, 25), rng.uniform(70, 140)
        x1 = x0 + math.tan(ang) * H / 2
        poly = np.int32([(x0 - w0, 0), (x0 + w0, 0), (x1 + w1, H // 2), (x1 - w1, H // 2)])
        cv2.fillPoly(lay, [poly], 0.5 + 0.5 * rng.random(), cv2.LINE_AA)
    lay = cv2.GaussianBlur(lay, (0, 0), 18)
    lay *= np.linspace(1.0, 0.25, H // 2, dtype=np.float32)[:, None]
    lay = cv2.resize(lay, (W, H))
    return screen(canvas, lay[..., None] * np.array(color, np.float32), strength * (0.9 + 0.1 * math.sin(t * 1.3)))


def particles(canvas, t, seed, n, box, color, size=(1.5, 3.5), rise=18, strength=0.9, twinkle=2.0):
    """Slowly drifting magic motes inside box=(x0, y0, x1, y1), drawn with a soft glow."""
    rng = np.random.default_rng(seed)
    base = rng.random((n, 5))
    x0, y0, x1, y1 = box
    lay = np.zeros((H // 2, W // 2), np.float32)
    core = np.zeros((H, W), np.float32)
    for bx, by, ph, sz, sp in base:
        x = x0 + bx * (x1 - x0) + 22 * math.sin(t * (0.3 + sp * 0.5) + ph * 6.28)
        y = y1 - ((by * (y1 - y0) + t * rise * (0.5 + sp)) % (y1 - y0))
        tw = 0.5 + 0.5 * math.sin(t * twinkle * (0.6 + sp) + ph * 9)
        r = size[0] + (size[1] - size[0]) * sz
        cv2.circle(lay, (int(x / 2), int(y / 2)), max(1, int(r * 1.6)), 0.6 * tw, -1, cv2.LINE_AA)
        cv2.circle(core, (int(x), int(y)), max(1, int(r * 0.6)), tw, -1, cv2.LINE_AA)
    glow_l = cv2.resize(cv2.GaussianBlur(lay, (0, 0), 3), (W, H))
    m = np.clip(glow_l + core, 0, 1.5)[..., None]
    return screen(canvas, m * np.array(color, np.float32), strength)


def glow(canvas, center, radius, color, amount):
    yy, xx = np.ogrid[0:H, 0:W]
    g = np.exp(-(((xx - center[0]) ** 2 + (yy - center[1]) ** 2) / float(radius * radius)))[..., None]
    return screen(canvas, g.astype(np.float32) * np.array(color, np.float32), amount)


def energy_stream(canvas, t, start, end, color, core_color, progress, seed, width=10, strands=4, jitter=26):
    """Sinuous magic tendrils from `start` toward `end` (progress 0..1 of the way)."""
    if progress <= 0:
        return canvas
    lay = np.zeros((H // 2, W // 2), np.float32)
    sx, sy = start
    ex, ey = end
    n = 60
    for k in range(strands):
        pts = []
        for i in range(n + 1):
            u = i / n * progress
            x = sx + (ex - sx) * u
            y = sy + (ey - sy) * u
            env = math.sin(math.pi * min(1.0, u / max(progress, 1e-3))) ** 0.7
            off = jitter * env * (math.sin(u * 11 + t * (2.1 + k) + seed + k * 1.7) +
                                  0.5 * math.sin(u * 23 - t * 3.3 + k))
            pts.append((x / 2, (y + off) / 2))
        cv2.polylines(lay, [np.int32(pts)], False, 0.55 if k else 1.0, max(1, int(width / 2 / (1 + k * 0.6))), cv2.LINE_AA)
    g1 = cv2.GaussianBlur(lay, (0, 0), 8)
    g2 = cv2.GaussianBlur(lay, (0, 0), 2)
    big = cv2.resize(g1 * 1.4 + g2, (W, H))
    screen(canvas, big[..., None] * np.array(color, np.float32), 0.9)
    core = cv2.resize(cv2.GaussianBlur(lay, (0, 0), 0.8), (W, H))
    return screen(canvas, np.clip(core - 0.4, 0, 1)[..., None] * np.array(core_color, np.float32), 1.0)


def finish(canvas, t, grade=None, contrast=1.06, grain=0.022, halftone=0.45, flash=0.0, fade=0.0, floor_dark=0.45):
    if grade is not None:
        mult, add = grade
        canvas[:] = canvas * np.array(mult, np.float32) + np.array(add, np.float32)
    canvas[:] = np.clip((canvas - 0.5) * contrast + 0.5, 0, 1)
    canvas *= A.vignette
    # Cinematic dark floor under the safe area: grounds cropped busts and sits under platform captions.
    canvas *= 1 - floor_dark * A.bottom_fade
    ht = A.halftone[..., None] * halftone
    canvas *= 1 - ht
    canvas += ht * np.array((0.0, 0.03, 0.04), np.float32)
    g = cv2.resize(A.grain[int(t * FPS) % len(A.grain)], (W, H), interpolation=cv2.INTER_NEAREST)
    canvas += g[..., None] * grain
    if flash > 0:
        canvas[:] = canvas * (1 - flash) + flash
    if fade > 0:
        canvas *= 1 - fade
    return np.clip(canvas, 0, 1)


GREEN_GRADE = ((0.96, 1.02, 0.97), (0.0, 0.008, 0.004))
BLUE_GRADE = ((0.92, 0.98, 1.10), (0.0, 0.006, 0.02))
HARRY_RIM = [(EMERALD, (-6, -2), 1.3), (SILVER * 0.8, (6, -3), 0.9)]
DUMB_RIM = [(MIDNIGHT, (6, -2), 1.3), (SILVER, (-6, -4), 1.0)]
HARRY_KEY = ("left", (0.30, 1.00, 0.55), 0.32, 0.62)   # emerald from frame-left, other side in shadow
DUMB_KEY = ("right", (0.55, 0.70, 1.00), 0.45, 0.65)   # moon-blue from frame-right


# ----------------------------------------------------------------------------- shots
def to_frame(bx, by, cx, cy, vh):
    """Bay pixel -> frame pixel for a view centered on (cx, cy), vh bay pixels tall."""
    k = H / vh
    return W / 2 + (bx - cx) * k, H / 2 + (by - cy) * k


def s1_hall(c, t, lt, u):
    # The green Slytherin bay, full height; a slow push toward Harry standing alone on the floor.
    k = ease(u)
    cx, cy, vh = lerp(270, 250, k), lerp(470, 610, k), lerp(941, 760, k)
    place_bg(c, A.bay_green, cx, cy, vh, sigma=lerp(0.0, 0.6, k), mult=0.9)
    beams(c, t, W * 0.3, EMERALD * 0.8 + SILVER * 0.2, 0.18, seed=2)
    fx, fy = to_frame(245, 905, cx, cy, vh)
    lay = sway(A.char("harry_1", HARRY_RIM, HARRY_KEY, GREEN_GRADE), t, 2.5, low_region(0.45, (0.95, 0.1)))
    sh = np.zeros((H, W), np.float32)
    cv2.ellipse(sh, (int(fx), int(fy)), (int(95 * H / vh), int(12 * H / vh)), 0, 0, 360, 0.6, -1, cv2.LINE_AA)
    c *= 1 - cv2.GaussianBlur(sh, (0, 0), 8)[..., None]
    put(c, lay, (fx, fy), 560 * H / vh, anchor=(0.45, 0.985))
    glow(c, (fx, fy - 30 * H / vh), 140 * H / vh, EMERALD, 0.22)
    particles(c, t, 1, 80, (0, 0, W, H), EMERALD, rise=16, strength=0.55)
    fog(c, t, EMERALD_DEEP * 0.6 + SILVER * 0.1, 0.35, low=0.6)
    return finish(c, t, grade=GREEN_GRADE)


def harry_bg(c, t, cx, cy, vh, sigma):
    place_bg(c, A.bay_green, cx, cy, vh, sigma, mult=0.85)
    beams(c, t, W * 0.3, EMERALD * 0.7 + SILVER * 0.3, 0.14, seed=4)


def s2a_harry(c, t, lt, u):
    # Medium close-up, wand at his chin: composed, holding something back.
    harry_bg(c, t, 330, 420, 420, 7)
    lay = A.char("harry_5", HARRY_RIM, HARRY_KEY, GREEN_GRADE)
    put(c, lay, (W * 0.52, 900), lerp(1250, 1330, ease(u)), anchor=(0.5, 0.45), rot=lerp(1.2, 0.0, ease(u)))
    particles(c, t, 3, 50, (0, 0, W, H), EMERALD, rise=10, strength=0.5)
    fog(c, t, EMERALD_DEEP * 0.5, 0.22, low=0.65)
    return finish(c, t, grade=GREEN_GRADE, floor_dark=0.75)


def s2b_harry_close(c, t, lt, u):
    # Closer, on the scar and the confident half-smile: resolve lands on "someone else's destiny".
    harry_bg(c, t, 300, 380, 340, 9)
    lay = A.char("harry_2", HARRY_RIM, HARRY_KEY, GREEN_GRADE)
    put(c, lay, (W * 0.50, 900), lerp(1480, 1600, ease(u)), anchor=(0.5, 0.42), rot=0.4 * math.sin(t * 0.8))
    glow(c, (W * 0.15, H * 0.25), 420, EMERALD, 0.18)
    particles(c, t, 5, 45, (0, 0, W, H), EMERALD, rise=8, strength=0.45)
    return finish(c, t, grade=GREEN_GRADE, floor_dark=0.75)


def s3_over_shoulder(c, t, lt, u):
    # Over Harry's shoulder: rack focus from him (foreground) to Dumbledore across the blue hall.
    rack = ease((lt - 0.2) / 1.0)
    cx, cy, vh = 285, lerp(560, 545, u), lerp(720, 680, u)
    place_bg(c, A.bay_blue, cx, cy, vh, lerp(5, 2.0, rack), mult=0.8)
    beams(c, t, W * 0.6, SILVER * 0.6 + MIDNIGHT * 0.4, 0.2, seed=6)
    fx, fy = to_frame(330, 760, cx, cy, vh)
    d = sway(A.char("dumbledore_1", DUMB_RIM, DUMB_KEY, BLUE_GRADE), t, 1.8, low_region(0.55, (0.55, 0.1)))
    put(c, d, (fx, fy), 330 * H / vh, anchor=(0.5, 0.97), sigma=lerp(4, 0, rack))
    particles(c, t, 7, 60, (W * 0.35, H * 0.2, W, H * 0.7), SILVER * 0.7 + MIDNIGHT * 0.3, rise=9,
              strength=0.6 * (0.4 + 0.6 * rack))
    fog(c, t, MIDNIGHT * 0.35, 0.3, low=0.55, speed=-20)
    hlay = A.char("harry_3", HARRY_RIM, None, GREEN_GRADE)
    put(c, hlay, (lerp(W * 0.26, W * 0.24, u), H * 0.80), 1550, anchor=(0.5, 0.45),
        sigma=lerp(0.0, 9.0, rack), mult=lerp(0.85, 0.5, rack))
    return finish(c, t, grade=BLUE_GRADE)


def dumb_bg(c, t, cx, cy, vh, sigma):
    place_bg(c, A.bay_blue, cx, cy, vh, sigma, mult=0.8)
    beams(c, t, W * 0.7, SILVER * 0.6 + MIDNIGHT * 0.4, 0.16, seed=8)


def s4a_dumbledore(c, t, lt, u):
    dumb_bg(c, t, 300, 330, 360, 8)
    lay = sway(A.char("dumbledore_3", DUMB_RIM, DUMB_KEY, BLUE_GRADE), t, 1.6, low_region(0.6, (0.5, 0.18)), 0.35)
    put(c, lay, (W * 0.50, 900), lerp(1260, 1330, ease(u)), anchor=(0.5, 0.42))
    particles(c, t, 9, 45, (0, 0, W, H), SILVER * 0.7 + MIDNIGHT * 0.3, rise=6, strength=0.45)
    return finish(c, t, grade=BLUE_GRADE, floor_dark=0.75)


def s4b_dumbledore_eyes(c, t, lt, u):
    # Extreme close-up on the eyes for "Harry." - almost still, a very slow push.
    dumb_bg(c, t, 330, 300, 300, 10)
    lay = A.char("dumbledore_5", DUMB_RIM, DUMB_KEY, BLUE_GRADE)
    put(c, lay, (W * 0.50, 650), lerp(1540, 1600, ease(u)), anchor=(0.55, 0.42))
    particles(c, t, 11, 30, (0, 0, W, H), SILVER, rise=5, strength=0.35)
    return finish(c, t, grade=BLUE_GRADE, floor_dark=0.75)


# Standoff in the corridor bay. Characters are laid out in frame pixels (big, near the camera:
# Harry left-front, Dumbledore right and a step further back); the bay behind them is framed
# separately. Three layouts: NEAR (start of the pull-back), FULL (no card) and CARD (both sink so
# their heads clear the info card).
H1_WAND = (0.98, 0.74)   # wand tip, relative to the harry_1 panel
D1_WAND = (0.55, 0.80)   # wand tip, relative to the dumbledore_1 panel
H1_ANCHOR, D1_ANCHOR = (0.45, 0.985), (0.5, 0.97)
LAYOUT = {
    #        bg view (cx, cy, vh)   Harry feet, height     Dumbledore feet, height
    "near": ((270, 600, 640), (170, 2060), 1450, (900, 1560), 900),
    "full": ((270, 540, 760), (185, 1850), 1220, (880, 1500), 800),
    "card": ((270, 470, 760), (190, 2130), 1160, (880, 1835), 860),
}


def mix_layout(a, b, k):
    la, lb = LAYOUT[a], LAYOUT[b]

    def mx(x, y):
        if isinstance(x, tuple):
            return tuple(lerp(p, q, k) for p, q in zip(x, y))
        return lerp(x, y, k)
    return tuple(mx(x, y) for x, y in zip(la, lb))


def standoff(c, t, layout, energy, flash_amt):
    view, hfeet, hh, dfeet, dh = layout
    cx, cy, vh = view
    place_bg(c, A.bay_corridor, cx, cy, vh, sigma=1.2, mult=0.85)
    beams(c, t, W * 0.5, SILVER * 0.5 + MIDNIGHT * 0.3 + EMERALD * 0.2, 0.15, seed=10)
    breathe = 1 + 0.006 * math.sin(t * 1.3)
    hh, dh = hh * breathe, dh * (2 - breathe)
    sh = np.zeros((H, W), np.float32)
    cv2.ellipse(sh, (int(dfeet[0]), int(dfeet[1])), (int(dh * 0.2), int(dh * 0.025)), 0, 0, 360, 0.6, -1, cv2.LINE_AA)
    c *= 1 - cv2.GaussianBlur(sh, (0, 0), 8)[..., None]
    dl = sway(A.char("dumbledore_1", DUMB_RIM, DUMB_KEY, BLUE_GRADE), t, 2.0, low_region(0.5, (0.5, 0.12)))
    put(c, dl, dfeet, dh, anchor=D1_ANCHOR)
    glow(c, (dfeet[0], dfeet[1] - dh * 0.5), dh * 0.6, MIDNIGHT * 0.5 + SILVER * 0.2, 0.2 + 0.12 * energy)
    hl = sway(A.char("harry_1", HARRY_RIM, HARRY_KEY, GREEN_GRADE), t, 2.4, low_region(0.45, (0.95, 0.1)))
    put(c, hl, hfeet, hh, anchor=H1_ANCHOR)
    pw_h, ph_h = A.chars["harry_1"][1].shape[1], A.chars["harry_1"][1].shape[0]
    pw_d, ph_d = A.chars["dumbledore_1"][1].shape[1], A.chars["dumbledore_1"][1].shape[0]
    hx = hfeet[0] + (H1_WAND[0] - H1_ANCHOR[0]) * pw_h * hh / ph_h
    hy = hfeet[1] + (H1_WAND[1] - H1_ANCHOR[1]) * hh
    dx = dfeet[0] + (D1_WAND[0] - D1_ANCHOR[0]) * pw_d * dh / ph_d
    dy = dfeet[1] + (D1_WAND[1] - D1_ANCHOR[1]) * dh
    # The energies rise from both wand tips and meet in the open air between the two of them.
    mx, my = (hfeet[0] + dfeet[0]) / 2 + 40, dfeet[1] - 0.48 * dh
    k = hh / 1260
    gap = lerp(200, 22, energy) * k
    energy_stream(c, t, (hx, hy), (mx - gap / 2, my + gap * 0.15), EMERALD, (0.85, 1.0, 0.9), energy, 1,
                  width=11 * k, jitter=22 * k)
    energy_stream(c, t, (dx, dy), (mx + gap / 2, my - gap * 0.15), MIDNIGHT * 0.6 + SILVER * 0.4, (1.0, 1.0, 1.0),
                  energy, 4, width=10 * k, jitter=20 * k)
    glow(c, (hx, hy), 60 * k, EMERALD, 0.4 + 0.4 * energy)
    glow(c, (dx, dy), 52 * k, SILVER * 0.6 + MIDNIGHT * 0.4, 0.4 + 0.4 * energy)
    if energy > 0.85:
        crackle = 0.5 + 0.5 * math.sin(t * 17) * math.sin(t * 7.3)
        glow(c, (mx, my), (34 + 24 * crackle) * k, WHITE, 0.35 + 0.25 * crackle)
    particles(c, t, 13, 70, (0, 0, W / 2, H), EMERALD, rise=10, strength=0.5)
    particles(c, t, 14, 70, (W / 2, 0, W, H), SILVER * 0.6 + MIDNIGHT * 0.4, rise=10, strength=0.5)
    fog(c, t, EMERALD_DEEP * 0.3 + MIDNIGHT * 0.25, 0.3, low=0.6)
    if flash_amt > 0:
        glow(c, (mx, my), 900, WHITE, 0.55 * flash_amt)
    return c


def s5_standoff(c, t, lt, u):
    # Slow pull-back from close on the two of them; the energies reach toward each other.
    k = ease(u)
    standoff(c, t, mix_layout("near", "full", k), k * 0.92, 0.0)
    return finish(c, t, grade=((0.95, 1.0, 1.04), (0, 0.004, 0.01)), floor_dark=0.3)


def s6_hold(c, t, lt, u):
    # Flash as the energies almost touch, then a 7.9 s held standoff with idle motion (no hard freeze).
    # When the info card arrives both sink a little so their heads stay clear below it.
    room = ease((t - INFO_AT) / 0.5)
    lay = mix_layout("full", "card", room)
    push = 1 + 0.03 * ease((t - INFO_AT - 0.5) / (DURATION - INFO_AT - 0.5))
    lay = (lay[0], lay[1], lay[2] * push, lay[3], lay[4] * push)
    standoff(c, t, lay, 0.92 + 0.08 * ease(lt / 0.4), max(0.0, 1 - lt / 0.5))
    fade = ease((t - (DURATION - 0.25)) / 0.25)
    return finish(c, t, grade=((0.95, 1.0, 1.04), (0, 0.004, 0.01)), flash=0.6 * max(0, 1 - lt / 0.12), fade=fade,
                  floor_dark=0.3)


# Mist and magic laid over every shot: (left tint, right tint, amount).
ATMOS = {
    "s1_hall": (EMERALD, EMERALD, 1.0), "s2a_harry": (EMERALD, EMERALD, 0.8),
    "s2b_harry_close": (EMERALD, EMERALD, 0.7), "s3_over_shoulder": (EMERALD, SILVER * 0.6 + MIDNIGHT * 0.4, 0.9),
    "s4a_dumbledore": (SILVER * 0.6 + MIDNIGHT * 0.4, SILVER * 0.6 + MIDNIGHT * 0.4, 0.8),
    "s4b_dumbledore_eyes": (SILVER * 0.6 + MIDNIGHT * 0.4, SILVER * 0.6 + MIDNIGHT * 0.4, 0.6),
    "s5_standoff": (EMERALD, SILVER * 0.6 + MIDNIGHT * 0.4, 1.0), "s6_hold": (EMERALD, SILVER * 0.6 + MIDNIGHT * 0.4, 1.0),
}
_XR = np.linspace(0, 1, W, dtype=np.float32)[None, :, None]
_YR = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]


def atmosphere(c, t, name):
    """Rolling low mist, a drifting mid-height haze, slow glowing wisps and twinkling motes."""
    left, right, amt = ATMOS[name]
    tint = left * (1 - _XR) + right * _XR
    # Two mist banks moving at different speeds (parallax), thickest near the floor.
    for speed, low, strength, off in ((22, 0.55, 0.42, 0), (-14, 0.3, 0.22, W // 2)):
        o = (int(t * speed) + off) % W
        f = A.fog[:, o:o + W][..., None]
        mask = f * smoothstep(low, 1.0, _YR) * (0.6 + 0.4 * f)
        screen(c, mask * (0.55 * tint + 0.45 * SILVER * 0.5), strength * amt)
    # A soft overall haze that lifts the blacks a little, like air full of fine mist.
    screen(c, (0.12 * tint + 0.05) * (0.6 + 0.4 * smoothstep(0.2, 1.0, _YR)), 0.5 * amt)
    # Slow glowing wisps of magic smoke.
    lay = np.zeros((H // 4, W // 4), np.float32)
    for k in range(4):
        ph = k * 1.9
        base_y = (0.25 + 0.18 * k) * H / 4
        pts = [(x, base_y + 18 * math.sin(x / 40 + t * (0.5 + 0.1 * k) + ph) + 8 * math.sin(x / 13 - t * 0.9 + k))
               for x in np.linspace(-20, W / 4 + 20, 40)]
        cv2.polylines(lay, [np.int32(pts)], False, 0.7, 2, cv2.LINE_AA)
    lay = cv2.GaussianBlur(lay, (0, 0), 3.5) * (0.55 + 0.45 * np.sin(t * 0.8 + _XR[..., 0][:, ::4] * 6) ** 2)[:H // 4]
    wisps = cv2.resize(lay, (W, H))[..., None]
    screen(c, wisps * tint, 0.5 * amt)
    # Twinkling motes with tiny cross flares.
    rng = np.random.default_rng(int(t * 3) + 100)
    pts = np.zeros((H // 2, W // 2), np.float32)
    for _ in range(int(26 * amt)):
        x, y = rng.uniform(0, W / 2), rng.uniform(0, H / 2)
        tw = math.sin(math.pi * ((t * 3) % 1)) * rng.uniform(0.4, 1.0)
        cv2.circle(pts, (int(x), int(y)), 1, tw, -1, cv2.LINE_AA)
        cv2.line(pts, (int(x) - 5, int(y)), (int(x) + 5, int(y)), tw * 0.5, 1, cv2.LINE_AA)
        cv2.line(pts, (int(x), int(y) - 5), (int(x), int(y) + 5), tw * 0.5, 1, cv2.LINE_AA)
    pts = cv2.resize(cv2.GaussianBlur(pts, (0, 0), 1.0) * 1.8 + pts, (W, H))[..., None]
    screen(c, pts * (0.5 * tint + 0.5), 0.8 * amt)
    return np.clip(c, 0, 1)


SHOT_FUNCS = {name: globals()[name] for _, _, name in SHOTS}


def shot_at(t):
    for s, e, name in SHOTS:
        if s <= t < e or (name == SHOTS[-1][2] and t >= s):
            return s, e, name
    raise ValueError(t)


def render_frame(t, lettering=True):
    a = assets()
    s, e, name = shot_at(t)
    c = np.zeros((H, W, 3), np.float32)
    frame = SHOT_FUNCS[name](c, t, t - s, (t - s) / (e - s))
    frame = atmosphere(frame, t, name)
    if name == "s6_hold" and t > DURATION - 0.25:
        frame *= 1 - ease((t - (DURATION - 0.25)) / 0.25)
    if lettering:
        import magic_text
        frame = magic_text.draw(frame, t)
        import info_card
        frame = info_card.draw(frame, t)
        if t > DURATION - 0.25:
            frame *= 1 - ease((t - (DURATION - 0.25)) / 0.25)
    return (np.clip(frame, 0, 1) * 255 + 0.5).astype(np.uint8)

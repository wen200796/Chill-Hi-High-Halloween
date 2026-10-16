#!/usr/bin/env python3
"""
合成預告片的音樂與音效（只需要 numpy）。

依 src/config/timeline.json 的時間點產生：
  public/audio/trailer_mix.wav   音樂 + 音效（正式版）
  public/audio/trailer_sfx.wav   只有音效（無音樂版）
  public/audio/stems/*.wav       個別音軌（方便之後替換）

所有聲音都是程式合成的原創素材，沒有授權問題。
若要改用自己的配樂：把配樂檔放進 public/audio/，並修改 src/config/audio.ts 的 mix 路徑。
"""
import json
import os
import wave

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TL = json.load(open(os.path.join(ROOT, "src", "config", "timeline.json"), encoding="utf-8"))

SR = 48000
DUR = TL["durationSec"]
N = int(SR * DUR)
S = TL["scenes"]
C = TL["cues"]
rng = np.random.default_rng(20261027)

# ---------------------------------------------------------------- 工具函式


def tt(d):
    return np.arange(int(SR * d)) / SR


def noise(d, seed=None):
    r = np.random.default_rng(seed) if seed is not None else rng
    return r.standard_normal(int(SR * d))


def fft_filter(x, lo=None, hi=None, order=2):
    """頻域濾波：lo = 高通截止、hi = 低通截止（Butterworth 形狀）"""
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    g = np.ones_like(f)
    if hi:
        g *= 1 / np.sqrt(1 + (f / hi) ** (2 * order))
    if lo:
        with np.errstate(divide="ignore"):
            g *= 1 / np.sqrt(1 + (lo / np.maximum(f, 1e-6)) ** (2 * order))
    return np.fft.irfft(X * g, len(x))


def env_adsr(n, a=0.01, d=0.1, s=0.7, r=0.2):
    e = np.ones(n) * s
    na, nd, nr = int(a * SR), int(d * SR), int(r * SR)
    na = min(na, n)
    e[:na] = np.linspace(0, 1, na)
    nd = min(nd, n - na)
    e[na : na + nd] = np.linspace(1, s, nd)
    nr = min(nr, n)
    if nr > 0:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def exp_decay(n, tau):
    return np.exp(-np.arange(n) / SR / tau)


def saw(freq, d, harmonics=30, detune=0.0):
    t = tt(d)
    out = np.zeros_like(t)
    for k in range(1, harmonics + 1):
        if freq * k > SR / 2 - 1000:
            break
        out += np.sin(2 * np.pi * freq * k * t * (1 + detune)) / k
    return out * 0.6


def note(name):
    names = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11}
    pitch, octave = name[:-1], int(name[-1])
    midi = 12 * (octave + 1) + names[pitch]
    return 440.0 * 2 ** ((midi - 69) / 12)


class Bus:
    def __init__(self):
        self.L = np.zeros(N)
        self.R = np.zeros(N)

    def add(self, sig, at, gain=1.0, pan=0.0):
        i = int(round(at * SR))
        if i >= N:
            return
        sig = sig[: N - i]
        gl = gain * np.sqrt((1 - pan) / 2) * np.sqrt(2)
        gr = gain * np.sqrt((1 + pan) / 2) * np.sqrt(2)
        self.L[i : i + len(sig)] += sig * gl
        self.R[i : i + len(sig)] += sig * gr

    def add_st(self, l, r, at, gain=1.0):
        i = int(round(at * SR))
        n = min(len(l), N - i)
        self.L[i : i + n] += l[:n] * gain
        self.R[i : i + n] += r[:n] * gain

    def cut(self, t0, t1, fade=0.004):
        """t0–t1 完全靜音（含極短淡出，避免爆音）"""
        i0, i1, nf = int(t0 * SR), int(t1 * SR), int(fade * SR)
        ramp = np.linspace(1, 0, nf)
        for ch in (self.L, self.R):
            ch[i0 - nf : i0] *= ramp
            ch[i0:i1] = 0

    def stereo(self):
        return np.stack([self.L, self.R], axis=1)


music = Bus()
sfx = Bus()

# ---------------------------------------------------------------- Scene 1：低頻轟鳴、風聲、遠方雷聲

d = S["portal"]["end"] + 0.2
rum = fft_filter(noise(d, 1), hi=90, order=3) * 2.2
t = tt(d)
rum += np.sin(2 * np.pi * 41 * t) * 0.35 * np.clip(t / 1.2, 0, 1)
rum *= np.clip(t / 0.5, 0, 1) * np.clip((d - t) / 0.4, 0, 1)
sfx.add(rum, 0.0, 0.55)

d = S["portal"]["end"]
for seed, pan in ((2, -0.6), (3, 0.6)):
    w = fft_filter(noise(d, seed), lo=250, hi=1300, order=2)
    t = tt(d)
    mod = 0.55 + 0.45 * np.sin(2 * np.pi * (0.4 + seed * 0.07) * t + seed)
    w *= mod * np.clip(t / 0.4, 0, 1) * np.clip((d - t) / 0.6, 0, 1)
    sfx.add(w, 0.0, 0.18, pan)

# 雷聲
lt = C["lightning"]
crack = fft_filter(noise(0.25, 4), lo=900, order=2) * exp_decay(int(0.25 * SR), 0.04)
sfx.add(crack, lt + 0.02, 0.22, 0.4)
d = 1.6
thun = fft_filter(noise(d, 5), hi=160, order=3)
t = tt(d)
thun *= (np.clip(t / 0.08, 0, 1) * np.exp(-t / 0.55)) * (0.7 + 0.3 * np.sin(2 * np.pi * 7 * t) ** 2) * 3.0
sfx.add(thun, lt + 0.08, 0.7, 0.3)

# ---------------------------------------------------------------- 低音 Drone（音樂）

d = TL["cues"]["musicStop"] + 0.1
t = tt(d)
drone = (saw(note("D2"), d, 20) + saw(note("A2"), d, 16, 0.002) * 0.6 + saw(note("D1"), d, 8) * 0.8)
drone = fft_filter(drone, hi=320, order=2)
drone *= np.clip(t / 1.0, 0, 1) * (0.55 + 0.45 * np.clip((t - 3.0) / 6.5, 0, 1))
music.add(drone, 0.0, 0.32)

# ---------------------------------------------------------------- Scene 2：能量充電、低頻衝擊

def impact(size=1.0, seed=10):
    d = 1.8
    t = tt(d)
    f = 30 + 70 * np.exp(-t / 0.08)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / (0.5 * size))
    hit = fft_filter(noise(d, seed), hi=2400, order=2) * np.exp(-t / 0.06) * 0.9
    tail = fft_filter(noise(d, seed + 1), hi=500, order=2) * np.exp(-t / (0.5 * size)) * 0.6
    return (sub * 1.4 + hit + tail) * size


p0, p1 = S["portal"]["start"], S["portal"]["end"]
sfx.add(impact(0.9, 11), p0, 0.6)
d = p1 - p0
t = tt(d)
f = 140 * (1500 / 140) ** (t / d) ** 1.6
riser = np.sin(2 * np.pi * np.cumsum(f) / SR) * (t / d) ** 1.4
riser += np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR) * (t / d) ** 2 * 0.4
nr = noise(d, 12)
nr = fft_filter(nr, lo=800, hi=9000) * (t / d) ** 2.2 * 1.6
sfx.add(riser * 0.25 + nr * 0.3, p0, 0.9)
# 電流嗶剝聲
for i in range(14):
    at = p0 + 0.05 + rng.random() * (d - 0.15)
    z = fft_filter(noise(0.05, 30 + i), lo=2500, order=2) * exp_decay(int(0.05 * SR), 0.01)
    sfx.add(z, at, 0.12, rng.uniform(-0.8, 0.8))

# ---------------------------------------------------------------- Scene 3：角色登場重擊 + 呼嘯 + 弦樂頑固音型

r0 = S["roster"]["start"]
nshots = len(TL["roster"])
shot = (S["roster"]["end"] - r0) / nshots
sfx.add(impact(1.2, 20), r0, 0.8)


def taiko(seed):
    d = 0.7
    t = tt(d)
    f = 55 + 70 * np.exp(-t / 0.03)
    b = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.22)
    sk = fft_filter(noise(d, seed), hi=1800) * np.exp(-t / 0.02) * 0.6
    return b + sk


def whoosh(d=0.22, seed=0):
    t = tt(d)
    w = fft_filter(noise(d, seed), lo=400, hi=5000)
    return w * np.sin(np.pi * t / d) ** 2 * (t / d)


for i in range(nshots):
    at = r0 + i * shot
    if i > 0:
        sfx.add(taiko(40 + i), at, 0.75)
    sfx.add(whoosh(0.18, 60 + i), at - 0.16, 0.45, (-0.5 if i % 2 else 0.5))

ost_pat = ["D3", "D3", "F3", "D3", "G3", "D3", "F3", "E3"]
step = 0.25
t_end = S["assemble"]["end"]
k = 0
at = r0
while at < t_end - 0.01:
    n = ost_pat[k % len(ost_pat)]
    d = 0.22
    s = saw(note(n), d, 24) + saw(note(n) * 2, d, 12, 0.003) * 0.4
    s = fft_filter(s, hi=2200) * env_adsr(len(s), 0.005, 0.08, 0.4, 0.06)
    music.add(s, at, 0.2 if at < S["assemble"]["start"] else 0.24, -0.2 if k % 2 else 0.2)
    k += 1
    at += step
# 低音每拍
at = r0
while at < t_end - 0.01:
    d = 0.45
    b = saw(note("D2"), d, 10)
    b = fft_filter(b, hi=400) * env_adsr(len(b), 0.005, 0.15, 0.5, 0.15)
    music.add(b, at, 0.35)
    at += 0.5

# ---------------------------------------------------------------- Scene 4：銅管和弦、重擊、鼓滾漸強

a0 = S["assemble"]["start"]
theme_at = a0 + 2.0
chords = [
    (a0, a0 + 1.0, ["D3", "F3", "A3", "D4"]),
    (a0 + 1.0, theme_at, ["Bb2", "D3", "F3", "Bb3"]),
    (theme_at, theme_at + 0.7, ["F2", "F3", "A3", "C4", "F4"]),
    (theme_at + 0.7, t_end + 0.2, ["A2", "E3", "A3", "C#4", "E4"]),
]
for (c0, c1, ns) in chords:
    d = c1 - c0 + 0.05
    t = tt(d)
    sig = np.zeros(len(t))
    for j, n in enumerate(ns):
        sig += saw(note(n), d, 28, 0.0015 * (j - 2))
        sig += saw(note(n), d, 28, -0.002 * (j - 1)) * 0.6
    bright = fft_filter(sig, hi=2600)
    dark = fft_filter(sig, hi=700)
    sw = np.exp(-t / 0.35)  # 強起音後收暗
    s = bright * sw + dark * (1 - sw) * 1.3
    s *= env_adsr(len(s), 0.02, 0.2, 0.85, 0.03)
    music.add(s, c0, 0.11)

sfx.add(impact(1.3, 70), a0, 0.85)
sfx.add(impact(1.0, 71), a0 + 1.0, 0.6)
sfx.add(impact(1.6, 72), theme_at, 1.0)
# 鼓滾漸強
roll_start = theme_at + 0.5
at = roll_start
while at < t_end - 0.02:
    p = (at - roll_start) / (t_end - roll_start)
    d = 0.08
    sn = fft_filter(noise(d, int(at * 1000)), lo=180, hi=6000) * exp_decay(int(d * SR), 0.03)
    sfx.add(sn, at, 0.12 + 0.35 * p, rng.uniform(-0.3, 0.3))
    at += 0.125 * (1 - p * 0.7)
# 上升音
d = t_end - roll_start
t = tt(d)
f = 200 * 4 ** (t / d)
up = np.sin(2 * np.pi * np.cumsum(f) / SR) * (t / d) ** 2
sfx.add(up, roll_start, 0.12)

# ---------------------------------------------------------------- 音樂突然停止

ms = C["musicStop"]
music.cut(ms, S["finale"]["start"])
sfx.cut(ms, S["stage"]["start"])

# ---------------------------------------------------------------- Scene 5–6：寂靜的舞台、聚光燈、提示音

st0 = S["stage"]["start"]
d = S["finale"]["start"] - st0 + 0.3
room = fft_filter(noise(d, 80), hi=600, order=1)
t = tt(d)
room *= np.clip(t / 0.3, 0, 1) * np.clip((d - t) / 0.3, 0, 1)
sfx.add(room, st0, 0.012)
# 聚光燈開關
d = 0.25
t = tt(d)
clunk = np.sin(2 * np.pi * 95 * t) * np.exp(-t / 0.05) + fft_filter(noise(d, 81), lo=1500) * np.exp(-t / 0.006) * 0.8
sfx.add(clunk, C["spotlightOn"], 0.45)

# 任務卡：紙卡拍擊 + 短促提示音
cs = C["cardSlam"]
d = 0.2
t = tt(d)
slap = fft_filter(noise(d, 90), lo=700, hi=5000) * np.exp(-t / 0.025) * 1.2 + np.sin(2 * np.pi * 70 * t) * np.exp(-t / 0.07)
sfx.add(slap, cs, 0.6)
d = 0.9
t = tt(d)
ding = np.zeros(len(t))
for ratio, amp, tau in ((1, 1, 0.35), (2.0, 0.5, 0.22), (2.76, 0.35, 0.15), (5.4, 0.15, 0.08)):
    ding += np.sin(2 * np.pi * 1318.5 * ratio * t) * amp * np.exp(-t / tau)
ding *= np.clip(t / 0.003, 0, 1)
sfx.add(ding, cs + 0.02, 0.22)

# ---------------------------------------------------------------- Scene 7：腳步、溫暖鋼琴、片尾和弦

f0 = S["finale"]["start"]
for i, at in enumerate((f0 + 0.04, f0 + 0.28, f0 + 0.52)):
    d = 0.2
    t = tt(d)
    step_s = np.sin(2 * np.pi * 150 * t) * np.exp(-t / 0.03) + fft_filter(noise(d, 100 + i), hi=1200) * np.exp(-t / 0.015) * 0.6
    sfx.add(step_s, at, 0.28 - i * 0.05, -0.1 + i * 0.1)


def piano(freq, d):
    t = tt(d)
    s = np.zeros(len(t))
    for k2, amp in ((1, 1), (2, 0.45), (3, 0.2), (4, 0.12), (5, 0.06)):
        s += np.sin(2 * np.pi * freq * k2 * t) * amp * np.exp(-t / (1.1 / k2))
    return s * np.clip(t / 0.004, 0, 1) * np.clip((d - t) / 0.05, 0, 1)


arp = ["D4", "F#4", "A4", "D5", "E5", "A4", "F#5", "D5"]
for i, n in enumerate(arp):
    music.add(piano(note(n), 1.6), f0 + 0.1 + i * 0.2, 0.13, -0.3 + 0.6 * (i % 2))

# 溫暖和弦鋪底
pad0 = C["finaleSpotlight"]
d = DUR - pad0
t = tt(d)
pad = np.zeros(len(t))
for j, n in enumerate(["D3", "A3", "D4", "F#4", "A4", "E5"]):
    pad += np.sin(2 * np.pi * note(n) * t * (1 + 0.001 * j)) * (1 if j < 4 else 0.5)
    pad += np.sin(2 * np.pi * note(n) * 2 * t) * 0.15
pad = fft_filter(pad, hi=2500)
pad *= np.clip(t / 0.5, 0, 1) * np.clip((d - t) / 0.6, 0, 1)
music.add(pad, pad0, 0.09)
# 片尾主和弦（鋼琴）
for j, n in enumerate(["D3", "A3", "D4", "F#4", "A4", "D5"]):
    music.add(piano(note(n), DUR - C["endCardComplete"]), C["endCardComplete"] - 0.02 + j * 0.015, 0.1)

# 片尾閃光聲
d = 1.2
t = tt(d)
sh = np.zeros(len(t))
for j, fr in enumerate((2637, 3136, 3520, 4186)):
    sh += np.sin(2 * np.pi * fr * t) * np.exp(-((t - 0.1 - j * 0.07) ** 2) / 0.01) * (0.6 + 0.4 * np.sin(2 * np.pi * 14 * t))
sfx.add(sh, C["endCardStart"], 0.05, 0.2)
sw = whoosh(0.5, 120)
sfx.add(sw, C["endCardStart"] - 0.25, 0.25)

# ---------------------------------------------------------------- 混音與輸出


def finish(x, peak_db=-4.5):
    x = x - np.mean(x, axis=0)
    x = np.tanh(x * 1.1) / np.tanh(1.1)  # 輕微軟限幅
    peak = np.max(np.abs(x))
    x = x / peak * 10 ** (peak_db / 20)
    # 首尾淡入淡出，避免爆音
    nf = int(0.01 * SR)
    x[:nf] *= np.linspace(0, 1, nf)[:, None]
    nf = int(0.25 * SR)
    x[-nf:] *= np.linspace(1, 0, nf)[:, None]
    return x


def write_wav(path, x):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = (np.clip(x, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())
    print("wrote", os.path.relpath(path, ROOT))


m = music.stereo()
s = sfx.stereo()
mix = m * 1.0 + s * 1.0
# 混音版與音效版使用同一個增益，讓兩版本的音效音量一致
mix_f = finish(mix)
gain = np.max(np.abs(np.tanh(mix * 1.1) / np.tanh(1.1)))
sfx_only = np.tanh(s * 1.1) / np.tanh(1.1) / gain * 10 ** (-4.5 / 20)
nf = int(0.25 * SR)
sfx_only[-nf:] *= np.linspace(1, 0, nf)[:, None]

out = os.path.join(ROOT, "public", "audio")
write_wav(os.path.join(out, "trailer_mix.wav"), mix_f)
write_wav(os.path.join(out, "trailer_sfx.wav"), sfx_only)
write_wav(os.path.join(out, "stems", "music.wav"), finish(m, -3))
write_wav(os.path.join(out, "stems", "sfx.wav"), finish(s, -3))

"""Score, sound effects and final mix, all synthesized here with numpy/scipy.

No third-party music or sample libraries are used: every music part and sound effect is
generated from oscillators and filtered noise below, so the result is original and free
to use. The two voice files are the project's own recordings, used unedited (only level
matched and placed on the timeline).

Output: output/_build/mix.wav (48 kHz stereo) plus stems for inspection.
"""
import subprocess
from pathlib import Path

import numpy as np
from scipy import signal

import scene

ROOT = scene.ROOT
BUILD = ROOT / "output/_build"
SR = 48000
DUR = scene.DURATION
N = int(round(DUR * SR))
BPM = 96
BEAT = 60 / BPM
RNG = np.random.default_rng(2026)

# Cue times on the master timeline (seconds), matched to the picture in scene.py.
WHOOSH_AT = 0.80
STINGER_AT = scene.JOKER_VO_AT + 5.25
HERO_IMPACT_AT = 7.60
CAPE_AT = 8.05
SMILE_GLITCH_AT = 15.85
CLASH_AT = scene.IMPACT_AT
INFO_AT = scene.INFO_AT
CARD_AT = INFO_AT + 0.15          # info card lands (matches scene.overlays)
PRIZE_AT = INFO_AT + 1.5          # first of the four bouncing prize characters
ENDING_AT = DUR - 0.85            # closing button under the info card
FADE_END = DUR - 0.02
TARGET_LUFS = -16.0


def t_axis(n):
    return np.arange(n) / SR


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def sos(kind, f, order=2):
    return signal.butter(order, f, btype=kind, fs=SR, output="sos")


def filt(x, kind, f, order=2):
    return signal.sosfilt(sos(kind, f, order), x, axis=0)


def place(bus, sig, at, pan=0.0, gain=1.0):
    """Add mono or stereo `sig` into stereo `bus` at time `at` with equal-power pan."""
    i = int(round(at * SR))
    if i >= len(bus):
        return
    # De-click: 1 ms fade-in and 6 ms fade-out on every event.
    sig = sig.copy()
    fi, fo = min(len(sig), int(0.001 * SR)), min(len(sig), int(0.006 * SR))
    ramp_shape = (slice(None),) + (None,) * (sig.ndim - 1)
    sig[:fi] *= np.linspace(0, 1, fi)[ramp_shape]
    sig[len(sig) - fo:] *= np.linspace(1, 0, fo)[ramp_shape]
    if sig.ndim == 1:
        a = (pan + 1) * np.pi / 4
        sig = np.stack([sig * np.cos(a), sig * np.sin(a)], axis=1) * np.sqrt(2)
    j = min(len(bus), i + len(sig))
    bus[i:j] += sig[: j - i] * gain


def adsr(n, a, d, s_level=0.0, r=0.0):
    t = t_axis(n)
    e = np.where(t < a, t / max(a, 1e-4), s_level + (1 - s_level) * np.exp(-(t - a) / max(d, 1e-4)))
    if r:
        e *= np.clip((n / SR - t) / r, 0, 1)
    return e


def saw(f, n, detune=0.0, phase=0.0):
    t = t_axis(n)
    return 2 * ((f * (1 + detune) * t + phase) % 1) - 1


def noise(n):
    return RNG.standard_normal(n)


def sweep_sine(f0, f1, n, curve=6.0):
    t = t_axis(n)
    f = f1 + (f0 - f1) * np.exp(-t * curve)
    return np.sin(2 * np.pi * np.cumsum(f) / SR)


def tv_bandpass(x, centers, q=1.4):
    """Time-varying band-pass by overlap-adding zero-phase filtered blocks (whooshes/risers)."""
    hop = 512
    win = np.hanning(hop * 2 + 1)[:-1]  # sums to 1 at 50% overlap
    xp = np.concatenate([np.zeros(hop), x, np.zeros(hop * 3)])
    out = np.zeros_like(xp)
    for s in range(0, len(x) + hop, hop):
        c = float(centers[min(s, len(centers) - 1)])
        lo, hi = max(30.0, c / (1 + 1 / q)), min(SR / 2 - 200.0, c * (1 + 1 / q))
        seg = xp[s: s + hop * 2]
        out[s: s + hop * 2] += signal.sosfiltfilt(sos("bandpass", [lo, hi]), seg) * win
    return out[hop: hop + len(x)]


def reverb_ir(seconds=2.2, rt60=2.0, tone=5000):
    n = int(seconds * SR)
    t = t_axis(n)
    ir = np.stack([noise(n), noise(n)], axis=1) * np.exp(-6.9 * t / rt60)[:, None]
    ir = filt(ir, "lowpass", tone)
    ir[: int(0.012 * SR)] = 0  # pre-delay
    return ir / np.sqrt((ir ** 2).sum(axis=0, keepdims=True))


IR_HALL = None


def reverb(x, wet=0.3, ir=None):
    global IR_HALL
    if ir is None:
        if IR_HALL is None:
            IR_HALL = reverb_ir()
        ir = IR_HALL
    if x.ndim == 1:
        x = np.stack([x, x], axis=1)
    y = np.stack([signal.fftconvolve(x[:, c], ir[:, c])[: len(x)] for c in range(2)], axis=1)
    return x * (1 - wet) + y * wet


def db(v):
    return 10 ** (v / 20)


# ----------------------------------------------------------------------------- music
def music():
    bus = np.zeros((N, 2))
    t = t_axis(N)

    # 1. Low atmosphere: detuned saws on D2/A2 through a slow-moving low-pass.
    pad = sum(saw(midi(m), N, d, ph) for m in (38, 45) for d, ph in ((-0.004, 0.1), (0.005, 0.6)))
    pad = filt(pad, "lowpass", 420, 4)
    lvl = np.interp(t, [0, 1.4, 7.4, 7.7, 15.0, 15.2, 15.85, 17.0, 17.1], [0, 1, 1, 0.75, 0.75, 0.45, 0.45, 0.7, 0])
    stereo = np.stack([pad, np.roll(pad, 240)], axis=1)
    bus += stereo * lvl[:, None] * db(-30)

    # 2. Mysterious pulse (0 – 7.6): sub thump + filtered pluck with ping-pong echo.
    for k in range(int(7.6 / BEAT)):
        at = k * BEAT
        n = int(0.5 * SR)
        thump = sweep_sine(110, 45, n, 18) * adsr(n, 0.004, 0.16)
        place(bus, thump, at, gain=db(-17))
        if k % 2 == 1:
            n = int(0.35 * SR)
            pl = filt(saw(midi(62), n) + saw(midi(62), n, 0.006), "lowpass", 1400) * adsr(n, 0.002, 0.09)
            for e, (pan, g) in enumerate(((-0.5, -27), (0.6, -33), (-0.6, -39))):
                place(bus, pl, at + e * BEAT * 0.75, pan, db(g))

    # 3. Trickster groove (1.0 – 7.6): irregular square blips + swung ticks.
    scale = [74, 77, 79, 81, 84, 86]  # D minor pentatonic, high
    step = BEAT / 4
    pattern_rng = np.random.default_rng(13)
    for k in range(int(1.0 / step), int(7.55 / step)):
        at = k * step + (0.035 if k % 2 else 0.0)  # swing
        if pattern_rng.random() < 0.42:
            n = int(0.09 * SR)
            f = midi(int(pattern_rng.choice(scale)))
            sq = np.sign(np.sin(2 * np.pi * f * t_axis(n))) * adsr(n, 0.001, 0.025)
            sq = filt(sq, "bandpass", [600, 5000])
            place(bus, sq, at, float(pattern_rng.uniform(-0.7, 0.7)), db(-31))
        if k % 2 == 1:
            n = int(0.05 * SR)
            hat = filt(noise(n), "highpass", 7000) * adsr(n, 0.001, 0.012)
            place(bus, hat, at, 0.3, db(-30 if k % 4 == 3 else -36))

    # 4. Hero section (8.85 – 15): half-time deep drums, steady bass ostinato, dark chord.
    for at in np.arange(8.85, 15.0, BEAT * 2):
        n = int(1.1 * SR)
        drum = sweep_sine(95, 42, n, 10) * adsr(n, 0.003, 0.35)
        drum += filt(noise(n), "lowpass", 260) * adsr(n, 0.002, 0.07) * 0.6
        place(bus, reverb(drum, 0.25), at, gain=db(-13))
    for k, at in enumerate(np.arange(8.20, 15.0, BEAT / 2)):
        n = int(BEAT / 2 * SR)
        root = 26 if at < 12.25 else 22  # D1 then Bb0
        f = midi(root + (12 if k % 4 == 2 else 0))
        b = np.sin(2 * np.pi * f * t_axis(n)) + 0.3 * filt(saw(f, n), "lowpass", 220)
        place(bus, b * adsr(n, 0.005, 0.18, 0.4, 0.03), at, gain=db(-17))
    for at, chord in ((8.2, (50, 53, 57)), (12.25, (46, 50, 53))):
        n = int((12.25 - 8.2 if at < 12 else 15.0 - 12.25) * SR)
        ch = sum(saw(midi(m), n, d) for m in chord for d in (-0.003, 0.004))
        ch = filt(ch, "lowpass", 900, 4) * adsr(n, 0.8, 99, 1.0, 0.25)
        place(bus, np.stack([ch, np.roll(ch, 300)], axis=1), at, gain=db(-33))

    # 5. Smile-freeze dropout (15.0 – 15.85): a single high glassy tone only.
    n = int(0.85 * SR)
    place(bus, np.sin(2 * np.pi * midi(86) * t_axis(n)) * adsr(n, 0.05, 0.4), 15.0, 0.2, db(-34))

    # 6. Riser (15.85 – 17.1): rising noise sweep + climbing saw, crescendo.
    n = int((CLASH_AT - 15.85) * SR)
    ramp = np.linspace(0, 1, n) ** 2
    rs = tv_bandpass(noise(n), 400 * (1 + 15 * ramp), q=2.5) * ramp
    f = midi(50) * 2 ** (ramp * 1.0)
    rs2 = filt(2 * ((np.cumsum(f) / SR) % 1) - 1, "lowpass", 2500) * ramp
    place(bus, rs * 0.9 + rs2 * 0.25, 15.85, gain=db(-11))

    # 7. The hit (CLASH_AT): sub drop + low brass-like stab + cymbal wash, long reverb tail.
    n = int((DUR - CLASH_AT) * SR)
    hit = sweep_sine(70, 30, n, 3) * adsr(n, 0.003, 0.9)
    stab = sum(saw(midi(m), n, d) for m in (38, 45, 50, 53) for d in (-0.004, 0.005))
    stab = filt(stab, "lowpass", 1500, 4) * adsr(n, 0.01, 0.5) * 0.25
    wash = filt(noise(n), "highpass", 4000) * adsr(n, 0.002, 0.7) * 0.25
    tail = reverb(hit * 0.9 + stab + wash, 0.45, reverb_ir(2.6, 2.4, 4000))
    place(bus, tail, CLASH_AT, gain=db(-13))

    # 8. Outro bed under the info card: both themes together, kept low so the card reads.
    start, stop = INFO_AT + 0.1, ENDING_AT
    n = int((stop - start + 0.4) * SR)
    bed = sum(saw(midi(m), n, d) for m in (38, 45, 50) for d in (-0.004, 0.005))
    bed = filt(bed, "lowpass", 600, 4) * adsr(n, 0.6, 99, 1.0, 0.4)
    place(bus, np.stack([bed, np.roll(bed, 300)], axis=1), start, gain=db(-31))
    for k, at in enumerate(np.arange(start, stop, BEAT)):
        n = int(0.5 * SR)
        place(bus, sweep_sine(100, 45, n, 16) * adsr(n, 0.004, 0.15), at, gain=db(-19))  # pulse
        if k % 2 == 1:
            n = int(0.9 * SR)
            drum = sweep_sine(90, 44, n, 10) * adsr(n, 0.003, 0.3)
            place(bus, reverb(drum, 0.25), at, gain=db(-19))  # hero drum, softer
    outro_rng = np.random.default_rng(31)
    step = BEAT / 4
    for k in range(int(start / step) + 1, int(stop / step)):
        at = k * step + (0.035 if k % 2 else 0.0)
        if outro_rng.random() < 0.28:  # sparser trickster blips
            n = int(0.08 * SR)
            f = midi(int(outro_rng.choice(scale)))
            sq = filt(np.sign(np.sin(2 * np.pi * f * t_axis(n))), "bandpass", [600, 4500]) * adsr(n, 0.001, 0.022)
            place(bus, sq, at, float(outro_rng.uniform(-0.7, 0.7)), db(-36))

    # 9. Closing button: one short low hit and a stab, ringing out before the last frame.
    n = int(0.85 * SR)
    end_hit = sweep_sine(80, 36, n, 5) * adsr(n, 0.003, 0.3)
    end_stab = filt(sum(saw(midi(m), n, d) for m in (38, 50, 53, 57) for d in (-0.004, 0.005)), "lowpass", 1800, 4)
    end_stab *= adsr(n, 0.005, 0.18) * 0.2
    place(bus, reverb(end_hit + end_stab, 0.35, reverb_ir(0.9, 0.7, 5000)), ENDING_AT, gain=db(-11))
    return bus


# ----------------------------------------------------------------------------- sound effects
def sfx():
    bus = np.zeros((N, 2))

    # Trickster entrance whoosh, panned right -> center (he slides in from the right).
    n = int(0.55 * SR)
    tt = np.linspace(0, 1, n)
    centers = 500 + 3500 * np.sin(np.pi * np.clip(tt * 1.1, 0, 1)) ** 2
    w = tv_bandpass(noise(n), centers, q=1.2) * np.sin(np.pi * np.clip(tt, 0, 1)) ** 1.5
    pan = np.interp(tt, [0, 0.6, 1], [0.9, 0.1, 0.0])
    a = (pan + 1) * np.pi / 4
    place(bus, np.stack([w * np.cos(a), w * np.sin(a)], axis=1) * np.sqrt(2), WHOOSH_AT, gain=db(-13))

    # Taunt stinger: glitchy stutter bursts + a falling "pew" (after "fun!", before the cut).
    g_rng = np.random.default_rng(5)
    for k in range(6):
        n = int(g_rng.uniform(0.018, 0.04) * SR)
        f = g_rng.choice([880, 1320, 1760, 660, 2200])
        b = np.sign(np.sin(2 * np.pi * f * t_axis(n))) * 0.6 + 0.4 * noise(n)
        b = np.round(b * 6) / 6  # bit-crush
        place(bus, filt(b, "bandpass", [500, 7000]) * adsr(n, 0.001, 0.02), STINGER_AT + k * 0.045,
              float(g_rng.uniform(-0.8, 0.8)), db(-21))
    n = int(0.22 * SR)
    place(bus, sweep_sine(1500, 280, n, 14) * adsr(n, 0.002, 0.08), STINGER_AT + 0.25, 0.0, db(-22))

    # Hero entrance: deep cinematic impact with a reverb bloom.
    n = int(2.0 * SR)
    boom = sweep_sine(75, 32, n, 2.5) * adsr(n, 0.004, 0.75)
    boom += filt(noise(n), "lowpass", 180) * adsr(n, 0.002, 0.12) * 0.8
    place(bus, reverb(boom, 0.35), HERO_IMPACT_AT, gain=db(-9))

    # Cape movement: low, soft wind swell.
    n = int(1.0 * SR)
    tt = np.linspace(0, 1, n)
    wind = tv_bandpass(noise(n), 250 + 500 * np.sin(np.pi * tt), q=0.9)
    wind *= np.sin(np.pi * tt) ** 2
    place(bus, wind, CAPE_AT, -0.3, db(-19))

    # Smile returns: two tiny digital ticks, barely there.
    for k in range(2):
        n = int(0.03 * SR)
        b = filt(np.round(noise(n) * 3) / 3, "bandpass", [2000, 8000]) * adsr(n, 0.001, 0.008)
        place(bus, b, SMILE_GLITCH_AT + k * 0.06, 0.4 - 0.8 * k, db(-30))

    # Standoff clash: comic crack + low-frequency impact; its reverb is the final ring-out.
    n = int(2.4 * SR)
    snap = noise(n) * adsr(n, 0.0005, 0.012)
    crack = filt(noise(n), "bandpass", [900, 4500]) * adsr(n, 0.001, 0.07)
    low = sweep_sine(90, 34, n, 4) * adsr(n, 0.003, 0.6)
    place(bus, reverb(snap * 0.6 + crack * 0.8 + low, 0.4, reverb_ir(2.4, 2.2, 6000)), CLASH_AT, gain=db(-12))

    # Info card lands: a papery slap with a small low thud.
    n = int(0.3 * SR)
    slap = filt(noise(n), "bandpass", [300, 3500]) * adsr(n, 0.001, 0.035)
    thud = sweep_sine(140, 60, n, 20) * adsr(n, 0.002, 0.06)
    place(bus, slap * 0.7 + thud, CARD_AT, gain=db(-16))
    # Club ribbon: a lighter slap.
    place(bus, slap * 0.6, CARD_AT + 0.2, 0.3, db(-23))
    # "神秘小禮": four bubbly pops climbing D minor, one per character.
    for i, m in enumerate((74, 77, 81, 86)):
        n = int(0.14 * SR)
        f0 = midi(m)
        pop = np.sin(2 * np.pi * np.cumsum(f0 * (1 + 0.6 * np.exp(-t_axis(n) * 60))) / SR) * adsr(n, 0.002, 0.04)
        place(bus, pop, PRIZE_AT + i * 0.14, -0.45 + 0.3 * i, db(-24))
    return bus


# ----------------------------------------------------------------------------- voice + mix
def load_voice(name):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(ROOT / name), "-f", "f32le", "-ac", "1",
                          "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)


def active_rms(x):
    frame = int(0.05 * SR)
    r = np.sqrt(np.convolve(x ** 2, np.ones(frame) / frame, "same"))
    return np.sqrt(np.mean(x[r > r.max() * 0.1] ** 2))


def voices():
    bus = np.zeros(N)
    for name, at in (("joker2.mp3", scene.JOKER_VO_AT), ("batman.mp3", scene.HERO_VO_AT)):
        v = filt(load_voice(name), "highpass", 70)
        v *= db(-17) / active_rms(v)  # match both voices to the same speech level
        i = int(round(at * SR))
        bus[i:i + len(v)] += v[: N - i]
    return bus


def duck_env(vo, depth_db=-9, attack=0.04, release=0.35):
    """Smooth gain curve that pulls the music down while anyone speaks."""
    frame = int(0.02 * SR)
    r = np.sqrt(np.convolve(vo ** 2, np.ones(frame) / frame, "same"))
    on = (r > db(-45)).astype(float)
    cur = 0.0
    # Run the envelope on a decimated signal for speed, then interpolate back.
    step = 48
    idx = np.arange(0, len(on), step)
    out = np.empty(len(idx))
    ka, kr = 1 - np.exp(-step / (attack * SR)), 1 - np.exp(-step / (release * SR))
    for j, i in enumerate(idx):
        target = on[i]
        cur += (target - cur) * (ka if target > cur else kr)
        out[j] = cur
    g = np.interp(np.arange(len(on)), idx, out)
    return db(depth_db * g)


def soft_limit(x, ceiling_db=-1.5, knee_db=-6.0):
    """Linear below the knee, smooth tanh shoulder up to the ceiling (no color on the voice)."""
    c, k = db(ceiling_db), db(knee_db)
    mag = np.abs(x)
    over_k = k + (c - k) * np.tanh((mag - k) / (c - k))
    return np.sign(x) * np.where(mag > k, over_k, mag)


def main():
    BUILD.mkdir(parents=True, exist_ok=True)
    m, s, v = music(), sfx(), voices()
    duck = duck_env(v)
    m *= duck[:, None]
    # Music + SFX share the stereo field; the voice sits dead center on top.
    mix = m + s + v[:, None]
    # Gentle master fade so the ring-out lands before the last frame.
    t = t_axis(N)
    mix *= np.clip((FADE_END - t) / 0.45, 0, 1)[:, None] ** 1.5
    # Loudness-normalize to -16 LUFS (mobile/social level), then a soft ceiling.
    import pyloudnorm
    meter = pyloudnorm.Meter(SR)
    gain = db(TARGET_LUFS - meter.integrated_loudness(mix))
    mix *= gain
    mix = soft_limit(mix)

    def write(name, x):
        x = np.ascontiguousarray(np.clip(x, -1, 1).astype(np.float32))
        if x.ndim == 1:
            x = np.stack([x, x], axis=1)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                        "-c:a", "pcm_s24le", str(BUILD / name)], input=x.tobytes(), check=True)

    write("stem_music.wav", m)
    write("stem_sfx.wav", s)
    write("stem_voice.wav", v)
    write("mix.wav", mix)
    np.save(BUILD / "duck_curve.npy", duck[::480])
    print("mix peak dBFS", 20 * np.log10(np.abs(mix).max()))


if __name__ == "__main__":
    main()

"""Original score, sound effects and mix for the Harry x Dumbledore piece (self-contained).

Everything except the two voice files is synthesized here (oscillators, Karplus-Strong plucks,
formant-filtered "choir", filtered noise, convolution reverb), so the music is original and free
to use. The style nods to the films' sound world - celesta in 3/4, E minor with chromatic turns,
strings, wordless choir, harp, timpani, tubular bell - but the melody is newly written and
does not quote any film theme. The voice files are used unedited (level-matched and placed).

Output: 哈鄧/output/_build/mix.wav (48 kHz stereo) + stems.
"""
import subprocess

import numpy as np
import pyloudnorm
from scipy import signal

import scene

ROOT = scene.ROOT
BUILD = ROOT / "output/_build"
SR = 48000
DUR = scene.DURATION
N = int(round(DUR * SR))
BEAT = 60 / 90          # 3/4 at 90 bpm: a bar is 2.0 s
RNG = np.random.default_rng(1997)
TARGET_LUFS = -16.0


def t_axis(n):
    return np.arange(n) / SR


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


NOTE = {n: i for i, n in enumerate(["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"])}


def m(name):
    """'E5' -> midi number."""
    return 12 * (int(name[-1]) + 1) + NOTE[name[:-1]]


def sos(kind, f, order=2):
    return signal.butter(order, f, btype=kind, fs=SR, output="sos")


def filt(x, kind, f, order=2):
    return signal.sosfilt(sos(kind, f, order), x, axis=0)


def adsr(n, a, d, s=0.0, r=0.0):
    t = t_axis(n)
    e = np.where(t < a, t / max(a, 1e-4), s + (1 - s) * np.exp(-(t - a) / max(d, 1e-4)))
    if r:
        e = e * np.clip((n / SR - t) / r, 0, 1)
    return e


def place(bus, sig, at, pan=0.0, gain=1.0):
    i = int(round(at * SR))
    if i >= len(bus) or i < 0:
        return
    sig = sig.copy()
    fi, fo = min(len(sig), int(0.002 * SR)), min(len(sig), int(0.01 * SR))
    shape = (slice(None),) + (None,) * (sig.ndim - 1)
    sig[:fi] *= np.linspace(0, 1, fi)[shape]
    sig[len(sig) - fo:] *= np.linspace(1, 0, fo)[shape]
    if sig.ndim == 1:
        a = (pan + 1) * np.pi / 4
        sig = np.stack([sig * np.cos(a), sig * np.sin(a)], axis=1) * np.sqrt(2)
    j = min(len(bus), i + len(sig))
    bus[i:j] += sig[: j - i] * gain


def reverb_ir(seconds=3.0, rt60=2.6, tone=6000, seed=0):
    rng = np.random.default_rng(seed)
    n = int(seconds * SR)
    t = t_axis(n)
    ir = rng.standard_normal((n, 2)) * np.exp(-6.9 * t / rt60)[:, None]
    ir = filt(ir, "lowpass", tone)
    ir[: int(0.02 * SR)] = 0
    return ir / np.sqrt((ir ** 2).sum(axis=0, keepdims=True))


HALL = reverb_ir()


def reverb(x, wet=0.35, ir=HALL):
    if x.ndim == 1:
        x = np.stack([x, x], axis=1)
    y = np.stack([signal.fftconvolve(x[:, c], ir[:, c])[: len(x)] for c in range(2)], axis=1)
    return x * (1 - wet) + y * wet


def db(v):
    return 10 ** (v / 20)


# ----------------------------------------------------------------------------- instruments
def celesta(note, dur=1.6):
    n = int(dur * SR)
    t = t_axis(n)
    f = midi(note)
    x = np.zeros(n)
    for mult, amp, dec in ((1.0, 1.0, 0.9), (2.0, 0.28, 0.35), (3.0, 0.10, 0.2), (4.07, 0.07, 0.12)):
        x += amp * np.sin(2 * np.pi * f * mult * t * (1 + 0.0007 * np.sin(2 * np.pi * 5 * t))) * np.exp(-t / dec)
    x += 0.015 * filt(RNG.standard_normal(n), "lowpass", 6000) * np.exp(-t / 0.004)  # soft hammer
    return x * adsr(n, 0.002, 99)


def bell(note, dur=4.0):
    """Tubular bell: inharmonic partials, long ring."""
    n = int(dur * SR)
    t = t_axis(n)
    f = midi(note)
    x = sum(a * np.sin(2 * np.pi * f * k * t) * np.exp(-t / d)
            for k, a, d in ((0.5, 0.4, 2.5), (1.0, 1.0, 2.0), (2.76, 0.5, 1.2), (5.4, 0.25, 0.6), (8.93, 0.12, 0.3)))
    return x


def pluck(note, dur=1.8, bright=0.5):
    """Karplus-Strong harp string, computed a period at a time."""
    n = int(dur * SR)
    p = int(SR / midi(note))
    buf = RNG.uniform(-1, 1, p)
    buf = filt(buf, "lowpass", 2000 + 6000 * bright)
    out = np.zeros(n + p)
    out[:p] = buf
    for s in range(p, n, p):
        prev = out[s - p:s]
        nxt = 0.5 * (prev + np.roll(prev, 1)) * 0.996
        out[s:s + p] = nxt[: min(p, n + p - s)]
    return out[:n] * adsr(n, 0.001, 99)


def strings(notes, dur, attack=0.8, release=0.8, tremolo=0.0, bright=1600):
    n = int(dur * SR)
    t = t_axis(n)
    x = np.zeros(n)
    for note in notes:
        f = midi(note)
        for det in (-0.004, 0.0, 0.005):
            vib = 1 + 0.003 * np.sin(2 * np.pi * (5.2 + det * 100) * t)
            x += 2 * ((np.cumsum(f * (1 + det) * vib) / SR) % 1) - 1
    x = filt(x, "lowpass", bright, 4) / (3 * len(notes))
    if tremolo:
        x *= 1 - 0.5 * tremolo * (1 + np.sin(2 * np.pi * 11 * t))
    return x * adsr(n, attack, 99, 1.0, release)


def choir(notes, dur, attack=1.0, release=1.0, vowel=((700, 110), (1220, 120), (2600, 160))):
    """Wordless 'aah': saw voices through vowel formants."""
    n = int(dur * SR)
    t = t_axis(n)
    src = np.zeros(n)
    for note in notes:
        f = midi(note)
        for det in (-0.006, 0.0, 0.007):
            vib = 1 + 0.004 * np.sin(2 * np.pi * (4.8 + det * 50) * t + det * 300)
            src += 2 * ((np.cumsum(f * (1 + det) * vib) / SR) % 1) - 1
    y = sum(signal.sosfilt(sos("bandpass", [fc - bw, fc + bw]), src) * g
            for (fc, bw), g in zip(vowel, (1.0, 0.6, 0.25)))
    y += 0.02 * filt(RNG.standard_normal(n), "bandpass", [600, 3000])  # breath
    return y / (3 * len(notes)) * adsr(n, attack, 99, 1.0, release)


def timpani(note="E2", dur=1.6):
    n = int(dur * SR)
    t = t_axis(n)
    f = midi(m(note))
    x = np.sin(2 * np.pi * np.cumsum(f * (1 + 0.15 * np.exp(-t / 0.03))) / SR) * np.exp(-t / 0.7)
    x += 0.5 * np.sin(2 * np.pi * f * 1.5 * t) * np.exp(-t / 0.4)
    x += 0.4 * filt(RNG.standard_normal(n), "lowpass", 300) * np.exp(-t / 0.05)
    return x


def sparkle(dur=0.35, bright=1.0):
    """Tiny magic glint: high pings with a shimmer of filtered noise."""
    n = int(dur * SR)
    t = t_axis(n)
    x = 0.4 * filt(RNG.standard_normal(n), "bandpass", [5000, 11000]) * np.exp(-t / 0.08)
    for f in RNG.choice([2637, 3136, 3520, 3951, 4699], 2, replace=False):
        x += 0.25 * np.sin(2 * np.pi * f * t) * np.exp(-t / (0.12 * bright))
    return x


# ----------------------------------------------------------------------------- score
# Original celesta motif (E minor, chromatic descent B-A#-A), 3/4: (beat offset, note, beats)
MOTIF = [(0, "G5", 1), (1, "E5", 1), (2, "B5", 1),
         (3, "A#5", 1.5), (4.5, "A5", 0.5), (5, "F#5", 1),
         (6, "G5", 1), (7, "D#5", 1), (8, "E5", 1),
         (9, "C6", 3)]


def play_motif(bus, start, gain, octave=0, transpose_end=None, pan=-0.15):
    for beat, note, length in MOTIF:
        nn = m(note) + 12 * octave
        if transpose_end and note == "C6":
            nn = m(transpose_end) + 12 * octave
        place(bus, celesta(nn, 1.2 + length * BEAT), start + beat * BEAT, pan + 0.1 * np.sin(beat), gain)


def music():
    dry = np.zeros((N, 2))
    t = t_axis(N)

    # Low string drone through the whole piece, swelling and thinning with the story.
    drone = strings([m("E2"), m("B2")], DUR, attack=1.5, release=0.6, bright=700)
    lvl = np.interp(t, [0, 3, 6.7, 9.5, 13.3, 16.8, 17.1, 18, 24, 25], [0.8, 1, 0.9, 0.8, 1.1, 1.4, 0.4, 0.8, 0.8, 0])
    dry += np.stack([drone * lvl, np.roll(drone * lvl, 400)], axis=1) * db(-18)

    # Opening: celesta motif over a soft E minor pad.
    play_motif(dry, 0.9, db(-17))
    place(dry, strings([m("E3"), m("G3"), m("B3")], 3.4, 1.2, 0.8), 0.4, -0.2, db(-24))
    # Harry's line: C major colour under "destiny", choir enters.
    place(dry, strings([m("C3"), m("E3"), m("G3"), m("B3")], 3.6, 0.8, 0.8), 3.2, 0.2, db(-24))
    place(dry, choir([m("E4"), m("G4"), m("B4")], 2.4, 0.9, 0.9), 5.1, 0.0, db(-22))

    # Dumbledore's reveal: harp glissando up, the colour turns to B minor / G.
    for i, note in enumerate(["E3", "F#3", "G3", "B3", "D4", "E4", "F#4", "G4", "B4", "D5", "E5", "F#5"]):
        place(dry, pluck(m(note), 2.2, 0.4 + i * 0.04), 6.70 + i * 0.045, -0.6 + i * 0.1, db(-17))
    place(dry, choir([m("D4"), m("F#4"), m("B4")], 3.0, 1.0, 1.0, vowel=((450, 90), (800, 100), (2830, 160))), 6.9,
          0.15, db(-21))
    place(dry, strings([m("G2"), m("D3"), m("B3")], 3.1, 1.0, 0.9), 6.7, 0.0, db(-23))
    # High string shimmer for the blue side.
    place(dry, strings([m("B5"), m("F#6")], 2.8, 1.0, 1.0, tremolo=0.6, bright=5000), 7.0, 0.4, db(-34))

    # Dumbledore's line: Am colour, then only one celesta note between "wisely," and "Harry".
    place(dry, strings([m("A2"), m("E3"), m("C4")], 2.1, 0.8, 0.6), 9.55, 0.0, db(-25))
    place(dry, celesta(m("E6"), 2.5), 11.45, 0.25, db(-20))
    place(dry, strings([m("C3"), m("G3"), m("E4")], 1.9, 0.6, 0.8), 11.4, 0.0, db(-27))

    # Standoff: string tremolo climbing, timpani roll crescendo, low brass swell.
    for at, chord in ((13.3, ["E3", "G3", "B3"]), (14.6, ["C3", "G3", "E4"]), (15.9, ["B2", "D#3", "F#3", "A3"])):
        place(dry, strings([m(n) for n in chord], 1.45, 0.25, 0.15, tremolo=0.8, bright=2400), at, 0.0, db(-21))
    brass = strings([m("E2"), m("B2"), m("E3")], 3.6, 2.8, 0.05, bright=900)
    place(dry, brass * np.linspace(0.4, 1.0, len(brass)), 13.5, 0.0, db(-19))
    roll_t = 14.6
    while roll_t < scene.FLASH_AT - 0.05:
        k = (roll_t - 14.6) / (scene.FLASH_AT - 14.6)
        place(dry, timpani("E2", 0.5), roll_t, float(RNG.uniform(-0.2, 0.2)), db(-30 + 16 * k))
        roll_t += 0.085 - 0.03 * k

    # The flash: timpani + low boom + tubular bell + choir chord, ringing out.
    hit = timpani("E2", 2.5) * 1.2
    nb = int(2.5 * SR)
    hit += np.sin(2 * np.pi * np.cumsum(65 * np.exp(-t_axis(nb) * 1.2) + 30) / SR) * np.exp(-t_axis(nb) / 0.9)
    place(dry, hit, scene.FLASH_AT, 0.0, db(-15))
    place(dry, bell(m("E4"), 5.0), scene.FLASH_AT, 0.1, db(-21))
    place(dry, choir([m("E3"), m("B3"), m("E4"), m("G4")], 3.0, 0.02, 2.5), scene.FLASH_AT, 0.0, db(-21))

    # Ending under the info card: the motif returns, gentle strings, close on E minor (add 9).
    play_motif(dry, 18.15, db(-20), transpose_end="E6", pan=0.1)
    for at, chord, dur in ((17.9, ["E3", "G3", "B3"], 2.1), (20.0, ["C3", "G3", "E4"], 2.1),
                           (22.1, ["A2", "E3", "C4"], 1.0), (23.1, ["E3", "B3", "F#4", "G4"], 1.85)):
        place(dry, strings([m(n) for n in chord], dur, 0.6, 0.6), at, 0.0, db(-24))
    place(dry, choir([m("E4"), m("G4"), m("B4")], 2.0, 0.6, 1.2), 23.0, 0.0, db(-27))
    place(dry, celesta(m("E5"), 1.9), 23.1, -0.2, db(-19))
    place(dry, celesta(m("B5"), 1.8), 23.1 + BEAT, 0.2, db(-22))
    wet = reverb(dry, 0.38)
    # Close cleanly: everything has rung out by the last frame.
    wet *= np.clip((DUR - 0.03 - t) / 1.2, 0, 1)[:, None] ** 1.5
    return wet


def sfx():
    bus = np.zeros((N, 2))
    t = t_axis(N)
    # Ambience: distant wind in a stone hall, and a faint magical hum (two close tones beating).
    wind = filt(RNG.standard_normal(N), "bandpass", [180, 900])
    wind *= 0.6 + 0.4 * np.sin(2 * np.pi * 0.13 * t + 1)
    hum = 0.5 * np.sin(2 * np.pi * 329.6 * t) + 0.5 * np.sin(2 * np.pi * 331.1 * t)
    amb_lvl = np.interp(t, [0, 1.5, 17.0, 17.1, 18.0, 24.0, 25.0], [0, 1, 1, 0.5, 0.8, 0.6, 0])
    bus += np.stack([wind, np.roll(wind, 900)], axis=1) * amb_lvl[:, None] * db(-36)
    bus += (hum * amb_lvl)[:, None] * db(-44)

    # Words lighting up: the faintest glint per English word (kept far under the voice).
    for speaker, words, at, end, zh, plan in scene.LINES:
        for w, off, row in words:
            place(bus, sparkle(0.3), at + off, float(RNG.uniform(-0.4, 0.4)), db(-40))
    for text, speaker, at, end, c in scene.ROLE_TAGS:
        place(bus, sparkle(0.6, 2.0), at, 0.3 if c[0] > 540 else -0.3, db(-30))

    # Rack-focus reveal: a low "whoom".
    n = int(1.6 * SR)
    whoom = np.sin(2 * np.pi * np.cumsum(55 * np.exp(-t_axis(n) * 0.8) + 32) / SR) * adsr(n, 0.25, 0.5)
    whoom += 0.3 * filt(RNG.standard_normal(n), "lowpass", 400) * adsr(n, 0.3, 0.4)
    place(bus, reverb(whoom, 0.3), 6.72, 0.0, db(-17))

    # Energy building: two charged tones (green / blue) and a riser into the flash.
    n = int((scene.FLASH_AT - 13.6) * SR)
    tt = t_axis(n)
    ramp = np.linspace(0, 1, n) ** 1.8
    green = np.sin(2 * np.pi * np.cumsum(164.8 * (1 + 0.004 * np.sin(2 * np.pi * 6 * tt))) / SR)
    blue = np.sin(2 * np.pi * np.cumsum(174.6 * (1 + 0.004 * np.sin(2 * np.pi * 5 * tt + 1))) / SR)
    crackle = filt(RNG.standard_normal(n) * (RNG.random(n) < 0.003), "bandpass", [2500, 6500])
    place(bus, np.stack([green * ramp + crackle * ramp * 3, blue * ramp + crackle * ramp * 3], axis=1), 13.6, 0.0, db(-26))
    rise = filt(RNG.standard_normal(n), "bandpass", [700, 6500]) * ramp ** 2
    place(bus, rise, 13.6, 0.0, db(-32))

    # The flash itself: a short magical impact with a bright shimmer.
    n = int(1.2 * SR)
    shimmer = filt(RNG.standard_normal(n), "bandpass", [3000, 12000]) * np.exp(-t_axis(n) / 0.35)
    place(bus, reverb(shimmer, 0.5), scene.FLASH_AT, 0.0, db(-22))

    # Info card: a soft magical swish as it appears; each prize letter gets a celesta ping.
    import info_card
    n = int(0.8 * SR)
    swish = filt(RNG.standard_normal(n), "bandpass", [1200, 6000]) * adsr(n, 0.25, 0.25)
    place(bus, reverb(swish, 0.4), scene.INFO_AT + 0.05, 0.0, db(-26))
    for i, note in enumerate(["E6", "G6", "B6", "E7"]):
        place(bus, celesta(m(note), 1.0), scene.INFO_AT + 1.1 + i * 0.12, -0.45 + 0.3 * i, db(-24))
        place(bus, celesta(m(note), 0.8), info_card.PRIZE_REBOUNCE_AT + i * 0.1, -0.45 + 0.3 * i, db(-31))
    return bus


# ----------------------------------------------------------------------------- voice + mix
def load_voice(name):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(ROOT / name), "-f", "f32le", "-ac", "1",
                          "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)


def active_rms(x):
    fr = int(0.05 * SR)
    r = np.sqrt(np.convolve(x ** 2, np.ones(fr) / fr, "same"))
    return np.sqrt(np.mean(x[r > r.max() * 0.1] ** 2))


def voices():
    bus = np.zeros(N)
    for name, at in (("harry_dialogue.mp3", scene.HARRY_VO_AT), ("dumbledore_dialogue.mp3", scene.DUMB_VO_AT)):
        v = filt(load_voice(name), "highpass", 70)
        v *= db(-17) / active_rms(v)
        i = int(round(at * SR))
        bus[i:i + len(v)] += v[: N - i]
    return bus


def duck_env(vo, depth_db=-9, attack=0.04, release=0.35):
    fr = int(0.02 * SR)
    r = np.sqrt(np.convolve(vo ** 2, np.ones(fr) / fr, "same"))
    on = (r > db(-45)).astype(float)
    step = 48
    idx = np.arange(0, len(on), step)
    out = np.empty(len(idx))
    ka, kr = 1 - np.exp(-step / (attack * SR)), 1 - np.exp(-step / (release * SR))
    cur = 0.0
    for j, i in enumerate(idx):
        cur += (on[i] - cur) * (ka if on[i] > cur else kr)
        out[j] = cur
    return db(depth_db * np.interp(np.arange(len(on)), idx, out))


def limit(x, ceiling_db=-1.5, window=0.006):
    """Look-ahead peak limiter: smooth gain reduction instead of waveshaping, so no added distortion.

    Gain is the running minimum of the needed gain over 2 windows, then averaged over one window:
    the result never exceeds the needed gain and moves without clicks.
    """
    from scipy.ndimage import minimum_filter1d, uniform_filter1d
    c = db(ceiling_db)
    peak = np.abs(x).max(axis=1)
    need = np.minimum(1.0, c / np.maximum(peak, 1e-9))
    L = int(window * SR)
    g = uniform_filter1d(minimum_filter1d(need, 2 * L + 1), L)
    return x * g[:, None]


def main():
    BUILD.mkdir(parents=True, exist_ok=True)
    mus, fx, vo = music(), sfx(), voices()
    duck = duck_env(vo)
    mus *= duck[:, None]
    fx_d = fx * (0.5 + 0.5 * duck)[:, None]  # ambience dips a little under the voice too
    mix = mus + fx_d + vo[:, None]
    meter = pyloudnorm.Meter(SR)
    mix *= db(TARGET_LUFS - meter.integrated_loudness(mix))
    mix = limit(mix)

    def write(name, x):
        x = np.ascontiguousarray(np.clip(x, -1, 1).astype(np.float32))
        if x.ndim == 1:
            x = np.stack([x, x], axis=1)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                        "-c:a", "pcm_s24le", str(BUILD / name)], input=x.tobytes(), check=True)

    write("stem_music.wav", mus)
    write("stem_sfx.wav", fx_d)
    write("stem_voice.wav", vo)
    write("mix.wav", mix)
    print("mix peak dBFS", 20 * np.log10(np.abs(mix).max()))


if __name__ == "__main__":
    main()

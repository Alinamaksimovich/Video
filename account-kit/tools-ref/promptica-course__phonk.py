"""Original drift-phonk bed for the PROMPTICA course reel (written for this video).

167 BPM (half-time feel 83.5, the reel's visual beat grid), C# minor:
melodic 808 cowbell riff, gliding saturated 808 bass, punchy kick, clap on
2 and 4, hats with triplet rolls. Kept "moderately dynamic": one filtered intro
bar, then the groove; a lighter bar under "сделай тише"; final hit at 15.83 s.
Deterministic. Writes assets/audio/phonk.wav. Run: python3 tools/phonk.py
"""

import os

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt

SR = 44100
DUR = 16.5
N = int(SR * DUR)
T0 = 0.023  # bar 0 starts here so bar 1 lands on the first visual downbeat (1.46 s)
Q = 0.7186 / 2  # quarter note at 167 BPM
S16 = Q / 4
BAR = 4 * Q
rng = np.random.default_rng(11)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets", "audio", "phonk.wav")


def t_axis(n):
    return np.arange(n) / SR


def add(buf, sig, at, gain=1.0):
    i = int(round(at * SR))
    if i < 0:
        sig, i = sig[-i:], 0
    j = min(len(buf), i + len(sig))
    if j > i:
        buf[i:j] += sig[: j - i] * gain


def filt(x, kind, f, order=2):
    return sosfilt(butter(order, f, btype=kind, fs=SR, output="sos"), x)


def note(name):
    names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    n, octv = name[:-1], int(name[-1])
    return 440.0 * 2 ** ((names.index(n) - 9) / 12 + (octv - 4))


# ---------------------------------------------------------------- voices
def kick():
    n = int(0.32 * SR)
    t = t_axis(n)
    f = 48 + 110 * np.exp(-t * 35)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)
    click = filt(rng.standard_normal(n), "high", 3000) * np.exp(-t * 400) * 0.3
    return np.tanh((body + click) * 1.8) * 0.9


def clap():
    n = int(0.28 * SR)
    t = t_axis(n)
    noise = filt(rng.standard_normal(n), "band", [900, 4000])
    env = np.zeros(n)
    for k, d in enumerate([0, 0.009, 0.018]):
        i = int(d * SR)
        env[i:] += np.exp(-t[: n - i] * (110 if k < 2 else 18))
    snap = filt(rng.standard_normal(n), "high", 5000) * np.exp(-t * 60) * 0.3
    return (noise * env + snap) * 0.55


def hat(open_=False):
    n = int((0.16 if open_ else 0.04) * SR)
    t = t_axis(n)
    metal = sum(np.sign(np.sin(2 * np.pi * f * t)) for f in (3140, 4170, 5310, 6820))
    x = filt(metal * 0.25 + rng.standard_normal(n) * 0.6, "high", 7000)
    return x * np.exp(-t * (20 if open_ else 110)) * 0.22


def cowbell(f, length=0.16):
    """The phonk cowbell: two detuned squares through a band-pass, quick decay."""
    n = int(length * SR)
    t = t_axis(n)
    sq = np.sign(np.sin(2 * np.pi * f * t)) + 0.8 * np.sign(np.sin(2 * np.pi * f * 1.5 * t))
    x = filt(sq, "band", [f * 0.9, f * 4.5])
    env = np.exp(-t * 16) * np.minimum(1, t * 900)
    return np.tanh(x * env * 1.4) * 0.35


def bass808(f_from, f_to, length, glide=0.06):
    n = int(length * SR)
    t = t_axis(n)
    g = np.clip(t / glide, 0, 1)
    f = f_from * (f_to / f_from) ** g
    f = f * (1 + 0.6 * np.exp(-t * 40))  # punch
    x = np.sin(2 * np.pi * np.cumsum(f) / SR)
    env = np.minimum(1, t * 300) * np.minimum(1, (length - t) / 0.03).clip(0) * np.exp(-t * 0.9)
    return np.tanh(x * env * 2.2) * 0.55  # warm saturation


def pad(freqs, length):
    n = int(length * SR)
    t = t_axis(n)
    x = np.zeros(n)
    for f in map(note, freqs):
        for d in (-0.005, 0.0, 0.005):
            x += 2 * ((t * f * (1 + d) + rng.random()) % 1.0) - 1
    x = filt(x / (len(freqs) * 3), "low", 1100)
    env = np.minimum(1, t / 0.3) * np.minimum(1, (length - t) / 0.3).clip(0)
    return x * env


def riser(length):
    n = int(length * SR)
    t = t_axis(n)
    x = filt(rng.standard_normal(n), "band", [800, 7000]) * (t / length) ** 2.5
    return x * 0.25


# ---------------------------------------------------------------- arrangement
# C#m – A – F#m – G#  (one bar each)
ROOTS = ["C#1", "A0", "F#1", "G#1"]
PADS = [["C#3", "E3", "G#3"], ["A2", "C#3", "E3"], ["F#2", "A2", "C#3"], ["G#2", "C3", "D#3"]]
# two-bar cowbell riff, 16ths (None = rest)
RIFF = [
    "C#5", None, "E5", None, "G#5", None, "F#5", "E5", None, "C#5", None, "E5", "F#5", None, "E5", None,
    "C#5", None, "E5", None, "B4", None, "A4", None, "G#4", None, "A4", "B4", None, "C#5", None, None,
]
QUIET_BAR = 7  # bar under "сделай тише": drums thin out
END_BAR = 11  # 15.83 s: final hit, then ring out


def build():
    drums = np.zeros(N)
    bass = np.zeros(N)
    bell = np.zeros(N)
    pads = np.zeros(N)
    fx = np.zeros(N)

    for b in range(12):
        bt = T0 + b * BAR
        chord = b % 4
        intro = b == 0
        quiet = b == QUIET_BAR
        if b == END_BAR:
            add(drums, kick(), bt, 1.0)
            add(bass, bass808(note(ROOTS[0]) * 2, note(ROOTS[0]) * 2, 0.62), bt, 1.0)
            add(bell, cowbell(note("C#5"), 0.4), bt, 0.9)
            add(pads, pad(PADS[0], 0.62), bt, 0.25)
            break

        # pad under everything (dark, quiet)
        add(pads, pad(PADS[chord], BAR), bt, 0.18 if not intro else 0.12)

        # cowbell riff
        for s, nm in enumerate(RIFF[(b % 2) * 16 : (b % 2) * 16 + 16]):
            if nm:
                add(bell, cowbell(note(nm)), bt + s * S16, 0.55 if intro else (0.6 if quiet else 0.85))

        if intro:
            add(fx, riser(BAR), bt, 1.0)
            continue

        # drums
        kicks = [0, 10] if b % 2 == 0 else [0, 7, 10]
        if quiet:
            kicks = [0]
        for s in kicks:
            add(drums, kick(), bt + s * S16, 1.0)
        for s in (4, 12):
            add(drums, clap(), bt + s * S16, 0.85 if not quiet else 0.5)
        for s in range(0, 16, 2):
            add(drums, hat(open_=(s % 8 == 6)), bt + s * S16, 0.9 if not quiet else 0.5)
        if b % 2 == 1 and not quiet:  # triplet roll into the next bar
            for k in range(6):
                add(drums, hat(), bt + 14 * S16 + k * (2 * S16 / 6), 0.6 + 0.06 * k)

        # 808: root on the one, glide up an octave on step 10 every other bar
        r = note(ROOTS[chord]) * 2
        if b % 2 == 0:
            add(bass, bass808(r, r, 10 * S16), bt, 1.0)
            add(bass, bass808(r, r * 2, 6 * S16, glide=0.08), bt + 10 * S16, 0.9)
        else:
            add(bass, bass808(r, r, 7 * S16), bt, 1.0)
            add(bass, bass808(r * 1.5, r, 9 * S16, glide=0.1), bt + 7 * S16, 0.85)

    # sidechain pump on kicks (subtle)
    env = np.ones(N)
    for b in range(1, END_BAR):
        for s in ([0, 10] if b % 2 == 0 else [0, 7, 10]):
            i = int((T0 + b * BAR + s * S16) * SR)
            m = min(N - i, int(0.18 * SR))
            if m > 0:
                env[i : i + m] = np.minimum(env[i : i + m], 0.55 + 0.45 * np.linspace(0, 1, m) ** 0.7)

    bell_wet = bell + 0.35 * np.concatenate([np.zeros(int(Q * 0.75 * SR)), bell])[:N]  # dotted-8th echo
    mix = drums + bass * env + filt(bell_wet, "high", 300) * (0.6 + 0.4 * env) + pads * env + fx
    # intro bar heard through a low-pass, opening into bar 1
    lp = filt(mix, "low", 900, order=2)
    t = t_axis(N)
    w = np.clip((t - (T0 + BAR - 0.25)) / 0.25, 0, 1)
    mix = lp * (1 - w) + mix * w
    mix *= np.clip((DUR - t) / 0.6, 0, 1)
    mix = np.tanh(mix * 1.1)
    return mix / np.max(np.abs(mix)) * 0.89


if __name__ == "__main__":
    sf.write(OUT, build().astype(np.float32), SR)
    print("ok", OUT)

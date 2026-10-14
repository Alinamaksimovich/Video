"""Original deep-house bed for the WeArt canvas reel (written for this video).

109.09 BPM (bar = 2.2 s), A minor: Am7 - Fmaj7 - Cmaj7 - G6. The grid is locked to
the voice: the drop lands on 3.82 s ("I was made in a few clicks"), bar lines fall
on "Canvas" (6.02), "Drop a photo" (8.22) and "all in one place" (12.62).
Soft by design: it sits ~15 dB under speech. Pre-drop: pad swell + filtered chords;
drop: kick, offbeat bass, chord stabs, shaker; the arp joins at 6.02, a lead pad at
10.42; fades out over the last second. Deterministic.
Writes assets/audio/house.wav. Run: python3 tools/house.py
"""

import os

import numpy as np
import soundfile as sf
from scipy.signal import butter, fftconvolve, sosfilt

SR = 44100
DUR = 15.04
N = int(SR * DUR)
DROP = 3.82
BAR = 2.2
Q = BAR / 4
S16 = Q / 4
rng = np.random.default_rng(5)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets", "audio", "house.wav")


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


def hz(name):
    names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    return 440.0 * 2 ** ((names.index(name[:-1]) - 9) / 12 + (int(name[-1]) - 4))


def saw(f, n, phase=0.0):
    return 2 * ((t_axis(n) * f + phase) % 1.0) - 1


def reverb(x, secs=1.4, wet=0.3):
    n = int(secs * SR)
    ir = filt(rng.standard_normal(n), "low", 5500) * np.exp(-t_axis(n) * 5 / secs)
    ir /= np.sqrt(np.sum(ir**2))
    return x * (1 - wet) + fftconvolve(x, ir)[: len(x)] * wet


# ---------------------------------------------------------------- drums
def kick():
    n = int(0.3 * SR)
    t = t_axis(n)
    f = 46 + 120 * np.exp(-t * 38)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 10)
    click = filt(rng.standard_normal(n), "high", 2500) * np.exp(-t * 450) * 0.2
    return np.tanh((body + click) * 1.7) * 0.85


def clap():
    n = int(0.28 * SR)
    t = t_axis(n)
    noise = filt(rng.standard_normal(n), "band", [1000, 4200])
    env = np.zeros(n)
    for k, d in enumerate([0, 0.010, 0.021]):
        i = int(d * SR)
        env[i:] += np.exp(-t[: n - i] * (110 if k < 2 else 20))
    return noise * env * 0.45


def hat(open_=False):
    n = int((0.2 if open_ else 0.04) * SR)
    t = t_axis(n)
    return filt(rng.standard_normal(n), "high", 7500) * np.exp(-t * (14 if open_ else 120)) * 0.2


def shaker():
    n = int(0.06 * SR)
    t = t_axis(n)
    return filt(rng.standard_normal(n), "band", [4500, 11000]) * np.exp(-t * 60) * 0.12


# ---------------------------------------------------------------- tonal
ROOTS = ["A1", "F1", "C2", "G1"]
CHORDS = [["A3", "C4", "E4", "G4"], ["F3", "A3", "C4", "E4"], ["C3", "E3", "G3", "B3"], ["G3", "B3", "D4", "E4"]]
ARP = [0, 2, 1, 3, 2, 1, 3, 2]


def bass(f, length):
    n = int(length * SR)
    t = t_axis(n)
    x = np.sin(2 * np.pi * f * t) + 0.35 * saw(f, n)
    x = filt(x, "low", 420)
    env = np.minimum(1, t * 250) * np.exp(-t * 3.2) * np.minimum(1, (length - t) / 0.02).clip(0)
    return np.tanh(x * env * 1.4) * 0.5


def stab(names, length=0.4):
    n = int(length * SR)
    t = t_axis(n)
    x = sum(saw(hz(nm), n, rng.random()) + saw(hz(nm) * 1.005, n, rng.random()) for nm in names)
    cut = 900 + 2200 * np.exp(-t * 7)
    out = np.zeros(n)
    for lo, hi in ((0, n // 3), (n // 3, 2 * n // 3), (2 * n // 3, n)):  # cheap moving filter
        out[lo:hi] = filt(x, "low", float(cut[lo]))[lo:hi]
    return out / (2 * len(names)) * np.exp(-t * 6.5) * 0.55


def pluck(f, length=0.2):
    n = int(length * SR)
    t = t_axis(n)
    x = np.sign(np.sin(2 * np.pi * f * t)) * 0.4 + saw(f, n) * 0.6
    return filt(x, "low", 3200) * np.exp(-t * 16) * 0.22


def pad(names, length, cut=1300):
    n = int(length * SR)
    t = t_axis(n)
    x = sum(saw(hz(nm) / 2, n, rng.random()) for nm in names for _ in range(2))
    x = filt(x / (2 * len(names)), "low", cut)
    return x * np.minimum(1, t / 0.4) * np.minimum(1, (length - t) / 0.4).clip(0) * 0.5


def riser(length):
    n = int(length * SR)
    t = t_axis(n)
    noise = filt(rng.standard_normal(n), "band", [500, 8000]) * (t / length) ** 2.2
    return noise * 0.3


# ---------------------------------------------------------------- arrangement
def build():
    drums, bs, tone, fx = (np.zeros(N) for _ in range(4))
    t = t_axis(N)

    # swell before the drop
    add(tone, pad(CHORDS[0], DROP + 0.4, cut=700), 0.0, 0.7)
    add(fx, riser(DROP - 1.4), 1.4, 0.8)
    for k in range(4):  # filtered chord pulses in the bar before the drop
        add(tone, stab(CHORDS[0], 0.5) * 0.7, DROP - BAR + k * Q, 0.6)
    for s in range(8):
        add(drums, hat(), DROP - BAR + s * 2 * S16 + S16, 0.5 + 0.06 * s)

    for b in range(0, 6):
        bt = DROP + b * BAR
        c = b % 4
        if bt >= DUR:
            break
        for k in range(4):  # four on the floor
            add(drums, kick(), bt + k * Q, 1.0)
        for k in (1, 3):
            add(drums, clap(), bt + k * Q, 0.8)
        for k in range(4):  # offbeat open hats + 16th shaker
            add(drums, hat(open_=True), bt + k * Q + Q / 2, 0.8)
        for s in range(16):
            add(drums, shaker(), bt + s * S16, 0.9 if s % 2 else 0.6)
        r = hz(ROOTS[c]) * 2
        for k in range(4):  # house offbeat bass
            add(bs, bass(r, Q * 0.45), bt + k * Q + Q / 2, 1.0)
        add(bs, bass(r / 2, Q * 1.3), bt, 0.9)
        add(tone, stab(CHORDS[c]), bt + Q * 0.75, 0.9)  # syncopated stabs
        add(tone, stab(CHORDS[c]), bt + Q * 2.75, 0.8)
        add(tone, pad(CHORDS[c], BAR, 1100), bt, 0.45)
        if b >= 1:  # arp joins on "Canvas"
            for s in range(16):
                add(tone, pluck(hz(CHORDS[c][ARP[s % 8]]) * 2), bt + s * S16, 0.5 if s % 4 == 0 else 0.3)
        if b >= 3:  # lead pad lifts the last phrase
            add(tone, pad([CHORDS[c][1], CHORDS[c][3]], BAR, 2400), bt, 0.35)

    # sidechain pump from the kicks
    env = np.ones(N)
    for b in range(0, 6):
        for k in range(4):
            i = int((DROP + b * BAR + k * Q) * SR)
            m = int(0.22 * SR)
            if i < N:
                env[i : min(N, i + m)] = np.minimum(env[i : min(N, i + m)], (0.45 + 0.55 * np.linspace(0, 1, m) ** 0.7)[: N - i])

    tone = reverb(tone, 1.3, 0.28)
    mix = drums + bs * env + tone * env + fx
    mix *= np.clip((DUR - t) / 1.0, 0, 1) ** 1.4  # fade out over the last second
    mix = np.tanh(mix * 1.1)
    return mix / np.max(np.abs(mix)) * 0.89


if __name__ == "__main__":
    sf.write(OUT, build().astype(np.float32), SR)
    print("ok", OUT)

"""Original drum & bass bed for the PROMPTICA 15 s presentation (written for this video).

174 BPM, F minor (Fm - Db - Ab - Eb). Bar 0: filtered intro with a riser and a
snare roll; drop on bar 1 (1.379 s) with a two-step break, rolling reese bass +
sub, chord stabs and a pluck arp; a one-beat stop before the end hit on bar 9
(12.414 s), then the tail rings out to 15 s. Deterministic.
Writes assets/audio/music.wav. Run: python3 tools/dnb.py
"""

import os

import numpy as np
import soundfile as sf
from scipy.signal import butter, fftconvolve, sosfilt

SR = 44100
DUR = 15.0
N = int(SR * DUR)
BPM = 174
Q = 60 / BPM
S16 = Q / 4
BAR = 4 * Q
END_BAR = 9
rng = np.random.default_rng(23)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets", "audio", "music.wav")


def t_axis(n):
    return np.arange(n) / SR


def add(buf, sig, at, gain=1.0):
    i = int(round(at * SR))
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


def reverb(x, secs=1.2, wet=0.25):
    n = int(secs * SR)
    ir = filt(rng.standard_normal(n), "low", 6000) * np.exp(-t_axis(n) * 5 / secs)
    ir /= np.sqrt(np.sum(ir**2))
    return x * (1 - wet) + fftconvolve(x, ir)[: len(x)] * wet


# ---------------------------------------------------------------- drums
def kick():
    n = int(0.25 * SR)
    t = t_axis(n)
    f = 52 + 140 * np.exp(-t * 45)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 14)
    click = filt(rng.standard_normal(n), "high", 2500) * np.exp(-t * 500) * 0.4
    return np.tanh((body + click) * 2.0) * 0.9


def snare():
    n = int(0.3 * SR)
    t = t_axis(n)
    tone = np.sin(2 * np.pi * 185 * t) * np.exp(-t * 30) * 0.6
    noise = filt(rng.standard_normal(n), "band", [1200, 9000]) * np.exp(-t * 18)
    return np.tanh((tone + noise) * 1.6) * 0.6


def ghost():
    return snare() * 0.22


def hat(open_=False):
    n = int((0.14 if open_ else 0.035) * SR)
    t = t_axis(n)
    return filt(rng.standard_normal(n), "high", 8000) * np.exp(-t * (22 if open_ else 140)) * 0.25


def ride():
    n = int(0.4 * SR)
    t = t_axis(n)
    metal = sum(np.sin(2 * np.pi * f * t) for f in (3200, 4710, 6390, 8120))
    return filt(metal, "high", 3000) * np.exp(-t * 9) * 0.05


# ---------------------------------------------------------------- tonal
ROOTS = ["F1", "C#1", "G#1", "D#1"]
CHORDS = [["F3", "G#3", "C4"], ["C#3", "F3", "G#3"], ["G#3", "C4", "D#4"], ["D#3", "G3", "A#3"]]
ARP = [0, 1, 2, 1, 2, 0, 1, 2]


def reese(f, length, cut):
    n = int(length * SR)
    x = saw(f, n) + saw(f * 1.007, n, 0.3) + saw(f * 0.993, n, 0.6)
    x = filt(x / 3, "low", cut)
    env = np.minimum(1, t_axis(n) * 200) * np.minimum(1, (length - t_axis(n)) / 0.02).clip(0)
    return np.tanh(x * env * 1.8) * 0.45


def sub(f, length):
    n = int(length * SR)
    t = t_axis(n)
    env = np.minimum(1, t * 200) * np.minimum(1, (length - t) / 0.02).clip(0)
    return np.sin(2 * np.pi * f * t) * env * 0.6


def stab(names, length=0.22):
    n = int(length * SR)
    t = t_axis(n)
    x = sum(saw(hz(nm), n, rng.random()) + saw(hz(nm) * 1.004, n, rng.random()) for nm in names)
    return filt(x / (2 * len(names)), "low", 3500) * np.exp(-t * 9) * 0.5


def pluck(f, length=0.18):
    n = int(length * SR)
    t = t_axis(n)
    x = np.sign(np.sin(2 * np.pi * f * t)) * 0.5 + saw(f, n) * 0.5
    return filt(x, "low", 4200) * np.exp(-t * 20) * 0.3


def pad(names, length):
    n = int(length * SR)
    t = t_axis(n)
    x = sum(saw(hz(nm) / 2, n, rng.random()) for nm in names for _ in range(2))
    x = filt(x / (2 * len(names)), "low", 1500)
    return x * np.minimum(1, t / 0.3) * np.minimum(1, (length - t) / 0.3).clip(0) * 0.4


def riser(length):
    n = int(length * SR)
    t = t_axis(n)
    f = 200 * 16 ** (t / length)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * (t / length) ** 2 * 0.2
    noise = filt(rng.standard_normal(n), "band", [600, 9000]) * (t / length) ** 2.4 * 0.35
    return tone + noise


def impact():
    n = int(2.6 * SR)
    t = t_axis(n)
    f = 40 + 90 * np.exp(-t * 16)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.8)
    crack = filt(rng.standard_normal(n), "low", 6000) * np.exp(-t * 10) * 0.5
    return reverb(np.tanh((boom + crack) * 1.5), 2.2, 0.35) * 0.9


# ---------------------------------------------------------------- arrangement
def build():
    drums, bass, music, fx = (np.zeros(N) for _ in range(4))
    stop = END_BAR * BAR - Q  # one-beat stop before the end hit

    # intro bar: pad + riser + snare roll, all filtered
    add(music, pad(CHORDS[0], BAR), 0.0, 0.8)
    add(fx, riser(BAR), 0.0, 1.0)
    for k in range(16):
        g = 0.15 + 0.85 * (k / 16) ** 2
        add(fx, snare(), 2 * Q + k * (2 * Q / 16), 0.45 * g)

    for b in range(1, END_BAR):
        bt = b * BAR
        c = (b - 1) % 4
        # two-step break: kick 1 + 3&, snare 2 + 4, ghosts, 16th hats
        for s in (0, 10):
            add(drums, kick(), bt + s * S16, 1.0)
        for s in (4, 12):
            add(drums, snare(), bt + s * S16, 1.0)
        for s in (7, 9, 15):
            add(drums, ghost(), bt + s * S16, 1.0)
        for s in range(16):
            add(drums, hat(open_=(s % 8 == 2)), bt + s * S16, 0.9 if s % 2 == 0 else 0.5)
        add(drums, ride(), bt, 1.0)
        add(drums, ride(), bt + 2 * Q, 0.7)
        # bass: rolling reese on 8ths with a moving filter + sub on the root
        r = hz(ROOTS[c]) * 2
        add(bass, sub(r, BAR * 0.98), bt, 1.0)
        for e in range(8):
            cut = 300 + 900 * (0.5 + 0.5 * np.sin(2 * np.pi * (b * 8 + e) / 16))
            add(bass, reese(r * (2 if e in (3, 6) else 1), Q / 2 * 0.95, cut), bt + e * Q / 2, 0.9)
        # stabs on the one and the "2&", arp on 16ths
        add(music, stab(CHORDS[c]), bt, 0.9)
        add(music, stab(CHORDS[c]), bt + 6 * S16, 0.7)
        for s in range(16):
            nm = CHORDS[c][ARP[s % 8]]
            add(music, pluck(hz(nm) * 2), bt + s * S16, 0.55 if s % 4 == 0 else 0.35)
        add(music, pad(CHORDS[c], BAR), bt, 0.35)

    # cut everything for the stop beat
    t = t_axis(N)
    gap = np.where((t >= stop) & (t < END_BAR * BAR), 0.0, 1.0)
    gap = np.convolve(gap, np.ones(int(0.004 * SR)) / int(0.004 * SR), mode="same")
    drums, bass, music = drums * gap, bass * gap, music * gap
    add(fx, riser(Q), stop, 0.8)

    # end hit on bar 9
    et = END_BAR * BAR
    add(fx, impact(), et, 1.0)
    add(music, reverb(stab(CHORDS[0], 1.2), 2.5, 0.5), et, 1.0)
    add(bass, sub(hz(ROOTS[0]) * 2, 1.4) * np.exp(-t_axis(int(1.4 * SR)) * 1.5), et, 1.0)
    add(drums, kick(), et, 1.0)

    # sidechain pump from the kicks
    env = np.ones(N)
    for b in range(1, END_BAR):
        for s in (0, 10):
            i = int((b * BAR + s * S16) * SR)
            m = int(0.16 * SR)
            env[i : i + m] = np.minimum(env[i : i + m], 0.5 + 0.5 * np.linspace(0, 1, m) ** 0.6)

    music = reverb(music, 1.0, 0.22)
    mix = drums + bass * env + music * env + fx
    # intro heard through a low-pass that opens on the drop
    lp = filt(mix, "low", 700)
    w = np.clip((t - (BAR - 0.3)) / 0.3, 0, 1)
    mix = lp * (1 - w) + mix * w
    mix *= np.clip((DUR - t) / 0.8, 0, 1)
    mix = np.tanh(mix * 1.15)
    return mix / np.max(np.abs(mix)) * 0.89


if __name__ == "__main__":
    sf.write(OUT, build().astype(np.float32), SR)
    print("ok", OUT)

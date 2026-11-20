"""Original neo-soul / downtempo bed for the WeArt lipstick creative (written for this video).

84 BPM, lazy swung 16ths. Intro (0-11.8 s, prompt + storyboard): filtered electric piano and soft hats.
Gray street (11.8-21.5 s): kick, rim, sub, minor chords (Bbm9 - Gbmaj7 - Ebm9 - F7sus).
Golden turn (21.5 s): the harmony brightens to Db major (Dbmaj9 - Gbmaj9 - Bbm9 - Absus), full drums,
bell melody. End card (26.9 s): final Dbmaj9 swell and tail. Deterministic. Writes assets/audio/music.wav.
"""

import os

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt, lfilter

SR = 44100
DUR = 29.0
N = int(SR * DUR)
BPM = 84
Q = 60 / BPM
BAR = 4 * Q
SW = 0.1 * Q
GOLD = 21.5
STREET = 11.8
END = 26.9
rng = np.random.default_rng(84)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "audio", "music.wav")


def ta(n):
    return np.arange(n) / SR


def add(buf, sig, at, g=1.0):
    i = int(round(at * SR))
    if i >= len(buf):
        return
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i] * g


def hz(m):
    return 440 * 2 ** ((m - 69) / 12)


def lp(x, f, o=2):
    return sosfilt(butter(o, f, "low", fs=SR, output="sos"), x)


def hp(x, f, o=2):
    return sosfilt(butter(o, f, "high", fs=SR, output="sos"), x)


def bp(x, a, b, o=2):
    return sosfilt(butter(o, [a, b], "band", fs=SR, output="sos"), x)


def s16(t0, step):
    return t0 + step * Q / 4 + (SW if step % 2 else 0)


# ---- instruments
def epiano(notes, dur, bright=1.0):
    n = int(dur * SR)
    t = ta(n)
    s = np.zeros(n)
    for k, m in enumerate(notes):
        f = hz(m)
        mod = np.sin(2 * np.pi * f * 14 * t) * 1.2 * np.exp(-t * 9) * bright
        s += np.sin(2 * np.pi * f * t + mod) * np.exp(-t * 1.6) * (0.9 if k else 1.0)
        s += 0.25 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 3)
    trem = 1 + 0.12 * np.sin(2 * np.pi * 4.5 * t)
    env = np.minimum(1, t / 0.006) * np.minimum(1, (dur - t) / 0.08).clip(0, 1)
    return s * trem * env * 0.05


def kick():
    n = int(0.5 * SR)
    t = ta(n)
    f = 48 + 90 * np.exp(-t * 28)
    return np.tanh(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6) * 1.5) * 0.8


def snare():
    n = int(0.3 * SR)
    t = ta(n)
    body = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30) * 0.4
    nz = bp(rng.standard_normal(n), 1500, 7000) * np.exp(-t * 18) * 0.35
    return (body + nz) * 0.7


def rim():
    n = int(0.06 * SR)
    t = ta(n)
    return (np.sin(2 * np.pi * 1700 * t) * np.exp(-t * 110) + bp(rng.standard_normal(n), 2500, 6000) * np.exp(-t * 150) * 0.3) * 0.22


def hat(op=False):
    n = int((0.18 if op else 0.04) * SR)
    t = ta(n)
    return hp(rng.standard_normal(n), 8000, 3) * np.exp(-t * (18 if op else 110)) * (0.12 if op else 0.09)


def sub(m, dur):
    n = int(dur * SR)
    t = ta(n)
    ph = 2 * np.pi * hz(m) * t
    env = np.minimum(1, t / 0.01) * np.minimum(1, (dur - t) / 0.05).clip(0, 1)
    return np.tanh((np.sin(ph) + 0.2 * np.sin(2 * ph)) * 1.3) * env * 0.38


def bell(m, dur):
    n = int(dur * SR)
    t = ta(n)
    f = hz(m)
    s = np.sin(2 * np.pi * f * t + 2.0 * np.sin(2 * np.pi * f * 3.5 * t) * np.exp(-t * 4)) * np.exp(-t * 2.2)
    return s * np.minimum(1, t / 0.003) * 0.07


def vinyl(n):
    s = lp(rng.standard_normal(n), 3000) * 0.006
    cr = (rng.random(n) > 0.9993) * rng.standard_normal(n) * 0.08
    return s + hp(cr, 2000)


MINOR = [([58, 61, 65, 68, 72], 34), ([54, 58, 61, 65], 30), ([51, 54, 58, 61, 65], 27), ([53, 58, 60, 63], 29)]
MAJOR = [([61, 65, 68, 72, 75], 37), ([54, 58, 61, 65, 68], 30), ([58, 61, 65, 68, 72], 34), ([56, 61, 63, 68], 32)]

if __name__ == "__main__":
    keys = np.zeros(N)
    drums = np.zeros(N)
    bass = np.zeros(N)
    mel = np.zeros(N)
    K, S = kick(), snare()

    nb = int(DUR / BAR) + 1
    for b in range(nb):
        t0 = b * BAR
        if t0 >= END:
            break
        gold = t0 >= GOLD - 0.01
        prog = MAJOR if gold else MINOR
        ch, root = prog[b % 4]
        # keys: chord on 1 and a push on the "and" of 3
        add(keys, epiano(ch, min(2.4 * Q, END - t0), 1.3 if gold else 0.8), t0)
        if s16(t0, 10) < END:
            add(keys, epiano(ch[1:], min(1.4 * Q, END - s16(t0, 10)), 1.0), s16(t0, 10), 0.6)
        for st in range(16):
            at = s16(t0, st)
            if at >= END:
                break
            if st % 2 == 0:
                add(drums, hat(), at, 0.7 + 0.3 * (st % 4 == 2))
            if t0 >= STREET - 0.01:
                if st in (0, 7, 10) or (gold and st == 13):
                    add(drums, K, at)
                if st in (4, 12):
                    add(drums, S if gold else rim(), at, 1.0 if gold else 1.6)
                if gold and st in (6, 14):
                    add(drums, hat(True), at)
        if t0 >= STREET - 0.01:
            for st, ln in [(0, 6), (7, 3), (10, 6)]:
                at = s16(t0, st)
                if at < END:
                    add(bass, sub(root, min(ln * Q / 4, END - at)), at)
    # bell melody over the golden part
    MEL = [(0, 77, 3), (3, 80, 2), (6, 82, 4), (10, 80, 2), (12, 77, 4)]
    b = int(np.ceil(GOLD / BAR))
    while b * BAR < END - 0.1:
        for st, m, ln in MEL:
            at = s16(b * BAR, st)
            if at < END:
                add(mel, bell(m, ln * Q / 4 * 2.5), at)
        b += 1
    # end card swell
    add(keys, epiano([49, 61, 65, 68, 72, 75], 2.1, 1.0), END, 1.3)
    add(mel, bell(80, 2.0), END + 0.05, 1.2)
    add(bass, sub(25, 1.8), END, 1.0)
    add(drums, K, END)

    # intro is filtered (prompt + storyboard), opens at the street
    mix = keys + bass + mel * 0.9
    cut = int(STREET * SR)
    sweep = lp(mix[:cut], 1400, 2)
    mix[:cut] = sweep
    mix += drums * 0.85
    mix += vinyl(N)
    rev = lfilter([0.22], [1, -0.85], lp(mix, 5000))
    mix = mix + 0.18 * np.roll(rev, int(0.03 * SR))
    fi = int(0.4 * SR)
    mix[:fi] *= np.linspace(0, 1, fi)
    fo = int(0.6 * SR)
    mix[-fo:] *= np.linspace(1, 0, fo)
    mix = np.tanh(mix * 1.3)
    mix /= np.abs(mix).max() / 0.89
    L = mix
    R = np.roll(mix, int(0.008 * SR)) * 0.6 + mix * 0.4
    sf.write(OUT, np.stack([L, R], 1).astype(np.float32), SR)
    print("ok", OUT)

"""Original UK garage / 2-step bed for the PROMPTICA cases video (written for this video).

132 BPM, swung 16ths, F minor (Fm9 - Dbmaj7 - Ebsus - Cm7). Bar 0: low-passed intro
with organ stabs and a riser; drop on bar 1 (1.818 s): skippy 2-step kick, clap on 2
and 4, shuffled hats, rubbery sub bass, organ chord stabs and formant "vocal" chops.
One stop half-bar before the end card (bar 7 beat 2 = 13.636 s), then an end hit and tail.
Deterministic. Writes assets/audio/music.wav. Run: python3 tools/garage.py
"""

import os

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt, lfilter

SR = 44100
DUR = 15.0
N = int(SR * DUR)
BPM = 132
Q = 60 / BPM
BAR = 4 * Q
SWING = 0.12 * Q  # late offbeat 16ths
END = 7 * BAR + 2 * Q
rng = np.random.default_rng(132)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets", "audio", "music.wav")


def t_axis(n):
    return np.arange(n) / SR


def add(buf, sig, at, gain=1.0):
    i = int(round(at * SR))
    if i < 0:
        sig = sig[-i:]
        i = 0
    j = min(len(buf), i + len(sig))
    if j > i:
        buf[i:j] += sig[: j - i] * gain


def s16(bar, step):
    """time of 16th `step` (0-15) in `bar`, with garage swing on odd steps"""
    return bar * BAR + step * Q / 4 + (SWING if step % 2 else 0)


def hz(m):
    return 440 * 2 ** ((m - 69) / 12)


def lp(x, f, order=2):
    return sosfilt(butter(order, f, "low", fs=SR, output="sos"), x)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, "high", fs=SR, output="sos"), x)


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], "band", fs=SR, output="sos"), x)


# ---------- drums ----------
def kick():
    n = int(0.42 * SR)
    t = t_axis(n)
    f = 46 + 120 * np.exp(-t * 32)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t * 7.5)
    click = hp(rng.standard_normal(n), 2500) * np.exp(-t * 300) * 0.3
    return np.tanh((body + click) * 1.6) * 0.95


def clap():
    n = int(0.35 * SR)
    t = t_axis(n)
    noise = bp(rng.standard_normal(n), 900, 5200)
    env = np.zeros(n)
    for k, d in enumerate([0, 0.009, 0.018, 0.027]):
        i = int(d * SR)
        env[i:] += np.exp(-(t[: n - i]) * (160 if k < 3 else 22))
    return noise * env * 0.42


def rim():
    n = int(0.08 * SR)
    t = t_axis(n)
    s = np.sin(2 * np.pi * 1650 * t) * np.exp(-t * 90) + bp(rng.standard_normal(n), 2000, 6000) * np.exp(-t * 140) * 0.4
    return s * 0.3


def hat(open_=False):
    n = int((0.22 if open_ else 0.05) * SR)
    t = t_axis(n)
    s = hp(rng.standard_normal(n), 7500, 3)
    return s * np.exp(-t * (16 if open_ else 95)) * (0.2 if open_ else 0.16)


def shaker():
    n = int(0.07 * SR)
    t = t_axis(n)
    return bp(rng.standard_normal(n), 4000, 11000) * np.sin(np.pi * t / t[-1]) ** 2 * 0.07


# ---------- tonal ----------
CHORDS = [  # one per bar, midi notes
    [53, 56, 60, 63, 67],  # Fm9
    [49, 53, 56, 60],  # Dbmaj7
    [51, 56, 58, 63],  # Ebsus
    [48, 51, 55, 58],  # Cm7
]
ROOTS = [29, 25, 27, 24]  # F1 Db1 Eb1 C1


def organ(notes, dur):
    n = int(dur * SR)
    t = t_axis(n)
    s = np.zeros(n)
    for m in notes:
        f = hz(m)
        for h, a in [(1, 1.0), (2, 0.5), (3, 0.28), (4, 0.16), (6, 0.08)]:
            s += np.sin(2 * np.pi * f * h * t + m) * a
    env = np.minimum(1, t / 0.004) * np.exp(-t * 9)
    return lp(s * env, 3200) * 0.05


def sub(m, dur, slide_from=None):
    n = int(dur * SR)
    t = t_axis(n)
    f = np.full(n, hz(m))
    if slide_from is not None:
        f = hz(m) + (hz(slide_from) - hz(m)) * np.exp(-t * 40)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) + 0.35 * np.sin(2 * ph) * np.exp(-t * 6)
    env = np.minimum(1, t / 0.005) * np.minimum(1, (dur - t) / 0.02).clip(0, 1)
    return np.tanh(s * 1.4) * env * 0.42


FORMANTS = {"oo": (300, 870, 2240), "ah": (730, 1090, 2440), "eh": (530, 1840, 2480), "ee": (270, 2290, 3010)}


def vox(m, dur, vowel):
    """formant-filtered saw = a pitched vocal chop"""
    n = int(dur * SR)
    t = t_axis(n)
    f = hz(m) * (1 + 0.006 * np.sin(2 * np.pi * 5.5 * t))
    ph = np.cumsum(f) / SR
    saw = 2 * (ph % 1) - 1
    s = np.zeros(n)
    for k, fc in enumerate(FORMANTS[vowel]):
        s += bp(saw, fc * 0.88, fc * 1.12) * [1.0, 0.6, 0.3][k]
    env = np.minimum(1, t / 0.01) * np.minimum(1, (dur - t) / 0.03).clip(0, 1)
    return s * env * 0.32


def riser(dur):
    n = int(dur * SR)
    t = t_axis(n)
    out = np.zeros(n)
    noise = rng.standard_normal(n)
    # sweep a band upward block by block
    blk = 1024
    for i in range(0, n, blk):
        fr = i / n
        lo = 300 + 6000 * fr**2
        seg = noise[max(0, i - 4096) : i + blk]
        y = bp(seg, lo, lo * 1.6 + 200)[-min(blk, n - i) :]
        out[i : i + len(y)] = y
    return out * (t / dur) ** 2 * 0.25


def end_hit():
    n = int(1.4 * SR)
    t = t_axis(n)
    k = np.zeros(n)
    kk = kick()
    k[: len(kk)] += kk
    cr = hp(rng.standard_normal(n), 5000) * np.exp(-t * 3.2) * 0.12
    ch = sum(np.sin(2 * np.pi * hz(m) * t) for m in [41, 53, 56, 60, 63, 67]) * np.exp(-t * 2.2) * 0.05
    sb = np.sin(2 * np.pi * hz(29) * t) * np.exp(-t * 2.5) * 0.4
    return k + cr + ch + sb


if __name__ == "__main__":
    drums = np.zeros(N)
    bass = np.zeros(N)
    keys = np.zeros(N)
    voc = np.zeros(N)
    fx = np.zeros(N)
    K, C, R = kick(), clap(), rim()

    # 2-step kick: 1, then the swung "a" of beat 2 (step 7) and step 10 on alternate bars
    KICK_A = [0, 7, 10]
    KICK_B = [0, 7, 11, 14]
    for bar in range(1, 8):
        last = bar == 7
        for st in (KICK_A if bar % 2 else KICK_B):
            if s16(bar, st) < END - 0.01:
                add(drums, K, s16(bar, st))
        for st in (4, 12):
            if s16(bar, st) < END - 0.01:
                add(drums, C, s16(bar, st))
        for st in range(16):
            if s16(bar, st) >= END - 0.01:
                continue
            if st % 4 == 2:
                add(drums, hat(True), s16(bar, st))
            elif st % 2:
                add(drums, hat(), s16(bar, st), 0.8 + 0.4 * (st % 4 == 3))
            add(drums, shaker(), s16(bar, st), 0.6 + 0.5 * (st % 2))
        for st in (3, 14):
            if not last:
                add(drums, R, s16(bar, st))

    # intro bar: just rim + hats hint + riser
    for st in (2, 6, 10, 14):
        add(drums, hat(), s16(0, st), 0.6)
    add(fx, riser(BAR), 0)
    add(fx, riser(2 * Q), END - 2 * Q, 0.8)

    # organ stabs: garage offbeat rhythm
    STAB = [3, 6, 10, 13]
    for bar in range(0, 8):
        ch = CHORDS[bar % 4]
        for st in STAB:
            at = s16(bar, st)
            if at < END - 0.01:
                add(keys, organ(ch, 0.24), at)

    # sub bass: syncopated, octave slides
    BASS = [(0, 3, 0), (3, 2, 12), (6, 4, 0), (11, 2, 12), (13, 3, 0)]
    for bar in range(1, 8):
        r = ROOTS[bar % 4]
        for st, ln, oc in BASS:
            at = s16(bar, st)
            if at < END - 0.01:
                d = min(ln * Q / 4, END - at)
                add(bass, sub(r + 12 + oc, d, slide_from=(r + 24 if oc else None)), at)

    # vocal chops: short call each bar, answer every other
    CALL = [(0, 2, 72, "oo"), (2, 1, 75, "ah"), (6, 2, 77, "eh"), (9, 3, 75, "oo")]
    ANSWER = [(12, 1, 79, "ee"), (14, 2, 77, "ah")]
    for bar in range(1, 8):
        shift = [0, -4, -2, -5][bar % 4]
        for st, ln, m, v in CALL + (ANSWER if bar % 2 == 0 else []):
            at = s16(bar, st)
            if at < END - 0.01:
                add(voc, vox(m + shift, ln * Q / 4 * 0.9, v), at)

    add(fx, end_hit(), END)
    # end card pad
    pad = sum(organ(CHORDS[0], 1.3) for _ in range(1))
    add(keys, pad * 0.8, END)

    # mix: intro bar low-passed
    bus = drums * 0.9 + bass + keys + voc * 0.55
    cut = int(BAR * SR)
    intro = lp(bus[:cut], 700, 2)
    xf = np.linspace(0, 1, int(0.03 * SR))
    bus[:cut] = intro
    bus[cut : cut + len(xf)] *= xf
    # light sidechain from the kick
    sc = np.ones(N)
    for bar in range(1, 8):
        for st in (KICK_A if bar % 2 else KICK_B):
            i = int(s16(bar, st) * SR)
            L = int(0.18 * SR)
            j = min(N, i + L)
            sc[i:j] = np.minimum(sc[i:j], 0.55 + 0.45 * np.linspace(0, 1, j - i) ** 1.5)
    mix = (bus - drums * 0.9) * sc + drums * 0.9 + fx
    # simple room
    rev = lfilter([0.25], [1, -0.82], lp(mix, 4000))
    mix = mix + 0.12 * np.roll(rev, int(0.023 * SR))
    mix = np.tanh(mix * 1.2)
    fade = int(0.4 * SR)
    mix[-fade:] *= np.linspace(1, 0, fade)
    mix /= np.abs(mix).max() / 0.89
    st = np.stack([mix, mix], 1)
    # widen keys/vocals slightly with a short delay on R
    side = np.roll((keys + voc * 0.55) * sc, int(0.011 * SR)) * 0.25
    st[:, 1] += side - (keys + voc * 0.55) * sc * 0.25
    st /= np.abs(st).max() / 0.89
    sf.write(OUT, st.astype(np.float32), SR)
    print("ok", OUT)

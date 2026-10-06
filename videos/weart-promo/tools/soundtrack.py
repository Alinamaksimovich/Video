"""Procedural soundtrack for the WeArt Studio promo (no voiceover).

Dark tech groove at 120 BPM in E minor: half-time kick/snare that opens into
four-on-the-floor for the pricing beat, 16th-note filtered arp, 808-style sub,
plus UI sound design (typing, glitch blips, node pops, cash register, impact).

Writes assets/audio/music.wav and assets/audio/sfx.wav (+ preview-mix.wav).
Deterministic: fixed RNG seed, no network. Run: python3 tools/soundtrack.py
"""

import os

import numpy as np
import soundfile as sf
from scipy.signal import butter, fftconvolve, lfilter, sosfilt

SR = 44100
DUR = 20.0
N = int(SR * DUR)
BPM = 120
BEAT = 60 / BPM
DROP = 18.0  # end-card hit
BREAK = DROP - 0.5  # kick/bass breath before the drop
ROLL = DROP - 1.0  # snare roll start
LAST = DUR - 0.5  # final chord
FOUR = 15.5  # four-on-the-floor from the pricing beat
rng = np.random.default_rng(7)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets", "audio")


def t_axis(n):
    return np.arange(n) / SR


def add(buf, sig, at, gain=1.0):
    i = int(at * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i] * gain


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], btype="band", fs=SR, output="sos"), x)


def lp(x, f, order=2):
    return sosfilt(butter(order, f, btype="low", fs=SR, output="sos"), x)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, btype="high", fs=SR, output="sos"), x)


def reverb(x, secs=1.4, wet=0.25, tone=5000):
    n = int(secs * SR)
    ir = rng.standard_normal(n) * np.exp(-t_axis(n) * (6.0 / secs))
    ir = lp(ir, tone)
    ir /= np.sqrt(np.sum(ir**2))
    w = fftconvolve(x, ir)[: len(x)]
    return x * (1 - wet) + w * wet


def saw(freq, n, detune=0.0, phase=0.0):
    f = freq * (1 + detune)
    return 2 * ((t_axis(n) * f + phase) % 1.0) - 1


# ---------------------------------------------------------------- drums
def kick():
    n = int(0.45 * SR)
    t = t_axis(n)
    f = 42 + 120 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t * 6.5)
    click = hp(rng.standard_normal(n), 2000) * np.exp(-t * 300) * 0.25
    return np.tanh((body + click) * 1.6)


def clap():
    n = int(0.3 * SR)
    t = t_axis(n)
    noise = bp(rng.standard_normal(n), 900, 3200)
    env = np.zeros(n)
    for k, d in enumerate([0, 0.011, 0.022]):
        i = int(d * SR)
        env[i:] += np.exp(-(t[: n - i]) * (90 if k < 2 else 16))
    return noise * env * 0.6


def hat(open_=False):
    n = int((0.18 if open_ else 0.05) * SR)
    t = t_axis(n)
    return hp(rng.standard_normal(n), 7500) * np.exp(-t * (18 if open_ else 80)) * 0.35


def snare_roll(buf, start, end):
    steps = int(round((end - start) / (BEAT / 4)))
    for s in range(steps):
        g = 0.15 + 0.85 * (s / steps) ** 2
        add(buf, clap(), start + s * BEAT / 4, 0.55 * g)


# ---------------------------------------------------------------- harmony
# E minor: Em – C – Am – B, one bar (2 s) each
ROOTS = [41.2, 32.7, 55.0, 61.74]
TRIADS = [
    [164.81, 196.0, 246.94],
    [130.81, 164.81, 196.0],
    [220.0, 261.63, 329.63],
    [246.94, 311.13, 369.99],
]


def bar_of(t):
    return int(t // (4 * BEAT)) % 4


def sidechain(n_total, kicks):
    env = np.ones(n_total)
    for k in kicks:
        i = int(k * SR)
        m = min(n_total - i, int(0.32 * SR))
        if m <= 0:
            continue
        r = np.linspace(0, 1, m) ** 0.6
        env[i : i + m] = np.minimum(env[i : i + m], 0.18 + 0.82 * r)
    return env


def stab(freqs, length=0.2):
    n = int(length * SR)
    t = t_axis(n)
    s = np.zeros(n)
    for f in freqs:
        for d in (-0.006, -0.002, 0.0, 0.003, 0.007):
            s += saw(f, n, d, phase=rng.random())
    s = lp(s / (len(freqs) * 5), 3200)
    return s * np.exp(-t * 11)


def bass_note(f, length):
    n = int(length * SR)
    t = t_axis(n)
    s = 0.6 * saw(f, n) + 0.4 * saw(f, n, 0.004) + 0.5 * np.sin(2 * np.pi * f * t)
    s = lp(s, 520)
    env = np.minimum(1, t * 300) * np.exp(-t * 3.5)
    return s * env


def pad(freqs, length):
    n = int(length * SR)
    t = t_axis(n)
    s = np.zeros(n)
    for f in freqs:
        for d in (-0.004, 0.0, 0.004):
            s += saw(f / 2, n, d, phase=rng.random())
    s = lp(s / (len(freqs) * 3), 1400)
    env = np.minimum(1, t / 0.15) * np.minimum(1, (length - t) / 0.2).clip(0)
    return s * env


def pluck(f, length=0.16, cutoff=2600):
    n = int(length * SR)
    t = t_axis(n)
    sq = np.sign(np.sin(2 * np.pi * f * t)) * 0.5 + saw(f, n, 0.003) * 0.5
    return lp(sq, cutoff) * np.exp(-t * 22)


def sub808(f, length):
    n = int(length * SR)
    t = t_axis(n)
    ff = f * (1 + 0.5 * np.exp(-t * 30))
    s = np.sin(2 * np.pi * np.cumsum(ff) / SR)
    env = np.minimum(1, t * 200) * np.exp(-t * 1.2)
    return np.tanh(s * env * 1.8) * 0.8


def build_music():
    drums = np.zeros(N)
    bass = np.zeros(N)
    arp = np.zeros(N)
    pads = np.zeros(N)

    kicks = []
    for b in range(int(DUR / BEAT)):
        t = b * BEAT
        if BREAK <= t < DROP or t >= LAST:
            continue
        if t >= FOUR:
            kicks.append(t)
        else:
            # half-time: kick on 1 and the "and" of 2 in each 4-beat bar
            pos = b % 4
            if pos == 0:
                kicks.append(t)
            if pos == 1:
                kicks.append(t + BEAT / 2)
            # snare on beat 3 (half-time feel)
            if pos == 2:
                add(drums, clap(), t, 0.9)
    for k in kicks:
        add(drums, kick(), k, 0.95)
    for b in range(int(DUR / BEAT)):
        t = b * BEAT
        if t >= FOUR and b % 2 == 1 and not (ROLL <= t < DROP) and t < LAST:
            add(drums, clap(), t, 0.8)

    # hats: 8ths, with 32nd-note rolls at the end of every 2nd bar
    step = BEAT / 2
    for s_ in range(int(DUR / step)):
        t = s_ * step
        if BREAK <= t < DROP or t >= LAST:
            continue
        add(drums, hat(), t, 0.4 if s_ % 2 else 0.25)
        if s_ % 16 == 14:
            for r in range(4):
                add(drums, hat(), t + r * step / 4, 0.18 + 0.06 * r)
        if t >= FOUR and s_ % 2 == 1:
            add(drums, hat(open_=True), t, 0.45)
    snare_roll(drums, ROLL, DROP)

    # 808 sub on each bar root
    for bar in range(int(DUR / (4 * BEAT))):
        t = bar * 4 * BEAT
        if t >= LAST:
            break
        if t < BREAK:
            add(bass, sub808(ROOTS[bar % 4] * 2, min(2.0, BREAK - t)), t, 0.9)
    add(bass, sub808(ROOTS[0] * 2, 2.0), DROP, 0.9)

    # 16th arp, filter opening over the piece
    s16 = BEAT / 4
    for s_ in range(int(DUR / s16)):
        t = s_ * s16
        if t >= LAST or BREAK <= t < DROP:
            continue
        tri = TRIADS[bar_of(t)]
        pattern = [0, 1, 2, 1, 0, 2, 1, 2]
        f = tri[pattern[s_ % 8]] * (2 if s_ % 8 in (2, 5) else 1)
        cutoff = 900 + 3200 * min(1.0, t / FOUR)
        add(arp, pluck(f, 0.16, cutoff), t, 0.32)

    for bar in range(int(DUR / (4 * BEAT))):
        t = bar * 4 * BEAT
        if t >= LAST:
            break
        add(pads, pad(TRIADS[bar % 4], 4 * BEAT), t, 0.3)

    sc = sidechain(N, kicks)
    arp = reverb(arp * (0.5 + 0.5 * sc), 1.0, 0.3)
    pads = reverb(pads * sc, 1.8, 0.4)
    music = drums + bass * sc + arp + pads * 0.7
    tail = t_axis(N)
    music *= np.clip((DUR - tail) / 0.9, 0, 1) ** 1.5
    music = np.tanh(music * 0.9)
    return music / np.max(np.abs(music)) * 0.89


# ---------------------------------------------------------------- sfx
def sweep_noise(length, f0, f1, shape="arc"):
    n = int(length * SR)
    t = np.linspace(0, 1, n)
    noise = rng.standard_normal(n)
    out = np.zeros(n)
    # time-varying band via 12 crossfaded bands
    bands = 12
    edges = np.geomspace(f0, f1, bands + 1)
    for b in range(bands):
        seg = bp(noise, edges[b] * 0.7, min(edges[b + 1] * 1.3, SR / 2 - 100))
        centre = (b + 0.5) / bands
        w = np.exp(-(((t - centre) * bands / 1.6) ** 2))
        out += seg * w
    if shape == "arc":
        env = np.sin(np.pi * t) ** 1.6
    else:  # rise
        env = t**2.2
    return out * env


def whoosh(length=0.45, up=True):
    return sweep_noise(length, 250, 6000) if up else sweep_noise(length, 6000, 250)


def swish():
    return sweep_noise(0.2, 1200, 9000) * 0.8


def shutter():
    n = int(0.16 * SR)
    t = t_axis(n)
    out = np.zeros(n)
    for d in (0.0, 0.07):
        i = int(d * SR)
        m = n - i
        out[i:] += bp(rng.standard_normal(m), 1500, 7000) * np.exp(-t[:m] * 160)
    return out * 0.9


def tap():
    n = int(0.08 * SR)
    t = t_axis(n)
    return (np.sin(2 * np.pi * 1700 * t) * np.exp(-t * 70) + hp(rng.standard_normal(n), 3000) * np.exp(-t * 400) * 0.3) * 0.7


def ping(f, length=0.6):
    n = int(length * SR)
    t = t_axis(n)
    return (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t)) * np.exp(-t * 7)


def shimmer(length=1.7):
    n = int(length * SR)
    out = np.zeros(n)
    notes = [880.0, 1046.5, 1318.5, 1568.0, 1760.0, 2093.0, 2637.0]
    k = 0
    tt = 0.0
    while tt < length - 0.3:
        f = notes[k % len(notes)] * (1 if k < 7 else 2 ** (rng.integers(0, 2)))
        add(out, ping(f, 0.5), tt, 0.22 + 0.1 * rng.random())
        tt += BEAT / 4
        k += 1
    sparkle = hp(rng.standard_normal(n), 9000) * (0.5 + 0.5 * np.sin(np.linspace(0, 40, n))) * 0.04
    env = np.minimum(1, t_axis(n) / 0.1) * np.clip((length - t_axis(n)) / 0.4, 0, 1)
    return reverb((out + sparkle) * env, 1.6, 0.4, 9000)


def riser(length=1.0):
    n = int(length * SR)
    t = t_axis(n)
    f = 180 * (8 ** (t / length))
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.25
    return (sweep_noise(length, 300, 9000, "rise") * 0.9 + tone * (t / length) ** 2) * 0.8


def impact():
    n = int(2.2 * SR)
    t = t_axis(n)
    f = 38 + 80 * np.exp(-t * 18)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2)
    crack = lp(rng.standard_normal(n), 5000) * np.exp(-t * 14) * 0.5
    return reverb(np.tanh((boom + crack) * 1.4), 2.0, 0.3) * 0.95


def pop_ding():
    n = int(0.9 * SR)
    t = t_axis(n)
    s = (np.sin(2 * np.pi * 1318.5 * t) + 0.6 * np.sin(2 * np.pi * 1975.5 * t)) * np.exp(-t * 6)
    s += np.sin(2 * np.pi * 220 * t) * np.exp(-t * 40) * 0.6
    return reverb(s * 0.45, 1.0, 0.3, 9000)


def thud():
    n = int(0.3 * SR)
    t = t_axis(n)
    f = 60 + 90 * np.exp(-t * 40)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 14) * 0.9


def key_click():
    n = int(0.03 * SR)
    t = t_axis(n)
    return bp(rng.standard_normal(n), 2500, 8000) * np.exp(-t * 300) * 0.6


def blip(f):
    n = int(0.06 * SR)
    t = t_axis(n)
    return np.sign(np.sin(2 * np.pi * f * t)) * np.exp(-t * 50) * 0.25


def cash():
    s = pop_ding()
    n = int(0.25 * SR)
    t = t_axis(n)
    drawer = bp(rng.standard_normal(n), 400, 2500) * np.exp(-t * 25) * 0.6
    out = np.zeros(len(s))
    add(out, drawer, 0)
    add(out, s, 0.06)
    add(out, ping(2637.0, 0.5) * 0.4, 0.12)
    return out


def build_sfx():
    s = np.zeros(N)
    for i, at in enumerate((0.25, 0.75, 1.25, 1.75, 2.25)):  # subscription cards slam in
        add(s, thud(), at, 0.8)
        add(s, swish(), at - 0.08, 0.45)
    add(s, sweep_noise(0.5, 6000, 200), 3.3, 0.8)  # cards implode
    add(s, impact() * 0.6, 3.8, 0.8)
    for i, at in enumerate(np.arange(5.2, 6.75, 0.07)):  # typing
        add(s, key_click(), at + (0.012 if i % 3 == 0 else 0), 0.7)
    add(s, tap(), 7.0, 0.9)  # send
    add(s, whoosh(0.4), 7.02, 0.6)
    for i, at in enumerate(np.arange(7.25, 8.2, 0.0625)):  # generation glitch blips
        add(s, blip(600 + (i * 137) % 900), at, 0.6)
    add(s, shimmer(1.0), 7.3, 0.6)
    add(s, pop_ding(), 8.3, 0.7)  # image revealed
    for at in (9.5, 10.25, 11.0, 11.75):  # mode switches
        add(s, tap(), at, 0.7)
        add(s, swish(), at - 0.05, 0.55)
    add(s, whoosh(0.45), 12.3, 0.7)  # → canvas
    for i, at in enumerate((12.9, 13.5, 14.1)):  # node connections
        add(s, ping(660.0 * (1.26 ** i), 0.4), at, 0.5)
        add(s, tap(), at, 0.5)
    add(s, whoosh(0.45), 15.3, 0.7)  # → pricing
    for at in np.arange(16.0, 16.8, 0.05):  # count-up ticks
        add(s, key_click(), at, 0.5)
    add(s, cash(), 16.85, 0.9)
    add(s, riser(1.0), ROLL, 0.7)
    add(s, impact(), DROP, 1.0)
    add(s, pop_ding(), 18.8, 0.8)  # CTA
    return s / max(1.0, np.max(np.abs(s)) / 0.89)


if __name__ == "__main__":
    music = build_music()
    sfx = build_sfx()
    sf.write(os.path.join(OUT, "music.wav"), music.astype(np.float32), SR)
    sf.write(os.path.join(OUT, "sfx.wav"), sfx.astype(np.float32), SR)
    mix = music * 0.6 + sfx * 0.6
    mix = mix / np.max(np.abs(mix)) * 0.95
    sf.write(os.path.join(OUT, "preview-mix.wav"), mix.astype(np.float32), SR)
    print("ok")

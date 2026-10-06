"""Procedural soundtrack for the MIRRO dynamic promo.

Writes three stems into assets/audio/:
  music.wav  — 120 BPM electro-pop groove, pre-ducked under the voiceover
  sfx.wav    — whooshes, shutter, shimmer, taps, riser, impact, CTA pop
  voice.wav  — the supplied voiceover, cleaned (composition places it at VO_OFFSET)
plus preview-mix.wav for listening.

Deterministic: fixed RNG seed, no network. Run: python3 tools/soundtrack.py
"""

import os

import numpy as np
import soundfile as sf
from scipy.signal import butter, fftconvolve, lfilter, sosfilt

SR = 44100
DUR = 15.0
N = int(SR * DUR)
BPM = 120
BEAT = 60 / BPM
VO_OFFSET = 0.6
DROP = 11.0  # logo hit
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
# A minor: Am – F – C – G, one bar (2 s) each
ROOTS = [55.0, 43.65, 65.41, 49.0]
TRIADS = [
    [220.0, 261.63, 329.63],
    [174.61, 220.0, 261.63],
    [261.63, 329.63, 392.0],
    [196.0, 246.94, 293.66],
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


def build_music():
    drums = np.zeros(N)
    bass = np.zeros(N)
    keys = np.zeros(N)
    pads = np.zeros(N)

    # kick on every beat, except the breath before the drop (10.5–11.0)
    kicks = [b * BEAT for b in range(int(DUR / BEAT)) if not (10.5 <= b * BEAT < DROP)]
    kicks = [k for k in kicks if k < 14.5]
    for k in kicks:
        add(drums, kick(), k, 0.95)

    for b in range(int(DUR / BEAT)):
        t = b * BEAT
        if t >= 14.5:
            break
        if b % 2 == 1 and not (10.0 <= t < DROP):
            add(drums, clap(), t, 0.8)
        # offbeat hats always, 16ths in the build and after the drop
        if not (10.5 <= t < DROP):
            add(drums, hat(open_=True), t + BEAT / 2, 0.55)
            if 6.5 <= t < 10.5 or t >= DROP:
                add(drums, hat(), t + BEAT / 4, 0.5)
                add(drums, hat(), t + 3 * BEAT / 4, 0.45)
            elif t < 6.5:
                add(drums, hat(), t, 0.25)

    snare_roll(drums, 10.0, DROP)

    # bass: driving 8ths, octave jump on the "and"
    step = BEAT / 2
    for s in range(int(DUR / step)):
        t = s * step
        if 10.5 <= t < DROP or t >= 14.5:
            continue
        f = ROOTS[bar_of(t)] * (2 if s % 2 else 1)
        add(bass, bass_note(f, step * 0.95), t, 0.85)

    # offbeat chord stabs, denser after the drop
    for s in range(int(DUR / step)):
        t = s * step
        if t >= 14.5 or 10.5 <= t < DROP:
            continue
        if s % 2 == 1 or t >= DROP:
            add(keys, stab(TRIADS[bar_of(t)], 0.22), t, 0.5)
    # final long chord on the last downbeat
    add(keys, stab(TRIADS[0], 1.4) * 1.2, 14.5, 0.6)

    # soft pad bed per bar
    for bar in range(int(DUR / (4 * BEAT))):
        t = bar * 4 * BEAT
        if t >= 14.5:
            break
        add(pads, pad(TRIADS[bar % 4], 4 * BEAT), t, 0.35)

    sc = sidechain(N, kicks)
    keys = reverb(keys * sc, 1.2, 0.3)
    pads = reverb(pads * sc, 1.8, 0.35)
    music = drums + bass * sc + keys + pads * 0.8

    # fade out the tail
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


def build_sfx():
    s = np.zeros(N)
    add(s, impact() * 0.45, 0.0)
    add(s, whoosh(0.5), 0.0, 0.6)
    add(s, whoosh(0.4), 2.72, 0.75)  # → processing
    add(s, shutter(), 3.25, 0.8)  # "сфотографируй"
    add(s, shimmer(1.75), 4.55, 0.9)  # AI cut-out
    add(s, whoosh(0.4), 6.22, 0.75)  # → try-on
    add(s, whoosh(0.18, up=False), 7.42, 0.45)  # punch-in
    add(s, tap(), 8.88, 0.9)  # tap on outfit
    for at in (9.0, 9.5, 10.0):
        add(s, swish(), at - 0.06, 0.7)
    add(s, riser(1.0), 10.0, 0.7)
    add(s, impact(), DROP, 1.0)  # logo
    add(s, pop_ding(), 11.85, 0.8)  # CTA
    return s / max(1.0, np.max(np.abs(s)) / 0.89)


# ---------------------------------------------------------------- voice
def build_voice():
    v, sr = sf.read(os.path.join(OUT, "voiceover-src.mp3"), dtype="float32")
    if v.ndim > 1:
        v = v.mean(axis=1)
    assert sr == SR, sr
    v = hp(v, 80)
    v = v / np.max(np.abs(v)) * 0.89
    out = np.zeros(N)
    add(out, v, VO_OFFSET)
    return v, out


def duck_env(voice):
    # smoothed voice envelope → music gain (−9 dB under speech)
    a = np.abs(voice)
    win = int(0.05 * SR)
    env = np.convolve(a, np.ones(win) / win, mode="same")
    env = env / (env.max() + 1e-9)
    gate = (env > 0.04).astype(float)
    k = int(0.18 * SR)
    gate = np.convolve(gate, np.ones(k) / k, mode="same")
    return 1 - gate.clip(0, 1) * (1 - 10 ** (-9 / 20))


if __name__ == "__main__":
    voice_clip, voice = build_voice()
    music = build_music() * duck_env(voice)
    sfx = build_sfx()
    sf.write(os.path.join(OUT, "music.wav"), music.astype(np.float32), SR)
    sf.write(os.path.join(OUT, "sfx.wav"), sfx.astype(np.float32), SR)
    sf.write(os.path.join(OUT, "voice.wav"), voice_clip.astype(np.float32), SR)  # placed at VO_OFFSET
    mix = voice * 1.0 + music * 0.42 + sfx * 0.55
    mix = mix / np.max(np.abs(mix)) * 0.95
    sf.write(os.path.join(OUT, "preview-mix.wav"), mix.astype(np.float32), SR)
    print("ok")

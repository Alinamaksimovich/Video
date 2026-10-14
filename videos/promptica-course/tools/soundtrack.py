"""Audio for the PROMPTICA course reel: her voice up front, an original phonk bed
under it, a few hand-picked SFX from her packs.

- voice: assets/audio/voice-raw.wav exactly as recorded (no EQ, denoise or
  compression), only a clean gain so its peaks sit at -1 dBFS.
- music: assets/audio/phonk.wav from tools/phonk.py, ~16 dB under her speech.
- sfx: assets/sfx/*.wav (cut from her sound-pack demos), quiet, key moments only.
Writes music.wav, sfx.wav, voice.wav, preview-mix.wav. Run: python3 tools/soundtrack.py
"""

import os

import numpy as np
import soundfile as sf

SR = 44100
DUR = 16.5
N = int(SR * DUR)
BEAT0, BEAT = 1.46, 0.7186  # visual beat grid (tools/phonk.py is written on it)
QUIET = (10.15, 11.45)  # "сделай тише": the bed really drops

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets", "audio")
SFX = os.path.join(HERE, "..", "assets", "sfx")


def load(path, mono=True):
    a, sr = sf.read(path, dtype="float32")
    assert sr == SR, (path, sr)
    if mono and a.ndim == 2:
        a = a.mean(1)
    return a


def rms_db(x):
    return 20 * np.log10(np.sqrt(np.mean(x**2)) + 1e-9)


def add(buf, sig, at, gain=1.0):
    i = int(at * SR)
    j = min(len(buf), i + len(sig))
    if j > i:
        buf[i:j] += sig[: j - i] * gain


def build_music():
    out = load(os.path.join(OUT, "phonk.wav"))
    return np.pad(out, (0, max(0, N - len(out))))[:N]


def raw_voice():
    """Her recording untouched: resample 48k -> 44.1k and one gain stage, nothing else."""
    from scipy.signal import resample_poly

    v, sr = sf.read(os.path.join(OUT, "voice-raw.wav"), dtype="float64")
    if v.ndim == 2:
        v = v.mean(1)
    v = resample_poly(v, 147, 160) if sr == 48000 else v
    return v * (10 ** (-1 / 20) / np.abs(v).max())


def speech_gate(voice):
    win = int(0.05 * SR)
    env = np.convolve(np.abs(voice), np.ones(win) / win, mode="same")
    gate = (env > env.max() * 0.05).astype(float)
    k = int(0.25 * SR)
    return np.convolve(gate, np.ones(k) / k, mode="same").clip(0, 1)


SFX_CUES = [  # (file, time, gain dB)
    ("appear_1", 0.05, -6),  # timer appears
    ("select", 1.46, -8),  # timer lands on 10:00
    ("typing", 2.25, -4),  # prompt typed
    ("trtrtr_1", 3.20, -8),  # storyboard cards
    ("loading", 6.12, -8),  # tools connect
    ("whoosh_shine", 7.05, -10),  # editor opens
    ("appear_2", 8.65, -8),  # preview plays
    ("click_1", 10.08, -6),  # "тише"
    ("trtrtr_2", 10.80, -8),  # "короче": clips shrink
    ("appear_3", 11.52, -8),  # course card
    ("click_2", 14.75, -4),  # subscribe click
    ("sms", 14.85, -10),  # subscribed
]


if __name__ == "__main__":
    voice = np.zeros(N)
    add(voice, raw_voice(), 0.0)
    gate = speech_gate(voice)
    speech = rms_db(voice[gate > 0.5])

    music = build_music()
    music *= 10 ** ((speech - 12.0 - rms_db(music)) / 20)  # bed 12 dB under her speech
    t = np.arange(N) / SR
    duck = 1 - gate * (1 - 10 ** (-6 / 20))  # another 6 dB down while she talks
    q0, q1 = QUIET
    quiet = np.interp(t, [q0, q0 + 0.2, q1 - 0.15, q1 + 0.1], [1, 10 ** (-12 / 20), 10 ** (-12 / 20), 1])
    music *= duck * quiet

    sfx = np.zeros(N)
    for name, at, g in SFX_CUES:
        s = load(os.path.join(SFX, name + ".wav"))
        s *= 10 ** ((speech - 8.0 - rms_db(s[np.abs(s) > 0.02])) / 20)  # each hit ~8 dB under speech
        add(sfx, s, at, 10 ** (g / 20))

    for name, x in (("voice", voice), ("music", music), ("sfx", sfx)):
        sf.write(os.path.join(OUT, name + ".wav"), x.astype(np.float32), SR)
    sfx /= max(1.0, np.abs(sfx).max() / 0.5)
    mix = voice + music + sfx
    sf.write(os.path.join(OUT, "preview-mix.wav"), (mix / max(1.0, np.abs(mix).max() / 0.95)).astype(np.float32), SR)
    print("speech", round(rms_db(voice[gate > 0.5]), 1), "music under speech", round(rms_db(music[gate > 0.5]), 1),
          "music in gaps", round(rms_db(music[(gate < 0.1) & (t > 0.3) & (t < 16)]), 1), "peak", round(np.abs(mix).max(), 2))

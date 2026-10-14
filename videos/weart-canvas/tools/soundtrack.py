"""Final mix for the WeArt canvas reel: her voice up front (no processing, gain
only), the house bed under it, SFX from the shared sfx-library on the key moments.

Levels: bed ~15 dB under her speech RMS (and ducked 4 dB more while she talks),
SFX ~9 dB under it. Writes voice.wav, music.wav, sfx.wav, preview-mix.wav.
Run: python3 tools/house.py && python3 tools/soundtrack.py
"""

import os

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

SR = 44100
DUR = 15.04
N = int(SR * DUR)
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets", "audio")
SFX = os.path.join(HERE, "..", "assets", "sfx")

CUES = [  # (file, time s, gain dB, max length s or None)
    ("whoosh_shine", 3.55, -10, None),  # video flies up
    ("SJC_IMPACT_Liquid_Impact_01", 3.82, -9, None),
    ("SJC_CLICK_Woodblock_01", 4.10, -6, None),  # three clicks
    ("SJC_CLICK_Woodblock_01", 4.48, -6, None),
    ("SJC_CLICK_Tonal_Click_Double_01", 4.86, -6, None),
    ("SJC_HOVER_Hover_01", 3.93, -10, None),
    ("SJC_HOVER_Hover_04", 4.33, -10, None),
    ("SJC_HOVER_Hover_01", 4.71, -10, None),
    ("SJC_BLEEP_Data_Notification_01", 5.25, -10, None),  # "Here's the trick"
    ("SJC_FILMCAMERA_Leaf_Shutter_04", 6.02, -6, None),  # CANVAS
    ("appear_1", 6.04, -10, None),
    ("whoosh_shine", 6.55, -12, None),  # board opens
    ("SJC_TILE_Plastic_Tiles_01", 8.42, -6, None),  # photo drops
    ("typing", 9.10, -9, 0.8),  # prompt typed
    ("SJC_CLICK_Tonal_Click_Run_Up_01", 10.00, -8, None),  # connect
    ("SJC_POP_PopUp_Soft_02", 10.32, -9, None),
    ("SJC_POP_Bubble_Single_01", 10.95, -8, None),  # Photos
    ("SJC_POP_Bubble_Single_01", 11.39, -8, None),  # Videos
    ("SJC_POP_Bubble_Triple_01", 11.82, -8, None),  # Voice
    ("SJC_DSLR_Focus_Beep_01", 12.50, -9, None),  # all in one place
    ("SJC_IMPACT_Liquid_Impact_01", 13.92, -10, None),  # logo
    ("SJC_DSLR_Flash_Close_02", 13.95, -10, None),
    ("SJC_BLEEP_Cute_Double_Bleep_01", 14.55, -9, None),  # CTA
]


def load(path, mono=True):
    a, sr = sf.read(path, dtype="float64")
    if a.ndim == 2:
        a = a.mean(1)
    if sr == 48000:
        a = resample_poly(a, 147, 160)
    elif sr != SR:
        raise ValueError((path, sr))
    return a


def rms_db(x):
    return 20 * np.log10(np.sqrt(np.mean(x**2)) + 1e-9)


def speech_gate(voice):
    win = int(0.05 * SR)
    env = np.convolve(np.abs(voice), np.ones(win) / win, mode="same")
    gate = (env > env.max() * 0.04).astype(float)
    k = int(0.25 * SR)
    return np.convolve(gate, np.ones(k) / k, mode="same").clip(0, 1)


if __name__ == "__main__":
    # voice = new intro take (0 - 3.425 s) + the original recording from 3.64 s on.
    # Her recordings are untouched: only gain (the intro take is quieter, +5 dB matches its speech
    # level to the main take) and a 30 ms fade-in where the original starts.
    orig = load(os.path.join(OUT, "voice-raw.wav"))
    g = 10 ** (-1 / 20) / np.abs(orig).max()  # main take: peak at -1 dBFS
    intro = load(os.path.join(OUT, "voice-intro-raw.wav")) * g * 10 ** (5.0 / 20)
    voice = np.zeros(N)
    cut = int(3.64 * SR)
    tail = orig[cut:N] * g
    voice[cut : cut + len(tail)] = tail
    voice[cut : cut + int(0.03 * SR)] *= np.linspace(0, 1, int(0.03 * SR))
    n_in = min(len(intro), cut)
    voice[:n_in] += intro[:n_in]
    gate = speech_gate(voice)
    speech = rms_db(voice[gate > 0.5])

    music = load(os.path.join(OUT, "house.wav"))
    music = np.pad(music, (0, max(0, N - len(music))))[:N]
    music *= 10 ** ((speech - 15.0 - rms_db(music[int(4 * SR) : int(14 * SR)])) / 20)
    music *= 1 - gate * (1 - 10 ** (-4 / 20))

    sfx = np.zeros(N)
    for name, at, g, maxlen in CUES:
        s = load(os.path.join(SFX, name + ".wav"))
        if maxlen:
            s = s[: int(maxlen * SR)].copy()
            s[-int(0.05 * SR) :] *= np.linspace(1, 0, int(0.05 * SR))
        s *= 0.89 * 10 ** ((g - 3.0) / 20) / np.abs(s).max()  # peak = her peak minus (3 dB + cue gain)
        i = int(at * SR)
        j = min(N, i + len(s))
        sfx[i:j] += s[: j - i]

    for name, x in (("voice", voice), ("music", music), ("sfx", sfx)):
        sf.write(os.path.join(OUT, name + ".wav"), x.astype(np.float32), SR)
    mix = voice + music + sfx
    sf.write(os.path.join(OUT, "preview-mix.wav"), (mix / max(1.0, np.abs(mix).max() / 0.95)).astype(np.float32), SR)
    t = np.arange(N) / SR
    print("speech", round(speech, 1), "| music under speech", round(rms_db(music[gate > 0.5]), 1),
          "| music in gaps", round(rms_db(music[(gate < 0.1) & (t > 4)]), 1), "| sfx peak", round(np.abs(sfx).max(), 2),
          "| mix peak", round(np.abs(mix).max(), 2))

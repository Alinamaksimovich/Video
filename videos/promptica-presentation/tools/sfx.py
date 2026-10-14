"""SFX layer for the PROMPTICA presentation, from the sound packs in assets/sfx.
Writes assets/audio/sfx.wav. Run: python3 tools/sfx.py
"""

import os

import numpy as np
import soundfile as sf

SR = 44100
DUR = 15.0
N = int(SR * DUR)
Q = 60 / 174
BAR = 4 * Q
HERE = os.path.dirname(os.path.abspath(__file__))
SFX = os.path.join(HERE, "..", "assets", "sfx")

CUES = [  # (file, time, gain dB)
    ("typing", 0.12, -6),  # prompt types in the intro
    ("select_2", BAR - 0.12, -6),  # enter -> drop
    ("appear_1", 2 * BAR, -10),  # headline
    ("appear_2", 4 * BAR, -8),  # services
    ("appear_3", 4 * BAR + 2 * Q, -10),
    ("appear_4", 5 * BAR, -10),
    ("appear_1", 5 * BAR + 2 * Q, -10),
    ("appear_2", 6 * BAR, -10),
    ("whoosh_shine", 7 * BAR - 0.25, -10),  # statement
    ("click_1", 9 * BAR + 2 * Q, -8),  # end card CTA
]


def load(name):
    a, sr = sf.read(os.path.join(SFX, name + ".wav"), dtype="float32")
    assert sr == SR
    return a.mean(1) if a.ndim == 2 else a


if __name__ == "__main__":
    out = np.zeros(N)
    for name, at, g in CUES:
        s = load(name) * 10 ** (g / 20) * 0.6
        i = int(at * SR)
        j = min(N, i + len(s))
        out[i:j] += s[: j - i]
    out /= max(1.0, np.abs(out).max() / 0.7)
    sf.write(os.path.join(HERE, "..", "assets", "audio", "sfx.wav"), out.astype(np.float32), SR)
    print("ok")

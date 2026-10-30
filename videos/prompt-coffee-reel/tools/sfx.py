"""Light SFX from her library, timed to the cards. Writes assets/audio/sfx.wav. Run: python3 tools/sfx.py"""

import os

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

SR = 44100
DUR = 34.09
N = int(SR * DUR)
HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, "..", "..", "..", "sfx-library")
S1, S2, S3, S4 = 2.82, 10.0, 18.71, 27.21

CUES = [  # (file, time, gain dB) - kept well under the voice
    ("pops/SJC_POP_PopUp_Soft_02", 1.72, -20),
    ("pops/SJC_POP_PopUp_Soft_02", 1.92, -20),
    ("pops/SJC_POP_PopUp_Soft_02", 2.12, -20),
    ("ui-pack/appear_1", S1, -22),
    ("ui-pack/appear_2", S2, -22),
    ("pops/SJC_POP_Bubble_Single_01", 17.80, -22),  # "каша"
    ("ui-pack/appear_3", S3, -22),
    ("pops/SJC_POP_PopUp_Soft_02", S4, -20),
    ("pops/SJC_POP_PopUp_Soft_02", S4 + 0.18, -20),
    ("pops/SJC_POP_PopUp_Soft_02", S4 + 0.36, -20),
]


def load(name):
    a, sr = sf.read(os.path.join(LIB, name + ".wav"), dtype="float32")
    a = a.mean(1) if a.ndim == 2 else a
    if sr != SR:
        a = resample_poly(a, SR, sr).astype(np.float32)
    return a


if __name__ == "__main__":
    out = np.zeros(N)
    for name, t, g in CUES:
        s = load(name)
        s = s / max(1e-6, np.abs(s).max()) * 10 ** (g / 20)
        i = int(t * SR)
        j = min(N, i + len(s))
        out[i:j] += s[: j - i]
    sf.write(os.path.join(HERE, "..", "assets", "audio", "sfx.wav"), out.astype(np.float32), SR)
    print("ok")

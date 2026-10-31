"""Audio for the 5 s node-board clip.
music.wav = the first 5 s of the UK garage bed from ../promptica-cases (intro build + drop at 1.82 s), faded out.
sfx.wav   = cues from her sound library (../../../sfx-library), timed to the board animation.
Run: python3 tools/audio.py
"""

import os

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

SR = 44100
DUR = 5.0
N = int(SR * DUR)
HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, "..", "..", "..", "sfx-library")
SRC = os.path.join(HERE, "..", "..", "promptica-cases", "assets", "audio", "music.wav")
OUT = os.path.join(HERE, "..", "assets", "audio")

CUES = [  # (file, time, gain dB, max length s or None)
    ("ui-pack/appear_1", 0.05, -10, None),  # reference nodes
    ("ui-pack/appear_2", 0.18, -10, None),
    ("pops/SJC_POP_PopUp_Soft_02", 0.34, -12, None),
    ("ui-pack/whoosh_shine", 0.40, -12, 0.8),  # pan 1
    ("ui-pack/typing", 0.80, -8, 0.95),  # prompt 1
    ("ui-pack/click_1", 1.75, -8, None),  # run
    ("pops/SJC_POP_PopUp_Soft_02", 1.78, -12, None),  # frame node
    ("ui-pack/loading", 1.95, -14, 0.45),
    ("camera/SJC_DSLR_Flash_Close_02", 2.35, -8, None),  # frame revealed
    ("ui-pack/appear_1", 2.40, -12, None),  # prompt 2 node
    ("ui-pack/whoosh_shine", 2.50, -12, 0.8),  # pan 3
    ("ui-pack/typing", 2.90, -8, 0.6),  # prompt 2
    ("ui-pack/click_2", 3.50, -8, None),  # run
    ("pops/SJC_POP_PopUp_Soft_02", 3.52, -12, None),  # video node
    ("ui-pack/loading", 3.85, -14, 0.35),
    ("camera/SJC_DSLR_Flash_Close_02", 4.20, -8, None),  # video revealed
    ("ui-pack/select_2", 4.40, -10, None),  # brand
]


def load(name):
    a, sr = sf.read(os.path.join(LIB, name + ".wav"), dtype="float32")
    a = a.mean(1) if a.ndim == 2 else a
    if sr != SR:
        a = resample_poly(a, SR, sr).astype(np.float32)
    return a


if __name__ == "__main__":
    m, sr = sf.read(SRC, dtype="float32")
    assert sr == SR
    m = m[:N]
    f = int(0.35 * SR)
    m[-f:] *= np.linspace(1, 0, f)[:, None]
    sf.write(os.path.join(OUT, "music.wav"), m, SR)

    out = np.zeros(N)
    for name, t, g, ln in CUES:
        s = load(name)
        if ln:
            s = s[: int(ln * SR)].copy()
            k = int(0.06 * SR)
            s[-k:] *= np.linspace(1, 0, k)
        s = s / max(1e-6, np.abs(s).max()) * 10 ** (g / 20)
        i = int(t * SR)
        j = min(N, i + len(s))
        out[i:j] += s[: j - i]
    out /= max(1.0, np.abs(out).max() / 0.7)
    sf.write(os.path.join(OUT, "sfx.wav"), out.astype(np.float32), SR)
    print("ok")

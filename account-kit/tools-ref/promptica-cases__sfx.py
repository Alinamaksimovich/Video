"""SFX layer for the PROMPTICA cases video, from her library (../../sfx-library).
Writes assets/audio/sfx.wav. Run: python3 tools/sfx.py
"""

import os

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

SR = 44100
DUR = 15.0
N = int(SR * DUR)
Q = 60 / 132
BAR = 4 * Q
HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, "..", "..", "..", "sfx-library")


def at(bar, beat=0.0):
    return bar * BAR + beat * Q


E = at(7, 2)
CUES = [  # (file, time, gain dB)
    ("ui-pack/intro_whoosh", 0.0, -10),  # logo in
    ("bleeps/SJC_CLICK_Tonal_Click_Double_01", at(0, 2), -14),  # "AI-agency" tag
    ("ui-pack/whoosh_shine", at(1) - 0.2, -10),  # drop
] + [("bleeps/SJC_CLICK_Woodblock_01", at(1, b), -14) for b in (0.75, 1.5, 2.25, 3)] + [  # service words
    ("pops/SJC_POP_PopUp_Soft_02", at(2), -10),  # empty can card
    ("ui-pack/loading", at(2, 1.75), -16),  # scan
    ("camera/SJC_DSLR_Flash_Close_02", at(2, 2), -10),  # reveal
    ("pops/SJC_POP_Bubble_Triple_01", at(2, 2.25), -12),  # fizz
] + [("camera/SJC_FILMCAMERA_Leaf_Shutter_04", at(3, b), -12) for b in range(4)] + [  # visuals
    ("ui-pack/appear_2", at(4), -10),  # phone
    ("impacts/SJC_IMPACT_Liquid_Impact_01", at(4, 0.4), -12),  # splash
    ("camera/SJC_DSLR_Focus_Beep_01", at(5) - 0.08, -16),
] + [("camera/SJC_FILMCAMERA_Leaf_Shutter_04", at(5, b * 1.33), -12) for b in range(3)] + [
    ("ui-pack/appear_3", at(6), -10),  # phones
    ("impacts/SJC_IMPACT_Liquid_Impact_01", at(6, 0.6), -13),  # pour
    ("foley/SJC_TILE_Plastic_Tiles_01", at(7), -14),  # wall
    ("ui-pack/appear_4", at(7, 1), -12),
    ("camera/SJC_FLASHBULB_Flashbulb_05", E, -10),  # end card
    ("ui-pack/click_1", E + 0.4, -10),  # CTA
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
    out /= max(1.0, np.abs(out).max() / 0.7)
    sf.write(os.path.join(HERE, "..", "assets", "audio", "sfx.wav"), out.astype(np.float32), SR)
    print("ok", len(CUES))

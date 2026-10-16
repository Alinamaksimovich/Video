"""Audio for the WeArt end-card CTA (2.7 s).

voice: "Try now." off-screen (Kokoro TTS, male voice am_michael, offline; KOKORO_DIR = model folder).
sfx: whoosh in, soft impact as TRY NOW lands, hover, click, "subscribed" bleep, confetti pops (sfx-library).
Writes assets/audio/voice.wav, sfx.wav, mix-vo.wav (voice + sfx) and mix-novo.wav (sfx only).
Run: KOKORO_DIR=... python3 tools/audio.py
"""

import os

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

SR = 44100
DUR = 2.7
N = int(SR * DUR)
VO_AT = 0.16
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets", "audio")
SFXD = os.path.join(HERE, "..", "assets", "sfx")

CUES = [  # (file, time s, gain dB)
    ("whoosh_shine", 0.0, -8),
    ("SJC_IMPACT_Liquid_Impact_01", 0.14, -10),
    ("SJC_HOVER_Hover_01", 0.92, -10),
    ("SJC_CLICK_Tonal_Click_Double_01", 1.15, -4),
    ("SJC_BLEEP_Cute_Double_Bleep_01", 1.24, -6),
    ("SJC_POP_Bubble_Triple_01", 1.30, -9),
]


def load(path):
    a, sr = sf.read(path, dtype="float64")
    if a.ndim == 2:
        a = a.mean(1)
    if sr == 48000:
        a = resample_poly(a, 147, 160)
    elif sr == 24000:
        a = resample_poly(a, 147, 80)
    elif sr != SR:
        raise ValueError((path, sr))
    return a


def place(buf, sig, t):
    i = int(t * SR)
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i]


if __name__ == "__main__":
    from kokoro_onnx import Kokoro

    k = os.environ["KOKORO_DIR"]
    kok = Kokoro(os.path.join(k, "kokoro-v1.0.onnx"), os.path.join(k, "voices-v1.0.bin"))
    a, sr = kok.create("Try now!", voice="am_michael", speed=1.0, lang="en-us")
    idx = np.where(np.abs(a) > 0.01)[0]
    a = a[max(0, idx[0] - 400) : idx[-1] + 2400]
    tmp = os.path.join(OUT, "_vo24.wav")
    sf.write(tmp, a.astype(np.float32), sr)
    vo = load(tmp)
    os.remove(tmp)
    vo = vo / np.abs(vo).max() * 0.89
    voice = np.zeros(N)
    place(voice, vo, VO_AT)

    sfx = np.zeros(N)
    for name, t, g in CUES:
        s = load(os.path.join(SFXD, name + ".wav"))
        s = s / np.abs(s).max() * 0.89 * 10 ** ((g - 3.0) / 20)  # peak under the voice peak
        place(sfx, s, t)
    t = np.arange(N) / SR
    fade = np.clip((DUR - t) / 0.25, 0, 1)
    sfx *= fade

    for name, x in (("voice", voice), ("sfx", sfx)):
        sf.write(os.path.join(OUT, name + ".wav"), x.astype(np.float32), SR)
    for name, x in (("mix-vo", voice + sfx), ("mix-novo", sfx)):
        x = x / max(1.0, np.abs(x).max() / 0.95)
        sf.write(os.path.join(OUT, name + ".wav"), np.stack([x, x], 1).astype(np.float32), SR)
    print("vo length", round(len(vo) / SR, 2), "s at", VO_AT)

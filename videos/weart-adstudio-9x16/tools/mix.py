"""Mix for the WeArt Ad Studio style ad: her creative's own sound, then her voiceover. No music, no sfx.
Both voices only get a gain stage and a peak limiter (no EQ, no compression, no effects). Writes assets/audio/mix.wav.
Run: python3 tools/mix.py
"""

import os

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, "..", "assets", "audio")
SR = 48000
DUR = 27.1
VO_AT = 9.4
TARGET_LUFS = -14.0


def load(name):
    a, sr = sf.read(os.path.join(A, name), dtype="float64")
    assert sr == SR
    return a if a.ndim == 1 else a.mean(1)


def lufs(x):
    # simple BS.1770-ish estimate: K-weighting skipped, RMS of gated blocks, close enough for gain matching
    blk = int(0.4 * SR)
    p = [np.mean(x[i : i + blk] ** 2) for i in range(0, len(x) - blk, blk // 4)]
    p = [v for v in p if v > 1e-7]
    return -0.691 + 10 * np.log10(np.mean(p))


c = load("creative-voice.wav")
v = load("voiceover.wav")
mix = np.zeros(int(DUR * SR))
# match both voices to the same loudness first
gc = 10 ** ((TARGET_LUFS - lufs(c)) / 20)
gv = 10 ** ((TARGET_LUFS - lufs(v)) / 20)
mix[: len(c)] += c * gc
i = int(VO_AT * SR)
mix[i : i + len(v)] += v * gv
sf.write(os.path.join(A, "mix_raw.wav"), mix.astype(np.float32), SR)
# the creative has one plosive spike (-4.8 dBFS): a transparent peak limiter keeps the loudness up, nothing else touches the voices
import subprocess
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(A, "mix_raw.wav"), "-af", "alimiter=limit=0.84:attack=3:release=60:level=disabled", os.path.join(A, "mix.wav")], check=True)
os.remove(os.path.join(A, "mix_raw.wav"))
print("gain creative %.1f dB, voiceover %.1f dB" % (20 * np.log10(gc), 20 * np.log10(gv)))

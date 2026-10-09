"""Male English voiceover for the WeArt UGC ad (Kokoro TTS, offline).

Needs kokoro-onnx plus kokoro-v1.0.onnx / voices-v1.0.bin in $KOKORO_DIR.
Writes assets/audio/vo/<key>.wav and prints each clip's duration.
"""

import os

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

LINES = {
    "stamps": "No actor. No camera. Just two clicks on WeArt Studio.",
    "cta": "Create UGC ads in minutes with WeArt Studio.",
}
VOICE = os.environ.get("VOICE", "am_michael")
SPEED = float(os.environ.get("SPEED", "1.08"))

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets", "audio", "vo")
K = os.environ["KOKORO_DIR"]
kok = Kokoro(os.path.join(K, "kokoro-v1.0.onnx"), os.path.join(K, "voices-v1.0.bin"))

for key, text in LINES.items():
    audio, sr = kok.create(text, voice=VOICE, speed=SPEED, lang="en-us")
    idx = np.where(np.abs(audio) > 0.01)[0]
    audio = audio[max(0, idx[0] - 800) : idx[-1] + 2400]
    audio = audio / np.max(np.abs(audio)) * 0.89
    sf.write(os.path.join(OUT, f"{key}.wav"), audio.astype(np.float32), sr)
    print(key, round(len(audio) / sr, 2), VOICE, text)

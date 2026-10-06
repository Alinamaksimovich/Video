"""English voiceover for the WeArt promo, one clip per scene (Kokoro TTS, offline).

Needs kokoro-onnx plus kokoro-v1.0.onnx / voices-v1.0.bin (GitHub release
thewh1teagle/kokoro-onnx model-files-v1.0) in $KOKORO_DIR.
Writes assets/audio/vo/sN.wav and prints each clip's duration.
"""

import os
import sys

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

LINES = {
    "s1": "Paying for every AI separately?",
    "s2": "Meet WeArt Studio. All A.I. in one place.",
    "s3": "Type your idea, pick a model, and hit generate.",
    "s4": "Images, video, audio and chat. Every top model.",
    "s5": "Build whole pipelines on Canvas.",
    "s6": "One subscription instead of five.",
    "s7": "WeArt Studio. Start creating now.",
}
VOICE = os.environ.get("VOICE", "af_heart")
SPEED = float(os.environ.get("SPEED", "1.08"))

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets", "audio", "vo")
K = os.environ["KOKORO_DIR"]
kok = Kokoro(os.path.join(K, "kokoro-v1.0.onnx"), os.path.join(K, "voices-v1.0.bin"))

for key, text in LINES.items():
    audio, sr = kok.create(text, voice=VOICE, speed=SPEED, lang="en-us")
    # trim leading/trailing silence
    idx = np.where(np.abs(audio) > 0.01)[0]
    audio = audio[max(0, idx[0] - 800) : idx[-1] + 2400]
    audio = audio / np.max(np.abs(audio)) * 0.89
    sf.write(os.path.join(OUT, f"{key}.wav"), audio.astype(np.float32), sr)
    print(key, round(len(audio) / sr, 2), sr, text)

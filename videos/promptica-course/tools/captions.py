"""Word timings for the captions, from the known script + the voice energy envelope.

Each phrase has a hand-checked window; inside it, words are spread over the
voiced frames in proportion to their vowel count. Prints captions.json.
"""

import json
import os
import sys

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
PHRASES = [
    (0.00, 1.82, "Этот ролик я собрала за 10 минут."),
    (2.05, 4.46, "Claude мне дал полную раскадровку по секундам."),
    (4.76, 8.75, "Далее всё, что нужно, — это просто подключить нужные инструменты и делать все правки голосом."),
    (9.86, 11.27, "Сделай тише, сделай короче."),
    (11.85, 12.82, "Как сделать так же —"),
    (13.18, 15.58, "мы расскажем в своём курсе. Подписывайся, чтобы не пропустить."),
]
VOWELS = set("аеёиоуыэюяaeiouy")


def weight(w):
    n = sum(c in VOWELS for c in w.lower())
    if w.isdigit():
        n = 3  # "десять"
    return max(1, n)


a, sr = sf.read(os.path.join(HERE, "..", "assets", "audio", "voice-raw.wav"), dtype="float32")
hop = int(sr * 0.01)
rms = np.sqrt(np.convolve(a**2, np.ones(hop * 3) / (hop * 3), mode="same"))[::hop]
voiced = rms > np.max(rms) * 0.04

words = []
for s, e, text in PHRASES:
    toks = [t for t in text.split() if t != "—"]
    idx = np.arange(int(s * 100), min(int(e * 100), len(voiced)))
    v = idx[voiced[idx]]
    if len(v) == 0:
        v = idx
    cw = np.cumsum([0] + [weight(t) for t in toks]) / sum(weight(t) for t in toks)
    for i, t in enumerate(toks):
        a0 = v[min(len(v) - 1, int(cw[i] * len(v)))] / 100
        a1 = v[min(len(v) - 1, max(0, int(cw[i + 1] * len(v)) - 1))] / 100 + 0.01
        words.append({"w": t, "s": round(a0, 2), "e": round(max(a1, a0 + 0.12), 2)})
json.dump(words, sys.stdout, ensure_ascii=False)

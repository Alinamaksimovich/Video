"""Tighten + sound-design the 30 s WeArt "aging guy" clip (480x854) into a 9:16 1080x1920 cut.

Cuts: the 3.5 s of eye-darting at the start (kept: the last 1.1 s, eyes flick then lock onto the camera),
every pause between phrases (down to ~0.2 s), and the 6 s without speech while the old man walks up
(sped up 2.5x and cut to the wink). SFX come from sfx-library (her packs), her voice is untouched.
Run: python3 tools/edit.py   ->  renders/weart-guy-cut.mp4
"""

import os
import subprocess

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "assets", "source.mp4")
SFXD = os.path.join(HERE, "..", "assets", "sfx")
OUT = os.path.join(HERE, "..", "renders")
SR = 44100

# (src start, src end, speed, audio: "orig" keeps the recording, "tone" = room tone only)
CHUNKS = [
    (2.55, 5.24, 1.0, "orig"),  # eyes flick -> lock on camera -> "I'm not real."
    (5.50, 11.55, 1.0, "orig"),  # "I was made on WeArt Studio in two clicks, and my background also one click."
    (12.02, 12.40, 1.0, "orig"),  # "Yep,"
    (12.70, 13.42, 1.0, "orig"),  # "it was a set."
    (14.10, 17.60, 1.0, "orig"),  # "One more click." + the hand-swipe that ages him + "Back in my day,"
    (17.76, 19.80, 1.0, "orig"),  # "this took a whole crew."
    (19.90, 22.70, 2.5, "tone"),  # he walks up to the camera (sped up)
    (22.80, 24.00, 1.0, "tone"),  # wink + smile
    (25.44, 30.04, 1.0, "orig"),  # "Create your ideas in WeArt Studio."
]

# SFX: (file, source time, gain dB). Source times are mapped through the cut list.
SFX = [
    ("SJC_DSLR_Focus_Beep_02", 3.10, -12),  # eyes lock onto the camera
    ("whoosh_shine", 3.40, -10),  # pull-back to the wide shot
    ("SJC_BLEEP_Cute_Double_Bleep_01", 6.90, -13),  # "WeArt Studio"
    ("SJC_CLICK_Tonal_Click_Double_01", 7.92, -8),  # "two clicks"
    ("whoosh_shine", 9.50, -11),  # the sky backdrop is pulled away
    ("SJC_IMPACT_Liquid_Impact_01", 10.45, -10),
    ("SJC_CLICK_Tonal_Click_Double_01", 11.18, -8),  # "one click"
    ("SJC_CLICK_Woodblock_01", 12.12, -12),  # "Yep"
    ("SJC_CLICK_Tonal_Click_Double_01", 14.50, -8),  # "one more click"
    ("whoosh_shine", 14.68, -9),  # the swipe
    ("SJC_FILMCAMERA_Leaf_Shutter_04", 15.05, -6),  # he is old
    ("SJC_IMPACT_Liquid_Impact_01", 15.08, -10),
    ("whoosh_shine", 19.90, -9),  # the speed ramp
    ("SJC_DSLR_Focus_Beep_01", 23.05, -9),  # wink
    ("SJC_DSLR_Flash_Close_02", 23.10, -11),
    ("SJC_POP_PopUp_Soft_02", 25.50, -13),
    ("SJC_BLEEP_Cute_Double_Bleep_01", 29.62, -11),  # "...Studio"
]


def out_time(t):
    acc = 0.0
    for s, e, sp, _ in CHUNKS:
        if s <= t <= e:
            return acc + (t - s) / sp
        acc += (e - s) / sp
    raise ValueError(t)


def load(path):
    a, sr = sf.read(path, dtype="float64")
    if a.ndim == 1:
        a = np.stack([a, a], 1)
    if sr == 48000:
        a = resample_poly(a, 147, 160, axis=0)
    elif sr != SR:
        raise ValueError((path, sr))
    return a


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    tmp_a = os.path.join(OUT, "_a.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-vn", "-ar", str(SR), "-ac", "2", tmp_a], check=True)
    src = load(tmp_a)
    tone = src[int(0.3 * SR) : int(3.3 * SR)]  # silent room tone

    # ---- audio: chunk by chunk, 12 ms fades at every join ----
    parts = []
    fade = int(0.012 * SR)
    for s, e, sp, mode in CHUNKS:
        n = int(round((e - s) / sp * SR))
        if mode == "orig":
            seg = src[int(s * SR) : int(s * SR) + n].copy()
        else:
            seg = np.tile(tone, (n // len(tone) + 1, 1))[:n].copy()
        seg = np.pad(seg, ((0, max(0, n - len(seg))), (0, 0)))
        seg[:fade] *= np.linspace(0, 1, fade)[:, None]
        seg[-fade:] *= np.linspace(1, 0, fade)[:, None]
        parts.append(seg)
    voice = np.concatenate(parts)
    total = len(voice) / SR

    # ---- sfx: peak = her speech peak minus (3 dB + cue gain) ----
    speech_peak = np.abs(voice).max()
    sfx = np.zeros_like(voice)
    for name, t, g in SFX:
        s = load(os.path.join(SFXD, name + ".wav"))
        s = s / np.abs(s).max() * speech_peak * 10 ** ((g - 3.0) / 20)
        i = int(out_time(t) * SR)
        j = min(len(sfx), i + len(s))
        sfx[i:j] += s[: j - i]
    mix = voice + sfx
    mix = mix / max(1.0, np.abs(mix).max() / 0.95)
    sf.write(tmp_a, mix.astype(np.float32), SR)

    # ---- video: trim/speed each chunk, concat, upscale to 1080x1920 ----
    f = []
    for i, (s, e, sp, _) in enumerate(CHUNKS):
        f.append(f"[0:v]trim=start={s}:end={e},setpts=(PTS-STARTPTS)/{sp},fps=30[v{i}]")
    cat = "".join(f"[v{i}]" for i in range(len(CHUNKS)))
    f.append(f"{cat}concat=n={len(CHUNKS)}:v=1:a=0,scale=1080:1920:flags=lanczos,unsharp=5:5:0.6:5:5:0,format=yuv420p[v]")
    raw = os.path.join(OUT, "_raw.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-filter_complex", ";".join(f), "-map", "[v]", "-c:v", "libx264", "-crf", "16", "-preset", "medium", raw], check=True)
    final = os.path.join(OUT, "weart-guy-cut.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-i", tmp_a, "-c:v", "copy", "-af", "volume=1.5dB,alimiter=limit=0.89:attack=5:release=60:level=false", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", final], check=True)
    os.remove(raw)
    os.remove(tmp_a)
    print("ok", round(total, 2), "s ->", final)

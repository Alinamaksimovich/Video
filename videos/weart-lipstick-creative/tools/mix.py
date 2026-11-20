"""Final audio: music bed (whole piece) + the result video's own natural sounds (from 11.8 s).
Video sounds get one gain so they sit ~4 dB over the music while the video plays; music dips a little there.
Writes assets/audio/mix.wav; final loudness is set on the rendered mp4 (ffmpeg, one gain)."""
import os, subprocess, numpy as np, soundfile as sf
H = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SR = 44100; VID_AT = 11.8; DUR = 29.0
m, sr = sf.read(os.path.join(H, "assets/audio/music.wav")); assert sr == SR
tmp = os.path.join(H, "assets/audio/_vid.wav")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", os.path.join(H, "assets/video/result.mp4"), "-ac", "2", "-ar", str(SR), tmp], check=True)
v, _ = sf.read(tmp); os.remove(tmp)
rms = lambda x: np.sqrt(np.mean(x**2) + 1e-12)
i = int(VID_AT * SR); j = min(len(m), i + len(v))
mus_seg = m[i:j]
v = v[: j - i] * (rms(mus_seg) * 10 ** (4 / 20) / rms(v))   # one gain for the sounds
duck = np.ones(len(m)); r = int(0.3 * SR)
duck[i:j] = 0.7; duck[i - r:i] = np.linspace(1, 0.7, r); duck[j:j + r] = np.linspace(0.7, 1, min(r, len(m) - j))
out = m * duck[:, None]
out[i:j] += v
out /= np.abs(out).max() / 0.89
sf.write(os.path.join(H, "assets/audio/mix.wav"), out.astype(np.float32), SR)
print("ok")

"""Speed-ramped edit of the raw screen recording onto the promo timeline.

Each row maps a final-timeline slot to a source range of the recording; the
range is retimed to fill the slot exactly. Output: assets/video/screen-edit.mp4
(H.264, silent, 30 fps, 20 s). Run: python3 tools/edit_screen.py
"""

import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "assets", "video", "recording-src.mov")
OUT = os.path.join(HERE, "..", "assets", "video", "screen-edit.mp4")

# (final_start, final_end, src_start, src_end)
EDL = [
    (0.0, 1.0, 1.15, 1.75),  # hook: selfie
    (1.0, 2.0, 4.30, 5.05),  # hook: jeans photo
    (2.0, 3.0, 14.55, 15.55),  # hook: finished look
    (3.0, 7.0, 0.00, 3.05),  # avatar: selfie → avatar updated
    (7.0, 9.0, 3.05, 5.05),  # add item: menu → jeans photo
    (9.0, 11.0, 5.05, 8.50),  # category → AI cut-out → check → add
    (11.0, 12.0, 8.50, 9.25),  # wardrobe with the new jeans
    (12.0, 13.6, 9.25, 12.00),  # pick jeans + jacket, tap try on
    (13.6, 15.4, 12.00, 14.53),  # "trying on…"
    (15.4, 17.0, 14.53, 16.08),  # result
    (17.0, 19.0, 16.10, 16.82),  # save sheet
    (19.0, 20.0, 16.83, 17.20),  # saved outfit page
]

parts = []
for i, (fs, fe, ss, se) in enumerate(EDL):
    factor = (fe - fs) / (se - ss)  # >1 slows down
    parts.append(
        f"[0:v]trim=start={ss}:end={se},setpts=(PTS-STARTPTS)*{factor:.6f},"
        f"fps=30,trim=duration={fe - fs},setpts=PTS-STARTPTS,"
        f"tpad=stop_mode=clone:stop_duration=0.2,trim=duration={fe - fs}[v{i}]"
    )
graph = ";".join(parts) + ";" + "".join(f"[v{i}]" for i in range(len(EDL))) + f"concat=n={len(EDL)}:v=1:a=0,format=yuv420p[out]"

subprocess.run(
    ["ffmpeg", "-y", "-loglevel", "error", "-i", SRC, "-filter_complex", graph, "-map", "[out]",
     "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-r", "30", "-movflags", "+faststart", OUT],
    check=True,
)
print("ok", OUT)

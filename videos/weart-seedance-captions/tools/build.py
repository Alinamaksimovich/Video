"""Builds index.html: her video untouched + captions on bright yellow pills from "How do" to the end.

CAPS = (line1, t1, line2, t2): line 1 pops on its first word, line 2 on its first word.
Times come from Whisper (incremental decode), rounded by hand. Run: python3 tools/build.py
"""

import os

DUR = 28.566667
END = DUR
CAPS = [
    ("HOW DO", 7.75, "PEOPLE MAKE", 8.08),
    ("VIDEOS LIKE", 8.55, "THIS", 8.98),
    ("IN A", 9.45, "MINUTE?", 9.72),
    ("YOU ONLY", 10.40, "NEED TWO", 10.72),
    ("FILES:", 11.0, "A TRENDING", 11.55),
    ("VIDEO", 12.10, "AND ONE", 12.40),
    ("PHOTO.", 13.0, None, None),
    ("OPEN WEART", 14.0, "STUDIO,", 15.05),
    ("GO TO", 15.55, "THE VIDEO", 15.90),
    ("GENERATOR", 16.15, "AND PICK", 16.95),
    ("SEEDANCE.", 17.25, None, None),
    ("UPLOAD THE", 18.30, "CLIP AS", 18.80),
    ("THE MOTION,", 19.05, "YOUR PHOTO", 19.60),
    ("AS THE", 19.95, "LEAD,", 20.25),
    ("PASTE THE", 20.60, "PROMPT", 21.30),
    ("AND HIT", 21.65, "GENERATE.", 22.05),
    ("A COUPLE", 22.60, "OF MINUTES", 22.90),
    ("LATER,", 23.12, "YOU'VE GOT", 23.50),
    ("A TRENDING", 23.98, "VIDEO", 24.45),
    ("STARRING", 24.70, "YOU.", 25.15),
    ("TAP THE", 25.45, "LINK AND", 25.90),
    ("MAKE YOUR", 26.36, "FIRST VIDEO", 26.75),
    ("RIGHT NOW.", 27.25, None, None),
]


def cap_html(i, c):
    l1, t1, l2, t2 = c
    end = CAPS[i + 1][1] if i + 1 < len(CAPS) else END
    lines = f'<span class="ln" id="c{i}a">{l1}</span>'
    if l2:
        lines += f'<span class="ln" id="c{i}b">{l2}</span>'
    return f'      <div class="cap clip" id="c{i}" data-start="{t1}" data-duration="{round(end - t1, 3)}" data-track-index="{2 + i % 2}">{lines}</div>'


html = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>WeArt Seedance captions</title>
    <script src="assets/vendor/gsap.min.js"></script>
    <style>
      @font-face {{
        font-family: "Roboto Flex";
        src: url("assets/fonts/rf-lat.woff2") format("woff2");
        font-weight: 100 1000;
        font-stretch: 25% 151%;
      }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: #000; }}
      #root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; background: #000; font-family: "Roboto Flex", system-ui, sans-serif; }}
      #v {{ position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; }}
      /* caption zone: fixed, centred; lines are stacked pills */
      .cap {{ position: absolute; left: 0; width: 1080px; top: 1380px; height: 260px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 14px; }}
      .ln {{ display: block; padding: 8px 30px 12px; border-radius: 22px; background: #effc00; color: #0b0b0b; font-size: 84px; font-weight: 900; font-stretch: 100%; line-height: 1.02; letter-spacing: -0.01em; white-space: nowrap; opacity: 0; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35); }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1080" data-height="1920">
      <video id="v" class="clip" src="assets/video/clip.mp4" playsinline data-has-audio="true" data-start="0" data-duration="{DUR}" data-media-start="0" data-track-index="1"></video>
{chr(10).join(cap_html(i, c) for i, c in enumerate(CAPS))}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true, defaults: {{ immediateRender: false }} }});
      const CAPS = {[[f"c{i}", c[1], c[3]] for i, c in enumerate(CAPS)]};
      const pop = (sel, t) => tl.fromTo(sel, {{ opacity: 0, y: 24 }}, {{ opacity: 1, y: 0, duration: 0.18, ease: "power2.out" }}, t);
      CAPS.forEach(([id, t1, t2]) => {{
        pop("#" + id + "a", t1);
        if (t2 !== null) pop("#" + id + "b", t2);
      }});
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
""".replace("None", "null")

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "index.html")
open(out, "w").write(html)
print("ok", len(CAPS), "captions")

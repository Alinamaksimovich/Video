"""Builds index.html: her video untouched + captions on bright yellow pills from "How to" to the end.

CAPS = (line1, t1, line2, t2): line 1 pops on its first word, line 2 on its first word.
Times come from Whisper (incremental decode), rounded by hand. Run: python3 tools/build.py
"""

import os

DUR = 27.033333
END = DUR
CAPS = [
    ("HOW TO", 6.10, "MAKE VIDEO", 6.36),
    ("LIKE THIS", 6.75, None, None),
    ("IN ONE", 7.60, "MINUTE?", 8.10),
    ("YOU ONLY", 9.05, "NEED TWO", 9.45),
    ("FILES:", 9.80, "A TRENDING", 10.15),
    ("VIDEO", 10.60, "AND ONE", 11.20),
    ("PHOTO.", 11.60, None, None),
    ("OPEN WEART", 12.50, "STUDIO,", 13.50),
    ("GO TO", 13.95, "THE VIDEO", 14.38),
    ("GENERATOR", 14.60, "AND PICK", 15.40),
    ("SEEDANCE.", 15.80, None, None),
    ("UPLOAD THE", 16.95, "CLIP AS", 17.40),
    ("THE MOTION,", 17.75, "YOUR PHOTO", 18.15),
    ("AS THE", 18.60, "LEAD,", 18.95),
    ("PASTE THE", 19.60, "PROMPT", 19.85),
    ("AND HIT", 20.10, "GENERATE.", 20.65),
    ("A COUPLE", 21.10, "OF MINUTES", 21.32),
    ("LATER,", 21.55, "YOU'VE GOT", 22.05),
    ("A TRENDING", 22.50, "VIDEO", 22.95),
    ("STARRING", 23.40, "YOU.", 23.70),
    ("TAP THE", 23.95, "LINK AND", 24.40),
    ("MAKE YOUR", 24.75, "FIRST VIDEO", 25.20),
    ("RIGHT NOW.", 25.75, None, None),
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
    <title>WeArt tutorial captions</title>
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
      .cap {{ position: absolute; left: 0; width: 1080px; top: 1480px; height: 260px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 14px; }}
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

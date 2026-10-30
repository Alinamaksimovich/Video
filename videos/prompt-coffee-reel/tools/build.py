"""Builds index.html for the prompt reel: her voice, three result videos, two-line captions.
Captions: 2 lines x 2 words (1 word per line next to video 3), timed to her voice
(whisper-small segments + manual word placement). Run: python3 tools/build.py
"""

import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "index.html")
END = 34.09

S1, S2, S3, S4 = 2.82, 10.0, 18.71, 27.21  # sections: video 1, video 2, video 3, call to action

# (line1, t1, line2, t2, zone, dx, dy)  - zone sets where the block sits, dx/dy make it hop a little
CAPS = [
    ("Один запрос", 0.30, "три результата", 1.69, "center", 0, 0),
    ("Первый кадр,", 2.82, "три слова", 3.64, "bottom", -30, 0),
    ("в запросе.", 4.15, "Нейросеть", 4.94, "bottom", 35, -40),
    ("дорисовала", 5.30, "всё сама.", 5.85, "bottom", -20, 30),
    ("и вышел", 6.59, "случайный свет", 7.13, "bottom", 25, -20),
    ("и пластиковая", 7.95, "кожа.", 8.85, "bottom", -35, 25),
    ("Второй.", 10.06, "", None, "top", 20, 0),
    ("Человек решил", 10.89, "наверняка", 11.65, "top", -25, 30),
    ("и накидал", 12.18, "в запрос", 12.72, "top", 30, -20),
    ("10 модных", 13.21, "слов.", 13.75, "top", -20, 20),
    ("Стили спорят", 14.51, "друг с другом,", 14.95, "top", 25, -25),
    ("и в кадре", 15.85, "получилась", 16.60, "top", -30, 15),
    ("каша.", 17.80, "", None, "top-big", 0, 0),
    ("Третий.", 18.71, "", None, "right", 0, 0),
    ("Запрос", 19.45, "по структуре:", 19.85, "right", 0, -40),
    ("Кто", 20.89, "в кадре,", 21.12, "right", 20, 40),
    ("что", 21.64, "делает,", 21.90, "right", -10, -30),
    ("откуда", 22.45, "свет,", 22.85, "right", 15, 30),
    ("какая", 23.42, "мимика?", 23.80, "right", -5, -45),
    ("Видны", 24.46, "поры,", 24.86, "right", 20, 20),
    ("свет", 25.30, "мягкий,", 25.65, "right", 0, -20),
    ("и мимика", 26.23, "живая.", 26.70, "right", -10, 35),
    ("Шаблон структуры", 27.21, "промптов", 28.09, "center", 0, -20),
    ("я собрала", 28.60, "у себя", 29.30, "center", 30, 20),
    ("в телеграме.", 29.65, "", None, "center", -25, 0),
    ("Напиши любой", 30.83, "смайлик", 31.35, "center", 20, -25),
    ("под этим", 31.93, "видео", 32.40, "center", -30, 20),
    ("и я пришлю", 32.75, "тебе ссылку", 33.40, "center", 15, -10),
]

P2 = ("beautiful girl with coffee, ultra realistic, 8k, hyper detailed, cinematic, masterpiece, best quality, "
      "golden hour, studio light, dramatic lighting, soft light, bokeh, vibrant colors, moody, warm tones, "
      "cold tones, perfect face, perfect hands, anime style, photorealistic")
P3 = ("Young woman with a loose low ponytail holding a white ceramic mug with both hands by a window, soft morning "
      "daylight from the left at 45 degrees, a calm relaxed expression, a faint half-smile, eyes looking at the mug. "
      "Cozy bright apartment, a blurred plant in the background. Natural matte skin with visible pores and fine "
      "peach-fuzz hairs, no plastic effect. Shot on a full-frame camera, 85mm, shallow depth of field, fine grain.")

ZONE = {  # css for the caption block
    "center": "left: 0; width: 1080px; top: 900px; text-align: center; font-size: 84px;",
    "bottom": "left: 0; width: 1080px; top: 1440px; text-align: center; font-size: 84px;",
    "top": "left: 0; width: 1080px; top: 250px; text-align: center; font-size: 84px;",
    "top-big": "left: 0; width: 1080px; top: 300px; text-align: center; font-size: 170px;",
    "right": "left: 620px; width: 440px; top: 760px; text-align: center; font-size: 52px;",
}


def cap_html(i, c):
    l1, t1, l2, t2, zone, dx, dy = c
    style = ZONE[zone] + f" margin-top: {dy}px;"
    end = CAPS[i + 1][1] if i + 1 < len(CAPS) else END
    lines = f'<div class="ln" id="c{i}a">{l1}</div>'
    if l2:
        lines += f'<div class="ln" id="c{i}b">{l2}</div>'
    return (f'      <div class="cap clip" id="c{i}" style="{style}" data-start="{t1:.2f}" '
            f'data-duration="{end - t1:.2f}" data-track-index="20">{lines}</div>')


def video(id_, src, start, dur, mstart, style, track, alt):
    return (f'<div class="card" id="{id_}" style="{style}{"; opacity: 0" if id_[0] in "ae" else ""}"><video id="{id_}v" src="assets/video/{src}" muted playsinline '
            f'data-start="{start}" data-duration="{dur:.2f}" data-media-start="{mstart}" data-track-index="{track}" '
            f'aria-label="{alt}"></video></div>')


def trio(prefix, start, end, mstart, track0):
    d = end - start
    pos = [
        ("v1-three-words.mp4", "left: 70px; top: 250px; width: 360px; height: 520px; --r: -6deg", "результат запроса из трёх слов"),
        ("v2-long-prompt.mp4", "left: 650px; top: 300px; width: 360px; height: 520px; --r: 5deg", "результат запроса из десяти модных слов"),
        ("v3-structure.mp4", "left: 360px; top: 1240px; width: 360px; height: 560px; --r: -3deg", "результат структурного запроса"),
    ]
    return "\n        ".join(video(f"{prefix}{k}", s, start, d, mstart, st, track0 + k, a) for k, (s, st, a) in enumerate(pos))


html = f"""<!doctype html>
<html lang="ru">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>Один запрос — три результата</title>
    <script src="assets/vendor/gsap.min.js"></script>
    <style>
      @font-face {{
        font-family: "Helios Ext";
        src: url("assets/fonts/HeliosExtC.ttf") format("truetype");
      }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: #ffffff; }}
      #root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; background: #ffffff; color: #111111; font-family: "Helios Ext", sans-serif; }}
      .scene {{ position: absolute; inset: 0; opacity: 0; }}
      .card {{ position: absolute; overflow: hidden; border-radius: 34px; background: #eeeeee; box-shadow: 0 24px 60px rgba(0, 0, 0, 0.18); transform: rotate(var(--r, 0deg)); }}
      .card video {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
      .cap {{ position: absolute; line-height: 1.12; white-space: nowrap; }}
      .ln {{ opacity: 0; }}
      .prompt {{ position: absolute; font-family: "DejaVu Sans", sans-serif; font-size: 23px; line-height: 1.38; color: #707070; }}
      .prompt b {{ color: #111111; font-weight: 700; letter-spacing: 0.08em; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{END}" data-width="1080" data-height="1920">
      <!-- her voice, untouched (gain only at export) + light SFX from her library (tools/sfx.py); no music -->
      <audio id="voice" src="assets/audio/voice.wav" data-start="0" data-duration="{END}" data-track-index="10" data-volume="1"></audio>
      <audio id="sfx" src="assets/audio/sfx.wav" data-start="0" data-duration="{END}" data-track-index="11" data-volume="1"></audio>

      <!-- intro: one prompt, three results -->
      <div class="scene" id="s0">
        {trio("a", 0, S1, 0, 1)}
      </div>

      <!-- 1 · three words: centre, captions below -->
      <div class="scene" id="s1">
        <div class="prompt" style="left: 170px; top: 170px; width: 740px"><b>ПРОМПТ</b>&nbsp; girl with coffee</div>
        {video("b", "v1-three-words.mp4", S1, S2 - S1, 0, "left: 170px; top: 240px; width: 740px; height: 1110px", 4, "результат запроса из трёх слов")}
      </div>

      <!-- 2 · ten buzzwords: a little below centre, captions on top -->
      <div class="scene" id="s2">
        {video("c", "v2-long-prompt.mp4", S2, S3 - S2, 0, "left: 200px; top: 600px; width: 680px; height: 1020px", 5, "результат запроса из десяти модных слов")}
        <div class="prompt" style="left: 90px; top: 1660px; width: 900px"><b>ПРОМПТ</b>&nbsp; {P2}</div>
      </div>

      <!-- 3 · structured prompt: off to the side, captions to the right, one word per line -->
      <div class="scene" id="s3">
        {video("d", "v3-structure.mp4", S3, S4 - S3, 0, "left: 50px; top: 300px; width: 560px; height: 996px", 6, "результат структурного запроса")}
        <div class="prompt" style="left: 50px; top: 1340px; width: 980px; font-size: 22px"><b>ПРОМПТ</b>&nbsp; {P3}</div>
      </div>

      <!-- call to action: all three again -->
      <div class="scene" id="s4">
        {trio("e", S4, END, 3, 7)}
      </div>

{chr(10).join(cap_html(i, c) for i, c in enumerate(CAPS))}
    </div>

    <script>
      const tl = gsap.timeline({{ paused: true, defaults: {{ immediateRender: false }} }});
      const pop = (sel, t) => tl.fromTo(sel, {{ opacity: 0, scale: 0.6 }}, {{ opacity: 1, scale: 1, duration: 0.32, ease: "back.out(2)" }}, t);

      // scenes are hard cuts on her words
      tl.set("#s0", {{ opacity: 1 }}, 0);
      tl.set("#s0", {{ opacity: 0 }}, {S1});
      tl.set("#s1", {{ opacity: 1 }}, {S1});
      tl.set("#s1", {{ opacity: 0 }}, {S2});
      tl.set("#s2", {{ opacity: 1 }}, {S2});
      tl.set("#s2", {{ opacity: 0 }}, {S3});
      tl.set("#s3", {{ opacity: 1 }}, {S3});
      tl.set("#s3", {{ opacity: 0 }}, {S4});
      tl.set("#s4", {{ opacity: 1 }}, {S4});

      // intro: the three results pop around "три результата"
      pop("#a0", 1.72);
      pop("#a1", 1.92);
      pop("#a2", 2.12);
      // each section's video
      tl.fromTo("#b", {{ opacity: 0, scale: 0.92 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "back.out(1.6)" }}, {S1});
      tl.fromTo("#c", {{ opacity: 0, scale: 0.92 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "back.out(1.6)" }}, {S2});
      tl.fromTo("#d", {{ opacity: 0, x: 200 }}, {{ opacity: 1, x: 0, duration: 0.35, ease: "power3.out" }}, {S3});
      tl.fromTo(".prompt", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, 0);
      // call to action: three again
      pop("#e0", {S4});
      pop("#e1", {S4 + 0.18});
      pop("#e2", {S4 + 0.36});

      // captions: each line pops in on its word
      const CAPS = {[[f"c{i}", c[1], c[3]] for i, c in enumerate(CAPS)]};
      CAPS.forEach(([id, t1, t2]) => {{
        tl.fromTo("#" + id + "a", {{ opacity: 0, y: 24, scale: 0.9 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.18, ease: "back.out(2.2)" }}, t1);
        if (t2 !== null) tl.fromTo("#" + id + "b", {{ opacity: 0, y: 24, scale: 0.9 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.18, ease: "back.out(2.2)" }}, t2);
      }});

      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
html = html.replace("None]", "null]")
with open(OUT, "w") as f:
    f.write(html)
print("ok", len(CAPS), "captions")

"""Builds index.html for the WeArt lipstick creative.

0-8.6 s   references (@image1 product, @image2 model) + the full prompt scrolling + Generate tap
8.6-11.8  storyboard: the 5 frames, in the order they were sent
11.8-26.84 the result video (its own sounds are in assets/audio/mix.wav, tools/mix.py)
26.9-29   WeArt logo
Run: python3 tools/build.py
"""

import html
import os
import re

H = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DUR = 29.0
VID_AT = 11.8
VID_LEN = 15.041667

prompt = open(os.path.join(H, "tools", "prompt.txt")).read().strip()
p = html.escape(prompt)
p = re.sub(r"@image([12])", r'<b class="tag">@image\1</b>', p)
p = re.sub(r"^(\d\d \| [^\n]+)$", r'<b class="sh">\1</b>', p, flags=re.M)
p = re.sub(r"^([A-Z][A-Z ]+:)", r'<b class="hd">\1</b>', p, flags=re.M)

SB = "".join(
    f'<div class="sb" id="sb{i}" style="left: {x}px; top: {y}px"><img src="assets/img/sb{i}.jpg" alt="Storyboard frame {i}" /><span>0{i}</span></div>'
    for i, (x, y) in enumerate([(60, 300), (390, 300), (720, 300), (225, 863), (555, 863)], 1)
)

doc = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>WeArt lipstick creative</title>
    <script src="assets/vendor/gsap.min.js"></script>
    <style>
      @font-face {{ font-family: "Roboto Flex"; src: url("assets/fonts/rf-lat.woff2") format("woff2"); font-weight: 100 1000; font-stretch: 25% 151%; }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: #05080f; }}
      #root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; font-family: "Roboto Flex", system-ui, sans-serif; color: #f5f7fa; background: radial-gradient(90% 55% at 50% 38%, #0f3a52 0%, #0a1e36 45%, #060b16 100%); }}
      .scene {{ position: absolute; inset: 0; opacity: 0; }}
      .card {{ position: absolute; border-radius: 48px; background: #11151f; border: 3px solid #272f45; box-shadow: 0 40px 100px rgba(0, 0, 0, 0.55); overflow: hidden; }}
      .ic {{ fill: none; stroke: #f5f7fa; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }}

      /* 1 · references + prompt */
      #hdr {{ position: absolute; left: 0; width: 1080px; top: 90px; display: flex; justify-content: center; align-items: center; gap: 22px; font-size: 44px; font-weight: 800; }}
      #hdr img {{ height: 52px; }}
      #hdr i {{ width: 3px; height: 44px; background: #3a4562; }}
      .ref {{ position: absolute; top: 210px; width: 300px; height: 420px; border-radius: 40px; }}
      .ref img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
      .ref span {{ position: absolute; left: 18px; bottom: 18px; padding: 8px 18px; border-radius: 20px; background: rgba(8, 12, 22, 0.78); font-size: 28px; font-weight: 700; white-space: nowrap; }}
      .ref span b {{ color: #d8f27f; }}
      #pc {{ left: 60px; top: 680px; width: 960px; height: 850px; padding: 36px 44px; }}
      #pc .top {{ display: flex; justify-content: space-between; align-items: center; font-size: 36px; font-weight: 800; }}
      #pc .top em {{ font-style: normal; font-size: 28px; font-weight: 600; color: #9aa6c2; }}
      #pmask {{ position: absolute; left: 44px; right: 44px; top: 110px; bottom: 30px; overflow: hidden; -webkit-mask-image: linear-gradient(180deg, transparent 0, #000 40px, #000 calc(100% - 90px), transparent 100%); mask-image: linear-gradient(180deg, transparent 0, #000 40px, #000 calc(100% - 90px), transparent 100%); }}
      #ptxt {{ padding-top: 30px; font-size: 30px; line-height: 1.42; font-weight: 400; color: #dfe5f2; white-space: pre-wrap; }}
      #ptxt .tag {{ color: #11151f; background: #d8f27f; border-radius: 10px; padding: 0 8px; font-weight: 800; }}
      #ptxt .sh {{ color: #d8f27f; font-weight: 800; }}
      #ptxt .hd {{ color: #ffffff; font-weight: 800; }}
      #bar {{ position: absolute; left: 60px; width: 960px; top: 1580px; height: 130px; display: flex; align-items: center; gap: 18px; }}
      .chip {{ height: 76px; padding: 0 28px; border-radius: 38px; background: #11151f; border: 3px solid #272f45; display: flex; align-items: center; gap: 12px; font-size: 32px; font-weight: 700; white-space: nowrap; }}
      .chip svg {{ width: 38px; height: 38px; }}
      #gen {{ margin-left: auto; height: 104px; padding: 0 44px; border-radius: 52px; background: #d8f27f; color: #11151f; display: flex; align-items: center; gap: 14px; font-size: 40px; font-weight: 900; }}
      #gen svg {{ width: 40px; height: 40px; }}
      #cur {{ position: absolute; left: 900px; top: 1670px; width: 76px; height: 76px; opacity: 0; }}

      /* 2 · storyboard */
      #sbt {{ position: absolute; left: 0; width: 1080px; top: 150px; text-align: center; font-size: 64px; font-weight: 900; letter-spacing: -0.01em; }}
      #sbt em {{ font-style: normal; color: #d8f27f; }}
      .sb {{ position: absolute; width: 300px; height: 533px; border-radius: 34px; overflow: hidden; border: 3px solid #272f45; box-shadow: 0 30px 70px rgba(0, 0, 0, 0.5); opacity: 0; }}
      .sb img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
      .sb span {{ position: absolute; left: 16px; top: 14px; padding: 4px 14px; border-radius: 16px; background: #d8f27f; color: #11151f; font-size: 26px; font-weight: 900; }}

      /* 3 · result */
      #vc {{ left: 70px; top: 140px; width: 940px; height: 1672px; }}
      #vc video {{ width: 100%; height: 100%; object-fit: cover; display: block; }}

      /* 4 · logo */
      #glow {{ position: absolute; left: 90px; top: 450px; width: 900px; height: 900px; border-radius: 50%; background: radial-gradient(closest-side, rgba(40, 150, 190, 0.55), rgba(40, 150, 190, 0)); }}
      #logo {{ position: absolute; left: 260px; top: 720px; width: 560px; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1080" data-height="1920">
      <audio id="mix" src="assets/audio/mix.wav" data-start="0" data-duration="{DUR}" data-track-index="10" data-volume="1"></audio>

      <div class="scene" id="s1">
        <div id="hdr"><img src="assets/img/wa-logo.png" alt="WeArt" /><i></i><svg viewBox="0 0 24 24" style="width: 52px; height: 52px"><rect class="ic" x="3" y="5" width="18" height="14" rx="3"/><path class="ic" d="M10 9l5 3-5 3z"/></svg>AI Video</div>
        <div class="card ref" id="r1" style="left: 210px"><img src="assets/img/product.jpg" alt="Product reference" /><span><b>@image1</b> Product</span></div>
        <div class="card ref" id="r2" style="left: 570px"><img src="assets/img/woman.jpg" alt="Model reference" /><span><b>@image2</b> Model</span></div>
        <div class="card" id="pc">
          <div class="top">Prompt<em>15 sec · 9:16 · 8 shots</em></div>
          <div id="pmask"><div id="ptxt">{p}</div></div>
        </div>
        <div id="bar">
          <div class="chip"><svg viewBox="0 0 24 24"><rect class="ic" x="3" y="5" width="18" height="14" rx="3"/><path class="ic" d="M10 9l5 3-5 3z"/></svg>Video</div>
          <div class="chip">15 sec</div>
          <div class="chip">9:16</div>
          <div id="gen"><svg viewBox="0 0 24 24"><path d="M12 2l2.200 6.800L21 11l-6.800 2.200L12 20l-2.200-6.800L3 11l6.800-2.200z" fill="#11151f"/></svg>Generate</div>
        </div>
        <svg id="cur" viewBox="0 0 24 24"><path d="M5 3l14 8-6 1.500L10 19z" fill="#f5f7fa" stroke="#11151f" stroke-width="1.400" stroke-linejoin="round"/></svg>
      </div>

      <div class="scene" id="s2">
        <div id="sbt">Storyboard</div>
        {SB}
      </div>

      <div class="scene" id="s3">
        <div class="card" id="vc"><video id="res" class="clip" src="assets/video/result.mp4" muted playsinline data-start="{VID_AT}" data-duration="{VID_LEN}" data-media-start="0" data-track-index="1"></video></div>
      </div>

      <div class="scene" id="s4">
        <div id="glow"></div>
        <img id="logo" src="assets/img/wa-logo.png" alt="WeArt Studio" />
      </div>
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true, defaults: {{ immediateRender: false }} }});
      const pop = (sel, t, st) => tl.fromTo(sel, {{ opacity: 0, scale: 0.88, y: 30 }}, {{ opacity: 1, scale: 1, y: 0, duration: 0.4, ease: "back.out(1.6)", stagger: st || 0 }}, t);

      // 1 · references + prompt
      tl.to("#s1", {{ opacity: 1, duration: 0.25 }}, 0);
      pop("#hdr", 0.05);
      pop("#r1", 0.3);
      pop("#r2", 0.55);
      pop("#pc", 0.9);
      pop("#bar .chip, #gen", 1.1, 0.08);
      const ptxt = document.getElementById("ptxt");
      const maskH = document.getElementById("pmask").clientHeight;
      const scroll = Math.max(0, ptxt.scrollHeight - maskH + 60);
      tl.fromTo("#ptxt", {{ y: 0 }}, {{ y: -scroll, duration: 6.0, ease: "power1.inOut" }}, 1.5);
      tl.fromTo("#cur", {{ x: 120, y: 160, opacity: 0 }}, {{ x: 0, y: 0, opacity: 1, duration: 0.35, ease: "power3.out" }}, 7.4);
      tl.to("#gen", {{ scale: 0.92, duration: 0.08, ease: "power2.in" }}, 7.85);
      tl.to("#gen", {{ scale: 1, duration: 0.25, ease: "back.out(3)" }}, 7.93);
      tl.to("#s1", {{ opacity: 0, y: -40, duration: 0.3, ease: "power2.in" }}, 8.35);

      // 2 · storyboard
      tl.to("#s2", {{ opacity: 1, duration: 0.2 }}, 8.6);
      pop("#sbt", 8.6);
      pop(".sb", 8.8, 0.22);
      tl.to("#s2", {{ opacity: 0, scale: 1.04, duration: 0.25, ease: "power2.in" }}, 11.55);

      // 3 · result
      tl.fromTo("#s3", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.01 }}, {VID_AT});
      tl.fromTo("#vc", {{ scale: 0.94 }}, {{ scale: 1, duration: 0.5, ease: "power3.out" }}, {VID_AT});
      tl.to("#s3", {{ opacity: 0, duration: 0.2 }}, {round(VID_AT + VID_LEN - 0.05, 3)});

      // 4 · logo
      tl.to("#s4", {{ opacity: 1, duration: 0.3 }}, 26.9);
      tl.fromTo("#logo", {{ opacity: 0, scale: 0.85 }}, {{ opacity: 1, scale: 1, duration: 0.6, ease: "back.out(1.6)" }}, 26.95);
      tl.fromTo("#glow", {{ opacity: 0, scale: 0.6 }}, {{ opacity: 1, scale: 1, duration: 0.9, ease: "power2.out" }}, 26.9);

      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
open(os.path.join(H, "index.html"), "w").write(doc)
print("ok")

"""Write out/index.html: the final video plus source/reference comparison sheets.

    .venv/bin/python make_preview.py
"""
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "out")

PAGE = """<!doctype html>
<html lang="en"><meta charset="utf-8">
<title>No After Effects. Just Clawd. — recreation</title>
<style>
 body{{margin:0;background:#17110d;color:#e9ddd3;font:15px/1.5 -apple-system,Helvetica,sans-serif}}
 main{{max-width:1280px;margin:0 auto;padding:32px}}
 h1{{font-size:28px;margin:0 0 4px}} h1 span{{color:#d97757}}
 h2{{font-size:16px;margin:36px 0 10px;color:#d97757;letter-spacing:.06em;text-transform:uppercase}}
 video,img{{width:100%;border-radius:8px;background:#000;display:block}}
 .pair{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
 figcaption{{font-size:13px;color:#a8988b;margin:6px 0 0}}
 code{{color:#f2a272}}
</style>
<main>
<h1>No After Effects. <span>Just Clawd.</span></h1>
<p>Local procedural restaging: HTML/canvas UI textures, Blender Cycles, numpy/scipy/pedalboard soundtrack, FFmpeg encode. 12.0 s, 30 fps, 1920x1080, 360 frames.</p>
<video src="clawd_no_after_effects.mp4" controls playsinline preload="auto" poster="poster.png"></video>
<h2>Recreation at 0.0, 0.5 … 11.5 s</h2>
<div class="pair">
 <figure><img src="contact_recreation.png" alt="recreation contact sheet"><figcaption>Recreation (encoded MP4)</figcaption></figure>
 <p><a href="https://x.com/0xwhrrari/status/2112166940081004693" style="color:#f2a272">Original post and video</a>. Reference footage is not bundled.</p>
</div>
<h2>The comp canvas Clawd builds</h2>
<img src="../build/comp_contact.png" alt="comp contact sheet">
<h2>Interface texture</h2>
<img src="../build/ui_preview.png" alt="UI texture">
<h2>Soundtrack loudness per half second vs prompt-pack targets</h2>
<img src="../audio/loudness.png" alt="loudness">
<p>Sources: <code>timeline.py</code>, <code>ui/</code>, <code>render_ui.js</code>, <code>scene.py</code>, <code>clawd.blend</code>, <code>audio/make_audio.py</code>. See BRIEF.md.</p>
</main></html>
"""

os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "index.html"), "w") as fh:
    fh.write(PAGE.format())
print("wrote out/index.html")

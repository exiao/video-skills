"""Render selected frames as stills (preview/QC).

    blender -b clawd.blend -P gpu.py -P render_stills.py -- --frames 1,46,61 --pct 50 --samples 40 --out build/stills
"""
import os
import sys
import time

import bpy

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
opts = dict(frames="1", pct="50", samples="40", out="build/stills", noblur="0")
for i in range(0, len(argv), 2):
    opts[argv[i].lstrip("-")] = argv[i + 1]
root = os.path.dirname(bpy.data.filepath)
out = os.path.abspath(opts["out"])  # relative to the shell cwd
os.makedirs(out, exist_ok=True)
sc = bpy.context.scene
sc.render.resolution_percentage = int(opts["pct"])
sc.cycles.samples = int(opts["samples"])
if opts["noblur"] == "1":
    sc.render.use_motion_blur = False
frames = []
for part in opts["frames"].split(","):
    if "-" in part:
        a, b = part.split("-")
        frames += list(range(int(a), int(b) + 1))
    else:
        frames.append(int(part))
log = []
for f in frames:
    sc.frame_set(f)
    sc.render.filepath = os.path.join(out, "f%04d.png" % f)
    t0 = time.time()
    bpy.ops.render.render(write_still=True)
    log.append((f, time.time() - t0))
    print("STILL f%04d %.2fs" % (f, log[-1][1]), flush=True)
with open(os.path.join(out, "timing.txt"), "a") as fh:
    for f, s in log:
        fh.write("frame %d  %.2f s  pct %s  samples %s\n" % (f, s, opts["pct"], opts["samples"]))

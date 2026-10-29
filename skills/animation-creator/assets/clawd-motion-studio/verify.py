"""Verify the encoded MP4 and write build/verification.md plus out/contact_recreation.png.

    .venv/bin/python verify.py
"""
import json
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import timeline as T  # noqa: E402

MP4 = os.path.join(ROOT, "out", "clawd_no_after_effects.mp4")
REPORT = os.path.join(ROOT, "build", "verification.md")


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, check=True).stdout


lines = ["# Verification", "", "File: `out/clawd_no_after_effects.mp4`", ""]
probe = json.loads(run(["ffprobe", "-v", "error", "-count_frames", "-show_streams", "-show_format",
                        "-of", "json", MP4]))
v = next(s for s in probe["streams"] if s["codec_type"] == "video")
a = next(s for s in probe["streams"] if s["codec_type"] == "audio")
checks = [
    ("video codec", v["codec_name"] + " " + v.get("profile", ""), v["codec_name"] == "h264"),
    ("resolution", "%sx%s" % (v["width"], v["height"]), (v["width"], v["height"]) == (1920, 1080)),
    ("frame rate", v["r_frame_rate"], v["r_frame_rate"] == "30/1"),
    ("decoded frames", v["nb_read_frames"], int(v["nb_read_frames"]) == 360),
    ("pixel format", v["pix_fmt"], v["pix_fmt"] == "yuv420p"),
    ("audio", "%s %s Hz %s ch %s kb/s" % (a["codec_name"], a["sample_rate"], a["channels"],
                                         int(a.get("bit_rate", 0)) // 1000), a["codec_name"] == "aac"),
    ("container duration", probe["format"]["duration"], abs(float(probe["format"]["duration"]) - 12.0) < 0.06),
]
# full decode with error reporting
dec = subprocess.run(["ffmpeg", "-v", "error", "-i", MP4, "-f", "null", "-"], capture_output=True, text=True)
checks.append(("full decode errors", "none" if not dec.stderr.strip() else dec.stderr.strip()[:200],
               dec.returncode == 0 and not dec.stderr.strip()))
lines += ["| check | value | ok |", "|---|---|---|"]
lines += ["| %s | %s | %s |" % (k, val, "yes" if ok else "**NO**") for k, val, ok in checks]

# frame mapping: encoded frame n (0-based) == build/frames/(n+1).png == wall time n/30
lines += ["", "## Frame mapping", "",
          "Blender frame f = round(t x 30) + 1. Encoded frame index n (0-based) = Blender frame n + 1.",
          "First: encoded 0 = frame 0001 = t 0.000 s. Last: encoded 359 = frame 0360 = t 11.967 s.", ""]
lines += ["| encoded n | source PNG | PSNR dB (encode vs source) |", "|---|---|---|"]
psnrs = []
for n in (0, 60, 90, 150, 180, 240, 300, 359):
    enc =np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", MP4, "-vf", "select=eq(n\\,%d)" % n,
                                        "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                                       capture_output=True, check=True).stdout, dtype=np.uint8)
    enc = enc.reshape(1080, 1920, 3).astype(np.float64)
    src = np.asarray(Image.open(os.path.join(ROOT, "build", "frames", "%04d.png" % (n + 1))).convert("RGB"),
                     dtype=np.float64)
    mse = np.mean((enc - src) ** 2)
    p = 10 * math.log10(255 ** 2 / mse) if mse > 0 else 99
    psnrs.append(p)
    lines.append("| %d | %04d.png | %.1f |" % (n, n + 1, p))
lines.append("")
lines.append("PSNR includes the soft vignette added during encoding. It is a similarity diagnostic; frame order also depends on the encoder input sequence and visual inspection.")

# isolated one-frame jump scan on the encoded video (mean abs diff between consecutive frames)
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", MP4, "-vf", "scale=192:108", "-f", "rawvideo",
                      "-pix_fmt", "gray", "-"], capture_output=True, check=True).stdout
fr = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 108, 192).astype(np.float32)
d = np.abs(np.diff(fr, axis=0)).mean(axis=(1, 2))
spikes = [i + 1 for i in range(1, len(d) - 1) if d[i] > 3 * max(d[i - 1], d[i + 1], 1.0) and d[i] > 6]
lines += ["", "## One-frame jump scan", "",
          "Consecutive-frame mean abs difference (gray, 192x108). Isolated spikes (> 3x both neighbours and > 6): %s" %
          (", ".join("n=%d (t %.2f s)" % (s, s / 30) for s in spikes) or "none")]

# audio: loudness per half second of the muxed track
pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", MP4, "-vn", "-ac", "2", "-ar", "48000", "-f", "f32le", "-"],
                     capture_output=True, check=True).stdout
au = np.frombuffer(pcm, dtype=np.float32).reshape(-1, 2)
win = 24000
rms = [20 * math.log10(max(np.sqrt(np.mean(au[i * win:(i + 1) * win] ** 2)), 1e-9)) for i in range(24)]
peak = 20 * math.log10(np.max(np.abs(au)))
lines += ["", "## Muxed soundtrack", "",
          "Samples decoded: %d (%.3f s). Sample peak %.2f dBFS." % (len(au), len(au) / 48000, peak),
          "", "RMS dBFS per half second: " + ", ".join("%.1f" % r for r in rms),
          "", "Prompt-pack targets: -28 first 0.5 s, ~-21 knocks, ~-14 peel, -11..-12 pop to end, ~-19 fade."]
# hit alignment: the loudest transient near key events in the muxed track
lines += ["", "| event | t | detected peak t | delta ms |", "|---|---|---|---|"]
env = np.abs(au).max(axis=1)
for t_ev, kind in [(T.T_KNOCKS[0], "knock 1"), (T.T_POP, "pop"), (T.T_KICK, "kick thwack"),
                   (T.T_KEYS[0], "keyframe ding C"), (T.T_PLAY, "Play brass")]:
    i0, i1 = int((t_ev - 0.03) * 48000), int((t_ev + 0.06) * 48000)
    seg = env[i0:i1]
    onset = i0 + int(np.argmax(np.diff(np.convolve(seg, np.ones(48) / 48, mode="same"))))
    lines.append("| %s | %.3f | %.3f | %+.1f |" % (kind, t_ev, onset / 48000, (onset / 48000 - t_ev) * 1000))

# recreation contact sheet at the reference timestamps
tiles = []
for k in range(24):
    t = k * 0.5
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", "%.3f" % (t + 0.001), "-i", MP4, "-frames:v", "1",
                          "-vf", "scale=480:270", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    tiles.append(Image.frombytes("RGB", (480, 270), raw[:480 * 270 * 3]))
sheet = Image.new("RGB", (480 * 4, 270 * 6))
dr = ImageDraw.Draw(sheet)
for k, im in enumerate(tiles):
    x, y = (k % 4) * 480, (k // 4) * 270
    sheet.paste(im, (x, y))
    dr.text((x + 6, y + 4), "%.1f s" % (k * 0.5), fill=(255, 220, 0))
os.makedirs(os.path.join(ROOT, "out"), exist_ok=True)
sheet.save(os.path.join(ROOT, "out", "contact_recreation.png"))
lines += ["", "Contact sheet of the encoded MP4 at 0.0, 0.5 ... 11.5 s: `out/contact_recreation.png` "
          "(same layout as `reference/contact-sheet.png`)."]

ok = all(c[2] for c in checks)
lines += ["", "**Overall technical checks: %s**" % ("PASS" if ok else "FAIL")]
with open(REPORT, "w") as fh:
    fh.write("\n".join(lines) + "\n")
print("\n".join(lines))
if not ok:
    raise SystemExit(1)

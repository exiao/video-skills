# General animation production workflow

## Claude brief template

Fill only the fields relevant to the request. Do not invent restrictions or commit every project to Canvas.

```text
Create the finished animation in [output directory]. Preserve [existing files/stack].

Purpose and subject: [what the viewer should see/understand/feel].
Visual direction: [style, composition, palette, materials, typography or lighting].
References: [paths/URLs, and which visual or motion properties each reference informs].
Motion: [key actions, pacing, camera, transitions, ending or loop behavior].
Storyboard: [selected storyboard and scene stills, or present three options for a new narrative/product/multi-scene piece and wait for selection before producing one still per scene and building full motion].
Delivery: [HTML/video/native project], [dimensions/aspect], [duration], [fps if needed].
Sound: [silent, supplied audio, or requested music/voice/effects].
Assets and constraints: [available assets, code-only/offline if explicitly required].
For a one-prompt workflow test: [whether Claude should write the visuals and audio as code, permitted local renderer/encoder, and whether outside generation/assets are allowed].

Choose the simplest rendering approach that supports this brief. Reuse relevant
existing code/tools. Implement the piece, render representative frames and a short
motion sample, inspect them, and revise concrete weaknesses. Finish the requested
outputs and test the actual playback/export. Report artifact paths, verification,
the actual production stack, first-pass result, revisions, and any material
limitations. Do not publish.
```

Use the current claude-cli skill for the command and authentication. Include its delegation guidance. Resume the same session for focused revisions, with concrete keep/change notes rather than “make it better.”
Before a full export, confirm the output directory is writable and the chosen local renderer, `ffmpeg`, and `ffprobe` are available. For rendered-video delivery, use the early motion sample to test the complete capture, encode, and playback path before expanding production: a representative 3–5 seconds, or the full piece if shorter, including audio when requested. Inspect the encoded sample and resolve missing assets, rendering differences, or audio sync failures before the full export. Animation builds use the direct Claude CLI workflow; the read-only `ask_claude.py` consultation helper cannot write or render artifacts.

## Export contract for browser work

Prefer a completed seek operation (`await renderFrame(f, seed)`) over sleeping for assumed animation time. A synchronous implementation is also valid because `await` handles both. Assets and fonts must be ready before the first capture.

- **Canvas 2D:** capture the backing bitmap with `toDataURL`/`toBlob`, or fix CSS size and device scale for a canvas screenshot. Balance clipping/transforms and save/restore; `clearRect` alone does not reset state.
- **SVG/DOM/CSS:** capture the art container at a fixed viewport. Seek Web Animations/GSAP or set time-derived properties; disable competing autonomous timers. Do not capture only a canvas if the piece includes DOM text or overlays.
- **WebGL/3D:** seek scene/camera state and complete a render before capture. Capture immediately after rendering or use the engine's render-target/readback mechanism; do not assume the default drawing buffer persists. Wait for textures and shader compilation.
- **Physics/stateful simulations:** reset to a fixed seeded state and advance fixed timesteps, or restore a checkpoint and replay. Test that seeking through this mechanism is reproducible. Out-of-order direct draws are not a valid requirement unless that seek mechanism exists.
- **Audio:** render/mix to the same timeline, then mux. Browser audio may require a gesture for interactive playback. Verify sync and duration in the encoded video.

Render into a new run directory. Await frame completion, then capture frame 0 through N−1, named in numerical order. Reuse an installed Node/Playwright/Chromium runtime when suitable; verify it launches and avoid embedding temporary installation paths in reusable code. Use a native exporter when the requested tool/format makes that the better route.

## Encoding example

For a silent 5-second, 24-fps opaque sequence of 120 PNGs, with FFmpeg/libx264 available:

```bash
ffmpeg -framerate 24 -start_number 0 -i 'frames/frame-%05d.png' \
  -frames:v 120 -an -c:v libx264 -preset slow -crf 16 \
  -pix_fmt yuv420p -movflags +faststart animation.mp4

ffprobe -v error -count_frames \
  -show_entries stream=codec_type,codec_name,width,height,r_frame_rate,nb_read_frames,duration \
  -show_entries format=duration -of json animation.mp4

ffmpeg -v error -i animation.mp4 -f null -
```

These numbers are examples. Set them from the current brief and ensure duration×fps is an integer, or choose/document the nearest representable duration. Remove `-an` and map/mux the intended audio when needed. Use even dimensions for yuv420p. Use a format/codec with alpha when transparency matters. Fine colored lines, halftones, gradients, and grain can change during encoding; inspect the actual video.

## Verification evidence

Keep evidence proportionate: a contact sheet, the exported artifact, media metadata/decode results, and a short note on actual playback/control checks usually suffice. Use same-renderer frame hashes for determinism; do not expect lossy MP4 pixels to match PNGs. Do not infer smooth motion from a contact sheet, or artistic quality from a green technical check.

For loops, compare motion/audio across the seam. For explainers and kinetic text, check reading time and conceptual clarity. For data animations, confirm the animation does not distort the values. For interactive work, test user input, pause/restart, responsive bounds, and reduced motion.

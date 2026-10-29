# 3D character animation on video editor panels

Use this when a 3D character performs on and interacts with video editor panels: the toolbar, composition canvas, effects list, timeline and playback controls form its physical stage. The worked reference is the accepted 12-second “No After Effects. Just Clawd.” recreation, featuring Clawd. This is one worked example, not the default look or stack for Animation Creator. For the same video, regenerate the bundled source; new implementation is unnecessary. For an adaptation, give Claude CLI the starter, `BRIEF.md`, requested changes and bounded ownership. Carry the accepted story forward rather than reopening storyboard selection.

Example future request: “Use $animation-creator to make a 3D character animation on video editor panels, like the saved Clawd reference.” For the same recreation, ask to rebuild the saved reference from its starter.

## Reusable animation mechanism

Build the editor panels as surfaces in the same 3D scene as the character, with crisp UI textures and physical controls where contact matters. The character’s feet, hands and props meet those surfaces; pressing a tool, kicking an effect chip or landing on a keyframe visibly changes the composition. Camera moves reveal the relationship between the character, the controls and the result.

For a different character or editor, preserve those relationships and replace the character geometry, panel layout, labels and resulting composition as the brief requires. Share contact coordinates and event times between the UI, character, camera and sound. The included Clawd source is a concrete starting point for this technique; its identity, title and beat sequence belong to the reference example.

## References and preserved source

- [Original post and video — 0xwhrrari](https://x.com/0xwhrrari/status/2112166940081004693) (the user's reference; video attachment `2112159859609161728`).
- [Six-page prompt pack](https://drive.google.com/file/d/1-VZJxR-VpR1rY4FyymcMDIq742fkQYLT/view): visual brief, three follow-ups, beat table and sound prompt.
- [Motion Engineering: Build a Video Studio Around Opus 5.5](https://x.com/0xwhrrari/status/2105643919119696297): the creator's workflow article. The guide describes a production stack, not a single studio installer.
- [Reusable source starter](../assets/clawd-motion-studio/): accepted scene, UI, timeline, original synthesized soundtrack code, pinned dependency manifests, render/encode commands and verifiers. Generated textures, renders, environments and original footage are excluded; they are not needed to regenerate the remake.

The accepted build was authored through Claude Code Opus 5.5, with an independent audio worker. Blender, Chrome, Python and FFmpeg produced the media locally. It is a procedural restaging with differences in camera, material and typography, not a pixel copy or model-native video generation. No source frames or audio are reused.

## Copy and install

Copy the **contents** of `assets/clawd-motion-studio/` into a fresh project directory; keep the installed starter clean. Resolve the asset path relative to this skill's actual location. Example on Eric's Mac:

```sh
mkdir -p "$HOME/Documents/clawd-remake"
cp -R "$HOME/.codex/skills/animation-creator/assets/clawd-motion-studio/." "$HOME/Documents/clawd-remake/"
cd "$HOME/Documents/clawd-remake"
```

Choose an unused destination if that directory already contains work. Inspect installed tools before installing. This example was verified on Apple Silicon macOS with Blender **5.2.2 LTS**, Node **22.23.1**, Python **3.13.7**, installed Google Chrome, FFmpeg/ffprobe and uv. Versions describe the known working build, not whatever Homebrew serves in the future. For a later Blender release, prove a scene build and sample render before a full pass; use the official 5.2.2 release if compatibility fails.

```sh
# Install only missing tools. Chrome is required separately if absent.
brew install --cask blender
brew install node ffmpeg uv

# Confirm the installed Blender version before generating the scene.
blender --version

# In the copied project:
PUPPETEER_SKIP_DOWNLOAD=1 npm ci
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python -r requirements.txt
mkdir -p build
```

`package-lock.json` locks Puppeteer 25.14.0; `requirements.txt` pins NumPy, SciPy, Pedalboard and Pillow. Puppeteer uses the installed Chrome rather than downloading another browser. Its default executable is `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`; set `CHROME_PATH` if different. Python dependencies stay in `.venv`; Blender uses its own Python and imports the standard-library-only timeline.

`gpu.py` selects **Metal on every render process**. Device preferences do not travel with the `.blend`. The guide's OptiX example is for NVIDIA; port GPU selection explicitly for another platform, or select CPU and benchmark it. This starter's default GPU setup is Mac-specific.

## Regenerate and render

Run from the copied project directory. The still and short-sample steps are the compatibility check for the installed Blender version: stop and resolve any failed build, missing texture or bad render before starting the full pass.

```sh
.venv/bin/python timeline.py --json build/timeline.json
node render_ui.js
.venv/bin/python audio/make_audio.py
.venv/bin/python audio/verify_audio.py  # diagnostic report; inspect it, not an exit-code gate
blender -b --factory-startup -P scene.py

# Include the previously missed jump peaks, plus opening/ending states.
blender -b clawd.blend -P gpu.py -P render_stills.py -- --frames 1,68,125,294,360 --pct 50 --samples 40 --out build/stills
# Short motion sample: frames 121–200 cover Glow and the keyframe hops.
blender -b clawd.blend -P gpu.py -P render_stills.py -- --frames 121-200 --pct 50 --samples 40 --out build/sample
ffmpeg -y -framerate 30 -start_number 121 -i build/sample/f%04d.png -ss 4 -i audio/soundtrack.wav -frames:v 80 -t 2.666667 -c:v libx264 -pix_fmt yuv420p -c:a aac -movflags +faststart build/sample.mp4

# After inspecting stills and the sample:
./render_all.sh
./encode.sh
.venv/bin/python verify.py
.venv/bin/python make_preview.py
```

Outputs: `clawd.blend`, `textures/`, `audio/soundtrack.wav`, `out/clawd_no_after_effects.mp4`, `out/poster.png`, `out/index.html`, and verification reports. Keep the `.blend` beside `textures/`; its image references are relative. A copied `.blend` alone is not a complete editable delivery. All generators work locally after dependency installation.

Frame convention: Blender **f = 1…360**, wall time **(f−1)/30**, encoded index **n = f−1**. The final video is 12 seconds at 1920×1080/30 fps. `./render_all.sh 105 145` replaces only that inclusive frame range; run `./encode.sh` afterward to update the MP4.

The accepted full pass took **3,118 seconds, about 52 minutes**, on an M1 Max 32-core GPU at 1080p, 96 samples, adaptive threshold .03, OIDN and shutter .5. Half-resolution previews at 40 samples were about 1.3–1.8 seconds/frame. Measure the current machine; do not quote the creator's RTX benchmark as this Mac's ETA.

## What makes the scene work

| Source | Responsibility |
| --- | --- |
| `timeline.py` | UI pixel rectangles, their mapping into Blender metres, action times, seekable actor/UI/comp state and audio events |
| `ui/`, `render_ui.js` | CSS 1280×720 at device scale 3 → 3840×2160 UI texture; 360 comp frames and timecode textures |
| `scene.py` | Separate horizontal panel slabs, mascot, keycaps, chip, camera, lights and baked frame keys |
| `audio/make_audio.py` | Seeded 48 kHz stereo synthesized music/effects from shared event times |
| `gpu.py`, `render_all.sh`, `encode.sh` | GPU selection, numbered PNGs and H.264/AAC encode |

Keep one owner for layout and time. Tool presses must meet the same pixel rectangles the UI renderer paints; the visible press causes the matching comp change. Bake native scene keys for direct seeking without a runtime timeline handler. UI texture capture and Blender rendering are distinct stages.

| Time | Recognizable beat |
| --- | --- |
| 0–1.5 s | Selected flat `clawd.png`; knocks at .5 and 1.0 s |
| 1.5–2.0 s | Card peels; pops into the 3D mascot at 2.0 s, with shards |
| 2.5 / 3.0 / 3.5 s | Type / Rectangle / Pen presses create title, spark and swoosh |
| 4.5–5.5 s | Glow chip appears, kick at 5.0 s, activation at 5.5 s |
| 6.0 / 6.5 / 7.0 / 7.5 s | Four Position keyframes and matching comp poses |
| 8.0–9.6 s | Playhead hop, rewind, then surf/playback |
| 10.0–12.0 s | Preview Play; panels fall away; final comp and waving mascot |

Final copy: **MADE WITH CLAUDE**, orange spark/swoosh, **OPUS 5.5** subtitle. The accepted remake uses Arial Black; typography and camera differ from the reference. For adaptations, edit copy and geometry together. Changing duration/FPS/tempo requires coordinating the scene, duration-specific audio arrangement, encoder and verifier; this is not a generic arbitrary-duration template.

## Lessons from the actual traces

### Inspect flight peaks between preview stills

Sparse previews missed cropped heads in three flights. Project the **evaluated vertices after modifiers of the render-visible mascot meshes** through the camera for every flight frame, then inspect dense rendered samples around failures. Exclude the flat peel card, shards, chip and control geometry: a broad collection bounding box produced false alarms. Geometric bounds do not cover the full blur, depth-of-field or glow footprint; leave a visible margin and inspect actual renders.

The preserved `CAM_LIFTS` in `scene.py` raise the target and pull the camera back with smootherstep windows that become exactly zero outside the correction:

| Action | Window (seconds) | Changed camera keys | Rerender range |
| --- | --- | --- | --- |
| Opening pop | 2.0 / 2.15 / 2.36 / 2.46 | f62–74 | f61–75 |
| Glow flip | 3.85 / 4.05 / 4.30 / 4.42 | f117–133 | f116–134 |
| Play leap | 9.60 / 9.70 / 9.86 / 9.95 | f290–299 | f289–300 |

These values are specific to this scene. Baked linear camera interpolation and shutter .5 also affect neighboring rendered frames; changing only images whose own key changed leaves boundary artifacts. The final geometry check across f61–360 retained at least 6.1% frame margin. Preserve successful contacts, landings and camera states outside a repair; compare them against the accepted scene.

### Give a long render one accepted source version

The main maker and a repair worker both edited the opening camera. A note file alone did not reliably interrupt a maker waiting on a long render. Assign one writer per source region; communicate ownership and release explicitly. For a render already in progress, keep its input scene version clear, wait until it has passed a replacement range, then install the accepted replacement frames. Rebuild the final `.blend` from the accepted source before final encoding so editable source and movie agree. A small render with one author needs no elaborate snapshot process.

### Verify the real pipeline

- Keep `set -euo pipefail` in the render wrapper: `tee`/`grep` previously could hide a Blender failure. `verify.py` exits nonzero for failed metadata/decode checks. `audio/verify_audio.py` produces a diagnostic report, not a pass/fail exit code: review its onset misses, levels and clipping before accepting sound.
- GPU output can vary by one 8-bit level in a handful of channels. The repeat-seek probe f360 → f360 → f1 → f360 found that tiny noise, not state drift. Compare decoded image differences with a declared tolerance; do not demand PNG byte identity as proof of visual repeatability.
- The encoder adds a vignette, so raw-versus-encoded full-frame PSNR alone cannot prove frame order. Check the numbered sequence, decoded count and corresponding encoded frames; compare a crop less affected by the vignette when needed.
- Audio timing and levels were measured in the accepted run: the knock, pop, kick, first keyframe and Play muxed transients were within 1 ms, WAV peak −1 dBFS, AAC decoded peak −.06 dBFS with no clipping. The WAV envelope report also flags four peel/power-down/boom detections 12–23 ms from their event times; this is not an all-events timing pass. **Listening was unavailable in that environment.** Measure the encoded track as well as the WAV and audition when possible; signal checks do not establish how it sounds.
- Reopen the generated `.blend`, resolve its texture paths, inspect encoded jump peaks, check full decode and watch playback. Technical PASS is separate from reference fidelity and subjective sound review.

## Trace provenance and evidence

This recipe was extracted from the accepted local build on October 19–20, 2026. Regeneration depends on the bundled starter and installed tools.

- `claude-build.jsonl`: original Claude session `b48b9afb-9f83-437c-b023-e6ad52fa184d`; lines 830 (Glow CSS fix), 954 (measured render estimate), 1145 (52-minute pass), 1208 (delivery and listening limit).
- `claude-opening-fix.jsonl`: session `74ed59c4-cca9-4c95-b418-0bd0d6e7c563`; lines 133, 197, 279 record bounded camera repair and the overlapping staged edit.
- `claude-camera-followup.jsonl`: resumed repair session; lines 157, 188, 255 record the all-flight audit, actual old-camera crop and final replacement ranges.
- `work/opening-fix/followup-report.md`, `flight-bounds.md`, `build/code-review.md`, `build/verification.md`: unchanged-state comparisons, geometry limits, decode/audio measurements and source review.

On a future rebuild, record the current tool versions and inspect the new output; the historical acceptance and benchmark do not prove a new machine's render.

## Starter packaging check

On October 20, 2026, a fresh copy installed dependencies, regenerated all 1,084 texture PNGs and the soundtrack, rebuilt/reopened the scene with all seven relative image paths resolving, and rendered f1, f68, f125, f294 and f360 at 25%/16 samples. A separate f61–90 sample encoded as 30 frames at 480×270 with audio. The regenerated WAV matched the accepted SHA256 `42044208ae45c49a6ace2c8bea3164beb9a90e1bac6695151b9d2c977805ae0d`. A missing Chrome executable returned failure rather than success. Skill validation and a separate reproducibility review passed. This check did not repeat the complete 360-frame production export or a listening audition.

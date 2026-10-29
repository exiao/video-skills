# Optional example: procedural risograph jellyfish

This reference applies only when the requested piece uses the printed/riso style or explicitly reuses the jellyfish example. Its palette, Canvas implementation, code-only restrictions, duration, silence, and loop are example-specific. Use workflow.md for the general process.

## What is preserved

`../assets/jellyfish.html` is the actual Claude-created renderer from the accepted five-second experiment, including the final pause/replay fix. It is source code, not an embedded image or video. Copy it into the new project before editing.

The original was verified on 2026-09-15: 1080×1080, 24 fps, 120 frames, 5.000 seconds, silent H.264/yuv420p; repeated and out-of-order frames matched, another seed differed, and no network requests occurred. This is provenance, not a guarantee for modified versions or future environments.

The visual inspiration was Kevin Ngo's post: https://x.com/kevin_t_ngo/status/2099477219877978289 . His unavailable source was not recreated exactly. This bundled example is our own implementation of the procedural three-ink approach.

## Adapting the source

Search the source for `mulberry32`, `buildTextures`, `buildScene`, `drawScene`, `compositeInks`, `renderFrame`, and `boot`.

- Preserve the seeded randomness and cached paper/screen data when replacing the jellyfish drawing.
- The scene draws grayscale ink coverage, then the compositor applies halftone thresholds, ink irregularity, and multiplicative ink color. Drawing arbitrary RGB directly to the final canvas bypasses that appearance.
- Coverage polarity matters: white adds ink and black knocks it out. Preserve the blue/pink/yellow layer ordering when adapting masks and screen arrays.
- Dimensions appear in the canvas element, `W/H/N`, `PLATE` bounds, static CSS, and scene composition. Texture caches are keyed by seed, so clear or rebuild them when changing dimensions. For another aspect ratio, update these together and recompose subjects; do not simply stretch a square print.
- Timing includes `FPS`, `TOTAL_FRAMES`, `LOOP_SECONDS`, `PULSE_PERIOD`, and visible frame-count text. Audit these together for another duration. Changing frame count alone can break the seam. Keep pulse periods as exact divisors of the loop duration and fade wrapped particles to zero opacity at their wrap point.
- Keep controls outside the canvas. Match the accessible canvas description to the new subject.

## Claude task brief

Use the current claude-cli skill's invocation and authentication workflow. Pass a brief like this, substituting subject, duration, dimensions, and output directory:

```text
Create a finished five-second procedural risograph animation in this output directory.
Use the copied jellyfish.html as a working renderer reference; deliver animation.html,
animation.mp4, contact.png, and a small reproducible exporter. Preserve unrelated files.

Subject: a large translucent pink jellyfish with a ribbed bell and flowing curled
pink/yellow tendrils, deep cobalt water, a few distant jellyfish, restrained particles,
thin orbital rings, and an ivory paper margin. No title card. Silent.

Create everything with Canvas code: three ink coverage layers, distinct angled
halftone screens, subtle registration slip, irregular ink and stable paper grain.
Prioritize silhouette, depth and delicate linework. Keep highlights open. Avoid
random flashing and excessively noisy margins.

Deliver 1080x1080, 24 fps, exactly 120 frames. Keep renderFrame(frame,seed), FPS,
TOTAL_FRAMES, and paused ?f=N&s=N mode. Frames must render independently of history.
Keep geometry and textures seeded and stable. Use periodic motion for a smooth loop.

Inspect representative stills before full export. Export every frame deterministically,
then encode with ffmpeg. Inspect a contact sheet and video playback. Verify same-seed
fresh-context/order independence, changed-seed variation, zero external requests,
nonblank frames, exact dimensions/duration/frame count, no audio, and full decode.
Fix observed issues and report evidence with artifact paths. Do not publish.
```

Append the delegation guidance required by the current claude-cli skill. Continue with `--resume SESSION_ID` for bounded artistic feedback instead of regenerating the entire scene. Good revision: “Keep the silhouette and tendrils. Open the bell apex, emphasize ribs, soften paper speckles, then re-export and inspect.”

## Minimal export procedure

Use Node with Playwright resolved from the project's dependencies or an explicitly discovered installation. Keep any environment-specific path in the run configuration, not the skill. Await sync or async rendering uniformly:

```js
await page.goto(htmlFileUrl + '?f=0&s=7');
// Route/block external requests before navigation and collect errors.
await page.waitForFunction(() => typeof window.renderFrame === 'function');
const { fps, frames } = await page.evaluate(() => ({
  fps: window.FPS, frames: window.TOTAL_FRAMES
}));
for (let frame = 0; frame < frames; frame++) {
  await page.evaluate(async ({frame, seed}) => {
    await window.renderFrame(frame, seed);
  }, {frame, seed: 7});
  const png = await page.locator('canvas').evaluate(c => c.toDataURL('image/png'));
  // Decode the PNG data URL and write frame-00000.png, frame-00001.png, etc.
}
```

This is a recipe excerpt, not a standalone script. Implement file handling and checks for the selected project. Capture the canvas backing bitmap to avoid viewport/CSS screenshot-size errors. Validate metadata and expected frame count before encoding. Use a new run directory or temporary output and rename after successful verification.

For the original 24 fps silent output, after producing all PNGs:

```bash
ffmpeg -framerate 24 -start_number 0 -i 'frames/frame-%05d.png' \
  -frames:v 120 -an -c:v libx264 -preset slow -crf 16 \
  -pix_fmt yuv420p -movflags +faststart animation.mp4

ffprobe -v error -count_frames \
  -show_entries stream=codec_type,codec_name,width,height,r_frame_rate,nb_read_frames,duration \
  -show_entries format=duration -of json animation.mp4

ffmpeg -v error -i animation.mp4 -f null -
```

Use FPS/frame-count values matching the current brief, not always 24/120. H.264 yuv420p needs even dimensions. Fine colored halftones may soften under chroma subsampling; inspect the encoded video, not just source PNGs.

## Failures caught in the original run

- **History-dependent drawings:** a clip accumulated and stroke state persisted between frames. Balanced per-frame save/restore fixed it; deterministic tests then passed. Keep one frame-order check after renderer edits.
- **Wrong screenshot size:** CSS scaled a 1080 canvas to 984. Static mode received fixed sizing; canvas bitmap capture also avoids the mismatch.
- **Flat/noisy first draft:** dense fill hid bell ribs, and interior anatomy read as a large X. More open coverage, finer ribs and smaller interior details improved readability.
- **Duplicate live loops:** replay could schedule another animation callback without cancelling the old one. The bundled source includes cancellation.

References for unfamiliar APIs: Canvas compositing (https://developer.mozilla.org/en-US/docs/Web/API/CanvasRenderingContext2D/globalCompositeOperation), Canvas caching (https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API/Tutorial/Optimizing_canvas), Playwright screenshots (https://playwright.dev/docs/screenshots), FFmpeg image sequences (https://ffmpeg.org/ffmpeg-formats.html#image2).

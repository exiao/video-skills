# p5.js creative sketches within Animation Creator

Build the actual interactive artwork and deliver its runnable source. Adapted from the local `creative/p5js` skill by SHL0MS and Hermes Agent (MIT).

## Choose the piece

Resolve the subject, visual identity, motion, interaction, and output from the brief. For an open request, choose a concrete creative concept and explain it briefly before coding. Respect established palette and type; do not impose dense effects, a dark background, or a fixed style on every piece.

Use p5.js for code-native drawing. If the piece needs generated bitmap assets, use the image-generation-guide skill and built-in image generation; save those assets into the project.

## Build

- Prefer a small HTML sketch with inline CSS/JavaScript and a pinned p5.js dependency. Keep an existing application's stack when integrating there. Verify the chosen version against official p5.js documentation when API or addon compatibility matters; older references here contain version-specific examples, not a latest-version recommendation.
- For a portable download, bundle the library beside the HTML and package both. A downloaded HTML file with a missing vendor script is not standalone. Load p5.js before setting `p5.disableFriendlyErrors`.
- Seed both `randomSeed()` and `noiseSeed()` for repeatable artwork. Keep parameters separate from drawing state. Use controls that affect the underlying behavior, such as branching, turbulence, or growth rate.
- For a parameter-and-seed viewer, adapt [the p5 viewer template](../../assets/p5js/viewer.html). It is a starting point, not mandatory chrome. Keep simple passive sketches smaller.
- Use offscreen `createGraphics()` buffers when layers or persistent trails benefit; do not add buffers solely to meet a template. Bound particle/branch histories so repeated interaction does not grow memory forever.
- Preserve artwork and pause state across resize when possible. Reset and parameter changes should respect an explicit pause. Start reduced-motion users at a useful still, with an opt-in play control. Keyboard shortcuts must not steal input from focused buttons or form controls.
- For `curveVertex()`, duplicate boundary vertices when the curve needs to reach its first and last data points; inspect branch joints and endpoint dots for gaps.

## Focused references

Read only what the piece needs. These are imported technique references; current APIs and the user's brief take precedence over old version claims or universal creative rules.

- [Visual effects](visual-effects.md): noise, particles, flow fields, textures.
- [Color systems](color-systems.md) and [shapes](shapes-and-geometry.md): palette and geometry.
- [Interaction](interaction.md): pointer, keyboard, audio input, parameters.
- [Animation](animation.md): time, easing, loops, motion.
- [WebGL and 3D](webgl-and-3d.md): shaders and spatial rendering.
- [Typography](typography.md): text-driven sketches.
- [Core API](core-api.md) and [troubleshooting](troubleshooting.md): targeted implementation help.
- [Export pipeline](export-pipeline.md): capture concepts. Use available browser tooling and project-local scripts; legacy helper paths in this reference are not installed commands.

## Preview and deliver

Open the real sketch, inspect desktop and relevant mobile sizes, and exercise its controls. Verify that animation advances, pause holds, reset behaves as labeled, resizing preserves coherent state, and downloads open. Check browser errors and actual performance; do not promise a frame rate from code alone.

For a PNG, use `saveCanvas()` and inspect the saved file. For a video, drive time deterministically (for example `render(frame / fps)`, or `noLoop()` plus awaited `redraw()` with explicit time) and capture the canvas, then encode with ffmpeg. Screenshot delays are not a reliable simulation clock. Inspect early/middle/late frames and measure final dimensions and duration. Use even dimensions for H.264 yuv420p.

Save outputs in the current project, provide the interactive page plus requested exports, and distinguish what was actually tested from unverified behavior. A local sketch does not authorize publishing it.

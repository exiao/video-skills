# 3D character on video editor panels — Clawd reference brief

Reference: https://x.com/0xwhrrari/status/2112166940081004693
Prompt pack: https://drive.google.com/file/d/1-VZJxR-VpR1rY4FyymcMDIq742fkQYLT/view
Workflow article: https://x.com/0xwhrrari/status/2105643919119696297

This source starter preserves the locally accepted 3D animation of Clawd performing on video editor panels. Use it directly for the same video. For a new subject, pass this brief, the reference, and the requested changes to Claude CLI with bounded file ownership. Read Animation Creator's `references/clawd-motion-studio.md` for setup, regeneration and review lessons. Source video/audio are reference material; this project generates its own imagery and soundtrack.

12 seconds, 30 fps, final 1920x1080, 360 frames. Warm dark brown studio, black/dark-gray editor slabs, blue selection accents, colored timeline tracks. Terracotta rounded rectangular toy mascot, side nubs, four short legs, narrow black eyes. Workspace actually resembles After Effects with real labels and icons, no Adobe logos. Smooth 3D, soft bevels and studio highlights, shallow focus, deliberate camera follows/whips.

Read and implement the PDF's exact beats: flat selected PNG and knocks; peel and pop with shards; Type/Rectangle/Pen presses; Glow chip kick; four Position keyframes; rewind and surf playhead; Preview Play; surrounding panels fall, composition remains and Clawd waves. Every contact must register with the UI target and cause its corresponding change. Final title MADE WITH CLAUDE, orange spark and swoosh, OPUS 5.5 subtitle.

Reference inspection: panels lie in a horizontal-ish plane tilted in the camera perspective, not an upright monitor. Camera starts wide from above/front, pushes toward comp, follows mascot close on toolbar at 2.5–3.5, moves to right Effects panel at 4.5–5.0, tracks low along timeline at 6–9.5, then pulls up/back to isolate comp. Main comp fills central workspace. Final mascot sits at comp lower right corner without obscuring subtitle. Source has music and precise effects; recreate the sound using code per page 6, don't reuse original track.

## Implementation and output

Keep `timeline.py` as the shared owner of UI geometry, per-frame state and audio cue times. HTML/canvas textures feed distinct Blender panel slabs; the scene bakes all 360 frames for direct seeking in Blender. The included `scene.py` contains the accepted camera repairs for the opening pop, Glow flip and Play leap. Do not overwrite these with an older scene.

Output: 12 seconds, 1920×1080, 30 fps, 360 frames, H.264/AAC MP4, poster and editable `.blend` plus sources. Frame f uses wall time (f−1)/30. Check jump apices, tool contact and the final subtitle as well as representative stills; inspect a motion sample before the full pass. Reopen the scene with its generated `textures/` beside it. Render through `gpu.py` on each process (this starter selects Metal).

For adaptations, change only the requested copy/story/layout, preserve agreed successful beats, and revise duration-specific audio/encoding/verification code together if duration or tempo changes. Do not promise pixel identity or audio quality based only on technical checks.

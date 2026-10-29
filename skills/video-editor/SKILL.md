---
name: video-editor
description: "Edit and assemble video with available local media tools such as ffmpeg: trim, concat, overlays, transitions, speed, crop, scale, captions, audio mixing, normalization, GIFs, and edit decision lists."
---

# Video editor

For new code-generated or procedural scenes that need editable source and re-rendering, use [animation-creator](../animation-creator/SKILL.md). Use this skill to assemble or finish their exported media with other footage and audio.

For editable CapCut desktop projects, use capcut-local (external resource; not included): assemble native tracks through the local MCP and verify/finish them in CapCut. Preserve the editable project rather than substituting a flattened render.

For searching a substantial or reused footage collection, read [footage indexing](references/footage-index.md). For recurring founder clips, interviews, or demos, read [verified format recipes](references/format-recipes.md): complete a representative edit, preserve the working procedure in the project, and reuse it with new source material. A contained trim needs neither a library nor a new format recipe.

For social and launch videos, read packaging and attention (external resource; not included). Review the title/cover, first second, first five seconds, first ten seconds, and later intervals in that order before polishing the timeline. Identify what changes and what the viewer wants to see next; remove or replace beats that only display setup or repeat a claim. A screenshot montage with zooms is not sufficient evidence of an engaging demonstration. Preserve approved story decisions and judge pauses by the attention they sustain, not a fixed cut frequency.

For side-by-side demos, read comparison-demo packaging (external resource; not included) when trimming idle footage or aligning visible action. Preserve common timing and playback speed for speed or latency claims; an illustrative alignment must disclose material offsets. Inspect crop and capture quality at phone size.

Editing and rendering are execution work. Confirm the input files, output path, available tools, and requested deliverable before changing media. Check `command -v ffmpeg` and `ffprobe -version`; inspect each input with `ffprobe` for duration, streams, codec, resolution, frame rate, and audio channels. Keep source files and prior cuts intact, write outputs to an explicit project directory, and preview a short segment before a long render.

Use frame-accurate re-encoding when cuts must land precisely; stream copy is appropriate only when keyframe and codec constraints are acceptable. For mixed inputs, normalize resolution, frame rate, pixel format, and audio layout before concat. For captions, logos, and UI, composite them in post. For audio, measure real voice durations, duck music under speech, normalize to the requested loudness, and verify sync at several timestamps.

For one long talking-to-camera take cut into short clips, follow [single-take talking video](references/single-take-talking.md): word-timed cuts, spoken "cut that out" cues, best-of-repeats, face crop, and every length rendered from one EDL.

For multi-take edits, create a reviewable JSON EDL with source take, in/out seconds, scene ID, and rationale. Select on performance, clean starts/ends, continuity, and intelligibility. Re-render from the EDL instead of making opaque manual changes. After rendering, verify full decode, duration, stream presence, frame samples, audio levels, and any requested caption or transition behavior. Decode proves file integrity; it does not prove artistic quality, pacing, emotion, or lip sync, so label those judgments separately.

When deciding how long to hold a shot, use the Columbo phone-call example (external resource; not included). Keep an ordinary task on screen if it gives viewers something to anticipate. If unsure, compare shorter and longer edits and watch which works better.

For AI-generated sequences, assemble representative shots early so continuity and performance problems are found before more generation. Cut for setup, reaction, consequence, and payoff; do not force quick cuts where a held moment carries the scene. Unify voices, room tone, sound perspective, and color across separately generated clips. Test texture, grain, and upscaling on the actual output; they can damage detail and do not repair weak story or acting. Mark the precise missing reaction, insert, transition, or audio beat for the production workflow when an edit cannot resolve it. See AI creative judgment (external resource; not included) for audience-payoff and authenticity checks.

Sources: [Mork editing workflow (2026-04-25)](https://pjace.beehiiv.com/p/you-re-using-seedance-2-0-wrong-try-this-massive-time-saver-instead) describes bringing shots into the timeline during generation; [Patchwright interview (2026-05-13)](https://pjace.beehiiv.com/p/gossip-goblin-s-crazy-workflow-for-building-original-worlds-200m-views) discusses editorial cohesion, sound, and avoiding damaging upscaling. These are dated production accounts, not universal tool benchmarks; verify techniques on the actual output.

This skill may execute local editing commands when the user asks for an edit. It does not generate footage, buy media, publish, or send the output externally unless that scope is explicitly included. Read [references/recipes.md](references/recipes.md) for common filter chains and [references/multi-take-edl.md](references/multi-take-edl.md) for auditable take selection.

For vertical short-form text and graphics, use [Reels placement and keyframes](../reference-style-video/references/reels-placement.md). Keep titles and subtitles in separate useful regions, protect faces and essential actions, and verify the intended platform interface clearance after final crop/scale. Inspect long captions and moving subjects, not just a clean opening frame; the reference rectangle is illustrative, not a universal export-safe template.

For reconstructed messaging or notes UI (iMessage, WhatsApp, ChatGPT, Apple Notes), use [native chat and notes](references/native-chat-and-notes.md).

## Generated media in this workflow

When assembling generated loops or linked shots, use generated media and storytelling (external resource; not included) for continuity, compositing, interactive-delivery constraints, and fallback. Inspect identity, geometry, light, camera, matte edges, and the last-to-first or shot-to-shot join at delivery size and speed. Preserve the selected visual language alongside exact product captures and editable text. Do not hide a failed essential transformation with a cut or change the premise to make a clip usable. Return material direction changes to the host's human checkpoint; editing an approved sequence does not authorize extra generation or a new treatment.

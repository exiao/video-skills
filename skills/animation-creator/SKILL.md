---
name: animation-creator
description: Create and revise animations with Claude CLI, including p5.js generative art, interactive sketches, hand-drawn write-on text, brush-painted photos and video, 3D recreations, motion graphics, explainers, and mixed-media sequences. Deliver interactive HTML, rendered video, or the requested editable format.
---

# Animation creator

Turn a concept or reference into a finished animation. Use Claude CLI for implementation, inspect rendered output, and iterate on the actual piece. The skill generalizes the process, not the appearance of a previous example.

## Generated media in this workflow

Use [generated media and storytelling](../shared-video-references/creative-exploration.md#generated-media-and-storytelling) when generated illustrations, physical motion, materials, or atmosphere better express the piece than code-only primitives. Combine those assets with code for precise typography, controls, compositing, or timeline interaction; retain an explicitly requested procedural or offline implementation. Establish the keyframe and short motion sample before coding the full sequence. When Content Factory coordinates the work, its human creative checkpoints (external resource; not included) also bind Claude and other delegated makers: preparing a rough option is allowed, committing to an unselected direction is not.

## Understand the piece

For article illustrations or animations in Eric's selected cream-and-orange style, use lenny-image (external resource; not included) for appearance and text density. Read the project's `BRIEF.md` and the brief beside the source asset when present; carry their selected copy, source version, exclusions, and preservation decisions into Claude's assignment. A style change or simplification must preserve selected labels and subtitles unless the user asks to change them. Update the asset brief after consequential feedback so another chat can reuse the decision.

Use the user's subject, message, audience, visual references, duration, format, aspect ratio, and sound requirements. Infer reasonable defaults for a small experiment; ask only when an unresolved choice materially changes the result. Identify what changes over time and the intended payoff. An illustrative loop, explanatory sequence, and interactive experience need different timing and structure. For a claim or test of a one-prompt animation workflow, record the starting brief, tool/model, external assets or services, elapsed work, revisions, and finished artifact so the result can be judged against the claim.

Do not impose a subject, palette, texture, number of scenes, duration, frame rate, silence, looping, or asset restriction. Risograph is only one optional style. References can guide composition, motion, timing, lighting, typography, or texture independently; distinguish what should be preserved from what should be reimagined.

For a reference, inspect representative frames and playback where available. Label inaccessible details and interpretations. Use the relevant video-direction or reference-style-video skill when substantial shot planning or reference analysis is needed. For a code-authored 3D recreation that must match a clip's action and timing, use [reference-style-video](../reference-style-video/SKILL.md) to establish what stays or changes, then read [reference-driven 3D recreation](references/reference-driven-3d.md) before building the scene.

Translate a reference into a motion brief, not a style name alone: note its framing, type scale, scene length, visual density, sound accents, and the exact mechanism that moves one state into the next. Pick only the parts that serve this piece. When several references are available, give each a distinct role rather than asking Claude to imitate all of them wholesale. Preserve the user's product identity and original story.

For a reference adaptation, give Claude a concrete scene mapping before implementation: the source beat, its motion mechanism, the new subject's message or action, and the assets or copy that express it. Replacing a logo and accent color can leave the source's story intact. Rewrite or remove beats whose wording, numbers, or symbols have no purpose for the new subject, and adjust layout and reading time to the replacement copy. For an original concept, specify the new premise and payoff rather than relying on "improvise"; for a requested faithful recreation, preserve the agreed source relationships.

For pieces meant for social feeds or paid ads, read [social posts and paid-ad videos](references/social-ad-production.md). It gates the story with three divergent options before rendering, lists the hard rules Eric enforced by hand (no meta text, metaphor logic, real logo and data, cut to music, delivery spec), and requires a separate cold-read review of the encoded file.

For a product teaser, inspect the actual project or running product before scripting. Find the entry, meaningful action, and visible result; reuse its real components, copy, screenshots, colors, and type where possible. Make the first seconds reveal the benefit or a distinctive visual hook. Do not invent features, testimonials, metrics, or UI states to make the animation easier.

For 3D character animation staged on video editor panels—walking across the interface, pressing tools, adding keyframes or riding a playhead—read [3D characters on video editor panels](references/clawd-motion-studio.md). The worked reference is 0xwhrrari’s “No After Effects. Just Clawd.”, with Clawd as the example character. It includes the [original post](https://x.com/0xwhrrari/status/2112166940081004693), install commands, the accepted source starter, exact beats, measured rendering costs, and fixes learned from the build traces. Copy the starter into a fresh project for the same video; use Claude for requested adaptations. Its Blender/HTML/audio stack and 12-second story are example choices, not general defaults.

## Start from the material the user has

Choose a brief shape that matches the input. These are options adapted from [Vox's code-animation thread](https://x.com/Voxyz_ai/status/2102805198838321649), not fixed prompts or promises about speed or cost:

- **Reference clip:** Ask Claude to identify the visual system, timeline, transitions, and rendering technique before building a new version. State what to preserve and what may change. Inspect the source and output in motion; a request to “reverse-engineer” does not establish that the result matches.
- **Idea only:** Give Claude the intended outcome and room to propose the story, look, and implementation. Use high reasoning when the open-ended creative work warrants its time and cost; review a representative result before expanding it.
- **Character or product image:** Supply the actual image and its role, then specify the story or product payoff, audience, duration, and destination. Keep recognizable identity and truthful product UI where those matter. A screenshot can guide animation without requiring every frame to be generated from it.
- **Specific art style:** Translate the style into executable constraints: drawing resolution and scaling, palette, edge treatment, frame cadence, movement phases, and loop behavior where relevant. Pixel art might use a low-resolution canvas scaled by whole numbers with antialiasing off; those choices do not apply to every style.

## Choose the simplest suitable medium

Keep an existing project stack or an explicitly requested native format. Otherwise choose based on the visual problem:

| Need | Useful starting point |
| --- | --- |
| Text, shapes, diagrams, interface motion | HTML/CSS, SVG, Web Animations |
| Illustrated scenes, particles, procedural textures | Canvas 2D; p5.js if it materially helps |
| 3D geometry, lighting, camera moves, heavy effects | WebGL/Three.js or the requested native 3D tool |
| Layered footage, images, typography, synchronized audio | A compositing/timeline workflow; existing Remotion or video-editor tooling when appropriate |
| Interactive artwork | Browser renderer with intentional input and playback behavior |
| Self-contained story, explainer, or motion graphic delivered as MP4 | Code-generated scenes and timeline, local audio synthesis or supplied audio, deterministic frame export, then local encoding |

These are options, not required dependencies. Use installed tools where possible. Single-file HTML is convenient for small self-contained pieces, but assets, libraries, multiple files, and native projects are allowed when useful. Honor an explicit code-only or offline requirement. Use media-generation skills when needed for assets or footage; do not substitute generated footage for a requested procedural renderer or assume permission for paid generation.

Use the installed [claude-cli skill](../claude-cli/SKILL.md) for model, effort, authentication, resume, and delegation conventions. Supply the relevant source/reference paths, concrete write boundaries, visual and motion brief, output contracts, and verification requirements. Ask Claude to build and inspect artifacts, not merely explain how. Preserve user-selected tools and models.

When testing an “all made with Claude” claim, distinguish **Claude authoring code** from direct video generation. State which renderer, encoder, audio tools, assets, and outside services actually produced the file. Do not describe local FFmpeg or browser rendering as model-native video generation. A no-external-generation brief can still use installed local software and self-authored assets; keep it offline when that is part of the test.

## Develop appearance and motion together

For shared timelines, reusable brand motion profiles, camera choreography, narration timing, aspect-ratio variants, motion B-roll, or substantial films needing signature moments and independent comprehension review, read [motion craft and production recipes](references/motion-craft.md). Use only the techniques relevant to the brief; the linked repositories supply examples rather than additional mandatory workflows.

For mechanical explainers, exploded views, or physical-product reveals, read [mechanical explainers and product reveals](references/mechanical-explainers-and-reveals.md). It covers shared object models, assembly motion, feature demonstrations, and reveal pacing. Establish the mechanism and a short disassembly/reassembly sample before expanding detail; distinguish measured dimensions and documented internals from illustrative assumptions.

Establish representative compositions and a short motion sample early. For typography, prioritize hierarchy and reading time; for characters or illustration, silhouette and gesture; for 3D, lighting and camera; for data, truthful transitions and legible scales. Do not let ornamental effects obscure the subject or message.

For a new narrative animation, product video, or multi-scene piece, use [$storyboards](../storyboards/SKILL.md) to create three illustrated storyboard options before the full motion build. Make them meaningfully different in story, opening hook, visual approach, or pacing. Give each option its intended visual direction through the storyboards skill's editable style profile. Show the actual board images with approximate timing, visible action, transitions, payoff, and sound cues where relevant. ASCII or text-only storyboards are appropriate when explicitly requested; they are not the default creative review artifact.

Claude may draft the narrative and panel specifications, but complete the storyboards skill's image-generation and visual-inspection steps before presenting the options. Pass the verified board files and chosen style brief to Claude as concrete references for implementation. Wait for the user to select one or more options, then show one representative still per scene; reuse approved storyboard panels when they already establish that composition. Resolve requested composition, copy, and story changes before expanding into full motion. Carry an already selected storyboard forward for revisions or faithful remakes. A simple loop or isolated interface effect needs only its relevant key states unless the user requests a storyboard.

For a multi-scene or music-led piece, map what carries between scenes and where the audio accents land in the selected storyboard. Inspect at least one transition in playback after the scene stills; stills establish composition but cannot verify timing or motion.

Give motion a purpose: anticipation, action, follow-through, pacing, pauses, and transitions should support the piece. Use easing intentionally. Test camera movement, parallax, or transformations in playback rather than judging still frames alone. Plan sound cues with the timeline when audio is requested.

For procedural environments, separate slow scene changes from fast local motion: season or daylight, wind-driven plants, drifting particles, and moving light need different time scales. Couple effects that share a cause, such as wind affecting both attached foliage and falling leaves, while varying phase and strength so the scene does not move in lockstep. Keep silhouettes and depth readable through the change. Use these relationships when relevant to the brief, not as a requirement to add effects.

Continuous transformation is useful when the story benefits from object permanence: a button can become a loader, a photo can become a card, or a status shape can become the next scene. Keep a recognizable edge, position, color, or content relationship through the change; make pointer clicks and drags visibly cause state changes when a cursor is part of the piece. Coordinate camera moves with the transformed object and scale the cursor with the camera. Give entering and exiting text its own timing and mask so labels stay readable instead of overlapping. Use cuts, fades, or holds when they communicate better; a continuous take is a direction, not a default.

If a song drives the sequence, measure its beat and section changes, then place important actions on chosen beats rather than forcing activity on every beat. Align effects by their audible peaks, audition the complete mix, and allow settled text enough time to read. Use the source story to choose collage layers, archival material, stickers, or recurring props; each addition should explain a specific claim or transition rather than fill empty space.

Choose sound by the brief: synthesize a score in code when code-only or offline creation is the point, or use supplied/local samples and appropriately licensed audio when natural instruments or effects matter. Time sound to story beats, audition it with the video, and revise the score if it does not support the action. Do not silently add an external voice or effects service to a code-only brief.

Iterate with specific keep/change instructions against actual renders. Preserve successful work and use Claude's resume flow for bounded revisions. Scale scenes and detail after the core visual/motion idea works. Do not require approval between routine local iterations unless a creative decision truly needs the user.

## Make playback and export reliable

For browser animations intended for video, expose an explicit seek/render contract such as `renderFrame(frame, seed)`, `FPS`, and `TOTAL_FRAMES`. Drive visual time from frame index during export and await completion. For DOM/CSS animations, pause autonomous playback and seek timelines; for 3D, await rendering/assets; for simulations, use a fixed timestep with reset/replay or checkpoints rather than pretending every state is analytically seekable. See [references/workflow.md](references/workflow.md).

For a tightly timed, code-authored morph, a pure `seek(t)` with time-derived transforms and closed-form easing can make any frame reproducible. During a drag, derive the controlled value from pointer position; spring from the release state afterward. If the piece includes video, make frame seeking reliable before committing to full export. These techniques are optional implementation choices, not requirements for ordinary interface motion.

Live playback may use elapsed time, but export must not race it. Keep randomness seeded when reproducibility matters. Deterministic per-frame noise can still flicker; anchor texture to the appropriate object/world/screen coordinates. Reset mutable renderer state between independent frame requests.

Wait for fonts, images, shaders, and other required assets before capture. Match capture dimensions and device scale to output dimensions. Canvas backing dimensions and CSS screenshot dimensions are different. Keep controls outside the exported artwork. Preserve alpha in a suitable format if requested; MP4/H.264 is not the transparency default.

For interactive delivery, provide appropriate playback/input controls, responsive layout, and reduced-motion behavior. For a promised loop, verify the last-to-first boundary including audio; a non-looping piece needs its own ending.

## Verify and deliver

Use checks appropriate to the requested output, not a fixed universal suite:

- Inspect representative frames/contact sheets AND playback. Check composition, readability, timing, motion, transitions, unintended flicker, and any loop seam.
- For beat-mapped work, inspect frames on selected beats and around scene boundaries before rendering everything; scan the output for isolated one-frame jumps and review any flagged moments in playback. Give revision notes as concrete changes to timing, framing, path, or transition.
- For rendered media, verify dimensions, duration, frame rate/count, audio presence/sync, and full decode. Exact-frame export should cover indices 0 through N−1. Inspect the encoded output as well as source frames.
- For a one-prompt workflow test, compare the finished piece with the brief and report the first-pass result and any corrections separately. Include the actual soundtrack check when sound was requested; a muxed audio stream alone is not evidence of audible, well-timed sound.
- For deterministic renderers, compare repeated renders and frame-order behavior in a consistent environment. Only require changed-seed variation if the piece actually uses seeded variation.
- For self-contained/offline work, block external requests and verify a nonblank complete render. Do not apply a no-assets rule to an asset-based brief.
- For HTML/native projects, exercise the actual controls and reopen the delivered artifact; preserve editability if requested.
- For interactive simulations, check that parameter changes affect the depicted behavior, pause freezes simulation time, and reset restores the intended state. For physical behavior, inspect contacts, resting states, and responses to moving boundaries at different playback rates; reject visible tunneling or unexplained energy growth when they violate the intended model. Attractive trails or shaders do not establish correct physics.
- For factual explainers, verify the depicted chronology, labels, and causal claims against appropriate sources before final export; distinguish illustrative motion and speculation from supported facts.

Fix observed failures and recheck the affected outputs. Separate technical verification from subjective artistic judgment. Return the requested playable video/preview and links to editable source. Do not publish without authorization.

## Optional examples and libraries

Read [worked examples and the reference library](references/examples-and-library.md) when the brief calls for a reference adaptation, frame-locked remake, printed jellyfish, lyric-driven painted video, or a relevant engine/library example. It preserves the source prompts, links, example-specific limits, and read-when routes for GSAP, HyperFrames, product teasers, loaders, Anime.js, the HTML gallery, p5.js, and p5.brush. Load only the examples or technique guides relevant to the brief.

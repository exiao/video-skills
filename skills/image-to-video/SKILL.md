---
name: image-to-video
description: Animate an existing or prepared still image into an actual video clip using a suitable browser model, Google Flow, Higgsfield, or fal API. Use for image-to-video requests, animating a photo or keyframe, or a video brief that needs a start frame prepared first. For video editing or coded motion graphics, use the relevant editing or animation skill.
---

# Image to video

Own the generation through a saved, inspected clip. A prompt or provider recommendation alone is not a completed image-to-video task.

## Input and motion

Inspect the supplied image first. Record its aspect ratio, subject, identity/product details that must survive, current pose and prop state, and any text or hands likely to distort. Keep the original file intact. If the user identified an image that is missing, retrieve it or ask for it. When the brief instead calls for creating the scene from an idea and style references, prepare a reviewable start frame with an image-generation workflow before animating; do not treat a style screenshot as the start frame.

Describe the shot as **start state → physical action → end state**, plus camera movement, duration, framing, and audio intent. Make movement specific and plausible for what the image depicts. Name what should stay fixed. Use a start frame for animating one still; add an end frame only when the user provides or approves a target state. Character or style references are different from start/end frames. Check each model's actual input roles before uploading.

For a realistic character-led clip with several beats, a location or wardrobe change, or identity that must survive multiple shots, use [character-led shot preparation](references/character-led-shots.md). It shows how to assign reference roles, distinguish planned changes from drift, check physical camera geometry and clip-length limits, and test a difficult motion beat before spending on a sequence. A simple one-still animation does not need a character sheet or this extra preparation.

## Choose a route

Honor an explicit provider/model. Otherwise use the user's existing included UI usage or prepaid credits first. For Eric's video workspace, read Documents/videos/AGENTS.md (external resource; not included) for the current preference order: Grok, Gemini/Google Flow, Higgsfield, Midjourney, then other available UIs. Choose among suitable options by required image input, motion fidelity, aspect, duration, audio, export, and remaining allowance. Account entitlements and model menus change: inspect the signed-in UI and costs before generating. A named provider that cannot accept the needed image or motion is unsuitable; explain the constraint and choose the next viable route.

Use the browser route in [references/browser-and-flow.md](references/browser-and-flow.md) for Grok, Gemini/Flow, Higgsfield UI, or another existing account. Use [references/higgsfield.md](references/higgsfield.md) for the Higgsfield CLI. Use [references/fal.md](references/fal.md) for fal API. Read only the chosen route. The CLI/API may have different credits or model access from the website. Never infer one from the other.

Before any paid API run, verify current endpoint, accepted input fields, duration/resolution limits, price including reference input and retries, and available authorization to spend. If authorization is absent, prepare the exact request and cost for review; do not submit it. Included subscription usage and existing prepaid credits can be used for an authorized generation task. Do not buy credits or upgrade plans without authorization.

## Generate and finish

1. Submit one short, low-cost draft when uncertainty about motion or identity is high; keep the intended shot duration when a shorter draft would hide the critical action. Record provider, model, mode, source image, prompt, settings, job/project link, and credit/cost evidence. Never expose keys.
2. Wait for a terminal result. A submitted job is not a finished clip. Download or otherwise retain the actual video file when possible; preserve the project/job link too.
3. Play the clip with audio if present. Check the requested movement, first/last frame, subject/prop continuity, hands/faces/text, camera behavior, duration, crop, black frames, and sound. Use `ffprobe` or equivalent for dimensions, duration, codec, and audio stream when a local file exists. Sampled frames alone do not prove temporal quality.
4. If it fails, change one major variable (model, reference role, prompt, motion strength, or duration) based on the observed defect. Bound retries by available usage and authorized spend. Deliver the best inspected clip with its path/link, model/settings, and any visible defect; distinguish generation completed from quality approved.

Use `video-direction` when the user needs a multi-shot treatment; `reference-style-video` when motion must follow a source video; `video-editor` to assemble finished clips.

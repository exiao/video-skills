# Character-led realistic shots from stills

Use this when a person, vehicle, product, or location must stay recognizable across generated motion or multiple clips. The [@abxxai thread](https://x.com/abxxai/status/2102775755646337530) is a useful example of a character sheet → composed start frames → timed motion prompts. Its attached 19-second video was sampled locally. The written prompts are evidence of the creator's intended workflow, not proof that every constraint rendered as requested.

## Prepare only the references the action needs

Start from the user's idea and any inspected style screenshots. Turn them into a small asset plan: character identity, scene geometry, one start frame per materially different camera setup, and the intended movement. The source thread used Claude to write these prompts, but the useful mechanism is this explicit preparation and review, not a required writer model.

- Choose one image that owns the **first frame and scene composition**. Check aspect ratio and crop against the planned video. The first video frame should resemble it, but treat pixel-exact matching as a result to inspect, not a guarantee.
- If identity must persist, keep a clearly identifiable portrait and, when needed, a body/wardrobe view. A multi-panel character sheet can help plan expressions and details, but supply only views the selected model can interpret cleanly. Do not make a sheet mandatory for a one-off still animation. Use the [video-direction reference-role guidance](~/.codex/skills/video-direction/references/prompting.md#reusable-reference-packs) for recurring assets.
- Label each input's job: `start frame`, `identity`, `wardrobe/product`, `setting`, or `style only`. A style image should not import another person's face, text overlays, or props. Check the provider's actual slots and limits, then attach each file to the right role; prompt labels alone do not upload media.
- Reconcile one continuity manifest before submission: person and wardrobe, prop/vehicle identity and color, door/seat/location geometry, light direction and time of day, lens/framing, and aspect ratio. If still and motion instructions conflict, fix the source assets or shot plan first.

### Planned changes are states, not drift

The [QAiStudio slice-of-life example](https://x.com/QAiStudio/status/2102643806424506710) asks for one subject across nine everyday beats while deliberately changing her top halfway through. Record **invariants** (face, hair, body, necklace, jeans) separately from **shot state** (top, location, props, time of day). Put the outfit transition at a named cut or visible action, and prepare a matching reference for the new state if the model needs it. Check both sides of the transition: an intentional shirt change must not also change identity or unrelated accessories. Treat a prompt label such as `img` as a description until the image is attached to the provider's actual reference input.

## Direct one physically coherent shot

State **who holds the camera, where they are, what lens/framing they have, and what movement their body permits**. A friend in a car implies small handheld sway and delayed focus/exposure response; a fixed camera can remain in place while the subject moves. Pick a camera behavior that fits the blocking rather than stacking incompatible moves.

Break the action into a few timed beats: initial pose and hold, movement with contact points, reaction or spoken line, ending pose. Describe the observable movement of hands, feet, gaze, fabric, and props where it matters. For an actor entering a car, verify which door, which seat, where the camera sits, what remains visible through the window, and how the face changes scale. If that transition is the hard part, test it before generating the surrounding shots.

Keep dialogue, breaths, ambient sound, and music roles explicit. If a line must lip-sync, inspect the actual mouth and audio timing. If the final edit needs beat-synced cuts or captions, plan and verify those in the edit; prompt prohibitions do not guarantee their absence from a posted example.

## Generate and review

For a continuous shot, ask for one camera position and the permitted human movement. For a montage with materially different viewpoints, either use a model that supports multi-shot structure or generate shot-specific clips and assemble them. Reuse approved identity/location assets and state transitions across clips; do not force a multi-location script into one image-to-video call merely because the example did.

Check the selected endpoint's maximum duration before translating a long reference prompt. QAiStudio posted a roughly 30-second, 1280×720 file, but the post does not establish whether it came from one call or assembled clips. As checked on September 23, 2026, [fal's Seedance 2.0 image-to-video endpoint](https://fal.ai/models/bytedance/seedance-2.0/image-to-video/api) accepts 4–15 seconds per request. For that endpoint, divide a 30-second plan into supported clips, place boundaries at natural shot or wardrobe changes, and carry forward the approved identity and scene state. Recheck limits for other routes and later model versions.

For a raw handheld look, assign camera behavior to each beat: who follows, when the operator reacts or reframes late, when focus/exposure briefly hunts, and where movement settles enough to read the subject. Varied, motivated imperfections create the feel; a blanket instruction for heavy shake can obscure the action. The QAiStudio clip's sampled frames show the planned shirt change and varied camera distances, but still frames cannot establish the quality of its motion or sound.

Before submitting, map `start frame` and optional extra references to the chosen provider's documented input fields. For Seedance 2.5 via Higgsfield, inspect the live schema and use a reference-accepting mode such as `omni_reference`; `t2v` will reject media. For another provider, follow its own schema. Then run the shortest draft that exposes the difficult action and inspect the downloaded video at normal speed.

Check first-frame match, physical path and contact, identity, car/prop geometry, light and color across cuts, audio/lip sync, overlays, and the requested duration. In the source thread, the start-frame prompt describes a silver sedan and rear passenger door while the animation prompt calls it white and front passenger; one reference asks for 4:3 while the video is 16:9. The posted clip also contains captions despite a no-captions instruction. Resolve such differences in your own asset manifest and judge the render, not the confidence of the prompt.

# Motion craft and production recipes

Use these recipes for code-authored films, recurring brand animation, and narrated motion inserts. Keep the current project stack and selected direction. Original sources were inspected October 9–10, 2026; the Anatomy Reveal sampling reference was inspected October 21, 2026. Their production claims and helper scripts have not been independently reproduced.

## Shared timeline

For a piece with several scenes or sound cues, maintain one timeline of named beats. Scene animation, audio cue placement, and review-frame capture read those same beats. Store seconds or frame indices with an explicit frame rate; use relative offsets for local choreography. Retiming a reveal should also retime its sound and review snapshots.

For example, `reveal.start`, `reveal.settled`, and `reveal.exit` can drive the visual, a sound peak, and a readability capture. If the sound's peak occurs after its file starts, place the file early enough for the peak to land on the intended beat. Rebuild the mix after changing timing and inspect the encoded join. A small loop can keep these values in its existing source rather than adding a manifest.

Source: [claude-motion](https://github.com/whaleyxbt/claude-motion), especially its [motion rules](https://github.com/whaleyxbt/claude-motion/blob/main/.claude/skills/motion-design/SKILL.md).

## Motion profile and timing recipes

For recurring brand work, record the selected motion language in existing brand documentation or a compact `MOTION.md`: easing families, typical entrance/exit/settle durations, reading holds, camera energy, texture, and exclusions. Carry exact supplied brand tokens forward. Still references establish appearance; inspect playback before inferring timing or easing. Keep unknown motion properties separate from observed ones. Reuse the profile in maker assignments and render review without requiring another intake for an established project.

Useful starting recipes, adjustable to the output and audience:

| Action | Starting choice | Review |
| --- | --- | --- |
| Entrance | Decelerating ease-out | Arrives decisively and settles cleanly |
| Exit | Accelerating ease-in, often shorter than entry | Clears without competing with the next subject |
| Movement between states | Ease-in-out or a suitable physical spring | Preserves object relationships and intended weight |
| Word reveal | Try about 0.09 seconds between words | Long lines still complete with time to read |
| Reading hold | Try at least one second for a short phrase after settling; extend for longer copy | Read at phone size without tracking moving text |

These values are examples from a source piece, not universal timing rules. Brand, action, narration, and observed readability determine the final values. Static holds, linear continuous movement, and restrained effects are valid when they serve the piece.

Sources: [brand intake](https://github.com/charlie947/motion-graphics-skills/tree/main/skills/brand-intake), [claude-motion timing](https://github.com/whaleyxbt/claude-motion/blob/main/.claude/skills/motion-design/SKILL.md), and [LottieFiles motion principles](https://github.com/LottieFiles/motion-design-skill).

## Camera choreography

Choose camera energy with the treatment: locked, subtle, motivated by action, or continuously moving. Record the intended focal target and reason for consequential moves. Distinguish camera movement from movement of elements within the shot. Let the important action become visible before following it when that causal order helps comprehension.

When element motion already commands attention, reduce background camera drift. Keep copy on the focal plane during a depth move unless a deliberate focus transfer is the action. Check the focal subject, cursor, and text bounds throughout zooms and transitions. Vary repeated moves where repetition weakens the sequence; a consistent locked camera is also a legitimate direction. Do not import perpetual-motion or fixed reaction-delay requirements.

Source: [Klik camera craft](https://github.com/t3knobox/klik-anim-skill-creation/blob/main/klik-cam/SKILL.md).

## Narration and motion B-roll

For narration-led work, measure the actual recording before fixing scene lengths. Cue a relevant reveal to the word or phrase it explains when that improves understanding. Word-level alignment supports precise timing; subtitle cue bounds and interpolated word times are estimates. Check important cues against the recording and retain their timing uncertainty. Music accents support the explanation without forcing each reveal onto a musical beat.

For inserts over existing footage, plan each passage as a full-frame cutaway, a transparent panel in available space, or unchanged footage. Choose by explanatory value and composition. Preserve space around the speaker, real UI, and captions; do not force every passage into one morphing shape. Match insert resolution and frame rate to the edit. When inserts are the deliverable, include clip paths, in/out times, covered lines, an assembled preview, and a synchronized before/after comparison where useful. Use a suitable alpha codec for transparent overlays.

Sources: [product launch motion](https://github.com/AbubakrChan/product-launch-motion) and [motion B-roll](https://github.com/Barty-Bart/motion-graphics/tree/main/skills/motion-broll).

## Aspect ratios and export finish

For requested format variants, recompose the scene for each aspect ratio: text wrapping, subject scale, UI bounds, overlays, and camera framing. Reuse the story and assets while checking each exported version separately. Cropping is sufficient only when it preserves the intended composition and readability.

For fast movement that looks staccato in frame capture, try subframe sampling across a chosen shutter interval. Blend only samples within the same shot; do not blur across a hard cut. Compare a short draft with and without blur before paying its full render cost. Keep text sharp during reading holds.

For pieces that alternate fast whips and settled holds, consider adaptive sample counts based on movement in output pixels during the shutter interval. Track projected bounds, camera targets, and moving assemblies or feature points so local motion counts even when the camera is still. A starting rule is `samples = clamp(ceil(pixelTravel / pixelsPerSample), 1, maxSamples)`, with the threshold and cap chosen from a short render. Inspect fast frames for separated ghost copies and increase sampling or shorten the shutter if needed. Keep shutter duration independently adjustable; the source's full-frame shutter and sample cap are example settings. See [Anatomy Reveal's rendering method](https://github.com/annnguyentt/anatomy-reveal-skill/blob/main/references/shots.md#motion-blur-and-encode).

When preview and export differ, inspect the actual encoded frame and isolate renderer/compositing behavior. Check blend modes and filters, perspective flattening, transparent layers, font/assets readiness, color range, and grain before changing the entire treatment. For an inaudible effect, inspect its source onset and mix masking as well as gain. Detailed scripts from these repositories need inspection and a local trial before reuse.

Sources: [Animate format variants](https://github.com/cth9191/animate), [Howseen rendering pipeline](https://github.com/howseen-ai/claude-motion-design), and [product launch troubleshooting](https://github.com/AbubakrChan/product-launch-motion).


## Concept and independent film review

Adapted from [Min Choi's motion-director prompt](https://x.com/minchoi/status/2111306178164584547), inspected October 18, 2026. These techniques supplement the existing storyboard and review workflow; the source's production and quality claims have not been independently reproduced.

- **Signature moments:** For a substantial narrative or product film, describe 1–3 memorable actions in the existing concept or storyboard before choosing effects or libraries. Say what visibly happens and why it serves the message, rather than naming an effect. Use these moments to distinguish the storyboard options; carry the selected ones into implementation.
- **Claim traceability:** For factual or product films, map consequential on-screen and spoken claims to their source passages and URLs or files in the existing brief. Check final copy and narration against that mapping, including claims introduced during revisions. A separate facts file is useful only when the volume warrants it; source support still needs the factual verification required by the main skill.
- **Audio-only review:** When sound is part of the brief, audition the mix alone before final assembly for pacing, intelligibility, masking, and abrupt edits, then review it with the picture. Intentional silence and visual timing may determine the mix; audio-first editing is an option for music- or narration-led work.
- **Independent comprehension review:** For substantial films, use a fresh reviewer who receives the rendered piece and audience context without the intended story explanation or builder's rationale. For a piece meant to communicate silently, have them watch silent playback and retell what happens, what causes the result, and the takeaway. Compare the retelling with the brief afterward. For narration-dependent work, check the full audiovisual explanation and use the silent pass only to assess visual clarity. A contact sheet can support frame inspection but cannot establish motion comprehension.
- **Focused revision:** Ask the reviewer for ranked, timestamped problems. Fix the most consequential mismatch first and recheck the affected passage and earlier findings. Keep notes in the existing review record; a new critic after every scene and a separate ledger are unnecessary for ordinary work.

For the early complete export check, use the [production workflow](workflow.md#claude-brief-template). Keep review effort proportionate to the piece. These recipes do not prescribe constant movement, beat-aligned cuts, fixed loudness targets, or a ban on screenshots or generated assets; the brief and observed result determine those choices.

## Engine guidance

Keep this skill as the production entrypoint. When a project uses Remotion or GSAP, consult their maintained [official Remotion skills](https://github.com/remotion-dev/skills) or [official GSAP skills](https://github.com/greensock/gsap-skills) for current APIs. A project-local installation can be useful for repeated work with that engine; it is optional, not a dependency of this skill. Use the existing HyperFrames reference when that renderer fits. Do not install a broad creative pack just to obtain one recipe.

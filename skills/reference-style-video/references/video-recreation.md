# Reference-driven video recreation

Use when the user wants to preserve a video's timing, performance, or shot structure while replacing selected visual elements. This complements style adaptation; it does not imply that every “like this” request needs an exact motion transfer.

## Define what stays and what changes

Put a compact keep/replace map in the existing production document. Resolve it from the user's request and supplied assets, not by copying a creator's prompt wholesale.

| Layer | Example decision |
|---|---|
| Performance | Keep head turns, gesture sequence, gaze changes, and action timing |
| Edit and camera | Keep cut boundaries, per-shot framing, camera path and subject scale |
| Identity | Replace source person using approved character references |
| Wardrobe and setting | Replace outfit and room; preserve them across the new sequence |
| Props and geometry | Decide separately: a door-opening action needs a door in a compatible position |
| Audio and text | Specify supplied track reuse, new recording, silence, caption replacement, and branding separately |

Use only relevant rows. A new setting must support retained actions and camera relationships; resolve incompatible blocking before generation. Distinguish matching performance beats from cloning a person's identity or voice. Reusing a supplied soundtrack does not require voice synthesis; do not introduce voice cloning unless expressly requested with the person's consent. Do not frame a fictional replacement as a real person's testimony or endorsement.

## Inspect the actual input

Fetch the named clip and thread where useful. Record the source URL, available assets, and inspection limits. A prompt saying “four attached images” does not establish that those images were retrieved. Do not invent files, versions, approved identities, provider settings, or hidden workflow steps.

If the upload contains side-by-side examples, borders, captions, or a tutorial overlay, distinguish that comparison wrapper from the video to recreate. Identify the intended panel from supplied context; do not guess which person is real. If the original is unavailable, a panel crop may be usable for analysis, but document its crop, reduced resolution, audio ambiguity, and unknown time offset. Do not feed both people to a model as one motion source unless the requested output is the comparison itself.

Inspect the full motion and audio where tools permit; use frame samples only for visible composition and asset differences. Record each cut and important action beat with source in/out time, framing, start/peak/end pose, gaze, hand/prop contact, camera movement, and audio anchor as needed. Scene detection proposes cuts; confirm boundaries around camera shake, occlusion, and fast movement. A continuous shot needs action anchors even when it has no cuts.

## Prepare and execute a transfer

Use the existing [reference-pack guidance](../../video-direction/references/prompting.md#reusable-reference-packs). Assign replacement portrait, profile, detail, and body views only when supplied or needed; four images are not mandatory. State which reference owns each feature. Separate identity from expression: the replacement images supply the face; the source performance supplies its changing expression. Pick one coherent replacement room instead of leaving “bedroom, kitchen, or living room” unresolved across shots.

Check whether the selected tool actually accepts video conditioning or motion/performance transfer, image references, the required duration, and any requested audio control. Verify current controls instead of inferring capabilities from a viral post. Preserve the user's provider choice. If only still-to-video is available, source keyframes and shot-level prompts can guide a restaging, but do not call it exact motion transfer or silently relax an exact-match requirement.

Test a short segment containing the hardest essential action: head/profile turn, hand/face occlusion, prop contact, or camera-to-subject movement. Compare its timing and identity before expanding. Use one continuous generation when needed to preserve uninterrupted movement and supported by the tool; otherwise split at observed cuts, carrying boundary poses, gaze, prop state, and screen direction. Do not impose a fixed clip count or duration.

If the user asks to retain audio exactly, preserve the provided track in the edit rather than asking a generator to recreate it. Distinguish voiceover from visible speech: an on-camera speaker needs mouth timing checked against that track. If new dialogue changes duration, reconcile the conflict with locked motion/cuts instead of silently stretching the performance. Composite approved captions and graphics in post.

### Adaptable handoff

```text
Source: actual clip path, selected range/panel, timeline origin.
Keep: requested performance beats, cut times, framing and camera motion.
Replace: approved character, outfit, setting; named reference ownership.
Props: retained/replaced objects and compatible positions/contact surfaces.
Continuity: one replacement identity/outfit/room; shot boundary states.
Shot action: measured start → peak gesture/contact → end, with time anchors.
Audio/text: reuse named track, replace, or omit; voiceover vs visible speech.
Look: concrete light, texture and camera behavior that serve this brief.
Verification: important matches, allowed differences, unverified inputs.
```

This is a brief, not literal provider syntax. Include only needed fields. Raw phone footage may benefit from natural exposure, handheld movement, and skin texture when supported by the reference; do not automatically add blemishes, shake, or grain to every person or clip.

## Compare before calling it recreated

Align source and output to the same timeline origin; inspect a synchronized side-by-side and the complete standalone output. Compare cut boundaries and action peaks numerically when exact timing matters. At common timecodes, compare pose, gaze, hand contact, framing, subject scale, and camera direction. Equal duration or cut count alone does not prove matched performance. Set any allowed tolerance from the requested fidelity and delivery frame rate, not an arbitrary universal threshold.

Check replacement success separately: identity throughout turns and occlusions, stable outfit and room layout, intended prop count/state, and no unintended source-person or background remnants. For preserved audio, check the track, edit offsets, sync and final playback; matching narration text alone is insufficient. Route findings to visual-content review (external resource; not included), repair the failed shot/range, and recheck neighboring joins.

Report what was actually inspected, measured matches, remaining deviations, and blocked capabilities. A prompt-only request ends at a handoff. A finished recreation requires an inspected export; sampled frames or an attractive first frame cannot close its motion or audio requirements.

## Source example and limits

Source: [@twoclipping comparison, 2026-09-15](https://x.com/twoclipping/status/2099843401290060145) and [recreation prompt](https://x.com/twoclipping/status/2099843406268637533). The prompt separates replacement person, environment and clothing from retained performance, edit timing, framing and audio; it assigns face, profile, detail and body to four described image references. This is a creator's written method, not a controlled model benchmark or proof of a reproducible complete pipeline.

The downloaded comparison contains 1080×1080 video at 30 fps, about 10.434 seconds of video and 10.495 seconds including audio. Samples at 0.5, 3.5 and 5.5 seconds show corresponding close, full-body and laptop beats across two panels:

[Reference image omitted: Comparison samples at 0.5, 3.5 and 5.5 seconds, left to right]

These samples support visible shot and subject comparisons only. They do not establish which panel is real, exact performance transfer, audio fidelity, or full playback quality. The retrieved prompt describes a blonde replacement in a black tank, while sampled panels show different appearance/outfit combinations; the four referenced character images were not attached in the retrieved reply. Treat the prompt as illustrative and the missing inputs as unavailable. The workflow above is our adaptation, not a claim that this output was produced by those exact instructions.

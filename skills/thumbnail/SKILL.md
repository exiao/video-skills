---
name: thumbnail
description: Create truthful, legible video thumbnails and cover frames by extracting from footage or designing a custom raster asset. Use for thumbnail, cover-frame, or video-still requests; video timeline editing belongs to a video-editing skill.
---

# Video thumbnails and cover frames

Create a still image that makes the video's actual payoff clear at the size where a viewer will encounter it. A thumbnail can create curiosity, but it must not imply a result, feature, person, or claim that the video does not support.

This skill owns frame selection and still-image design. Use a video-editing skill for cutting, pacing, transitions, captions across a timeline, or export of the video itself.

## Generated media in this workflow

Use generated media and storytelling (external resource; not included) when a custom image can express the video's specific tension or reveal more clearly than an extracted frame. Preserve the selected visual language between cover and film; a polished cover must not promise a scene or result the video cannot deliver. Show the cover with the opening and payoff when that comparison informs the human direction choice. Do not expand a cover-only request into video production.

## Develop the packaging before the body

For social and launch videos, use packaging and attention (external resource; not included). Treat title and thumbnail/cover as one promise: the image contributes visible evidence or intrigue, and the title adds a reason to care. For open production briefs, choose this pair before making the body, not as decoration after export. When editing an existing approved video, package its supported payoff faithfully. On autoplay surfaces, make the first frame carry the cover's attention job; do not assume a custom thumbnail will be shown.

For X Article covers, use article-card guidance (external resource; not included) with an available static-design skill. This skill remains focused on video thumbnails; the X Article cover study does not establish winning video styles.

## Choose the approach

### Extract a frame from video

Use `ffmpeg` to inspect candidate timestamps. Do not assume that an I-frame or keyframe is the sharpest or best frame; choose from the actual content.

```bash
# Extract a frame at a known timestamp
ffmpeg -ss 00:00:05 -i video.mp4 -frames:v 1 -q:v 2 thumb.jpg

# Make timestamp candidates for visual review
ffmpeg -i video.mp4 -vf "fps=1/5" -q:v 2 thumb_%03d.jpg
```

Review candidates and choose the frame with the clearest subject, action, meaningful state, and composition. Prefer a frame that shows the video's real payoff over a merely dramatic or technically sharp frame. If the subject is a person, an expression can help when it is natural to the story; a face is not required.

For long footage where manual browsing is costly, use [frame shortlisting](references/frame-shortlisting.md) to narrow timestamped candidates with an available visual decision model, then inspect neighboring original frames. Keep ordinary manual selection for a small clip.

### Design a custom thumbnail

For a custom raster image, use the installed `imagegen` skill and built-in image-generation tool by default. Use another provider or deterministic raster workflow only when the user explicitly asks for it. Read the image-generation guidance when prompting or reviewing the asset.

Brief the image around:

- the specific, truthful payoff visible in the video;
- the main subject or object and the action or state that matters;
- a simple composition that survives a small display size;
- exact text only when it adds information, kept short and checked verbatim;
- the requested visual identity, references, and crop.

Faces, saturated color, borders, and text are optional tools. Use them only when they clarify the video's promise. Do not add generic reaction faces, visual noise, or invented product screens, logos, numbers, or outcomes.

## Platform and format

If a platform is named, verify its current official thumbnail, cover, dimensions, crop, safe-area, and upload or selection rules before finalizing. Platform behavior changes, so do not rely on a fixed specification embedded in this skill. If no platform is named, preserve the source aspect ratio for an extracted frame or state the working format assumption before designing a custom asset.

## Review at the real viewing size

Inspect the full-resolution candidate and a downscaled preview approximating its intended feed or player size. Confirm that the subject, action, payoff, and any text remain immediately legible. Check the crop, contrast, hierarchy, text spelling, faces or hands when present, product geometry, and unwanted artifacts. Validate actual dimensions and file format from the saved file instead of trusting the filename.

Keep two judgments separate: whether the image communicates the video's promise and whether it meets the current platform's technical requirements. Report assumptions, unverified platform behavior, or text-generation limitations. A thumbnail is a creative asset; it does not prove click-through rate, views, or audience response.

Deliver the selected image at a stable path and show it for review. Preserve the original extracted frame or source render when making a revision, and make focused edits that address an observed problem.

## Saved PDF references

For the source rationale behind title/cover expectations and the opening promise, consult the MrBeast PDF pointers in these notes. Its examples inform the packaging decision, not a guaranteed click-through rate. Read source notes (external resource; not included).

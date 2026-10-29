---
name: yt-dlp
description: Fetch online video/audio, inspect media metadata, and download available subtitle tracks with yt-dlp. Use for media downloads and obtaining source captions for video or podcast research; not generic transcription of local files or video editing.
---

# yt-dlp

Use the user's URL and requested media scope. Inspect title, uploader, duration, and available tracks before downloading. For a search request, inspect candidate metadata before choosing a result; the first YouTube search hit is not necessarily the intended recording. Keep downloads in the current project's `output/media/` or the user's chosen directory. Use IDs in filenames to avoid title collisions.

## Runtime

Check `command -v yt-dlp` and `yt-dlp --version`. Prefer the existing installation and its package manager for updates. If missing, use a supported isolated installation such as `uv tool install 'yt-dlp[default]'`, or Homebrew on macOS; do not modify system Python with `--break-system-packages`. Check `ffmpeg` and `ffprobe` for extraction/merging. Full YouTube support also needs yt-dlp-ejs and a supported JavaScript runtime; inspect current [upstream guidance](https://github.com/yt-dlp/yt-dlp#dependencies) when diagnosing runtime errors.

Check the version first on extractor failures, then distinguish outdated extractors, login requirements, unavailable media, and throttling. Updating is a diagnostic step, not proof a login error is false. Use the intended logged-in browser profile only when authenticated access is needed and authorized; do not print/export cookies into logs. Avoid repeated retries on authentication failures or rate limits.

## Commands

Examples use placeholders; replace URL and track language from inspected metadata. `--ignore-config` makes these examples independent of personal yt-dlp defaults; preserve explicitly requested configuration instead when needed.

```bash
# Inspect without downloading; no incidental playlist expansion
yt-dlp --ignore-config --no-playlist --skip-download --dump-json 'URL'
yt-dlp --ignore-config --no-playlist --list-formats --list-subs 'URL'

# Best available video and audio, with a combined-format fallback
yt-dlp --ignore-config --no-playlist -f 'bv*+ba/b' -P output/media -o '%(id)s.%(ext)s' 'URL'

# Audio; convert to MP3 only when requested (conversion cannot improve source quality)
yt-dlp --ignore-config --no-playlist -x --audio-format mp3 --audio-quality 0 -P output/media -o '%(id)s.%(ext)s' 'URL'

# Prefer a supplied subtitle track when available
yt-dlp --ignore-config --no-playlist --skip-download --write-subs --sub-langs en --sub-format vtt -P output/media -o '%(id)s.%(ext)s' 'URL'

# Otherwise request automatic captions and label them as such
yt-dlp --ignore-config --no-playlist --skip-download --write-auto-subs --sub-langs en --sub-format vtt -P output/media -o '%(id)s.%(ext)s' 'URL'
```

Do not hardcode extractor format numbers. If MP4 or a particular codec is required, inspect available formats and choose compatible streams or explicitly transcode; changing the container alone does not ensure device compatibility. For an intentional playlist, bound its scope before removing `--no-playlist`.

For posts with multiple attached clips or quoted videos, inventory each media item within the requested scope. A post ID or `--no-playlist` alone does not establish that all attachments were covered. Retain the post ID plus media ID or attachment index and duration; deduplicate repeated copies of the same media while retaining links to every referring post. Inspect unexpected playlist results to distinguish attachments, quoted material, and unrelated expansion. Report bookmark count, unique clip count, and total duration separately, excluding duplicate media from the duration total.

## Captions as research sources

Use [scripts/clean_vtt.py](scripts/clean_vtt.py) with Python 3. It preserves every cue, its raw text, and its timestamp in JSON, plus a readable timestamped transcript. Text cleanup removes markup and merges rolling overlaps between overlapping cues (or a multiword rolling prefix at a touching boundary); original VTT remains the source of truth. Timestamps are cue bounds, not exact word timing.

```bash
python3 /absolute/path/to/yt-dlp/scripts/clean_vtt.py output/media/VIDEO.en.vtt --output-prefix output/media/VIDEO.en
```

The command writes `.json` and `.txt` without a character limit and reports cue/character counts. It refuses to overwrite existing outputs unless `--force` is supplied. Retain the source URL, title, language, and whether captions are automatic alongside the transcript. Read long transcripts in contiguous sections for comprehensive coverage; sampled sections support only a partial summary. Search the saved transcript for follow-ups, then inspect surrounding cues. Keyword misses alone do not prove a topic is absent.

Do not infer speaker identity from a title alone or present unverified auto-captions as exact quotes. Check important names, numbers, and quoted wording against the recording. Captions do not establish what appeared on screen; inspect media frames when visual claims matter.

When a page lacks a transcript, a public upload of the same episode may provide captions. Verify episode identity and duration, and disclose use of an alternate source. For an X clip, preserve the requested clip's scope; fetch its metadata directly where supported, or use an available X reader/browser. Do not silently replace a clip with a full episode. If no captions are available, use available local speech transcription when within scope and disclose the method.

Check a suspect transcript against the corresponding audio. Repeated nonsense, garbled fragments, or words invented over music or silence are not usable dialogue. Retain the raw output and exclude unsupported text from the summary. Report verified music or silence as no speech, and unrecovered speech as a coverage gap. Use another available transcription method only when that gap matters to the requested result.

## Review coverage

For each reviewed clip, save which caption ranges were read, frame timestamps inspected, playback ranges reviewed with or without sound, evidence file paths, and remaining gaps. Distinguish metadata/thumbnail inspection, partial review, complete transcript review, and full playback; these describe different evidence and can overlap. A thumbnail supports a claim about that frame's appearance. To verify an interaction or procedure, inspect the starting state, action, and result in sequence. Judge timing, transitions, audio, and motion from playback of the relevant sequence. A visible score or dashboard proves the display exists, not the claimed accuracy or business outcome.

When the user asks to watch the videos, review playback across the requested duration, using available captions or transcription to understand speech. Use streaming, browser playback, or a local download as needed within the user's media scope. Give delegated reviewers the same coverage requirement; do not impose metadata-only or no-download limits that prevent it. If full review cannot be completed, identify the affected clips and remaining ranges and report partial coverage explicitly. For an ordinary summary, choose inspection depth based on the claims being summarized and disclose any consequential limits.

## Delivery

When the requested summary depends on onscreen demonstrations, preserve the video and timestamps alongside captions and use content-factory's visual-summary workflow (external resource; not included). Captions alone do not preserve that learning; carry essential frames or clips into the delivered summary. A download-only request still ends with the requested files.

Verify the actual output exists and is nonempty; use ffprobe to check media duration and streams when audio/video was downloaded. Link files with absolute paths in Codex. Report extraction failures or partial coverage explicitly. Downloads do not authorize uploads, publishing, or messaging.

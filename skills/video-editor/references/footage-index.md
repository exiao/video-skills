# Search footage before editing

Use for a substantial library or footage reused across multiple edits. For a few known clips, inspect those files directly. Reuse an existing media catalog when available; a small project manifest can serve the same purpose without a new service.

## Prepare a searchable index

Retain a stable media ID, original path or provider ID, duration, and file version or fingerprint. Attach two distinct kinds of timecoded evidence:

- **Speech:** transcript ranges, speaker when established, language, and whether text came from source captions or automatic transcription. Transcript timestamps must refer to the original source.
- **Visible content:** ranges describing subjects, actions, setting, useful product states, framing, and camera angle. Include silent B-roll. Record whether descriptions came from direct inspection or automated tagging, and flag uncertain labels.

Keep proxies, transcripts, and index rows linked to the original. An altered source invalidates affected offsets and tags; add or refresh the affected records rather than retranscribing unchanged media. Index only the collection authorized for the job.

## Retrieve and verify

Search speech and visual descriptions separately or together according to the shot needed. Return a shortlist with source ID/path, in/out times, why the range fits, and evidence type. Inspect the actual candidate range with surrounding context before selecting it. A transcript cannot establish a visible action, and a visual tag cannot establish what was said.

Open shortlisted ranges or proxies in the editor instead of loading the entire collection. Translate selections into the existing [EDL](multi-take-edl.md), retaining original source offsets even if proxy or timeline offsets differ. Keep final take selection based on performance, intelligibility, and continuity.

## Illustrative retrieval

For “show the founder explaining reconciliation, then a silent shot of invoice matching,” retrieve the spoken explanation from transcript ranges and the screen action from visual ranges. Preview both sources, then place the verified selections in the EDL. Searching transcripts alone would miss the silent screen recording.

## Source and limits

In [Mason Warner's Slash workflow video](https://x.com/masonwarner/status/2110403718604853440), 7:05–7:46, he describes a media library that indexes transcripts and visual content before editing. These instructions capture that method without requiring his chosen vendor. His lower-token-cost claim is an account of his setup, not a measured guarantee for another library or editor.

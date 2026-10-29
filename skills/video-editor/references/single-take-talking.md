# Single-take talking video to short clips

Use when the source is one long phone recording of a person talking to camera (often 5 to 30 minutes, with flubs and retakes) and the deliverable is one or more short vertical clips.

## Steps

1. **Transcribe with word timing.** Run local Whisper (or whisper.cpp) with word-level timestamps. Keep the transcript JSON next to the source; every later step reads it.
2. **Find marked cuts.** Search the transcript for spoken edit cues such as "cut that out", "start over", "again". Drop the flubbed line before the cue and the cue itself. Confirm each one against the audio; transcripts mishear.
3. **Pick the best of repeated lines.** When a line is said more than once, compare the takes on completeness, delivery and timing. Keep one and record why in the EDL rationale (see [multi-take EDL](multi-take-edl.md)).
4. **Cut on word boundaries.** Start each segment at the first word's start and end it right after the last word's end. Remove dead air between segments instead of using a fixed silence threshold. For comedy, a late cut kills the joke; check punchlines at playback speed.
5. **Frame the speaker.** Track the face and crop to 9:16. Vary framing between wide, mid and close on beat changes or reactions; do not change on every cut.
6. **Overlay and caption.** Add screen captures or product images where the speaker names them. Burn one-word or short-phrase captions from the word timestamps, kept clear of the platform interface.
7. **Render lengths from one EDL.** Keep one row per kept segment with a priority. Render the 15, 30 and 60 second versions (and landscape if asked) by dropping lower-priority rows, never by re-editing by hand.

## Verify

Watch every rendered length with sound. Check that no marked flub survived, no word is clipped, captions match speech, and the face stays in frame. A clean decode does not prove the timing is funny or clear.

Source: How I AI, "Claude Code for creators: AI editing is here" (2026-10-19), Brooke Lacey's workflow. One creator's account, not a measured benchmark.

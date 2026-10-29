# Social posts and paid-ad videos

Read this when an animation is meant for social feeds or paid ads (Reels, TikTok, Shorts, X video). The rules come from Eric's corrections in Sep–Oct 2026 asset sessions. The quotes below show what each rule prevents; they aren't copy to reuse.

## Gate the story before rendering

A first idea that goes straight to render produced the escalations "These are not creative enough", "Improve the concepts. They seem weak", and "this is generic slop. it should actually create curiosity, intrigue, make the other person laugh". To avoid that:

- Write three options that differ in premise or angle, not in wording. Give each a hook (first 1.5 s), a turn, a payoff, and a proof beat.
- Pick one against explicit criteria: curiosity gap, specificity, emotional payoff, and fit with the art direction. Record why it won.
- When the user wants many pieces, assign each one a distinct art direction and medium up front. Otherwise they drift toward one house look.

## Hard rules a reviewer checks on the encoded file

1. **No meta text.** That means no eyebrows, footers, "illustrative/fictional/sample data" labels, version tags, credits, or attribution lines. Eric removed these by hand repeatedly ("what the heck"). If a claim seems to need a disclaimer, change the claim.
2. **One idea, minimal copy.** Aim for ≤7 words per card. Allow ≥0.25 s per word plus 0.5 s of dwell. Use ghost UI rather than dense UI nobody can read.
3. **Hook in 1.5 s.** Don't open on a logo or a slow fade.
4. **The metaphor obeys its own logic.** "Doesn't it look kind of weird for a bigger doll to come out of a smaller one?" and "It's 'Approve?', not 'Delegate this?'" were both caught by Eric, not the agent. The reviewer states the one-sentence meaning after one watch.
5. **Product truth.** Use the real logo file, real UI and copy, and real dated data ("this says nothing? give me an example of it actually working"). Never invent features, testimonials, metrics, or returns.
6. **Financial content.** Don't give buy/sell instructions or promise returns. Label a hypothetical pitch inside the story, not in a footer.
7. **Smooth, social-paced motion.** Use deterministic frame export, not real-time screen capture ("why is this MP4 so choppy and bad?"). Land a new beat every 0.7–1.5 s. Hold the end ≥1.5 s.
8. **Cut to music.** Measure beats and the drop first, land the key reveal on the drop, and end on a resolution.
9. **Copy a stranger can follow.** Every number says what it measures: "Hilton +18%" beside "Same hotel rooms." read as room prices, not the stock. Every line makes sense on its own. Eric called a run of clever fragments ("Yes. No. Try again.") "makes no sense." When a visual shows a labeled thing, say plainly what it does.
10. **Delivery spec.** 1080×1920, H.264 yuv420p, AAC 48 kHz, −14 LUFS integrated, ≤−1 dBTP. Keep key text out of the top 220 px, the bottom 420 px, and the right-side action rail.

## Review step

Have a *separate* agent do a cold read of the encoded MP4. It works from a 0.5 s contact sheet, full-resolution frames around each transition, and a loudness/ffprobe report. Its output is a one-sentence meaning, pass/fail on each hard rule, the three most important concrete fixes (timing, framing, copy, or transition), and a 1–10 "would stop the scroll" score. The builder fixes and re-encodes. The self-check that only confirms "no overlap, fits frame" was not enough.

## Deliverables

`final.mp4`, `poster.jpg`, `contact.jpg`, `CAPTION.md` (organic caption, three ad primary-text variants, headline ≤40 chars, hashtags, claims needing verification), `NOTES.md` (story options, beat sheet, music prompt and job, data sources with timestamps), and the re-renderable `source/`.

## Music without paid-generation surprises

Use the provider the user approved for the run. In Oct 2026, fal `fal-ai/lyria2` returned a ~32.8 s, 48 kHz instrumental WAV whose header misreports its length; re-encode it with ffmpeg. `fal-ai/stable-audio-25/text-to-audio` takes a `seconds_total`. Keep to one or two generations per piece and log the prompt and the returned URL. For beat analysis, use `uv run --with librosa`.

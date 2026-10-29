# Native chat and notes reconstruction

Portable execution reference for recreating familiar messaging/notes UI (iMessage, WhatsApp, ChatGPT, Apple Notes) as scripted video. Read only when the brief explicitly requests a reconstructed chat, AI-answer, or typed-note sequence.

Source: an external iMessage video ads reference (iMessage flagship plus ChatGPT/Notes/WhatsApp extension) and Notes App Format in an external ad formats library (static list/checklist structure).
Credit: format popularized by Shiv Sakhuja and the Gooseworks team ([@shivsakhuja](https://x.com/shivsakhuja), [gooseworks-ai/gooseworks-ads-skills](https://github.com/gooseworks-ai/gooseworks-ads-skills)). Treat their pipeline as reference reading; verify licensing before copying code. No installation is required to apply these techniques.

## Transparency (do not skip)

This is a scripted dramatization, not a real conversation, screenshot, or unprompted AI output. Every factual claim inside the thread/answer/note must still be true of the product and trace to a real result, review, or verifiable fact. Do not frame it as a real customer text, real testimonial, real leaked chat, or genuine unprompted model endorsement; use no real customer names. Run paid placements with platform disclosure (e.g. Meta "Sponsored"); never seed as organic found footage. Health, medical, or financial advice inside a fabricated AI answer needs legal review. If a claim needs a landing-page disclaimer, it needs one in the video too.

## Choose the surface

- **iMessage:** friend recommendation; product discovered through a shared result ("what app is that?").
- **WhatsApp:** same timeline pipeline, different UI shell. Do not impose iMessage specifics (no required 8-14 bubble count, late brand reveal, or iMessage SFX).
- **ChatGPT:** authoritative answer to the viewer's verbatim question, awkward phrasing included. Brand lands in the recommendation or a typed follow-up ("what's the best one?").
- **Apple Notes:** private confession, first person, no dialogue. Title is the hook ("Things nobody told me about 45"); product is one understated list item, not the most enthusiastic line.

## Exact UI fidelity

Mimic the real surface in HTML/CSS; do not AI-generate app UI (garbled chrome reads as slop). Copy brand colors, typography, and layout conventions for hook screenshots; reserve image generation for photographic backgrounds. iMessage: dark theme default, full-bleed or iPhone frame (status bar + Dynamic Island) over a relevant photo. Notes: larger title, body list, formatting bar above visible keyboard, iOS-yellow accents. ChatGPT: short paragraphs, one bolded phrase or short list, never a wall of text. End card uses the real brand logo SVG (press kit, Wikimedia, or brandfetch.com), never styled text. Apple/OpenAI UI is their trade dress: regulated or risk-averse brands get legal review, with a generic chat-app / AI-assistant / notes-app skin as fallback.

## Native resolution and deterministic timeline

Record 9:16 master at native 1080x1920: set both Playwright `viewport` and `recordVideo.size` (omitting the latter records scaled-down, blurry text); 1:1 variant is a center crop, not a squeeze. Keep script as reviewable JSON (participants, ordered messages, typing flags, theme). Render all bubbles hidden with `display: none`, drive reveal/composer/scroll from one timeline array, and record in one continuous session (scene-by-scene concat causes micro-flicker). Derive ffmpeg SFX cues from the same timeline so sounds land on bubble pops. Stitch chat to static end card (~3s, no zoom/drift) with a 300ms crossfade; `xfade` needs matching resolution, pixfmt, and fps, so pre-render the end card to matching MP4.

## Typing and sound

Type sent-bubble text in the composer; typed text must exactly equal sent text. Default thumb pace is ~12-15 chars/sec with +/-30% jitter; a requested typewriter speed overrides this default. iMessage pacing: short reactions 250-450ms apart, sentence replies 600-900ms air, ~600ms silence before the closer; typing indicator before sentence replies, silent always, receive SFX only when the bubble lands. ChatGPT: type the question like thumbs, stream the answer in word chunks (not per-character, not whole paragraphs) with a subtle tick and clean stop, no chat tritones. Notes: keyboard taps only, no chat SFX; one typo-and-correction max reads human. Music bed quiet (~30%, highpass ~60Hz), faded ~1.5s before the CTA; send/receive recordings (e.g. BigSoundBank CC0 `bigsoundbank.com/UPLOAD/mp3/1313.mp3` send, `bigsoundbank.com/UPLOAD/mp3/1111.mp3` receive trimmed ~1.4s/400ms fade) normalized loud (~-9 LUFS). Mix with `amix=normalize=0` then limit just under full scale (e.g. `alimiter=limit=0.95`).

## Minimal ship check

- Claims grounded; dramatization disclosed; no fake-testimonial framing.
- Texting/first-person voice read aloud; no ad adjectives in bubbles.
- Composer typed for every sent bubble; SFX on pops, silence on typing; final beat breathes before end card.
- Native 1080x1920 master, static logo end card, no flicker except the crossfade.

# Video prompting

Translate the established concept and visual treatment into the prompt. If meaningful lighting, palette, and camera decisions are missing, resolve them using visual-language guidance (external resource; not included). Describe the intended framing and subject/environment relationship alongside any lens cue; focal length alone does not specify the shot.

Default to opening with the subject and physical action, environment, styling, and meaningful props. Follow with real light sources, color, framing, camera, and tactile texture; weave the concept throughout and specify how the shot evolves from beginning to end. An optional final sentence can name the intended feeling. This written order differs from the concept-first planning order; see the translation example (external resource; not included). Adapt to explicit user or tool-specific formats. Prefer precise verbs such as dolly push, shoulder-camera drift, whip-pan, rack focus, orbit, or locked-off tripod over “moves around.”

Example:

> A couple eats in slow synchrony in a narrow ramen shop, shoulders almost touching; steam rises from their bowls and condensation fogs the window. A magenta sign casts flickering light across the wet glass, balanced by warm counter lamps. A locked-off medium two-shot keeps both diners close in frame; focus shifts from the steaming broth to their faces as they exchange a quiet glance. Fine grain and restrained color support the feeling of ordinary closeness at the end of a long day.

Fill the shot with the established scene elements (external resource; not included): who or what acts, where it happens, and the wardrobe, hair, or props that matter. Preserve story-bearing spatial relationships and behavior; leave incidental decoration flexible.

Keep a prompt focused. Name aspect ratio and duration in the generation settings when available. Do not rely on “cinematic,” “viral,” or “realistic” alone. Avoid asking a video model for readable text, logos, app UI, or subtitles; composite those after the footage exists.

When using multiple references, assign each a role and define rendering boundaries (external resource; not included): identify the source for garment/identity, composition, or style, and what must remain faithful. For mixed illustration and photorealism, state which elements use each treatment. Verify requested preservation against the actual output; prompt wording alone does not establish fidelity.

When handing a concept image to another generation or editing tool, explicitly preserve its style relationships as well as its subjects. Describe how the subject belongs in the environment through palette, texture, scale, contact, and appropriate shadows while retaining intentional mixed styles. Check the integration guidance (external resource; not included) against the output; a multi-tool workflow alone does not guarantee coherence.

## Direct the action through time

When a gesture carries the idea, describe its physical steps, completion condition, and the result that must persist into the next action. Direct performance through observable behavior: a change in gaze, posture, hesitation, delivery, or response to another subject. Name the trigger and allow the reaction time to read. Keep these details in the existing `action_and_performance` and continuity fields; leave incidental movement flexible.

Separate camera setup or behavior (tripod, handheld, stabilized), framing (wide, medium, close), viewpoint (overhead, over-the-shoulder, low), and movement (hold, pan, track) when ambiguity would change the shot. A locked camera can observe a moving subject. For simultaneous actions, specify what moves, its permitted path or region, and what stays still. State necessary occlusion and rendering boundaries explicitly. Use focused prohibitions for a concrete failure; a long negative list is not a substitute for a clear action.

These original miniature examples illustrate the decisions, not tested generation recipes:

- **Repeated action:** In a locked close-up, a baker presses a cutter fully through the dough, lifts it, transfers the freed shape to the tray, then repeats at an untouched patch. The cut-out holes and placed pieces remain visible. The essential result is a completed transfer, not repeated hand movement.
- **Mixed-media movement:** A photographic hand slides a paper tab to the right while a flat ink bird attached to the tab travels along a printed horizontal track. The camera and paper stay fixed; the bird retains its drawn linework and moves only with the tab. The hand releases after the bird reaches the marked endpoint. Paper friction supplies the sound; no score is needed for this example.
- **Reaction and reveal:** A mechanic hears an unexpected ticking, stops tightening a screw, looks toward a closed drawer, and holds before opening it. Cut to the object producing the sound, then return to the reaction. Keep the source hidden until the reveal; carry the ticking across the cut and allow time to recognize the object.

Source: Grace Liu, *A Creative's Guide to Directed AI Film*, supplied PDF, pp. 10–18 (all pages and images inspected 2026-10-12). Its prompts describe intended performance, timing, sound, and constraints; linked films were not reviewed. Keep prompt order adaptable to the task and tool. Model rankings and prices in the guide are dated claims, not defaults.

## Reusable reference packs

When a supplied video controls performance and timing while images replace its cast or setting, use [reference-driven recreation](../../reference-style-video/references/video-recreation.md) to separate those responsibilities and verify the transfer.

For recurring scenes or variants that must share a cast, product, and setting, reuse an inspected reference pack. Build only the views and states the action needs; see still references for video (external resource; not included). Five inputs are a creator's example, not a required pack size or a guaranteed provider capability.

In the existing shot's `references` field, name each file/version, what it controls, the selected view/state, and allowed changes. Resolve overlaps explicitly: a portrait may own facial identity, a body view wardrobe and proportions, and a room image layout; reference lighting need not override the scene's intended lighting. Translate these names into the selected tool's actual input slots only at submission, checking attachment order and supported controls.

Carry the relevant constraints into the action: starting state → physical action → ending state, with continuity into the next shot. A closed/open reference card depicts alternate states of one object, not two objects to place in frame. When a panel is ambiguous or too small, use a clearly selected view rather than adding stronger prompt adjectives. Prompt instructions to preserve text or branding do not prove fidelity; retain the post-production guidance above.

### Worked example: a fictional productivity gadget

Premise: a desk button supposedly clears a founder's schedule; pressing it merely sweeps the paperwork out of view. This is an invented visual joke, not a product demonstration or testimonial.

| Reference | Controls | May change |
|---|---|---|
| Approved founder portrait and body view | Face, hair, blue shirt, body proportions | Expression, pose, scene lighting |
| Button front and side views | One red button, cream base, relative dimensions | Button depressed or released |
| Office wide | Desk/window relationship, desk surface, paper tray | Camera angle and framing |

- **Setup:** medium shot; founder and one button at a crowded desk. Establish the paperwork before the action.
- **Demonstration:** close shot; the finger depresses that button once. End with the button depressed and the papers beginning to move; test this contact and motion before expanding coverage.
- **Payoff:** wide shot; the desk is clear but the paperwork has piled onto the founder's lap. Keep the same founder, desk, and button. The absurd mechanism is intentional; disappearing props or a different room are continuity failures.

Use shot-specific references where supported; do not attach every asset to every shot by habit. For an opening variant, hold the approved pack and later shots constant, change the opening action, and inspect whether the supposedly fixed elements actually held. This supports a controlled creative comparison, not a claim of audience or conversion improvement. Reuse the existing [shot revision loop](shot-list-workflow.md) to repair failures and recheck joins.

Source: Ivanna's [reference-card prompts (2026-09-14)](https://x.com/ivanka_humeniuk/status/2099490874845544900) and [episode animation prompt](https://x.com/ivanka_humeniuk/status/2099490880004473303) illustrate separate character, product, location, and prop responsibilities, including alternate object states. The gadget example and workflow above are our adaptation. The written prompts were inspected; they do not establish Seedance reliability, exact packaging preservation, or measured production savings.

## Worked example: consumer-DV home video

For an ordinary, friend-recorded home-video aesthetic, read [the Seoul DV example](seoul-dv-home-video-example.md). It preserves the source's full 30-second prompt, six timed beats, identity constraints, camera imperfections, and location-only audio. Use it as an adaptable example; its requested resolution and continuity still need output verification.

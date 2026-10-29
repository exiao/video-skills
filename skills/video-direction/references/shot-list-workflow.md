# Shot-list workflow

Keep one canonical production document. When a script exists, preserve its scene sections and add shot records beneath them. Scene text owns dialogue and narration; shots reference scene/line IDs. Use stable shot IDs such as SC01-SH01 and SC01-SH02 for multiple shots within SC01. A direction-only request can use shot IDs without inventing a script. Start with three treatment adjectives, each tied to an observable test for image, movement, or sound. Record a few visual directions with strengths and trade-offs, then lock the chosen direction. For each shot, separate essential details from flexible details so a useful surprise is accepted without losing story, identity, dialogue, framing, or continuity.

After establishing the human concept and visual treatment, specify scene elements (external resource; not included): subject and observable action; environment and spatial relationships; wardrobe, hair, and props. Identify which details carry the story and which may vary. Record them with the shot rather than in a separate scene-elements document.

For major subjects and props, note their purpose when it affects direction: product connection, viewer viewpoint, action, or camera choreography. Choose presentation to serve the scene; no particular pose or viewpoint guarantees relatability.

For a narrative sequence, use the existing `purpose` field to state what viewers understand before the shot, what it adds or changes, and why the next shot follows. Plan order and enough time to read the action or reaction before generating coverage. A story beat may span several shots. Establish, develop, shift, and reveal is one possible progression, not a required four-shot structure. Atmospheric work may sustain a feeling rather than reveal new information; name that intention when it governs the sequence.

When holding a shot, use its existing `purpose` and timing notes to say what viewers are waiting for, what keeps them interested, and when to cut. See Columbo walking to a phone booth and making a call (external resource; not included). Try different lengths and watch the edits if the timing is unclear.

Source: Grace Liu, *A Creative's Guide to Directed AI Film*, supplied PDF, pp. 8–9 (inspected 2026-10-12). Its canoe example shows five images grouped under four beat labels. The stills illustrate shot roles and information order; they do not establish the film's actual timing or playback quality.

Recommended fields:

```text
shot_id, scene_id_if_present, purpose, essential_details, flexible_details,
framing_and_camera, subject, action_and_performance, environment, styling, duration_target,
edit_join, spoken_line_refs, sound_cues, references, continuity_in,
continuity_out, prompt, candidate_takes, selected_take,
measured_duration, edit_range, notes
```

Treat the flow as treatment -> scene changes -> shot list -> references -> generation or capture -> assembly with sound -> review -> targeted revision. Preserve prior cuts and update only failed shot IDs or ranges. A changed duration updates downstream offsets. Distinguish estimated duration from measured take or edit duration. If the planned shots cannot accommodate approved spoken copy, identify the affected scene and propose a timing or copy adjustment; do not silently change the copy. After an authorized revision, update scene timing and dependent shot references together. A deterministic fixture can prove IDs and assembly plumbing, but cannot prove identity, acting, artistic quality, or intelligibility.

## Review the sequence and select takes

When several references must hold together, put their ownership and selected states in the existing `references` field using [reusable reference packs](prompting.md#reusable-reference-packs). Carry state changes through `continuity_in` and `continuity_out`; no separate tracking document is needed.

Plan joins as well as individual shots. Check compatible composition, scale, palette, and motion state. Inspect the edited sequence at playback speed for comprehension and rhythm, then inspect transition frames for discontinuities. Two attractive takes can still make a poor edit.

Select takes that deliver essential action, fidelity, continuity, and payoff within resource constraints. Consciously accept minor variations after inspection; attempt count does not make a broken essential action acceptable. Consider a usable trim or targeted repair before regenerating. Report unmet requirements if resources prevent completion.

For an optional two-shot reveal example, read Into the Toile (external resource; not included). Its exit, print transformation, and camera move are case-specific.

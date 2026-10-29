---
name: animation-explainer
description: Explain a concept intuitively from the bottom up through simple, concrete, step-by-step animations. Use when the user wants to really understand how or why something works through an animated visual explanation. Uses animation-creator with Claude CLI.
---

# Animation explainer

Teach so the learner can predict what happens next and explain why. Interpret “hyper intuitively, bottoms up” as starting with familiar objects and visible actions, then building the mechanism one small step at a time.

Use [animation-creator](../animation-creator/SKILL.md) for animation production and claude-cli (external resource; not included) for implementation. Read both before building. Use **Opus 5.5 through Claude CLI** for animation and UI creation, following that skill's authentication and resume workflow. This skill supplies the teaching brief; animation-creator supplies the production, creative checkpoints, playback, export, and verification workflow.

## Find the smallest thing to understand

Resolve “this” from the supplied material and current conversation. Identify the precise question, the learner's likely starting knowledge, and the observable outcome they should be able to explain. Ask bundled questions with request_user_input_async only when a missing subject or prerequisite materially changes the explanation; otherwise state a reasonable assumption and proceed.

Read the actual source, code, diagram, or reference before explaining it. Verify unfamiliar or changing factual claims against appropriate primary sources. Keep a source note for substantive claims and label illustrative assumptions. If the subject is large, teach the smallest complete mechanism first and connect it back to the larger question.

## Build the understanding from concrete steps

Prepare a short teaching brief before delegating:

- **Destination:** “After this, you can explain why/how ___.”
- **Starting point:** Only the prerequisites the learner needs for this example.
- **Worked example:** A tiny instance with actual objects, values, inputs, and outputs.
- **Steps:** For each step, state what is visible before, the single action or change, what becomes visible after, and why it follows.
- **General rule:** Name the concept or introduce notation after the example makes it meaningful.
- **Transfer check:** Change one input and let the learner predict the result before revealing it.

Start with the thing itself when it is drawable. Use an analogy only when it makes the mechanism easier to see; explicitly map its parts to the real system and identify where the analogy stops working. Never let an analogy substitute for showing the actual mechanism.

Introduce one new idea at a time. Show intermediate states and arithmetic instead of jumping to the final arrangement or answer. Explain necessary prerequisites at the moment they become useful. Define jargon in ordinary language before using it; connect every symbol to a visible quantity. Finish by reconstructing the original question from the pieces just learned.

For example, explain an average by showing three piles of 2, 4, and 6 tokens, moving tokens until each has 4, and only then connecting “same total, shared equally” to (2 + 4 + 6) / 3. The motion demonstrates the operation; a formula fading onto the screen would leave that operation unexplained.

## Make motion carry the explanation

Prefer the simplest representation that exposes the mechanism: dots, blocks, containers, arrows, number lines, small tables, or the actual interface. Keep identity, position, labels, and color meanings stable so the learner can track what changed. Use labels or shapes as well as color.

Animate the causal action itself: move an item, split a group, pass a message, fill a capacity, compare quantities, or trace a dependency. Distinguish logical order from real elapsed time and avoid implying a physical process where the drawing is only a conceptual model. Hold the result long enough to inspect it before the next change. Use brief plain-language captions beside the relevant objects.

Default to a learner-controlled HTML explanation when no format is specified. A single persistent diagram with successive states often makes a small mechanism clearest. Include numbered steps, Back, Next, Replay step, and a short explanation of the current state; add Play/Pause and speed control when continuous playback helps. Let the learner inspect each settled state without a timer. Reduced-motion mode should preserve all information through static steps. Honor requested video or other formats and retain the same teaching progression.

Choose the number of steps from the mechanism. Keep decoration, camera movement, scene changes, and sound only when they improve understanding. For a narrative or multi-scene treatment, follow animation-creator's storyboard and selection requirements; carry an already approved direction forward.

## Give Claude a concrete assignment

Pass Claude the teaching brief, source evidence, both required skill paths, output location, write boundaries, requested format, and definition of done. Require a working animation with the actual example and transitions. Keep the brief focused on the learner's understanding, with freedom to choose the simplest suitable rendering technique.

Have Claude implement and inspect the smallest complete example before expanding it. Review the rendered mechanism yourself and resume the same Claude session with specific corrections. If a step is hard to follow, simplify its objects, split its action, or restore a missing intermediate state before adding styling.

## Verify understanding and delivery

Follow animation-creator's checks for the chosen medium. Additionally:

- Walk through every step in order and backward. Replay must start from the same state; navigating must not leave stale objects, values, or captions.
- Check the worked example independently: quantities, units, causal relationships, intermediate results, and final result must agree with the explanation and sources.
- Inspect actual playback as well as settled states. Confirm that the important action can be followed and the captions have reading time.
- Run the changed-input example against the same rule. Its visible outcome must follow from the mechanism rather than a canned animation.
- Ask whether each step's outcome follows from what the learner has already seen. Repair unexplained leaps. Do not claim learner comprehension without learner feedback.

Deliver the playable artifact and editable source with a brief statement of what it explains and any material simplification. Offer a concise prediction question tied to the example when useful. A prose explanation or storyboard alone does not complete a request for an animation.

# Mechanical explainers and product reveals

Use for a concept explained through a working mechanism, an interactive dissection, or a physical-product reveal. Keep the selected style, stack, sound, and delivery format. This is an optional path within Animation Creator; its existing storyboard selection and playback review still apply.

## Choose what the object explains

For a conceptual explainer, choose a recognizable machine whose actions map to the idea: a queue can become a marble run whose gate releases the next waiting marble. State what moves and what that movement means. Drive motion, numerical readouts, captions, and accessible descriptions from the same behavior model. Keep the metaphor's limits explicit where its mechanics differ from the real system.

For a real product, identify the model or variant and research the dimensions, visible features, materials, moving controls, and any internals shown. Prefer manufacturer specifications and documented teardowns. A single photo can establish appearance but cannot establish hidden construction or absolute scale by itself. Record verified facts, estimates, and illustrative internals separately in the existing brief. Choose the feature worth demonstrating before adding small details.

## Build one object for the requested outputs

Organize geometry into named parts and assemblies with stable rest transforms. Give moving groups their actual hinge axes, pivots, or slide directions, and give important details local camera-target anchors. Where both a viewer and a film are requested, share geometry, feature state, and assembly motion; let input or the timeline drive that state. Avoid constructing a second object solely for the video.

Use documented real units for a faithful product model, or consistent declared units for an illustrative machine. Establish silhouette and proportions early, then render one working feature and a short disassembly/reassembly sample before expanding detail.

For an exploded view, plan the exit order and swept clearance. Outer panels may need to lead before inner components can leave; a hinge needs clearance throughout its arc. Build a housing with a cavity when parts must emerge from it. Derive the assembled pose from the stored rest transforms so reassembly returns to the same structure without accumulated drift.

The linked Anatomy kit uses convex solids and separating-plane ordering for projected SVG geometry. Those constraints belong to that renderer. Inspect its current template and audit tools if choosing it; an existing mesh renderer or native 3D project can use its own geometry and depth handling.

## Choreograph discovery

A useful product-reveal option is:

| Beat | Purpose |
| --- | --- |
| Establish the silhouette | Make the object recognizable |
| Inspect selected details | Show meaningful construction or identity |
| Demonstrate a feature | Let the viewer see what the object does |
| Separate assemblies | Reveal relationships and hidden structure |
| Reassemble and settle | Resolve the action into a readable hero view |

Adapt or remove beats to serve the subject. A demonstration should show a real action and result, rather than only orbiting decorative geometry. For macro shots, target a point in the object's local coordinates and project it through the current pose so the feature stays framed during rotation. Inspect candidate angles in renders before committing to them.

When changing duration, treat transition, demonstration, and reading time separately. Preserve a brief transition when its speed is essential, adjust holds within readable limits, and add or remove meaningful detail or feature beats for larger duration changes. Retiming should update sound and review cues through the shared timeline. Initialize animated channels at the start so a later feature pose does not leak into the opening; keep rotation values continuous through full turns. Use the existing seek/render contract and [adaptive sampling guidance](motion-craft.md#aspect-ratios-and-export-finish) when needed.

## Review the mechanism and assembly

Inspect assembled, intermediate, and fully separated states from the film's chosen view and several other revealing angles. Check intersections, occlusion order, clipped parts, feature clearance, and whether the separated arrangement remains understandable. Review the moving intervals in playback; clean endpoint stills do not establish clean travel. Use renderer audits where available and inspect any flagged frames rather than treating a clean audit as visual proof.

Check that controls, computed readouts, and the depicted mechanism agree. Confirm reassembly returns every part to its intended pose. Reframe and review each requested aspect ratio with both assembled and exploded bounds. Deliver only the requested outputs and identify any remaining approximations.

## Sources and limits

- [Ryan's Anatomy](https://skills.wheresryan.sh/anatomy): working mechanical metaphors and shared behavior/readout models.
- [Anatomy Reveal source](https://github.com/annnguyentt/anatomy-reveal-skill): an optional object/viewer/film template; see its [geometry guidance](https://github.com/annnguyentt/anatomy-reveal-skill/blob/main/references/object.md) and [shot/timeline recipes](https://github.com/annnguyentt/anatomy-reveal-skill/blob/main/references/shots.md).
- [Reference post](https://x.com/renproton/status/2111857166030418376) and [TypingMind listing](https://www.typingmind.com/skills/annnguyentt-anatomy-reveal).

Sources reviewed October 19–21, 2026; their bundled renderer and performance claims have not been independently reproduced. Read and trial scripts before adopting them. Paper styling, minimum part counts, geometry-only assets, perpetual drift, fixed whips, silence, duration, and model recommendations are source-specific choices. Apply only what the user's brief calls for; the source template does not replace the existing production workflow.

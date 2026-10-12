---
name: game-app-ui-image2
description: "Create game and app UI mockups or raster UI assets with ChatGPT Images 2 through Codex's built-in image_gen tool. Use for exploratory raster UI work; do not use for deterministic production UI layout or vector icon systems."
---

# Game & App UI Image2

Turn a product or game UI request into a visually coherent raster mockup or image asset with ChatGPT Images 2, using Codex's built-in `image_gen` tool. This is a Codex-only image-generation skill: do not substitute another generator, a mockup made in HTML/CSS, or a text-only prompt when the tool is unavailable. Treat generated screens as a design reference unless the user explicitly asks to ship them as project assets.

## Choose the right deliverable

- Use ChatGPT Images 2 for a screen concept, art-directed mockup, HUD visual direction, menu background, illustrated panel, texture, emblem, or other bitmap asset.
- Use native UI code, SVG, or the project's established components for responsive layouts, interactive controls, icons, and final localized text. Do not replace a production UI system with a screenshot.
- When the request needs both, generate the visual direction first, then translate the approved composition into native components only when requested.

## Gather only the inputs that affect the result

Infer missing, low-risk details from the product context. Ask only when a missing decision would substantially change the design. The useful inputs are:

- target: game or app; genre/domain; device, orientation, and target resolution
- screen purpose, primary user action, and required information hierarchy
- art direction: references, mood, palette, era, materials, accessibility constraints
- UI states to show: for example normal, selected, disabled, error, combat, or paused
- whether the result is a presentation mockup, implementation reference, or a project-bound image asset

If the user supplies exact copy, preserve it verbatim in the prompt, but warn that image-rendered text needs visual verification. Prefer short placeholder copy in exploratory mockups when exact wording is not material.

## Create the prompt

Use the `ui-mockup` image taxonomy and write a compact, screen-first specification. State the viewport, screen type, hierarchy, and visual direction before decorative detail. Include a direct constraint that the result must be an original, frame-free UI composition.

Use this shape when helpful:

```text
Use case: ui-mockup
Asset type: <design-review mockup | project image asset>
Primary request: <screen and primary task>
Platform and viewport: <e.g., PC 16:9, portrait mobile>
Information hierarchy: <primary / secondary / tertiary>
States shown: <normal, selected, disabled, etc.>
Style/medium: <visual language and materials>
Color palette: <palette and contrast intention>
Composition: <safe areas, focal point, spacing>
Text (verbatim): "<only essential text>"
Constraints: original UI; no device frame; readable grouping; no watermark; <user constraints>
Avoid: copied brand UI, tiny illegible text, clutter, unnecessary icons
```

For game HUDs, specify gameplay-safe areas, player focus, and diegetic/non-diegetic intent. For app screens, specify the principal task and error/empty/loading state when it matters. Read [prompt recipes](references/prompt-recipes.md) for reusable screen-specific scaffolds.

## Generate, inspect, and iterate

1. Confirm that the built-in `image_gen` tool is available. If it is unavailable, stop and say that this skill requires Codex with ChatGPT Images 2; do not fall back to an API, CLI script, or another image model.
2. Generate one screen or one asset per prompt with `image_gen`. For a flow, create screens individually so each has a focused hierarchy.
3. Inspect the output against the requested viewport, hierarchy, visual consistency, text, contrast, safe areas, and prohibited elements.
4. Iterate only on the identified defect. Keep all approved elements explicitly unchanged in an edit prompt.
5. For project-bound output, save the selected final artifact in the project and report its path. Never overwrite an existing asset without explicit instruction.

For local edit targets, inspect the image with `view_image` before sending it to `image_gen`, so the target is available in the conversation. For transparent UI assets, explicitly require a transparent background and preserve alpha.

Do not claim that an image mockup is production-ready or accessible without implementing and testing the corresponding UI. When a generated image is the reference for implementation, identify the reusable tokens and components it implies: color roles, typography scale, spacing rhythm, panel treatments, and named control states. Always report that ChatGPT Images 2 via the built-in `image_gen` tool was used.

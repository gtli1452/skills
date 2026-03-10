---
name: canvas-design
description: Create static design artifacts as polished PNG, PDF, SVG, or HTML-first visuals with strong art direction.
---

# Canvas Design

## Use when
- The user wants a poster, cover, one-pager, social graphic, visual study, or other static design artifact.
- The work should feel art-directed and original rather than like a generic layout.
- The output can be produced as PNG, PDF, SVG, or another local file-first format.

## Do not use when
- The deliverable needs to be a live application or interactive UI; use `frontend-design`.
- The task is primarily generative or animated; use `algorithmic-art` or `slack-gif-creator`.
- The user wants a reusable brand system rather than a specific visual piece.

## Capability checks and fallbacks
1. Check the most dependable render format in the environment.
   - Prefer SVG or HTML/CSS when deterministic layout matters most.
   - Prefer PNG or PDF exports when the user needs a final handoff asset.
2. Check what rendering tools are actually available.
   - If image libraries or PDF toolchains exist, use them.
   - If not, build in SVG or HTML first and export later.
3. Check font availability before committing to typography.
   - Start with the bundled local fonts in `canvas-fonts\`.
   - If a chosen font cannot be embedded cleanly, switch early to a nearby fallback.
4. If the request references copyrighted media, create an original interpretation rather than a close replica.

## Default workflow
1. Distill the brief into audience, tone, format, dimensions, and the subtle concept worth encoding.
2. Write a short visual philosophy or direction note so the piece has a clear point of view before execution.
3. Choose canvas size, grid logic, and material language: typography, color, spacing, image treatment, and texture.
4. Inspect the bundled fonts and pick combinations that support the concept instead of defaulting to generic system choices.
5. Build the composition in a deterministic source format such as SVG, HTML/CSS, or a scriptable drawing pipeline.
6. Export the requested asset and do a second refinement pass focused on spacing, hierarchy, and restraint.
7. Validate that nothing clips, overlaps, or falls outside the canvas.

## Resource map
- `canvas-fonts\`: bundled local fonts and licenses that can be used for posters, covers, and other static compositions.

## Output contract
Return or create:
- a short design note or `philosophy.md` when the concept matters,
- the source artifact (`.svg`, `.html`, script, or equivalent) when practical,
- the requested export (`.png`, `.pdf`, or both),
- a short note about font choices, assumptions, or manual export steps if any remain.

## Validation checklist
- The composition is original and not a traced copy of someone else's work.
- Text, marks, and imagery stay inside the canvas with proper breathing room.
- Typography and palette choices feel intentional and consistent.
- The output format is appropriate for the delivery channel.
- A second-pass polish was done to remove crowding, imbalance, and obvious filler elements.

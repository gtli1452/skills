---
name: algorithmic-art
description: Build original generative art as local, reproducible HTML or JS sketches with seeded controls.
---

# Algorithmic Art

## Use when
- The user wants generative art, creative coding, parametric visuals, particle systems, or algorithmic posters.
- The deliverable should be original, reproducible, and explorable rather than hand-drawn or copied.
- A local browser artifact, scriptable SVG, or code-driven canvas is acceptable.

## Do not use when
- The request is to imitate a living artist or closely copy a copyrighted work.
- The task is a production UI build rather than a self-contained artwork.
- The user needs a static brand system or theme pack instead of a generative piece.

## Capability checks and fallbacks
1. Confirm the most reliable output format for the repo and environment.
   - Default: a single local `index.html` or `viewer.html` that opens in a browser.
   - If the repo prefers split assets, use `index.html` plus local JS and CSS files.
2. Check whether p5.js is already vendored or can be loaded.
   - If yes, p5 is fine.
   - If no, switch to the Canvas API or SVG so the piece still works offline.
3. Check whether fonts, textures, or palettes are needed.
   - Prefer local assets that can ship with the sketch.
   - If none are available, generate the look procedurally and keep dependencies minimal.
4. If browser preview is unavailable, still create deterministic files and include a short note explaining how to open them.

## Default workflow
1. Distill the request into a creative brief: mood, motion, medium, constraints, and any subtle conceptual thread.
2. Write a short design note or `philosophy.md` that names the movement and explains the system's rules.
3. Pick the execution format:
   - single-file HTML for portability,
   - split HTML/JS/CSS for maintainability,
   - SVG or Canvas when offline execution matters more than library choice.
4. Define a seeded parameter model before drawing:
   - seed,
   - scale or density,
   - motion or drift,
   - palette or contrast,
   - one or two piece-specific controls.
5. Build the sketch so the philosophy shows up in the process, not just the final frame.
6. Add basic controls when they help exploration:
   - seed navigation or randomize,
   - regenerate,
   - reset,
   - export PNG if the runtime supports it.
7. Validate reproducibility, performance, and legibility across several seeds.

## Resource map
- `templates\viewer.html`: optional local-browser starter with a neutral layout, seed controls, and a working sample sketch. Restyle or replace it freely.
- `templates\generator_template.js`: reference patterns for seeded randomness, parameter wiring, regeneration, and export hooks.

## Output contract
Return or create:
- a short philosophy or design note (`philosophy.md` or equivalent),
- the runnable sketch (`index.html`, `viewer.html`, or split source files),
- any local assets required to run it,
- a short note telling the user how to open and explore it if the controls are non-obvious.

## Validation checklist
- The work is original and not a style-clone of a protected artist.
- The same seed produces the same output.
- Controls map cleanly to visual behavior.
- The piece works as a local browser or static artifact, or the fallback path is documented.
- The final composition looks intentional across multiple seeds rather than like uncontrolled noise.

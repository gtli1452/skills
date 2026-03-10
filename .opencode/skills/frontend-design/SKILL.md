---
name: frontend-design
description: Build distinctive frontend interfaces with strong design direction and production-ready code.
---

# Frontend Design

## Use when
- The user wants a page, component, dashboard, landing page, design system surface, or other frontend interface.
- The code should be both functional and visually memorable.
- The repo already has a frontend stack, or a small standalone frontend can be created responsibly.

## Do not use when
- The user only needs a theme pack or brand guide without implementation.
- The task is a static poster or art print rather than an interface.
- The deliverable is an animated GIF or generative art sketch rather than product UI.

## Capability checks and fallbacks
1. Inspect the repo before choosing an implementation path.
   - If a framework already exists, stay inside that stack.
   - If not, default to the smallest maintainable HTML/CSS/JS solution that matches the request.
2. Check whether the request requires motion, accessibility, responsiveness, or design-token integration.
   - Use existing libraries when the repo already depends on them.
   - If not, prefer CSS-first motion and simple primitives over adding brittle dependencies.
3. Check asset availability.
   - Use existing local assets first.
   - If assets are missing, design with shapes, gradients, typography, and reusable tokens rather than blocking on mock content.
4. Run the repo's existing build, test, or lint commands when they exist.

## Default workflow
1. Understand the interface's audience, task flow, tone, and technical constraints.
2. Pick a clear aesthetic direction instead of drifting into generic defaults.
3. Define a small token set for color, typography, spacing, radius, and motion before building the UI.
4. Implement the working code in the repo's native patterns.
5. Refine states and hierarchy: empty, loading, hover, focus, mobile, and dense content cases.
6. Validate responsiveness, contrast, keyboard behavior, and build/test status.

## Resource map
- No bundled assets are required. Start with the existing codebase, then create only the files the target stack actually needs.

## Output contract
Return or create:
- the working frontend code,
- a short note on the design direction and major decisions,
- any follow-up instructions required to run or review the UI locally.

## Validation checklist
- The result fits the existing stack and passes the repo's normal checks when available.
- The layout works across expected screen sizes.
- Visual choices feel deliberate rather than template-generic.
- Interactive states are covered.
- Accessibility basics are not broken by the design treatment.

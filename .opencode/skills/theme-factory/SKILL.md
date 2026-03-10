---
name: theme-factory
description: Apply or generate coherent theme packs for slides, docs, HTML, and other design artifacts.
---

# Theme Factory

## Use when
- The user wants a fast, coherent theme for a deck, report, landing page, dashboard, or other artifact.
- A prebuilt palette and font pairing would speed up styling decisions.
- The job is to apply or adapt a theme, not to define a full corporate brand system from scratch.

## Do not use when
- The user needs a true brand pack with voice, rules, and governance; use `brand-guidelines`.
- The task is to build the interface itself rather than choose its visual system.
- The task is a one-off art poster where a reusable theme is not the point.

## Capability checks and fallbacks
1. Check the target medium and editable surface.
   - Slides, docs, HTML, and dashboards all need the same theme translated differently.
   - If direct editing is hard, still deliver tokens and mapping notes.
2. Check whether the user already chose a theme.
   - If yes, apply it.
   - If not, shortlist a few candidates and proceed with the best default for the audience and tone.
3. Check font availability before locking the final application.
   - Keep the intended hierarchy even if a fallback font must be substituted.
4. If none of the bundled themes fit, create a custom theme that matches the same level of specificity as the provided theme files.

## Default workflow
1. Read the artifact or brief and identify audience, tone, contrast needs, and delivery channel.
2. Inspect the bundled theme files or generate a custom theme when nothing fits.
3. Convert the chosen theme into implementation-friendly tokens: colors, typography, spacing cues, and component emphasis.
4. Apply the theme consistently across the target artifact.
5. Validate readability, contrast, and visual consistency after application.

## Resource map
- `theme-showcase.pdf`: optional visual preview of the bundled themes.
- `themes\*.md`: individual theme specs with colors, fonts, and best-use notes.

## Output contract
Return or create:
- the selected or generated theme,
- the applied artifact or a clear token mapping for the artifact,
- a short note about any fallbacks, substitutions, or customizations.

## Validation checklist
- The theme matches the audience and medium.
- Colors have enough contrast for the intended use.
- Font substitutions preserve the original hierarchy if exact fonts are unavailable.
- The styling is applied consistently instead of as isolated spot fixes.
- A custom theme, if created, is concrete enough for someone else to reuse.

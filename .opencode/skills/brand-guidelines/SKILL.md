---
name: brand-guidelines
description: Create or extract reusable brand packs with palette, type, voice, tokens, and usage rules.
---

# Brand Guidelines

## Use when
- The user needs a brand pack, style guide, design tokens, or a reusable visual system.
- Existing brand material must be extracted into a cleaner, more actionable reference.
- A team needs palette, typography, spacing, imagery, and voice rules that can be applied across docs, UI, slides, or marketing assets.

## Do not use when
- The task is only to theme one artifact; use `theme-factory` for that.
- The task is to build the implementation itself; use `frontend-design` for UI work.
- The user needs a single illustration or poster rather than a repeatable brand system.

## Capability checks and fallbacks
1. Inventory available inputs first.
   - Ideal inputs: existing site, deck, logo, screenshots, tokens, copy samples, or a short brand brief.
   - If only partial inputs exist, extract what is real and clearly label assumptions.
2. Check whether the user wants extraction or invention.
   - Extraction: document what already exists and normalize it.
   - Invention: create a starter brand pack and say it is a proposed system, not an official standard.
3. If there is no design-token format in the repo, default to a readable markdown pack plus a small JSON token file.
4. If logo files or font licenses are unavailable, document recommended usage and fallbacks rather than inventing assets that cannot be delivered honestly.

## Default workflow
1. Gather inputs and identify the brand's audience, market position, and personality.
2. Distill the core system:
   - promise or essence,
   - tone keywords,
   - audience cues,
   - visual constraints.
3. Build the practical brand pack:
   - color roles,
   - typography pairings and fallbacks,
   - spacing and shape language,
   - imagery and icon direction,
   - voice and copy guidance,
   - do and do-not examples.
4. Convert the pack into implementation-friendly tokens when useful.
5. If asked to apply the brand immediately, map the system into the target medium after the pack is coherent.

## Resource map
- `templates\brand-pack-template.md`: reusable outline for a markdown brand pack.
- `templates\brand-tokens.json`: starter token structure for colors, typography, spacing, and voice cues.

## Output contract
Return or create:
- a brand pack (`brand-pack.md` or equivalent),
- structured tokens (`brand-tokens.json`, CSS variables, or similar) when helpful,
- a short note describing assumptions, missing inputs, or areas that still need stakeholder review.

## Validation checklist
- The pack can be used by someone who was not in the original conversation.
- Colors have clear roles, not just a list of swatches.
- Typography choices include realistic fallbacks.
- Voice guidance is concrete enough to steer copy decisions.
- Any inferred decisions are clearly marked as proposed rather than official.

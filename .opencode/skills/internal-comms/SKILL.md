---
name: internal-comms
description: Draft concise internal updates, FAQs, newsletters, and status messages from local source material.
---

# Internal Comms

## Use when
- The user needs an internal status update, FAQ, newsletter, leadership note, incident update, or other employee-facing communication.
- The content should be grounded in real source material such as notes, docs, tickets, or pasted updates.
- The output needs to be concise, readable, and easy to circulate asynchronously.

## Do not use when
- The task is a long-form proposal or specification; use `doc-coauthoring`.
- The audience is external press, customers, or marketing channels.
- The request is mostly visual styling rather than writing.

## Capability checks and fallbacks
1. Identify the audience, time window, and channel before drafting.
   - A weekly team update and a company-wide note should not sound the same.
2. Check what source material exists.
   - If official notes or documents exist, use them as the factual backbone.
   - If context is incomplete, draft carefully and label assumptions or missing facts.
3. Pick the closest reference format from `examples\`.
   - Use the exact format when one clearly fits.
   - Default to `examples\general-comms.md` when the request is unusual.
4. If links, owners, or dates are unknown, use placeholders or explicit follow-up notes rather than inventing details.

## Default workflow
1. Gather the audience, purpose, channel, timing, and call to action.
2. Pull the key facts from the available material and group them by importance.
3. Choose the closest format reference from `examples\`.
4. Draft the message so the most important information lands first.
5. Tighten for brevity, clarity, and confidence without overstating unknowns.
6. Validate every claim against the available source material before finalizing.

## Resource map
- `examples\3p-updates.md`: compact progress, plans, problems format.
- `examples\company-newsletter.md`: company-wide roundup structure.
- `examples\faq-answers.md`: recurring-question format.
- `examples\general-comms.md`: fallback structure for other internal announcements.

## Output contract
Return or create:
- the final communication draft,
- a short note on any placeholders, missing facts, or suggested follow-up links,
- alternate subject line or heading options when the channel needs them.

## Validation checklist
- The audience and call to action are obvious.
- The message is sourced, concise, and not padded with generic filler.
- Facts, dates, and metrics are either verified or clearly marked as tentative.
- The format matches the communication type.
- Someone skimming quickly can still understand the main point.

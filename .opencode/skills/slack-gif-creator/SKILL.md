---
name: slack-gif-creator
description: Create Slack-ready GIFs with Python utilities, validators, and size-aware animation workflows.
---

# Slack GIF Creator

## Use when
- The user wants an animated GIF for Slack emoji, reactions, announcements, or chat messages.
- The output needs to respect Slack-friendly dimensions, file size constraints, and looping behavior.
- A Python + PIL workflow is acceptable.

## Do not use when
- The user only needs a static illustration or poster.
- The target is a web animation or video rather than a GIF.
- The request depends on emoji fonts or packaged assets that are not actually available.

## Capability checks and fallbacks
1. Verify the target form factor first.
   - Emoji-style GIFs usually want small square dimensions.
   - Message GIFs can be larger but still need disciplined file size control.
2. Check whether Python and the packages in `requirements.txt` are available.
   - If they are, use the bundled utilities directly.
   - If not, install only what is needed in the active environment or fall back to a simpler scripted render plan.
3. Check whether the animation depends on user-provided imagery.
   - If yes, load and process the asset locally with PIL.
   - If not, draw original graphics from primitives rather than assuming hidden assets exist.
4. If the GIF is too heavy, reduce dimensions, frames, colors, or duration before redesigning the concept entirely.

## Default workflow
1. Choose the target size, duration, and loop style based on the Slack use case.
2. Sketch the motion in a few key beats before writing frame code.
3. Build frames with PIL and the utilities in `core\`.
4. Save with Slack-aware optimization settings.
5. Run validation and iterate on the smallest set of changes needed to hit the constraints.
6. Deliver the GIF plus the source script when the user may want revisions later.

## Resource map
- `requirements.txt`: Python dependencies for rendering and optimization.
- `core\gif_builder.py`: frame assembly and save helpers.
- `core\validators.py`: Slack-readiness checks.
- `core\easing.py`: easing helpers for better motion.
- `core\frame_composer.py`: convenience drawing helpers.

## Output contract
Return or create:
- the final `.gif`,
- the source script used to generate it when practical,
- a short validation summary covering size, dimensions, duration, and any compromises.

## Validation checklist
- The GIF matches the intended Slack use case.
- The animation loops cleanly and reads quickly.
- File size and dimensions are under control.
- Graphics look intentional and polished, not like placeholder primitives.
- Validation was run or the remaining risk is stated clearly.

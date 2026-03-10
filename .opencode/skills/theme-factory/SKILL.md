---
name: theme-factory
description: Toolkit for styling decks, docs, web pages, reports, and other deliverables with reusable themes. It provides 10 preset themes with colors and font pairings that can be applied directly or translated into local design tokens.
license: Complete terms in LICENSE.txt
---

# Theme Factory Skill

This skill provides a curated collection of professional themes, each with carefully selected color palettes and font pairings. Once a theme is chosen, it can be applied as a reusable visual system across slides, documents, HTML/CSS, React apps, PDFs, or other local deliverables.

## Purpose

Use this skill when a task needs cohesive styling but does not already have a strong visual system. Each theme includes:
- A cohesive color palette with hex codes
- Complementary font pairings for headers and body text
- A distinct visual identity suitable for different contexts and audiences
- Enough structure to convert the theme into CSS variables, JSON design tokens, or slide/document styles

## Workflow

1. **Identify the output target**
   - Slides, docs, reports, HTML pages, React components, dashboards, PDFs, or mixed deliverables

2. **Choose a theme source**
   - If the user names a theme, load it directly from `themes/`
   - If not, read a few theme files and recommend the best fit based on the content and tone
   - `theme-showcase.pdf` is optional reference material, not a required interaction step

3. **Translate the theme into reusable tokens**
   - Map colors into background, surface, text, muted, accent, and border roles
   - Map fonts into heading, body, and optional monospace roles
   - Preserve contrast, hierarchy, and readability

4. **Apply the theme consistently**
   - Use the same palette and font logic throughout the deliverable
   - Keep charts, tables, callouts, and buttons aligned with the theme
   - When the user is not available for a choice, pick the strongest-fit theme and state the decision clearly

## Themes Available

The following 10 preset themes are defined in the `themes/` directory:

1. **Ocean Depths** - Professional and calming maritime theme
2. **Sunset Boulevard** - Warm and vibrant sunset colors
3. **Forest Canopy** - Natural and grounded earth tones
4. **Modern Minimalist** - Clean and contemporary grayscale
5. **Golden Hour** - Rich and warm autumnal palette
6. **Arctic Frost** - Cool and crisp winter-inspired theme
7. **Desert Rose** - Soft and sophisticated dusty tones
8. **Tech Innovation** - Bold and modern tech aesthetic
9. **Botanical Garden** - Fresh and organic garden colors
10. **Midnight Galaxy** - Dramatic and cosmic deep tones

## Token Application Guidelines

When applying a chosen theme, translate it into roles such as:

```css
:root {
  --theme-bg: #ffffff;
  --theme-surface: #f5f5f5;
  --theme-text: #171717;
  --theme-muted: #6b7280;
  --theme-accent: #2563eb;
  --theme-border: #d1d5db;
  --font-heading: "Your Header Font", sans-serif;
  --font-body: "Your Body Font", sans-serif;
}
```

Use the same theme roles whether you are styling HTML, React components, slides, or documents.

## Application Process

After a theme is selected or inferred:
1. Read the corresponding theme file from `themes/`
2. Convert the palette and font pairing into the target format
3. Apply the tokens consistently throughout the deliverable
4. Ensure proper contrast and readability
5. Keep the chosen theme's visual identity intact across all screens or pages

## Preview Options

If the user needs a preview before full application, choose the lightest useful method:
- Summarize 2-3 candidate themes in text
- Create a quick local swatch sheet in HTML or markdown
- Reference `theme-showcase.pdf` if a visual comparison is helpful

Do not depend on the PDF showcase alone when a text summary or token preview would be faster.

## Create Your Own Theme

If none of the existing themes fit, create a custom theme. Based on the request, generate:
- A theme name
- A compact color palette with clearly defined roles
- Heading/body font pairings
- A short explanation of what the theme is trying to express
- Reusable tokens or style variables that can be applied immediately

After generating the custom theme, show a compact preview in text, HTML, or token form, then apply it consistently to the final deliverable.

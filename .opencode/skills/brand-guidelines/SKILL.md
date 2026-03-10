---
name: brand-guidelines
description: Applies a project's brand system to decks, docs, interfaces, and other visual deliverables. Use it when brand colors, typography, visual formatting, or design standards matter; if none exist, fall back to a clean OpenCode-style public-site aesthetic.
license: Complete terms in LICENSE.txt
---

# Project Brand Styling

## Overview

Use this skill when work should align with an existing brand system or visual identity. Start with explicit brand guidance from the user, then inspect any local source material such as logos, screenshots, CSS variables, slide templates, theme files, or marketing assets.

**Keywords**: branding, corporate identity, visual identity, brand colors, typography, design tokens, visual formatting, style guide, brand system

## Default Workflow

1. **Look for an existing brand system first**
   - User-provided brand guides, logos, screenshots, or copy
   - Local CSS variables, Tailwind config, theme files, slide masters, or design tokens
   - Repeated colors, typography, spacing, iconography, and UI patterns in adjacent assets

2. **Extract the brand primitives**
   - Primary/background/text colors
   - Accent and status colors
   - Heading, body, and monospace font stacks
   - Spacing, radius, border, icon, and image-treatment rules

3. **Translate the brand into reusable tokens**
   - Prefer named tokens over hard-coded values
   - Keep hierarchy, contrast, and whitespace consistent
   - Apply the same system across docs, slides, HTML/CSS, React, PDF, or PNG outputs

4. **If no brand system exists, use the fallback**
   - A clean, modern, documentation-friendly aesthetic inspired by OpenCode's public-facing site and docs
   - Neutral surfaces, strong text contrast, restrained accent color, generous whitespace, and subtle developer-tool polish
   - Sans-serif UI text with monospace reserved for code, labels, or metadata

## Fallback Brand System

### Colors
- Background: `#f7f7f3`
- Surface: `#ffffff`
- Primary text: `#171717`
- Secondary text: `#5f6368`
- Border/subtle UI: `#d9dde3`
- Accent: `#2563eb`
- Accent alternative: `#0f766e`

### Typography
- **Headings and UI**: `system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`
- **Body**: the same sans stack, unless the project already has a stronger editorial body face
- **Code and metadata**: `"SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace`

## Application Guidelines

### Typography Hierarchy
- Use semibold or bold headings with tight spacing
- Keep body copy readable with `1.4-1.6` line-height
- Reserve monospace for code, tabs, labels, metrics, or metadata

### Color Usage
- Use one dominant accent color and at most one supporting accent
- Keep backgrounds calm and legible
- Ensure accessible contrast for interactive states, charts, and callouts

### Layout and Components
- Favor consistent spacing, modest radius values, clear borders, and restrained shadow use
- Let branding come through palette, type, tone, and rhythm rather than decorative excess
- Prefer project assets or system fonts before fetching new ones

## Technical Details

### Tokenization
When applying a brand to HTML or React, map it into reusable variables such as:

```css
:root {
  --brand-bg: #f7f7f3;
  --brand-surface: #ffffff;
  --brand-fg: #171717;
  --brand-muted: #5f6368;
  --brand-accent: #2563eb;
  --brand-border: #d9dde3;
}
```

### Deliverable Strategy
- In web UI, use CSS variables or theme tokens
- In slide decks or documents, reuse the same palette for headings, dividers, charts, and emphasis
- If an existing brand conflicts with the fallback, preserve the real brand rather than forcing the fallback

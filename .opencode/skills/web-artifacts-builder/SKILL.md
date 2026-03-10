---
name: web-artifacts-builder
description: Suite of tools for creating elaborate, multi-component local web apps using modern frontend web technologies (React, Tailwind CSS, shadcn/ui). Use it for complex web UIs requiring state management, routing, or shadcn/ui components - not for simple single-file HTML/JSX pages.
license: Complete terms in LICENSE.txt
---

# Web App Builder

To build substantial local web apps in OpenCode, follow these steps:
1. Initialize the frontend repo using `scripts/init-web-app.sh`
2. Develop the app by editing the generated code
3. Preview locally with `pnpm dev`
4. (Optional) Bundle the app into a single self-contained HTML file using `scripts/bundle-web-app.sh`
5. (Optional) Test the app or bundle

**Stack**: React 18 + TypeScript + Vite + Parcel (single-file bundling) + Tailwind CSS + shadcn/ui

## Design & Style Guidelines

VERY IMPORTANT: To avoid what is often referred to as "AI slop", avoid using excessive centered layouts, purple gradients, uniform rounded corners, and Inter font.

## Quick Start

### Step 1: Initialize Project

Run the initialization script to create a new React project:
```bash
bash scripts/init-web-app.sh <project-name>
cd <project-name>
```

This creates a fully configured project with:
- ✅ React + TypeScript (via Vite)
- ✅ Tailwind CSS 3.4.1 with shadcn/ui theming system
- ✅ Path aliases (`@/`) configured
- ✅ 40+ shadcn/ui components pre-installed
- ✅ All Radix UI dependencies included
- ✅ Parcel configured for single-file bundling (via `.parcelrc`)
- ✅ Node 18+ compatibility (auto-detects and pins the appropriate Vite version)

### Step 2: Develop the App

Edit the generated files to build the requested interface. For many requests, `src/App.tsx`, `src/index.css`, and a small component tree are enough. For larger requests, create routes, state management, and additional components as needed.

### Step 3: Preview Locally

Start the dev server while implementing:
```bash
pnpm dev
```

Use the Vite preview loop as the default OpenCode workflow. This is the fastest way to inspect and iterate on the app before worrying about single-file export.

### Step 4: Bundle to a Single HTML File (Optional)

If a portable one-file deliverable is useful, run:
```bash
bash scripts/bundle-web-app.sh
```

This creates `bundle.html` - a self-contained local HTML deliverable with all JavaScript, CSS, and dependencies inlined. Open it directly in a browser or hand it off as a portable build.

**Requirements**: Your project must have an `index.html` in the root directory.

**What the script does**:
- Installs bundling dependencies into the local project
- Creates `.parcelrc` with path-alias support
- Builds with Parcel (no source maps)
- Inlines assets into `bundle.html`

### Step 5: Testing or Visualizing (Optional)

Use available tools (including `webapp-testing`) after the first working version exists. In general, avoid heavyweight testing up front unless the user requested it or you suspect a bug.

## Local Delivery Guidance

- Default to the multi-file Vite project during development
- Use `bundle.html` when a single-file handoff is useful
- For larger apps or routed interfaces, provide both the source project and any bundled export
- Include the minimum commands needed to preview locally (`pnpm install`, `pnpm dev`, `pnpm build`)

## Reference

- **shadcn/ui components**: https://ui.shadcn.com/docs/components

---
name: web-artifacts-builder
description: Build rich local web deliverables—standalone HTML, static bundles, or small React apps—with Windows-friendly scaffolding and bundling scripts for demos, dashboards, microsites, and interactive prototypes.
license: See LICENSE.txt
---

# Static Web Bundle Builder

This OpenCode adaptation keeps the original frontend stack, but targets outputs that run in a local browser or any static hosting environment instead of chat-client-specific artifacts.

## Use when
- The deliverable should be an interactive browser experience.
- The task needs React, TypeScript, Tailwind, shadcn/ui, or more than a single hand-written HTML file.
- You want either a self-contained `bundle.html` or a deployable static `dist\` folder.

## Do not use when
- A single static HTML file is enough.
- The task is backend-only or not primarily a browser deliverable.
- The repo already has its own production frontend build system and you only need a small patch inside it.

## Capability checks and fallbacks
- If Node.js 18+ and a package manager are available, use the bundled PowerShell scripts in `scripts\`.
- Prefer `pnpm`; the scripts automatically fall back to `npm`.
- If bundling dependencies cannot be installed, still deliver a normal static `dist\` build or a simpler single-file HTML/CSS/JS prototype.
- If `tar` is unavailable or extracting bundled shadcn components fails, continue with Tailwind plus custom components.
- If browser automation is unavailable, still produce the output and give the file path or dev-server URL for manual review.

## Default workflow
1. Decide whether the job needs a React app or a simpler static page.
2. For richer work, scaffold with `scripts\init-static-web.ps1 <project-name>`.
3. Implement the UI, keeping assets local and browser-safe.
4. Run the app's existing build or dev commands to confirm it works.
5. Produce either `dist\` or a single `bundle.html` via `scripts\bundle-static-web.ps1`.
6. If needed, test the result with the `webapp-testing` skill.

## Resource map
- `scripts\init-static-web.ps1` — React/Vite/Tailwind/shadcn bootstrap.
- `scripts\bundle-static-web.ps1` — build + inline a standalone HTML bundle.
- `scripts\shadcn-components.tar.gz` — bundled UI component set carried over from the source skill.

## Output contract
- Deliver a runnable project plus either a `bundle.html` or a ready-to-serve `dist\` folder.
- State the entry point, build command, and any assets the user must keep alongside the bundle.
- Prefer local assets over remote CDNs unless the user explicitly wants CDN dependencies.

## Validation checklist
- The project installs and builds with the available package manager.
- Final HTML or `dist\` opens without missing assets.
- Relative asset paths work from the output location.
- The UI avoids generic placeholder styling and matches the user's requested tone.

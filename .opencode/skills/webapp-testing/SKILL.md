---
name: webapp-testing
description: Test and debug local web applications with Playwright, including static HTML files, dev servers, screenshots, console logs, and repeatable UI flows.
license: See LICENSE.txt
---

# Web Application Testing

This OpenCode adaptation keeps the original Playwright workflow and helper scripts, but frames them as general local-browser testing tools rather than product-specific automation.

## Use when
- The task needs browser-level verification of a local app or static HTML.
- You need screenshots, DOM inspection, console logs, or UI action/repro scripts.
- A bug only appears after client-side JavaScript runs.

## Do not use when
- The task is API-only or can be solved with existing unit/integration tests.
- You only need a code review of frontend source without running a browser.
- The target is a remote production system you should not automate from this environment.

## Capability checks and fallbacks
- If Playwright is available, write a small native Python script and keep it rerunnable.
- If the app server is not running, inspect `scripts\with_server.py --help` first and use it to manage one or more servers.
- If browser automation is unavailable, fall back to static HTML inspection, HTTP requests, logs, and clear manual repro steps.
- If the page is a static file, skip server startup and use `file://` or direct file reads to choose selectors.
- If multiple services are required, list all commands, ports, and health checks before starting automation.

## Default workflow
1. Decide whether the target is static HTML or a dynamic local webapp.
2. For dynamic apps, run `python scripts\with_server.py --help`, then launch the needed servers through the helper.
3. Write a short Playwright script that navigates, waits for a stable page state, performs reconnaissance, then executes actions or assertions.
4. Capture screenshots, console logs, and rendered DOM state whenever behavior is unclear.
5. Save the script and any evidence files so the user can rerun or inspect them.
6. Summarize findings with selectors, waits, repro steps, and observed failures.

## Resource map
- `scripts\with_server.py` — lifecycle helper for one or more local servers.
- `examples\element_discovery.py` — selector reconnaissance.
- `examples\static_html_automation.py` — static-file automation pattern.
- `examples\console_logging.py` — browser console capture.

## Output contract
- Provide a runnable script or a clear browser-level bug report with evidence.
- Include the target URL or file path, required server command(s), and saved artifacts.
- If the test fails, call out the exact selector, wait, or console error involved.

## Validation checklist
- Browser runs headless unless interactive debugging is explicitly needed.
- Dynamic pages wait for `networkidle` or another explicit stable condition.
- The browser closes cleanly.
- Temporary servers are shut down after the run.
- Logs or screenshots are saved when diagnosing failures.

---
name: mcp-builder
description: Build, extend, or harden MCP servers and MCP tool suites for OpenCode agents, including stdio or streamable HTTP transports, tool schemas, pagination, auth, and evaluation plans.
license: See LICENSE.txt
---

# MCP Builder

This OpenCode adaptation keeps the original skill's strongest parts: MCP server design, tool ergonomics, and evaluation discipline. Use the bundled references heavily; they are mostly portable across runtimes.

## Use when
- Building a new MCP server around an API, database, filesystem, or service.
- Adding tools, resources, or prompts to an existing MCP server.
- Refactoring an MCP server for better discoverability, schema quality, pagination, or auth handling.
- Designing read-only eval sets to verify whether an MCP server is actually useful to agents.

## Do not use when
- You only need a one-off script or direct API client with no MCP layer.
- The task is consuming an existing MCP server rather than authoring one.
- The work is unrelated to tools/resources/prompts exposed through MCP.

## Capability checks and fallbacks
- Prefer TypeScript or Python based on the repo and available toolchain; if one toolchain is broken, switch to the other only when the user is flexible.
- If web access is available, read current MCP spec pages and SDK READMEs; otherwise use the bundled references in `reference\`.
- If MCP Inspector is unavailable, use the bundled connection utilities in `scripts\connections.py` and do manual smoke tests.
- If no tool-calling model endpoint is available, skip the automated evaluation harness and perform manual tool-based evaluations from the XML question set.
- If streamable HTTP is overkill for the deployment target, use stdio for local workflows.

## Default workflow
1. Identify the service surface, auth model, and whether the server is local (`stdio`) or remote (`streamable HTTP`).
2. Read `reference\mcp_best_practices.md` plus the language-specific implementation guide you need.
3. Implement shared client/auth/error-handling utilities before adding tools.
4. Expose tools with small, descriptive schemas and pagination/filters wherever lists can grow.
5. Build and smoke test the server with Inspector or the bundled connection helper.
6. Create a read-only evaluation XML set that stresses real workflows, not toy lookups.
7. Run the automated harness only if an OpenAI-compatible tool-calling model is available; otherwise execute the evals manually and record findings.

## Resource map
- `reference\mcp_best_practices.md` — core design rules.
- `reference\node_mcp_server.md` — TypeScript patterns.
- `reference\python_mcp_server.md` — Python patterns.
- `reference\evaluation.md` — eval design guide plus harness usage.
- `scripts\connections.py` — local/remote MCP connection helpers.
- `scripts\evaluation.py` — provider-neutral evaluation harness.
- `scripts\example_evaluation.xml` — starter XML format.

## Output contract
- Deliver working server code or a concrete implementation patch.
- Document transport choice, auth expectations, and tool inventory.
- Include smoke-test commands and, if requested, an evaluation XML file.
- Call out any tool surfaces that were intentionally left out.

## Validation checklist
- Tool names are descriptive and easy to discover.
- Schemas are strict enough to prevent ambiguous tool calls.
- Pagination, filters, and output size controls exist where needed.
- Error messages tell an agent how to recover.
- The chosen transport works in the intended runtime.
- Build/test commands pass, and the server can be listed/queried by an MCP client.

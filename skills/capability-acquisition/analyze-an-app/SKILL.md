---
name: analyze-an-app
description: "Use when you need to understand how a JavaScript or Electron app works without its source code. Run REA static analysis and report findings tied to evidence."
---

# Analyze an app

Understand a JavaScript or Electron app you cannot read the source of. You have a shipped artifact: an ASAR, an extracted app tree, or a path to either. REA reads it and returns evidence, a module graph, limitations, and unknowns.

Scope: JavaScript and Electron only. Native binaries, Android APKs, and firmware are out of scope here. Point those at the REA reference guides instead.

## When to use

- You need to explain how an app works, but you have no source access.
- You have a path to an ASAR or an extracted JavaScript/Electron tree.
- A connected system's behavior needs mapping before you draft a skill for it.

Do not use this for ordinary source-repo analysis. If you can read the source directly, do that.

## Prerequisites

- REA MCP connected, or the REA CLI reachable. See capability/README.md to enable.
- An absolute path to the target: an ASAR or an extracted app directory.
- Static JavaScript analysis needs no native engine. No Ghidra, Hopper, or IDA.

## Flow

1. Decide the entry tool. For an ASAR or extracted JavaScript/Electron tree, call `analyze_javascript_application` with the absolute path.
2. Start with `detail: "summary"` when the tool advertises it. It returns a small overview and retains the full analysis in the session. Skip summary only when a tiny app's full output fits in one reply.
3. Read the result before asking more. Check evidence, the module graph, coverage, limitations, and unknowns.
4. Follow up only on open questions. Use `trace_application_feature` for one literal node, route, string, IPC channel, or export. Use `inspect_analysis_view` on the retained parent evidence ID to page modules or read one module.
5. Stop when every question on your checklist is answered, or when you have named what stays unknown.

### CLI fallback

When the MCP is not registered, run:

```bash
npx -y rea-agents@latest analyze-javascript-application /absolute/path/to/app --json
```

No MCP registration or native engine needed. The command returns the Evidence record directly. Read evidence, graph, limitations, and unknowns the same way you would an MCP result.

## Read the result

- Evidence: each finding carries an evidence ID. Cite it. Never report a claim without the ID that produced it.
- Module graph: shows which files import what. It is static. It does not prove runtime reachability.
- Limitations: the tool states what it could not cover. Repeat those limits in your report.
- Unknowns: unresolved imports, dynamic IPC channels, ambiguous channels. List them. Do not fill them in.

Static analysis is not runtime proof. A requested `.node` member is not a verified native export. Do not claim runtime behavior, registration, defaults, or policy enforcement from a static read.

## Report

State plainly:

- What the app does.
- How it is structured: modules, entry points, Electron boundaries (main, preload, renderer).
- Each claim tied to an evidence ID.
- A Limitations section: what static analysis could not establish.

Output is ready to forward as-is. No follow-up needed to make it usable.

Uses the REA MCP (https://github.com/morluto/rea, MIT).
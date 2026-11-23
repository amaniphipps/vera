---
name: plannotator
description: Use when reviewing a material plan, spec, or artifact with the user before building. Opens the plan in Plannotator for annotation and returns an approved/feedback/unavailable decision. Inline review is an explicit fallback, never a silent substitute.
---

# Plannotator

Thin adapter around the upstream Plannotator binary for plan review. Vera
does not reimplement annotation; she invokes, parses the decision, and acts
on it.

## When to use

Material Build It plans, onboarding runtime-rebuild plans, and any spec the
user should mark up before implementation. One or two quick actions skip
review; multi-step or expensive-to-undo work does not.

## Invocation

1. Detect `plannotator` on PATH, then the configured repo-local binary
   (`org.example.yaml: binary_path`).
2. Desktop flow opens the browser normally. Headless flow (this OpenCode
   environment) uses:

   ```bash
   PLANNOTATOR_BROWSER=none PLANNOTATOR_SHARE=disabled PLANNOTATOR_AI=disabled \
     plannotator annotate plan.md --gate --json \
     --result-file <runtime>/plannotator/decision.json
   ```

   Print the loopback URL so the user opens it explicitly.
3. Outcomes: **approved** → build the approved slice; **feedback/revise** →
   revise the plan and resubmit, never implement first; **unavailable/error**
   → name it and ask whether inline review is acceptable.

## Hard rules

1. Feedback is never approval. Scope changes re-enter review.
2. If the user requires Plannotator approval, stop before implementation
   until it works.
3. Loopback only by default. Tailscale, Cloudflare Access, public sharing,
   and AI review are separate opt-ins, never silent defaults.
4. Never log secret values or full plan contents; record only the decision,
   timestamp, and artifact pointer.
5. Doctor checks binary presence/version only; it never opens a server or
   browser during checks.

## Definition of done

An approved plan with the decision recorded, or explicit user-accepted
fallback documented with the reason Plannotator was unavailable.

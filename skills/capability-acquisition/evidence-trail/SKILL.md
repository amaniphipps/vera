---
name: evidence-trail
description: "Use when answering 'how does this system work' so every claim carries evidence, confidence, and open unknowns. Keep a reusable finding ledger."
---

# Evidence trail

The house standard for any "how does this system work" answer. Every claim you make carries its evidence. You never smooth over what is still unknown.

## The rule

No claim without evidence. Each claim names:

- The tool that produced it.
- The target it was run against.
- A timestamp or evidence ID.
- A confidence level.

If you cannot tie a claim to evidence, it is an assumption. Say so, or drop it.

## Confidence levels

- confirmed: backed by observed evidence the tool returned.
- inferred: a reasonable read of the evidence, not directly observed.
- unknown: not established. Stated as a gap, never guessed.

## Search boundary

Every answer states what it looked at and what it did not. A bounded negative search is a finding, not a failure. "Not found in these files" is honest. "Does not exist" is not, unless you searched everything.

## Finding ledger

Keep a short ledger linking each conclusion to its evidence IDs, confidence, search boundary, and remaining unknowns. Store it in the evidence dir from org.yaml (default `knowledge/graph/evidence/`), one ledger per system slug. A later pass reuses the ledger instead of redoing the search.

## Residual unknowns

State what you still do not know, under its own heading. Do not round an unknown up to a confident claim to make the answer feel complete.

## Template

Copy this block into your answer:

```
## What I found
- <claim one>. (evidence: <tool> on <target>, <id or timestamp>, confidence: <level>)

## Search boundary
- Looked at: <targets or files>
- Did not look at: <what is out of scope>

## Residual unknowns
- <thing not established, and why>
```

Output is ready to forward as-is. The evidence trail is part of the deliverable, not a side note.

Uses the REA MCP (https://github.com/morluto/rea, MIT).
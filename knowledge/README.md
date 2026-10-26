# Knowledge

Two layers of what Vera knows:

## `seed/` — ships with the repo

Canonical, generic knowledge every deployment gets on day one.

- `seed/saas-terms.md` — the shared SaaS glossary (ARR, churn, CAC, PLG, the
  50 standard terms plus a few RevOps additions).

## `graph/` — built per deployment

The org's own knowledge graph, constructed by Vera as she works. Ships empty
on purpose; your org's facts never come from us.

```
graph/
├── entities/
│   ├── people/       # roles, teams, timezones, preferences (no HR data)
│   ├── systems/      # owner, purpose, auth model class, endpoint refs
│   ├── glossary/     # what YOUR words mean here (org-specific terms)
│   └── business/     # revenue model, metrics, targets (org-authored)
├── evidence/         # receipts: analysis output, run logs, drift notes
└── schema/           # entity and link definitions
```

Write rules that keep the graph honest:

1. Facts enter only from verified sources: a real API read, a confirmed
   admin statement. Never from chat assertions alone.
2. People-sensitive classes (comp, performance, anything HR-flavored) are
   excluded by schema and policy. No exceptions.
3. Every claim can point at evidence. The evidence-trail skill sets the
   format.

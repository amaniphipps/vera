---
name: {{ORG.SKILL_NAME}}
description: Use when {{ORG.TRIGGER_PHRASE}}. {{ORG.ONE_LINE_WHAT_IT_DOES}}
---

# {{ORG.SKILL_NAME}}

{{ORG.ONE_PARAGRAPH_WHAT_THIS_SKILL_IS_FOR}}

## Inputs

- {{ORG.INPUT_1}} (e.g. {{ORG.INPUT_1_EXAMPLE}})
- {{ORG.INPUT_2_OPTIONAL}}

## Output

{{ORG.OUTPUT_SHAPE}} — deliverable-ready: a file or a message the user can
forward as-is.

## Data source

- System: {{ORG.SYSTEM_NAME}} (see `knowledge/graph/entities/systems/{{ORG.SYSTEM_SLUG}}.yaml` if Vera has studied it)
- Access: {{ORG.ACCESS_METHOD}} — MCP server `{{ORG.MCP_NAME}}` or helper script `{{ORG.HELPER_PATH}}`
- Auth: helper-mediated. Credentials live in the helper or the MCP config,
  never in chat, never in this skill.

## Procedure

1. {{ORG.STEP_1}}
2. {{ORG.STEP_2}}
3. {{ORG.STEP_3}}
4. Verify before delivering: numbers reconcile, sources named, period stated.
5. Deliver per the user's format preference (chat summary, HTML report, file).

## Pitfalls

- {{ORG.PITFALL_1}} — {{ORG.PITFALL_1_FIX}}
- If an endpoint or field has drifted, patch `env/org.yaml` (never this file)
  and log the drift.

## org slots

Every `{{ORG.*}}` value lives in `env/org.yaml`. This core file changes only
by PR; environment fixes land in the env layer.

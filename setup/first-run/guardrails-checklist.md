# Guardrails checklist — for the infrastructure owner

Vera ships **read-only**. Widening that is your call, made in one file:
`policy/guardrails.yaml` (in the Hermes home directory after setup). Nothing
Vera learns or is asked in chat can override what this file says.

## Decisions to make (15 minutes)

1. **Who Vera serves.** `domains.serve_only` — restrict to your email domain,
   or leave open. Most orgs restrict.
2. **Where she never posts.** `channels.blocked_send` — channel IDs (best) or
   name patterns (e.g. `*-leaders`, `exec-*`). Get IDs from your platform admin.
3. **What she never reads.** `channels.blocked_read` — same shape.
4. **Topics she never relays.** `content_rules.forbidden_topics` — regex list.
   The default covers comp/performance-review patterns; tune to your org.
5. **Write posture.** `writes.default` — keep `read-only` until you have a
   reason not to. `writes.allowed_surfaces` lists the ONLY systems she may
   write to, ever. `writes.confirm_before_write: always` means she asks per
   action even when she holds keys; `standing` means you trust the grants.
6. **SQL guard.** `sql.allowed_statements` — default is SELECT/SHOW/DESCRIBE/
   EXPLAIN only. Leave it.
7. **Approvals.** `approvals.require_for` — actions that always need a human
   first (external writes, secret-adjacent commands, system analysis).

## The contract

- These rules are enforced as **data**, at the send/tool/skill level — not as
  instructions Vera promises to follow.
- Draft skills (things Vera learns on the job) are quarantined: no external
  writes, no secret material, until a human promotes them.
- Change the file, and every channel, every skill, and everything she learns
  later honors it. Change it in chat with Vera and nothing changes — by design.

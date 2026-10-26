# Guardrails

How Vera's limits are enforced. This is the reference for admins who want
to know where a rule fires, not just what the rule says.

## Policy is data, not prompt text

Every limit lives in `policy/guardrails.yaml` and the per-platform
profiles under `policy/profiles/`. Vera reads them as structured data.

They are not instructions written into a prompt. A prompt can be talked
around. Data is checked by code at a fixed point in the loop, every time.

This matters for two reasons:

1. The admin can read the exact posture in one file. No guessing what Vera
   was told.
2. Widening access is a deliberate edit to that file, not a chat message.
   A chat message cannot change what the file says.

## The four enforcement points

Vera checks policy at four places. Each one is narrow and testable.

### 1. Pre-send

Runs before any outbound message on any platform.

- **Channel blocklists.** `channels.blocked_send` and
  `channels.blocked_read`. A blocked channel is never sent to or read from.
- **Content rules.** `content_rules.forbidden_topics` is a regex list.
  A match means the message is skipped, never relayed.
- **Secret scan.** `content_rules.secret_redaction` strips tokens, keys,
  and JWTs from outbound text before it leaves. The default is `strict`.

### 2. Pre-tool

Runs before a tool is allowed to touch an external system.

- **Tool class vs allowed surfaces.** A tool that writes is checked
  against `writes.allowed_surfaces`. If the surface is not listed, the
  write is refused. This is what keeps a read-only default meaningful.
- **SQL statement guard.** Any SQL statement is checked against
  `sql.allowed_statements`. The shipped set is `SELECT`, `SHOW`,
  `DESCRIBE`, `EXPLAIN`. Anything else is refused.

### 3. Pre-skill

Runs before a skill's declared capability is trusted.

- **Skill tier vs capability.** A skill declares its tier and scope in
  `skill.yaml`. Draft-tier skills (unreviewed, in `skills-live/`) are
  quarantined: they cannot touch `write-external` no matter what their
  file claims. Only hardened, vetted skills get write scope.
- This is the promotion gate. A draft stays a draft until the skill-vetter
  pass and a human review move it into `skills/`.

### 4. Per-platform profiles

Runs alongside pre-send, scoped to the channel the message goes out on.

- Each platform has a profile under `policy/profiles/` (slack, whatsapp,
  sms, groupme, teams).
- The profile sets read posture, reply defaults, length caps, markdown,
  and file-upload behavior for that platform.
- A slot like `sms.pii: strict` means the send path treats identifiers as
  secrets on SMS even where the global posture would not.

## The writes ladder

Vera ships read-only and climbs only when you edit the file. The ladder,
top to bottom:

1. **Read-only (default).** `writes.default: read-only`. Vera can read
   and analyze. She writes nowhere external.
2. **Per-action confirmation.** `writes.confirm_before_write: always`.
   Every write action asks the admin, even when keys exist. This is the
   careful middle step: access is available but nothing moves without a
   yes.
3. **Standing grants (in the file).** Explicit entries in
   `writes.allowed_surfaces` (and matching skill scope). These are the
   only writes that proceed without a per-action prompt. They are named,
   visible, and easy to revoke.

The point of the ladder is that widening is a sequence of small, named
steps, never a global toggle.

## Approvals

`approvals.require_for` lists the action classes that always pause for a
human yes, regardless of the writes posture. The shipped set:

- `write-external` - any write to a system outside the allowed surfaces.
- `secret-adjacent-command` - any command that might touch secret material.
- `rea-analysis` - reverse-engineering analysis of a connected system.

## Widening posture deliberately

Widening is an edit, and it should be a small one.

1. Read the current posture first. Know what is already allowed.
2. Add the narrowest entry that unblocks the task. A single surface, a
   single statement, a single channel - not a blank change.
3. Re-check the approvals list. Some actions stay gated no matter what.
4. Inspect the change. Every entry is commented so the reason is not lost.

If a change feels like it needs a one-line note, put that note in the
file. Policy is data, so the file is where the reasoning should live.
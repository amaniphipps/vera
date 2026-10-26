# Scrub checklist — the gate before anything goes public

Run this in full before flipping the repo public, and re-run it after any
large import of outside material. Tools catch token shapes; only a human
catches a customer's name in a comment. Both are required.

## Automated passes

- [ ] `gitleaks dir .` — working tree, no leaks
- [ ] `gitleaks git .` — FULL history, no leaks (history is forever)
- [ ] CI: secrets workflow (gitleaks + trufflehog) green on every PR once
      `.github/workflows/secrets.yaml` lands

## Manual grep passes (tools can't flag these)

- [ ] Org nouns: `grep -ri -E '<your-org-name>|internal codenames|vendor names' .`
      must return nothing. (For this repo's origin: no Bonusly, SignalForge,
      OpsBot, internal vendor names, internal table names.)
- [ ] Same pass over history: `git grep -i -E '<pattern>' $(git rev-list --all)`
- [ ] Real IDs: no real Slack/Teams/Discord channel, user, or bot IDs.
      Placeholders like `C0123456789` or `19:xxx@thread.tacv2` are fine.
- [ ] Key material: no sha prefixes of real keys, no project refs, no signed
      URLs (`token=`, `sig=`, `*.supabase.co/storage`)
- [ ] Emails: only `example.com` / platform-format placeholders
- [ ] People: no real names in examples (use "Jordan", "Dana", "Testco",
      "Northwind"); no personal phone numbers
- [ ] Session data: no exported session DBs, transcripts, or DM logs anywhere
      in the tree

## Sign-off

- [ ] A second set of human eyes has read the full diff of the initial commit
- [ ] The person flipping the switch has read this checklist end to end

---

## Audit log

### 2026-10-25 — pre-publish audit (repo private, 13 commits)

| Check | Tool | Result |
|---|---|---|
| Working tree secrets | gitleaks 8.30.1 `dir` | CLEAN — no leaks |
| Full history (13 commits) | gitleaks `git` | CLEAN — no leaks |
| Org nouns (origin org, codenames, vendors, tables) | grep, tree + all commits | CLEAN |
| Real Slack IDs (6 known live IDs) | grep | CLEAN |
| Key shas, project refs, phone, signed-URL patterns | grep | CLEAN |
| Emails | grep | CLEAN — example.com + Teams-format placeholders only |
| Personal name as example | grep | FIXED — 2 files said `e.g. "Amani"`, now `e.g. "Jordan"` (NOTICE/README keep the author name by design) |

**Remaining pre-publish gates:**
1. CI secrets workflow pushed (blocked on `gh auth refresh -h github.com -s workflow`)
2. Kevin (or second-eyes) reads the full tree
3. Re-run this checklist the day of the flip

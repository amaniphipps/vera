---
name: code-review
description: "Use when reviewing a diff or checking work before commit. Spec first, then quality and security."
---

# Code review

Review code before it lands: another person's diff, or your own work before commit.

## Order of review: spec first

Review in this order. Stop correctly when an earlier pass already fails.

1. Spec compliance. Does the change do what it was asked to do, and nothing that contradicts the ask? Does it match the plan or requirements? A change that does the wrong thing correctly is still wrong.
2. Correctness. Edge cases, error paths, off-by-one, wrong conditions.
3. Security. Hardcoded secrets, input validation, injection, path traversal, auth checks.
4. Quality. Naming, duplication, single responsibility, test coverage, documentation.

A review that jumps to style before confirming the change is correct wastes everyone's time.

## How to review a diff

- Get the scope first: file list and a summary of changes.
- Read the full diff, then open changed files for surrounding context. Diffs alone miss issues visible only with nearby code.
- Apply the checklist below.

## Checklist

- [ ] No hardcoded secrets, API keys, or credentials
- [ ] User-provided data is validated
- [ ] Queries are parameterized (no string-built SQL)
- [ ] File paths are validated (no traversal)
- [ ] External calls handle errors
- [ ] No leftover debug prints or commented-out code
- [ ] New code has tests where a test suite exists
- [ ] No merge-conflict markers left in files

## Feedback that lands

- Attach every finding to a file and line. Ground an opinion in specific code, not general advice.
- Sort by severity and keep the buckets few: blocking issues, warnings, suggestions, and what looks good.
- Say what to change, not just that it is wrong. A fix suggestion beats a complaint.
- Lead with the one thing that matters most. A reviewer who lists twenty minor notes hides the critical one.
- Separate blocking from non-blocking explicitly. The author must be able to tell what actually has to change.

## Pre-commit self-review

Before you commit your own work:

- Get the diff (`git diff --cached`, then `git diff` if empty).
- Run a static scan over added lines: secrets, shell injection, unsafe eval, unsafe deserialization, string-built queries.
- Run tests and linting. Capture failures before your change as a baseline; only new failures block.
- Walk the checklist above.
- Prefer an independent reviewer. No one checks their own work well. If you can delegate a fresh review with only the diff, do it, and treat an unparseable response as a fail.

If the first pass surfaces issues, fix only those issues and re-verify. Do not refactor or add features while fixing a review.
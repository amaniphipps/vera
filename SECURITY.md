# Security

## Reporting

Please do not open a public issue for vulnerabilities. Email the maintainer
(see the GitHub profile) with details and we'll respond within 72 hours.

## Vera's security model in short

- Real secrets live only in `.env` (git-ignored) or your platform's secret store.
- Vera ships **read-only**. Write access is widened deliberately, per surface,
  in `policy/guardrails.yaml`.
- Skills Vera learns at runtime are quarantined (`skills-live/`): they cannot
  write to external systems and cannot read secret material until reviewed.
- Every pull request is scanned for secrets (gitleaks + trufflehog).

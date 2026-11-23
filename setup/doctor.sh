#!/usr/bin/env bash
# Vera doctor - is this install honest?
# Renders the capability table from capability/core-capabilities.yaml plus
# the active runtime profile (deploy/runtimes/<runtime>.yaml).
# Core FAILs exit 1; enhanced capabilities report INFO, never FAIL.
#
# Flags:
#   --runtime hermes|opencode|generic   skip auto-detection
#   --json                              machine-readable output
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
RUNTIME=""
JSON=0
while [ $# -gt 0 ]; do
  case "$1" in
    --runtime) RUNTIME="$2"; shift 2 ;;
    --json) JSON=1; shift ;;
    -h|--help) grep '^#' "$0" | head -12; exit 0 ;;
    *) echo "unknown flag: $1" >&2; exit 2 ;;
  esac
done

FAILS=0; WARNS=0
pass() { printf '  PASS  %s\n' "$*"; }
warn() { printf '  WARN  %s\n' "$*"; WARNS=$((WARNS+1)); }
fail() { printf '  FAIL  %s\n' "$*"; FAILS=$((FAILS+1)); }
say_section() { printf '\n%s\n' "$*"; }

say_section "Preflight"
command -v python3 >/dev/null || { fail "python3 missing (install 3.9+)"; exit 1; }
PY=python3
if ! python3 -c 'import yaml' 2>/dev/null; then
  # Isolated fallback: use a repo-local venv if one exists, else tell the user.
  if [ -x "$REPO_ROOT/.venv/bin/python" ] && "$REPO_ROOT/.venv/bin/python" -c 'import yaml' 2>/dev/null; then
    PY="$REPO_ROOT/.venv/bin/python"
  else
    fail "pyyaml missing. Install into an isolated venv:"
    printf '         python3 -m venv %s/.venv && %s/.venv/bin/pip install pyyaml\n' "$REPO_ROOT" "$REPO_ROOT"
    exit 1
  fi
fi
pass "python3 + pyyaml available ($PY)"

say_section "Capabilities"
ARGS=(--repo "$REPO_ROOT")
[ -n "$RUNTIME" ] && ARGS+=(--runtime "$RUNTIME")
[ "$JSON" = 1 ] && ARGS+=(--json)
"$PY" "$REPO_ROOT/setup/capability_check.py" "${ARGS[@]}"
CAP_EXIT=$?
[ "$CAP_EXIT" -eq 2 ] && exit 2

say_section "Secret hygiene"
hits=$(grep -rlE '(xox[baprs]-[A-Za-z0-9-]{10,}|sk-[A-Za-z0-9_-]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)' \
  "$REPO_ROOT/skills" "$REPO_ROOT/policy" "$REPO_ROOT/knowledge" 2>/dev/null | wc -l | tr -d ' ')
[ "${hits:-0}" -eq 0 ] && pass "no secret-shaped strings in skills/, policy/, knowledge/" \
  || fail "$hits file(s) contain secret-shaped strings"
if [ -f "$HERMES_HOME/.env" ] && grep -qE '(your-key-here|placeholder|CHANGEME)' "$HERMES_HOME/.env" 2>/dev/null; then
  warn "$HERMES_HOME/.env still contains placeholder values"
fi

say_section "Summary"
if [ "$CAP_EXIT" -ne 0 ] || [ "$FAILS" -gt 0 ]; then
  printf '  Core capability failures present - fix the FAILs and re-run.\n'; exit 1
elif [ "$WARNS" -gt 0 ]; then
  printf '  0 FAIL, %d WARN - usable; review warnings when convenient.\n' "$WARNS"; exit 0
else
  printf '  All core checks pass. Enhanced INFO rows are choices, not failures.\n'; exit 0
fi

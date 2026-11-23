#!/usr/bin/env bash
# Vera tests. Uses an isolated repo-local venv; never touches system python.
set -uo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV="$REPO_ROOT/.venv"

if [ ! -x "$VENV/bin/python" ] || ! "$VENV/bin/python" -c 'import yaml' 2>/dev/null; then
  echo "creating isolated test venv at .venv/"
  python3 -m venv "$VENV" || exit 2
  "$VENV/bin/pip" install -q pyyaml || exit 2
fi

FAIL=0
for t in "$REPO_ROOT"/tests/onboarding/test_*.py; do
  echo "== $(basename "$t") =="
  "$VENV/bin/python" "$t" || FAIL=1
done
exit "$FAIL"

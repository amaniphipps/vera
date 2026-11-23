#!/usr/bin/env bash
# Plannotator review entrypoint — one tested path for plan annotation.
# Usage: review.sh <plan.md> [--result-file PATH]
# Prints the session URL; with --gate --json the decision JSON goes to stdout
# (or --result-file when given). Never logs plan contents.
set -euo pipefail
PLAN="${1:-}"; shift || true
[ -z "$PLAN" ] && { echo "usage: review.sh <plan.md> [--result-file PATH]" >&2; exit 2; }
[ -f "$PLAN" ] || { echo "plan not found: $PLAN" >&2; exit 2; }
BIN="${PLANNOTATOR_BIN:-$(command -v plannotator || true)}"
[ -z "$BIN" ] && { echo "plannotator not on PATH and PLANNOTATOR_BIN unset" >&2; exit 3; }
RESULT_FILE=""
while [ $# -gt 0 ]; do
  case "$1" in
    --result-file) RESULT_FILE="$2"; shift 2 ;;
    *) echo "unknown flag: $1" >&2; exit 2 ;;
  esac
done
ARGS=(annotate "$PLAN" --gate --json)
[ -n "$RESULT_FILE" ] && ARGS+=(--result-file "$RESULT_FILE")
: "${PLANNOTATOR_BROWSER:=none}" "${PLANNOTATOR_SHARE:=disabled}" "${PLANNOTATOR_AI:=disabled}"
export PLANNOTATOR_BROWSER PLANNOTATOR_SHARE PLANNOTATOR_AI
exec "$BIN" "${ARGS[@]}"
